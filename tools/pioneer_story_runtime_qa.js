/* Real DOM checks for compact Pioneer navigation; no provider/network calls. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const dom = new JSDOM(`<a id="jump" href="#destination">Read</a><a id="external" href="https://example.com/#destination">Other</a><details id="outer" class="pioneer-timeline-group"><summary>Journey</summary><details id="inner"><summary>More</summary><p id="destination">History</p></details><div data-focus-expand="timeline" data-topic="exodus"><a id="owned" href="#destination">Existing control</a><div class="ai-response">Saved answer</div></div></details>`, { url: 'https://focuschrist.com/pioneers.html#destination', runScripts: 'outside-only' });
const { window } = dom;
const d = window.document;
const frames = [];
window.requestAnimationFrame = fn => frames.push(fn);
let scrolled = null;
window.HTMLElement.prototype.scrollIntoView = function () { scrolled = this.id; };
window.eval(fs.readFileSync(path.join(__dirname, '..', 'pioneer-story.js'), 'utf8'));
d.dispatchEvent(new window.Event('DOMContentLoaded'));
while (frames.length) frames.shift()();
assert(d.getElementById('outer').open && d.getElementById('inner').open, 'Initial fragment opens every closed ancestor');
assert.equal(scrolled, 'destination');
function close() { d.getElementById('outer').open = false; d.getElementById('inner').open = false; scrolled = null; }
function click(id, options = {}) { const event = new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0, ...options }); d.getElementById(id).dispatchEvent(event); return event; }
close();
window.dispatchEvent(new window.HashChangeEvent('hashchange'));
assert(d.getElementById('inner').open, 'Back/forward hash change reveals nested target');
close();
const jump = click('jump');
assert(!jump.defaultPrevented, 'Fragment navigation retains browser history/default behavior');
assert(d.getElementById('outer').open, 'Repeated same-hash click reopens closed group');
close(); click('external'); assert(!d.getElementById('outer').open, 'External destination untouched');
click('jump', { ctrlKey: true }); assert(!d.getElementById('outer').open, 'Modified click untouched');
click('owned'); assert(!d.getElementById('inner').open, 'Existing disclosure controls never intercepted');
assert.equal(d.querySelector('.ai-response').textContent, 'Saved answer', 'Existing saved answer retained');
window.history.replaceState({}, '', '#%E0%A4%A');
assert.doesNotThrow(() => window.dispatchEvent(new window.HashChangeEvent('hashchange')), 'Malformed fragment is harmless');
window.history.replaceState({}, '', '#missing');
assert.doesNotThrow(() => window.dispatchEvent(new window.HashChangeEvent('hashchange')), 'Missing destination is harmless');
dom.window.close();
// Exercise the actual shared detail controller and authored Pioneer source links together.
const root = path.join(__dirname, '..');
// CSS geometry is browser QA; jsdom cannot parse the page's legacy inline stylesheet.
const authoredMarkup = fs.readFileSync(path.join(root, 'pioneers.html'), 'utf8').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '');
const artDOM = new JSDOM(authoredMarkup, { url: 'https://focuschrist.com/pioneers.html?gallery-position=test', runScripts: 'outside-only' });
const aw = artDOM.window;
const ad = aw.document;
const artFrames = [];
aw.requestAnimationFrame = fn => artFrames.push(fn);
aw.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
aw.HTMLDialogElement.prototype.close = function () { this.open = false; this.dispatchEvent(new aw.Event('close')); };
let returnedTo = null;
aw.HTMLElement.prototype.scrollIntoView = function () { returnedTo = this.id; };
aw.eval(fs.readFileSync(path.join(root, 'artwork-details.js'), 'utf8'));
aw.eval(fs.readFileSync(path.join(root, 'pioneer-story.js'), 'utf8'));
const artTrigger = ad.querySelector('[data-artwork-detail^="pioneer-story-"]');
assert(artTrigger, 'Published page contains new story artwork');
function artClick(element) { element.dispatchEvent(new aw.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 })); }
artClick(artTrigger);
const artDialog = ad.getElementById('artworkDetailDialog');
assert(artDialog.open, 'Shared artwork controller opens normally');
const expectedSources = [...artTrigger.closest('.pioneer-story-card').querySelectorAll('.pioneer-source-links a')].filter(a => a.href !== ad.getElementById('artworkDetailSource').href).map(a => [a.textContent, a.href]);
assert.deepEqual([...ad.querySelectorAll('#artworkDetailCopy [data-pioneer-story-sources] a')].map(a => [a.textContent, a.href]), expectedSources, 'Secondary sources survive without duplicating primary source');
const expectedScriptures = [
    'https://www.churchofjesuschrist.org/study/scriptures/nt/matt/25?lang=eng&id=p35-p40#p35',
    'https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah/18?lang=eng&id=p8-p9#p8'
];
for (const storyTrigger of ad.querySelectorAll('[data-artwork-detail^="pioneer-story-"]')) {
    artDialog.close();
    artClick(storyTrigger);
    const scriptureLinks = [...ad.querySelectorAll('#artworkDetailCopy [data-pioneer-scripture-links] a')];
    const urls = scriptureLinks.map(a => a.href);
    for (const url of expectedScriptures) assert(urls.includes(url), 'Every new story has both exact reflection scripture ranges');
    for (const originalLink of storyTrigger.closest('.pioneer-story-card').querySelectorAll('.pioneer-story-copy a[href*="/study/scriptures/"]')) {
        assert(scriptureLinks.some(a => a.href === originalLink.href), 'Story-specific scripture link retained in panel');
    }
    assert.equal(urls.length, new Set(urls).size, 'Scripture destinations are not repeated');
    const reflection = ad.querySelector('#artworkDetailCopy [data-pioneer-scripture-links]');
    const sources = ad.querySelector('#artworkDetailCopy [data-pioneer-story-sources]');
    const primaryURL = ad.getElementById('artworkDetailSource').href;
    const expectedSecondary = [...storyTrigger.closest('.pioneer-story-card').querySelectorAll('.pioneer-source-links a')].filter(a => a.href !== primaryURL).map(a => a.href);
    assert.deepEqual(sources ? [...sources.querySelectorAll('a')].map(a => a.href) : [], expectedSecondary, 'Secondary source parity excludes primary destination');
    if (sources) assert(reflection.compareDocumentPosition(sources) & aw.Node.DOCUMENT_POSITION_FOLLOWING, 'Reflection appears before historical source links');
    else assert.equal(expectedSecondary.length, 0, 'No empty secondary source group');
}
artDialog.close();
artClick(artTrigger);
assert.equal(ad.querySelectorAll('#artworkDetailCopy [data-pioneer-story-sources]').length, expectedSources.length ? 1 : 0, 'Reopening does not duplicate source groups');
artClick(ad.getElementById('artworkDetailStudy'));
assert(!artDialog.open, 'Return to this story closes detail dialog');
while (artFrames.length) artFrames.shift()();
assert.equal(returnedTo, artTrigger.dataset.artworkDetail, 'Story is scrolled into view after shared focus restoration');
assert.equal(ad.activeElement, artTrigger, 'Shared trigger focus restoration is preserved');
assert.equal(aw.location.search, '?gallery-position=test', 'Gallery query is preserved');
assert.equal(aw.location.hash, '#' + artTrigger.dataset.artworkDetail, 'Return updates story fragment');
const oldTrigger = ad.querySelector('[data-artwork-detail="pioneer-leaving-nauvoo"]');
artClick(oldTrigger);
assert.equal(ad.querySelectorAll('#artworkDetailCopy [data-pioneer-story-sources]').length, 0, 'Existing artwork never inherits new story sources');
artDOM.window.close();
console.log('PIONEER STORY RUNTIME PASS: fragment ancestors, controller isolation, complete source links, close/return, focus and gallery query.');
