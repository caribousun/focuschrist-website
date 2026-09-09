import assert from 'node:assert/strict';
import worker from './src/index.js';
const originalFetch=globalThis.fetch;
const draft='Prayer can help a person seek direction while thinking carefully about an important decision. It invites a sincere conversation with God about needs, concerns, and hopes. A person should consider what is known, examine available choices, and remain willing to learn. This process does not promise that every answer comes immediately or in the form someone expects. Patient attention can help a person recognize what needs further thought. The question calls for thoughtful preparation together with spiritual openness. These practices can support deliberate choices without replacing personal responsibility. They encourage a person to keep learning and to seek understanding as circumstances become clearer over time.';
const json=value=>new Response(JSON.stringify(value),{headers:{'Content-Type':'application/json'}});
try {
 for(const auditMode of ['reject','unavailable','correct']){
  let audits=0;
  globalThis.fetch=async(url,options={})=>{
   const address=String(url);
   if(address.endsWith('/chat/completions')){
    const prompt=JSON.parse(options.body).messages.map(x=>x.content).join(' ');
    if(prompt.includes('Act as a skeptical source editor')){
     audits++;assert(prompt.includes('PROPOSED ANSWER:'));assert(prompt.includes('EVIDENCE:'));
     if(auditMode==='unavailable')return new Response('{}',{status:503});
     return json({choices:[{message:{content:JSON.stringify({approved:auditMode==='correct',answer:auditMode==='correct'?draft.replace('Prayer can help','Sincere prayer can help'):'',source_indexes:auditMode==='correct'?[1]:[]})}}]});
    }
    return json({choices:[{message:{content:JSON.stringify({approved:true,answer:draft,source_indexes:[1]})}}]});
   }
   if(address.endsWith('/responses'))throw Error('Indexed fixture should not require search');
   return new Response('<p>Prayer guides important decisions and is a way of communicating with Heavenly Father. People may ask Him for guidance and seek spiritual direction. Studying a problem carefully and considering available options accompanies prayer. We may need patience when answers do not arrive as expected.</p>',{headers:{'Content-Type':'text/html'}});
  };
  const result=await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',focuschrist_profile:'faith-study',messages:[{role:'user',content:'How can prayer guide important decisions?'}]})}),{OPENAI_API_KEY:'offline-test'});
  const payload=await result.json();assert.equal(audits,1,JSON.stringify(payload));
  assert.equal(payload.focuschrist_openai_verifier_calls,2,'composition and audit calls must both be accounted for, including audit outage');
  assert.equal(payload.focuschrist_source_integrity_verified,auditMode==='correct',JSON.stringify(payload));
  if(auditMode==='correct')assert(payload.choices[0].message.content.startsWith('Sincere prayer'));
  else assert(!payload.choices[0].message.content.includes(draft),'audit failure must not publish original approved draft');
 }
 console.log('Relationship audit QA PASS: separate critic invoked; rejection/provider failure fail closed; correction survives final guards.');
}finally{globalThis.fetch=originalFetch;}

