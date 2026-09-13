import assert from 'node:assert/strict';
import reviewedReadings from '../groq-proxy/src/reviewed-readings.json' with {type:'json'};
const endpoint=process.env.FOCUSCHRIST_ENDPOINT || 'https://focuschrist-groq-proxy.caribousun.workers.dev';
const policy=process.env.FOCUSCHRIST_EXPECTED_POLICY || '2026-09-13.94';
async function request(page,messages){
 const r=await fetch(endpoint,{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:page,focuschrist_profile:'faith-study',messages}),signal:AbortSignal.timeout(26000)});
 const p=await r.json();
 assert.equal(r.status,200,JSON.stringify({page,messages,p}));
 assert.equal(p.focuschrist_source_policy,policy);
 assert.equal(p.focuschrist_source_integrity_verified,true,JSON.stringify({page,messages,p}));
 assert.equal(p.focuschrist_scripture_validated,true);
 assert.ok(p.focuschrist_sources?.length);
 return p;
}
const cases=[
 {first:'where is god in the old testament',next:'is he the same god that is in the new testament',expected:[/jesus|christ/i,/old testament|jehovah/i,/new testament|father/i]},
 {first:'what year did the pioneer exodus begin',next:'when did it end',expected:[/1846|1847|1868|1869/,/nauvoo|pioneer|migration/i],pioneerDates:true}
];
for(const page of ['ask','pioneers']) for(const test of cases){
 const start=Date.now();
 const firstMessages=[{role:'user',content:test.first}];
 const first=await request(page,firstMessages);
 const firstAnswer=first.choices?.[0]?.message?.content;
 assert.ok(firstAnswer?.trim(),'First turn must return a real verified answer');
 const messages=[...firstMessages,{role:'assistant',content:firstAnswer},{role:'user',content:test.next}];
 const p=await request(page,messages);
 const answer=p.choices?.[0]?.message?.content||'';
 assert.equal(p.focuschrist_classification_mode,'conversation-context');
 for(const pattern of test.expected)assert.match(answer,pattern);
 if(!test.pioneerDates){
  const reviewed=reviewedReadings.readings['god-across-testaments'];
  assert.equal(answer,reviewed.answer,'The comparison must preserve the reviewed referent and source distinction');
  assert.equal(p.focuschrist_reviewed_reading_status,'verified-current-source');
  assert.equal(p.focuschrist_review_revision,reviewed.reviewRevision);
  assert.equal(p.focuschrist_openai_verifier_calls,0);
 }
 if(test.pioneerDates){
  const sentences=answer.split(/(?<=[.!?])\s+|\n+/);
  for(const sentence of sentences){
   const wrongNauvooDeparture=/\b1847\b/.test(sentence)
    && /\bNauvoo\b/i.test(sentence)
    && /\b(?:left|departed|departure|leaving|leav(?:e|es|ing)|exodus began)\b/i.test(sentence)
    && !/\b(?:1846|not|rather than|instead of)\b/i.test(sentence);
   assert.equal(wrongNauvooDeparture,false,`Unsupported 1847 Nauvoo departure claim: ${sentence}`);
  }
 }
 assert.ok(p.focuschrist_sources.every(source=>{const h=new URL(source.url).hostname;return h==='churchofjesuschrist.org'||h.endsWith('.churchofjesuschrist.org');}));
 console.log(JSON.stringify({page,firstQuestion:test.first,firstAnswer,question:test.next,answer,sources:p.focuschrist_sources,policy:p.focuschrist_source_policy,durationMs:Date.now()-start}));
}
console.log('PASS: live comparison and event-end follow-ups on Ask and Pioneer.');
