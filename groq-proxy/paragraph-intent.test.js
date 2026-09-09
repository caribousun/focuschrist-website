import assert from 'node:assert/strict';
import { paragraphRetrievalTerms } from './src/paragraph-intent.js';
const construction = paragraphRetrievalTerms('How long did construction of the temple take?');
for (const term of ['began','groundbreaking','dedicated','completed']) assert(construction.includes(term));
assert.deepEqual(paragraphRetrievalTerms('How long did the journey take?'),[],'travel duration must not imply building endpoints');
assert.deepEqual(paragraphRetrievalTerms('What does building faith mean?'),[],'construction vocabulary requires duration as well');
for (const term of ['dress','coat','shoes','garment']) assert(paragraphRetrievalTerms('What clothing did they use?').includes(term));
for (const term of ['young','boy','born','grew','family']) assert(paragraphRetrievalTerms('Describe her childhood.').includes(term));
assert.deepEqual(paragraphRetrievalTerms('Explain faith in Jesus Christ.'),[]);
assert.deepEqual(paragraphRetrievalTerms('When was he born?'),[],'a birth date alone does not ask for a childhood narrative');
assert(!paragraphRetrievalTerms('Describe clothing in childhood.').some(x=>/https|\d/.test(x)),'retrieval vocabulary contains no source IDs, dates or assertions');
assert.equal(new Set(paragraphRetrievalTerms('Describe clothing in childhood.')).size,paragraphRetrievalTerms('Describe clothing in childhood.').length);
console.log('Paragraph retrieval intent QA PASS');

assert(paragraphRetrievalTerms('In which month did severe weather trap the company?').includes('snowstorm'));
assert(paragraphRetrievalTerms('Which company arrived first?').includes('reached'));
