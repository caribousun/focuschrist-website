// Structural regression coverage; actual geometry is checked in a rendered browser.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {JSDOM, VirtualConsole} = require('jsdom');
const source = fs.readFileSync('site-common.js', 'utf8');
const fn = source.slice(source.indexOf('    function initMobileOpening('), source.indexOf('    function initExternalLinks('));
const pages = [...fs.readFileSync('sitemap.xml', 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)]
  .map(m => new URL(m[1]).pathname.slice(1) || 'index.html');
const ADAMS_INTRO = 'timelines/adams-1881-introduction.html';
const openingPages = [];
function checkOpeningInventory(found) {
  assert.equal(new Set(found).size, found.length, 'Canonical opening routes must be unique');
  assert.equal(found.filter(page => page === ADAMS_INTRO).length, 1, 'Adams must retain its canonical opening invitation');
  assert.equal(found.filter(page => page !== ADAMS_INTRO).length, 46, 'The 46 historical canonical openings must retain their invitations');
}
function selfTestOpeningInventory() {
  const historical = Array.from({length:46}, (_, i) => `historical-${i}.html`);
  checkOpeningInventory([...historical, ADAMS_INTRO]);
  for (const mutation of [historical, [...historical.slice(1), ADAMS_INTRO], [...historical, ADAMS_INTRO, ADAMS_INTRO], [...historical, ADAMS_INTRO, 'extra.html']]) {
    assert.throws(() => checkOpeningInventory(mutation), 'Opening inventory regression escaped');
  }
}
selfTestOpeningInventory();
const sectionCopyPages = new Set([
  'answers/what-is-eternal-marriage.html',
  'answers/look-unto-me-doctrine-and-covenants-6-36.html',
  'answers/bible-and-book-of-mormon-together.html',
  'answers/melchizedek-priesthood-restoration.html',
  'birth-of-christ.html',
  'art-study/the-living-christ.html', 'art-study/the-good-shepherd.html',
  'art-study/suffer-the-little-children.html', 'art-study/be-still.html'
]);
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
  const artCopy = page.startsWith('art-study/') ? initialOpening?.querySelector('.fc-page-intro-copy') : null;
  const artCopyMarkup = artCopy?.innerHTML;
  const originalText = initialOpening?.textContent.replace(/\s+/g, ' ').trim();
  const originalLinks = initialOpening ? [...initialOpening.querySelectorAll('a[href]')].map(a => a.href) : [];
  w.eval('function initOpeningInvitation() {}\n' + fn + '\ninitMobileOpening();');
  if (artCopy) {
    assert(initialOpening.contains(artCopy), page + ': Art introduction must remain in the mobile opening');
    assert.equal(artCopy.innerHTML, artCopyMarkup, page + ': Preserve complete Art introduction wording');
    assert(!artCopy.closest('.fc-mobile-opening-notes'), page + ': Art introduction must not move below Continue');
  }
  const opening = w.document.querySelector('.fc-mobile-cued-opening');
  if(page==='joseph-smith-likeness.html'){
    assert.equal(w.document.querySelectorAll('.fc-visual-hero[data-hero-viewer]').length,1,'Joseph gateway retains its reviewed artwork');
    assert.equal(w.document.querySelector('.joseph-bridge-intro h1').textContent,'Explore his life and the portrait');
    assert.deepEqual([...w.document.querySelectorAll('#joseph-study-entrance .fc-button--primary')].map(a=>a.getAttribute('href')),['answers/who-was-joseph-smith.html#joseph-family-life','joseph-smith-portrait-research.html']);
    assert(!w.document.querySelector('.fc-mobile-scroll-cue'),'Compact gateway must expose destinations directly');
  }
  if (opening) {
    assert.equal(w.document.querySelectorAll('.fc-mobile-hero-surround').length, 0, page + ': owner rejected side treatment');
    const cue = opening.querySelector('.fc-mobile-scroll-cue');
    assert(cue, page + ': missing mobile invitation');
    assert.equal(cue.parentElement, opening.querySelector('.fc-page-intro') || opening, page + ': cue must follow introduction content');
    const target = w.document.getElementById(cue.hash.slice(1));
    assert(target, page + ': missing next-section destination');
    assert(!target.hidden, page + ': mobile cue targets hidden supporting content');
    if (sectionCopyPages.has(page) && w.document.querySelector('.fc-mobile-opening-notes')) {
      assert.equal(target, w.document.querySelector('.fc-mobile-opening-notes'), page + ': Continue must not skip retained introduction');
    }
    if (page === 'answers/look-unto-me-doctrine-and-covenants-6-36.html') {
      assert(target.textContent.includes('Look unto me in every thought; doubt not, fear not.'), 'Exact scripture must remain at Continue destination');
      assert(target.querySelector('.fc-inline-scripture[href*="id=p36"]'), 'Scripture reference must remain clickable');
    }
    assert.equal(opening.querySelectorAll('.fc-mobile-scroll-cue').length, 1, page + ': duplicate invitation');
    for (const action of opening.querySelectorAll('[data-fc-mobile-label]')) {
      assert(action.getAttribute('aria-label').includes(action.textContent.trim()), page + ': accessible name must include visible action wording');
    }
    if (!w.document.body.classList.contains('fc-main-opening') && !sectionCopyPages.has(page)) {
      const restoredCopy = opening.cloneNode(true);
      restoredCopy.querySelector('.fc-mobile-scroll-cue').remove();
      assert.equal(restoredCopy.textContent.replace(/\s+/g, ' ').trim(), originalText, page + ': individual study opening must remain untouched');
      assert.equal(w.document.querySelectorAll('.fc-mobile-opening-notes, [data-fc-mobile-label]').length, 0, page + ': main-page redesign escaped its scope');
    }
    if (page === ADAMS_INTRO) {
      const timelineCues = opening.querySelectorAll('.timeline-opening-continue');
      assert.equal(timelineCues.length, 1, 'Adams must retain its one original Timeline Continue');
      assert.equal(timelineCues[0].getAttribute('href'), '#adams-overview', 'Adams original Continue must reach its overview');
      assert(timelineCues[0].classList.contains('fc-desktop-scroll-cue'), 'Adams original cue must be recognized by the mobile initializer');
      assert.equal(cue.getAttribute('href'), '#adams-overview', 'Adams generated mobile cue must preserve the same target');
    }
    openingPages.push(page);
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
assert(pages.includes('answers/holy-ghost.html'), 'New Holy Ghost opening must be included');
assert(pages.includes('answers/plan-of-salvation.html'), 'New Plan of Salvation opening must be included');
assert(pages.includes('timeline.html'), 'New Timeline opening must be included');
for(const page of ['timelines/latter-day-saint-church-history-timeline.html','timelines/willie-and-martin-handcart-map.html','timelines/life-of-christ-journey-map.html'])assert(pages.includes(page),'New timeline experience opening must be included: '+page);
assert.equal(pages.filter(page => page === ADAMS_INTRO).length, 1, 'Adams introduction must be canonical exactly once');
checkOpeningInventory(openingPages);
console.log('Opening flow and cards QA PASS: 46 historical and one Adams opening invitation; compact Joseph gateway; complete Answers rows.');
