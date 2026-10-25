/* Runtime QA for the bank context bypass successor (Defect 1).
 *
 * Defect: in study-intelligence-v3.js, askV3 runs resolveFollowup()
 * against session history before bank matching. A complete bank
 * canonical containing a referential token ("What does IT mean to
 * endure to the end?") is classified as a generic-context follow-up
 * whenever any prior question exists, genericContext becomes true,
 * the reviewed bank is never consulted, and the question falls to
 * the research Worker (a generated answer, or the fail-closed
 * "unable to check our approved study sources" message). Fresh
 * single-question sessions are unaffected, which is why every
 * one-question census missed it (diagnosis:
 * fcfix2/endure-pill-diagnosis, Jeff black-box reproduction
 * J-2026-10-25-096).
 *
 * Fix under test: when genericContext is true, askV3 first matches
 * the reviewed bank against the visitor's ORIGINAL wording and
 * returns an actual bank serve (never a suggestion set). Genuinely
 * elliptical follow-ups, whose own wording the bank does not serve,
 * keep the contextual flow unchanged.
 *
 * This harness runs the real composed Ask chain in a vm page
 * context (site-common.js, reviewed-ask-knowledge.js, the shipped
 * bank data / matcher / guards / lane, the scripture library, and
 * study-intelligence-v3.js driving window.sendMessage), in two
 * worlds: the candidate bytes, and the layer's BEFORE bytes
 * reconstructed from the successor manifest spans. It proves:
 *
 * - With history: all 13 referential-token bank canonicals from the
 *   diagnosis verdict sweep serve their bank records through askV3
 *   on the original wording, with zero research Worker calls.
 * - Wyatt's path: the faith-during-trials starter serves its bank
 *   record, renders its follow-up chips, and clicking the endure
 *   chip submits through window.sendMessage and serves the endure
 *   record in full, with zero Worker calls on the chip ask.
 * - Ellipsis controls: three genuinely elliptical follow-ups after
 *   a Joseph Smith question produce exactly the pre-fix outcome
 *   (same class, same answer, same Worker call count, no bank
 *   force-match) in the candidate and BEFORE worlds.
 * - No-history controls: fresh single-question serves of the 13
 *   canonicals are unchanged (same bank record, zero Worker calls)
 *   in both worlds.
 * - A non-bank question with history still reaches the research
 *   leg exactly as before.
 * - Ordinary nonreferential bank canonicals with history serve
 *   identically in both worlds (controls), and unrecognized
 *   questions with history reach research identically.
 *
 * Acceptance evidence (A-2026-10-25-PHONE-FAILURE-ACCEPTANCE-01):
 * every attempt emits one ATTEMPT JSON line as it runs, before its
 * assertions, recording the original wording, the resolver's
 * resolved wording and decision, the prior-history state, the
 * chosen dispatch branch, the Worker call count, and the full
 * actual output, so failed and partial attempts stay in the log.
 * Bank serves are proven to make zero research requests through the
 * instrumented fetch stub in this harness: these are nonbillable
 * tests, and no live paid-model call is made. Where a bank serve is
 * claimed, the complete answer text and the complete source-link
 * destination set are compared, not prefixes. Device limit: this
 * harness is a vm composed-chain test, not an Android device; the
 * visitor-side device evidence is Jeff's black-box reproduction
 * and the post-merge live census under real-visitor conditions.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
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
    remove() {
        if (this.parent) this.parent._nodes = this.parent._nodes.filter(c => c !== this);
        this.parent = null; this.isConnected = false;
    }
    contains(node) {
        if (node === this) return true;
        return this._nodes.some(c => c.nodeType === 1 && c.contains(node));
    }
    addEventListener(name, cb) { this.listeners[name] = cb; }
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

/* ---------------- BEFORE bytes from the successor manifest ---------------- */
const manifest = JSON.parse(read('docs/bank-context-bypass-successor/manifest.json'));
const candidateBuf = fs.readFileSync(path.join(root, 'study-intelligence-v3.js'));
const candidateV3 = candidateBuf.toString('utf8');
const span = manifest.files['study-intelligence-v3.js'].spans[0];
assert.equal(span.previous_b64, '', 'the registered span must be a pure insertion');
/* Span coordinates are byte offsets in the manifest (the successor
 * module operates on raw bytes), so reconstruction is on Buffers. */
