import {withVerifierFixture} from './openai-fixture.js';
const worker=withVerifierFixture(actualWorker);
import assert from 'node:assert/strict';
import actualWorker,{rankChurchSourceCandidates,namedGospelTopicSource,fetchOfficialSource,retrieveIndexedChurchEvidence,extractRelevantParagraphs,relevantParagraphText,compactParagraphPack,hasExcessiveSourceOverlap} from './src/index.js';
const originalFetch=globalThis.fetch;
const godheadQuestion='How are the Father, Son, and Holy Ghost described in Latter-day Saint teaching?';
assert.equal(rankChurchSourceCandidates(godheadQuestion,'ask')[0].title,'Godhead');
assert.equal(rankChurchSourceCandidates('Who is God?','ask')[0].title,'God The Father',
  'short foundational identity questions must prioritize God The Father over related topics');
assert.equal(rankChurchSourceCandidates('What is God?','ask')[0].title,'God The Father',
  'equivalent foundational identity wording must share the same focused route');
assert.equal(rankChurchSourceCandidates('How can teaching help someone learn?','ask').some(x=>x.sourceAliasMatch),false);
const janeQuestion='Find an official biography of Jane Manning James and explain her journey to Utah without inventing journal quotations.';
assert.equal(rankChurchSourceCandidates(janeQuestion,'pioneers')[0].title,'Jane Elizabeth Manning James');
assert.notEqual(rankChurchSourceCandidates('Tell me about Utah and James','pioneers')[0]?.title,'Jane Elizabeth Manning James');
const question='How can I study humility without confusing it with having no worth?';
const humility='Humility acknowledges a need to learn and a dependence on God. It does not require someone to believe they are worthless or unable to act courageously. An honest recognition of limitations can coexist with a willingness to serve and learn.';
const contextParagraphs=[
  'Earlier events happened in a different city and involved another association. This paragraph establishes the earlier setting without locating a later organization.',
  'In a later year, women in a different region formed a council for community service. The council helped the poor through designated neighborhood representatives.',
  'The following discussion describes changes in medical education. It does not identify the unnamed city of the preceding organization.'
];
const contextCandidate={namedGospelTopic:true,kind:'history-topic',title:'Community health',tokens:'community health council'};
const contextText=relevantParagraphText(contextParagraphs,'How did the council help the poor?',contextCandidate);
assert.ok(contextText.includes(contextParagraphs[0]+'\n\n'+contextParagraphs[1]+'\n\n'+contextParagraphs[2]),'neighboring setting paragraphs and their boundaries must survive selection');
assert.deepEqual(compactParagraphPack(contextParagraphs,contextCandidate,'How did the council help the poor?'),contextParagraphs,'cache packing must retain the same contextual paragraph boundaries');
assert.ok(contextText.length<=4200);
const copied='Hyrum Smith was the older brother of Joseph Smith and a trusted leader in the early Church Hyrum Smith served as Church patriarch and remained with Joseph Smith during severe persecution';
const fragments=copied.split(' ').reduce((parts,word,index)=>{if(index%4===0)parts.push([]);parts.at(-1).push(word);return parts;},[]).map(part=>part.join(' ')).join(' Indeed, ');
assert.equal(hasExcessiveSourceOverlap((fragments+'. ').repeat(3),[{content:copied}]),true,'repeated ordered reconstruction cannot dilute the copying ratio');
assert.equal(hasExcessiveSourceOverlap(('Hyrum Smith appears in this independently composed discussion of questions whose wording has little relation to the original account. ').repeat(3),[{content:copied}]),false,'ordinary repeated names cannot restart a substantial ordered source pass');
try {
  const identityFetches=[];
  globalThis.fetch=async(request)=>{
    const url=String(request?.url || request);
    identityFetches.push(url);
    return new Response('<h1>Official identity</h1><p>Who is God? God is our loving Heavenly Father. The Godhead teaches us about God and His work. Official teachings explain His character, purpose, identity, and relationship with His children in clear language for study and worship.</p>',{headers:{'Content-Type':'text/html'}});
  };
  const identityEvidence=await retrieveIndexedChurchEvidence('Who is God?','ask',Date.now()+10000);
  assert.deepEqual(identityFetches,[
    'https://www.churchofjesuschrist.org/study/manual/gospel-topics/god-the-father?lang=eng',
    'https://www.churchofjesuschrist.org/study/manual/gospel-topics/godhead?lang=eng',
  ],'foundational identity questions must fetch the focused Father source and its Godhead companion');
  assert.equal(identityEvidence.evidence.length,2,'foundational identity questions must retain both approved sources when available');
  for(const page of ['ask','pioneers','church-history']) {
    const candidate=namedGospelTopicSource(question,page,rankChurchSourceCandidates(question,page));
    assert.ok(candidate?.url.includes('/humility?'),'unambiguous explicit Gospel Topic must be eligible on each study surface');
    globalThis.fetch=async()=>new Response(`<head><title>Humility worth</title><link onload="fonts.forEach(f=>f.family.startsWith('Ensign'))"></head><p>${humility}</p>`,{headers:{'Content-Type':'text/html'}});
    const admitted=await fetchOfficialSource(candidate,question,Date.now()+10000);
    assert.ok(admitted?.content.includes('Humility acknowledges'));
    assert.ok(!admitted.content.includes('fonts.forEach'));
    globalThis.fetch=async()=>new Response('<head><title>Humility worth</title></head><p>Humility</p><p>The history of railway timetables concerns the movement of passenger trains between different stations. This paragraph contains unrelated transport information and does not describe the requested personal quality or a religious teaching.</p>',{headers:{'Content-Type':'text/html'}});
    assert.equal(await fetchOfficialSource(candidate,question,Date.now()+10000),null,'title boilerplate alone must not admit unrelated body content');
  }
  assert.equal(namedGospelTopicSource('Compare humility and forgiveness','ask',rankChurchSourceCandidates('Compare humility and forgiveness','ask')),null,'ambiguous/comparative topics must not acquire single-topic admission');
  for(const q of ['What caused the Cold War?','How does a train engine work?']) {
    const candidates=rankChurchSourceCandidates(q,'pioneers');
    assert.ok(!candidates.some(source=>source.pioneerDisclosure || /departure-from-nauvoo|chapter-twenty-six/.test(source.url)),'generic cold/train tokens cannot select pioneer landmarks');
  }
  const irrigation=rankChurchSourceCandidates('How did cooperative irrigation help pioneer settlements?','pioneers')[0];
  assert.ok(irrigation.topicPinned && !irrigation.pioneerDisclosure,'irrigation must not be scoped to the earlier Journey section');
  for(const [q,needle,route] of [
    ['Why did the Saints leave Nauvoo in the winter of 1846?','Nauvoo','departure-from-nauvoo'],
    ['Why was Fort Laramie important on the pioneer route?','Fort Laramie','chapter-twenty-six'],
    ['Why did the pioneers cross South Pass?','South Pass','chapter-twenty-six']
  ]) {
    const candidate=rankChurchSourceCandidates(q,'pioneers')[0];
    assert.ok(candidate.url.includes(route) && candidate.overlapCount>=2);
    if(needle!=='Nauvoo') assert.deepEqual(candidate.focalPhrases,[needle.toLowerCase()]);
    let verifierCalls=0;
    globalThis.fetch=async()=>new Response(needle==='Nauvoo'
      ? '<p>In 1846 the Saints prepared to leave Nauvoo during winter. The official source describes the departure and preparations for the journey across Iowa.</p>'
      : `<p>${needle} EARLIER1846 must not appear in the selected evidence for the later company.</p><h2>Journey of the Pioneer Company</h2><p>${needle} was a landmark on the pioneer route in 1847. The company traveled through this area while making its journey toward the Salt Lake Valley.</p><h2>Establishing a Settlement in the Valley</h2>`,{headers:{'Content-Type':'text/html'}});
    const response=await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:'pioneers',focuschrist_profile:'pioneer-study',messages:[{role:'user',content:q}]})}),{verifierFixture:async(_model,body)=>{
      verifierCalls++; const prompt=body.messages[0].content;
      assert.ok(prompt.includes(`QUESTION:\n${q}`) && prompt.includes(needle));
      assert.ok(prompt.includes('Answer coverage is required') && prompt.includes('different time period') && prompt.includes('set approved false so additional sources can be researched'));
      assert.ok(prompt.includes('Do not increase geographic specificity') && prompt.includes('shift of time or setting'));
      assert.ok(!prompt.includes('EARLIER1846'));
      return {response:{approved:false,answer:'No answer is authorized by this transport fixture.',source_indexes:[]}};
    }});
    const payload=await response.json();
    assert.ok(verifierCalls>=1 && verifierCalls<=2,'reviewed discovery must reach the verifier, not become an answer by itself');
    assert.equal(payload.focuschrist_source_integrity_verified,false);
  }
} finally {globalThis.fetch=originalFetch;}
console.log('PASS: clean article extraction, exact Gospel Topic admission, reviewed Pioneer metadata, scoped landmarks, irrigation preservation and cold/train negatives.');
