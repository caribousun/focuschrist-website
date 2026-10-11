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

// Exercise Home's deferred heading return independently of non-Home legacy QA.
const heading = new Element(); heading.isConnected = true;
heading.hasAttribute = n => n in heading.attributes;
heading.getBoundingClientRect = () => ({top: 400});
figure.closest = () => ({querySelector: () => heading});
const header = {getBoundingClientRect: () => ({height: 52})};
let fixed = true;
document.querySelector = selector => selector.startsWith('.nav') ? header : record;
document.documentElement = {scrollHeight: 3000};
const frames = []; const scrolls = [];
const window = {location:{pathname:'/index.html'},scrollY:500,innerHeight:900,
 getComputedStyle:()=>({position:fixed?'fixed':'static'}),scrollTo:o=>scrolls.push(o)};
vm.runInNewContext(fs.readFileSync('artwork-details.js','utf8'),{document,window,URLSearchParams,requestAnimationFrame:fn=>frames.push(fn)});
const resume = ids.artworkDetailFullImage.afterNode;
function open(){bodyTrigger.listeners.click({button:0,preventDefault(){}});}
function flush(){while(frames.length)frames.shift()();}
open();resume.listeners.click();assert.equal(scrolls.length,0,'wait for modal layout');flush();
assert.equal(scrolls[0].top,832,'heading position minus actual fixed header and gap');
assert.equal(scrolls[0].behavior,'instant');assert(heading.focused);assert.equal(heading.attributes.tabindex,'-1');
heading.listeners.blur();assert(!('tabindex' in heading.attributes),'temporary focus target removed');
fixed=false;open();resume.listeners.click();flush();assert.equal(scrolls[1].top,884,'static phone header adds no height');
open();close.listeners.click();flush();assert.equal(scrolls.length,2,'ordinary Close does not move lesson');
assert(bodyTrigger.focused,'ordinary Close restores trigger');
open();resume.listeners.click();open();flush();assert.equal(scrolls.length,2,'reopened dialog cancels deferred return');
close.listeners.click();heading.isConnected=false;open();resume.listeners.click();flush();assert.equal(scrolls.length,2,'detached target cancels return');
console.log('Home return QA passed: deferred heading, fixed/static header, focus, Close, reopened and detached guards.');
