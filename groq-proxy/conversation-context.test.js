import assert from 'node:assert/strict';
import worker, { classifyResearchScope, sanitizePayload, relatedConversationSources } from './src/index.js';

const legacy = (question, antecedent) => `${question}\n\nThe immediately preceding user question was: "${antecedent}".\n\nResolve pronouns and omitted subjects only from that immediately preceding question.`;
const examples = [
  ['is god in the bible old testament', 'is he the same god that is in the new testament'],
  ['what year did the pioneer exodus begin', 'when did it end'],
];
const assistantClaim = 'ASSISTANT_ONLY_UNVERIFIED: John 99:1 proves that the event ended in 9999.';
for (const page of ['ask', 'pioneers']) {
  for (const [antecedent, current] of examples) {
    for (const question of [current, legacy(current, antecedent)]) {
      const messages = [{role:'user',content:antecedent}, {role:'assistant',content:assistantClaim}, {role:'user',content:question}];
      const scope = classifyResearchScope(messages, page, 'faith-study');
      assert.equal(scope.question, current, 'current request must not include legacy context instructions');
      assert.deepEqual(scope.conversationContext, [antecedent], 'context comes from prior user questions, not assistant assertions');
      assert.equal(scope.classificationMode, 'conversation-context');
      assert.ok(scope.retrievalQuestion.includes(current) && scope.retrievalQuestion.includes(antecedent));
      assert.ok(!scope.retrievalQuestion.includes('ASSISTANT_ONLY_UNVERIFIED'));
      assert.ok(!scope.conversationContext.join(' ').includes('John 99:1'));
      const sanitized = sanitizePayload({messages,focuschrist_page:page,focuschrist_profile:'faith-study'});
      assert.equal(sanitized.scope.question, current, 'payload sanitation must retain the new requested attribute');
      assert.deepEqual(sanitized.scope.conversationContext, [antecedent]);
      if (current === 'when did it end') assert.equal(sanitized.scope.question.includes('begin'), false, 'end-date request must never turn back into the beginning-date question');
    }
  }
  const resetMessages = [
    {role:'user',content:examples[0][0]}, {role:'assistant',content:assistantClaim},
    {role:'user',content:'What causes ocean tides?'}, {role:'assistant',content:'A previous explanation.'},
    {role:'user',content:'Why does it happen?'}
  ];
  assert.deepEqual(classifyResearchScope(resetMessages,page,'general-knowledge').conversationContext, ['What causes ocean tides?'],
    'a standalone topic reset must exclude the older God subject');
  const explicit = classifyResearchScope(resetMessages.slice(0,3),page,'general-knowledge');
  assert.deepEqual(explicit.conversationContext, [], 'a new standalone question must not inherit unrelated context');
  assert.equal(explicit.question, 'What causes ocean tides?');
  const possessiveReset = classifyResearchScope([
    {role:'user',content:'Who is Hyrum Smith?'},
    {role:'assistant',content:assistantClaim},
    {role:'user',content:'What did Abraham Lincoln say about his childhood?'}
  ],page,'general-knowledge');
  assert.deepEqual(possessiveReset.conversationContext, [], 'a named new subject with its own possessive must not inherit the older Church person');
  assert.equal(possessiveReset.retrievalQuestion, 'What did Abraham Lincoln say about his childhood?');
  if (page === 'ask') assert.equal(possessiveReset.faith, false, 'a new general subject must not be routed into old Church history evidence');
  const personalAddress = classifyResearchScope([
    {role:'user',content:'Who is Hyrum Smith?'},
    {role:'user',content:'What can you tell me about his childhood?'}
  ],page,'general-knowledge');
  assert.deepEqual(personalAddress.conversationContext, ['Who is Hyrum Smith?'], 'addressing the assistant must not be mistaken for naming a new subject');
  assert.equal(personalAddress.question, 'What can you tell me about his childhood?');
  const missing = classifyResearchScope([{role:'assistant',content:assistantClaim},{role:'user',content:'when did it end'}],page,'faith-study');
  assert.deepEqual(missing.conversationContext, [], 'an assistant message alone cannot supply a user antecedent');
  const chain = [examples[0][0], examples[0][1], 'What does that mean for worship?', 'can you site a scripture'];
  const chainMessages = chain.flatMap((content,index) => index === chain.length-1 ? [{role:'user',content}] : [{role:'user',content},{role:'assistant',content:assistantClaim}]);
  const chained = classifyResearchScope(chainMessages,page,'faith-study');
  assert.deepEqual(chained.conversationContext, chain.slice(0,3), 'three-turn relationship context must preserve chronological user intent');
  assert.equal(chained.question, chain[3]);
  assert.equal(chained.scriptureSupportRequested, true, 'cite/site support handling remains available');
  assert.equal(chained.scriptureSupportAntecedent, chain[2]);
  const boundedMessages = [examples[0][0], 'Is he described there?', 'How does that relate?', 'What does it mean?', 'Can you explain that?'].map(content => ({role:'user',content}));
  assert.deepEqual(classifyResearchScope(boundedMessages,page,'faith-study').conversationContext, boundedMessages.slice(1,4).map(message=>message.content),
    'context must remain bounded to the three preceding user turns');
  const multiline = 'What does Genesis 1:1 say?\nPlease distinguish quotation from explanation.';
  assert.equal(classifyResearchScope([{role:'user',content:multiline}],page,'faith-study').question,multiline,
    'ordinary multiline user wording must not be truncated as if it were a legacy wrapper');
}

