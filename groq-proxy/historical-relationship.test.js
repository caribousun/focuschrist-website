import assert from 'node:assert/strict';
import { hasWinterQuartersLocationSwap } from './src/historical-relationship.js';
import { hasKnownFalseClaim, guardVerifiedAnswer } from './src/index.js';

for (const answer of [
  'Whitney bought food for the Winter Quarters storehouse in St. Louis.',
  'The Winter Quarters storehouse was located in St. Louis.',
  'He supplied the storehouse in St. Louis for Winter Quarters.',
  'Winter Quarters had its storehouse in St. Louis.',
  'There was no rain. The Winter Quarters storehouse was in St. Louis.',
  'Winter Quarters was a temporary settlement. Resources for migration were strengthened when 500 men joined the Mormon Battalion; much of their pay was donated to the Church, enabling Bishop Newel K. Whitney to purchase food and supplies for the storehouse in St. Louis.',
  'Winter Quarters needed provisions. Whitney supplied its storehouse in St. Louis.',
  'At Winter Quarters, Whitney supplied the St. Louis storehouse.',
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
  'Winter Quarters needed provisions. Whitney purchased food and supplies in St. Louis for the storehouse.',
  'Winter Quarters needed provisions. Whitney bought supplies for the storehouse while in St. Louis.',
  'Winter Quarters needed provisions. Whitney did not place its storehouse in St. Louis; its storehouse in St. Louis is an incorrect description.',
  'A merchant supplied the storehouse in St. Louis.',
  'People remained in St. Louis while others settled at Winter Quarters.',
]) assert.equal(hasWinterQuartersLocationSwap(answer), false, answer);
console.log('PASS: observed Winter Quarters destination/purchase-location swap blocked; correct and negated relationships preserved.');
