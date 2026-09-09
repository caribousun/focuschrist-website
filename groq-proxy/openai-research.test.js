import assert from 'node:assert/strict';
import worker, {callApprovedResearch,callVerifier,collectSourceEvidence,hydrateResearchEvidence} from './src/index.js';
const original=globalThis.fetch;
const approved='https://www.churchofjesuschrist.org/study/general-conference/2025/04/forgiveness';
const body={messages:[{role:'system',content:'UNTRUSTED SYSTEM CLAIM'},{role:'user',content:'How can forgiveness rebuild trust?'}]};
const env={RESEARCH_PROVIDER:'openai',VERIFIER_PROVIDER:'openai',OPENAI_API_KEY:'offline-test',GROQ_KEY_NEW:'must-not-use'};
const response=data=>new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}});
const completed={status:'completed',output:[{type:'web_search_call',status:'completed',action:{sources:[{type:'url',url:approved},{type:'url',url:'https://churchofjesuschrist.org.evil.example/article'},{type:'url',url:'https://user:pass@www.churchofjesuschrist.org/study/article'},{type:'url',url:'https://unapproved.rsc.byu.edu/article'}]}},{type:'message',content:[{type:'output_text',text:'UNVERIFIED ANSWER MUST NEVER BECOME DRAFT'}]}]};
let calls=0;
try{
 globalThis.fetch=async(url,options)=>{calls++;assert.equal(String(url),'https://api.openai.com/v1/responses');const request=JSON.parse(options.body);assert.equal(request.model,'gpt-5.6-luna');assert.equal(request.max_tool_calls,1);assert.equal(request.max_output_tokens,900);assert.equal(request.store,false);assert.equal(request.tool_choice.type,'web_search');assert(request.tools[0].filters.allowed_domains.includes('churchofjesuschrist.org'));assert(request.tools[0].filters.allowed_domains.includes('rsc.byu.edu'));assert(!JSON.stringify(request.input).includes('UNTRUSTED'));assert.deepEqual(request.include,['web_search_call.action.sources']);return response(completed);};
 const diagnostic={};const result=await callApprovedResearch(env,body,Date.now()+22000,diagnostic);
 assert.equal(calls,1);assert.equal(result.data.choices[0].message.content,'');const leads=collectSourceEvidence(result.data.choices[0].message);assert.deepEqual(leads.map(x=>x.url),[approved]);assert.equal(leads[0].content,'');
 await callApprovedResearch(env,body,Date.now()+22000,diagnostic);assert.equal(calls,1,'one Responses request maximum across request phases');
 for(const payload of [{status:'incomplete',output:completed.output},{status:'failed',output:completed.output},{status:'completed',output:[completed.output[1]]},{status:'completed',output:[{...completed.output[0],status:'failed'}]}]){globalThis.fetch=async()=>response(payload);assert.equal((await callApprovedResearch(env,body,Date.now()+22000,{})).response.ok,false);}
 globalThis.fetch=async()=>response({...completed,status:'incomplete',incomplete_details:{reason:'max_output_tokens'}});
 const partialDiagnostic={};const partial=await callApprovedResearch(env,body,Date.now()+22000,partialDiagnostic);
 assert.equal(partial.response.ok,true);assert.equal(partial.data.choices[0].message.content,'');assert.equal(collectSourceEvidence(partial.data.choices[0].message).length,1);
 assert.equal(partialDiagnostic.focuschrist_openai_research_http_status,200);assert.equal(partialDiagnostic.focuschrist_openai_research_response_status,'incomplete');assert.equal(partialDiagnostic.focuschrist_openai_research_incomplete_reason,'max_output_tokens');assert.equal(partialDiagnostic.focuschrist_openai_research_search_status,'completed');
 for(const reason of ['content_filter','private-secret-value']){globalThis.fetch=async()=>response({...completed,status:'incomplete',incomplete_details:{reason}});const diagnostic={};const rejected=await callApprovedResearch(env,body,Date.now()+22000,diagnostic);assert.equal(rejected.response.ok,false);assert(!JSON.stringify(diagnostic).includes('private-secret-value'));}
 globalThis.fetch=async()=>new Response('',{status:302,headers:{location:'https://evil.example'}});
 assert.equal((await hydrateResearchEvidence(leads,'forgiveness trust',Date.now()+10000,{})).length,0,'redirect article must never become evidence');
 globalThis.fetch=async()=>new Response('<p>Forgiveness and trust require an honest willingness to listen carefully and acknowledge hurt. People may need patient effort and meaningful changes in conduct as they consider how relationships can become more dependable over time.</p>',{headers:{'Content-Type':'text/html'}});
 assert.equal((await hydrateResearchEvidence(leads,'forgiveness trust',Date.now()+10000,{})).length,1,'actual fetched approved text required');
 globalThis.fetch=async(_url,options)=>new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('private failure','AbortError'))));
 const timeout=await callApprovedResearch(env,body,Date.now()+7600,{});assert.equal(timeout.response.status,504);
 globalThis.fetch=async(url)=>{assert.equal(String(url),'https://api.openai.com/v1/chat/completions');return response({choices:[{message:{content:JSON.stringify({approved:false,answer:'',source_indexes:[]})}}]});};
 for(const forceOpenAI of [false,true]){const verified=await callVerifier(env,body,Date.now()+10000,{forceOpenAI,requireSourceIndexes:true});assert.equal(verified.totalOpenAIVerifierCalls,1);assert.equal(verified.verifierRoute,forceOpenAI?'openai-repair':'openai-primary');}
 globalThis.fetch=async(_url,options)=>({text:()=>new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('stalled body','AbortError'))))});
 const stalled=await callVerifier(env,body,Date.now()+350,{requireSourceIndexes:true});
 assert.equal(stalled.response.status,504,'verifier timeout must include the response body after headers');
 for (const indexed of [false,true]) {
  let searches=0,verifications=0,articles=0;
  globalThis.fetch=async(url,options={})=>{
   const address=String(url);assert(!address.includes('groq.com'),'legacy provider must never be contacted');
   if(address.endsWith('/v1/responses')){searches++;return response(completed);}
   if(address.endsWith('/v1/chat/completions')){verifications++;const prompt=JSON.parse(options.body).messages.map(x=>x.content).join(' ');assert(!prompt.includes('UNVERIFIED ANSWER MUST NEVER BECOME DRAFT'));return response({choices:[{message:{content:JSON.stringify({approved:false,answer:'',source_indexes:[]})}}]});}
   if(address===approved || indexed){articles++;return new Response('<p>Forgiveness and trust require careful listening, acknowledging harm, and patient effort. Mutual trust can develop through consistent actions that show responsibility and respect for another person. An honest apology does not automatically restore every relationship or remove the need for appropriate boundaries.</p>',{headers:{'Content-Type':'text/html'}});}
   return new Response('',{status:404});
  };
  const result=await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',focuschrist_profile:'faith-study',messages:[{role:'user',content:'How can forgiveness rebuild trust?'}]})}),env);
  const payload=await result.json();assert.equal(searches,1,'initial or rejected-index route must use one approved search');assert(articles>0 && verifications>0);assert.equal(payload.focuschrist_source_integrity_verified,false,'rejected source interpretation must never publish');
  if(indexed)assert.equal(payload.focuschrist_research_escalated,true);
 }
 console.log('PASS: OpenAI primary search/verifier with zero Groq, approved URL leads only, hydration/redirect gates, incomplete/no-tool rejection, timeout and one-call bound.');
}finally{globalThis.fetch=original;}
