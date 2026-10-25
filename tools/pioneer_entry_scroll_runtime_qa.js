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
        className: '', children: [], textContent: '', parentElement: null,
        appendChild(child) { child.parentElement = this; this.children.push(child); return child; },
        setAttribute() {},
        scrollIntoView(options) { viewedB.push({ node: this, options }); },
    };
}
const boxB = {
    children: [],
    appendChild(node) { node.parentElement = this; this.children.push(node); return node; },
    querySelector() { return null; },
};
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

// Scenario C: the composed composer path. The real helper +
// addMessage and the real promoteLatestExchangeToTop +
// positionAnswer + answer-ready listener run together against a
// geometry model of the panel, driven through a simulation of
// site-common's scripture display gate (placeholder append, caller
// positioning, late real append, child transplant, answer-ready
// dispatch). This is the composition the isolation scenarios above
// cannot see: the gate appends the real answer AFTER the caller
// has positioned the placeholder, so an append-time scroll on the
// real append lands after positioning and wins.
const CLIENT_H = 558;
const BOX_TOP = 260;
const FIRST_OFFSET = 25;
const sivCallsC = [];
function matchesC(el, selector) {
    if (selector.startsWith('.')) return el.classList.contains(selector.slice(1));
    if (selector === '[data-scripture-pending]') return el.getAttribute('data-scripture-pending') === 'true';
    return false;
}
class ElC {
    constructor(tag) {
        this.tagName = tag;
        this.className = '';
        this.children = [];
        this.parentElement = null;
        this.attributes = {};
        this._text = '';
    }
    get classList() {
        const self = this;
        return { contains(name) { return self.className.split(/\s+/).filter(Boolean).includes(name); } };
    }
    get firstElementChild() { return this.children[0] || null; }
    get previousElementSibling() {
        if (!this.parentElement) return null;
        const siblings = this.parentElement.children;
        const index = siblings.indexOf(this);
        return index > 0 ? siblings[index - 1] : null;
    }
    get nextSibling() { return this.nextElementSibling; }
    get nextElementSibling() {
        if (!this.parentElement) return null;
        const siblings = this.parentElement.children;
        const index = siblings.indexOf(this);
        return index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : null;
    }
    get isConnected() {
        let node = this;
        while (node) { if (node === boxC) return true; node = node.parentElement; }
        return false;
    }
    get textContent() { return this._text + this.children.map((child) => child.textContent).join(''); }
    set textContent(value) { this._text = String(value); this.children = []; }
    get height() { return 24 + Math.ceil(this.textContent.length / 38) * 20; }
    appendChild(child) {
        if (child.parentElement) child.remove();
        child.parentElement = this;
        this.children.push(child);
        return child;
    }
    insertBefore(node, reference) {
        if (node.parentElement) node.remove();
        node.parentElement = this;
        if (reference == null) { this.children.push(node); return node; }
        const index = this.children.indexOf(reference);
        if (index < 0) this.children.push(node); else this.children.splice(index, 0, node);
        return node;
    }
    remove() {
        if (!this.parentElement) return;
        const siblings = this.parentElement.children;
        const index = siblings.indexOf(this);
        if (index >= 0) siblings.splice(index, 1);
        this.parentElement = null;
    }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return name in this.attributes ? this.attributes[name] : null; }
    removeAttribute(name) { delete this.attributes[name]; }
    addEventListener() {}
    querySelectorAll(selector) {
        const found = [];
        const walk = (el) => { for (const child of el.children) { if (matchesC(child, selector)) found.push(child); walk(child); } };
        walk(this);
        return found;
    }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
    compareDocumentPosition(other) {
        if (other === this) return 0;
        if (!this.parentElement || this.parentElement !== other.parentElement) return 1;
        const siblings = this.parentElement.children;
        return siblings.indexOf(other) > siblings.indexOf(this) ? 4 : 2;
    }
    offsetInContent() {
        if (!this.parentElement) return 0;
        let offset = FIRST_OFFSET;
        for (const sibling of this.parentElement.children) {
            if (sibling === this) break;
            offset += sibling.height;
        }
        return offset;
    }
    getBoundingClientRect() {
        if (this === boxC) return { top: BOX_TOP, bottom: BOX_TOP + CLIENT_H, height: CLIENT_H };
        const top = BOX_TOP + this.offsetInContent() - boxC.scrollTop;
        return { top, bottom: top + this.height, height: this.height };
    }
    scrollIntoView(options) {
        sivCallsC.push({ node: this, options });
        if (this.parentElement === boxC) {
            const maxScroll = Math.max(0, boxC.scrollHeight - CLIENT_H);
            boxC.scrollTop = Math.min(Math.max(this.offsetInContent(), 0), maxScroll);
        }
    }
    dispatchEvent(event) {
        event.target = this;
        for (const listener of (docListenersC[event.type] || [])) listener(event);
        return true;
    }
}
const boxC = new ElC('div');
boxC.scrollTop = 0;
Object.defineProperty(boxC, 'scrollHeight', {
    get() { return FIRST_OFFSET + this.children.reduce((sum, child) => sum + child.height, 0) + 7; },
});
Object.defineProperty(boxC, 'clientHeight', { get() { return CLIENT_H; } });
boxC.scrollTo = function (options) { this.scrollTop = options.top; };
const docListenersC = {};
const documentC = {
    createElement(tag) { return new ElC(tag); },
    createTextNode(text) { const node = new ElC('#text'); node._text = String(text); return node; },
    addEventListener(type, listener) { (docListenersC[type] = docListenersC[type] || []).push(listener); },
    querySelector() { return null; },
    getElementById() { return null; },
};
const timersC = [];
const windowC = {
    innerHeight: 844,
    scrollY: 0,
    setTimeout(fn) { timersC.push(fn); return timersC.length; },
    scrollTo() {},
    addEventListener() {},
    location: { href: 'https://focuschrist.com/pioneers.html' },
};
const contextC = vm.createContext({
    window: windowC,
    document: documentC,
    console,
    chatBox() { return boxC; },
    appendTextParagraph(parent, text) { const p = new ElC('p'); p._text = text; parent.appendChild(p); },
    focusPioneerInput() {},
});
const posSliceStart = code.indexOf('    function promoteLatestExchangeToTop(');
const posSliceEnd = code.indexOf('    function pioneerRecordContext(');
assert(posSliceStart > sliceEndB && posSliceEnd > posSliceStart, 'the promote/positionAnswer slice must be present in pioneer-experience.js');
vm.runInContext(code.slice(sliceStartB, sliceEndB), contextC);
vm.runInContext(code.slice(posSliceStart, posSliceEnd), contextC);
vm.runInContext('window.__positionAnswer = positionAnswer;', contextC);
const positionAnswerC = windowC.__positionAnswer;
assert.equal(typeof windowC.addMessage, 'function', 'composed context must expose window.addMessage');
assert.equal(typeof positionAnswerC, 'function', 'composed context must expose positionAnswer');
assert.equal(sivCallsC.length, 0, 'no scrolling happens on script load in the composed context');
assert.equal(boxC.scrollTop, 0, 'the panel starts unscrolled');

