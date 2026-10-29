/* Synthetic classification only; it does not run a browser or prove providers. */
'use strict';
const assert=require('node:assert/strict'),{classify,allowedRequest,enforceRequest,makeTrace,makeHandlerTracker,publicPathClass,publicTile,installEarlySourceObserver}=require('./world_provider_browser_diagnostic');
const ok={denied:false,pageErrors:0,failedRequests:0,badResponses:0,blockedRequests:0,blockedRedirects:0,boundaryErrors:0,openfreemapResponses:1,mapterhornResponses:1,sourcesLoaded:true,rendererLoaded:true,statusHidden:true,canvasVisible:true,sourceObserverAttached:true,sourceObservationComplete:true};
assert.equal(classify(ok),'PASS');
for(const field of ['sourcesLoaded','rendererLoaded','statusHidden','canvasVisible','openfreemapResponses','mapterhornResponses','sourceObserverAttached','sourceObservationComplete'])assert.equal(classify({...ok,[field]:false}),'FAIL',field);
for(const field of ['pageErrors','failedRequests','badResponses','blockedRequests','blockedRedirects','boundaryErrors','handlerErrors','handlerDrainTimeout','sourceTraceDropped','sourceErrors'])assert.equal(classify({...ok,[field]:1}),'FAIL',field);
assert.equal(classify({...ok,eventsDropped:1}),'FAIL');
assert.equal(classify({...ok,error:'failure'}),'FAIL');assert.equal(classify({...ok,denied:true}),'DENIED');assert.equal(classify({}),'FAIL');
function earlyObserverTests(){
 const originalWindow=global.window;global.window={};
 try{
  installEarlySourceObserver();
  class MapStub{constructor(){this.listeners={};}on(name,fn){this.listeners[name]=fn;return this;}off(name,fn){assert.equal(this.listeners[name],fn);delete this.listeners[name];return this;}emit(name,event){if(this.listeners[name])this.listeners[name](event);}}
  window.maplibregl={Map:MapStub};assert(window.__providerSourceTrace.installed);
  const map=new window.maplibregl.Map();assert(window.__providerSourceTrace.attached);
  map.emit('sourcedataabort',{sourceId:'ne2_shaded',coord:{canonical:{z:2,x:1,y:3}}});
  map.emit('error',{sourceId:'private-source-name',coord:{z:2,x:9,y:3},error:{message:'private error'}});
  const records=window.__providerSourceTrace.events;
  assert.deepEqual(records[0].coord,{z:2,x:1,y:3});assert.equal(records[0].source,'ne2_shaded');
  assert.equal(records[1].source,null);assert.equal(records[1].coord,null);assert(!JSON.stringify(records).includes('private'));
  assert(Number.isInteger(records[0].epochMs));
  for(let i=0;i<255;i++)map.emit('error',{});assert.equal(records.length,256);assert.equal(window.__providerSourceTrace.dropped,1);
  assert.equal(classify({...ok,sourceTraceDropped:1}),'FAIL');assert.equal(classify({...ok,sourceErrors:1}),'FAIL');
  // An error arriving after prior inspection but before the cutoff must be in the returned snapshot.
  installEarlySourceObserver();window.maplibregl={Map:MapStub};const lateMap=new window.maplibregl.Map(),late=window.__providerSourceTrace;
  assert.equal(late.events.length,0);lateMap.emit('error',{sourceId:'ne2_shaded'});
  const snapshot=late.finish();assert(snapshot.complete);assert.equal(snapshot.events.length,1);assert.equal(snapshot.events[0].type,'error');
  assert.equal(classify({...ok,sourceErrors:snapshot.events.filter(e=>e.type==='error').length}),'FAIL');
  lateMap.emit('error',{sourceId:'ne2_shaded'});assert.equal(snapshot.events.length,1); // Outside the explicit cutoff.
  assert.throws(()=>late.finish(),/already finished/);
  installEarlySourceObserver();window.maplibregl={Map:MapStub};const broken=new window.maplibregl.Map();broken.off=()=>{throw Error('synthetic detach failure');};
  assert.throws(()=>window.__providerSourceTrace.finish(),/detach failure/);
  assert.equal(classify({...ok,sourceObservationComplete:false}),'FAIL');
  assert.equal(classify({...ok,failedRequests:1}),'FAIL'); // A matched or unmatched abort never becomes PASS.
  assert.deepEqual(publicTile('tiles.openfreemap.org','/natural_earth/ne2sr/2/1/3.png'),{source:'ne2_shaded',z:2,x:1,y:3});
  assert.deepEqual(publicTile('tiles.openfreemap.org','/planet/2/1/3.pbf'),{source:'openmaptiles',z:2,x:1,y:3});
  assert.deepEqual(publicTile('tiles.mapterhorn.com','/2/1/3.webp'),{source:'terrain-dem',z:2,x:1,y:3});
  for(const path of ['/customer/private','/natural_earth/ne2sr/2/99/3.png','/natural_earth/ne2sr/%32/1/3.png'])assert.equal(publicTile('tiles.openfreemap.org',path),null);
  assert.equal(publicTile('example.com','/2/1/3.webp'),null);
 }finally{global.window=originalWindow;}
}
earlyObserverTests();
async function routingTests(){
 const rowTrace={phase:'navigation',events:[],eventsDropped:0},trace=makeTrace(rowTrace);
 const req={url:()=>"https://tiles.openfreemap.org/tiles/2/1/3.pbf?token=secret",resourceType:()=>"fetch"};
 trace.mark('request',req);rowTrace.phase='teardown';trace.mark('request-failed',req,{code:'net::ERR_ABORTED'});
 assert.equal(rowTrace.events[0].path,'/tiles/{z}/{x}/{y}.pbf');assert.equal(rowTrace.events[1].phase,'teardown');assert.equal(rowTrace.events[0].id,rowTrace.events[1].id);assert(!JSON.stringify(rowTrace).includes('secret'));
 const secretPath={url:()=>"https://tiles.openfreemap.org/token/hidden",resourceType:()=>"fetch"};trace.mark('request',secretPath);assert.equal(rowTrace.events[2].path,'[redacted]');
 const encodedSecret={url:()=>"https://tiles.openfreemap.org/%74%6f%6b%65%6e/hidden",resourceType:()=>"fetch"};trace.mark('request',encodedSecret);assert.equal(rowTrace.events[3].path,'[redacted]');
 for(const path of ['/customer/jane-doe','/f7d602a1-49c5-49fb-8adb-a35e8fb56352','/tiles/987654321/22/44.pbf','/tiles/2/1234/3.pbf','/planet/1234567890123456','/planet/%32/1/3.pbf'])assert.equal(publicPathClass('tiles.openfreemap.org',path),'[redacted]',path);
 assert.equal(publicPathClass('tiles.openfreemap.org','/planet'),'/planet');assert.equal(publicPathClass('tiles.mapterhorn.com','/2/1/3.webp'),'/{z}/{x}/{y}.webp');assert.equal(publicPathClass('tiles.mapterhorn.com','/planet'),'[redacted]');
 for(let i=0;i<509;i++)trace.mark('request',req);assert.equal(rowTrace.events.length,512);assert.equal(rowTrace.eventsDropped,1);
 const origin='http://127.0.0.1:12345',good=['http://127.0.0.1:12345/index.html','https://tiles.openfreemap.org/planet','https://tiles.mapterhorn.com/0/0/0.webp'];
 const bad=['http://example.com/','http://tiles.openfreemap.org/','https://tiles.openfreemap.org.evil.test/','https://tiles.openfreemap.org:444/','https://user@tiles.openfreemap.org/','http://localhost:12345/','http://127.0.0.1:12346/','data:text/plain,x'];
 for(const url of good)assert(allowedRequest(url,origin),url);
 for(const url of bad)assert(!allowedRequest(url,origin),url);
 const mkrow=()=>({denied:false,denial:null,blockedRequests:0,blockedRedirects:0,boundaryErrors:0,badResponses:0,responseErrors:[]});
 const stub=(url,status,method='GET')=>{
  const calls=[],response={status:()=>status,dispose:async()=>calls.push('dispose')};
  return {calls,route:{request:()=>({url:()=>url,method:()=>method}),fetch:async opts=>{calls.push(['fetch',opts]);return response;},abort:async()=>calls.push('abort'),fulfill:async()=>calls.push('fulfill')}};
 };
 for(const url of bad){const r=stub(url,200),row=mkrow();await enforceRequest(r.route,origin,row,()=>{});assert.deepEqual(r.calls,['abort']);assert.equal(row.blockedRequests,1);}
 for(const status of [301,302,303,307,308]){
  const r=stub(good[1],status),row=mkrow();await enforceRequest(r.route,origin,row,()=>{});
  assert.deepEqual(r.calls,[['fetch',{maxRedirects:0,maxRetries:0,timeout:15000}],'dispose','abort']);assert.equal(row.blockedRedirects,1);
 }
 const goodCase=stub(good[1],200),goodRow=mkrow();await enforceRequest(goodCase.route,origin,goodRow,()=>{});
 assert.deepEqual(goodCase.calls,[['fetch',{maxRedirects:0,maxRetries:0,timeout:15000}],'fulfill','dispose']);
 const timedRow={phase:'waiting',events:[],eventsDropped:0},timedTrace=makeTrace(timedRow),traced=stub(good[1],200);
 await enforceRequest(traced.route,origin,mkrow(),()=>{},timedTrace.mark);
 assert.deepEqual(timedRow.events.map(e=>e.kind),['route-fetch-start','route-fetch-response','route-fulfilled']);
 assert(timedRow.events.every(e=>e.id===timedRow.events[0].id&&e.phase==='waiting'&&Number.isInteger(e.ms)));
 const failed=stub(good[1],200),failedRow=mkrow();failed.route.fetch=async()=>{throw new Error('net::ERR_ABORTED private-token-should-not-appear');};
 await enforceRequest(failed.route,origin,failedRow,()=>{},timedTrace.mark);
 assert.equal(failedRow.boundaryErrors,1);assert.equal(timedRow.events.at(-1).code,'net::ERR_ABORTED');assert(!JSON.stringify(timedRow).includes('private-token'));
 let signalled=0;const denied=stub(good[1],403),deniedRow=mkrow();await enforceRequest(denied.route,origin,deniedRow,()=>signalled++);
 assert(deniedRow.denied);assert.equal(signalled,1);assert.deepEqual(denied.calls,[['fetch',{maxRedirects:0,maxRetries:0,timeout:15000}],'dispose','abort']);
 const after=stub(good[2],200);await enforceRequest(after.route,origin,deniedRow,()=>{});assert.deepEqual(after.calls,['abort']);
 const post=stub(good[1],200,'POST');await enforceRequest(post.route,origin,mkrow(),()=>{});assert.deepEqual(post.calls,['abort']);
 const trackedRow={handlerErrors:0};let release;
 const tracker=makeHandlerTracker(()=>new Promise(resolve=>{release=resolve;}),trackedRow),work=tracker.run({});await Promise.resolve();
 const draining=tracker.drain(200);release();assert.equal(await draining,true);await work;
 let releaseSlow;const slowRow={handlerErrors:0},slow=makeHandlerTracker(()=>new Promise(resolve=>{releaseSlow=resolve;}),slowRow),pending=slow.run({});await Promise.resolve();
 assert.equal(await slow.drain(5),false);assert.equal(classify({...ok,handlerDrainTimeout:true}),'FAIL');releaseSlow();await pending;
 const thrownRow={handlerErrors:0},aborts=[];const throwing=makeHandlerTracker(()=>{throw Error('synthetic');},thrownRow);await throwing.run({abort:async code=>aborts.push(code)});assert.equal(thrownRow.handlerErrors,1);assert.deepEqual(aborts,['blockedbyclient']);assert.equal(await throwing.drain(200),true);
 console.log('PASS: synthetic fail-closed request, redirect, denial and report cases; no network used.');
}
routingTests().catch(e=>{console.error(e);process.exitCode=1;});
