const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const dom = new JSDOM(read('jesus-christ/parables/hearing.html'), {
    url: 'https://focuschrist.com/jesus-christ/parables/hearing.html', runScripts: 'outside-only'
});
const { window } = dom;
const { document } = window;
window.HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
window.HTMLDialogElement.prototype.close = function () { this.removeAttribute('open'); this.dispatchEvent(new window.Event('close')); };
window.HTMLElement.prototype.scrollIntoView = function () {};
window.eval(read('topic-artwork-details.js'));
document.dispatchEvent(new window.Event('DOMContentLoaded'));
const related = document.querySelector('#continue-study a[href]');
const title = related.querySelector('h3').textContent.trim();
const description = related.querySelector('p').textContent.trim();
const trigger = document.querySelector('[data-topic-artwork-detail]');
const panel = document.getElementById('topicArtworkDetailDialog');
const click = node => node.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0 }));
function openAndCheck(expected) {
    trigger.focus();
    click(trigger);
    assert(panel.open);
    const onward = [...panel.querySelectorAll('.fc-artwork-detail-actions a')].find(a => a.href === related.href);
    assert(onward, 'Onward destination is retained');
    assert.equal(onward.textContent, expected, 'Onward pill uses only the semantic title or plain-link fallback');
    assert(!onward.textContent.includes(description), 'Long card description must not enter the pill');
    assert(!onward.textContent.includes('Continue this study'), 'Card action copy must not enter the pill');
    const sources = panel.querySelectorAll('[data-topic-art-source]');
    assert(sources.length > 0, 'Actual artwork exposes source pills');
    for (const source of sources) {
        const original = [...trigger.closest('figure').querySelectorAll('figcaption a[href]')].find(a => a.href === source.href);
        assert(original, 'Exact source destination remains');
        assert.equal(source.textContent, original.textContent.trim(), 'External source label remains unchanged');
        assert.equal(source.target, '_blank');
    }
    panel.close();
    assert.equal(document.activeElement, trigger, 'Close restores invoking picture focus');
}
openAndCheck(title);
related.textContent = 'Continue another lesson';
openAndCheck('Continue another lesson');
related.innerHTML = '<h3> </h3>Fallback lesson';
openAndCheck('Fallback lesson');
related.textContent = '';
openAndCheck('Continue related study');
dom.window.close();
console.log('Onward artwork label QA PASS: real nested card, source labels, plain/empty fallback and focus return');
