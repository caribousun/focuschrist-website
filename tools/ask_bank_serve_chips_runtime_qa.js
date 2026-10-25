/* Follow-up chips on the inline bank serve (bank-serve decoupling
 * successor amendment, 2026-10-25).
 *
 * The Ask page has two submit controllers. study-intelligence-v3.js
 * replaces window.sendMessage once it loads, and its bank serves
 * render the served record's follow-up chips through its private
 * appendFollowUpChips. The inline controller in ask.html owns every
 * submit until then; since the decoupling fix it serves reviewed
 * bank answers itself, and before this amendment it rendered no
 * chips, so a bank serve's chips depended on which controller owned
 * the submit at the instant of the click (diagnosis:
 * 78 instrumented live probes separated perfectly on that flag).
 *
 * This harness exercises the shipped page both ways, in jsdom with
 * the real ask.html, the real bank scripts, and the display gate
 * extracted verbatim from site-common.js (the extraction pattern of
 * tools/answer_bank_display_gate_runtime_qa.js):
 *
 * - v3 blocked (its script never runs, the network-level block the
 *   diagnosis specifies): the inline controller owns the submit, and
 *   its bank serve must render the identical adjunct: the
 *   "Additional questions" heading as the group's sibling and the
 *   .ask-followup-chips group with data-followup-for for the served
 *   record, inside the served answer's message node (the display
 *   gate's child carry-over). Clicking the Atonement chip must
 *   submit and serve the Atonement record.
 * - v3 allowed: the v3 controller owns the submit, and exactly one
 *   chips group renders for the serve (the inline adjunct can never
 *   double-render, because it runs only on the inline controller's
 *   own serve, which returns before v3 can serve the same submit).
 *
 * Both serves must make zero fetch calls: a reviewed bank serve
 * never reaches the research Worker or the network.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const STARTER_QUESTION = 'Who is Jesus Christ, and why is He central to Latter-day Saint belief?';
const ATONEMENT_QUESTION = 'What is the Atonement of Jesus Christ?';

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

async function buildPage(withV3) {
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

    // site-common.js: swallow its DOMContentLoaded init (in production
    // that init is what installs the gate, after every deferred script
    // has run; here the gate is installed explicitly below, in the same
    // relative order). Its top level defines the question safety
    // evaluator the lane consults.
    const doc = window.document;
    const realDocAdd = doc.addEventListener.bind(doc);
    doc.addEventListener = (type, ...rest) => {
        if (type !== 'DOMContentLoaded') return realDocAdd(type, ...rest);
    };
    run(read('site-common.js'));
    doc.addEventListener = realDocAdd;

    run(read('reviewed-ask-knowledge.js'));
    run(read('answer-bank-data.js'));
    run(read('answer-bank-matcher.js'));
    run(read('answer-bank-guards.js'));
    run(read('answer-bank-lane.js'));

    // The real scripture library over the repo's own data, as in the
    // display-gate harness; bank serves return before consulting it.
    const createScriptureLibrary = require(path.join(root, 'scripture-library.js'));
    const library = createScriptureLibrary(
        JSON.parse(read('scripture-data/catalog.json')),
        async url => ({ json: async () => JSON.parse(fs.readFileSync(path.join(root, new URL(url, 'https://focuschrist.com').pathname.slice(1)), 'utf8')) }));
    window.focusChristScriptureReady = Promise.resolve(library);

    // The page's own inline script: addMessage and the inline
    // sendMessage controller.
    run(inlineScriptOfAskPage(html));

    // The shipped display gate, extracted verbatim from site-common.js
    // and installed over the page's addMessage.
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

    if (withV3) run(read('study-intelligence-v3.js'));
    return { dom, window, fetchCalls: () => fetchCalls };
}

async function waitFor(window, condition, label) {
    for (let i = 0; i < 500; i++) {
        if (condition()) return;
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    throw new Error('timed out waiting for: ' + label);
}

function settled(window) {
    return waitFor(window,
        () => !window.document.querySelector('[data-scripture-pending]'),
        'display gate to settle');
}

function assertChipsAdjunct(window, serve, expectedChips, label) {
    const doc = window.document;
    const groups = doc.querySelectorAll('.ask-followup-chips');
    assert.equal(groups.length, 1, label + ': exactly one follow-up chips group renders');
    const group = groups[0];
    assert.equal(group.getAttribute('data-followup-for'), serve.record_id,
        label + ': the group is bound to the served record');
    assert.equal(group.getAttribute('role'), 'group', label + ': group role');
    assert.equal(group.getAttribute('aria-label'), 'Follow-up questions', label + ': group aria-label');
    assert.ok(group.classList.contains('ask-clarification-options'), label + ': group carries the shared options class');
    const heading = group.previousElementSibling;
    assert.ok(heading && heading.classList.contains('ask-followup-chips-title'),
        label + ': the section heading renders as the group sibling');
    assert.ok(heading.classList.contains('sources-title'), label + ': the heading uses the page section-label treatment');
    assert.equal(heading.textContent, 'Additional questions', label + ': the heading text');
    const message = group.closest('.bot-message');
    assert.ok(message, label + ': the chips live inside the served answer message node');
    assert.ok(message.textContent.includes(serve.answer.slice(0, 60)),
        label + ': the answer text renders in the same message');
    assert.ok(message.querySelector('.sources'), label + ': the sources render in the same message');
    const buttons = Array.from(group.querySelectorAll('button.ask-followup-button'));
    // expectedChips is a window-realm array; normalize through this
    // realm's Array before the strict deep comparison.
    assert.deepEqual(buttons.map(b => b.textContent), Array.from(expectedChips, c => c.question),
        label + ': one button per curated chip, in lane order');
    buttons.forEach((button, index) => {
        assert.equal(button.type, 'button', label + ': chip is a button element');
        if (expectedChips[index].record_id) {
            assert.equal(button.getAttribute('data-followup-target'), expectedChips[index].record_id,
                label + ': chip carries its target record id');
        }
    });
    return group;
}

(async () => {
    /* ---- Condition 1: v3 blocked; the inline controller owns the submit ---- */
    {
        const { window, fetchCalls } = await buildPage(false);
        const doc = window.document;
        assert.equal(typeof window.focusChristStudyAskV3, 'undefined',
            'v3 must be absent when its script is blocked');
        const lane = window.FocusChristAnswerBankLane;
        assert.ok(lane && typeof lane.answer === 'function' && typeof lane.followUpChips === 'function',
            'the bank lane must be installed');
        const serve = lane.answer({ question_text: STARTER_QUESTION, profile: 'ask', history: [] });
        assert.equal(serve.status, 'serve', 'the starter question must be a bank serve');
        const expectedChips = lane.followUpChips(serve.record_id);
        assert.ok(expectedChips.length >= 3, 'the Jesus Christ record must carry its curated chips');

        doc.getElementById('userInput').value = STARTER_QUESTION;
        await window.sendMessage();
        await settled(window);
        assertChipsAdjunct(window, serve, expectedChips, 'inline serve');
        assert.equal(fetchCalls(), 0, 'a bank serve must make zero fetch calls');

        const atonementChip = expectedChips.find(chip => chip.question === ATONEMENT_QUESTION);
        assert.ok(atonementChip && atonementChip.record_id, 'the Atonement chip must be offered');
        const atonementServe = lane.answer({ question_text: ATONEMENT_QUESTION, profile: 'ask', history: [] });
        assert.equal(atonementServe.status, 'serve', 'the Atonement question must be a bank serve');
        assert.equal(atonementServe.record_id, atonementChip.record_id,
            'the chip target must be the record the follow-up serves');
        const group = doc.querySelector('.ask-followup-chips');
        const buttons = Array.from(group.querySelectorAll('button.ask-followup-button'));
        buttons[expectedChips.indexOf(atonementChip)].click();
        await waitFor(window, () => {
            const bots = Array.from(doc.querySelectorAll('.bot-message'));
            return bots.some(node => node.textContent.includes(atonementServe.answer.slice(0, 60)))
                && !doc.querySelector('[data-scripture-pending]');
        }, 'the chip click to serve the Atonement record');
        const followUpChips = lane.followUpChips(atonementServe.record_id);
        if (followUpChips.length) {
            assertChipsAdjunct(window, atonementServe, followUpChips, 'inline chip follow-up serve');
        } else {
            assert.equal(doc.querySelectorAll('.ask-followup-chips').length, 0,
                'a record without a curated list renders no chips on the follow-up serve either');
        }
        assert.equal(fetchCalls(), 0, 'the follow-up bank serve must make zero fetch calls');
        window.close();
    }

    /* ---- Condition 2: v3 allowed; the v3 controller owns the submit ---- */
    {
        const { window, fetchCalls } = await buildPage(true);
        const doc = window.document;
        assert.equal(typeof window.focusChristStudyAskV3, 'function',
            'v3 must be installed when its script loads');
        const lane = window.FocusChristAnswerBankLane;
        const serve = lane.answer({ question_text: STARTER_QUESTION, profile: 'ask', history: [] });
        assert.equal(serve.status, 'serve');
        const expectedChips = lane.followUpChips(serve.record_id);

        doc.getElementById('userInput').value = STARTER_QUESTION;
        await window.sendMessage();
        await settled(window);
        assertChipsAdjunct(window, serve, expectedChips, 'v3 serve');
        assert.equal(fetchCalls(), 0, 'a v3 bank serve must make zero fetch calls');
        window.close();
    }

    console.log('PASS: the inline bank serve renders the follow-up chips adjunct (heading, group, buttons), a chip click serves the follow-up record, and the v3-owned serve renders exactly one group.');
})().catch(error => { console.error(error); process.exit(1); });
