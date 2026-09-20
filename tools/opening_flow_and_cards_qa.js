// Structural regression coverage; actual geometry is checked in a rendered browser.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {JSDOM, VirtualConsole} = require('jsdom');
const source = fs.readFileSync('site-common.js', 'utf8');
const fn = source.slice(source.indexOf('    function initMobileOpening('), source.indexOf('    function initExternalLinks('));
const pages = [...fs.readFileSync('sitemap.xml', 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)]
  .map(m => new URL(m[1]).pathname.slice(1) || 'index.html');
let openings = 0;
for (const page of pages) {
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => {
    // JSDOM does not implement modern CSS; this gate tests structure only.
    if (error.type !== 'css parsing') throw error;
  });
  const dom = new JSDOM(fs.readFileSync(page, 'utf8'), {url:'https://focuschrist.com/' + page, runScripts:'outside-only', virtualConsole});
  const w = dom.window;
  w.matchMedia = () => ({matches:true, addEventListener() {}});
  // Pseudo-element painting is a browser check, not a JSDOM feature.
  const computedStyle = w.getComputedStyle.bind(w);
  w.getComputedStyle = (element, pseudo) => pseudo ? {backgroundImage:'none'} : computedStyle(element);
  w.eval('function initOpeningInvitation() {}\n' + fn + '\ninitMobileOpening();');
  const opening = w.document.querySelector('.fc-mobile-cued-opening');
  if (opening) {
    for (const surround of w.document.querySelectorAll('.fc-mobile-hero-surround')) {
      assert.equal(surround.getAttribute('aria-hidden'), 'true', page + ': decorative surround must be silent');
      assert.equal(surround.parentElement.querySelectorAll(':scope > .fc-mobile-hero-surround').length, 1);
    }
    const cue = opening.querySelector('.fc-mobile-scroll-cue');
    assert(cue, page + ': missing mobile invitation');
    assert.equal(cue.parentElement, opening.querySelector('.fc-page-intro') || opening, page + ': cue must follow introduction content');
    assert(w.document.getElementById(cue.hash.slice(1)), page + ': missing next-section destination');
    assert.equal(opening.querySelectorAll('.fc-mobile-scroll-cue').length, 1, page + ': duplicate invitation');
    openings++;
  }
  if (page === 'answers.html') {
    for (const grid of w.document.querySelectorAll('.fc-grid--2')) {
      assert.equal(grid.children.length % 2, 0, 'Answers directory leaves an unfinished row');
      for (const card of grid.querySelectorAll(':scope > a')) {
        assert(fs.existsSync(new URL(card.href).pathname.slice(1)), 'Missing study: ' + card.href);
      }
    }
  }
  dom.window.close();
}
assert.equal(openings, 40, 'Every canonical page except Search has an opening invitation');
console.log('Opening flow and cards QA PASS: 40 contained cue destinations; complete Answers rows.');
