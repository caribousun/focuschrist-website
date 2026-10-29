/* Synthetic classification only; it does not run a browser or prove providers. */
'use strict';
const assert=require('node:assert/strict'),{classify,allowedRequest,enforceRequest,makeTrace}=require('./world_provider_browser_diagnostic');
const ok={denied:false,pageErrors:0,failedRequests:0,badResponses:0,blockedRequests:0,blockedRedirects:0,boundaryErrors:0,openfreemapResponses:1,mapterhornResponses:1,sourcesLoaded:true,rendererLoaded:true,statusHidden:true,canvasVisible:true};
assert.equal(classify(ok),'PASS');
for(const field of ['sourcesLoaded','rendererLoaded','statusHidden','canvasVisible','openfreemapResponses','mapterhornResponses'])assert.equal(classify({...ok,[field]:false}),'FAIL',field);
for(const field of ['pageErrors','failedRequests','badResponses','blockedRequests','blockedRedirects','boundaryErrors'])assert.equal(classify({...ok,[field]:1}),'FAIL',field);
assert.equal(classify({...ok,eventsDropped:1}),'FAIL');
assert.equal(classify({...ok,error:'failure'}),'FAIL');assert.equal(classify({...ok,denied:true}),'DENIED');assert.equal(classify({}),'FAIL');
async function routingTests(){
 const rowTrace={phase:'navigation',events:[],eventsDropped:0},trace=makeTrace(rowTrace);
 const req={url:()=>"https://tiles.openfreemap.org/tiles/1/2/3.pbf?token=secret",resourceType:()=>"fetch"};
 trace.mark('request',req);rowTrace.phase='teardown';trace.mark('request-failed',req,{code:'net::ERR_ABORTED'});
 assert.equal(rowTrace.events[0].path,'/tiles/1/2/3.pbf');assert.equal(rowTrace.events[1].phase,'teardown');assert.equal(rowTrace.events[0].id,rowTrace.events[1].id);assert(!JSON.stringify(rowTrace).includes('secret'));
 const secretPath={url:()=>"https://tiles.openfreemap.org/token/hidden",resourceType:()=>"fetch"};trace.mark('request',secretPath);assert.equal(rowTrace.events[2].path,'[redacted]');
 const encodedSecret={url:()=>"https://tiles.openfreemap.org/%74%6f%6b%65%6e/hidden",resourceType:()=>"fetch"};trace.mark('request',encodedSecret);assert.equal(rowTrace.events[3].path,'[redacted]');
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
 console.log('PASS: synthetic fail-closed request, redirect, denial and report cases; no network used.');
}
routingTests().catch(e=>{console.error(e);process.exitCode=1;});
