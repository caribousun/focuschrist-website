import assert from 'node:assert/strict';
import fs from 'node:fs';
import worker, { isAllowedResearchFetchUrl } from './src/index.js';
import { checkCorpusCoverage, requestedTeachingCorpora } from './src/corpus-coverage.js';
import createScriptureLibrary from '../scripture-library.js';
import catalog from '../scripture-data/catalog.json' with { type: 'json' };
const library = createScriptureLibrary(catalog, async () => { throw new Error('unit coverage parser must not fetch'); });
const scope = question => ({ question });
const official = 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/grace?lang=eng';
const evidence = content => [{ url: official, content }];
const check = (question, answer, sources) => checkCorpusCoverage(scope(question), answer, sources, library, isAllowedResearchFetchUrl);
assert.equal(checkCorpusCoverage(scope('What does the New Testament teach about grace?'), 'Ephesians 2:8 teaches grace.', [{url:'https://www.churchofjesuschrist.org/study/scriptures/nt/eph/2?lang=eng'}], library, isAllowedResearchFetchUrl).ok, false);
const question = "What does the New Testament teach about God's grace?";
assert.equal(check(question, 'Grace comes through Jesus Christ.', evidence('Grace is a divine gift.')).ok, false);
assert.equal(check(question, 'Alma 32:21 teaches faith.', evidence('Alma 32:21 teaches faith.')).ok, false);
assert.equal(check(question, 'Ephesians 200:8 teaches grace.', evidence('Ephesians 2:8')).ok, false);
assert.equal(check(question, 'Ephesians 2:99 teaches grace.', evidence('Ephesians 2:8')).ok, false);
assert.equal(check(question, 'Ephesians 2:8 teaches grace.', evidence('A generic account of grace.')).ok, false);
assert.equal(check(question, 'Ephesians 2:8 teaches grace.', [{ url: official, title: 'Ephesians 2:8', content: '' }]).ok, false);
assert.equal(check(question, 'Ephesians 2:8 teaches grace.', evidence('Ephesians 2:8 teaches grace.')).ok, true);
assert.equal(check(question, 'Ephesians 2:8-9 teaches grace.', evidence('Ephesians 2:8')).ok, false);
assert.equal(check(question, 'Ephesians 2:8 teaches grace.', [{url:'https://www.churchofjesuschrist.org.evil.test/study/scriptures/nt/eph/2',content:'Ephesians 2:8'}]).ok,false);
assert.equal(check(question, 'Ephesians 2:8 teaches grace.', [{url:'https://www.churchofjesuschrist.org/study/scriptures/nt/eph/2?lang=eng',content:'Complete hydrated scripture.'}]).ok,true);
for (const [corpus, reference] of [['Old Testament','Genesis 1:1'], ['New Testament','John 1:17'], ['Book of Mormon','Alma 32:21'], ['Doctrine and Covenants','Doctrine and Covenants 6:36'], ['Pearl of Great Price','Moses 1:39'], ['Bible','John 1:17']]) {
  assert.equal(check(`What does the ${corpus} teach about God?`, `${reference} gives a teaching.`, evidence(`${reference} is discussed here.`)).ok,true,corpus);
}
assert.equal(check('Compare Old Testament and New Testament teachings about mercy.', 'John 3:16 teaches mercy.', evidence('John 3:16')).ok,false);
assert.equal(check('Compare Old Testament and New Testament teachings about mercy.', 'John 3:16 and Psalm 23 teach mercy.', evidence('John 3:16 and Psalm 23')).ok,true);
assert.deepEqual(requestedTeachingCorpora(scope('Is the God of the Old Testament the same as the New Testament?')), []);
assert.deepEqual(requestedTeachingCorpora(scope('What is grace?')), []);
assert.deepEqual(requestedTeachingCorpora(scope('What does @C999@ teach about grace?')), []);
assert.deepEqual(requestedTeachingCorpora(scope('What does @C0@ teach about grace?')), []);
assert.deepEqual(requestedTeachingCorpora(scope('What does the New Testament teach about @C999@?')), [['nt']]);

assert.deepEqual(requestedTeachingCorpora(scope('What did Joseph Smith teach about translating the Bible?')), []);
assert.deepEqual(requestedTeachingCorpora(scope('What do Church leaders say about the Book of Mormon?')), []);
assert.deepEqual(requestedTeachingCorpora(scope('What does the Bible teach about the Book of Mormon?')), [['ot', 'nt']]);
assert.deepEqual(requestedTeachingCorpora(scope('What does the New Testament say about the Old Testament?')), [['nt']]);
assert.deepEqual(requestedTeachingCorpora(scope('What does the Bible teach about translating the Pearl of Great Price?')), [['ot', 'nt']]);
assert.deepEqual(requestedTeachingCorpora(scope('Compare teachings about mercy in the Old Testament and New Testament.')), [['ot'], ['nt']]);
assert.deepEqual(requestedTeachingCorpora(scope('Explain teachings from the Book of Mormon about faith.')), [['bofm']]);
assert.deepEqual(requestedTeachingCorpora(scope('Does the New Testament teach that God does not exist?')), [['nt']]);