const beforeBuf = Buffer.concat([candidateBuf.subarray(0, span.start), candidateBuf.subarray(span.end)]);
const beforeV3 = beforeBuf.toString('utf8');
assert.equal(crypto.createHash('sha256').update(beforeBuf).digest('hex'),
    manifest.files['study-intelligence-v3.js'].before_sha256,
    'reconstructed BEFORE bytes must hash to the manifest predecessor');
assert.equal(crypto.createHash('sha256').update(candidateBuf).digest('hex'),
    manifest.files['study-intelligence-v3.js'].after_sha256,
    'candidate bytes must hash to the manifest candidate');

/* ---------------- world construction ---------------- */
function verifiedResponse() {
    return {
        ok: true,
        async json() {
            return {
                choices: [{ message: { content: 'RESEARCHED VERIFIED ANSWER' } }],
                focuschrist_sources: [{ text: 'Official source', url: 'https://www.churchofjesuschrist.org/study/scriptures' }],
                focuschrist_source_integrity_verified: true,
                focuschrist_gateway_mode: 'retrieval-researched-and-verified',
                focuschrist_source_policy: '2026-09-03.16',
            };
        },
    };
}
function makeWorld(v3Source, label) {
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
    sandbox.crypto = crypto.webcrypto;
    sandbox.addEventListener = function () {};
    let fetchCalls = 0;
    sandbox.fetch = async function () { fetchCalls += 1; return verifiedResponse(); };
    sandbox.module = { exports: {} };
    vm.createContext(sandbox);
    const run = (code, name) => vm.runInContext(code, sandbox, { filename: name });
    run(read('site-common.js'), 'site-common.js');
    run(read('reviewed-ask-knowledge.js'), 'reviewed-ask-knowledge.js');
    run(read('answer-bank-data.js'), 'answer-bank-data.js');
    run(read('answer-bank-matcher.js'), 'answer-bank-matcher.js');
    run(read('answer-bank-guards.js'), 'answer-bank-guards.js');
    run(read('answer-bank-lane.js'), 'answer-bank-lane.js');
    assert.ok(sandbox.FocusChristAnswerBankLane, label + ': the bank lane must load');
    run(read('scripture-library.js'), 'scripture-library.js');
    const factory = sandbox.module.exports;
    assert.equal(typeof factory, 'function', label + ': scripture library factory must export');
    const library = factory(JSON.parse(read('scripture-data/catalog.json')),
        async url => new Response(fs.readFileSync(path.join(root, url))));
    sandbox.focusChristScriptureLibrary = library;
    sandbox.focusChristScriptureReady = Promise.resolve(library);
    const renderedCalls = [];
    sandbox.addMessage = function (text, isUser, sources, extra) {
        const node = new FakeNode('div');
        node.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
        node.textContent = text;
        box.appendChild(node);
        renderedCalls.push({ text, isUser, sources, extra, node });
        return node;
    };
    sandbox.containsInappropriate = () => false;
    run(v3Source, 'study-intelligence-v3.js');
    assert.equal(typeof sandbox.sendMessage, 'function', label + ': v3 must own window.sendMessage');
    assert.equal(typeof sandbox.focusChristStudyAskV3, 'function', label + ': v3 must expose askV3');
    const world = {
        label, sandbox, box, userInput, renderedCalls,
        records: sandbox.FocusChristAnswerBankData.records,
        fetchCalls: () => fetchCalls,
        reset() {
            box.children.slice().forEach(n => n.remove());
            sandbox.conversationHistory.length = 0;
            renderedCalls.length = 0;
            fetchCalls = 0;
        },
        seedHistory(priorQuestion) {
            sandbox.conversationHistory.push({ role: 'user', content: priorQuestion });
            sandbox.conversationHistory.push({ role: 'assistant', content: 'Prior answer.' });
        },
        async askV3(question) {
            const before = fetchCalls;
            const result = await sandbox.focusChristStudyAskV3(question, '');
            return { result, fetchDelta: fetchCalls - before };
        },
        /* One acceptance attempt: probe the resolver with the same
         * history askV3 will see, run askV3, and emit the evidence
         * line BEFORE any assertion can stop the run. */
        async attempt(question) {
            const history = sandbox.conversationHistory.slice(-10)
                .filter(i => i && (i.role === 'user' || i.role === 'assistant') && i.content)
                .map(i => ({ role: i.role, content: i.content }));
            let resolver = null;
            const registry = sandbox.focusChristReviewedKnowledge;
            if (registry && typeof registry.resolveFollowup === 'function') {
                const r = registry.resolveFollowup(question, { profile: 'ask', history });
                resolver = {
                    resolved: r.resolved === true,
                    genericContext: r.genericContext === true,
                    entryId: r.entryId || null,
                    resolvedWording: r.query || question,
                };
            }
            const outcome = await this.askV3(question);
            const r = outcome.result || {};
            let branch;
            if (r.bankLocal === true && r.bankRecordId) branch = resolver && resolver.genericContext ? 'bank-original-wording-prematch' : 'bank';
            else if (r.reviewedLocal === true) branch = 'reviewed-local';
            else if (r.clarification === true) branch = 'clarification';
            else if (outcome.fetchDelta > 0) branch = 'research-worker';
            else branch = 'local-other';
            const evidence = {
                world: label, question, priorHistory: history, resolver, branch,
                fetchDelta: outcome.fetchDelta, bankRecordId: r.bankRecordId || null,
                sources: (r.sources || []).map(s => s && s.url).filter(Boolean),
                answer: r.answer || '',
            };
            console.log('ATTEMPT ' + JSON.stringify(evidence));
            return { outcome, evidence };
        },
        async send(question) {
            userInput.value = question;
            await sandbox.sendMessage();
            const bots = renderedCalls.filter(c => !c.isUser);
            return bots[bots.length - 1];
        },
    };
    return world;
}
function classify(outcome) {
    const r = outcome.result || {};
    if (r.bankLocal === true && r.bankRecordId) return 'bank:' + r.bankRecordId;
    if (r.reviewedLocal === true) return 'reviewed:' + (r.contextEntryId || r.localMatch || '');
    if (r.clarification === true) return 'clarification';
    if (outcome.fetchDelta > 0) return 'research';
    return 'other:' + String(r.answer || '').slice(0, 40);
}

