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
global.sessionStorage = { setItem() {}, getItem() { return null; }, removeItem() {} };
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
vm.runInThisContext(fs.readFileSync('reviewed-ask-knowledge.js', 'utf8'), { filename: 'reviewed-ask-knowledge.js' });
let fetchCalls = 0;
const requestBodies = [];
let delayedAskResponse = null;
let forceWorkerRateLimit = false;
function verifiedResponse() {
    return {
        ok: true,
        async json() {
            return {
                choices: [{ message: { content: 'RESEARCHED VERIFIED ANSWER' } }],
                focuschrist_sources: [{ text: 'Official source', url: 'https://www.churchofjesuschrist.org/study/scriptures' }],
                focuschrist_source_integrity_verified: true,
                focuschrist_gateway_mode: 'retrieval-researched-and-verified',
                focuschrist_source_policy: '2026-09-01.15',
            };
        },
    };
}
global.fetch = async (_url, options) => {
    fetchCalls += 1;
    const body = JSON.parse(options.body);
    requestBodies.push(body);
    if (forceWorkerRateLimit) {
        return {
            ok: true,
            async json() {
                return {
                    choices: [{ message: { content: 'RATE-LIMIT FALLBACK MUST NOT RENDER' } }],
                    focuschrist_sources: [],
                    focuschrist_source_integrity_verified: false,
                    focuschrist_gateway_mode: 'research-rate-limited',
                    focuschrist_source_policy: '2026-09-01.15'
                };
            }
        };
    }
    const isDelayed = body.messages.some((message) => String(message.content || '').includes('delayed Ask detail'));
    if (isDelayed) return new Promise((resolve) => { delayedAskResponse = () => resolve(verifiedResponse()); });
    return verifiedResponse();
};
vm.runInThisContext(fs.readFileSync('study-intelligence-v3.js', 'utf8'), { filename: 'study-intelligence-v3.js' });

const renderedMessages = [];
window.addMessage = (text, isUser, sources) => renderedMessages.push({ text, isUser, sources });
window.containsInappropriate = () => false;

