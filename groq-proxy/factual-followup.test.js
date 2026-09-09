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
