import assert from 'node:assert/strict';
import { hasWinterQuartersLocationSwap } from './src/historical-relationship.js';
import { hasKnownFalseClaim, guardVerifiedAnswer } from './src/index.js';

for (const answer of [
  'Whitney bought food for the Winter Quarters storehouse in St. Louis.',
  'The Winter Quarters storehouse was located in St. Louis.',
  'He supplied the storehouse in St. Louis for Winter Quarters.',
  'Winter Quarters had its storehouse in St. Louis.',
  'There was no rain. The Winter Quarters storehouse was in St. Louis.',
]) {
  assert.equal(hasWinterQuartersLocationSwap(answer), true, answer);
  assert.equal(hasKnownFalseClaim(answer), true, answer);
  assert.notEqual(guardVerifiedAnswer(answer, [{url:'https://www.churchofjesuschrist.org/study/history/topics/winter-quarters?lang=eng'}], {faith:true}, true), answer);
}
for (const answer of [
  'Whitney purchased food and supplies in St. Louis for the Winter Quarters storehouse.',
  'The supplies purchased in St. Louis were intended for the storehouse at Winter Quarters.',
  'The Winter Quarters storehouse was not located in St. Louis.',
  'The Winter Quarters storehouse in St. Louis is an incorrect description.',
  'There was no Winter Quarters storehouse in St. Louis.',
  'People remained in St. Louis while others settled at Winter Quarters.',
]) assert.equal(hasWinterQuartersLocationSwap(answer), false, answer);
console.log('PASS: observed Winter Quarters destination/purchase-location swap blocked; correct and negated relationships preserved.');