const pairPaths = [
  ['gospel-topics/jesus-christ', 'gospel-topics/godhead'],
  ['history/topics/departure-from-nauvoo', 'history/topics/pioneer-trek']
];
for (const [index,[antecedent,current]] of examples.entries()) {
  const scope = classifyResearchScope([{role:'user',content:antecedent},{role:'user',content:current}],'ask','faith-study');
  const candidates = relatedConversationSources(scope);
  assert.equal(candidates.length, 2, 'each relationship requires two complementary sources');
  for (const path of pairPaths[index]) assert.ok(candidates.some(candidate=>candidate.url.includes(path)));
}
assert.deepEqual(relatedConversationSources(classifyResearchScope([
  {role:'user',content:'When was the biblical Exodus of Moses from Egypt?'},
  {role:'user',content:'When did it end?'}
],'pioneers','faith-study')), [], 'Biblical Exodus must not select Latter-day Saint migration sources');
assert.deepEqual(relatedConversationSources(classifyResearchScope([
  {role:'user',content:examples[0][0]}, {role:'user',content:'What causes ocean tides?'}
],'ask','general-knowledge')), [], 'an unrelated new subject must not inherit a prior evidence pair');
assert.deepEqual(relatedConversationSources(classifyResearchScope([
  {role:'user',content:examples[0][0]}, {role:'user',content:'What does John 3:16 teach about God in the New Testament?'}
],'ask','faith-study')), [], 'an explicit scripture request must retain canonical passage precedence');
for (const messages of [
  [{role:'user',content:"What does the New Testament teach about God's grace?"}],
  [{role:'user',content:examples[0][0]}, {role:'user',content:'What does his grace mean for us?'}],
  [{role:'user',content:examples[1][0]}, {role:'user',content:'What challenges did they face during the pioneer migration?'}]
]) assert.deepEqual(relatedConversationSources(classifyResearchScope(messages,'ask','faith-study')), [],
  'specific grace or pioneer experience questions must keep their own retrieval instead of an identity or chronology pack');

// Prove paired official retrieval precedes model research, then falls back to
// research when those sources are unavailable. Every fetch is an offline mock.
const originalFetch = globalThis.fetch;
try {
  for (const page of ['ask','pioneers']) for (const [antecedent,current] of examples) {
    const calls = [];
    globalThis.fetch = async (url, options) => {
      calls.push({url:String(url),body:options?.body ? JSON.parse(options.body) : null});
      return new Response(JSON.stringify({error:{message:'Offline route fixture unavailable'}}),{status:400,headers:{'Content-Type':'application/json'}});
    };
    await worker.fetch(new Request('https://worker.test',{method:'POST',headers:{Origin:'https://focuschrist.com','Content-Type':'application/json'},body:JSON.stringify({focuschrist_page:page,focuschrist_profile:'faith-study',messages:[{role:'user',content:antecedent},{role:'assistant',content:assistantClaim},{role:'user',content:current}]})}),{OPENAI_API_KEY:'offline-fixture'});
    const expectedPaths = pairPaths[examples.findIndex(example=>example[0]===antecedent)];
    for (const path of expectedPaths) assert.ok(calls.some(call=>call.url.includes(path)), 'both complementary official sources must be attempted');
    assert.ok(calls[0].url.includes('churchofjesuschrist.org'), 'paired official evidence must be attempted before model research');
    const researchCall = calls.find(call=>call.url.endsWith('/v1/responses'));
    assert.ok(researchCall, 'unavailable paired sources must still allow ordinary research');
    assert.ok(researchCall.body.input.some(message=>message.content.includes(current)), 'research must receive the current comparison or end-date request');
  }
} finally { globalThis.fetch = originalFetch; }
console.log('Conversation context QA PASS: both surfaces, raw/legacy requests, current intent, user-only bounded context, reset/missing/three-turn cases, paired official retrieval and research fallback.');
