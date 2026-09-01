const fs = require('fs');
const vm = require('vm');

global.window = {
    location: { pathname: '/ask.html' },
    setTimeout,
    clearTimeout,
    focusChristSourceIntegrity: null,
};
const dom = {
    userInput: { value: '', disabled: false, focus() {} },
    sendBtn: { disabled: false, textContent: 'Ask' },
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
        return { className: '', textContent: '', isConnected: false, setAttribute() {}, remove() { this.isConnected = false; } };
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
    return {
        ok: true,
        async json() {
            return {
                choices: [{ message: { content: 'RESEARCHED VERIFIED ANSWER' } }],
                focuschrist_sources: [{ text: 'Official source', url: 'https://www.churchofjesuschrist.org/study/scriptures' }],
                focuschrist_source_integrity_verified: true,
                focuschrist_gateway_mode: 'retrieval-researched-and-verified',
                focuschrist_source_policy: '2026-09-01.1',
            };
        },
    };
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
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 1, 'painting query must use verified research');
    result = await window.focusChristStudyAskV3('how is color used in website design', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 2, 'design query must use verified research');

    for (const query of ['what does D&C 18:15 say?', 'what does Genesis say about creation?', 'what does Isaiah teach about color?', 'what does Matthew say about prayer?', 'what does Mark say about baptism?', 'what does Words of Mormon teach?', 'what does Joseph Smith—Matthew say?']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.answer === 'RESEARCHED VERIFIED ANSWER', 'source query did not return verified research: ' + query);
        assert(result.sourceIntegrityStatus === 'retrieval-researched-and-verified', 'source query lacks verified status: ' + query);
        assert(result.sources.some((source) => source.url.includes('churchofjesuschrist.org')), 'source query omitted official evidence: ' + query);
    }
    assert(fetchCalls === 9, 'each unreviewed question must call the research gateway once');

    result = await window.askAI('what does D&C 18:15 say?', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 10,
        'window.askAI must preserve verified retrieval');

    dom.userInput.value = 'what does Mark say about baptism?';
    await window.sendMessage();
    assert(renderedMessages.length === 2, 'window.sendMessage must render one user message and one verified response');
    assert(renderedMessages[0].isUser === true && renderedMessages[0].text === 'what does Mark say about baptism?',
        'window.sendMessage must preserve the submitted question');
    assert(renderedMessages[1].isUser === false && renderedMessages[1].text === 'RESEARCHED VERIFIED ANSWER',
        'window.sendMessage must render the verified answer');
    assert(renderedMessages[1].sources.some((source) => source.url.includes('churchofjesuschrist.org')),
        'window.sendMessage must render verified sources');
    assert(fetchCalls === 11, 'window.sendMessage must call the research gateway');
    assert(dom.userInput.disabled === false && dom.sendBtn.disabled === false && dom.sendBtn.textContent === 'Ask',
        'window.sendMessage must restore Ask controls');
    console.log('Study Intelligence v3 runtime QA PASS');
})().catch((error) => { console.error(error); process.exit(1); });
