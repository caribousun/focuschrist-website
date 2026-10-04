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
  { name: 'static phone', position: 'static', height: 200, top: 0, margin: 68, expected: null },
  { name: 'other page keeps existing behavior', position: 'sticky', height: 100, top: 74, margin: 68, otherPage: true, expected: null },
  { name: 'near document start clamps', position: 'sticky', height: 100, top: 74, margin: 68, documentTop: 100, expected: 0 },
];
for (const c of cases) {
  const dom = new JSDOM(html, { url: 'https://focuschrist.com/art-study/the-good-shepherd.html', runScripts: 'outside-only' });
  const { window } = dom; const { document } = window;
  if (c.otherPage) document.querySelector('main').classList.remove('fc-art-study-page');
  window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
  window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
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
  assert.equal(document.activeElement, target, `${c.name}: focus restored to same lesson target`);
  assert.equal(document.querySelector('dialog').open, false, `${c.name}: detail closes`);
  if (c.expected === null) {
    assert.equal(scrolling, null, `${c.name}: no new measured scrolling`);
    assert.equal(fallback.target, target, `${c.name}: existing fallback preserved`);
    assert.equal(fallback.options.block, 'start');
  } else {
    assert.equal(fallback, null, `${c.name}: only one scroll mechanism`);
    assert(scrolling && Math.abs(scrolling.top - c.expected) < 0.001, `${c.name}: expected${c.expected}, got${scrolling?.top}`);
    assert.equal(scrolling.behavior, 'instant', `${c.name}: no intermediate smooth-scroll occlusion`);
  }
  dom.window.close();
}
console.log(`PASS ${cases.length} measured clearance and preserved-behavior cases; native viewport checks still required.`);
