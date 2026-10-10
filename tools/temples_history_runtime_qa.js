// Interaction contract; rendered framing, likeness and text-scale checks remain separate.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const dom = new JSDOM(read('answers/why-latter-day-saints-build-temples.html'), {
  url: 'https://focuschrist.com/answers/why-latter-day-saints-build-temples.html', runScripts: 'outside-only'
});
const { window } = dom;
const { document } = window;
window.TextEncoder = TextEncoder; let qaReturnTarget, qaScroll; const qaStyle=window.getComputedStyle.bind(window); window.getComputedStyle = el => el===qaReturnTarget ? {scrollMarginTop:'200px'} : qaStyle(el); Object.defineProperty(window.document.documentElement,'scrollHeight',{value:10000}); window.scrollTo = options => { qaScroll=options; }; const prepareReturn = target => { qaReturnTarget=target; qaScroll=null; target.getBoundingClientRect=()=>({top:2000}); }; const frames=new Map(); let frameId=0; window.requestAnimationFrame=fn=>{frames.set(++frameId,fn);return frameId;}; window.cancelAnimationFrame=id=>frames.delete(id); const tickFrames=()=>{const batch=[...frames.values()];frames.clear();batch.forEach(fn=>fn());};
window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
window.HTMLElement.prototype.scrollIntoView = function () { this.dataset.qaScrolled = 'true'; };
for (const script of document.scripts) {
  const asset = script.src && new URL(script.src).pathname.slice(1);
  if (['topic-artwork-details.js', 'full-image-viewer.js'].includes(asset)) window.eval(read(asset));
}
document.dispatchEvent(new window.Event('DOMContentLoaded'));
const pictures = [...document.querySelectorAll('#temple-history figure > a')];
assert(pictures.length >= 15, 'At least fifteen additional original pictures must be integrated');
const click = node => node.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
const originals = new Set();
let newsroomPills = 0;
const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
assert.equal(ids.length, new Set(ids).size, 'Page IDs must be unique');
for (const a of document.querySelectorAll('#temple-history a[href^="#"]')) assert(document.getElementById(a.hash.slice(1)), 'Every chapter destination exists');
for (const trigger of pictures) {
  assert(!originals.has(trigger.href), 'Every chronological picture has a distinct original'); originals.add(trigger.href);
  assert(trigger.hasAttribute('data-topic-artwork-detail'), 'Shared study panel attached');
  assert(!trigger.hasAttribute('data-full-image-viewer'), 'Study opens before full image');
  const figure = trigger.closest('figure');
  const caption = figure.querySelector('figcaption');
  const expectedSources = [...new Set([...caption.querySelectorAll('a[href^="https://www.churchofjesuschrist.org"],a[href^="https://newsroom.churchofjesuschrist.org"],a[href^="https://www.josephsmithpapers.org"]')].map(a => a.href))];
  assert(expectedSources.length, 'Each picture has official sources');
  trigger.focus(); click(trigger);
  const panel = document.getElementById('topicArtworkDetailDialog');
  const viewer = document.querySelector('.fc-full-image-viewer');
  assert(panel.open && !viewer.open, 'Study panel opens first');
  assert.equal(panel.querySelector('h2').textContent, caption.querySelector('h3').textContent);
  assert.deepEqual([...panel.querySelectorAll('[data-topic-art-source]')].map(a => a.href), expectedSources.slice(0, 3));
  newsroomPills += [...panel.querySelectorAll('[data-topic-art-source]')].filter(a => new URL(a.href).hostname === 'newsroom.churchofjesuschrist.org').length;
  const full = panel.querySelector('[data-full-image-viewer]');
  full.focus(); click(full); assert(viewer.open && panel.open, 'Full image nests over study');
  click(viewer.querySelector('button')); assert(!viewer.open && panel.open);
  assert.equal(document.activeElement, full, 'Nested close restores focus');
  click(panel.querySelector('[data-topic-art-close]')); assert(!panel.open);
  assert.equal(document.activeElement, trigger, 'Close restores invoking picture focus');
  click(trigger);
  const resume = panel.querySelector('[data-topic-art-continue]');
  const target = document.getElementById(new URL(resume.href).hash.slice(1));
  assert(target.closest('.fc-temple-history__chapter'), 'Continue Lesson returns to its chapter');
  prepareReturn(target); click(resume); tickFrames(); tickFrames(); assert.equal(document.activeElement, target); assert.equal(qaScroll?.top,1800); assert.equal(qaScroll.behavior,'instant');
  assert(!panel.open && !document.body.classList.contains('fc-dialog-open'));
}
assert(newsroomPills >= 1, 'Official Newsroom sources must remain available inside artwork studies');
dom.window.close();
console.log(`Temple history DOM QA passed: ${pictures.length} picture studies, chapter links, official source pills, nested full-size, close/reopen, focus and lesson return.`);
