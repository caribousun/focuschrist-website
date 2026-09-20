/* JSDOM interaction regression gate. Real desktop/phone framing remains browser QA. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const manifest = JSON.parse(read('docs/sitewide-artwork-review.json'));
assert.equal(manifest.heroes.length, 19, 'All nineteen replacement heroes require runtime verification');
const focusedHeroes = JSON.parse(read('docs/focused-answers-art-review.json')).images.filter(record => record.role === 'hero').map(record => {
    const aaronic = record.id === 'aaronic-hero', key = record.id.replace(/-hero$/, '');
    const chapter = aaronic ? '13' : '128', title = aaronic ? 'Prepare to serve at the sacrament table' : 'A blessing offered with care';
    const ask = new URL('/ask.html', 'https://focuschrist.com');
    ask.searchParams.set('topic', (aaronic ? 'Aaronic' : 'Melchizedek') + ' Priesthood');
    ask.searchParams.set('return', '/' + record.page + '?hero=1');
    return {...record, key, title, source: 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/' + chapter + '?lang=eng', sourceLabel: 'Read Doctrine and Covenants ' + chapter, study: record.page + '#begin-study', ask: ask.href};
});
assert.deepEqual(new Set(focusedHeroes.map(record => record.key)), new Set(['aaronic', 'melchizedek']), 'Both new focused heroes require runtime verification');
const runtimeHeroes = [...manifest.heroes, ...focusedHeroes];
const canonical = [...read('sitemap.xml').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => new URL(m[1]).pathname);
assert.equal(canonical.length, 42, 'Discover the complete canonical inventory');
const click = (window, node) => node.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
let checks = 0;
for (const record of runtimeHeroes) {
    assert(canonical.includes('/' + record.page), `${record.key}: canonical destination`);
    // Run at two viewport settings to catch viewport-dependent script branches; JSDOM does not render CSS.
    for (const width of [1440, 390]) {
        const dom = new JSDOM(read(record.page), { url: 'https://focuschrist.com/' + record.page, runScripts: 'outside-only', pretendToBeVisual: true });
        const { window } = dom, { document } = window;
        Object.defineProperty(window, 'innerWidth', { value: width });
        window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
        window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
        window.HTMLElement.prototype.scrollIntoView = function () {};
        const scripts = [...document.scripts];
        for (const expected of ['hero-details.js', 'full-image-viewer.js']) assert(scripts.some(s => s.src && new URL(s.src).pathname === '/' + expected), `${record.key}: missing ${expected}`);
        for (const script of scripts) {
            const name = script.src && new URL(script.src).pathname.slice(1);
            if (!['hero-details.js', 'full-image-viewer.js'].includes(name)) continue;
            Object.defineProperty(document, 'currentScript', { configurable: true, value: script });
            window.eval(read(name));
        }
        Object.defineProperty(document, 'currentScript', { configurable: true, value: null });
        document.dispatchEvent(new window.Event('DOMContentLoaded'));
        const trigger = document.querySelector('a[data-hero-viewer]');
        assert(trigger, `${record.key}: hero exists`);
        assert.equal(trigger.dataset.heroRecord, 'topic-' + record.key);
        const fullUrl = new URL('/' + record.asset, window.location.href).href;
        assert.equal(trigger.href, fullUrl);
        trigger.focus(); click(window, trigger);
        const detail = document.getElementById('heroDetailDialog');
        const viewer = document.querySelector('.fc-full-image-viewer');
        assert(detail.open && !viewer.open, `${record.key}: detail must open before full image`);
        assert.equal(detail.querySelector('h2').textContent, record.title);
        assert.equal(detail.querySelector('img').src, fullUrl);
        assert(detail.querySelector('.fc-artwork-detail-copy').textContent.trim().split(/\s+/).length >= 25, `${record.key}: substantive reflection`);
        assert.equal(detail.querySelector('[data-hero-source-link]').href, record.source, `${record.key}: exact source`);
        assert.equal(detail.querySelector('[data-hero-source-link]').textContent, record.sourceLabel);
        const study = detail.querySelector('[data-hero-study-link]');
        assert.equal(study.href, new URL(record.study, 'https://focuschrist.com/').href, `${record.key}: own study route`);
        assert.equal(new URL(study.href).pathname, window.location.pathname);
        assert(document.getElementById(new URL(study.href).hash.slice(1)), `${record.key}: real study anchor`);
        const ask = new URL(detail.querySelector('[data-hero-ask-link]').href);
        const expectedAsk = new URL(record.ask, 'https://focuschrist.com/');
        assert.equal(ask.pathname, '/ask.html'); assert.equal(ask.hash, '#ask-question');
        assert.equal(ask.searchParams.get('topic'), expectedAsk.searchParams.get('topic'));
        assert.equal(ask.searchParams.get('return'), expectedAsk.searchParams.get('return'));
        assert.equal(ask.searchParams.get('art'), record.title);
        const full = detail.querySelector('[data-full-image-viewer]');
        assert.equal(full.href, fullUrl); full.focus(); click(window, full);
        assert(viewer.open && detail.open, `${record.key}: nested full image preserves study panel`);
        assert.equal(viewer.querySelector('img').src, fullUrl);
        click(window, viewer.querySelector('button'));
        assert(!viewer.open && detail.open, `${record.key}: full-image close returns to study panel`);
        assert.equal(document.activeElement, full, `${record.key}: nested focus restored`);
        click(window, detail.querySelector('[data-hero-close]'));
        assert(!detail.open); assert.equal(document.activeElement, trigger, `${record.key}: hero focus restored`);
        click(window, trigger); assert(detail.open, `${record.key}: reopen works`);
        detail.close(); assert(!document.body.classList.contains('fc-dialog-open'));
        dom.window.close(); checks++;
    }
}
console.log(`PASS ${checks} hero interaction contexts across ${runtimeHeroes.length} destinations. CSS framing, keyboard native activation and actual phone rendering require browser verification.`);