/* The 13 referential-token canonicals from the diagnosis verdict
 * sweep, each with the prior question the sweep used. */
const JESUS_STARTER = 'Who is Jesus Christ, and why is He central to Latter-day Saint belief?';
const FAITH_PRIOR = 'How can faith in Jesus Christ help during difficult times?';
const CANONICALS = [
    ['What does it mean to endure to the end?', FAITH_PRIOR],
    ['Is there archaeological evidence for the Book of Mormon?', JESUS_STARTER],
    ['Why does God allow suffering and evil if He loves us?', JESUS_STARTER],
    ['What does it mean to pray in the name of Jesus Christ?', JESUS_STARTER],
    ['What does "as far as it is translated correctly" mean?', JESUS_STARTER],
    ['What is the Light of Christ, and how is it different?', JESUS_STARTER],
    ['Why was there a priesthood restriction for Black members, and when did it end?', JESUS_STARTER],
    ["Where do I find this week's Come, Follow Me lesson?", JESUS_STARTER],
    ['What does it mean to let your light shine?', JESUS_STARTER],
    ['Why did the pioneers travel west, and what was their journey like?', JESUS_STARTER],
    ['How did the risen Jesus appear to His disciples by the Sea of Tiberias?', JESUS_STARTER],
    ['How did Jesus teach His followers to love and serve one another?', JESUS_STARTER],
    ['What does it mean to follow Jesus Christ?', JESUS_STARTER],
];
const ELLIPSIS = ['What did he do next?', 'Why did that happen?', 'And what about his family?'];

