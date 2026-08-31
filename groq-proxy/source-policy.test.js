import { guardGeneratedAnswer, sanitizePayload } from './src/index.js';

function assert(condition, message) { if (!condition) throw new Error(message); }
assert(guardGeneratedAnswer('D&C 76:31-34 teaches colored degrees.') !== 'D&C 76:31-34 teaches colored degrees.',
  'gateway must block scripture citations');
assert(guardGeneratedAnswer('Latter-day Saint scripture assigns red to celestial glory.') !== 'Latter-day Saint scripture assigns red to celestial glory.',
  'gateway must block uncited scripture claims');
assert(guardGeneratedAnswer('Genesis teaches that creation happened this way.') !== 'Genesis teaches that creation happened this way.',
  'gateway must block uncited canonical-book claims');
assert(guardGeneratedAnswer('Brigham Young entered the valley on July 24, 1847.') !== 'Brigham Young entered the valley on July 24, 1847.',
  'gateway must block unreviewed historical dates');
assert(guardGeneratedAnswer('Joseph Smith said, "I saw two Personages."') !== 'Joseph Smith said, "I saw two Personages."',
  'gateway must block unreviewed quotations and attributions');
assert(guardGeneratedAnswer('The Church officially teaches this principle.') !== 'The Church officially teaches this principle.',
  'gateway must block unreviewed official-teaching claims');
assert(guardGeneratedAnswer('Here is a harmless-looking generated answer.') !== 'Here is a harmless-looking generated answer.',
  'gateway must fail closed for every unreviewed generated answer');
const clean = sanitizePayload({ model: 'other', temperature: 0.9, max_tokens: 9000, messages: [{ role: 'user', content: 'hello' }] });
assert(clean.model === 'openai/gpt-oss-20b', 'gateway must own the model');
assert(clean.temperature === 0.25 && clean.max_tokens === 1500, 'gateway must clamp generation settings');
assert(clean.messages[0].content.includes('SERVER SOURCE-INTEGRITY POLICY'), 'gateway must prepend server policy');
console.log('Gateway source policy QA PASS');
