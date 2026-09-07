/* Offline behavioral checks for progressive conference filtering. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '..', 'general-conference.js'), 'utf8');
function element(extra = {}) {
  return Object.assign({ hidden: false, disabled: false, value: '', textContent: '', events: {},
    addEventListener(name, fn) { this.events[name] = fn; },
    click() { this.events.click?.(); }, focus() { this.focused = true; } }, extra);
}
const search = element(), session = element({ value: 'all' }), reset = element();
const status = element(), empty = element(), controls = element({ hidden: true }), secondaryReset = element();
const sets = [
  ['saturday-morning', true, ['Prayers for Peace Henry B. Eyring', 'Ministering Kristin M. Yee']],
  ['saturday-afternoon', false, ['Love All; Love Each Gérald Caussé', 'Church Auditing Department Report, 2025 Jared B. Larson']],
  ['sunday-morning', false, ['Alive in Christ Dallin H. Oaks']],
  ['sunday-afternoon', false, ['Eternal Marriage Is an Eternal Journey Neil L. Andersen', 'Closing Remarks Dallin H. Oaks']]
];
const groups = sets.map(([id, open, texts]) => element({ open, dataset: { conferenceSession: id },
  cards: texts.map(text => element({ dataset: { conferenceSearch: text } })),
  querySelectorAll() { return this.cards; } }));
const cards = groups.flatMap(g => g.cards);
const nodes = { '#conference-search': search, '#conference-session': session,
  '[data-conference-reset]': reset, '[data-conference-status]': status,
  '[data-conference-empty]': empty, '[data-conference-controls]': controls };
const root = { querySelector: selector => nodes[selector] || null,
  querySelectorAll: selector => ({ '[data-conference-session]': groups,
    '[data-conference-talk]': cards, '[data-conference-clear]': [secondaryReset] })[selector] || [] };
vm.runInNewContext(source, { document: { getElementById: () => root } });
const visible = () => cards.filter(card => !card.hidden);
function query(value, selected = 'all') { search.value = value; session.value = selected; search.events.input(); }
assert.equal(controls.hidden, false, 'controls are revealed only after initialization');
assert.equal(visible().length, 7);
assert.equal(status.textContent, '7 messages across 4 sessions. Open a session to browse.');
assert.equal(empty.hidden, true); assert.equal(reset.disabled, true);
query('  GERALD   CAUSSE  ');
assert.equal(visible().length, 1, 'search folds case, accents and whitespace');
assert.equal(groups[1].open, true); assert.equal(groups[0].hidden, true);
query('oaks christ'); assert.equal(visible().length, 1, 'all query words must match a card');
query('Oaks', 'sunday-afternoon'); assert.equal(visible().length, 1, 'session and text filters combine');
assert.match(visible()[0].dataset.conferenceSearch, /Closing/);
session.value = 'saturday-morning'; session.events.change();
assert.equal(visible().length, 0); assert.equal(empty.hidden, false);
assert.equal(groups.every(g => g.hidden), true);
assert.equal(status.textContent, '0 of 7 messages match your selection.');
secondaryReset.click();
assert.equal(search.value, ''); assert.equal(session.value, 'all');
assert.equal(search.focused, true); assert.equal(visible().length, 7);
assert.deepEqual(groups.map(g => g.open), [true, false, false, false], 'reset restores initial disclosure state');
query('   '); assert.equal(reset.disabled, true, 'whitespace does not activate filters');
query('', 'saturday-afternoon'); assert.equal(visible().length, 2, 'session-only browsing works');
assert.equal(groups[1].open, true);
vm.runInNewContext(source, { document: { getElementById: () => null } });
const common = fs.readFileSync(path.join(__dirname, '..', 'site-common.js'), 'utf8');
const migrationStart = common.indexOf('const conferenceLegacyAnchors');
const migrationEnd = common.indexOf('const RESPECTFUL_QUESTION_RESPONSE', migrationStart);
assert.ok(migrationStart >= 0 && migrationEnd > migrationStart, 'legacy migration must be present');
function legacy(pathname, hash, search = '') {
  const replacements = [], events = {};
  const location = { pathname, hash, search, replace: value => replacements.push(value) };
  vm.runInNewContext(common.slice(migrationStart, migrationEnd), {
    window: { location, addEventListener: (name, fn) => { events[name] = fn; } }
  });
  return { replacements, events, location };
}
assert.deepEqual(legacy('/answers.html', '#general-conference').replacements, ['general-conference.html']);
assert.deepEqual(legacy('/answers.html', '#conference-messages', '?source=bookmark').replacements,
  ['general-conference.html?source=bookmark#conference-messages']);
for (const [page, hash] of [['/answers.html', '#connected-study'], ['/general-conference.html', '#conference-topics'], ['/ask.html', '#general-conference']]) {
  assert.deepEqual(legacy(page, hash).replacements, [], 'unrelated locations must not redirect');
}
const changed = legacy('/answers.html', '#connected-study');
changed.location.hash = '#conference-practice'; changed.events.hashchange();
assert.deepEqual(changed.replacements, ['general-conference.html#conference-practice']);
console.log('GENERAL CONFERENCE RUNTIME QA PASS: search, combined filters, empty state, reset, disclosure state, and exact legacy bookmark migration.');
