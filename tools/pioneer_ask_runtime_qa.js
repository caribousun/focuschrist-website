const fs = require('fs');
const vm = require('vm');

function node() {
    return {
        className: '', textContent: '', style: {}, dataset: {}, isConnected: true,
        offsetTop: 20, offsetLeft: 0,
        classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
        children: [],
        appendChild(child) { this.children.push(child); child.parentNode = this; return child; },
        attributes: {}, setAttribute(name, value) { this.attributes[name] = String(value); }, getAttribute(name) { return this.attributes[name] || null; }, listeners: {}, addEventListener(type, handler) { this.listeners[type] = handler; },
        querySelector() { return null; }, querySelectorAll() { return []; }, closest() { return null; },
        remove() { this.isConnected = false; },
        getBoundingClientRect() { return { top: 40, height: 40 }; },
        scrollTo() {}
    };
}

const input = Object.assign(node(), { value: '', disabled: false, focus() {} });
const button = Object.assign(node(), { disabled: false, textContent: 'Ask' });
const box = Object.assign(node(), {
    innerHTML: '', scrollTop: 0, scrollHeight: 100, offsetTop: 0,
    querySelector() { return null; }
});
const label = node();
const elements = { userInput: input, sendBtn: button, chatBox: box, pioneerComposerLabel: label };

global.window = {
    location: { pathname: '/pioneers.html', href: 'https://focuschrist.com/pioneers.html', origin: 'https://focuschrist.com', hash: '' },
    setTimeout, clearTimeout, scrollY: 0, innerHeight: 900,
    scrollTo() {}, addEventListener() {},
    matchMedia() { return { matches: false }; }
};
global.document = {
    getElementById(id) { return elements[id] || null; },
    createElement() { return node(); },
    createTextNode(text) { return { textContent: String(text) }; },
    querySelector() { return null; }, querySelectorAll() { return []; },
    addEventListener() {},
    body: { classList: { toggle() {} } },
    documentElement: { setAttribute() {} },
    head: { appendChild() {} }
};
global.sessionStorage = { setItem() {}, removeItem() {} };
global.conversationHistory = [];
global.URL = URL;

const siteCommonSource = fs.readFileSync('site-common.js', 'utf8');
vm.runInThisContext(
    siteCommonSource.slice(0, siteCommonSource.indexOf('    const OFFICIAL_RESOURCE_LINKS')) + '\n})();',
    { filename: 'site-common-question-safety.js' }
);
vm.runInThisContext(fs.readFileSync('reviewed-ask-knowledge.js', 'utf8'), { filename: 'reviewed-ask-knowledge.js' });

let fetchCalls = 0;
let delayedResponse = null;
let allowDisclosureRetry = false;
const requestBodies = [];
function verifiedResponse(verified = true) {
    return {
        ok: true,
        async json() {
            return {
                choices: [{ message: { content: 'VERIFIED REMOTE PIONEER ANSWER' } }],
                focuschrist_sources: [{ text: 'Official Church History', url: 'https://www.churchofjesuschrist.org/study/church-history' }],
                focuschrist_source_integrity_verified: verified,
                focuschrist_gateway_mode: 'retrieval-researched-and-verified',
                focuschrist_source_policy: '2026-09-03.16'
            };
        }
    };
}
global.fetch = async (_url, options) => {
    fetchCalls += 1;
    const body = JSON.parse(options.body);
    requestBodies.push(body);
    if (!allowDisclosureRetry && body.messages.some((message) => String(message.content || '').includes('FAIL DISCLOSURE'))) {
        throw new Error('simulated disclosure provider failure');
    }
    if (body.messages.some(message => String(message.content || '').includes('UNVERIFIED DISCLOSURE'))) return verifiedResponse(false);
    const isDelayed = body.messages.some((message) => String(message.content || '').includes('delayed pioneer detail'));
    if (isDelayed) return new Promise((resolve) => { delayedResponse = () => resolve(verifiedResponse()); });
    return verifiedResponse();
};
window.focusChristSourceIntegrity = {
    guardGeneratedAnswer(answer) { return { ok: true, answer }; }
};

vm.runInThisContext(fs.readFileSync('pioneer-experience.js', 'utf8'), { filename: 'pioneer-experience.js' });

const messages = [];
window.addMessage = (text, isUser, sources) => {
    messages.push({ text, isUser, sources: sources || [] });
    return node();
};

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

