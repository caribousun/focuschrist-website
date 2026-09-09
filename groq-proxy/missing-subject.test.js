import assert from 'node:assert/strict';
import { needsMissingSubjectClarification as needs } from './src/missing-subject.js';
import worker from './src/index.js';

for (const question of [
  'When did it start?', 'Why did they do that?', 'What did he mean?',
  'Which pioneer company was she in?', 'Where did she go after that?',
]) {
  assert.equal(needs({ question }), true, question);
  assert.equal(needs({ question, conversationContext: ['When did it start?', 'Why did they do that?'] }), true);
  assert.equal(needs({ question, selectedPioneer: true }), false);
  assert.equal(needs({ question, selectedPioneerName: 'Caroline Grant' }), false);
  assert.equal(needs({ question, conversationContext: ['Tell me about Caroline Grant.'] }), false);
  assert.equal(needs({ question, conversationContext: ['Tell me about Caroline Grant.', 'New topic:', 'When did it start?'] }), true);
}
for (const question of [
  'What did Joseph Smith say about his vision?', 'What does Jesus teach about love?',
  'Where is God in the Old Testament?', 'Why did God send His Son?',
  'Which pioneer company was Caroline Grant in?', 'How can I follow Jesus?',
  'What does it mean to follow Jesus?', 'Why is it important to forgive?',
  'What did he mean in John 3:16?',
]) assert.equal(needs({ question }), false, question);
assert.equal(needs({ question: 'Where did she go?', conversationContext: ['New topic: tell me about Eliza R. Snow.'] }), false);
const originalFetch = globalThis.fetch;
let externalCalls = 0;
try {
  globalThis.fetch = async () => { externalCalls++; throw new Error('Unresolved subject must not reach research or OpenAI'); };
  const response = await worker.fetch(new Request('https://worker.test', {
    method: 'POST', headers: { Origin: 'https://focuschrist.com', 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: 'Which pioneer company was she in?' }], focuschrist_page: 'pioneers' }),
  }), { OPENAI_API_KEY: 'offline-test-key' });
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.focuschrist_gateway_mode, 'missing-subject-clarification');
  assert.equal(payload.focuschrist_verifier_route, 'local-clarification');
  assert.equal(payload.focuschrist_openai_verifier_calls, 0);
  assert.equal(externalCalls, 0);
} finally {
  globalThis.fetch = originalFetch;
}
console.log('missing-subject: PASS');
