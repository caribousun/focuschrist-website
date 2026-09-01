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
    'joseph smith death': {
        verified: true,
        intent: [['joseph'], ['die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered']],
        intentTest(query) {
            const value = String(query || '').toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
            if (!/\b(?:die|died|death|killed|martyred|martyrdom|murdered)\b/.test(value)) return false;
            if (/\bjoseph\s+smith\b/.test(value) || /\bjoseph\s+the\s+prophet\b/.test(value)) return true;
            const bare = value.match(/\bjoseph(?:\s+([a-z'-]+))?/);
            if (!bare) return false;
            if (!bare[1]) return true;
            return ['was', 'is', 'did', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered', 'get', 'got', 'be'].includes(bare[1]);
        },
        answer: 'JOSEPH SMITH DIED IN 1844',
        sources: [{ text: 'Deaths of Joseph and Hyrum Smith', url: 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith' }],
    },
};

vm.runInThisContext(fs.readFileSync('site-common.js', 'utf8'), { filename: 'site-common.js' });
let fetchCalls = 0;
const requestBodies = [];
global.fetch = async (_url, options) => {
    fetchCalls += 1;
    requestBodies.push(JSON.parse(options.body));
    return {
        ok: true,
        async json() {
            return {
                choices: [{ message: { content: 'RESEARCHED VERIFIED ANSWER' } }],
                focuschrist_sources: [{ text: 'Official source', url: 'https://www.churchofjesuschrist.org/study/scriptures' }],
                focuschrist_source_integrity_verified: true,
                focuschrist_gateway_mode: 'retrieval-researched-and-verified',
                focuschrist_source_policy: '2026-09-01.8',
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
    result = await window.focusChristStudyAskV3('what year was joseph killed', '');
    assert(result.answer === 'JOSEPH SMITH DIED IN 1844' && fetchCalls === 0,
        'reviewed Joseph Smith death intent must answer during research rate limits');
    result = await window.focusChristStudyAskV3('when did Joseph Smith die', '');
    assert(result.answer === 'JOSEPH SMITH DIED IN 1844' && fetchCalls === 0,
        'explicit Joseph Smith death phrasing must match the reviewed answer');
    result = await window.focusChristStudyAskV3('when did Joseph die', '');
    assert(result.answer === 'JOSEPH SMITH DIED IN 1844' && fetchCalls === 0,
        'bare Joseph death phrasing on the LDS Ask page must use the qualified reviewed answer');

    for (const query of ['what year was Joseph Stalin killed', 'was Joseph of Egypt murdered', 'Joseph Kennedy death']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.answer === 'RESEARCHED VERIFIED ANSWER',
            'a competing Joseph identity must not receive the Joseph Smith answer: ' + query);
    }
    assert(fetchCalls === 3, 'competing Joseph identities must use the gateway instead of the local Joseph Smith answer');

    result = await window.focusChristStudyAskV3('how is color used in painting', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 4, 'painting query must use verified research');
    result = await window.focusChristStudyAskV3('how is color used in website design', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 5, 'design query must use verified research');
    result = await window.focusChristStudyAskV3('what makes a family business successful', '');
    assert(result.profile === 'general-knowledge' && fetchCalls === 6,
        'generic family language must not inherit the faith or Pioneer source lane');
    assert(requestBodies[5].focuschrist_profile === 'general-knowledge',
        'Ask must send the gateway its narrowed general profile');
    result = await window.focusChristStudyAskV3('who was Joseph Smith', '');
    assert(result.profile === 'faith-study' && fetchCalls === 7,
        'an explicit Joseph Smith question must retain the faith source lane');
    assert(requestBodies[6].focuschrist_profile === 'faith-study',
        'explicit faith intent must remain available to the server-owned source policy');
    assert(requestBodies.every((body) => body.focuschrist_page === 'ask'),
        'Ask requests must identify the Ask surface explicitly');

    for (const query of ['what does D&C 18:15 say?', 'what does Genesis say about creation?', 'what does Isaiah teach about color?', 'what does Matthew say about prayer?', 'what does Mark say about baptism?', 'what does Words of Mormon teach?', 'what does Joseph Smith—Matthew say?']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.answer === 'RESEARCHED VERIFIED ANSWER', 'source query did not return verified research: ' + query);
        assert(result.sourceIntegrityStatus === 'retrieval-researched-and-verified', 'source query lacks verified status: ' + query);
        assert(result.sources.some((source) => source.url.includes('churchofjesuschrist.org')), 'source query omitted official evidence: ' + query);
    }
    assert(fetchCalls === 14, 'each unreviewed question must call the research gateway once');

    result = await window.askAI('what does D&C 18:15 say?', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 15,
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
    assert(fetchCalls === 16, 'window.sendMessage must call the research gateway');
    assert(dom.userInput.disabled === false && dom.sendBtn.disabled === false && dom.sendBtn.textContent === 'Ask',
        'window.sendMessage must restore Ask controls');
    console.log('Study Intelligence v3 runtime QA PASS');
})().catch((error) => { console.error(error); process.exit(1); });