(async () => {
    input.value = 'What year did the handcarts begin?';
    await window.sendMessage();
    assert(fetchCalls === 0, 'owner handcart question must make zero Worker requests');
    assert(messages.length === 2 && messages[1].text.includes('1856'), 'owner handcart question must render the reviewed 1856 answer');
    assert(messages[1].sources.some((source) => source.url.includes('handcart-companies')), 'handcart answer must render its official source');
    assert(input.disabled === false && button.disabled === false, 'Pioneer controls must restore after local answer');

    messages.length = 0;
    await window.askTopic('Handcart Companies');
    assert(fetchCalls === 0, 'visible Handcart Companies topic must make zero Worker requests');
    assert(messages.length === 2 && messages[1].text.includes('1856') && messages[1].text.length >= 400,
        'visible Handcart Companies topic must render the substantive reviewed answer');

    messages.length = 0;
    await window.askTopic('Winter Quarters');
    assert(fetchCalls === 0 && messages[1].text.includes('Mud and sickness')
        && !/trans.?continental/i.test(messages[1].text)
        && messages[1].sources.some((source) => source.url.includes('/winter-quarters?')),
        'Winter Quarters topic must render reviewed history without a provider request or invented road project');

    messages.length = 0;
    await window.askTopic('Exodus from Nauvoo');
    assert(fetchCalls === 0 && messages[1].text.includes('1846'),
        'Pioneer topic button owner must use reviewed local knowledge before the Worker');

    messages.length = 0;
    await window.focusChristAnswerSelectedPioneer({
        name: 'TEST PIONEER',
        fullStory: 'TEST PIONEER\nA locally indexed, reviewed book entry.'
    }, 'Tell me about this person');
    assert(fetchCalls === 0 && messages.some((message) => message.text.includes('locally indexed')),
        'selected-person lane must render its exact local source without a Worker dependency');

    function disclosure(kind) {
        const response = Object.assign(node(), { innerHTML: '' });
        const date = Object.assign(node(), { textContent: '1846' });
        const desc = Object.assign(node(), { textContent: 'A reviewed displayed card.' });
        const expanded = new Set();
        const control = Object.assign(node(), {
            classList: {
                add(name) { expanded.add(name); }, remove(name) { expanded.delete(name); },
                toggle(name, on) { if (on) expanded.add(name); else expanded.delete(name); },
                contains(name) { return expanded.has(name); }
            },
            querySelector(selector) {
                if (selector === '.ai-response') return response;
                if (selector.includes('date')) return date;
                if (selector.includes('desc') || selector.includes('map-content p')) return desc;
                return null;
            }
        });
        response.closest = () => control;
        return { control, response, kind };
    }
    for (const specimen of [disclosure('Journey'), disclosure('Trail')]) {
        await window.focusChristRunPioneerDisclosure(specimen.control, 'FAIL DISCLOSURE', specimen.kind);
        assert(specimen.response.dataset.focuschristResearchState === 'error',
            specimen.kind + ' disclosure must expose a recoverable error after provider failure');
        assert(specimen.response.children.some((child) => child.textContent === 'Try again'),
            specimen.kind + ' disclosure must offer an explicit retry');
    }
    assert(fetchCalls === 2, 'Journey and Trail optional enhancements should each make exactly one Worker attempt');

    messages.length = 0;
    input.value = 'When did handcart racing begin?';
    await window.sendMessage();
    assert(fetchCalls === 3, 'handcart racing negative control must use research rather than the Pioneer local fact');
    assert(messages[1].text === 'VERIFIED REMOTE PIONEER ANSWER', 'negative control must render the researched answer');

    conversationHistory.length = 0;
    input.value = 'When did the Oregon Trail migration begin?';
    await window.sendMessage();
    input.value = 'What year did it begin?';
    await window.sendMessage();
    const pioneerFollowupQuery = requestBodies.at(-1).messages.at(-1).content;
    assert(pioneerFollowupQuery.includes('What year did it begin?')
        && pioneerFollowupQuery.includes('When did the Oregon Trail migration begin?'),
        'Pioneer remote follow-up must explicitly resolve the immediately preceding subject');

    for (const kind of ['Journey', 'Trail', 'Willie & Martin Companies']) {
        const specimen = disclosure(kind);
        Object.defineProperty(specimen.response, 'innerHTML', {
            set() { this.children = []; }, get() { return ''; }
        });
        const before = fetchCalls;
        const pendingDisclosure = window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        assert(specimen.response.getAttribute('aria-busy') === 'true'
            && specimen.response.children.some(child => child.textContent.includes('Researching this topic')),
            kind + ' first open must clearly identify pending research');
        await window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        await window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        assert(fetchCalls === before + 1, kind + ' reopening during research must not duplicate the request');
        await window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        assert(specimen.response.style.display === 'none', kind + ' must collapse while research is pending');
        delayedResponse();
        await pendingDisclosure;
        assert(specimen.response.style.display === 'none' && !specimen.control.classList.contains('expanded'),
            kind + ' a completed background response must not reopen a collapsed disclosure');
        await window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        const completed = specimen.response.children.slice();
        assert(completed.some(child => child.textContent === 'VERIFIED REMOTE PIONEER ANSWER'),
            kind + ' must render completed research');
        await window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        await window.focusChristRunPioneerDisclosure(specimen.control, 'delayed pioneer detail', kind);
        assert(specimen.response.dataset.focuschristLoaded === 'verified-research'
            && specimen.response.children.length === completed.length
            && specimen.response.children.every((child, index) => child === completed[index]),
            kind + ' reopening must preserve the complete researched answer and controls');
        assert(fetchCalls === before + 1, kind + ' reopening completed research must not request again');
    }

    const retrySpecimen = disclosure('Journey');
    Object.defineProperty(retrySpecimen.response, 'innerHTML', {
        set() { this.children = []; }, get() { return ''; }
    });
    await window.focusChristRunPioneerDisclosure(retrySpecimen.control, 'FAIL DISCLOSURE', 'Journey');
    const retryButton = retrySpecimen.response.children.find(child => child.textContent === 'Try again');
    assert(retryButton, 'failed research must expose a retry control');
    allowDisclosureRetry = true;
    const beforeRetry = fetchCalls;
    await retryButton.listeners.click({ stopPropagation() {} });
    assert(fetchCalls === beforeRetry + 1 && retrySpecimen.response.dataset.focuschristResearchState === 'complete',
        'explicit retry must recover to the verified answer');
    assert(!retrySpecimen.response.children.some(child => child.textContent.includes('Reviewed journey summary')),
        'retry must never replace research with duplicated card text');
    allowDisclosureRetry = false;

    const rejectedSpecimen = disclosure('Trail');
    await window.focusChristRunPioneerDisclosure(rejectedSpecimen.control, 'UNVERIFIED DISCLOSURE', 'Trail');
    assert(rejectedSpecimen.response.dataset.focuschristResearchState === 'error'
        && !rejectedSpecimen.response.children.some(child => child.textContent === 'VERIFIED REMOTE PIONEER ANSWER'),
        'an unverified server answer must never appear as completed research');

    const beforeDelayed = messages.length;
    input.value = 'Tell me a delayed pioneer detail';
    const pending = window.sendMessage();
    assert(typeof delayedResponse === 'function', 'delayed Pioneer request did not start');
    window.clearChat();
    assert(input.disabled === false && button.disabled === false && button.textContent === 'Ask',
        'Pioneer reset must restore controls while an older request is pending');
    assert(conversationHistory.length === 0, 'Pioneer reset must clear committed conversation state immediately');
    delayedResponse();
    await pending;
    assert(messages.length === beforeDelayed + 1, 'a response resolved after Pioneer reset must not render');
    assert(conversationHistory.length === 0, 'a stale Pioneer response must not repopulate reset conversation state');

    delayedResponse = null;
    const selectedPending = window.focusChristAnswerSelectedPioneer(
        { name: 'NO LOCAL STORY', fullStory: '' },
        'Tell me a delayed pioneer detail about this selected-person fallback'
    );
    assert(typeof delayedResponse === 'function', 'delayed selected-person fallback did not start');
    window.clearChat();
    const messagesAfterSelectedReset = messages.length;
    delayedResponse();
    await selectedPending;
    assert(messages.length === messagesAfterSelectedReset,
        'a selected-person fallback resolved after reset must not render');
    assert(conversationHistory.length === 0,
        'a stale selected-person fallback must not repopulate reset conversation state');

    const beforeGenericJoseph = fetchCalls;
    input.value = 'What date did Joseph Smith die?';
    await window.sendMessage();
    input.value = 'How old was he?';
    await window.sendMessage();
    assert(fetchCalls === beforeGenericJoseph && messages.at(-1).text.includes('38 years old'),
        'Pioneer Joseph age follow-up must remain reviewed and useful during Worker rate limits');

    const questionContracts = JSON.parse(fs.readFileSync('ask-question-contracts.json', 'utf8'));
    for (const topicQuestion of questionContracts.contracts.pioneer_topics.values) {
        window.clearChat();
        messages.length = 0;
        await window.askTopic(topicQuestion);
        assert(messages.length === 2 && String(messages[1].text || '').trim(),
            'visible Pioneer topic did not complete through its final runtime owner: ' + topicQuestion);
        assert(!/cannot verify the specific source claim|please confirm the subject|could not complete/i.test(messages[1].text),
            'visible Pioneer topic returned a known generic non-answer: ' + topicQuestion);
    }

    window.clearChat();
    messages.length = 0;
    const callsBeforeBoundary = fetchCalls;
    input.value = 'Why are Democrats morons?';
    await window.sendMessage();
    assert(fetchCalls === callsBeforeBoundary && conversationHistory.length === 0,
        'blocked Pioneer content must make zero Worker requests and create no history');
    assert(messages.length === 1 && messages[0].isUser === false
        && messages[0].text === window.focusChristQuestionSafety.respectfulResponse,
        'Pioneer must render only the approved respectful redirect');
    assert(input.disabled === false && button.disabled === false,
        'Pioneer boundary must leave controls ready');

    console.log('Pioneer Ask final-owner runtime QA PASS: local handcart answer made zero Worker requests; negative and stale-response controls passed');
})().catch((error) => { console.error(error); process.exit(1); });
