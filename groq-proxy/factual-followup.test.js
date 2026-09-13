import assert from 'node:assert/strict';
import { isNarrowFactualFollowup } from './src/factual-followup.js';
const scope = question => ({question,classificationMode:'conversation-context',faith:true});
for (const question of ['When did it end?', 'What year was that?', 'Where was it printed?', 'Who was with him?', 'How many people were there?', 'How long did it take?', 'Who printed it?']) {
  assert(isNarrowFactualFollowup(scope(question)),question);
  assert(!isNarrowFactualFollowup({...scope(question),classificationMode:'request-scope'}),'standalone question must not use followup exception');
}
for (const question of ['Why did it end?', 'Where does it teach about grace?', 'Who was he and why does he matter?', 'When did it end? Explain its significance.', 'How many lessons can we learn?', 'How long did it influence the Church?', 'Compare their teachings.', 'Where is the meaning found?', 'Who was he? Where did he live?', 'How did it happen?', 'What year was it; explain the context.']) assert(!isNarrowFactualFollowup(scope(question)),question);
assert(!isNarrowFactualFollowup({classificationMode:'conversation-context',retrievalQuestion:'When did it end?'}),'current question is required');
console.log('Narrow factual followup QA PASS');

// Run the real Worker pipeline with offline source/provider fixtures. The critic
// must retain independently worded factual repairs without restoring copied prose.
const {default:worker,hasExcessiveSourceOverlap}=await import('./src/index.js');
const originalFetch=globalThis.fetch;
const sourceText='By September 1846, the remaining Latter-day Saints and their sympathizers were forced out of Nauvoo. Most evacuees made their way to Council Bluffs in western Iowa, while many remained scattered in the surrounding area for months or years. The pioneer exodus began in February 1846.';
const cleanAnswer='September 1846 marks the final forced departure from Nauvoo in this account. The city evacuation had begun earlier that year, and displacement continued afterward for some of those affected.';
assert(hasExcessiveSourceOverlap(sourceText,[{content:sourceText}]));
assert(!hasExcessiveSourceOverlap(cleanAnswer,[{content:sourceText}]));
const json=value=>new Response(JSON.stringify(value),{headers:{'Content-Type':'application/json'}});
try {
 for(const mode of ['concise','repair','still-copied']){
  let compositions=0,audits=0;
  globalThis.fetch=async(url,options={})=>{
   if(String(url).endsWith('/chat/completions')){
    const prompt=JSON.parse(options.body).messages.map(message=>message.content).join('\n');
    assert(!/90 to 220 words|100 to 170 words|at least four complete sentences/.test(prompt),'narrow followup must not receive conflicting study-essay targets');
    let answer;
    if(prompt.includes('Act as a skeptical source editor')){
     audits++;
     if(mode==='concise'||audits>1)assert(prompt.includes('already passes the deterministic source-overlap check'));
     else assert(prompt.includes('found excessive source overlap'));
     answer=mode==='concise'||(audits>1&&mode==='repair')?cleanAnswer:sourceText;
    }else{
     compositions++;
     if(compositions>1)assert(prompt.includes('failed the final publication overlap check'));
     answer=mode==='concise'||compositions>1?cleanAnswer:sourceText;
    }
    return json({choices:[{message:{content:JSON.stringify({approved:true,answer,source_indexes:[1]})}}]});
   }
   assert(!String(url).endsWith('/responses'),'verified chronology sources must not require a research fallback');
   return new Response(`<p>${sourceText}</p>`,{headers:{'Content-Type':'text/html'}});
  };
  const response=await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'pioneers',focuschrist_profile:'faith-study',messages:[{role:'user',content:'When did the pioneer exodus begin?'},{role:'assistant',content:'Unverified claim: the departure happened in 9999.'},{role:'user',content:'When did it end?'}]})}),{OPENAI_API_KEY:'offline-fixture'});
  const payload=await response.json();
  assert.equal(compositions,mode==='concise'?1:2,JSON.stringify(payload));
  assert.equal(audits,mode==='concise'?1:2,JSON.stringify(payload));
  assert.equal(payload.focuschrist_openai_verifier_calls,mode==='concise'?2:4);
  assert.equal(payload.focuschrist_source_integrity_verified,mode!=='still-copied',JSON.stringify(payload));
  if(mode==='still-copied')assert.equal(payload.focuschrist_verifier_publication_failure,'excessive-source-overlap');
  else assert.equal(payload.choices[0].message.content,cleanAnswer);
 }
}finally{globalThis.fetch=originalFetch;}
console.log('Narrow factual Worker pipeline PASS: concise first answer, audited paraphrase repair, unchanged four-call limit, final overlap fails closed.');