function assert(condition, message) { if (!condition) throw new Error(message); }
(async () => {
    assert(typeof window.askAI === 'function', 'v3 must own window.askAI');
    assert(typeof window.sendMessage === 'function', 'v3 must own window.sendMessage on Ask');

    let result = await window.focusChristStudyAskV3('Why is the sky blue?', '');
    assert(result.answer.includes('atmosphere') && result.reviewedLocal === true && fetchCalls === 0,
        'reviewed general sky answer must bypass the gateway');
    result = await window.focusChristStudyAskV3('how is color used in scripture', '');
    assert(result.answer === 'VERIFIED COLOR ANSWER' && fetchCalls === 0, 'exact verified intent must bypass generation');
    result = await window.focusChristStudyAskV3('how are colors used in scripture', '');
    assert(result.answer === 'VERIFIED COLOR ANSWER' && fetchCalls === 0, 'plural verified intent must bypass generation');
    result = await window.focusChristStudyAskV3('what year was joseph killed', '');
    assert(result.answer.includes('1844') && result.localMatch === 'joseph-smith-death-1844' && fetchCalls === 0,
        'reviewed Joseph Smith death intent must answer during research rate limits');
    result = await window.focusChristStudyAskV3('when did Joseph Smith die', '');
    assert(result.answer.includes('1844') && fetchCalls === 0,
        'explicit Joseph Smith death phrasing must match the reviewed answer');
    result = await window.focusChristStudyAskV3('when did Joseph die', '');
    assert(result.answer.includes('1844') && fetchCalls === 0,
        'bare Joseph death phrasing on the LDS Ask page must use the qualified reviewed answer');

    result = await window.focusChristStudyAskV3('Who is Jesus Christ, and why is He central to Latter-day Saint belief?', '');
    assert(result.reviewedLocal === true && result.answer.split(/\s+/).length >= 70 && result.sources.length >= 1 && fetchCalls === 0,
        'visible Jesus Christ Ask card must return a substantive reviewed answer with zero Worker calls');
    const questionContracts = JSON.parse(fs.readFileSync('ask-question-contracts.json', 'utf8'));
    for (const starterQuestion of questionContracts.contracts.ask_starters.values) {
        const starterResult = await window.focusChristStudyAskV3(starterQuestion, '');
        assert(starterResult.reviewedLocal === true && starterResult.answer.split(/\s+/).length >= 70
            && starterResult.sources.length >= 1,
        'visible Ask starter failed its final-owner contract: ' + starterQuestion);
    }
    assert(fetchCalls === 0, 'all visible Ask starters must make zero Worker calls');

    conversationHistory.length = 0;
    renderedMessages.length = 0;
    const beforeFollowupFlow = fetchCalls;
    dom.userInput.value = 'What date did Joseph Smith die?';
    await window.sendMessage();
    dom.userInput.value = 'Do we know the time he died';
    await window.sendMessage();
    const followupAnswer = renderedMessages.at(-1);
    assert(fetchCalls === beforeFollowupFlow, 'reviewed Joseph Smith conversation and follow-up must make zero Worker calls');
    assert(followupAnswer && /about or shortly after 5:00 p\.m\./.test(followupAnswer.text),
        'real Ask follow-up did not render the reviewed qualified time');
    assert(conversationHistory.some((item) => item.role === 'user' && item.content === 'Do we know the time he died'),
        'Ask must preserve the visitor\'s original follow-up wording in conversation history');

    const beforeEllipticalFollowup = fetchCalls;
    result = await window.focusChristStudyAskV3('What time?', '');
    assert(fetchCalls === beforeEllipticalFollowup && result.reviewedLocal === true
        && result.contextResolved === true && result.answer.includes('5:00 p.m.'),
        'a permitted subjectless follow-up must resolve Joseph Smith without a Worker call');

    const beforeCompetingFollowup = fetchCalls;
    dom.userInput.value = 'What date did Abraham Lincoln die?';
    await window.sendMessage();
    dom.userInput.value = 'Do we know the time he died';
    await window.sendMessage();
    assert(fetchCalls === beforeCompetingFollowup && renderedMessages.at(-1).text.includes('7:22 a.m.'),
        'the reviewed Lincoln main and follow-up answers must use the zero-Worker lane');
    result = await window.focusChristStudyAskV3('What time?', '');
    assert(fetchCalls === beforeCompetingFollowup && result.reviewedLocal === true
        && result.contextResolved === true
        && result.contextEntryId === 'general-abraham-lincoln-death-1865'
        && result.answer.includes('7:22 a.m.') && !result.answer.includes('10:00 p.m.'),
        'reviewed Ask context must preserve Lincoln through a chained ellipsis without hallucinating a time');

    window.focusChristCancelAskRequests();
    const beforeResetFollowup = fetchCalls;
    result = await window.focusChristStudyAskV3('Do we know the time he died', '');
    assert(fetchCalls === beforeResetFollowup + 1 && result.reviewedLocal !== true,
        'Ask reset must prevent stale Joseph Smith context inheritance');

    for (const query of ['what year was Joseph Stalin killed', 'was Joseph of Egypt murdered', 'Joseph Kennedy death']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.answer === 'RESEARCHED VERIFIED ANSWER',
            'a competing Joseph identity must not receive the Joseph Smith answer: ' + query);
    }
    for (const query of ['What did Alma Mahler compose?', 'Who was Moroni Olsen?', 'who was alma mahler?', 'who was moroni olsen?', 'Tell me about Alma Mahler.', 'tell me about alma mahler']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && result.profile === 'general-knowledge'
            && requestBodies.at(-1).focuschrist_profile === 'general-knowledge',
        'an ordinary person whose given name matches scripture must remain general knowledge: ' + query);
    }
    assert(fetchCalls === 10, 'generic chain, competing identities, and scripture-name people must use the correct gateway lane');

    result = await window.focusChristStudyAskV3('how is color used in painting', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 11, 'painting query must use verified research');
    result = await window.focusChristStudyAskV3('how is color used in website design', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 12, 'design query must use verified research');
    result = await window.focusChristStudyAskV3('what makes a family business successful', '');
    assert(result.profile === 'general-knowledge' && fetchCalls === 13,
        'generic family language must not inherit the faith or Pioneer source lane');
    assert(requestBodies[12].focuschrist_profile === 'general-knowledge',
        'Ask must send the gateway its narrowed general profile');
    result = await window.focusChristStudyAskV3('who was Joseph Smith', '');
    assert(result.profile === 'faith-study' && fetchCalls === 14,
        'an explicit Joseph Smith question must retain the faith source lane');
    assert(requestBodies[13].focuschrist_profile === 'faith-study',
        'explicit faith intent must remain available to the server-owned source policy');
    assert(requestBodies.every((body) => body.focuschrist_page === 'ask'),
        'Ask requests must identify the Ask surface explicitly');

    for (const query of ['what does D&C 18:15 say?', 'what is Genesis about?', 'tell me about Genesis', 'Tell me about Alma the Younger.', 'what does genesis creation account teach?', 'what does alma faith sermon teach?', 'What did Alma and Amulek say?', 'what did alma and amulek say?', 'what does Genesis say about creation?', 'what does Isaiah teach about color?', 'what does Matthew say about prayer?', 'what does Mark say about baptism?', 'what does Words of Mormon teach?', 'what does Joseph Smith—Matthew say?']) {
        result = await window.focusChristStudyAskV3(query, '');
        assert(result.answer === 'RESEARCHED VERIFIED ANSWER', 'source query did not return verified research: ' + query);
        assert(result.profile === 'faith-study' && requestBodies.at(-1).focuschrist_profile === 'faith-study',
            'bare and explicit scripture-book questions must retain the faith source lane: ' + query);
        assert(result.sourceIntegrityStatus === 'retrieval-researched-and-verified', 'source query lacks verified status: ' + query);
        assert(result.sources.some((source) => source.url.includes('churchofjesuschrist.org')), 'source query omitted official evidence: ' + query);
    }
    assert(fetchCalls === 28, 'each unreviewed question must call the research gateway once');

    result = await window.askAI('what does D&C 18:15 say?', '');
    assert(result.answer === 'RESEARCHED VERIFIED ANSWER' && fetchCalls === 29,
        'window.askAI must preserve verified retrieval');

    renderedMessages.length = 0;
    dom.userInput.value = 'what does Mark say about baptism?';
    await window.sendMessage();
    assert(renderedMessages.length === 2, 'window.sendMessage must render one user message and one verified response');
    assert(renderedMessages[0].isUser === true && renderedMessages[0].text === 'what does Mark say about baptism?',
        'window.sendMessage must preserve the submitted question');
    assert(renderedMessages[1].isUser === false && renderedMessages[1].text === 'RESEARCHED VERIFIED ANSWER',
        'window.sendMessage must render the verified answer');
    assert(renderedMessages[1].sources.some((source) => source.url.includes('churchofjesuschrist.org')),
        'window.sendMessage must render verified sources');
    assert(fetchCalls === 30, 'window.sendMessage must call the research gateway');
    assert(dom.userInput.disabled === false && dom.sendBtn.disabled === false && dom.sendBtn.textContent === 'Ask',
        'window.sendMessage must restore Ask controls');

    const topicButton = {
        textContent: 'Why is the sky blue?',
        getAttribute(name) { return name === 'data-ask-topic' ? 'Why is the sky blue?' : ''; },
        addEventListener(name, callback) { if (name === 'click') this.clickHandler = callback; }
    };
    const originalQuerySelectorAll = document.querySelectorAll;
    document.querySelectorAll = (selector) => selector === '[data-ask-topic]' ? [topicButton] : [];
    vm.runInThisContext(fs.readFileSync('ask-experience.js', 'utf8'), { filename: 'ask-experience.js' });
    window.focusChristInitAskTopicCards();
    const callsBeforeTopic = fetchCalls;
    const messagesBeforeTopic = renderedMessages.length;
    topicButton.clickHandler();
    await Promise.resolve();
    await Promise.resolve();
    assert(fetchCalls === callsBeforeTopic,
        'real main Ask topic-button event must retain the reviewed-local zero-Worker lane');
    assert(renderedMessages.length === messagesBeforeTopic + 2 && renderedMessages.at(-1).text.includes('atmosphere'),
        'real main Ask topic-button event must route through the v3 primary composer');
    document.querySelectorAll = originalQuerySelectorAll;

    const starterButton = {
        textContent: 'Who is Jesus Christ?',
        getAttribute(name) {
            return name === 'data-question'
                ? 'Who is Jesus Christ, and why is He central to Latter-day Saint belief?'
                : '';
        },
        addEventListener(name, callback) { if (name === 'click') this.clickHandler = callback; }
    };
    document.querySelectorAll = (selector) => selector === '[data-ask-starter]' ? [starterButton] : [];
    window.focusChristInitAskStarters();
    const callsBeforeStarter = fetchCalls;
    const messagesBeforeStarter = renderedMessages.length;
    starterButton.clickHandler();
    await Promise.resolve();
    await Promise.resolve();
    assert(fetchCalls === callsBeforeStarter,
        'real main Ask starter-card event must retain the reviewed-local zero-Worker lane');
    assert(renderedMessages.length === messagesBeforeStarter + 2
        && renderedMessages.at(-1).text.includes('Savior and Redeemer')
        && renderedMessages.at(-1).text.split(/\s+/).length >= 70,
        'real main Ask Jesus Christ starter-card event must render the substantive reviewed answer');
    document.querySelectorAll = originalQuerySelectorAll;

    window.focusChristCancelAskRequests();
    const beforeGenericJoseph = fetchCalls;
    forceWorkerRateLimit = true;
    dom.userInput.value = 'What date did Joseph Smith die?';
    await window.sendMessage();
    dom.userInput.value = 'How old was he?';
    await window.sendMessage();
    forceWorkerRateLimit = false;
    assert(fetchCalls === beforeGenericJoseph && renderedMessages.at(-1).text.includes('38 years old'),
        'Joseph age follow-up must remain available as a specific reviewed answer during Worker rate limits');

    window.focusChristCancelAskRequests();
    const beforeCarthage = fetchCalls;
    dom.userInput.value = 'What date did Joseph Smith die?';
    await window.sendMessage();
    dom.userInput.value = 'Why was he in Carthage Jail?';
    await window.sendMessage();
    assert(fetchCalls === beforeCarthage && renderedMessages.at(-1).text.includes('awaiting legal proceedings'),
        'Carthage Jail must resolve to its specific reviewed context without a Worker dependency');

    window.focusChristCancelAskRequests();
    const beforeExplicitLincoln = fetchCalls;
    dom.userInput.value = 'What date did Joseph Smith die?';
    await window.sendMessage();
    dom.userInput.value = 'Do we know what time he died, Abraham Lincoln?';
    await window.sendMessage();
    assert(fetchCalls === beforeExplicitLincoln
        && renderedMessages.at(-1).text.includes('7:22 a.m.')
        && !renderedMessages.at(-1).text.includes('5:00 p.m.'),
        'explicit Abraham Lincoln subject must switch from Joseph Smith to the reviewed zero-Worker answer');

    for (const topicQuestion of questionContracts.contracts.ask_topics.values) {
        const topicResult = await window.focusChristStudyAskV3(topicQuestion, '');
        assert(topicResult && String(topicResult.answer || '').trim()
            && !/cannot verify the specific source claim|please confirm the subject|could not complete/i.test(topicResult.answer),
        'visible Ask topic failed its final-owner answer contract: ' + topicQuestion);
    }

    renderedMessages.length = 0;
    dom.userInput.value = 'Tell me a delayed Ask detail';
    const pending = window.sendMessage();
    assert(typeof delayedAskResponse === 'function', 'delayed Ask request did not start');
    window.focusChristCancelAskRequests();
    assert(conversationHistory.length === 0, 'Ask reset must clear committed conversation state immediately');
    dom.userInput.disabled = false;
    dom.sendBtn.disabled = false;
    dom.sendBtn.textContent = 'Ask';
    delayedAskResponse();
    await pending;
    assert(renderedMessages.length === 1 && renderedMessages[0].isUser === true,
        'a response resolved after Ask reset must not render');
    assert(conversationHistory.length === 0, 'a stale Ask response must not repopulate reset conversation state');
    console.log('Study Intelligence v3 runtime QA PASS');
})().catch((error) => { console.error(error); process.exit(1); });
