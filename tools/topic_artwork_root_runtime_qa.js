const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('topic-artwork-details.js', 'utf8');
function run({ main = null, opted = null, loading = false } = {}) {
  const queried = [], scanned = [];
  function container(name) { return { querySelectorAll(selector) { scanned.push([name, selector]); return []; } }; }
  const nodes = { main: main && container('main'), '[data-topic-artwork-root]': opted && container('opted') };
  let ready;
  const document = {
    readyState: loading ? 'loading' : 'complete',
    getElementById() { return null; },
    querySelector(selector) { queried.push(selector); assert(selector in nodes, 'No broad body/document artwork scan'); return nodes[selector]; },
    addEventListener(event, fn) { assert.equal(event, 'DOMContentLoaded'); ready = fn; },
    createElement() { throw new Error('No empty-root dialog should be created'); }
  };
  vm.runInNewContext(source, { document, HTMLDialogElement: function () {} });
  if (loading) { assert.equal(scanned.length, 0); ready(); }
  return { queried, scanned };
}
assert.deepEqual(run(), { queried: ['main', '[data-topic-artwork-root]'], scanned: [] });
assert.equal(run({ main: true }).scanned[0][0], 'main');
assert.deepEqual(run({ main: true, opted: true }).queried, ['main']);
for (const loading of [false, true]) {
  const result = run({ opted: true, loading });
  assert.equal(result.scanned.length, 1);
  assert.equal(result.scanned[0][0], 'opted');
  assert.match(result.scanned[0][1], /^figure > a\[href\]/);
}
console.log('Scoped artwork root PASS: unmarked legacy page remains untouched; main precedence preserved; only explicit root scanned on immediate/deferred initialization. Native panel action review remains separate.');
