import assert from 'node:assert/strict';
import worker, { captureReviewedSourceSnapshot, fetchOfficialSource } from './src/index.js';
import { verifyReviewedReading, sha256Text } from './src/reviewed-readings.js';
import { PIONEER_TOPIC_SOURCES } from './src/pioneer-topic-sources.js';
const original={fetch:globalThis.fetch,caches:globalThis.caches,setTimeout:globalThis.setTimeout,now:Date.now};
const candidate={url:PIONEER_TOPIC_SOURCES.winterquarters.url,title:'Winter Quarters',pioneerDisclosure:true,reviewedSourceRequired:true};
const question='Winter Quarters settlement westward migration';
const html='<p>Winter Quarters served as a settlement where emigrant families prepared for the westward migration. Its residents gathered supplies and organized their journey while enduring difficult living conditions.</p>';
const counters=()=>({attempts:0,cacheHits:0,cacheMisses:0});
let lastTimer,calls=0;
globalThis.setTimeout=(fn,ms,...args)=>{lastTimer=ms;return original.setTimeout(fn,ms,...args);};
globalThis.caches=undefined;
try {
  // Fast responses expose timer selection without waiting or using the network.
  globalThis.fetch=async()=>new Response('',{status:503});
  for(const [flags,limit] of [[{},9000],[{pioneerDisclosure:true},9000],[{reviewedSourceRequired:true},9000],[{pioneerDisclosure:true,reviewedSourceRequired:true},12000]]) {
    await fetchOfficialSource({...candidate,pioneerDisclosure:false,reviewedSourceRequired:false,...flags},question,Date.now()+24000,counters());
    assert.equal(lastTimer,limit,'only the server constructed reviewed Pioneer path gets 12 seconds');
  }
  await fetchOfficialSource(candidate,question,Date.now()+5000,counters());
  assert.ok(lastTimer>=2900 && lastTimer<=3000,'two seconds retained for review/response');
  const exhausted=counters();calls=0;
  globalThis.fetch=async()=>{calls++;throw Error('must not fetch');};
  await fetchOfficialSource(candidate,question,Date.now()+2200,exhausted);
  assert.equal(calls,0);assert.equal(exhausted.officialFailureClasses.budget,1);
  // A cache wait must not consume the reserved response budget before a new fetch.
  let offset=0;const actualNow=original.now;
  Date.now=()=>actualNow()+offset;
  globalThis.caches={default:{match:async()=>{offset=1000;return undefined;},put:async()=>{}}};
  const delayedCache=counters();
  await fetchOfficialSource(candidate,question,Date.now()+2500,delayedCache);
  assert.equal(calls,0);assert.equal(delayedCache.officialFailureClasses.budget,1);
  Date.now=original.now;globalThis.caches=undefined;
  // This is a real 9.5-second asynchronous fixture, beyond the old cap, with
  // an independently pinned fixture reading. It is not production evidence.
  globalThis.fetch=async(_url,options)=>new Promise((resolve,reject)=>{
    const timer=original.setTimeout(()=>resolve(new Response(html,{headers:{'Content-Type':'text/html'}})),9500);
    options.signal.addEventListener('abort',()=>{clearTimeout(timer);reject(new DOMException('aborted','AbortError'));},{once:true});
  });
  const started=Date.now(),slow=counters();
  const source=await fetchOfficialSource(candidate,question,started+24000,slow);
  assert(source);assert.equal(slow.attempts,1);assert.equal(slow.officialFailureClasses,undefined);
  assert(Date.now()-started>=9400 && Date.now()-started<24000);
  const snapshot=await captureReviewedSourceSnapshot(candidate,html);
  const answer='A fixture reading preserves the source hash and review binding while testing retrieval timing.';
  const fixture={schemaVersion:1,readings:{winterquarters:{answer,answerSha256:await sha256Text(answer),reviewRevision:'timeout-fixture-only',sources:[{url:candidate.url,sourceSha256:snapshot.sourceSha256,extractionVersion:snapshot.extractionVersion}]}}};
  assert.equal((await verifyReviewedReading('winterquarters',[source],[candidate.url],fixture))?.answer,answer);
  assert.equal(await verifyReviewedReading('winterquarters',[{...source,sourceSha256:'0'.repeat(64)}],[candidate.url],fixture),null,'extra time never waives source drift');
  // A hanging source is actually cancelled at the new cap; no second attempt.
  calls=0;globalThis.fetch=(_url,options)=>{calls++;return new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')),{once:true}));};
  const timed=counters(),abortStarted=Date.now();
  assert.equal(await fetchOfficialSource(candidate,question,abortStarted+24000,timed),null);
  assert.equal(calls,1);assert.equal(timed.officialFailureClasses.timeout,1);
  assert(Date.now()-abortStarted>=11900 && Date.now()-abortStarted<24000);
  for(const [status,body,type,kind] of [[403,'','text/html','httpOther'],[503,'','text/html','http5xx'],[200,'x'.repeat(1500001),'text/html','oversize'],[200,'{}','application/json','contentType']]) {
    globalThis.fetch=async()=>new Response(body,{status,headers:{'Content-Type':type}});
    const c=counters();assert.equal(await fetchOfficialSource(candidate,question,Date.now()+24000,c),null);assert.equal(c.officialFailureClasses[kind],1);
  }
  let providerCalls=0;
  globalThis.fetch=async(url)=>{if(!String(url).startsWith('https://www.churchofjesuschrist.org/'))providerCalls++;return new Response(html,{headers:{'Content-Type':'text/html'}});};
  const response=await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'pioneers',focuschrist_pioneer_topic:'winterquarters',messages:[{role:'user',content:question}]})}),{});
  const payload=await response.json();
  assert.equal(payload.focuschrist_gateway_mode,'reviewed-source-review-required');
  assert.equal(payload.focuschrist_source_integrity_verified,false);
  assert.equal(providerCalls,0,'changed reviewed source never falls through to AI');
  console.log('PASS: narrow12s/general9s,2sreserve,cache-budget recompute,real9.5s pinnedfixture success,real12s abort,no retry,drift/denial/oversize/type failclosed and zero-AI changed-source hold.');
} finally {
  globalThis.fetch=original.fetch;globalThis.caches=original.caches;globalThis.setTimeout=original.setTimeout;Date.now=original.now;
}

