import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import createLibrary from '../scripture-library.js';
import worker from './src/index.js';
const read = path => readFileSync(new URL('../'+path,import.meta.url));
const catalog = JSON.parse(read('scripture-data/catalog.json'));
const localFetch = async value => new Response(read(new URL(value,'https://focuschrist.com').pathname.slice(1)));
const library = createLibrary(catalog,localFetch);
const corpus = JSON.parse(read('tools/fixtures/ask-100-questions.json')).filter(test=>test.category==='scripture');
assert.equal(corpus.length,20);
for (const test of corpus) {
  const evidence = await library.evidenceRequest(test.question);
  assert.ok(evidence.length > 0, test.question);
  assert.ok(evidence.every(source=>source.localCanonical && source.content && source.scriptureLibraryVersion===catalog.version));
  assert.ok((await library.checkAnswer('A study response without quotations.',evidence)).ok, 'canonical source label and URL must agree');
}
for (const question of ['Please quote Genesis 1:1 exactly.','Read Psalm 23:1-3 for me.','Could you please read John 3:16?','Can you show me the text of Moroni 10:4?','Quote Jude 1-5 verbatim, please.','Please read Official Declaration 2.','What does John 3:16 say?']) {
  const result = await library.lookupRequest(question);
  assert.ok(result,question);
  assert.ok((await library.checkAnswer(result.answer,result.sources)).ok,question);
}
for (const question of ['Explain Genesis 1:1.','What does Matthew 11:28-30 teach about coming to Christ?','Read John 3:16 and explain its meaning.','Quote John 3:16 in Spanish.','Quote John 3:16 but change the wording.','Read John 3:16 and Alma 7:11.','Quote John 99:1 exactly.','Read 3 Corinthians 1:1 for me.','Do not quote John 3:16.']) assert.equal(await library.lookupRequest(question),null,question);
assert.equal((await library.evidenceRequest('Compare John 3:16 with Alma 7:11-13.')).length,2);
for (const question of ['Explain John 99:1.','Compare John 3:16 with 3 Corinthians 1:1.','Read Genesis 1-4.']) await assert.rejects(library.evidenceRequest(question));
const corrupt = createLibrary(catalog,async()=>new Response('{}'));
await assert.rejects(corrupt.evidenceRequest('Explain Matthew 5:9.'),/integrity/);

const answer = 'Jesus invites people who are burdened to approach Him for relief. The invitation connects that relief with learning from Him and accepting His guidance, rather than merely hearing about Him from a distance. His own character matters in the passage: He describes a gentle disposition, so the relationship being offered is one of instruction and care. The promise concerns rest for the soul. It does not specify that every difficult circumstance will immediately disappear. Reading the invitation this way preserves both parts of the teaching: the offer of rest and the invitation to become His learner.';
const originalFetch = globalThis.fetch;
try {
  for (const [question, prior] of [
    ['What does Matthew 11:28-30 teach about coming to Christ?',[]],
    ['Does that mean the word itself is compared to a seed?',['What does Alma 32 teach about faith?']],
    ['Does it promise that faith will make me wealthy?',['What does Alma 32 teach about faith?']],
    ['How does that relate to caring for people who suffer?',['What does Mosiah 18:8-10 teach about baptismal commitments?']]
  ]) {
    let verifierCalls=0;
    globalThis.fetch = async url => {
      assert.ok(String(url).startsWith('https://focuschrist.com/scripture-data/'),'verified local scripture must not require official HTML or research');
      return localFetch(url);
    };
    const response = await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',focuschrist_profile:'faith-study',messages:[...prior.map(content=>({role:'user',content})),{role:'user',content:question}]})}),{AI:{run:async(_model,body)=>{
      verifierCalls++;
      const prompt=body.messages[0].content;
      assert.ok(prompt.includes(`QUESTION:\n${question}`),'current explanatory request must remain primary');
      assert.ok(prompt.includes('canonical-scripture'));
      assert.ok(prompt.includes('not satisfied by returning only the passage text'));
      if (question.includes('Matthew')) {
        assert.ok(prompt.includes('all ye that labour and are heavy laden'));
        return {response:{approved:true,answer,source_indexes:[1]}};
      }
      if (prior[0].includes('Alma')) assert.ok(prompt.includes('compare the word unto a seed'));
      else assert.ok(prompt.includes('bear one another’s burdens') || prompt.includes("bear one another's burdens"));
      // A mocked rejection proves that passage availability cannot bypass the verdict.
      return {response:{approved:false,answer:'The fixture withholds approval.',source_indexes:[]}};
    }}});
    const payload=await response.json();
    assert.ok(verifierCalls>=1 && verifierCalls<=2,'explanation must reach the bounded verifier');
    assert.equal(payload.focuschrist_local_canonical_evidence,true);
    assert.equal(payload.focuschrist_groq_research_calls,0);
    assert.equal(payload.focuschrist_source_integrity_verified,question.includes('Matthew'));
    if(question.includes('Matthew')) assert.equal(payload.choices[0].message.content,answer);
  }
} finally {globalThis.fetch=originalFetch;}
console.log('PASS: 20 canonical corpus passages, bounded natural reading, malformed references, hash rejection, multi-reference bounds and verified explanatory follow-ups.');