(async () => {
    const cand = makeWorld(candidateV3, 'candidate');
    const before = makeWorld(beforeV3, 'before');
    const byQuestion = new Map(cand.records.map(r => [r.question, r]));
    for (const [q] of CANONICALS) assert.ok(byQuestion.has(q), 'canonical must be a shipped bank record: ' + q);
    const expectedUrls = record => [...(record.sources_site || []), ...(record.sources_church || [])]
        .map(s => s.url).sort();
    const assertFullServe = (world, outcome, evidence, record, label) => {
        assert.equal(outcome.result.bankLocal, true, label + ' must bank-serve: ' + record.question);
        assert.equal(outcome.result.bankRecordId, record.id, label + ' record: ' + record.question);
        assert.equal(outcome.result.answer, record.answer, label + ' full answer identity: ' + record.question);
        assert.deepEqual([...evidence.sources].sort(), expectedUrls(record),
            label + ' source-link destinations: ' + record.question);
        assert.equal(outcome.fetchDelta, 0, label + ' must make zero Worker calls: ' + record.question);
    };

    /* ---------- no-history controls: both worlds serve the 13 ---------- */
    for (const world of [cand, before]) {
        for (const [q] of CANONICALS) {
            world.reset();
            const { outcome, evidence } = await world.attempt(q);
            assertFullServe(world, outcome, evidence, byQuestion.get(q), world.label + ' no-history');
        }
    }
    console.log('PASS no-history: 13/13 canonicals serve their bank records in both worlds, zero Worker calls');

    /* ---------- with history (typed): BEFORE bypasses, candidate serves ---------- */
    let beforeBypassed = 0;
    for (const [q, prior] of CANONICALS) {
        before.reset();
        before.seedHistory(prior);
        const { outcome: bOutcome, evidence: bEvidence } = await before.attempt(q);
        assert.equal(bEvidence.resolver && bEvidence.resolver.genericContext, true,
            'before world resolver must classify generic-context for: ' + q);
        assert.notEqual(bOutcome.result.bankRecordId, byQuestion.get(q).id,
            'before world must reproduce the bypass for: ' + q);
        beforeBypassed += 1;
        cand.reset();
        cand.seedHistory(prior);
        const { outcome, evidence } = await cand.attempt(q);
        assert.equal(evidence.branch, 'bank-original-wording-prematch',
            'candidate must take the original-wording prematch branch for: ' + q);
        assertFullServe(cand, outcome, evidence, byQuestion.get(q), 'candidate with-history');
    }
    /* The endure canonical also flips under the Jesus starter prior
     * (second sweep row for the same canonical). */
    cand.reset();
    cand.seedHistory(JESUS_STARTER);
    const { outcome: endureAlt, evidence: endureAltEv } =
        await cand.attempt('What does it mean to endure to the end?');
    assert.equal(endureAltEv.branch, 'bank-original-wording-prematch', 'endure alt-prior branch');
    assertFullServe(cand, endureAlt, endureAltEv,
        byQuestion.get('What does it mean to endure to the end?'), 'candidate endure alt-prior');
    console.log(`PASS with-history typed: before world bypassed ${beforeBypassed}/13; candidate serves 13/13 bank records, zero Worker calls`);

    /* ---------- Wyatt's path: starter serve, chips, chip click ---------- */
    cand.reset();
    const endureRecord = byQuestion.get('What does it mean to endure to the end?');
    const lane = cand.sandbox.FocusChristAnswerBankLane;
    const hostRecord = cand.records.find(r =>
        JSON.parse(JSON.stringify(lane.followUpChips(r.id))).some(c => c.record_id === endureRecord.id));
    assert.ok(hostRecord, 'a bank record must carry the endure chip');
    const firstBot = await cand.send(hostRecord.question);
    assert.ok(firstBot, 'the starter ask must render an answer');
    assert.equal(firstBot.extra && firstBot.extra.bankRecordId, hostRecord.id,
        'the starter ask must be a bank serve of the chip host record');
    assert.equal(firstBot.text, hostRecord.answer, 'the starter serve must render its pinned answer in full');
    assert.deepEqual([...(firstBot.sources || [])].map(s => s && s.url).filter(Boolean).sort(),
        expectedUrls(hostRecord), 'the starter serve source-link destinations must be complete');
    const groups = findByClass(firstBot.node, 'ask-followup-chips');
    assert.equal(groups.length, 1, 'the starter serve must render exactly one follow-up chip group');
    const chipButton = groups[0].children.find(b => b.textContent === endureRecord.question);
    assert.ok(chipButton, 'the endure chip must render under the starter answer');
    const fetchBeforeChip = cand.fetchCalls();
    const botsBeforeChip = cand.renderedCalls.filter(c => !c.isUser).length;
    chipButton.listeners.click();
    let chipBot = null;
    for (let i = 0; i < 300 && !chipBot; i++) {
        const bots = cand.renderedCalls.filter(c => !c.isUser);
        if (bots.length > botsBeforeChip) chipBot = bots[bots.length - 1];
        else await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.ok(chipBot, 'the chip click must render a new answer through the send path');
    /* Emit the chip attempt's evidence before its assertions. */
    const chipHistory = cand.sandbox.conversationHistory.slice(-10)
        .filter(i => i && i.content).map(i => ({ role: i.role, content: i.content }));
    const chipResolverRaw = cand.sandbox.focusChristReviewedKnowledge.resolveFollowup(
        endureRecord.question, { profile: 'ask', history: chipHistory.slice(0, -2) });
    console.log('ATTEMPT ' + JSON.stringify({
        world: 'candidate', via: 'sendMessage-chip-click', question: endureRecord.question,
        priorHistory: chipHistory.slice(0, -2),
        resolver: {
            resolved: chipResolverRaw.resolved === true,
            genericContext: chipResolverRaw.genericContext === true,
            entryId: chipResolverRaw.entryId || null,
            resolvedWording: chipResolverRaw.query || endureRecord.question,
        },
        branch: chipBot.extra && chipBot.extra.bankRecordId === endureRecord.id
            ? 'bank-original-wording-prematch' : 'other',
        fetchDelta: cand.fetchCalls() - fetchBeforeChip,
        bankRecordId: chipBot.extra && chipBot.extra.bankRecordId || null,
        sources: (chipBot.sources || []).map(s => s && s.url).filter(Boolean),
        answer: chipBot.text,
    }));
    assert.equal(chipBot.extra && chipBot.extra.bankRecordId, endureRecord.id,
        'the chip click must bank-serve the endure record (marker)');
    assert.equal(chipBot.text, endureRecord.answer,
        'the chip click must render the endure record answer in full, exactly');
    assert.deepEqual([...(chipBot.sources || [])].map(s => s && s.url).filter(Boolean).sort(),
        expectedUrls(endureRecord), 'the chip serve source-link destinations must be complete');
    assert.equal(cand.fetchCalls(), fetchBeforeChip, 'the chip ask must make zero Worker calls');
    /* Follow-up behavior of the chip serve itself: if the endure
     * record carries chips, its serve renders them under it. */
    const endureChips = JSON.parse(JSON.stringify(lane.followUpChips(endureRecord.id)));
    const chipBotGroups = findByClass(chipBot.node, 'ask-followup-chips');
    if (endureChips.length) {
        assert.equal(chipBotGroups.length, 1, 'the chip serve must render its own follow-up chips');
        assert.equal(chipBotGroups[0].getAttribute('data-followup-for'), endureRecord.id,
            'the chip serve follow-up group must name the endure record');
    } else {
        assert.equal(chipBotGroups.length, 0, 'the chip serve renders no chips when its record carries none');
    }
    console.log('PASS chip path: ' + hostRecord.id + ' serve renders the endure chip; the click serves '
        + endureRecord.id + ' in full through window.sendMessage, zero Worker calls');

    /* ---------- ellipsis controls: candidate identical to BEFORE ---------- */
    for (const q of ELLIPSIS) {
        const outcomes = {};
        for (const world of [cand, before]) {
            world.reset();
            world.seedHistory('Tell me about Joseph Smith.');
            outcomes[world.label] = (await world.attempt(q)).outcome;
        }
        const c = outcomes.candidate, b = outcomes.before;
        assert.notEqual(c.result.bankLocal, true, 'ellipsis must not be bank force-matched: ' + q);
        assert.equal(classify(c), classify(b), 'ellipsis class must match pre-fix: ' + q);
        assert.equal(c.result.answer, b.result.answer, 'ellipsis answer must match pre-fix: ' + q);
        assert.equal(c.fetchDelta, b.fetchDelta, 'ellipsis Worker calls must match pre-fix: ' + q);
        console.log('PASS ellipsis: "' + q + '" -> ' + classify(c) + ' (identical pre-fix and candidate)');
    }

    /* ---------- non-bank / unrecognized questions with history reach research ---------- */
    for (const q of ['How do I change a bicycle tire?', 'What is the capital of Norway?']) {
        const outcomes = {};
        for (const world of [cand, before]) {
            world.reset();
            world.seedHistory(JESUS_STARTER);
            outcomes[world.label] = (await world.attempt(q)).outcome;
        }
        const c = outcomes.candidate, b = outcomes.before;
        assert.notEqual(c.result.bankLocal, true, 'non-bank question must not bank-serve: ' + q);
        assert.equal(classify(c), 'research', 'non-bank question with history must reach the research leg: ' + q);
        assert.equal(classify(c), classify(b), 'non-bank class must match pre-fix: ' + q);
        assert.equal(c.result.answer, b.result.answer, 'non-bank answer must match pre-fix: ' + q);
        assert.equal(c.fetchDelta, b.fetchDelta, 'non-bank Worker calls must match pre-fix: ' + q);
        console.log('PASS non-bank: "' + q + '" with history reaches the research leg exactly as pre-fix ('
            + c.fetchDelta + ' Worker call)');
    }

    /* ---------- ordinary nonreferential controls with history ---------- */
    for (const q of ['What is the Atonement of Jesus Christ?', 'What is the plan of salvation?',
        'What is faith in Jesus Christ?']) {
        const record = byQuestion.get(q);
        assert.ok(record, 'control must be a shipped bank record: ' + q);
        const seen = {};
        for (const world of [cand, before]) {
            world.reset();
            world.seedHistory(JESUS_STARTER);
            const { outcome, evidence } = await world.attempt(q);
            assertFullServe(world, outcome, evidence, record, world.label + ' nonreferential control');
            seen[world.label] = outcome.result.answer;
        }
        assert.equal(seen.candidate, seen.before, 'control answer must be identical across worlds: ' + q);
        console.log('PASS nonreferential control: "' + q + '" serves ' + record.id + ' with history in both worlds');
    }

    console.log('PASS: bank context bypass runtime QA — 13 referential-token canonicals serve with history (typed and chip paths), ellipsis and non-bank flows unchanged, no-history serves unchanged.');
})().catch(error => { console.error(error); process.exitCode = 1; });
