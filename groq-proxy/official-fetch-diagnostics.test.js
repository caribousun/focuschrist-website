import assert from 'node:assert/strict';
import { fetchOfficialSource } from './src/index.js';
import { CLASSES, recordOfficialFailure, mergeOfficialFailureDiagnostics } from './src/official-fetch-diagnostics.js';
const originalFetch=globalThis.fetch;
const candidate={url:'https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/32?lang=eng',title:'Alma 32',deterministic:true};
let passed=0;
async function check(kind,fetcher,deadline=Date.now()+20000) {
 const counters={attempts:0,cacheHits:0,cacheMisses:0};let calls=0;
 globalThis.fetch=async(...args)=>{calls++;return fetcher(...args);};
 const result=await fetchOfficialSource(candidate,'Alma 32 faith',deadline,counters);
 assert.equal(result,null,'failed fetch must remain unserved');assert.equal(counters.officialFailureClasses?.[kind],1,kind);
 const diagnostic={};mergeOfficialFailureDiagnostics(diagnostic,counters);
 assert.equal(diagnostic['focuschrist_official_failure_'+kind],1);
 assert.equal(Object.keys(diagnostic).length,CLASSES.length);
 assert.ok(!JSON.stringify(diagnostic).includes('private-secret'));
 if(kind==='budget')assert.equal(calls,0,'budget exhaustion is pre-fetch');
 if(['network','timeout','http429','http5xx','budget'].includes(kind))assert.equal(counters.transportFailures,1,'legacy aggregate preserved');
 passed++;
}
try {
 await check('budget',()=>{throw Error('must not fetch');},Date.now()-1);
 await check('http429',()=>new Response('',{status:429}));
 await check('http5xx',()=>new Response('',{status:503}));
 await check('httpOther',()=>new Response('',{status:403}));
 await check('httpOther',()=>new Response('',{status:302,headers:{Location:'https://private-secret.example'}}));
 await check('contentType',()=>new Response('{}',{headers:{'Content-Type':'application/json'}}));
 await check('network',()=>{throw Error('private-secret URL/header/visitor text');});
 await check('timeout',()=>{throw new DOMException('private-secret','AbortError');});
 await check('oversize',()=>new Response('x'.repeat(1500001),{headers:{'Content-Type':'text/html'}}));
 await check('noEvidence',()=>new Response('<html><body></body></html>',{headers:{'Content-Type':'text/html'}}));
 const c={};recordOfficialFailure(c,'private-secret');assert.equal(c.officialFailureClasses,undefined);passed++;
 const bounded={};for(let i=0;i<1002;i++)recordOfficialFailure(bounded,'network');assert.equal(bounded.officialFailureClasses.network,1000);passed++;
 const target={};mergeOfficialFailureDiagnostics(target,{officialFailureClasses:{network:2}});mergeOfficialFailureDiagnostics(target,{officialFailureClasses:{network:3}});assert.equal(target.focuschrist_official_failure_network,5);passed++;
 console.log(`PASS ${passed} actual fetch/aggregate/privacy cases; unchanged fail-closed returns and legacy counters`);
} finally {globalThis.fetch=originalFetch;}
