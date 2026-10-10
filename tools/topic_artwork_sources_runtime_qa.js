// Exercise actual source pills and a hostile/mixed-domain caption through the UI adapter.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const dom = new JSDOM(read('joseph-smith-portrait-research.html'), {
    url: 'https://focuschrist.com/joseph-smith-portrait-research.html', runScripts: 'outside-only'
});
const { window } = dom;
const { document } = window;
window.TextEncoder = TextEncoder;
window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
window.HTMLElement.prototype.scrollIntoView = function () {};
// The former likeness route is now a concise bridge; actual migrated pictures are tested here.
const bridge=new JSDOM(read('joseph-smith-likeness.html')).window.document;
assert.equal(bridge.querySelectorAll('main img').length,0,'Bridge must not duplicate artwork ownership');
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
for (const figure of document.querySelectorAll('figure[data-research-art^="likeness-"]')) {
    const expected=[...figure.querySelectorAll('figcaption a[href]')].map(a=>a.href);
    click(figure.querySelector(':scope > a'));
    assert(panel.open,'Migrated real picture opens its study panel');
    assert.deepEqual([...panel.querySelectorAll('[data-topic-art-source]')].map(a=>a.href),expected,'Exact migrated source survives');
    panel.close();checked++;
}
assert.equal(checked,4,'All four migrated portrait scenes retain source panels');
click(fixture.querySelector(':scope > a'));
const pills = [...panel.querySelectorAll('[data-topic-art-source]')];
assert.deepEqual(pills.map(a => a.href), allowed, 'Only exact HTTPS institutional hosts become source pills');
for (const pill of pills) {
    assert.equal(pill.target, '_blank');
    assert.equal(pill.rel, 'noopener noreferrer');
}
assert(pills[0].classList.contains('fc-inline-scripture'), 'Scripture source still connects to contextual reader');
assert(!pills[1].classList.contains('fc-inline-scripture'), 'Historical journal remains an ordinary source');
// A browser queues close events; a fast next opening can precede the old event.
panel.close();
const scenes = [...document.querySelectorAll('figure[data-enriched-study-art^="likeness-"] > a')];
click(scenes[0]);
panel.removeAttribute('open'); // close() changes state before its queued event runs
click(scenes[1]);
const reopenedImage = panel.querySelector('.fc-artwork-detail-media img');
const reopenedSrc = reopenedImage.getAttribute('src');
const reopenedFocus = document.activeElement;
panel.dispatchEvent(new window.Event('close'));
assert(panel.open, 'Stale close event must not close the next study');
assert.equal(reopenedImage.getAttribute('src'), reopenedSrc, 'Stale close event must preserve the next image');
assert.equal(document.activeElement, reopenedFocus, 'Stale close event must preserve current dialog focus');
panel.close();
assert.equal(document.activeElement, scenes[1], 'Real next close restores its own trigger');
assert.equal(reopenedImage.getAttribute('src'), null, 'Real close still clears the image');
window.eval(read('full-image-viewer.js'));
const fullTriggers = [0, 1].map(index => {
    const a = document.createElement('a');
    a.href = 'assets/full-test-' + index + '.webp';
    a.setAttribute('data-full-image-viewer', '');
    a.dataset.fullImageAlt = 'Full test ' + index;
    a.textContent = 'View full size';
    document.body.appendChild(a);
    return a;
});
click(fullTriggers[0]);
const fullPanel = document.querySelector('dialog.fc-full-image-viewer');
fullPanel.removeAttribute('open');
click(fullTriggers[1]);
const fullImage = fullPanel.querySelector('img');
const fullSrc = fullImage.getAttribute('src');
const fullFocus = document.activeElement;
fullPanel.dispatchEvent(new window.Event('close'));
assert.equal(fullImage.getAttribute('src'), fullSrc, 'Stale full-image close preserves reopened image');
assert.equal(fullImage.alt, 'Full test 1', 'Stale full-image close preserves alternative text');
assert.equal(document.activeElement, fullFocus, 'Stale full-image close preserves dialog focus');
assert(document.body.classList.contains('fc-full-image-open'), 'Reopened full-image scroll lock remains');
fullPanel.close();
assert.equal(document.activeElement, fullTriggers[1], 'Actual full-image close returns to current trigger');
assert.equal(fullImage.getAttribute('src'), null, 'Actual full-image close clears its image');
dom.window.close();
console.log('Historical artwork source QA PASS: four real scene panels plus exact HTTPS host boundary, query/fragment preservation and scripture routing');

// The bridge follows only its explicit legacy anchors; no-JS links remain in markup.
const vm=require('node:vm');
const bridgeScript=read('joseph-study-bridge.js');
const bridgeRoutes=JSON.parse(bridgeScript.match(/const routes=(\{.*?\});/)[1]);
for(const [id,target] of Object.entries(bridgeRoutes)){
 let destination=null;const context={URL,location:{hash:'#'+id,href:'https://focuschrist.com/joseph-smith-likeness.html#'+id,replace:url=>destination=url},window:{addEventListener(){}}};
 vm.runInNewContext(bridgeScript,context);assert.equal(destination,new URL(target,context.location.href).href);
 assert(bridge.querySelector('#'+id+' a[href="'+target+'"]'),'No-JS legacy link agrees with runtime destination');
}
for(const hash of ['','#unknown','#https://evil.example','#%E0%A4%A','#constructor','#__proto__']){
 let destination=null;vm.runInNewContext(bridgeScript,{URL,location:{hash,href:'https://focuschrist.com/joseph-smith-likeness.html'+hash,replace:url=>destination=url},window:{addEventListener(){}}});assert.equal(destination,null,'Unknown or malformed hashes cannot redirect');
}
console.log('PASS exact legacy bridge redirects, matching no-JS links and unknown/malformed/prototype negatives.');
