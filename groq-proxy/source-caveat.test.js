import assert from 'node:assert/strict';
import {qualifyingBodyPositions} from './src/source-caveat.js';
const tokens = text => text.toLowerCase().match(/[a-z]+/g)||[];
const p = [
  'According to an unsubstantiated tradition, Danish settlers preceded the Icelanders. [1] Membership records provide no evidence of Scandinavians before their arrival. [2]',
  'Immigration brought families to the region.',
  '[1] Carter states that Danish converts already lived there.',
  '[2] Membership records show no Scandinavian names before Icelanders arrived.',
];
assert.deepEqual([...qualifyingBodyPositions(p,['scandinavians','danish'],tokens)],[0]);
assert.deepEqual([...qualifyingBodyPositions(p,['scandinavians','danish'],tokens,[2])],[0]);
assert.deepEqual([...qualifyingBodyPositions(p,['scandinavians','danish'],tokens,[1])],[],'unselected notes must not trigger retention');
assert.deepEqual([...qualifyingBodyPositions(p,['irrigation'],tokens,[2])],[],'unrelated author qualification must not displace requested evidence');
assert.deepEqual([...qualifyingBodyPositions(['Danish settlers arrived. [1]',p[2]],['danish'],tokens)],[],'ordinary citations do not receive qualification priority');
assert.deepEqual([...qualifyingBodyPositions([p[0],'[3] Danish settlement is described here.'],['danish'],tokens)],[],'a nonexistent cited note cannot trigger priority');
console.log('Source caveat context QA PASS');
