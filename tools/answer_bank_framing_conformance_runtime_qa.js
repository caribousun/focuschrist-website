/* Framing conformance gate for the composed answer surfaces.
 *
 * Wyatt direction, 2026-10-24: anything placed on the site must
 * follow the page's framing and section pattern; a group of pills or
 * chips never renders without its section label stating what it is.
 * PR #511 shipped the reviewed follow-up chips with no label because
 * the reviewed design was silent on framing and verification stopped
 * at "renders and works". This harness makes framing a structural
 * gate instead of a reviewer's memory.
 *
 * Construction follows tools/answer_bank_followup_chips_runtime_qa.js:
 * the real Ask chain in a vm page context (site-common.js with the
 * production Step S evaluator, the shipped bank data/matcher/guards/
 * lane, the real scripture library, the display gate extracted
 * verbatim from site-common.js), extended in two ways:
 *
 * - window.addMessage is the page's own implementation, extracted
 *   verbatim from ask.html, so the sources sections are real DOM
 *   (a .sources box with its title, groups with their group titles,
 *   and the source-link lists), not a recorder's summary.
 * - The Pioneer surface is exercised through the lane's
 *   serveDisclosure() into a disclosure container, the same direct
 *   DOM render pioneers.html uses.
 *
 * The invariant, checked structurally over the DOM each surface
 * renders for one answer turn:
 *
 *   Every pill group inside the answer block sits inside a section
 *   carrying a visible label in the page's established section-header
 *   treatment, the label present in the DOM as part of that section
 *   and preceding the group, with no other pill group between the
 *   label and the group it frames. A group whose own first child is
 *   such a label is framed by construction.
 *
 * Definitions are structural, never a search for one known label:
 *
 * - Pill group: an element whose element children, after skipping
 *   any leading label-treatment children, number at least one and
 *   are all pills (BUTTON elements, or A elements carrying a class,
 *   the page's pill-styled links), with no non-whitespace direct
 *   text. Prose paragraphs holding a bare link are not pill groups,
 *   and neither is a lone action button among paragraphs.
 * - Section label: a non-interactive element with visible text
 *   carrying a section-header treatment class. The treatment classes
 *   are DERIVED at startup from this tree's own shipped CSS
 *   (ask.html's inline styles, ask-experience.css,
 *   pioneer-experience.css, and the source router's injected
 *   styles): any class whose rule declares text-transform: uppercase
 *   together with letter-spacing. On the shipped tree that derives
 *   the classes behind SOURCES, OFFICIAL CHURCH SOURCES, RELATED
 *   FOCUSCHRIST STUDY, and OFFICIAL STUDY PATHS, and it derives any
 *   future label class styled with the same treatment, so the gate
 *   catches future unlabeled groups, not only today's.
 *
 * Scope, stated plainly: the scan covers everything one answer turn
 * renders into the chat box on Ask (the answer message, its sources
 * sections, the follow-up chips, and the clarification options the
 * send path appends as part of the turn) and the Pioneer disclosure
 * container. The source router's observer-appended study-path panels
 * are not rendered here (they need the page MutationObserver); their
 * titles are built by the same append functions that build their
 * lists, and no claim is made for them beyond that.
 *
 * Expected results: on the tree that shipped PR #511 this gate FAILS,
 * naming the follow-up chips group and the suggestion options group
 * (neither carries a visible label). Once the label fix lands, the
 * same harness passes on every surface.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

/* ---------------- section-label treatment, derived from shipped CSS ---------------- */
function deriveLabelClasses() {
    const cssTexts = [read('ask-experience.css'), read('pioneer-experience.css')];
    const askHtml = read('ask.html');
    for (const match of askHtml.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)) cssTexts.push(match[1]);
    const router = read('study-source-router.js');
    const injected = router.match(/style\.textContent = `([\s\S]*?)`;/);
    if (injected) cssTexts.push(injected[1]);
    const classes = new Set();
    for (const css of cssTexts) {
        for (const rule of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
            const declarations = rule[2].toLowerCase().replace(/\s+/g, '');
            if (!declarations.includes('text-transform:uppercase')) continue;
            if (!declarations.includes('letter-spacing')) continue;
            for (const selector of rule[1].split(',')) {
                const tokens = [...selector.matchAll(/\.([A-Za-z0-9_-]+)/g)].map(m => m[1]);
                if (tokens.length) classes.add(tokens[tokens.length - 1]);
            }
        }
    }
    return classes;
}
const LABEL_CLASSES = deriveLabelClasses();
assert.ok(LABEL_CLASSES.has('sources-title') && LABEL_CLASSES.has('sources-group-title')
    && LABEL_CLASSES.has('fc-source-paths-title'),
    'derived label classes must cover the shipped section headers: ' + [...LABEL_CLASSES].join(', '));

