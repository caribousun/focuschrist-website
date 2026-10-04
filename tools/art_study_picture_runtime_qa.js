// DOM contract test. Real viewport, keyboard and scripture-reader checks remain browser QA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
process.on('uncaughtException', error => {
    const detail = String(error && error.stack ? error.stack : error).replace(/\r?\n/g, '%0A');
    console.error(detail);
    console.log(`::error title=Featured art study runtime QA failure::${detail}`);
    process.exitCode = 1;
});
const ref = process.argv.find(arg => arg.startsWith('--ref='))?.slice(6);
const read = file => ref ? execFileSync('git', ['show', `${ref}:${file}`], { cwd: root, encoding: 'utf8' }) : fs.readFileSync(path.join(root, file), 'utf8');
const gallery = new JSDOM(read('art.html'), { url: 'https://focuschrist.com/art.html' });
const cards = [...gallery.window.document.querySelectorAll('a[data-artwork-detail][href^="art-study/"]')];
assert.equal(cards.length, 4, 'Audit all four Featured Art & Study cards');
const destinations = new Set();
let checked = 0;
for (const card of cards) {
    const record = gallery.window.document.querySelector(`[data-artwork-detail-content="${card.dataset.artworkDetail}"]`);
    assert(record, 'Featured card has a study detail record');
    assert.equal(record.dataset.detailStudy, card.getAttribute('href'), 'Featured card and complete-study pill reach the same page');
    const relative = card.getAttribute('href');
    assert(!destinations.has(relative), 'Featured destinations are distinct');
    destinations.add(relative);
    const dom = new JSDOM(read(relative), { url: card.href, runScripts: 'outside-only' });
    const { window } = dom;
    const { document } = window;
    window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
    window.HTMLElement.prototype.scrollIntoView = function () { this.dataset.qaScrolled = 'true'; };
    for (const asset of ['topic-artwork-details.js', 'full-image-viewer.js']) {
        assert([...document.scripts].some(script => script.src && new URL(script.src).pathname === '/' + asset), `${relative}: loads ${asset}`);
    }
    // Load actual page-order shared scripts, never inject a missing enhancer to hide a regression.
    for (const script of document.scripts) {
        const asset = script.src && new URL(script.src).pathname.slice(1);
        if (['topic-artwork-details.js', 'full-image-viewer.js'].includes(asset)) window.eval(read(asset));
    }
    document.dispatchEvent(new window.Event('DOMContentLoaded'));
    const triggers = [...document.querySelectorAll('a[data-art-study-supporting]')];
    assert.equal(triggers.length, 5, `${relative}: all five supporting pictures discovered`);
    const titles = new Set();
    const click = node => node.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
    for (const trigger of triggers) {
        const caption = trigger.closest('figure').querySelector('figcaption');
        const expectedTitle = caption.querySelector('h2,h3,strong').textContent.trim();
        const expectedSources = [...caption.querySelectorAll('a[href]')].map(a => a.href);
        assert(trigger.hasAttribute('data-topic-artwork-detail'), `${relative}: picture enhanced`);
        assert(!trigger.hasAttribute('data-full-image-viewer'), 'First activation cannot skip study options');
        assert.equal(trigger.getAttribute('aria-haspopup'), 'dialog');
        trigger.focus();
        click(trigger);
        const panel = document.getElementById('topicArtworkDetailDialog');
        const viewer = document.querySelector('.fc-full-image-viewer');
        assert(panel.open && !viewer.open, 'Image opens study panel first');
        const title = panel.querySelector('h2').textContent.trim();
        assert.equal(title, expectedTitle, 'Panel keeps image-specific title');
        assert(!titles.has(title), 'Five distinct image study titles');
        titles.add(title);
        assert.equal(panel.querySelector('img').src, trigger.href, 'Panel uses original full artwork');
        const copy = panel.querySelector('.fc-artwork-detail-copy');
        if (relative === 'art-study/the-good-shepherd.html') {
            const concise = JSON.parse(read('docs/good-shepherd-concise-copy-review-20260927.json'));
            const expected = concise.records.find(e => e.title === title);
            assert(expected);assert.equal(copy.textContent.replace(/\s+/g,' ').trim(), expected.copy, 'Owner-requested concise caption matches exact independent review');
        } else {
        assert(copy.textContent.trim().split(/\s+/).length >= 18, 'Substantive image-specific prose retained');
        }
        const expectedCopy = caption.cloneNode(true);
        expectedCopy.querySelector('h2,h3,strong').remove();
        const normalized = value => value.replace(/\s+/g, ' ').trim();
        assert.equal(normalized(copy.textContent), normalized(expectedCopy.textContent), 'Full caption prose is preserved without repeating its title');
        const pills = [...panel.querySelectorAll('[data-topic-art-source]')];
        assert.deepEqual(pills.map(a => a.href), expectedSources, 'Scripture pills preserve exact caption sources');
        for (const source of pills) {
            assert(source.classList.contains('fc-inline-scripture'), 'Scripture pill opts into contextual reader');
            assert.equal(source.target, '_blank', 'Official source remains a no-reader fallback');
            assert(copy.querySelector(`a[href="${source.getAttribute('href')}"]`), 'Inline scripture link survives caption cloning');
        }
        const full = panel.querySelector('[data-full-image-viewer]');
        const related = [...document.querySelectorAll('main #continue-study a[href]')].find(link => new URL(link.href).origin === window.location.origin && new URL(link.href).pathname !== window.location.pathname && !link.querySelector('img'));
        assert(related, 'Study page supplies an onward lesson');
        const studyPills = [...panel.querySelectorAll('.fc-artwork-detail-actions a')];
        if (trigger.dataset.topicStudy) {
            assert(studyPills.some(link => link.href === new URL(trigger.dataset.topicStudy, window.location.href).href && link.textContent === trigger.dataset.topicStudyLabel), 'Explicit contextual picture study remains available');
        } else {
            assert(!studyPills.some(link => link.href === related.href), 'Page-wide onward lesson must not be guessed as this picture destination');
        }
        assert.equal(full.textContent, 'View Full-Size Image');
        assert.equal(full.href, trigger.href);
        full.focus();
        click(full);
        assert(panel.open && viewer.open, 'Full size nests above existing study panel');
        assert.equal(viewer.querySelector('img').src, trigger.href);
        click(viewer.querySelector('button'));
        assert(!viewer.open && panel.open, 'Closing full image preserves study panel');
        assert.equal(document.activeElement, full, 'Nested viewer restores action focus');
        assert(document.body.classList.contains('fc-dialog-open'), 'Parent study scroll lock survives nested close');
        const close = [...panel.querySelectorAll('button')].find(button => button.textContent === 'Close');
        assert(close.hasAttribute('data-artwork-detail-close'), `${relative}: Close action exposes the shared artwork styling hook`);
        click(close);
        assert(!panel.open && document.activeElement === trigger, 'Close returns to invoking picture');
        click(trigger);
        const resume = panel.querySelector('[data-topic-art-continue]');
        assert.equal(resume.textContent, 'Continue Lesson');
        const target = document.getElementById(new URL(resume.href).hash.slice(1));
        assert(target && !target.closest('figure'), 'Lesson action targets surrounding study');
        click(resume);
        assert(!panel.open && document.activeElement === target && target.dataset.qaScrolled === 'true', 'Continue Lesson returns focus and scroll to reading');
        assert(!document.body.classList.contains('fc-dialog-open'), 'Study close clears scroll lock');
        click(trigger);
        assert.equal(panel.querySelectorAll('[data-topic-art-source]').length, expectedSources.length, 'Repeated opening does not duplicate pills');
        click(panel.querySelector('[data-topic-art-close]'));
        checked++;
    }
    dom.window.close();
}
// Exercise the active legacy gallery functions, not a copied viewer implementation.
const legacy = new JSDOM(read('art.html'), { url: 'https://focuschrist.com/art.html', runScripts: 'dangerously' });
const legacyWindow = legacy.window;
const legacyDocument = legacyWindow.document;
const originals = [...legacyDocument.querySelectorAll('.gallery-item')];
assert.equal(originals.length, 39, 'Every original gallery picture is covered');
const originalAssets = originals.map(item => item.querySelector('img').getAttribute('data-full-src'));
const originalTitles = originals.map(item => item.querySelector('.caption').textContent.trim());
const modalImage = legacyDocument.getElementById('modalImage');
const legacyModal = legacyDocument.getElementById('imageModal');
const closeLegacy = legacyModal.querySelector('.close');
const key = (target, value) => target.dispatchEvent(new legacyWindow.KeyboardEvent('keydown', { key: value, bubbles: true, cancelable: true }));
for (let index = 0; index < originals.length; index++) {
    const item = originals[index];
    const picture = item.querySelector('img');
    assert.equal(item.getAttribute('aria-label'), 'View ' + originalTitles[index], 'Visible title remains the gallery button name');
    assert(picture.alt.length > originalTitles[index].length, 'Original artwork has a scene description, not only its title');
    item.focus();
    key(item, index % 2 ? ' ' : 'Enter');
    assert(legacyModal.classList.contains('active'), 'Keyboard opens the real gallery');
    assert.equal(legacyDocument.activeElement, closeLegacy, 'Open puts focus on the close control');
    const visibleControls = [...legacyModal.querySelectorAll('[tabindex="0"]')];
    const lastControl = visibleControls[visibleControls.length - 1];
    closeLegacy.dispatchEvent(new legacyWindow.KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true, cancelable: true }));
    assert.equal(legacyDocument.activeElement, lastControl, 'Shift+Tab at first control stays inside the modal');
    key(lastControl, 'Tab');
    assert.equal(legacyDocument.activeElement, closeLegacy, 'Tab at last control wraps to close');
    assert.equal(modalImage.getAttribute('src'), originalAssets[index]);
    assert.equal(modalImage.alt, picture.alt, 'Selected image description follows opening');
    key(legacyDocument, 'ArrowRight');
    assert.equal(modalImage.alt, originals[(index + 1) % originals.length].querySelector('img').alt, 'Next updates description including wraparound');
    key(legacyDocument, 'ArrowLeft');
    assert.equal(modalImage.alt, picture.alt, 'Previous restores selected description');
    key(legacyDocument, 'ArrowRight');
    if (index % 3 === 0) key(legacyDocument, 'Escape');
    else if (index % 3 === 1) key(closeLegacy, 'Enter');
    else legacyModal.click();
    assert(!legacyModal.classList.contains('active'), 'Escape, close control and backdrop each close');
    assert.equal(legacyDocument.activeElement, item, 'Close returns to exact original trigger after navigation');
    assert.equal(legacyDocument.body.style.overflow, 'auto', 'Close restores page scrolling');
}
assert.deepEqual(originals.map(item => item.querySelector('img').getAttribute('data-full-src')), originalAssets);
assert.deepEqual(originals.map(item => item.querySelector('.caption').textContent.trim()), originalTitles);
// The study drawer can append controls after initial opening; include only visible ones.
legacyWindow.openModal(originals[0]);
const drawer = legacyDocument.createElement('div');
drawer.innerHTML = '<a href="#study">Study link</a><button hidden>Hidden action</button>';
legacyModal.append(drawer);
closeLegacy.dispatchEvent(new legacyWindow.KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true, cancelable: true }));
assert.equal(legacyDocument.activeElement, drawer.querySelector('a'), 'Dynamic visible drawer link participates in focus wrap; hidden controls do not');
key(drawer.querySelector('a'), 'Tab');
assert.equal(legacyDocument.activeElement, closeLegacy);
key(legacyDocument, 'Escape');
assert.equal(legacyDocument.activeElement, originals[0]);
legacyWindow.close();
gallery.window.close();
assert.equal(checked, 20);
console.log('Art study picture DOM QA passed: 4 featured paths, 20 study panels, exact titles and scripture, nested full-size viewer, repeated opening, focus and lesson return.');
console.log('Legacy gallery DOM QA passed: 39 descriptions, stable title labels/assets, next/previous/wraparound, keyboard opening and exact original-trigger return across three close paths.');