assert.deepEqual(requestedTeachingCorpora({question:'What year did the pioneer exodus begin?',conversationContext:[question]}), []);
assert.deepEqual(requestedTeachingCorpora({question:'Can you cite a scripture for that?',scriptureSupportRequested:true,scriptureSupportAntecedent:question}), [['nt']]);
assert.equal(check('According to the Book of Mormon, what is faith?', 'A doctrinal summary.', evidence('Alma 32:21')).ok,false);

// Worker integration: nominal verifier approval without requested corpus support
// must search once, and the same deficient repair must never be published.
const originalFetch = globalThis.fetch;
let verifierCalls = 0, searches = 0, searchUnavailable = false, supportedRepair = false;
try {
  globalThis.fetch = async (url, init) => {
    const target = String(url);
    if (target === 'https://api.openai.com/v1/chat/completions') {
      verifierCalls++;
      const body = JSON.parse(init.body);
      assert(body.messages[0].content.includes('named scriptural corpus'));
      return new Response(JSON.stringify({choices:[{message:{content:JSON.stringify({approved:true,answer:(supportedRepair && verifierCalls === 2 ? 'Ephesians 2:8 teaches that salvation is by grace through faith. ' : '') + 'Grace is the divine help that comes through Jesus Christ. God offers strength and forgiveness to those who turn toward Him. This gift helps people change and grow as they seek to follow His teachings. We depend on divine help rather than relying only on our own ability. The official study sources invite readers to deepen their trust in God and seek the assistance He provides throughout their lives. This doctrinal explanation describes a central teaching about grace and the power of Jesus Christ.',source_indexes:[1]})}}]}));
    }
    if (target === 'https://api.openai.com/v1/responses') {
      searches++;
      if (searchUnavailable) return new Response('{}', { status: 503 });
      return new Response(JSON.stringify({status:'completed',output:[{type:'web_search_call',status:'completed',action:{sources:[]}}]}));
    }
    if (target.startsWith('https://focuschrist.com/scripture-data/')) return new Response(fs.readFileSync(new URL('../' + new URL(target).pathname.slice(1), import.meta.url)));
    assert(isAllowedResearchFetchUrl(target));
    return new Response('<html><body><p>Grace is the help and strength received through the Atonement of Jesus Christ. God helps people change their lives and seek forgiveness through repentance. Grace provides divine assistance as people learn to follow Jesus Christ. Ephesians 2:8 describes salvation by grace through faith.</p></body></html>',{headers:{'Content-Type':'text/html'}});
  };
  const response = await worker.fetch(new Request('https://focuschrist-groq-proxy.caribousun.workers.dev',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',messages:[{role:'user',content:question}]})}),{OPENAI_API_KEY:'test-key'});
  const result = await response.json();
  assert.equal(searches,1,JSON.stringify(result));
  assert.equal(verifierCalls,2,JSON.stringify(result));
  assert.equal(result.focuschrist_source_integrity_verified,false);
  assert.equal(result.focuschrist_corpus_coverage_failure,'missing-requested-corpus-evidence');
  assert.equal(result.focuschrist_gateway_mode,'verification-rejected');
  searchUnavailable = true; verifierCalls = 0; searches = 0;
  const outageResponse = await worker.fetch(new Request('https://focuschrist-groq-proxy.caribousun.workers.dev',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',messages:[{role:'user',content:question}]})}),{OPENAI_API_KEY:'test-key'});
  const outage = await outageResponse.json();
  assert.equal(searches,1); assert.equal(verifierCalls,1);
  assert.equal(outage.focuschrist_source_integrity_verified,false);
  assert.equal(outage.focuschrist_gateway_mode,'research-unavailable');
  assert.match(outage.choices[0].message.content,/unable to check/);
  searchUnavailable = false; supportedRepair = true; verifierCalls = 0; searches = 0;
  const repairedResponse = await worker.fetch(new Request('https://focuschrist-groq-proxy.caribousun.workers.dev',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'ask',messages:[{role:'user',content:question}]})}),{OPENAI_API_KEY:'test-key'});
  const repaired = await repairedResponse.json();
  assert.equal(searches,1); assert.equal(verifierCalls,2);
  assert.equal(repaired.focuschrist_source_integrity_verified,true,JSON.stringify(repaired));
  assert.equal(repaired.focuschrist_scripture_validated,true);
  assert.equal('focuschrist_corpus_coverage_failure' in repaired,false);


} finally { globalThis.fetch = originalFetch; }
console.log('Requested corpus coverage QA PASS');
