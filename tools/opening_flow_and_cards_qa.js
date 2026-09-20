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
  const listeners = [];
  const media = {matches:true, addEventListener(type, listener) { listeners.push(listener); }};
  w.matchMedia = () => media;
  const initialOpening = w.document.querySelector('.fc-topic-opening, .fc-page-intro, .fc-gallery-intro, .cfm-hero, .gc-page-opening');
  const originalText = initialOpening?.textContent.replace(/\s+/g, ' ').trim();
  const originalLinks = initialOpening ? [...initialOpening.querySelectorAll('a[href]')].map(a => a.href) : [];
  w.eval('function initOpeningInvitation() {}\n' + fn + '\ninitMobileOpening();');
  const opening = w.document.querySelector('.fc-mobile-cued-opening');
  if (opening) {
    assert.equal(w.document.querySelectorAll('.fc-mobile-hero-surround').length, 0, page + ': owner rejected side treatment');
    const cue = opening.querySelector('.fc-mobile-scroll-cue');
    assert(cue, page + ': missing mobile invitation');
    assert.equal(cue.parentElement, opening.querySelector('.fc-page-intro') || opening, page + ': cue must follow introduction content');
    const target = w.document.getElementById(cue.hash.slice(1));
    assert(target, page + ': missing next-section destination');
    assert(!target.hidden, page + ': mobile cue targets hidden supporting content');
    assert.equal(opening.querySelectorAll('.fc-mobile-scroll-cue').length, 1, page + ': duplicate invitation');
    for (const action of opening.querySelectorAll('[data-fc-mobile-label]')) {
      assert(action.getAttribute('aria-label').includes(action.textContent.trim()), page + ': accessible name must include visible action wording');
    }
    if (!w.document.body.classList.contains('fc-main-opening')) {
      const restoredCopy = opening.cloneNode(true);
      restoredCopy.querySelector('.fc-mobile-scroll-cue').remove();
      assert.equal(restoredCopy.textContent.replace(/\s+/g, ' ').trim(), originalText, page + ': individual study opening must remain untouched');
      assert.equal(w.document.querySelectorAll('.fc-mobile-opening-notes, [data-fc-mobile-label]').length, 0, page + ': main-page redesign escaped its scope');
    }
    openings++;
    media.matches = false;
    listeners.forEach(listener => listener());
    const desktopCopy = opening.cloneNode(true);
    desktopCopy.querySelector('.fc-mobile-scroll-cue').remove();
    assert.equal(desktopCopy.textContent.replace(/\s+/g, ' ').trim(), originalText, page + ': desktop copy must restore exactly');
    assert.deepEqual([...desktopCopy.querySelectorAll('a[href]')].map(a => a.href), originalLinks, page + ': desktop destinations changed');
    assert([...w.document.querySelectorAll('.fc-mobile-opening-notes')].every(n => n.hidden), page + ': mobile notes visible on desktop');
    media.matches = true;
    listeners.forEach(listener => listener());
    assert(!target.hidden, page + ': cue target must return with mobile layout');
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
