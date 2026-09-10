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
    assert.equal(triggers.length, 4, `${relative}: all four supporting pictures discovered`);
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
        assert(!titles.has(title), 'Four distinct image study titles');
        titles.add(title);
        assert.equal(panel.querySelector('img').src, trigger.href, 'Panel uses original full artwork');
        const copy = panel.querySelector('.fc-artwork-detail-copy');
        assert(copy.textContent.trim().split(/\s+/).length >= 18, 'Substantive image-specific prose retained');
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
        assert([...panel.querySelectorAll('.fc-artwork-detail-actions a')].some(link => link.href === related.href && link.textContent.trim() === related.textContent.trim()), 'Panel keeps the correct onward study pill');
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
gallery.window.close();
assert.equal(checked, 16);
console.log('Art study picture DOM QA passed: 4 featured paths, 16 study panels, exact titles and scripture, nested full-size viewer, repeated opening, focus and lesson return.');
