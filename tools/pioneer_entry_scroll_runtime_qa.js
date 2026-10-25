const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

// Scenario A: addMessage in pioneers.html brings the top of each newly
// appended conversation entry into view at the append choke point,
// instead of forcing the transcript to its absolute top
// (c.scrollTop = 0) on every append.
const pioneersHtml = fs.readFileSync(path.join(__dirname, '../pioneers.html'), 'utf8');
assert(!pioneersHtml.includes('c.scrollTop=0'), 'the transcript top-force line must be gone from pioneers.html');
assert.equal(pioneersHtml.split('bringEntryIntoView(').length - 1, 2, 'the helper is defined once and called once in pioneers.html');
const sliceStartA = pioneersHtml.indexOf('    function bringEntryIntoView(');
const sliceEndA = pioneersHtml.indexOf('    async function sendMessage()');
assert(sliceStartA >= 0 && sliceEndA > sliceStartA, 'the entry scroll helper and addMessage must be present in pioneers.html');
const viewedA = [];
const scrollTopSetsA = [];
function nodeA() {
    return { className: '', innerHTML: '', scrollIntoView(options) { viewedA.push({ node: this, options }); } };
}
const boxA = { children: [], appendChild(node) { this.children.push(node); return node; } };
Object.defineProperty(boxA, 'scrollTop', { get() { return 0; }, set(value) { scrollTopSetsA.push(value); } });
const documentA = {
    getElementById(id) { return id === 'chatBox' ? boxA : null; },
    createElement() { return nodeA(); },
};
const contextA = vm.createContext({ document: documentA, console });
vm.runInContext(pioneersHtml.slice(sliceStartA, sliceEndA), contextA);
assert.equal(viewedA.length, 0, 'no scrolling happens on script load');
vm.runInContext("addMessage('Who were the Mormon pioneers?', true, [])", contextA);
vm.runInContext("addMessage('The pioneers gathered to Zion.', false, [])", contextA);
assert.equal(boxA.children.length, 2, 'both conversation entries are appended');
assert.equal(viewedA.length, 2, 'every appended entry is brought into view');
assert.equal(viewedA[0].node, boxA.children[0], 'the user entry is scrolled into view on its append');
assert.equal(viewedA[1].node, boxA.children[1], 'the answer entry is scrolled into view on its append');
assert.equal(viewedA[1].options.block, 'start', 'the entry top is the alignment target');
assert.equal(viewedA[1].options.behavior, 'auto', 'the entry anchor is immediate, not animated');
assert.equal(scrollTopSetsA.length, 0, 'an append no longer forces the transcript scroll position');

// Scenario B: the live append path, window.addMessage in
// pioneer-experience.js, anchors the message it just appended, so the
// appends that never call positionAnswer (choice lists, story and
// error messages) still land on their own entry, and the helper
// guards null and scroll-less entries without throwing.
const code = fs.readFileSync(path.join(__dirname, '../pioneer-experience.js'), 'utf8');
assert.equal(code.split('bringPioneerEntryIntoView(').length - 1, 2, 'the helper is defined once and called once in pioneer-experience.js');
assert(code.includes('function positionAnswer('), 'the exchange-level positionAnswer refinement is unchanged');
const sliceStartB = code.indexOf('    function bringPioneerEntryIntoView(');
const sliceEndB = code.indexOf('    function recentHistory()');
assert(sliceStartB >= 0 && sliceEndB > sliceStartB, 'the pioneer entry scroll helper and addMessage must be present in pioneer-experience.js');
const viewedB = [];
function elementB() {
    return {
        className: '', children: [], textContent: '',
        appendChild(child) { this.children.push(child); return child; },
        setAttribute() {},
        scrollIntoView(options) { viewedB.push({ node: this, options }); },
    };
}
const boxB = { children: [], appendChild(node) { this.children.push(node); return node; } };
const windowB = {};
const documentB = {
    createElement() { return elementB(); },
    createTextNode(text) { return { text }; },
};
const contextB = vm.createContext({
    window: windowB,
    document: documentB,
    console,
    chatBox() { return boxB; },
    appendTextParagraph(parent, text) { const p = elementB(); p.textContent = text; parent.appendChild(p); },
});
vm.runInContext(code.slice(sliceStartB, sliceEndB), contextB);
assert.equal(typeof windowB.addMessage, 'function', 'window.addMessage must be defined by the pioneer-experience.js slice');
assert.equal(viewedB.length, 0, 'no scrolling happens on script load');
const userEntry = windowB.addMessage('Who was Brigham Young?', true);
const answerEntry = windowB.addMessage('Brigham Young led the vanguard company west in 1847.', false, []);
assert.equal(boxB.children.length, 2, 'both conversation entries are appended');
assert.equal(userEntry, boxB.children[0], 'addMessage still returns the appended user entry');
assert.equal(answerEntry, boxB.children[1], 'addMessage still returns the appended answer entry');
assert.equal(viewedB.length, 2, 'every appended entry is brought into view');
assert.equal(viewedB[0].node, userEntry, 'the user entry is scrolled into view on its append');
assert.equal(viewedB[1].node, answerEntry, 'the answer entry is scrolled into view on its append');
assert.equal(viewedB[1].options.block, 'start', 'the entry top is the alignment target');
vm.runInContext('bringPioneerEntryIntoView(null)', contextB);
vm.runInContext('bringPioneerEntryIntoView({})', contextB);
assert.equal(viewedB.length, 2, 'the helper ignores null and scroll-less entries');
console.log('PASS: Pioneer appended entries are brought into view at append time on both addMessage implementations, with no forced transcript scroll and no scroll on load.');
