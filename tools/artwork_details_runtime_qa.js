const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
class Element {
    constructor() { this.listeners = {}; this.dataset = {}; this.attributes = {}; this.children = []; this.hidden = false; }
    addEventListener(name, fn) { this.listeners[name] = fn; }
    setAttribute(name, value) { this.attributes[name] = value; }
    removeAttribute(name) { delete this.attributes[name]; }
    before(node) { this.beforeNode = node; }
    after(node) { this.afterNode = node; }
    replaceChildren() { this.children = []; }
    appendChild(node) { this.children.push(node); }
    focus(options) { this.focused = true; this.focusOptions = options; }
    scrollIntoView(options) { this.scrollOptions = options; }
}
const ids = Object.fromEntries(['artworkDetailDialog','artworkDetailImage','artworkDetailEyebrow','artworkDetailTitle','artworkDetailCopy','artworkDetailSource','artworkDetailStudy','artworkDetailFullImage'].map(k => [k, new Element()]));
const dialog = ids.artworkDetailDialog;
const close = new Element();
dialog.querySelectorAll = () => [close];
dialog.querySelector = () => close;
dialog.showModal = () => { dialog.open = true; };
dialog.close = () => { dialog.open = false; dialog.listeners.close(); };
const figure = new Element();
const bodyTrigger = new Element();
bodyTrigger.dataset.artworkDetail = 'body';
bodyTrigger.href = '/body.webp';
bodyTrigger.closest = selector => selector === 'main figure' ? figure : null;
const otherTrigger = new Element();
otherTrigger.dataset.artworkDetail = 'hero';
otherTrigger.href = '/hero.webp';
otherTrigger.closest = () => null;
const record = new Element();
record.dataset = { detailImage: '/body.webp', detailImageAlt: 'Compassion', detailSource: 'https://example.org/source', detailFull: '/body.webp', detailStudy: '/study.html' };
record.querySelector = () => ({ textContent: 'Artwork study' });
record.querySelectorAll = () => [{ textContent: 'Meaningful artwork reflection.' }];
const classes = new Set();
const document = {
    getElementById: id => ids[id],
    createElement: () => new Element(),
    querySelector: () => record,
    querySelectorAll: () => [bodyTrigger, otherTrigger],
    body: { classList: { add: n => classes.add(n), remove: n => classes.delete(n) } },
};
vm.runInNewContext(fs.readFileSync('artwork-details.js','utf8'), { document, window: {location: {pathname:'/answers/death-of-a-child.html'}}, URLSearchParams });
function open(trigger) { trigger.listeners.click({button:0, preventDefault() {}}); }
const resume = ids.artworkDetailFullImage.afterNode;
assert.equal(resume.textContent, 'Continue Lesson');
open(bodyTrigger);
assert(dialog.open && !resume.hidden, 'Body artwork must offer Continue Lesson');
assert.equal(ids.artworkDetailSource.href, record.dataset.detailSource);
assert.equal(ids.artworkDetailStudy.href, '/study.html');
assert.equal(ids.artworkDetailFullImage.href, '/body.webp');
resume.listeners.click();
assert(!dialog.open && bodyTrigger.focused, 'Continue Lesson must close and restore invoking picture focus');
assert.equal(figure.scrollOptions.block, 'start', 'Continue Lesson must scroll its figure back into view');
assert(!classes.has('fc-dialog-open'));
figure.scrollOptions = null;
open(bodyTrigger);
close.listeners.click();
assert.equal(figure.scrollOptions, null, 'Ordinary Close must not scroll the lesson');
open(otherTrigger);
assert(resume.hidden, 'Non-body artwork must not gain an unrelated lesson action');
close.listeners.click();
assert(otherTrigger.focused, 'Existing close focus behavior must remain');
console.log('Legacy artwork runtime QA passed: body lesson return, focus, regular close, existing destinations, non-body scope.');
