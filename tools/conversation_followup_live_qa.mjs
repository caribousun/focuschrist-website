import assert from 'node:assert/strict';
const endpoint='https://focuschrist-groq-proxy.caribousun.workers.dev';
const cases=[
 {first:'where is god in the old testament',next:'is he the same god that is in the new testament',expected:[/jesus|christ/i,/old testament|jehovah/i,/new testament|father/i]},
 {first:'what year did the pioneer exodus begin',next:'when did it end',expected:[/1846|1847|1868|1869/,/nauvoo|pioneer|migration/i],pioneerDates:true}
];
for(const page of ['ask','pioneers']) for(const test of cases){
 const messages=[{role:'user',content:test.first},{role:'assistant',content:'Please continue with your question.'},{role:'user',content:test.next}];
 const start=Date.now();const r=await fetch(endpoint,{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:page,focuschrist_profile:'faith-study',messages}),signal:AbortSignal.timeout(26000)});
 const p=await r.json();const answer=p.choices?.[0]?.message?.content||'';
 assert.equal(r.status,200);assert.equal(p.focuschrist_source_policy,'2026-09-09.76');
 assert.equal(p.focuschrist_classification_mode,'conversation-context');
 assert.equal(p.focuschrist_source_integrity_verified,true,`${page}: ${test.next}: ${p.focuschrist_gateway_mode}`);
 assert.equal(p.focuschrist_scripture_validated,true);assert.ok(p.focuschrist_sources?.length);
 for(const pattern of test.expected)assert.match(answer,pattern);
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
 console.log(JSON.stringify({page,question:test.next,answer,sources:p.focuschrist_sources,policy:p.focuschrist_source_policy,durationMs:Date.now()-start}));
}
console.log('PASS: live comparison and event-end follow-ups on Ask and Pioneer.');
