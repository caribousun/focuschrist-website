/* Composed-chain QA for the reviewed follow-up chips (defect D5).
 *
 * Same construction as tools/answer_bank_display_gate_runtime_qa.js:
 * the real Ask chain in a vm page context (site-common.js with the
 * production Step S evaluator, the shipped bank data/matcher/guards/
 * lane, the real scripture library, the display gate extracted
 * verbatim from site-common.js over a recording addMessage, and
 * study-intelligence-v3.js driving window.sendMessage), extended with
 * the chip assertions:
 *
 * - A reviewed-bank serve renders the served record's follow-up chips
 *   inside the answer's message node: the lane's chips, in record
 *   order, as buttons carrying the targets' canonical questions.
 * - A chip tap submits the canonical question through the normal send
 *   path: a new user turn, a new pinned bank serve of the target
 *   record rendered in full through the display gate, and the target's
 *   own chips under it (conversations chain).
 * - A suggestion outcome renders its clarification options and no
 *   follow-up chips.
 * - A sensitive record's serve renders its answer AND its own chips:
 *   spec 4.4's stated interactions are exhaustive, and the addendum's
 *   sensitive exclusion (2.3 rule 3) is scoped to a sensitive record
 *   used as a component of another artifact's composition, so
 *   nothing suppresses the served record's own P1 adjunct.
 * - Census: for every record in the shipped bank, the lane's chips
 *   are exactly the matcher's chips (capped at five), sensitive
 *   records included, with nothing suppressed; and every rendered chip's canonical
 *   question serves its target record through the matcher running
 *   the production Step S evaluator, with any exception enumerated
 *   and required to be a Step S claim, never a matching failure.
 * - No bank probe reaches the research Worker (fetch stays unused).
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
    contains(node) {
        if (node === this) return true;
        return this._nodes.some(c => c.nodeType === 1 && c.contains(node));
    }
    addEventListener(name, cb) { this.listeners[name] = cb; }
    dispatchEvent(event) { this.lastEvent = event; return true; }
    querySelectorAll() { return []; }
    querySelector() { return null; }
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
assert.equal(typeof sandbox.FocusChristAnswerBankLane.followUpChips, 'function',
    'the lane must expose followUpChips for the Ask renderer');

/* Scripture library through its module factory, as in the display-gate QA. */
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

/* Install the shipped display gate over the recorder, extracted verbatim. */
const siteCommon = read('site-common.js');
const pattern = siteCommon.match(/    const SCRIPTURE_CITATION_PATTERN = [^\n]+/)[0];
const extract = siteCommon.slice(siteCommon.indexOf('    function extractScriptureCitations('), siteCommon.indexOf('    function withoutOutputPersonNameScriptureCollisions('));
const gate = siteCommon.slice(siteCommon.indexOf('    window.focusChristVerifyScriptureAnswer ='), siteCommon.indexOf('    function loadStudyJourney('));
assert.ok(gate.includes('function installScriptureDisplayGate()'), 'production gate extraction must resolve');
run(pattern + '\n' + extract + '\n' + gate + '\ninstallScriptureDisplayGate();', 'site-common.js#display-gate');

run(read('study-intelligence-v3.js'), 'study-intelligence-v3.js');
assert.equal(typeof sandbox.sendMessage, 'function', 'v3 must own window.sendMessage on Ask');

/* ------------- expected values from the shipped bank data ------------- */
const records = sandbox.FocusChristAnswerBankData.records;
assert.equal(records.length, 222, 'shipped bank must hold 222 records');
const byId = new Map(records.map(r => [r.id, r]));

/* A second matcher over the same pinned bank, wired to the production
 * Step S evaluator exactly as the lane wires it, for the chip census. */
const prodMatcher = sandbox.FocusChristAnswerBank.createMatcher(
    sandbox.FocusChristAnswerBank.loadBank(records, {
        assignments: sandbox.FocusChristAnswerBankData.assignments || {},
        guards: sandbox.FocusChristAnswerBankGuards || {}
    }).bank,
    {
        evaluateSafety(request) {
            const outcome = sandbox.focusChristQuestionSafety.evaluate(
                request && typeof request.question_text === 'string' ? request.question_text : '');
            if (!outcome || typeof outcome.kind !== 'string') return { kind: 'unavailable' };
            return { kind: outcome.kind, profile: request ? request.profile : undefined };
        }
    });