// A simulation of site-common's scripture display gate wrapper
// (installScriptureDisplayGate): user messages delegate at once;
// a bot answer appends a pending placeholder synchronously, the
// caller positions it, and the gate later calls the real
// addMessage, transplants the rendered children into the
// placeholder, and dispatches focuschrist:answer-ready on it.
const gateQueueC = [];
function gatedAddMessageC(text, isUser, sources) {
    if (isUser) return windowC.addMessage(text, true, sources || [], null);
    const pending = new ElC('div');
    pending.className = 'message bot-message';
    pending.textContent = 'Checking scripture sources…';
    pending.setAttribute('role', 'status');
    pending.setAttribute('data-scripture-pending', 'true');
    boxC.appendChild(pending);
    gateQueueC.push(() => {
        if (!pending.isConnected) return;
        const rendered = windowC.addMessage(text, false, sources || [], null);
        if (rendered && rendered !== pending) {
            for (const child of rendered.children.slice()) pending.appendChild(child);
            pending._text = rendered._text;
            rendered.remove();
        }
        pending.removeAttribute('role');
        pending.removeAttribute('data-scripture-pending');
        pending.dispatchEvent({ type: 'focuschrist:answer-ready', bubbles: true });
    });
    return pending;
}
function flushGateC() { while (gateQueueC.length) gateQueueC.shift()(); }
function flushTimersC() { while (timersC.length) timersC.shift()(); }
function topMinusBoxTopC(el) { return Math.round(el.getBoundingClientRect().top - boxC.getBoundingClientRect().top); }

const HANDCART_ANSWER = 'From 1856 through 1860, ten handcart companies crossed the plains. '.repeat(64);
const BRIGHAM_ANSWER = 'Brigham Young was born in Vermont in 1801 and led the vanguard company west. '.repeat(52);

// Case C2 (topic-button append on a fresh transcript): the caller
// positions the placeholder; the gate's late append must not move
// the panel away from the positioned exchange.
const topicUser = gatedAddMessageC('Handcart Companies', true);
const topicAnswer = gatedAddMessageC(HANDCART_ANSWER, false);
positionAnswerC(topicAnswer);
flushGateC();
flushTimersC();
assert.equal(boxC.scrollTop, 13, 'topic exchange ends at the positioned scroll offset');
assert.equal(boxC.children[0], topicUser, 'the topic question is promoted to the top of the transcript');
assert.equal(topMinusBoxTopC(topicUser), 12, 'the topic question sits just below the panel top');
assert.equal(boxC.children[1], topicAnswer, 'the topic answer follows its question');
console.log('PASS: composed topic-button append stays anchored after the display-gate transplant.');

