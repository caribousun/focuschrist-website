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
function makeTrace(row){
 const start=performance.now(),ids=new WeakMap();let next=1;
 const mark=(kind,request,detail={})=>{
  let u;try{u=new URL(request.url());}catch(_){return;}
  if(!providers.has(u.hostname))return;
  if(!ids.has(request))ids.set(request,next++);
  const raw=u.pathname;let decoded='';try{decoded=decodeURIComponent(raw);}catch(_){}
  const path=raw.length<=180&&decoded&&/^\/[A-Za-z0-9._~%/+,-]*$/.test(raw)&&!/(?:token|auth|secret|api.?key)/i.test(decoded)?raw:'[redacted]';
  const type=typeof request.resourceType==='function'?request.resourceType():'unknown';
  const record={id:ids.get(request),kind,host:u.hostname,path,resourceType:/^[a-z]{1,20}$/.test(type)?type:'unknown',phase:row.phase,ms:Math.round(performance.now()-start),...detail};
  if(row.events.length<512)row.events.push(record);else row.eventsDropped++;
 };
 return {mark,elapsed:()=>Math.round(performance.now()-start)};
}
async function enforceRequest(route,origin,row,onDenial,trace=()=>{}){
 const request=route.request(),url=request.url(),method=request.method();
 if(row.denied||!allowedRequest(url,origin)||!['GET','HEAD'].includes(method)){
  row.blockedRequests++;return route.abort('blockedbyclient');
 }
 const host=new URL(url).hostname;let response;
 try{
  trace('route-fetch-start',request);
  response=await route.fetch({maxRedirects:0,maxRetries:0,timeout:15000});
  const status=response.status();
  trace('route-fetch-response',request,{status});
  if(status>=300&&status<400){
   row.blockedRedirects++;if(row.responseErrors.length<10)row.responseErrors.push({host,status});
   await response.dispose();return route.abort('blockedbyclient');
  }
  if([401,403,451].includes(status)){
   row.denied=true;row.denial={host,status};row.badResponses++;
   if(row.responseErrors.length<10)row.responseErrors.push({host,status});
   onDenial();await response.dispose();return route.abort('blockedbyclient');
  }
  await route.fulfill({response});trace('route-fulfilled',request,{status});await response.dispose();
 }catch(error){
  row.boundaryErrors++;
  const message=String(error&&error.message||''),match=message.match(/net::ERR_[A-Z0-9_]+/);trace('route-error',request,{code:match?match[0]:'unclassified'});
  if(response)await response.dispose().catch(()=>{});
  await route.abort('blockedbyclient').catch(()=>{});
 }
}
function classify(row){
 if(row.denied)return 'DENIED';
 if(row.error||row.pageErrors||row.failedRequests||row.badResponses||row.blockedRequests||row.blockedRedirects||row.boundaryErrors||row.eventsDropped||!row.sourcesLoaded||!row.rendererLoaded||!row.statusHidden||!row.canvasVisible||!row.openfreemapResponses||!row.mapterhornResponses)return 'FAIL';
 return 'PASS';
}
module.exports={classify,allowedRequest,enforceRequest,makeTrace};
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
   const row={profile:profile.name,phase:'setup',events:[],eventsDropped:0,mapEvents:[],denied:false,denial:null,requestErrors:[],responseErrors:[],pageErrors:0,failedRequests:0,badResponses:0,blockedRequests:0,blockedRedirects:0,boundaryErrors:0,openfreemapResponses:0,mapterhornResponses:0};let deniedResolve;
   const trace=makeTrace(row);
   const deniedSignal=new Promise(resolve=>deniedResolve=resolve);
   await context.route('**/*',route=>enforceRequest(route,origin,row,deniedResolve,trace.mark));
   page.on('request',request=>trace.mark('request',request));
   page.on('pageerror',()=>row.pageErrors++);
   page.on('requestfailed',request=>{const host=new URL(request.url()).hostname;if(!providers.has(host))return;row.failedRequests++;const raw=request.failure()?.errorText||'',code=/^net::ERR_[A-Z0-9_]+$/.test(raw)?raw:'unclassified';trace.mark('request-failed',request,{code});if(row.requestErrors.length<10)row.requestErrors.push({host,code});});
   page.on('requestfinished',request=>trace.mark('request-finished',request));
   page.on('response',response=>{const host=new URL(response.url()).hostname;if(!providers.has(host))return;const status=response.status();trace.mark('response',response.request(),{status});if(status===401||status===403||status===451){row.denied=true;row.denial={host,status};deniedResolve();}if(status<200||status>=300){row.badResponses++;if(row.responseErrors.length<10)row.responseErrors.push({host,status});}else if(host==='tiles.openfreemap.org')row.openfreemapResponses++;else row.mapterhornResponses++;});
   try{
    row.phase='navigation';
    const response=await page.goto(origin+route+'#viewer',{waitUntil:'domcontentloaded',timeout:30000});assert(response&&response.status()===200);assert.equal(sha(await response.body()),identity.pageSha256,'Served candidate bytes differ');
    row.phase='map-monitor-setup';await page.waitForFunction(()=>!!window.__leafMap,null,{timeout:15000});
    const monitorBefore=trace.elapsed();await page.evaluate(()=>{const map=window.__leafMap,start=performance.now();window.__providerMapTrace=[];window.__providerMapTraceDropped=0;map.on('movestart moveend zoomstart zoomend resize',e=>{const a=window.__providerMapTrace;if(a.length<64)a.push({event:e.type,ms:Math.round(performance.now()-start)});else window.__providerMapTraceDropped++;});});row.mapMonitorStartedBetweenMs=[monitorBefore,trace.elapsed()];
    row.phase='scroll';
    await page.locator('#leafmap').scrollIntoViewIfNeeded();
    row.phase='waiting';
    const settled=page.waitForFunction(()=>{const g=window.__englishMap,status=document.getElementById('englishMapStatus');try{return !!(g&&g.loaded()&&g.isSourceLoaded('openmaptiles')&&g.isSourceLoaded('terrain-dem')&&status&&status.hidden);}catch(_){return false;}},null,{timeout:45000}).then(()=>true).catch(()=>false);
    const ready=await Promise.race([settled,deniedSignal.then(()=>false)]);
    if(ready){
     row.phase='renderer-state';const state=await page.evaluate(()=>{const g=window.__englishMap,c=g&&g.getCanvas(),r=c&&c.getBoundingClientRect(),s=document.getElementById('englishMapStatus');return {rendererLoaded:!!(g&&g.loaded()),sourcesLoaded:!!(g&&g.isSourceLoaded('openmaptiles')&&g.isSourceLoaded('terrain-dem')),statusHidden:!!(s&&s.hidden),canvasVisible:!!(r&&r.width>0&&r.height>0)};});
     Object.assign(row,state);
    }
    if(!row.denied){row.phase='screenshot';await page.screenshot({path:path.join(out,profile.name+'.png'),animations:'disabled',timeout:10000});}
   }catch(error){row.error='candidate navigation, provider readiness, or screenshot did not complete';}
   if(!row.denied){row.phase='map-trace';try{const m=await page.evaluate(()=>({events:window.__providerMapTrace||[],dropped:window.__providerMapTraceDropped||0}));row.mapEvents=m.events;row.mapEventsDropped=m.dropped;}catch(_){row.error='map event trace unavailable';}}
   row.phase='teardown';await context.close();row.phase='closed';if(row.mapEventsDropped)row.error='map event trace incomplete';row.status=classify(row);rows.push(row);
   if(row.denied)break; // Never retry an explicit provider denial in another profile.
  }
 }finally{
  if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));
  for(const row of rows)row.status=classify(row);
  fs.writeFileSync(path.join(out,'provider-diagnostic.json'),JSON.stringify({identity,rows,limits:['Provider-backed hosted Chromium only; screenshot review and physical-device verification are separate.','Map events are recorded only after monitor setup; the reported start interval bounds cross-process timing alignment.','Request failures during teardown are recorded and still fail the diagnostic.','The deterministic isolated browser suite remains separate.']},null,2)+'\n');
 }
 assert.equal(rows.length,2,'Both desktop and phone provider checks are required');assert(rows.every(r=>r.status==='PASS'),'Provider diagnostic failed; inspect bounded report and screenshots');
 console.log('PASS: configured map providers responded and settled on desktop and phone; visual review remains separate.');
}
if(require.main===module)run().catch(error=>{console.error(String(error));process.exitCode=1;});
