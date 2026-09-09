import assert from 'node:assert/strict';
import { evidenceForVerifier, providerDiagnostic, callGroq } from './src/index.js';
const sources = Array.from({length:6},(_,i)=>({host:'www.churchofjesuschrist.org',title:`Article ${i}`,url:`https://www.churchofjesuschrist.org/study/topic${i}`,content:'x'.repeat(4180)+`END-${i}`}));
const packed=evidenceForVerifier(sources);
for(const source of sources) assert(packed.includes(source.content));
assert(packed.length<40000);
assert.throws(()=>evidenceForVerifier([...sources,sources[0]]),/evidence-pack-limit/);
assert.throws(()=>evidenceForVerifier([{...sources[0],content:'x'.repeat(40001)}]),/evidence-pack-limit/);
function limited(message,delay){return {response:new Response('',{status:429,headers:delay===undefined?{}:{'retry-after':delay}}),data:{error:{code:'rate_limit_exceeded',message}}};}
assert.equal(providerDiagnostic(limited('Daily TPD quota secret-key','3600')).focuschrist_provider_rate_limit_category,'daily-quota');
assert.equal(providerDiagnostic(limited('tokens per minute try again in 20s')).focuschrist_provider_retry_after_seconds,20);
assert.equal(providerDiagnostic(limited('tokens per minute')).focuschrist_provider_rate_limit_category,'pacing');
assert.equal(providerDiagnostic(limited('try again in 2m3.5s')).focuschrist_provider_retry_after_seconds,124);
assert.equal(providerDiagnostic(limited('try again in 250ms')).focuschrist_provider_retry_after_seconds,1);
assert.equal(providerDiagnostic(limited('private data','invalid')).focuschrist_provider_retry_after_seconds,null);
const dateDelay=providerDiagnostic(limited('',new Date(Date.now()+60000).toUTCString())).focuschrist_provider_retry_after_seconds;
assert(dateDelay>=59 && dateDelay<=60);
assert.equal(providerDiagnostic(limited('private details')).focuschrist_provider_rate_limit_category,'unspecified');
assert(!JSON.stringify(providerDiagnostic(limited('secret-key private account','3600'))).includes('secret-key'));
const original=globalThis.fetch;let count=0;
try {
 globalThis.fetch=async()=>{count++;return new Response(JSON.stringify({error:{code:'rate_limit_exceeded',message:'Daily quota'}}),{status:429,headers:{'retry-after':'3600'}});};
 const result=await callGroq('test',{},Date.now()+10000);assert.equal(count,1);assert.equal(result.response.status,429);
 globalThis.fetch=async()=>{count++;return count===2?new Response(JSON.stringify({error:{code:'rate_limit_exceeded'}}),{status:429,headers:{'retry-after':'0'}}):new Response('{}',{status:200});};
 const retry=await callGroq('test',{},Date.now()+10000);assert.equal(retry.callCount,2);assert.equal(count,3);
} finally {globalThis.fetch=original;}
console.log('PASS: complete bounded source packs, safe quota diagnostics, respected cooldown and bounded retry.');
