/* Composed-chain regression QA for the answer bank display-gate exemption.
 *
 * Exercises the real Ask chain end to end in a vm context whose global is
 * the page window: site-common.js (production Step S + source integrity),
 * the shipped answer bank (data, matcher, guards, lane), the real
 * scripture library, the display gate extracted verbatim from
 * site-common.js and installed over a recording addMessage (the same
 * extraction pattern as tools/scripture_display_runtime_qa.js), and
 * study-intelligence-v3.js driving window.sendMessage.
 *
 * Assertions:
 * - The six known probes serve their pinned reviewed-bank records and
 *   the gate renders those answers exactly as served, with sources and
 *   the reviewed-bank provenance marker reaching the renderer.
 * - A non-bank text that trips checkAnswer is still replaced by the
 *   gate, with or without a bank answer's text: the exemption keys on
 *   the lane provenance marker only, never on answer text, and a
 *   marker missing its pin earns nothing.
 * - No bank serve reaches the research Worker: fetch stays unused until
 *   the intentional no-bank case, which must make exactly its two attempts.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

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
    addEventListener(name, cb) { this.listeners[name] = cb; }
    dispatchEvent(event) { this.lastEvent = event; return true; }
    querySelectorAll() { return []; }
    querySelector() { return null; }
    focus() {}
}

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
    documentElement: new FakeNode('html'),
    head: new FakeNode('head'),
    body: new FakeNode('body'),
};

/* ---------------- vm page context ---------------- */
const sandbox = {};
sandbox.window = sandbox;
sandbox.self = sandbox;
sandbox.globalThis = sandbox;
sandbox.location = { pathname: '/ask.html', search: '', hash: '' };
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

/* Scripture library through its module factory, chapters from the repo's
 * own scripture-data files (the library verifies their SHA-256 itself). */
run(read('scripture-library.js'), 'scripture-library.js');
const factory = sandbox.module.exports;
assert.equal(typeof factory, 'function', 'scripture library factory must export');
const library = factory(JSON.parse(read('scripture-data/catalog.json')),
    async url => new Response(fs.readFileSync(path.join(root, url))));
sandbox.focusChristScriptureLibrary = library;
sandbox.focusChristScriptureReady = Promise.resolve(library);

/* The page's own addMessage, as a recorder standing in for ask.html's. */
const renderedCalls = [];
sandbox.addMessage = function (text, isUser, sources, extra) {
    const node = new FakeNode('div');
    node.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
    node.textContent = text;
    box.appendChild(node);
    renderedCalls.push({ text, isUser, sources, extra, node });
    return node;
};

/* Install the shipped display gate over the recorder, extracted verbatim
 * from the fixed site-common.js exactly as the existing display QA does. */
const siteCommon = read('site-common.js');
const pattern = siteCommon.match(/    const SCRIPTURE_CITATION_PATTERN = [^\n]+/)[0];
const extract = siteCommon.slice(siteCommon.indexOf('    function extractScriptureCitations('), siteCommon.indexOf('    function withoutOutputPersonNameScriptureCollisions('));
const gate = siteCommon.slice(siteCommon.indexOf('    window.focusChristVerifyScriptureAnswer ='), siteCommon.indexOf('    function loadStudyJourney('));
assert.ok(gate.includes('function installScriptureDisplayGate()'), 'production gate extraction must resolve');
assert.ok(gate.includes('function isPinnedReviewedBankServe('), 'gate extraction must include the reviewed-bank exemption predicate');
run(pattern + '\n' + extract + '\n' + gate + '\ninstallScriptureDisplayGate();', 'site-common.js#display-gate');

run(read('study-intelligence-v3.js'), 'study-intelligence-v3.js');
assert.equal(typeof sandbox.sendMessage, 'function', 'v3 must own window.sendMessage on Ask');

/* ------------- expected values from the shipped bank data ------------- */
const records = sandbox.FocusChristAnswerBankData.records;
assert.equal(records.length, 222, 'shipped bank must hold 222 records');
const byId = new Map(records.map(r => [r.id, r]));
function mapSources(record) {
    const out = [];
    [['site', record.sources_site], ['church', record.sources_church]].forEach(([group, list]) => {
        (Array.isArray(list) ? list : []).forEach(source => {
            if (source && source.url) out.push({ text: source.label || 'Source', url: source.url });
        });
    });
    return out;
}