async function settled(node) {
    for (let i = 0; i < 200; i++) {
        if (!node.hasAttribute('data-scripture-pending')) return;
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    throw new Error('display gate did not settle');
}
async function waitFor(fn, label) {
    for (let i = 0; i < 300; i++) {
        const value = fn();
        if (value) return value;
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    throw new Error('timed out waiting for: ' + label);
}
function botNodes() { return box.children.filter(n => n.nodeType === 1 && /bot-message/.test(n.className)); }
function userNodes() { return box.children.filter(n => n.nodeType === 1 && /user-message/.test(n.className)); }
async function ask(question) {
    /* Each composed probe is a fresh visitor conversation: with prior
     * turns present, the registry's context resolution can claim a
     * question as a generic follow-up and bypass the local lanes by
     * design (verified against askV3 directly), which is production
     * behavior this QA does not test. The chip-tap probe continues its
     * own conversation because the tap happens after ask() returns. */
    box.children.slice().forEach(n => n.remove());
    sandbox.conversationHistory.length = 0;
    renderedCalls.length = 0;
    userInput.value = question;
    await sandbox.sendMessage();
    const bots = botNodes();
    assert.ok(bots.length, 'no bot message rendered for: ' + question);
    const node = bots[bots.length - 1];
    await settled(node);
    return node;
}
function chipGroups(scope) { return findByClass(scope, 'ask-followup-chips'); }

(async () => {
    /* ---------- census: lane chips vs matcher chips ---------- */
    const lane = sandbox.FocusChristAnswerBankLane;
    let matcherTotal = 0, laneTotal = 0, recordsWithChips = 0, maxList = 0, sensitiveRecords = 0;
    for (const record of records) {
        const raw = prodMatcher.followUpChips(record.id);
        matcherTotal += raw.length;
        if (raw.length) recordsWithChips++;
        if (raw.length > maxList) maxList = raw.length;
        if (record.sensitive === true) sensitiveRecords++;
        const viaLane = lane.followUpChips(record.id);
        /* Lane values are built inside the vm realm; compare by
         * canonical JSON, as the display-gate QA does. Sensitive
         * records are held to the same equality: their own serves
         * carry their chips like any other serve (spec 4.4). */
        assert.deepEqual(JSON.parse(JSON.stringify(viaLane)), JSON.parse(JSON.stringify(raw.slice(0, 5))),
            'lane chips must be the matcher chips in order (cap 5): ' + record.id);
        laneTotal += viaLane.length;
    }
    assert.equal(laneTotal, matcherTotal,
        'at this bank the cap binds nothing, so every matcher chip must be rendered-eligible');
    console.log(`CENSUS PASS: lane chips ${laneTotal} rendered-eligible of matcher total ${matcherTotal}; suppressed 0; records with at least one chip ${recordsWithChips}; sensitive records ${sensitiveRecords}; longest list ${maxList}`);

    /* ---------- census: every rendered chip serves its target ---------- */
    let taps = 0; const stepSClaims = [];
    for (const record of records) {
        for (const chip of lane.followUpChips(record.id)) {
            const res = prodMatcher.answer({ question_text: chip.question, profile: 'ask' });
            if (res.status === 'serve' && res.record_id === chip.record_id) { taps++; continue; }
            const safety = sandbox.focusChristQuestionSafety.evaluate(chip.question);
            assert.ok(safety && safety.kind !== 'allowed',
                'chip target must serve or be claimed by Step S: ' + chip.record_id + ' via ' + record.id + ' -> ' + res.status);
            stepSClaims.push(chip.record_id);
        }
    }
    console.log(`CENSUS PASS: ${taps} chip taps serve their target through the production Step S path; Step S-claimed targets: ${JSON.stringify(stepSClaims)}`);

    /* ---------- composed probe: a serve renders its chips ---------- */
    const gtf = byId.get('ask-who-is-god-the-father');
    const gtfChips = JSON.parse(JSON.stringify(lane.followUpChips(gtf.id)));
    assert.equal(gtfChips.length, 3, 'probe record must carry three chips');
    const node = await ask('Who is God the Father?');
    assert.ok(node.textContent.includes(gtf.answer), 'the serve must render the pinned answer');
    const groups = chipGroups(node);
    assert.equal(groups.length, 1, 'the answer message must carry exactly one follow-up chip group');
    assert.equal(groups[0].getAttribute('data-followup-for'), gtf.id, 'chip group must name the served record');
    const buttons = groups[0].children;
    assert.equal(buttons.length, gtfChips.length, 'one chip button per lane chip');
    buttons.forEach((button, i) => {
        assert.equal(button.textContent, gtfChips[i].question, 'chip label must be the target canonical question, in order');
        assert.equal(button.getAttribute('data-followup-target'), gtfChips[i].record_id, 'chip must name its target record');
    });
    console.log('PROBE PASS: serve renders its chips inside the answer message, in record order');

    /* ---------- composed probe: a chip tap submits through the send path ---------- */
    const target = byId.get(gtfChips[0].record_id);
    const usersBefore = userNodes().length;
    buttons[0].listeners.click();
    assert.equal(userInput.value, '', 'sendMessage must consume the submitted question from the composer');
    const followNode = await waitFor(() => {
        const bots = botNodes();
        const last = bots[bots.length - 1];
        return last && last !== node && !last.hasAttribute('data-scripture-pending') ? last : null;
    }, 'follow-up answer after chip tap');
    assert.equal(userNodes().length, usersBefore + 1, 'the chip tap must render the question as a new user turn');
    assert.equal(userNodes()[userNodes().length - 1].textContent, gtfChips[0].question,
        'the submitted user turn must be the chip canonical question exactly');
    assert.ok(followNode.textContent.includes(target.answer),
        'the follow-up serve must render the target record answer in full through the display gate');
    const followGroups = chipGroups(followNode);
    assert.equal(followGroups.length, 1, 'the follow-up answer must carry its own chips (chaining)');
    assert.equal(followGroups[0].getAttribute('data-followup-for'), target.id, 'chained chips must belong to the follow-up record');
    console.log('PROBE PASS: chip tap submits through the send path and the follow-up answer renders in full with its own chips');

    /* ---------- composed probe: a suggestion renders no follow-up chips ---------- */
    const sugNode = await ask('Who is our Heavenly Father?');
    assert.ok(sugNode.textContent.includes('I do not have a reviewed answer for that exact question yet'),
        'the suggestion probe must take the suggestion path');
    assert.equal(findByClass(box, 'ask-followup-chips').length, 0, 'a suggestion must render no follow-up chips');
    assert.ok(findByClass(box, 'ask-clarification-options').length >= 1, 'the suggestion options themselves must still render');
    console.log('PROBE PASS: suggestion renders its options and no follow-up chips');

    /* ---------- composed probe: a sensitive serve renders its chips ---------- */
    const suf = byId.get('ask-why-does-god-allow-suffering-and-evil');
    assert.equal(suf.sensitive, true, 'probe record must be sensitive');
    const sufChips = JSON.parse(JSON.stringify(lane.followUpChips(suf.id)));
    assert.equal(sufChips.length, 2, 'the sensitive record must carry two chips through the lane');
    assert.equal(prodMatcher.followUpChips(suf.id).length, 2, 'the matcher must derive the same two chips for the sensitive record');
    const sufNode = await ask('Why does God allow suffering and evil if He loves us?');
    assert.ok(sufNode.textContent.includes(suf.answer), 'the sensitive serve must render its pinned answer');
    const sufGroups = chipGroups(sufNode);
    assert.equal(sufGroups.length, 1, 'the sensitive serve must render its follow-up chip group');
    assert.equal(sufGroups[0].getAttribute('data-followup-for'), suf.id, 'the sensitive chip group must name the served record');
    const sufButtons = sufGroups[0].children;
    assert.equal(sufButtons.length, sufChips.length, 'one chip button per lane chip on the sensitive serve');
    sufButtons.forEach((button, i) => {
        assert.equal(button.textContent, sufChips[i].question, 'sensitive chip label must be the target canonical question, in order');
        assert.equal(button.getAttribute('data-followup-target'), sufChips[i].record_id, 'sensitive chip must name its target record');
    });
    console.log('PROBE PASS: sensitive serve renders its answer with its own chips');

    assert.equal(fetchCalls, 0, 'no probe may reach the research Worker');
    console.log('PASS: answer bank follow-up chips composed chain — serves render chips, taps chain through the send path, suggestions render none, and sensitive serves render their own chips.');
})().catch(error => { console.error(error); process.exitCode = 1; });
