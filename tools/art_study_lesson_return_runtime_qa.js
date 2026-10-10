// DOM regression for measured lesson-return clearance; native layout remains a separate gate.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const site = process.env.SITE_ROOT || path.resolve(__dirname, '..');
const { JSDOM } = require('jsdom');
const candidate = process.argv[2] || path.join(site, 'topic-artwork-details.js');
const source = fs.readFileSync(candidate, 'utf8');
const html = fs.readFileSync(path.join(site, 'art-study/the-good-shepherd.html'), 'utf8');
const cases = [
  { name: 'desktop sticky', position: 'sticky', height: 71.2, top: 74, margin: 68, expected: 1838.8 },
  { name: 'wrapped sticky', position: 'sticky', height: 151, top: 74, margin: 68, expected: 1759 },
  { name: 'target margin wins', position: 'sticky', height: 71.2, top: 74, margin: 200, expected: 1800 },
  { name: 'fixed navigation', position: 'fixed', height: 100, top: 52, margin: 68, expected: 1832 },
  { name: 'static phone measured margin', position: 'static', height: 200, top: 0, margin: 68, expected: 1932 },
  { name: 'other page ignores local study nav', position: 'sticky', height: 100, top: 74, margin: 68, otherPage: true, expected: 1932 },
  { name: 'near document start clamps', position: 'sticky', height: 100, top: 74, margin: 68, documentTop: 100, expected: 0 },
];
for (const c of cases) {
  const dom = new JSDOM(html, { url: 'https://focuschrist.com/art-study/the-good-shepherd.html', runScripts: 'outside-only' });
  const { window } = dom; const { document } = window;
  if (c.otherPage) document.querySelector('main').classList.remove('fc-art-study-page');
  window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
  window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
  let frameId = 0; const frames = new Map(); const timers = new Map();
  window.requestAnimationFrame = fn => { frames.set(++frameId, fn); return frameId; };
  window.cancelAnimationFrame = id => frames.delete(id);
  window.setTimeout = (fn, delay) => { timers.set(++frameId, {fn, delay}); return frameId; };
  window.clearTimeout = id => timers.delete(id);
  const tick = () => { const batch = [...frames.values()]; frames.clear(); batch.forEach(fn => fn()); };
  Object.defineProperty(document.documentElement, 'scrollHeight', { value: 10000 });
  let fallback = null; let scrolling = null;
  window.HTMLElement.prototype.scrollIntoView = function (options) { fallback = { target: this, options }; };
  window.scrollTo = options => { scrolling = options; };
  Object.defineProperty(window, 'scrollY', { value: 700 });
  const nav = document.querySelector('.fc-study-nav');
  nav.getBoundingClientRect = () => ({ height: c.height, top: c.top });
  const getComputedStyle = window.getComputedStyle.bind(window);
  window.getComputedStyle = element => element === nav ? { position: c.position, top: c.top + 'px' }
    : element.hasAttribute('data-topic-reading-target') ? { scrollMarginTop: c.margin + 'px' } : getComputedStyle(element);
  window.eval(source); document.dispatchEvent(new window.Event('DOMContentLoaded'));
  const trigger = document.querySelector('#shepherd-binds-hurt-20261004 a[data-topic-artwork-detail]');
  const target = document.getElementById('shepherd-binds-hurt-20261004-title');
  target.getBoundingClientRect = () => ({ top: (c.documentTop ?? 2000) - window.scrollY });
  const click = el => el.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
  click(trigger); click(document.querySelector('[data-topic-art-continue]'));
  assert.equal(scrolling, null, `${c.name}: close must not measure stale layout synchronously`);
  tick(); tick();
  assert.equal(document.activeElement, target, `${c.name}: focus restored to same lesson target`);
  assert.equal(document.querySelector('dialog').open, false, `${c.name}: detail closes`);
  assert.equal(fallback, null, `${c.name}: only measured scrolling`);
  assert(scrolling && Math.abs(scrolling.top - c.expected) < 0.001, `${c.name}: expected${c.expected}, got${scrolling?.top}`);
  assert.equal(scrolling.behavior, 'instant', `${c.name}: no intermediate smooth-scroll occlusion`);
  window.dispatchEvent(new window.Event('wheel'));
  assert.equal(frames.size, 0, `${c.name}: reader cancels pending frames`);
  assert.equal(timers.size, 0, `${c.name}: reader cancels all pending correction timers`);
  dom.window.close();
}
console.log(`PASS ${cases.length} measured clearance and deferred/cancelled-alignment cases; native viewport checks still required.`);
