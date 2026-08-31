const fs = require('fs');
const vm = require('vm');

global.window = {
    location: { pathname: '/ask.html' },
    setTimeout,
    clearTimeout,
    focusChristSourceIntegrity: null,
};
const dom = {
    userInput: {
        value: '',
        disabled: false,
        focus() {},
    },
    sendBtn: {
        disabled: false,
        textContent: 'Ask',
    },
    chatBox: {
        scrollTop: 0,
        scrollHeight: 1,
        querySelectorAll() { return []; },
        appendChild(node) { node.isConnected = true; this.lastChild = node; },
    },
};
global.document = {
    addEventListener() {},
    querySelector() { return null; },
    getElementById(id) { return dom[id] || null; },
    createElement() {
        return {
            className: '',
            textContent: '',
            isConnected: false,
            setAttribute() {},
            remove() { this.isConnected = false; },
        };
    },
    documentElement: { setAttribute() {} },
};
global.sessionStorage = { setItem() {}, getItem() { return null; } };
global.conversationHistory = [];
global.qaDatabase = {
    'color used in scripture': {
        verified: true,
        intent: [['color', 'colors'], ['scripture', 'scriptures', 'bible', 'canon']],
        answer: 'VERIFIED COLOR ANSWER',
        sources: [{ text: 'Isaiah 1:18', url: 'https://www.churchofjesuschrist.org/study/scriptures/ot/isa/1.18' }],
    },
};

vm.runInThisContext(fs.readFileSync('site-common.js', 'utf8'), { filename: 'site-common.js' });
let fetchCalls = 0;
global.fetch = async () => {
    fetchCalls += 1;
    return { ok: true, async json() { return { choices: [{ message: { content: 'GENERAL ANSWER' } }] }; } };
};
vm.runInThisContext(fs.readFileSync('study-intelligence-v3.js', 'utf8'), { filename: 'study-intelligence-v3.js' });

const renderedMessages = [];
window.addMessage = (text, isUser, sources) => renderedMessages.push({ text, isUser, sources });
window.containsInappropriate = () => false;

function assert(condition, message) { if (!condition) throw new Error(message); }
(async () => {
    assert(typeof window.askAI === 'function', 'v3 must own window.askAI');
    assert(typeof window.sendMessage === 'function', 'v3 must own window.sendMessage on Ask');

    let result = await window.focusChristStudyAskV3('how is color used in scripture', '');
    assert(result.answer === 'VERIFIED COLOR ANSWER' && fetchCalls === 0, 'exact verified intent must bypass generation');
    result = await window.focusChristStudyAskV3('how are colors used in scripture', '');
    assert(result.answer === 'VERIFIED COLOR ANSWER' && fetchCalls === 0, 'plural verified intent must bypass generation');
    result = await window.focusChristStudyAskV3('how is color used in painting', '');
    assert(result.answer !== 'VERIFIED COLOR ANSWER', 'painting query must not hit scripture answer');
    result = await window.focusChristStudyAskV3('how is color used in website design', '');
    assert(result.answer !== 'VERIFIED COLOR ANSWER', 'design query must not hit scripture answer');

    const before = fetchCalls;
    for (const query of ['what does D&C 18:15 say?', 'what does Genesis say about creation?', 'what does Isaiah teach about color?', 'what does Matthew say about prayer?', 'what does Mark say about baptism?', 'what does Words of Mormon teach?', 'what does Joseph Smith—Matthew say?']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.sourceIntegrityStatus === 'unreviewed-source-dependent-generation-blocked', 'source query did not fail closed: ' + query);
    }
    assert(fetchCalls === before, 'source-dependent queries must never call the model');

    result = await window.askAI('what does D&C 18:15 say?', '');
    assert(result.sourceIntegrityStatus === 'unreviewed-source-dependent-generation-blocked', 'window.askAI must preserve the v3 fail-closed gate');
    assert(fetchCalls === before, 'window.askAI source query must not call the model');

    dom.userInput.value = 'what does Mark say about baptism?';
    await window.sendMessage();
    assert(renderedMessages.length === 2, 'window.sendMessage must render one user message and one guarded response');
    assert(renderedMessages[0].isUser === true && renderedMessages[0].text === 'what does Mark say about baptism?', 'window.sendMessage must preserve the submitted question');
    assert(renderedMessages[1].isUser === false && /cannot verify/i.test(renderedMessages[1].text), 'window.sendMessage must render the fail-closed response');
    assert(fetchCalls === before, 'window.sendMessage source query must not call the model');
    assert(dom.userInput.disabled === false && dom.sendBtn.disabled === false && dom.sendBtn.textContent === 'Ask', 'window.sendMessage must restore Ask controls');
    console.log('Study Intelligence v3 runtime QA PASS');
})().catch((error) => { console.error(error); process.exit(1); });
