/* Hosted provider-backed diagnostic. No mocked tiles, credentials, or release approval. */
'use strict';
const assert=require('node:assert/strict'),crypto=require('node:crypto'),fs=require('node:fs'),http=require('node:http'),path=require('node:path'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/timeline/provider');
const providers=new Set(['tiles.openfreemap.org','tiles.mapterhorn.com']);
const {assess:assessCancellation}=require('./world_provider_cancellation_review');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function allowedRequest(url,origin){
 try{
  const u=new URL(url),local=new URL(origin);
  if(u.username||u.password||local.username||local.password||local.protocol!=='http:'||local.hostname!=='127.0.0.1'||!local.port)return false;
  return u.origin===local.origin||(u.protocol==='https:'&&!u.port&&providers.has(u.hostname));
 }catch(_){return false;}
}
function publicPathClass(host,path){
 if(host==='tiles.openfreemap.org'&&path==='/planet')return '/planet';
 const templates=host==='tiles.openfreemap.org'
  ?[[/^\/natural_earth\/ne2sr\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.png$/,'/natural_earth/ne2sr/{z}/{x}/{y}.png'],[/^\/planet\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.pbf$/,'/planet/{z}/{x}/{y}.pbf'],[/^\/tiles\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.pbf$/,'/tiles/{z}/{x}/{y}.pbf']]
  :host==='tiles.mapterhorn.com'?[[/^\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.webp$/,'/{z}/{x}/{y}.webp']]:[];
 for(const [pattern,label] of templates){const m=pattern.exec(path);if(!m)continue;const [z,x,y]=m.slice(1).map(Number);if(z<=22&&x<2**z&&y<2**z)return label;}
 return '[redacted]';
}
// Installed before navigation. Uses only the documented Map constructor and event API.
// Constructor-internal synchronous events cannot be observed by a post-construction listener.
function installEarlySourceObserver(){
 const allowed=new Set(['ne2_shaded','openmaptiles','terrain-dem']);
 const state={installed:false,attached:false,events:[],dropped:0};
 window.__providerSourceTrace=state;
 let exported,finished=false;const listeners=[];
 function coordinates(value){
  const c=value&&value.canonical||value;if(!c)return null;
  const {z,x,y}=c;
  return Number.isInteger(z)&&z>=0&&z<=22&&Number.isInteger(x)&&x>=0&&x<2**z&&Number.isInteger(y)&&y>=0&&y<2**z?{z,x,y}:null;
 }
 function observe(map){
  state.attached=true;
  for(const type of ['sourcedataabort','error']){
   const listener=event=>{
    const source=allowed.has(event.sourceId)?event.sourceId:null;
    const record={type,source,coord:coordinates(event.coord),epochMs:Date.now()};
    if(state.events.length<256)state.events.push(record);else state.dropped++;
   };
   map.on(type,listener);listeners.push({map,type,listener});
  }
 }
 // One synchronous page task defines the observation cutoff: all earlier event
 // callbacks have run, then listeners are removed before a snapshot is returned.
 state.finish=()=>{
  if(finished)throw new Error('source observer already finished');
  finished=true;
  if(!state.installed||!state.attached||!listeners.length)throw new Error('source observer unavailable');
  for(const item of listeners)item.map.off(item.type,item.listener);
  return {installed:state.installed,attached:state.attached,complete:true,cutoffEpochMs:Date.now(),events:state.events.slice(),dropped:state.dropped};
 };
 Object.defineProperty(window,'maplibregl',{configurable:true,enumerable:true,get(){return exported;},set(value){
  if(!value||typeof value.Map!=='function'){exported=value;return;}
  const original=value.Map;
  const wrapped=new Proxy(original,{construct(target,args,newTarget){const map=Reflect.construct(target,args,newTarget);observe(map);return map;}});
  // An ordinary export assignment is expected in the vendored UMD bundle.
  const descriptor=Object.getOwnPropertyDescriptor(value,'Map');
  if(!descriptor||!descriptor.writable){exported=value;return;}
  value.Map=wrapped;exported=value;state.installed=true;
 }});
}
function publicTile(host,path){
 const sources=[['tiles.openfreemap.org',/^\/natural_earth\/ne2sr\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.png$/,'ne2_shaded'],['tiles.openfreemap.org',/^\/(?:planet|tiles)\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.pbf$/,'openmaptiles'],['tiles.mapterhorn.com',/^\/(\d{1,2})\/(\d{1,7})\/(\d{1,7})\.webp$/,'terrain-dem']];
 for(const [h,re,source] of sources){if(host!==h)continue;const m=re.exec(path);if(!m)continue;const [z,x,y]=m.slice(1).map(Number);if(z<=22&&x<2**z&&y<2**z)return {source,z,x,y};}
 return null;
}
function makeHandlerTracker(handler,row){
 const pending=new Set();
 const run=route=>{
  const task=Promise.resolve().then(()=>handler(route)).catch(async()=>{row.handlerErrors++;await route.abort('blockedbyclient').catch(()=>{});});
  pending.add(task);task.then(()=>pending.delete(task));return task;
 };
 const drain=async timeout=>{
  const end=performance.now()+timeout;
  for(;;){
   if(!pending.size){await new Promise(resolve=>setImmediate(resolve));if(!pending.size)return true;}
   const remaining=end-performance.now();if(remaining<=0)return false;
   let timer;const done=await Promise.race([Promise.allSettled([...pending]).then(()=>true),new Promise(resolve=>{timer=setTimeout(()=>resolve(false),remaining);})]);
   clearTimeout(timer);if(!done)return false;
  }
 };
 return {run,drain};
}
function makeTrace(row){
 const start=performance.now(),ids=new WeakMap();let next=1;
 const mark=(kind,request,detail={})=>{
  let u;try{u=new URL(request.url());}catch(_){return;}
  if(!providers.has(u.hostname))return;
  if(!ids.has(request))ids.set(request,next++);
  const path=publicPathClass(u.hostname,u.pathname);
  const type=typeof request.resourceType==='function'?request.resourceType():'unknown';
  const record={id:ids.get(request),kind,host:u.hostname,path,resourceType:/^[a-z]{1,20}$/.test(type)?type:'unknown',tile:publicTile(u.hostname,u.pathname),phase:row.phase,ms:Math.round(performance.now()-start),epochMs:Date.now(),...detail};
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
 if(row.error||row.pageErrors||row.failedRequests||row.badResponses||row.blockedRequests||row.blockedRedirects||row.boundaryErrors||row.handlerErrors||row.handlerDrainTimeout||row.eventsDropped||row.sourceTraceDropped||row.sourceErrors||!row.sourceObservationComplete||!row.sourceObserverAttached||!row.sourcesLoaded||!row.rendererLoaded||!row.statusHidden||!row.canvasVisible||!row.openfreemapResponses||!row.mapterhornResponses)return 'FAIL';
 return 'PASS';
}
// This is a diagnostic result, not a release decision: any matched cancellation
// still requires an independent review of the actual provider screenshots.
function qualifiedStatus(row){
 const rawStatus=classify(row),cancellation=assessCancellation({...row,status:rawStatus});
 return {rawStatus,cancellation,status:rawStatus==='FAIL'&&cancellation.classification==='MATCHED_RENDERER_CANCELLATION'?'MATCHED_VISUAL_REVIEW_REQUIRED':rawStatus};
}
module.exports={classify,qualifiedStatus,allowedRequest,enforceRequest,makeTrace,makeHandlerTracker,publicPathClass,publicTile,installEarlySourceObserver};
async function run(){
 assert.equal(process.env.CI,'true','Hosted CI only');
 const {chromium}=require('playwright'),route='/timelines/world-and-scripture-timeline.html';
 const pageBytes=fs.readFileSync(path.join(root,route)),head=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
 const event=process.env.GITHUB_EVENT_PATH?JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH,'utf8')):{};
 const identity={checkout:head,pullRequestHead:event.pull_request?.head?.sha||null,workflowSha:process.env.GITHUB_SHA||null,runId:process.env.GITHUB_RUN_ID||null,runAttempt:process.env.GITHUB_RUN_ATTEMPT||null,pageSha256:sha(pageBytes),diagnosticSha256:sha(fs.readFileSync(__filename))};
 fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{try{const url=new URL(req.url,'http://localhost'),file=path.resolve(root,'.'+decodeURIComponent(url.pathname));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.json':'application/json'})[path.extname(file)]||'application/octet-stream'}).end(b));}catch(e){res.writeHead(400).end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin='http://127.0.0.1:'+server.address().port;
 let browser;const rows=[];
 try{
  browser=await chromium.launch({headless:true});
  for(const profile of [{name:'desktop',width:1366,height:900},{name:'phone',width:390,height:844}]){
   const context=await browser.newContext({viewport:{width:profile.width,height:profile.height},reducedMotion:'reduce',serviceWorkers:'block'});
   await context.routeWebSocket('**/*',socket=>socket.close());await context.addInitScript(installEarlySourceObserver);const page=await context.newPage();
   const row={profile:profile.name,phase:'setup',events:[],eventsDropped:0,mapEvents:[],denied:false,denial:null,requestErrors:[],responseErrors:[],pageErrors:0,failedRequests:0,badResponses:0,blockedRequests:0,blockedRedirects:0,boundaryErrors:0,handlerErrors:0,handlerDrainTimeout:false,openfreemapResponses:0,mapterhornResponses:0};let deniedResolve;
   const trace=makeTrace(row);
   const deniedSignal=new Promise(resolve=>deniedResolve=resolve);
   const tracker=makeHandlerTracker(route=>enforceRequest(route,origin,row,deniedResolve,trace.mark),row);
   await context.route('**/*',tracker.run);
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
   if(!row.denied){row.phase='map-trace';try{const m=await page.evaluate(()=>{const t=window.__providerSourceTrace,g=window.__englishMap,ids=['ne2_shaded','openmaptiles','terrain-dem'];const sourceTrace=t?t.finish():null;const sources={};for(const id of ids){try{sources[id]=g&&g.getSource(id)?g.isSourceLoaded(id):null;}catch(_){sources[id]=null;}}return {events:window.__providerMapTrace||[],dropped:window.__providerMapTraceDropped||0,sourceTrace,finalSources:sources};});row.mapEvents=m.events;row.mapEventsDropped=m.dropped;row.sourceObserverAttached=!!(m.sourceTrace&&m.sourceTrace.installed&&m.sourceTrace.attached);row.sourceObservationComplete=!!(m.sourceTrace&&m.sourceTrace.complete&&Number.isInteger(m.sourceTrace.cutoffEpochMs));row.sourceObservationCutoffEpochMs=m.sourceTrace?m.sourceTrace.cutoffEpochMs:null;row.sourceEvents=m.sourceTrace?m.sourceTrace.events:[];row.sourceErrors=row.sourceEvents.filter(e=>e.type==='error').length;row.sourceTraceDropped=m.sourceTrace?m.sourceTrace.dropped:1;row.finalSourceLoaded=m.finalSources;}catch(_){row.error='map event trace unavailable';}}
   row.phase='teardown';await context.close();row.phase='handler-drain';row.handlerDrainTimeout=!(await tracker.drain(5000));row.phase='closed';if(row.mapEventsDropped)row.error='map event trace incomplete';Object.assign(row,qualifiedStatus(row));rows.push(row);
   if(row.denied)break; // Never retry an explicit provider denial in another profile.
  }
 }finally{
  if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));
  for(const row of rows)Object.assign(row,qualifiedStatus(row));
  fs.writeFileSync(path.join(out,'provider-diagnostic.json'),JSON.stringify({identity,rows,releasePolicy:'A completed diagnostic is not release approval. Matched cancellation requires independent visual review of the exact run and source; later matched runs require fresh review or reconciliation.',limits:['Provider-backed hosted Chromium only; screenshot review and physical-device verification are separate.','Leaflet movement events are recorded only after monitor setup; source listeners attach immediately after the documented Map constructor returns, so constructor-internal synchronous events may be missed.', 'Source observation ends atomically at the reported cutoff before context teardown; later renderer events are outside the observed interval. Request events and handler draining continue through teardown.', 'Matched source and request cancellation is a bounded correlation, not proof of cause; rawStatus and all original events remain in the report. Any matched outcome requires a separate independent screenshot review before release.', 'Public isSourceLoaded reports source settlement, not a complete required-visible-tile success inventory; error events may omit source or coordinates.','Request failures during teardown are recorded and still fail the diagnostic.','Handler draining is bounded; timeout or handler errors fail the diagnostic.','Provider paths are classified using fixed public templates; other paths are redacted.','The deterministic isolated browser suite remains separate.']},null,2)+'\n');
 }
 assert.equal(rows.length,2,'Both desktop and phone provider checks are required');assert(rows.every(r=>r.status==='PASS'||r.status==='MATCHED_VISUAL_REVIEW_REQUIRED'),'Provider diagnostic failed; inspect bounded report and screenshots');
 console.log('Diagnostic completed, not a full provider pass or release approval; independent visual review of this run is required before release.');
}
if(require.main===module)run().catch(error=>{console.error(String(error));process.exitCode=1;});