/* ---------------- minimal DOM (FakeNode) ---------------- */
function textNode(text) { return { nodeType: 3, textContent: String(text), isConnected: false, parent: null }; }
class FakeNode {
    constructor(tag) {
        this.tagName = String(tag || 'div').toUpperCase();
        this.nodeType = 1;
        this.className = '';
        this._nodes = [];
        this.attributes = {};
        this.listeners = {};
        this.style = {};
        this.dataset = {};
        this.isConnected = false;
        this.parent = null;
        this.scrollTop = 0;
        this.scrollHeight = 0;
    }
    get childNodes() { return this._nodes; }
    get children() { return this._nodes.filter(n => n.nodeType === 1); }
    get lastElementChild() {
        const els = this.children;
        return els.length ? els[els.length - 1] : null;
    }
    get textContent() { return this._nodes.map(c => c.textContent).join(''); }
    set textContent(value) {
        const text = String(value == null ? '' : value);
        this._nodes.forEach(c => { c.isConnected = false; c.parent = null; });
        this._nodes = text ? [textNode(text)] : [];
        this._nodes.forEach(c => { c.parent = this; c.isConnected = this.isConnected; });
    }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return name in this.attributes ? this.attributes[name] : null; }
    hasAttribute(name) { return name in this.attributes; }
    removeAttribute(name) { delete this.attributes[name]; }
    appendChild(node) {
        if (node.parent) node.parent._nodes = node.parent._nodes.filter(c => c !== node);
        node.parent = this; node.isConnected = true;
        this._nodes.push(node);
        return node;
    }
    replaceChildren(...nodes) {
        this._nodes.forEach(c => { c.isConnected = false; c.parent = null; });
        this._nodes = [];
        nodes.forEach(n => this.appendChild(n));
    }
    remove() {
        if (this.parent) this.parent._nodes = this.parent._nodes.filter(c => c !== this);
        this.parent = null; this.isConnected = false;
    }
    contains(node) {
        if (node === this) return true;
        return this._nodes.some(c => c.nodeType === 1 && c.contains(node));
    }
    closest() { return null; }
    addEventListener(name, cb) { this.listeners[name] = cb; }
    dispatchEvent(event) { this.lastEvent = event; return true; }
    querySelector(selector) {
        const found = this.querySelectorAll(selector);
        return found.length ? found[0] : null;
    }
    querySelectorAll(selector) {
        const wanted = String(selector).split(',').map(s => s.trim())
            .filter(s => /^\.[A-Za-z0-9_-]+$/.test(s)).map(s => s.slice(1));
        if (!wanted.length) return [];
        return descendants(this).filter(n => wanted.some(cls => hasClass(n, cls)));
    }
    focus() {}
}
function descendants(node, out) {
    out = out || [];
    node.childNodes.forEach(c => { if (c.nodeType === 1) { out.push(c); descendants(c, out); } });
    return out;
}
function hasClass(node, cls) { return String(node.className || '').split(/\s+/).includes(cls); }
function findByClass(node, cls) { return descendants(node).filter(n => hasClass(n, cls)); }

