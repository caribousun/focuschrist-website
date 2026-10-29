/* Hosted provider-backed diagnostic. No mocked tiles, credentials, or release approval. */
'use strict';
const assert=require('node:assert/strict'),crypto=require('node:crypto'),fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/timeline/provider');
const providers=new Set(['tiles.openfreemap.org','tiles.mapterhorn.com']);
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function allowedRequest(url,origin){
 try{
  const u=new URL(url),local=new URL(origin);
  if(u.username||u.password||local.username||local.password||local.protocol!=='http:'||local.hostname!=='127.0.0.1'||!local.port)return false;
  return u.origin===local.origin||(u.protocol==='https:'&&!u.port&&providers.has(u.hostname));
 }catch(_){return false;}
}
async function enforceRequest(route,origin,row,onDenial){
 const request=route.request(),url=request.url(),method=request.method();
 if(row.denied||!allowedRequest(url,origin)||!['GET','HEAD'].includes(method)){
  row.blockedRequests++;return route.abort('blockedbyclient');
 }
 const host=new URL(url).hostname;let response;
 try{
  response=await route.fetch({maxRedirects:0,maxRetries:0,timeout:15000});
  const status=response.status();
  if(status>=300&&status<400){
   row.blockedRedirects++;if(row.responseErrors.length<10)row.responseErrors.push({host,status});
   await response.dispose();return route.abort('blockedbyclient');
  }
  if([401,403,451].includes(status)){
   row.denied=true;row.denial={host,status};row.badResponses++;
   if(row.responseErrors.length<10)row.responseErrors.push({host,status});
   onDenial();await response.dispose();return route.abort('blockedbyclient');
  }
  await route.fulfill({response});await response.dispose();
 }catch(_){
  row.boundaryErrors++;
  if(response)await response.dispose().catch(()=>{});
  await route.abort('blockedbyclient').catch(()=>{});
 }
}
function classify(row){
 if(row.denied)return 'DENIED';
 if(row.error||row.pageErrors||row.failedRequests||row.badResponses||row.blockedRequests||row.blockedRedirects||row.boundaryErrors||!row.sourcesLoaded||!row.rendererLoaded||!row.statusHidden||!row.canvasVisible||!row.openfreemapResponses||!row.mapterhornResponses)return 'FAIL';
 return 'PASS';
}
module.exports={classify,allowedRequest,enforceRequest};
async function run(){
 assert.equal(process.env.CI,'true','Hosted CI only');
 const {chromium}=require('playwright'),route='/timelines/world-and-scripture-timeline.html';
 const pageBytes=fs.readFileSync(path.join(root,route)),head=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
 const event=process.env.GITHUB_EVENT_PATH?JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH,'utf8')):{};
 const identity={checkout:head,pullRequestHead:event.pull_request?.head?.sha||null,workflowSha:process.env.GITHUB_SHA||null,pageSha256:sha(pageBytes),diagnosticSha256:sha(fs.readFileSync(__filename))};
 fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{try{const url=new URL(req.url,'http://localhost'),file=path.resolve(root,'.'+decodeURIComponent(url.pathname));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.json':'application/json'})[path.extname(file)]||'application/octet-stream'}).end(b));}catch(e){res.writeHead(400).end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin='http://127.0.0.1:'+server.address().port;
 let browser;const rows=[];
 try{
  browser=await chromium.launch({headless:true});
  for(const profile of [{name:'desktop',width:1366,height:900},{name:'phone',width:390,height:844}]){
   const context=await browser.newContext({viewport:{width:profile.width,height:profile.height},reducedMotion:'reduce',serviceWorkers:'block'});
   await context.routeWebSocket('**/*',socket=>socket.close());const page=await context.newPage();
   const row={profile:profile.name,denied:false,denial:null,requestErrors:[],responseErrors:[],pageErrors:0,failedRequests:0,badResponses:0,blockedRequests:0,blockedRedirects:0,boundaryErrors:0,openfreemapResponses:0,mapterhornResponses:0};let deniedResolve;
   const deniedSignal=new Promise(resolve=>deniedResolve=resolve);
   await context.route('**/*',route=>enforceRequest(route,origin,row,deniedResolve));
   page.on('pageerror',()=>row.pageErrors++);
   page.on('requestfailed',request=>{const host=new URL(request.url()).hostname;if(!providers.has(host))return;row.failedRequests++;const code=request.failure()?.errorText||'';if(row.requestErrors.length<10)row.requestErrors.push({host,code:/^net::ERR_[A-Z0-9_]+$/.test(code)?code:'unclassified'});});
   page.on('response',response=>{const host=new URL(response.url()).hostname;if(!providers.has(host))return;const status=response.status();if(status===401||status===403||status===451){row.denied=true;row.denial={host,status};deniedResolve();}if(status<200||status>=300){row.badResponses++;if(row.responseErrors.length<10)row.responseErrors.push({host,status});}else if(host==='tiles.openfreemap.org')row.openfreemapResponses++;else row.mapterhornResponses++;});
   try{
    const response=await page.goto(origin+route+'#viewer',{waitUntil:'domcontentloaded',timeout:30000});assert(response&&response.status()===200);assert.equal(sha(await response.body()),identity.pageSha256,'Served candidate bytes differ');
    await page.locator('#leafmap').scrollIntoViewIfNeeded();
    const settled=page.waitForFunction(()=>{const g=window.__englishMap,status=document.getElementById('englishMapStatus');try{return !!(g&&g.loaded()&&g.isSourceLoaded('openmaptiles')&&g.isSourceLoaded('terrain-dem')&&status&&status.hidden);}catch(_){return false;}},null,{timeout:45000}).then(()=>true).catch(()=>false);
    const ready=await Promise.race([settled,deniedSignal.then(()=>false)]);
    if(ready){
     const state=await page.evaluate(()=>{const g=window.__englishMap,c=g&&g.getCanvas(),r=c&&c.getBoundingClientRect(),s=document.getElementById('englishMapStatus');return {rendererLoaded:!!(g&&g.loaded()),sourcesLoaded:!!(g&&g.isSourceLoaded('openmaptiles')&&g.isSourceLoaded('terrain-dem')),statusHidden:!!(s&&s.hidden),canvasVisible:!!(r&&r.width>0&&r.height>0)};});
     Object.assign(row,state);
    }
    if(!row.denied)await page.screenshot({path:path.join(out,profile.name+'.png'),animations:'disabled',timeout:10000});
   }catch(error){row.error='candidate navigation, provider readiness, or screenshot did not complete';}
   row.status=classify(row);rows.push(row);await context.close();
   if(row.denied)break; // Never retry an explicit provider denial in another profile.
  }
 }finally{
  if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));
  fs.writeFileSync(path.join(out,'provider-diagnostic.json'),JSON.stringify({identity,rows,limits:['Provider-backed hosted Chromium only; screenshot review and physical-device verification are separate.','The deterministic isolated browser suite remains separate.']},null,2)+'\n');
 }
 assert.equal(rows.length,2,'Both desktop and phone provider checks are required');assert(rows.every(r=>r.status==='PASS'),'Provider diagnostic failed; inspect bounded report and screenshots');
 console.log('PASS: configured map providers responded and settled on desktop and phone; visual review remains separate.');
}
if(require.main===module)run().catch(error=>{console.error(String(error));process.exitCode=1;});
