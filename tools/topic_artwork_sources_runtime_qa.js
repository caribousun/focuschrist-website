// Exercise actual source pills and a hostile/mixed-domain caption through the UI adapter.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const dom = new JSDOM(read('joseph-smith-likeness.html'), {
    url: 'https://focuschrist.com/joseph-smith-likeness.html', runScripts: 'outside-only'
});
const { window } = dom;
const { document } = window;
window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
window.HTMLElement.prototype.scrollIntoView = function () {};
window.eval(read('hero-details.js'));
const hero = document.querySelector('a[data-hero-viewer]');
assert.equal(hero.dataset.heroRecord, 'joseph-likeness', 'Actual hero binds its named record');
hero.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
const heroPanel = document.getElementById('heroDetailDialog');
assert(heroPanel.open, 'Joseph hero opens the study panel rather than the raw image');
assert.equal(new URL(heroPanel.querySelector('[data-hero-source-link]').href).hostname,
    'churchhistorylibrary.churchofjesuschrist.org');
assert.equal(new URL(heroPanel.querySelector('[data-hero-study-link]').href).hash, '#our-portrait');
heroPanel.close();
assert.equal(document.activeElement, hero, 'Hero close restores focus');
const allowed = [
    'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/135?lang=eng&id=p3#p3',
    'https://www.josephsmithpapers.org/paper-summary/journal-december-1841-december-1842/30',
    'https://churchhistorylibrary.churchofjesuschrist.org/joseph-and-hyrum-death-masks?lang=eng'
];
const rejected = [
    'http://www.josephsmithpapers.org/paper-summary/example',
    'http://www.churchofjesuschrist.org/study/example',
    'http://churchhistorylibrary.churchofjesuschrist.org/example',
    'https://www.josephsmithpapers.org.example.com/example',
    'https://example.com/?source=www.churchofjesuschrist.org',
    'javascript:alert(1)'
];
const fixture = document.createElement('figure');
fixture.innerHTML = '<a href="assets/test.webp"><img src="assets/test.webp" alt="Test artwork"></a><figcaption><h3>Source boundary fixture</h3><p>Compare these source records.</p></figcaption>';
for (const href of [...rejected, ...allowed]) {
    const a = document.createElement('a'); a.href = href; a.textContent = href;
    fixture.querySelector('figcaption').appendChild(a);
}
const imageLink = document.createElement('a'); imageLink.href = allowed[0];
imageLink.innerHTML = '<img alt="Not a source pill">'; fixture.querySelector('figcaption').prepend(imageLink);
document.querySelector('main').appendChild(fixture);
window.eval(read('topic-artwork-details.js'));
document.dispatchEvent(new window.Event('DOMContentLoaded'));
const panel = document.getElementById('topicArtworkDetailDialog');
const click = node => node.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
let checked = 0;
for (const figure of document.querySelectorAll('figure[data-enriched-study-art^="likeness-"]')) {
    const expected = [...figure.querySelectorAll('figcaption a[href]')].map(a => a.href);
    assert(expected.length > 0, 'Each real scene supplies its historical source');
    click(figure.querySelector(':scope > a'));
    assert(panel.open, 'Real picture opens the native study panel');
    assert.deepEqual([...panel.querySelectorAll('[data-topic-art-source]')].map(a => a.href), expected,
        figure.dataset.enrichedStudyArt + ': exact historical source must survive into panel');
    panel.close(); checked++;
}
assert.equal(checked, 4);
click(fixture.querySelector(':scope > a'));
const pills = [...panel.querySelectorAll('[data-topic-art-source]')];
assert.deepEqual(pills.map(a => a.href), allowed, 'Only exact HTTPS institutional hosts become source pills');
for (const pill of pills) {
    assert.equal(pill.target, '_blank');
    assert.equal(pill.rel, 'noopener noreferrer');
}
assert(pills[0].classList.contains('fc-inline-scripture'), 'Scripture source still connects to contextual reader');
assert(!pills[1].classList.contains('fc-inline-scripture'), 'Historical journal remains an ordinary source');
dom.window.close();
console.log('Historical artwork source QA PASS: four real scene panels plus exact HTTPS host boundary, query/fragment preservation and scripture routing');