const FAILURE_TEXT = 'I could not confirm the scripture reference or wording.';
async function settled(node) {
    for (let i = 0; i < 200; i++) {
        if (!node.hasAttribute('data-scripture-pending')) return;
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    throw new Error('display gate did not settle');
}
function lastBotNode() {
    const bots = box.children.filter(n => n.nodeType === 1 && /bot-message/.test(n.className));
    return bots[bots.length - 1] || null;
}
async function ask(question) {
    box.children.slice().forEach(n => n.remove());
    renderedCalls.length = 0;
    userInput.value = question;
    await sandbox.sendMessage();
    const node = lastBotNode();
    assert.ok(node, 'no bot message rendered for: ' + question);
    await settled(node);
    return node;
}

const PROBES = [
    ['What does Doctrine and Covenants 6:36 teach?', 'ask-what-does-doctrine-and-covenants-6-36-teach'],
    ['Who is the Good Shepherd?', 'ask-who-is-the-good-shepherd'],
    ['What is The Living Christ?', 'ask-what-is-the-living-christ-the-testimony-of-the-apostles'],
    ['What is the Book of Alma about?', 'ask-what-is-the-book-of-alma'],
    ['Who is Jesus Christ, and why is He central to Latter-day Saint belief?', 'ask-what-do-latter-day-saints-believe-about-jesus-christ'],
    ['What is the Holy Ghost in the Godhead?', 'ask-who-is-the-holy-ghost'],
];

(async () => {
    for (const [question, recordId] of PROBES) {
        const record = byId.get(recordId);
        assert.ok(record, 'dataset record missing: ' + recordId);
        const node = await ask(question);
        assert.equal(node.textContent, record.answer,
            'gate must render the pinned bank answer exactly as served: ' + recordId);
        assert.ok(!node.textContent.includes(FAILURE_TEXT), 'bank answer must not be replaced: ' + recordId);
        const botCalls = renderedCalls.filter(c => !c.isUser);
        const render = botCalls[botCalls.length - 1];
        /* Rendered values are built inside the vm realm, so compare by
         * canonical JSON rather than deepStrictEqual (prototype check). */
        assert.equal(JSON.stringify(render.sources), JSON.stringify(mapSources(record)),
            'rendered sources must be the lane-mapped sources: ' + recordId);
        assert.equal(JSON.stringify(render.extra), JSON.stringify({
            reviewedBankServe: true,
            bankRecordId: recordId,
            bankPin: record.integrity,
            bankMode: 'focuschrist-answer-bank',
            bankProvenance: 'reviewed-bank',
        }), 'renderer must receive the lane provenance marker: ' + recordId);
        console.log('PROBE PASS:', recordId);
    }
    assert.equal(fetchCalls, 0, 'bank probes must make zero Worker calls');
    assert.equal(sandbox.conversationHistory.filter(t => t.role === 'user').length, PROBES.length,
        'each probe must be remembered as a user turn');

    /* Gate keying controls, called through the wrapped addMessage. */
    const gs = byId.get('ask-who-is-the-good-shepherd');
    const gsSources = mapSources(gs);

    let node = sandbox.addMessage('John 99:1 teaches faith.', false, []);
    await settled(node);
    assert.ok(node.textContent.includes('could not confirm') && !node.textContent.includes('John 99:1'),
        'non-bank text that trips checkAnswer must still be replaced by the gate');
    console.log('CONTROL PASS: non-bank tripping text replaced');

    node = sandbox.addMessage(gs.answer, false, gsSources);
    await settled(node);
    assert.ok(node.textContent.includes(FAILURE_TEXT) && node.textContent !== gs.answer,
        'a bank answer text without the provenance marker must still be replaced');
    console.log('CONTROL PASS: bank text without marker replaced');

    node = sandbox.addMessage(gs.answer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: gs.id, bankPin: '',
    });
    await settled(node);
    assert.ok(node.textContent.includes(FAILURE_TEXT),
        'a marker missing its pin must earn no exemption');
    console.log('CONTROL PASS: pin-less marker replaced');

    node = sandbox.addMessage(gs.answer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: gs.id, bankPin: gs.integrity,
    });
    await settled(node);
    assert.equal(node.textContent, gs.answer,
        'a complete lane provenance marker must render the answer as served');
    console.log('CONTROL PASS: complete marker renders as served');

    const userNode = sandbox.addMessage('A visitor message with "quotes" and John 3:16.', true, []);
    assert.equal(userNode.textContent, 'A visitor message with "quotes" and John 3:16.',
        'user messages must pass through untouched');
    console.log('CONTROL PASS: user message untouched');

    /* ---- Concurrence cases: A-2026-10-24-ASK-DECOUPLING-CONCURRENCE-01 ----
     * The exemption is bound through the bank-owning code, and a genuine
     * serve precedes the live lookup. The discriminator for exemption is
     * the library-down state: an exempt serve renders as served, anything
     * else becomes the gate's fail-closed fallback text. */
    const GATE_FALLBACK = 'Scripture verification is temporarily unavailable.';
    const readyGood = sandbox.focusChristScriptureReady;
    sandbox.focusChristScriptureReady = Promise.reject(new Error('library down'));
    sandbox.focusChristScriptureReady.catch(() => {});

    node = sandbox.addMessage(gs.answer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: gs.id, bankPin: gs.integrity,
    });
    await settled(node);
    assert.equal(node.textContent, gs.answer,
        'a genuine lane-verified serve must render with the library down');
    console.log('CONTROL PASS: genuine serve renders with library down');

    node = sandbox.addMessage(gs.answer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: gs.id,
        bankPin: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
    });
    await settled(node);
    assert.ok(node.textContent.includes(GATE_FALLBACK) && node.textContent !== gs.answer,
        'a wrong pin must earn no exemption');
    console.log('CONTROL PASS: wrong pin earns no exemption');

    node = sandbox.addMessage(gs.answer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: 'ask-no-such-record',
        bankPin: gs.integrity,
    });
    await settled(node);
    assert.ok(node.textContent.includes(GATE_FALLBACK),
        'a record the bank never carried must earn no exemption');
    console.log('CONTROL PASS: missing record earns no exemption');

    const stalePin = gs.integrity.replace(/.$/, c => (c === '0' ? '1' : '0'));
    node = sandbox.addMessage(gs.answer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: gs.id, bankPin: stalePin,
    });
    await settled(node);
    assert.ok(node.textContent.includes(GATE_FALLBACK),
        'a stale pin that no longer matches the loaded entry must earn no exemption');
    console.log('CONTROL PASS: stale pin earns no exemption');

    const editedAnswer = gs.answer + ' Amen.';
    node = sandbox.addMessage(editedAnswer, false, gsSources, {
        reviewedBankServe: true, bankMode: 'focuschrist-answer-bank',
        bankProvenance: 'reviewed-bank', bankRecordId: gs.id, bankPin: gs.integrity,
    });
    await settled(node);
    assert.ok(node.textContent.includes(GATE_FALLBACK) && node.textContent !== editedAnswer,
        'an edited answer must earn no exemption');
    console.log('CONTROL PASS: edited answer earns no exemption');

    /* A genuine composed serve with the library promise rejected: the
     * bank precedes the lookup, so the serve is unaffected. */
    const shepherdNode = await ask('Who is the Good Shepherd?');
    assert.equal(shepherdNode.textContent, gs.answer,
        'composed bank serve must render with the library down');
    console.log('CONTROL PASS: composed serve with library rejected');

    /* A genuine composed serve with the library promise never settling:
     * before the fix, askV3 awaited the lookup before the bank and the
     * ask stalled here. */
    sandbox.focusChristScriptureReady = new Promise(() => {});
    const dcRecord = byId.get('ask-what-does-doctrine-and-covenants-6-36-teach');
    const hangAsk = ask('What does Doctrine and Covenants 6:36 teach?');
    const hangOutcome = await Promise.race([
        hangAsk.then(node => ({ node })),
        new Promise(resolve => setTimeout(() => resolve({ timeout: true }), 12000)),
    ]);
    assert.ok(!hangOutcome.timeout, 'bank serve must not stall on a hung library promise');
    assert.equal(hangOutcome.node.textContent, dcRecord.answer,
        'composed bank serve must render with the library hung');
    console.log('CONTROL PASS: composed serve with library hung');
    sandbox.focusChristScriptureReady = readyGood;

    /* Topic render: a topic-card phrasing served by the bank renders
     * its pinned record exactly, marker included (checked by the gate). */
    const topicCandidates = ['Tell me about temples', 'Tell me about the Book of Mormon',
        'Tell me about Jesus Christ', 'Tell me about prayer', 'Tell me about faith'];
    let topicServed = null;
    for (const topicQuestion of topicCandidates) {
        const topicNode = await ask(topicQuestion);
        const served = records.find(r => r.answer === topicNode.textContent);
        if (served) { topicServed = served; break; }
    }
    assert.ok(topicServed, 'at least one topic phrasing must serve its pinned bank record');
    console.log('CONTROL PASS: topic serve renders pinned record', topicServed.id);

    /* Follow-up render: a follow-up chip's canonical question, asked as
     * the visitor's next question, serves its pinned record exactly. */
    const father = byId.get('ask-who-is-god-the-father');
    assert.ok(father, 'dataset record missing: ask-who-is-god-the-father');
    const fatherNode = await ask(father.question);
    assert.equal(fatherNode.textContent, father.answer, 'antecedent serve must render exactly');
    const chips = sandbox.FocusChristAnswerBankLane.followUpChips(father.id);
    assert.ok(Array.isArray(chips) && chips.length > 0, 'served record must offer follow-up chips');
    const chip = chips[0];
    const chipQuestion = typeof chip === 'string' ? chip : chip.question;
    const chipRecord = records.find(r => r.question === chipQuestion);
    assert.ok(chipRecord, 'chip target must be a shipped record: ' + chipQuestion);
    const chipNode = await ask(chipQuestion);
    assert.equal(chipNode.textContent, chipRecord.answer,
        'follow-up chip question must serve its pinned record exactly');
    console.log('CONTROL PASS: follow-up chip serve renders pinned record', chipRecord.id);

    /* Step S still stops at the lane: a safety-flagged question is not
     * a bank serve, whatever it resembles. */
    const lane = sandbox.FocusChristAnswerBankLane;
    assert.equal(lane.answer({ question_text: 'How do I kill myself?', profile: 'ask', history: [] }), null,
        'Step S must stop a flagged question before bank matching');
    console.log('CONTROL PASS: Step S stops flagged question at the lane');

    /* Ambiguity control still precedes the lanes: a bare-Joseph death
     * question earns the clarification, not an answer. */
    const ambNode = await ask('When did Joseph die?');
    assert.ok(ambNode.textContent.includes('Which Joseph do you mean'),
        'ambiguity clarification must be preserved');
    console.log('CONTROL PASS: ambiguity clarification preserved');

    /* Every serve above is a composed bank serve or a gate control, and
     * none of them may reach the research Worker: the bank precedes the
     * lookup, so fetch stays unused until the intentional no-bank case
     * below makes its own attempts. */
    assert.equal(fetchCalls, 0, 'no composed serve in this harness may reach the research Worker');

    /* Ordinary no-bank question: keeps the honest research-unavailable
     * behavior (the harness fetch throws, as a dead Worker would), and
     * is never dressed as a bank serve or the gate fallback. */
    const fetchCallsBeforeMiss = fetchCalls;
    const missNode = await ask('What is the airspeed velocity of an unladen swallow?');
    assert.ok(!records.some(r => r.answer === missNode.textContent),
        'a no-bank question must not render a bank answer');
    assert.ok(!missNode.textContent.includes(GATE_FALLBACK),
        'a no-bank question must not render the gate fallback');
    assert.ok(missNode.textContent.includes('temporarily unavailable') || missNode.textContent.includes('unable to check')
        || missNode.textContent.includes('I do not have a reviewed answer'),
        'a no-bank question must keep one of the honest no-bank outcomes (research-unavailable or suggestion)');
    console.log('CONTROL PASS: ordinary no-bank behavior preserved');
    assert.equal(fetchCalls - fetchCallsBeforeMiss, 2,
        'the no-bank question must make exactly its two research Worker attempts');

    console.log('PASS: answer bank display-gate composed chain — 6/6 probes render their pinned reviewed answers; gate unchanged for non-bank text.');
})().catch(error => { console.error(error); process.exitCode = 1; });
