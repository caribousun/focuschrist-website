import assert from 'node:assert/strict';
import fs from 'node:fs';
import createLibrary from '../scripture-library.js';
import { directScriptureReading } from './src/direct-scripture-reading.js';
const catalog = JSON.parse(fs.readFileSync(new URL('../scripture-data/catalog.json',import.meta.url)));
const library = createLibrary(catalog, async url => new Response(fs.readFileSync(new URL('..'+url,import.meta.url))));
for (const question of ['What does Articles of Faith 1:1 state?', 'What does John 3:16 say exactly?', 'Please quote Genesis 1:1 exactly.', 'Read Psalm 23:1-3 for me.', 'Show me Mosiah 18:8-10.']) {
  const result = await directScriptureReading(question,library);
  assert(result?.sourceIntegrityPassed, question);
  assert((await library.checkAnswer(result.answer,result.sources)).ok,question);
}
const article = await directScriptureReading('What does Articles of Faith 1:1 state?',library);
assert(article.answer.includes('We believe in God, the Eternal Father, and in His Son, Jesus Christ, and in the Holy Ghost.'));
for (const question of ['What does John 3:16 teach?', 'What does John 3:16 say about baptism?', 'Explain John 3:16.', 'Read John 3:16 and explain it.', 'How can I apply Mosiah 18:8-10?', 'What does Alma 150:1 state?', 'Read John 3:999.', 'What does Articles of Faith state?', 'Read John 3:16 and Genesis 1:1.']) assert.equal(await directScriptureReading(question,library),null,question);
console.log('Direct scripture reading QA PASS');