// Case C1 (typed composer path, second question): sendMessage
// clears the latest-first marker, appends the question, and
// positions the placeholder; the gate's late real append must not
// drag the panel to the bottom of the transcript, and the
// answer-ready listener stays suppressed because an earlier
// exchange follows the promoted one.
boxC.removeAttribute('data-focuschrist-latest-first');
const composerUser = gatedAddMessageC('Who was Brigham Young?', true);
const composerAnswer = gatedAddMessageC(BRIGHAM_ANSWER, false);
positionAnswerC(composerAnswer);
flushGateC();
flushTimersC();
assert.equal(boxC.scrollTop, 13, 'composer exchange ends at the positioned scroll offset, not dragged to the late append');
assert.equal(boxC.children[0], composerUser, 'the newest question is promoted to the top of the transcript');
assert.equal(boxC.children[1], composerAnswer, 'the newest answer follows its question');
assert.equal(topMinusBoxTopC(composerUser), 12, 'the newest question sits just below the panel top');
assert.equal(topMinusBoxTopC(composerAnswer), 12 + composerUser.height, 'the beginning of the newest answer is visible with its question');
assert.equal(boxC.children[2], topicUser, 'the earlier exchange follows the promoted one');
console.log('PASS: composed typed composer path anchors the promoted exchange after a first exchange.');

// Case C3 (error append, no caller positioning): the gate
// placeholder is positioned by the answer-ready listener, exactly
// as the live watch observed for the askTellMyStory error path;
// the appended entry ends fully in view.
const errorEntry = gatedAddMessageC('I could not load the pioneer index just now. Please try again.', false);
flushGateC();
flushTimersC();
assert.equal(boxC.children[boxC.children.length - 1], errorEntry, 'the error entry stays in the transcript');
const errorTop = topMinusBoxTopC(errorEntry);
assert(errorTop >= 0 && errorTop < CLIENT_H, 'the error entry lands inside the visible panel');
assert(errorTop + errorEntry.height <= CLIENT_H, 'the error entry is fully in view');
console.log('PASS: composed error append with no caller positioning ends fully in view.');
console.log('PASS: Pioneer composed scroll behavior across the display gate (topic, typed composer, error append).');

// Scenario B2: while the scripture display gate has a
// [data-scripture-pending] placeholder in the box, an append through
// window.addMessage must NOT scroll: that append is the gate's real
// answer, whose content is transplanted into the placeholder the
// caller positions. Once no placeholder is pending, appends anchor
// at append time again.
const viewedB2 = [];
function elementB2() {
    return {
        className: '', children: [], textContent: '', parentElement: null, attributes: {},
        appendChild(child) { child.parentElement = this; this.children.push(child); return child; },
        setAttribute(name, value) { this.attributes[name] = String(value); },
        getAttribute(name) { return name in this.attributes ? this.attributes[name] : null; },
        scrollIntoView(options) { viewedB2.push({ node: this, options }); },
    };
}
const boxB2 = {
    children: [],
    appendChild(node) { node.parentElement = this; this.children.push(node); return node; },
    querySelector(selector) {
        if (selector !== '[data-scripture-pending]') return null;
        return this.children.find((child) => typeof child.getAttribute === 'function'
            && child.getAttribute('data-scripture-pending') === 'true') || null;
    },
};
const windowB2 = {};
const contextB2 = vm.createContext({
    window: windowB2,
    document: { createElement() { return elementB2(); }, createTextNode(text) { return { text }; } },
    console,
    chatBox() { return boxB2; },
    appendTextParagraph(parent, text) { const p = elementB2(); p.textContent = text; parent.appendChild(p); },
});
vm.runInContext(code.slice(sliceStartB, sliceEndB), contextB2);
const pendingB2 = elementB2();
pendingB2.className = 'message bot-message';
pendingB2.setAttribute('data-scripture-pending', 'true');
boxB2.appendChild(pendingB2);
const gatedEntry = windowB2.addMessage('A reviewed answer arriving through the display gate.', false, []);
assert.equal(gatedEntry, boxB2.children[1], 'addMessage still returns the appended entry during a gate window');
assert.equal(viewedB2.length, 0, 'no append-time scroll while a display-gate placeholder is pending');
boxB2.children.splice(boxB2.children.indexOf(pendingB2), 1);
pendingB2.parentElement = null;
const directEntry = windowB2.addMessage('An answer appended with no gate pending.', false, []);
assert.equal(viewedB2.length, 1, 'append-time anchoring resumes once no placeholder is pending');
assert.equal(viewedB2[0].node, directEntry, 'the direct append is the one anchored');
console.log('PASS: appends inside a display-gate window do not scroll; direct appends anchor at append time.');