const box = new FakeNode('div');
box.setAttribute('id', 'chatBox');
const userInput = { value: '', disabled: false, focus() {} };
const sendBtn = { disabled: false, textContent: 'Ask' };
const documentStub = {
    addEventListener() {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
    getElementById(id) {
        if (id === 'chatBox') return box;
        if (id === 'userInput') return userInput;
        if (id === 'sendBtn') return sendBtn;
        return null;
    },
    createElement(tag) { return new FakeNode(tag); },
    createTextNode(text) { return textNode(text); },
    documentElement: new FakeNode('html'),
    head: new FakeNode('head'),
    body: new FakeNode('body'),
};

/* ---------------- vm page context ---------------- */
const sandbox = {};
sandbox.window = sandbox;
sandbox.self = sandbox;
sandbox.globalThis = sandbox;
sandbox.location = { pathname: '/ask.html', search: '', hash: '', href: 'https://focuschrist.com/ask.html', origin: 'https://focuschrist.com' };
sandbox.document = documentStub;
sandbox.sessionStorage = { getItem() { return null; }, setItem() {}, removeItem() {} };
sandbox.conversationHistory = [];
sandbox.qaDatabase = {};
sandbox.console = console;
sandbox.setTimeout = setTimeout;
sandbox.clearTimeout = clearTimeout;
sandbox.CustomEvent = CustomEvent;
sandbox.TextEncoder = TextEncoder;
sandbox.TextDecoder = TextDecoder;
sandbox.URL = URL;
sandbox.Response = Response;
sandbox.crypto = require('node:crypto').webcrypto;
sandbox.addEventListener = function () {};
let fetchCalls = 0;
sandbox.fetch = function () { fetchCalls += 1; throw new Error('the research Worker must not be called in this harness'); };
sandbox.module = { exports: {} };
vm.createContext(sandbox);
const run = (code, name) => vm.runInContext(code, sandbox, { filename: name });

run(read('site-common.js'), 'site-common.js');
run(read('reviewed-ask-knowledge.js'), 'reviewed-ask-knowledge.js');
run(read('answer-bank-data.js'), 'answer-bank-data.js');
run(read('answer-bank-matcher.js'), 'answer-bank-matcher.js');
run(read('answer-bank-guards.js'), 'answer-bank-guards.js');
run(read('answer-bank-lane.js'), 'answer-bank-lane.js');

/* Scripture library through its module factory, as in the display-gate QA. */
run(read('scripture-library.js'), 'scripture-library.js');
const factory = sandbox.module.exports;
assert.equal(typeof factory, 'function', 'scripture library factory must export');
const library = factory(JSON.parse(read('scripture-data/catalog.json')),
    async url => new Response(fs.readFileSync(path.join(root, url))));
sandbox.focusChristScriptureLibrary = library;
sandbox.focusChristScriptureReady = Promise.resolve(library);

/* The page's own addMessage, extracted verbatim from ask.html, so the
 * answer block's sections are the real shipped DOM. */
const askHtml = read('ask.html');
const addMessageStart = askHtml.indexOf('    function addMessage(text, isUser, sources = []) {');
const addMessageEnd = askHtml.indexOf('    async function sendMessage(){');
assert.ok(addMessageStart >= 0 && addMessageEnd > addMessageStart, 'ask.html addMessage extraction must resolve');
const addMessageSource = askHtml.slice(addMessageStart, addMessageEnd);
assert.ok(addMessageSource.includes('sources-group-title') && addMessageSource.includes('Official Church sources'),
    'extracted addMessage must be the shipped sources renderer');
run(addMessageSource + '\nwindow.addMessage = addMessage;', 'ask.html#addMessage');

/* Install the shipped display gate over the page's addMessage,
 * extracted verbatim, exactly as the display-gate QA does. */
const siteCommon = read('site-common.js');
const pattern = siteCommon.match(/    const SCRIPTURE_CITATION_PATTERN = [^\n]+/)[0];
const extract = siteCommon.slice(siteCommon.indexOf('    function extractScriptureCitations('), siteCommon.indexOf('    function withoutOutputPersonNameScriptureCollisions('));
const gate = siteCommon.slice(siteCommon.indexOf('    window.focusChristVerifyScriptureAnswer ='), siteCommon.indexOf('    function loadStudyJourney('));
assert.ok(gate.includes('function installScriptureDisplayGate()'), 'production gate extraction must resolve');
run(pattern + '\n' + extract + '\n' + gate + '\ninstallScriptureDisplayGate();', 'site-common.js#display-gate');

run(read('study-intelligence-v3.js'), 'study-intelligence-v3.js');
assert.equal(typeof sandbox.sendMessage, 'function', 'v3 must own window.sendMessage on Ask');

const records = sandbox.FocusChristAnswerBankData.records;
assert.equal(records.length, 222, 'shipped bank must hold 222 records');

/* ---------------- structural framing scan ---------------- */
function isInteractive(node) {
    return node.tagName === 'BUTTON' || node.tagName === 'A'
        || (typeof node.getAttribute === 'function' && node.getAttribute('role') === 'button');
}
function isPill(node) {
    if (node.tagName === 'BUTTON') return true;
    if (node.tagName === 'A') return String(node.className || '').trim().length > 0;
    return typeof node.getAttribute === 'function' && node.getAttribute('role') === 'button';
}
function carriesLabelTreatment(node) {
    return String(node.className || '').split(/\s+/).some(cls => LABEL_CLASSES.has(cls));
}
function isLabel(node) {
    return !isInteractive(node) && carriesLabelTreatment(node) && node.textContent.trim().length > 0;
}
function isPillGroup(node) {
    if (isInteractive(node)) return false;
    const kids = node.children;
    if (!kids.length) return false;
    let i = 0;
    while (i < kids.length && isLabel(kids[i])) i++;
    if (i >= kids.length) return false;
    for (; i < kids.length; i++) if (!isPill(kids[i])) return false;
    const directText = node.childNodes.filter(n => n.nodeType === 3)
        .map(n => n.textContent).join('').trim();
    return directText.length === 0;
}
function describeGroup(node) {
    const pills = node.children.filter(c => isPill(c));
    const first = pills.length ? pills[0].textContent.trim().replace(/\s+/g, ' ').slice(0, 48) : '';
    const forAttr = typeof node.getAttribute === 'function' ? node.getAttribute('data-followup-for') : null;
    return '<' + node.tagName.toLowerCase() + ' class="' + String(node.className || '') + '">'
        + (forAttr ? ' data-followup-for="' + forAttr + '"' : '')
        + ' — ' + pills.length + ' pill(s), first: "' + first + '"';
}
function scanBlock(blockRoot, surface) {
    const order = [blockRoot, ...descendants(blockRoot)];
    const groups = order.filter(isPillGroup)
        .filter(g => !order.some(o => o !== g && isPillGroup(o) && o.contains(g)));
    const violations = [];
    for (const group of groups) {
        const kids = group.children;
        if (kids.length && isLabel(kids[0])) continue; // framed by its own leading label
        const gi = order.indexOf(group);
        let framed = false;
        for (let j = gi - 1; j >= 0; j--) {
            const candidate = order[j];
            if (groups.includes(candidate)) break; // another pill group intervenes
            if (isLabel(candidate) && !groups.some(g => g.contains(candidate))) { framed = true; break; }
        }
        if (!framed) violations.push({ surface, group: describeGroup(group) });
    }
    return { groups: groups.map(describeGroup), violations };
}

/* ---------------- surface drivers ---------------- */
async function settled(node) {
    for (let i = 0; i < 200; i++) {
        if (!node.hasAttribute('data-scripture-pending')) return;
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    throw new Error('display gate did not settle');
}
function botNodes() { return box.children.filter(n => n.nodeType === 1 && /bot-message/.test(n.className)); }
async function ask(question) {
    box.children.slice().forEach(n => n.remove());
    sandbox.conversationHistory.length = 0;
    userInput.value = question;
    await sandbox.sendMessage();
    const bots = botNodes();
    assert.ok(bots.length, 'no bot message rendered for: ' + question);
    const node = bots[bots.length - 1];
    await settled(node);
    return node;
}

(async () => {
    console.log('Derived section-label treatment classes: ' + [...LABEL_CLASSES].sort().join(', '));
    const allViolations = [];

    /* ---------- Ask: reviewed-bank serve ---------- */
    const serveNode = await ask('Who is God the Father?');
    assert.ok(serveNode.textContent.includes('God the Father'), 'serve probe must render a bank answer');
    assert.equal(findByClass(box, 'ask-followup-chips').length, 1, 'serve probe must render the follow-up chips group');
    const serveScan = scanBlock(box, 'ask bank serve');
    console.log('SURFACE ask bank serve: pill groups found: ' + serveScan.groups.length);
    serveScan.groups.forEach(g => console.log('  group: ' + g));
    allViolations.push(...serveScan.violations);

    /* ---------- Ask: suggestion-only response ---------- */
    const sugNode = await ask('Who is our Heavenly Father?');
    assert.ok(sugNode.textContent.includes('I do not have a reviewed answer for that exact question yet'),
        'the suggestion probe must take the suggestion path');
    const sugGroups = findByClass(box, 'ask-clarification-options')
        .filter(n => !hasClass(n, 'ask-followup-chips'));
    assert.ok(sugGroups.length >= 1, 'the suggestion probe must render its options group');
    const sugScan = scanBlock(box, 'ask suggestion');
    console.log('SURFACE ask suggestion: pill groups found: ' + sugScan.groups.length);
    sugScan.groups.forEach(g => console.log('  group: ' + g));
    allViolations.push(...sugScan.violations);

    /* ---------- Pioneer: reviewed-bank disclosure ---------- */
    const item = records.find(r => typeof r.item_key === 'string' && r.item_key);
    assert.ok(item, 'the shipped bank must hold Pioneer item records');
    const control = new FakeNode('button');
    control.setAttribute('data-topic', item.item_key);
    const container = new FakeNode('div');
    const servedDisclosure = sandbox.FocusChristAnswerBankLane.serveDisclosure(control, container);
    assert.equal(servedDisclosure, true, 'the Pioneer disclosure must serve from the bank: ' + item.item_key);
    assert.ok(container.textContent.includes(String(item.answer || '').split('\n')[0].trim().slice(0, 24)),
        'the Pioneer disclosure must render the record answer');
    const pioneerScan = scanBlock(container, 'pioneer disclosure');
    console.log('SURFACE pioneer disclosure (' + item.item_key + '): pill groups found: ' + pioneerScan.groups.length);
    pioneerScan.groups.forEach(g => console.log('  group: ' + g));
    allViolations.push(...pioneerScan.violations);

    assert.equal(fetchCalls, 0, 'no probe may reach the research Worker');

    if (allViolations.length) {
        allViolations.forEach(v => console.error('FRAMING VIOLATION [' + v.surface + ']: unlabeled pill group: ' + v.group));
        console.error('FAIL: framing conformance — ' + allViolations.length + ' unlabeled pill group(s) across the composed answer surfaces.');
        process.exitCode = 1;
        return;
    }
    console.log('PASS: framing conformance — every pill group on the composed answer surfaces sits inside a section carrying its visible label.');
})().catch(error => { console.error(error); process.exitCode = 1; });
