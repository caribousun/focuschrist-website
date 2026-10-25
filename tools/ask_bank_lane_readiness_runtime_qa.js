/* Lane readiness wait on the inline bank serve (bank-serve
 * decoupling successor amendment, 2026-10-25).
 *
 * Defect 2 (fcfix2/endure-pill-diagnosis): the Ask page's bank
 * scripts are deferred, and answer-bank-data.js alone is about
 * 800 KB. A visitor on a slow connection who types and submits in
 * the first seconds reached ask.html's inline controller while
 * window.FocusChristAnswerBankLane was still unset, and the
 * controller fell through to the legacy askAI stub, whose verdict
 * ("I couldn't find a supported answer...") is false for bank
 * questions. The instrumented failing attempt recorded
 * lanePresent=false and bankDataPresent=false at submit; the
 * failure reproduced under Slow 4G throttling in two independent
 * probes (diagnostician 1 of 3 immediate, Jeff pooled 5 of 10).
 *
 * The amendment: inside the decoupling layer's existing ask.html
 * span, when the lane is absent at submit the inline controller
 * polls for it, bounded at 10 seconds, before any outcome; a
 * superseded submit renders nothing further; if the lane never
 * arrives it renders the site's existing SOURCE_UNAVAILABLE
 * temporary message and never runs the legacy lookup, so an
 * unasked bank is not converted into a proven miss.
 *
 * This harness builds the page in jsdom with the real ask.html and
 * the real bank scripts (the chips harness composition), but
 * installs the bank block on a timer the test controls, so the
 * lane's state at submit is exact, and records one ATTEMPT line
 * per submit before asserting:
 *
 * - delayed lane + bank question: the submit waits and then serves
 *   the bank record (on pre-amendment bytes this same procedure
 *   renders the false boundary verdict at once).
 * - ready lane + bank question: unchanged immediate serve.
 * - delayed lane + genuinely unrecognized question: after
 *   readiness the legacy lookup runs exactly once and decides;
 *   the temporary message is not substituted for its outcome.
 * - lane never arrives: the honest temporary message renders, the
 *   legacy lookup never runs, zero fetch calls.
 * - repeated submits during the wait: the second submit supersedes
 *   the first; exactly one answer renders, for the second
 *   question.
 *
 * Every condition also asserts zero fetch calls: no path here may
 * reach the research Worker as a substitute for waiting.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const ENDURE_QUESTION = 'What does it mean to endure to the end?';
const ATONEMENT_QUESTION = 'What is the Atonement of Jesus Christ?';
const MISS_QUESTION = 'How do I change a bicycle tire?';
const UNAVAILABLE_TEXT = 'I\u2019m unable to check our approved study sources right now. Please try again in a moment.';

function inlineScriptOfAskPage(html) {
    const marker = html.indexOf('    function toggleMenu()');
    assert(marker > 0, 'ask.html inline script marker must resolve');
    const tagStart = html.lastIndexOf('<script>', marker);
    const codeStart = html.indexOf('\n', tagStart) + 1;
    const codeEnd = html.indexOf('</script>', marker);
    const code = html.slice(codeStart, codeEnd);
    assert(code.includes('async function sendMessage('), 'inline slice must carry the inline controller');
    assert(code.includes('function addMessage('), 'inline slice must carry addMessage');
    return code;
}

function installBank(window) {
    const run = code => window.eval(code);
    run(read('answer-bank-data.js'));
    run(read('answer-bank-matcher.js'));
    run(read('answer-bank-guards.js'));
    run(read('answer-bank-lane.js'));
    assert.ok(window.FocusChristAnswerBankLane && typeof window.FocusChristAnswerBankLane.answer === 'function',
        'the bank lane must be installed by installBank');
}

async function buildPage() {
    const html = read('ask.html');
    const dom = new JSDOM(html, {
        url: 'https://focuschrist.com/ask.html',
        runScripts: 'outside-only',
        pretendToBeVisual: true,
    });
    const { window } = dom;
    window.HTMLElement.prototype.scrollIntoView = function () {};
    if (typeof window.IntersectionObserver !== 'function') {
        window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
    }
    if (typeof window.ResizeObserver !== 'function') {
        window.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
    }
    let fetchCalls = 0;
    window.fetch = () => {
        fetchCalls += 1;
        return Promise.reject(new Error('network is disabled in this harness'));
    };
    const run = code => window.eval(code);

    // site-common.js with its DOMContentLoaded init swallowed, as in
    // the chips harness; the display gate is installed explicitly
    // below. reviewed-ask-knowledge.js is a small early script and
    // is present from the start; the bank block (data, matcher,
    // guards, lane) is what a slow connection delays, and the test
    // installs it on its own schedule via installBank().
    const doc = window.document;
    const realDocAdd = doc.addEventListener.bind(doc);
    doc.addEventListener = (type, ...rest) => {
        if (type !== 'DOMContentLoaded') return realDocAdd(type, ...rest);
    };
    run(read('site-common.js'));
    doc.addEventListener = realDocAdd;
    run(read('reviewed-ask-knowledge.js'));

    const createScriptureLibrary = require(path.join(root, 'scripture-library.js'));
    const library = createScriptureLibrary(
        JSON.parse(read('scripture-data/catalog.json')),
        async url => ({ json: async () => JSON.parse(fs.readFileSync(path.join(root, new URL(url, 'https://focuschrist.com').pathname.slice(1)), 'utf8')) }));
    window.focusChristScriptureReady = Promise.resolve(library);

    run(inlineScriptOfAskPage(html));

    const siteCommon = read('site-common.js');
    const pattern = siteCommon.match(/    const SCRIPTURE_CITATION_PATTERN = [^\n]+/)[0];
    const extract = siteCommon.slice(
        siteCommon.indexOf('    function extractScriptureCitations('),
        siteCommon.indexOf('    function withoutOutputPersonNameScriptureCollisions('));
    const gate = siteCommon.slice(
        siteCommon.indexOf('    window.focusChristVerifyScriptureAnswer ='),
        siteCommon.indexOf('    function loadStudyJourney('));
    assert(gate.includes('function installScriptureDisplayGate()'), 'production gate extraction must resolve');
    assert(gate.includes('function isPinnedReviewedBankServe('), 'gate extraction must include the reviewed-bank exemption');
    run(pattern + '\n' + extract + '\n' + gate + '\ninstallScriptureDisplayGate();');

    // Count legacy lookups: the readiness paths are told apart by
    // whether the legacy lookup ever ran.
    let findAnswerCalls = 0;
    const realFindAnswer = window.findAnswer;
    assert.equal(typeof realFindAnswer, 'function', 'the inline legacy lookup must be reachable');
    window.findAnswer = function (q) { findAnswerCalls += 1; return realFindAnswer(q); };

    return { dom, window, fetchCalls: () => fetchCalls, findAnswerCalls: () => findAnswerCalls };
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function waitFor(window, condition, label) {
    for (let i = 0; i < 1500; i++) {
        if (condition()) return;
        await sleep(10);
    }
    throw new Error('timed out waiting for: ' + label);
}

function settled(window) {
    return waitFor(window,
        () => !window.document.querySelector('[data-scripture-pending]'),
        'display gate to settle');
}

function botTexts(window) {
    return Array.from(window.document.querySelectorAll('.bot-message')).map(n => n.textContent);
}

function record(attempt) {
    console.log('ATTEMPT ' + JSON.stringify(attempt));
}

(async () => {
    /* ---- Condition 1: delayed lane, bank question -> wait, then serve ---- */
    {
        const { window, fetchCalls, findAnswerCalls } = await buildPage();
        const doc = window.document;
        assert.equal(window.FocusChristAnswerBankLane, undefined,
            'the lane must be absent at build in the delayed conditions');
        doc.getElementById('userInput').value = ENDURE_QUESTION;
        const started = Date.now();
        const pending = window.sendMessage();
        const installed = new Promise(resolve => setTimeout(() => { installBank(window); resolve(); }, 700));
        await sleep(300);
        const midWait = {
            loadingPresent: !!doc.querySelector('.loading'),
            userMessagePresent: Array.from(doc.querySelectorAll('.user-message'))
                .some(n => n.textContent.includes(ENDURE_QUESTION)),
            botAnswers: botTexts(window).length,
        };
        await pending;
        await installed;
        await settled(window);
        const lane = window.FocusChristAnswerBankLane;
        const serve = lane.answer({ question_text: ENDURE_QUESTION, profile: 'ask', history: [] });
        assert.equal(serve.status, 'serve', 'the endure question must be a bank serve');
        const texts = botTexts(window);
        const attempt = {
            condition: 'delayed-lane-bank-question', question: ENDURE_QUESTION,
            laneStateAtSubmit: 'absent', laneInstalledMsAfterSubmit: 700,
            elapsedMs: Date.now() - started, midWait,
            outcome: texts.some(t => t.includes(serve.answer.slice(0, 60))) ? 'bank-serve' : 'other',
            botAnswers: texts.length, findAnswerCalls: findAnswerCalls(), fetchCalls: fetchCalls(),
        };
        record(attempt);
        assert.equal(attempt.outcome, 'bank-serve', 'the waited submit must serve the bank record');
        assert.equal(midWait.loadingPresent, true, 'the loading indicator stays up through the wait');
        assert.equal(midWait.userMessagePresent, true, 'the visitor question stays on screen through the wait');
        assert.equal(midWait.botAnswers, 0, 'no outcome is produced before readiness');
        assert.equal(texts.length, 1, 'exactly one answer renders');
        assert.ok(!texts[0].includes(UNAVAILABLE_TEXT), 'a served submit never shows the temporary message');
        assert.ok(!texts[0].includes(window.focusChristSourceIntegrity.fallback),
            'a served submit never shows the boundary verdict');
        assert.equal(findAnswerCalls(), 0, 'a bank serve never reaches the legacy lookup');
        assert.equal(fetchCalls(), 0, 'a bank serve must make zero fetch calls');
        assert.equal(doc.getElementById('sendBtn').disabled, false, 'the Ask button is re-enabled');
        assert.equal(doc.querySelector('.loading'), null, 'the loading indicator is removed');
        window.close();
    }

    /* ---- Condition 2: ready lane, bank question -> immediate serve ---- */
    {
        const { window, fetchCalls, findAnswerCalls } = await buildPage();
        const doc = window.document;
        installBank(window);
        const lane = window.FocusChristAnswerBankLane;
        const serve = lane.answer({ question_text: ENDURE_QUESTION, profile: 'ask', history: [] });
        assert.equal(serve.status, 'serve');
        doc.getElementById('userInput').value = ENDURE_QUESTION;
        const started = Date.now();
        await window.sendMessage();
        await settled(window);
        const elapsedMs = Date.now() - started;
        const texts = botTexts(window);
        const attempt = {
            condition: 'ready-lane-bank-question', question: ENDURE_QUESTION,
            laneStateAtSubmit: 'ready', elapsedMs,
            outcome: texts.some(t => t.includes(serve.answer.slice(0, 60))) ? 'bank-serve' : 'other',
            botAnswers: texts.length, findAnswerCalls: findAnswerCalls(), fetchCalls: fetchCalls(),
        };
        record(attempt);
        assert.equal(attempt.outcome, 'bank-serve', 'a ready-lane submit serves as before');
        assert.ok(elapsedMs < 5000, 'a ready-lane submit does not wait');
        assert.equal(findAnswerCalls(), 0);
        assert.equal(fetchCalls(), 0);
        window.close();
    }

    /* ---- Condition 3: delayed lane, genuine miss -> legacy decides ---- */
    {
        const { window, fetchCalls, findAnswerCalls } = await buildPage();
        const doc = window.document;
        doc.getElementById('userInput').value = MISS_QUESTION;
        const started = Date.now();
        const pending = window.sendMessage();
        const installed = new Promise(resolve => setTimeout(() => { installBank(window); resolve(); }, 700));
        await pending;
        await installed;
        await settled(window);
        const texts = botTexts(window);
        const attempt = {
            condition: 'delayed-lane-genuine-miss', question: MISS_QUESTION,
            laneStateAtSubmit: 'absent', laneInstalledMsAfterSubmit: 700,
            elapsedMs: Date.now() - started,
            outcome: texts.length ? 'legacy-outcome' : 'none',
            botAnswers: texts.length, findAnswerCalls: findAnswerCalls(), fetchCalls: fetchCalls(),
        };
        record(attempt);
        assert.equal(findAnswerCalls(), 1, 'after readiness a genuine miss reaches the legacy lookup exactly once');
        assert.equal(texts.length, 1, 'the miss still produces its answer');
        assert.ok(!texts[0].includes(UNAVAILABLE_TEXT),
            'the temporary message is not substituted for a genuine miss outcome');
        assert.equal(fetchCalls(), 0, 'the legacy stub path makes zero fetch calls');
        window.close();
    }

    /* ---- Condition 4: lane never arrives -> honest temporary state ---- */
    {
        const { window, fetchCalls, findAnswerCalls } = await buildPage();
        const doc = window.document;
        doc.getElementById('userInput').value = ENDURE_QUESTION;
        const started = Date.now();
        await window.sendMessage();
        await settled(window);
        const elapsedMs = Date.now() - started;
        const texts = botTexts(window);
        const attempt = {
            condition: 'lane-never-arrives', question: ENDURE_QUESTION,
            laneStateAtSubmit: 'absent', laneInstalledMsAfterSubmit: null,
            elapsedMs,
            outcome: texts.some(t => t.includes(UNAVAILABLE_TEXT)) ? 'temporary-unavailable' : 'other',
            botAnswers: texts.length, findAnswerCalls: findAnswerCalls(), fetchCalls: fetchCalls(),
        };
        record(attempt);
        assert.equal(attempt.outcome, 'temporary-unavailable',
            'readiness failure renders the existing temporary message');
        assert.ok(elapsedMs >= 9000 && elapsedMs < 15000,
            'the wait is bounded at about 10 seconds, elapsed ' + elapsedMs);
        assert.equal(texts.length, 1, 'exactly one answer renders');
        assert.ok(!texts[0].includes(window.focusChristSourceIntegrity.fallback),
            'the false boundary verdict is never shown for an unasked bank');
        assert.equal(findAnswerCalls(), 0, 'the legacy lookup never runs on the readiness-failure path');
        assert.equal(fetchCalls(), 0, 'no research fallthrough substitutes for waiting');
        assert.equal(doc.getElementById('sendBtn').disabled, false, 'the Ask button is re-enabled');
        assert.equal(doc.querySelector('.loading'), null, 'the loading indicator is removed');
        window.close();
    }

    /* ---- Condition 5: repeated submits during the wait ---- */
    {
        const { window, fetchCalls, findAnswerCalls } = await buildPage();
        const doc = window.document;
        doc.getElementById('userInput').value = ENDURE_QUESTION;
        const first = window.sendMessage();
        await sleep(300);
        doc.getElementById('userInput').value = ATONEMENT_QUESTION;
        const second = window.sendMessage();
        const installed = new Promise(resolve => setTimeout(() => { installBank(window); resolve(); }, 600));
        await Promise.all([first, second]);
        await installed;
        await settled(window);
        const lane = window.FocusChristAnswerBankLane;
        const endureServe = lane.answer({ question_text: ENDURE_QUESTION, profile: 'ask', history: [] });
        const atonementServe = lane.answer({ question_text: ATONEMENT_QUESTION, profile: 'ask', history: [] });
        assert.equal(endureServe.status, 'serve');
        assert.equal(atonementServe.status, 'serve');
        const texts = botTexts(window);
        const attempt = {
            condition: 'repeated-submits-during-wait',
            questions: [ENDURE_QUESTION, ATONEMENT_QUESTION],
            laneStateAtSubmit: 'absent', laneInstalledMsAfterFirstSubmit: 900,
            outcome: texts.some(t => t.includes(atonementServe.answer.slice(0, 60))) ? 'second-question-serve' : 'other',
            botAnswers: texts.length, findAnswerCalls: findAnswerCalls(), fetchCalls: fetchCalls(),
        };
        record(attempt);
        assert.equal(texts.length, 1, 'exactly one answer renders across both submits');
        assert.equal(attempt.outcome, 'second-question-serve',
            'the surviving answer is the newest submit\u2019s bank serve');
        assert.ok(!texts.some(t => t.includes(endureServe.answer.slice(0, 60))),
            'the superseded submit renders no answer');
        assert.equal(findAnswerCalls(), 0);
        assert.equal(fetchCalls(), 0);
        assert.equal(doc.getElementById('sendBtn').disabled, false, 'the Ask button is re-enabled');
        window.close();
    }

    console.log('PASS: a bank question submitted before the lane arrives waits and serves; a ready lane serves unchanged; a genuine miss reaches the legacy lookup after readiness; readiness failure renders the existing temporary message without the legacy lookup; repeated submits during the wait produce exactly one answer, the newest question\u2019s.');
})().catch(error => { console.error(error); process.exit(1); });
