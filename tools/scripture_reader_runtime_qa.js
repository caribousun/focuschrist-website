/* Node-only contract/runtime tests. Actual browser presentation is a separate review gate. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const api = require('../scripture-reader.js');
const base = 'https://www.churchofjesuschrist.org/study/scriptures/nt/john/20';
assert.deepEqual(api.reference(base + '?id=p1-p3,p5&lang=eng', '').selection, [1, 2, 3, 5]);
assert.deepEqual(api.reference(base + '#p2', '').selection, [2]);
assert.deepEqual(api.reference(base, 'John 20:1–3').selection, [1, 2, 3]);
assert.equal(api.reference(base, 'John 19:1').selection, null);
assert.equal(api.reference(base, 'Compare John 20:1 and Matthew 3:2').selection, null);
assert.equal(api.reference(base, 'Read John 20').selection, null);
assert.deepEqual(api.reference(base + '.2', 'John 20:2-3').selection, [2, 3]);
assert.deepEqual(api.reference(base + '.2-3', '').selection, [2, 3]);
assert.deepEqual(api.reference(base + '.2?id=p5', 'John 20:2-3').selection, [5]);
for (const suffix of ['?id=p3-p1', '?id=p0', '?id=p1-p10000', '?id=oops']) assert.equal(api.reference(base + suffix, '').invalid, true);
for (const url of [base.replace('www.churchofjesuschrist.org', 'evil.churchofjesuschrist.org'), base.replace('https:', 'http:'), base.replace('/nt/', '/manual/'), base + '/foo', 'javascript:alert(1)']) assert.equal(api.reference(url, ''), null);
const data = { title: 'John 20', source_url: base + '?lang=eng', verified_on: '2026-09-06', verses: [{ number: 1, text: '<b>Plain source text</b>' }, { number: 2, text: 'Second verse.' }, { number: 3, text: 'Third verse.' }] };
const ref = api.reference(base, '');
assert.equal(api.validate(data, ref), data);
assert.throws(() => api.validate({ ...data, source_url: base.replace('/20', '/21') + '?lang=eng' }, ref));
assert.throws(() => api.validate({ ...data, verses: [data.verses[0], data.verses[0]] }, ref));
assert.throws(() => api.selectVerses(data, [1, 4]));
assert.equal(api.selectVerses(data, null).length, 3);
class Element {
    constructor(tag = 'div') { this.tagName = tag; this.listeners = {}; this.attributes = {}; this.children = []; this.textContent = ''; this.isConnected = true; this.open = false; }
    setAttribute(k, v) { this.attributes[k] = v; }
    removeAttribute(k) { delete this.attributes[k]; }
    hasAttribute(k) { return Object.hasOwn(this.attributes, k); }
    addEventListener(k, fn) { this.listeners[k] = fn; }
    appendChild(child) { this.children.push(child); return child; }
    replaceChildren(...children) { this.children = children; }
    focus() { this.focused = true; }
    closest(selector) { return selector === 'a[href]' && this.tagName === 'a' ? this : null; }
    showModal() { this.open = true; }
    close() { this.open = false; this.listeners.close(); }
}
const nodes = new Map();
const dialog = new Element('dialog');
dialog.querySelector = selector => { if (!nodes.has(selector)) nodes.set(selector, new Element()); return nodes.get(selector); };
const classes = new Set(['existing-artwork-lock']);
const listeners = {};
const document = { getElementById: () => null, createElement: tag => tag === 'dialog' ? dialog : new Element(tag), createTextNode: text => ({ textContent: text }), createDocumentFragment: () => new Element('fragment'), body: { appendChild() {}, classList: { contains: x => classes.has(x), add: x => classes.add(x), remove: x => classes.delete(x) } }, addEventListener: (type, fn) => { listeners[type] = fn; } };
let requests = [];
const context = { document, HTMLDialogElement: Element, URL, Set, Map, fetch: url => new Promise(resolve => requests.push({ url, resolve })) };
context.window = context;
vm.runInNewContext(fs.readFileSync(require.resolve('../scripture-reader.js'), 'utf8'), context);
function click(href = base + '?id=p1', props = {}, attrs = {}) {
    const link = new Element('a'); link.href = href; link.textContent = 'John 20:1'; link.attributes = attrs;
    const event = { target: link, button: 0, preventDefault() { this.defaultPrevented = true; }, ...props };
    listeners.click(event); return { link, event };
}
const flush = () => new Promise(resolve => setImmediate(resolve));
(async () => {
    for (const props of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }, { defaultPrevented: true }]) { click(base, props); assert.equal(requests.length, 0); }
    click(base, {}, { download: '' }); click(base, {}, { 'data-scripture-source': '' }); assert.equal(requests.length, 0);
    const first = click(); assert.equal(first.event.defaultPrevented, true); assert.equal(dialog.open, true); assert(classes.has('fc-scripture-open'));
    assert.equal(requests[0].url, '/scripture-data/nt/john/20.json');
    dialog.close(); assert(first.link.focused); assert(!classes.has('fc-scripture-open')); assert(classes.has('existing-artwork-lock'));
    const second = click(base + '?id=p2'); assert.equal(requests.length, 1, 'one request per cached chapter');
    requests[0].resolve({ ok: true, json: async () => data }); await flush();
    assert.equal(nodes.get('#fc-scripture-title').textContent, 'John 20:2', 'closed request must not overwrite reopened selection');
    const fragment = nodes.get('.fc-scripture-verses').children[0];
    assert.equal(fragment.children.length, 1); assert.equal(fragment.children[0].children[1].textContent, ' Second verse.');
    click(base + '?id=p1'); await flush();
    assert.equal(nodes.get('.fc-scripture-verses').children[0].children[0].children[1].textContent, ' <b>Plain source text</b>', 'source is a text node, never inserted HTML');
    click(base + '?id=p1-p4'); await flush(); assert.match(nodes.get('.fc-scripture-status').textContent, /not available/); assert.equal(nodes.get('.fc-scripture-verses').children.length, 0, 'missing verse cannot produce a truncated passage');
    click(base.replace('/20', '/21')); assert.equal(requests.length, 2);
    requests[1].resolve({ ok: false }); await flush(); assert.match(nodes.get('.fc-scripture-status').textContent, /not available/);
    click(base.replace('/20', '/21')); assert.equal(requests.length, 3, 'failed fetch may retry');
    dialog.close(); requests[2].resolve({ ok: false }); await flush(); assert.equal(dialog.open, false);
    click(); await flush();
    dialog.listeners.pointerdown({ target: dialog }); dialog.listeners.click({ target: dialog }); assert.equal(dialog.open, false, 'backdrop click closes');
    click(); await flush(); nodes.get('.fc-scripture-close').listeners.click(); assert.equal(dialog.open, false, 'footer close works');
    click(); await flush(); nodes.get('.fc-scripture-x').listeners.click(); assert.equal(dialog.open, false, 'top close works');
    assert.equal(nodes.get('.fc-scripture-source').href, base + '?id=p1', 'source preserves the requested original URL');
    console.log('PASS: scripture reader URL, verse selection, source validation, safe rendering, delegated click, cache, race, fallback, close and focus/scroll-lock runtime contracts. Browser focus trapping, Escape, scrolling and presentation require real browser QA.');
})().catch(error => { console.error(error); process.exitCode = 1; });
