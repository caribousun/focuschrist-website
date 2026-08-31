import {
  SOURCE_INTEGRITY_FALLBACK,
  classifyResearchScope,
  collectSourceEvidence,
  guardVerifiedAnswer,
  hasKnownFalseClaim,
  isOfficialChurchSource,
  parseVerifierJson,
  sanitizePayload,
} from './src/index.js';

function assert(condition, message) { if (!condition) throw new Error(message); }

const faithMessages = [{ role: 'user', content: 'What does Isaiah 1:18 teach?' }];
const faith = classifyResearchScope(faithMessages);
assert(faith.faith, 'scripture citations must use the faith research scope');

const clean = sanitizePayload({ model: 'other', temperature: 0.9, max_tokens: 9000, messages: faithMessages });
assert(clean.research.model === 'groq/compound-mini', 'gateway must own the research model');
assert(clean.research.messages[0].content.includes('SERVER RESEARCH AND SOURCE-INTEGRITY POLICY'),
  'gateway must prepend the server research policy');
assert(clean.research.messages[0].content.includes('search only site:churchofjesuschrist.org'),
  'faith research must be instructed to search the official Church domain');

const general = sanitizePayload({ messages: [{ role: 'user', content: 'Why is the daytime sky blue?' }] });
assert(!general.scope.faith && !general.research.messages[0].content.includes('search only site:churchofjesuschrist.org'),
  'ordinary questions must not be forced into the Church-only domain');

const evidence = collectSourceEvidence({
  executed_tools: [{
    type: 'web_search',
    search_results: [
      { title: 'Isaiah 1', url: 'https://www.churchofjesuschrist.org/study/scriptures/ot/isa/1', content: 'Though your sins be as scarlet...' },
      { title: 'Unrelated', url: 'https://example.com/page', snippet: 'Example result' },
    ],
  }],
});
assert(evidence.length === 2, 'gateway must collect tool-returned source evidence');
assert(isOfficialChurchSource(evidence[0]), 'official Church subpages must be recognized');
assert(!isOfficialChurchSource(evidence[1]), 'non-Church evidence must not be treated as official');

const verifiedAnswer = 'Isaiah 1:18 uses scarlet and snow in an invitation to repent.';
assert(guardVerifiedAnswer(verifiedAnswer, [evidence[0]], faith, true) === verifiedAnswer,
  'a verified faith answer with official evidence must pass');
assert(guardVerifiedAnswer(verifiedAnswer, [evidence[1]], faith, true) === SOURCE_INTEGRITY_FALLBACK,
  'faith answers backed only by nonofficial evidence must fail closed');
assert(guardVerifiedAnswer(verifiedAnswer, [evidence[0]], faith, false) === SOURCE_INTEGRITY_FALLBACK,
  'a rejected verifier result must fail closed');
assert(guardVerifiedAnswer('D&C 76 says red, white, and black lights represent the three kingdoms.', [evidence[0]], faith, true) === SOURCE_INTEGRITY_FALLBACK,
  'the known false color claim must remain blocked even with a verification receipt');
assert(!hasKnownFalseClaim('Doctrine and Covenants 76 does not teach that red, white, and black lights represent three kingdoms.'),
  'a truthful refutation of the false color claim must remain answerable');

const verdict = parseVerifierJson('```json\n{"approved":true,"answer":"Supported","source_indexes":[1]}\n```');
assert(verdict && verdict.approved === true && verdict.source_indexes[0] === 1,
  'gateway must parse a verifier JSON object');

console.log('Gateway source policy QA PASS');
