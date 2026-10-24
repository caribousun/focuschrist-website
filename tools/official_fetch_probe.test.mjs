import assert from 'node:assert/strict';
import { observe, summarize, FAILURE_CLASSES, ENDPOINT, REQUEST } from './official_fetch_probe.mjs';
const payload = Object.fromEntries(FAILURE_CLASSES.map(k => ['focuschrist_official_failure_'+k,0]));
payload.focuschrist_official_failure_timeout=1;
payload.focuschrist_gateway_mode='reviewed-source-review-required';
payload.focuschrist_source_policy='2026-09-13.94';
payload.focuschrist_official_fetch_calls=1;
payload.focuschrist_official_cache_hits=0;
payload.focuschrist_official_cache_misses=1;
payload.focuschrist_source_transport_failures=1;
payload.choices=[{message:{content:'PRIVATE ANSWER'}}];
payload.focuschrist_sources=[{url:'https://secret.example/PRIVATE'}];
payload.error='PRIVATE EXCEPTION';
let calls=0;
const result=await observe(async(url,options)=>{
  calls++;
  assert.equal(url,ENDPOINT);
  assert.equal(options.method,'POST');
  assert.deepEqual(options.headers,{Origin:'https://focuschrist.com','Content-Type':'application/json'});
  assert.deepEqual(JSON.parse(options.body),REQUEST);
  assert.ok(options.signal instanceof AbortSignal);
  return {ok:true,status:200,json:async()=>payload};
},()=>100);
assert.equal(calls,1);
assert.equal(result.diagnostic.classes.timeout.value,1);
assert.equal(result.diagnostic.diagnosticFieldsComplete,true);
assert.equal(result.diagnostic.invalidNumericField,false);
assert.equal(JSON.stringify(result).includes('PRIVATE'),false);
const missing=summarize({});
assert.equal(missing.classes.timeout.state,'missing');
assert.equal(missing.classes.timeout.value,null);
assert.equal(missing.diagnosticFieldsComplete,false);
for(const invalid of [-1,1.5,1001,'1',null]) {
  assert.equal(summarize({...payload,focuschrist_official_failure_timeout:invalid}).classes.timeout.state,'invalid');
}
const hostile=summarize({...payload,focuschrist_gateway_mode:'PRIVATE https://secret.example'});
assert.equal(hostile.gatewayMode,null);
let reads=0;
const denied=await observe(async()=>{calls++;return{ok:false,status:403,json:async()=>{reads++;throw Error('PRIVATE')}};});
assert.equal(denied.observation,'http-failure');assert.equal(reads,0);
for(const name of ['TimeoutError','AbortError','OtherError']) {
  let attempts=0;
  const failure=await observe(async()=>{attempts++;const e=Error('PRIVATE');e.name=name;throw e;});
  assert.equal(attempts,1);assert.equal(JSON.stringify(failure).includes('PRIVATE'),false);
}
assert.equal((await observe(async()=>({ok:true,status:200,json:async()=>{throw Error('PRIVATE');}}))).observation,'invalid-json');
assert.equal((await observe(async()=>({ok:true,status:200,json:async()=>[]}))).observation,'invalid-payload');
console.log('PASS: fixed request, one attempt, numeric/missing fields, privacy, HTTP denial, timeout/network and malformed payload.');

