const fs = require('fs');
const vm = require('vm');

function hasClass(item, name) {
    return String(item.className || '').split(/\s+/).includes(name);
}

function node() {
    const item = {
        className: '', textContent: '', style: {}, children: [], attributes: {}, isConnected: true,
        scrollTop: 0, scrollHeight: 100,
        classList: {
            add(...names) { item.className = Array.from(new Set(String(item.className).split(/\s+/).filter(Boolean).concat(names))).join(' '); },
            remove() {}, toggle() {}, contains(name) { return hasClass(item, name); }
        },
        appendChild(child) { this.children.push(child); child.parentNode = this; return child; },
        replaceChildren(...children) { this.children = children; children.forEach((child) => { child.parentNode = this; }); },
        setAttribute(name, value) { this.attributes[name] = String(value); },
        getAttribute(name) { return this.attributes[name] || null; },
        addEventListener() {}, remove() { this.isConnected = false; },
        getBoundingClientRect() { return { top: 40, height: 40 }; },
        scrollTo(options) { this.scrollTop = options && options.top || 0; },
        querySelector(selector) { return this.querySelectorAll(selector)[0] || null; },
        querySelectorAll(selector) {
            const className = selector.startsWith('.') ? selector.slice(1) : null;
            const attr = selector.match(/^\[([^\]]+)\]$/);
            const matches = [];
            function visit(child) {
                if (className && hasClass(child, className)) matches.push(child);
                if (attr && Object.prototype.hasOwnProperty.call(child.attributes || {}, attr[1])) matches.push(child);
                (child.children || []).forEach(visit);
            }
            this.children.forEach(visit);
            return matches;
        }
    };
    return item;
}

const input = Object.assign(node(), { value: '', disabled: false, placeholder: '', focus() {} });
const button = Object.assign(node(), { disabled: false, textContent: 'Ask History' });
const reset = Object.assign(node(), { disabled: false });
const status = node();
const box = node();
const elements = {
    historyQuestion: input,
    historyAskButton: button,
    historyResetButton: reset,
    historyStatus: status,
    historyChatBox: box
};

global.window = {
    location: { pathname: '/church-history.html', hash: '', href: 'https://focuschrist.com/church-history.html' },
    history: { pushState() {} },
    setTimeout, clearTimeout, scrollY: 0,
    scrollTo() {}, addEventListener() {},
    matchMedia() { return { matches: false }; },
    getComputedStyle() { return { position: 'static' }; }
};
global.document = {
    readyState: 'loading',
    getElementById(id) { return elements[id] || null; },
    createElement() { return node(); },
    querySelector() { return null; }, querySelectorAll() { return []; },
    addEventListener() {},
    documentElement: { toggleAttribute() {}, setAttribute() {} },
    head: { appendChild() {} }
};

vm.runInThisContext(fs.readFileSync('reviewed-ask-knowledge.js', 'utf8'), { filename: 'reviewed-ask-knowledge.js' });

let remoteCalls = 0;
let delayedHistoryResponse = null;
const remoteQuestions = [];
window.focusChristStudyAskV3 = async (question) => {
    remoteCalls += 1;
    remoteQuestions.push(String(question));
    if (String(question).includes('delayed history detail')) {
        return new Promise((resolve) => {
            delayedHistoryResponse = () => resolve({ answer: 'STALE REMOTE HISTORY ANSWER', sources: [] });
        });
    }
    return { answer: 'VERIFIED REMOTE HISTORY ANSWER', sources: [] };
};

vm.runInThisContext(fs.readFileSync('church-history-experience.js', 'utf8'), { filename: 'church-history-experience.js' });

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

(async () => {
    const discoveredQuestions = [...fs.readFileSync('church-history.html', 'utf8').matchAll(/data-history-question="([^"]+)"/g)]
        .map((match) => match[1]);
    assert(discoveredQuestions.length === 10,
        'Church History card count changed without a final-owner runtime contract');
    for (const question of discoveredQuestions) {
        const cardResult = await window.focusChristHistoryAsk(question);
        assert(cardResult && cardResult.answer.split(/\s+/).length >= 70,
            'Church History card did not return a substantive final-owner answer: ' + question);
        assert(Array.isArray(cardResult.sources) && cardResult.sources.some((source) =>
            source.url.includes('churchofjesuschrist.org')),
        'Church History card did not retain an official source: ' + question);
        assert(!/cannot verify the specific source claim|please confirm the subject|could not complete/i.test(cardResult.answer),
            'Church History card returned a known generic non-answer: ' + question);
    }
    assert(remoteCalls === 0, 'every visible Church History card must answer with zero Worker requests');

    let result = await window.focusChristHistoryAsk('When was the First Vision?');
    assert(result && result.answer.includes('1820'), 'First Vision reviewed answer must render 1820');
    assert(remoteCalls === 0, 'First Vision reviewed answer must make zero Worker requests');

    result = await window.focusChristHistoryAsk('When was the Church organized?');
    assert(result && result.answer.includes('April 6, 1830'), 'Church organization reviewed answer must render April 6, 1830');
    assert(remoteCalls === 0, 'Church organization reviewed answer must make zero Worker requests');

    result = await window.focusChristHistoryAsk('What year did the handcarts begin?');
    assert(result && result.answer.includes('1856'), 'Church History handcart question must share the reviewed 1856 answer');
    assert(remoteCalls === 0, 'Church History handcart reviewed answer must make zero Worker requests');

    result = await window.focusChristHistoryAsk('What date did Joseph Smith die?');
    assert(result && result.answer.includes('June 27, 1844'), 'Church History Joseph Smith date must use the reviewed answer');
    result = await window.focusChristHistoryAsk('Do we know the time he died');
    assert(result && result.contextResolved === true && result.answer.includes('5:00 p.m.'),
        'Church History Joseph Smith follow-up must resolve and answer the qualified time');
    result = await window.focusChristHistoryAsk('What time?');
    assert(result && result.contextResolved === true && result.answer.includes('5:00 p.m.'),
        'Church History chained subjectless follow-up must retain the Joseph Smith context receipt');
    assert(remoteCalls === 0, 'Church History reviewed follow-up must make zero Worker requests');

    result = await window.focusChristHistoryAsk('How old was he?');
    assert(remoteCalls === 0 && result && result.answer.includes('38 years old'),
        'Church History Joseph age follow-up must remain reviewed during Worker rate limits');

    window.focusChristResetHistoryAsk();
    await window.focusChristHistoryAsk('What date did Joseph Smith die?');
    result = await window.focusChristHistoryAsk('Why was he in Carthage Jail?');
    assert(remoteCalls === 0 && result && result.answer.includes('awaiting legal proceedings'),
        'Carthage Jail must remain a reviewed place inside Joseph context, not a competing person');

    window.focusChristResetHistoryAsk();
    await window.focusChristHistoryAsk('What date did Abraham Lincoln die?');
    await window.focusChristHistoryAsk('Do we know the time he died');
    assert(remoteCalls === 2,
        'Church History follow-up after an intervening person must not skip backward and inherit Joseph Smith');
    assert(remoteQuestions.at(-1).includes('Do we know the time he died')
        && remoteQuestions.at(-1).includes('What date did Abraham Lincoln die?')
        && !remoteQuestions.at(-1).includes('Joseph Smith'),
        'Church History remote follow-up must explicitly resolve the immediately preceding Lincoln subject');

    window.focusChristResetHistoryAsk();
    result = await window.focusChristHistoryAsk('Do we know the time he died');
    assert(remoteCalls === 3 && result === undefined,
        'Church History reset must prevent stale Joseph Smith context inheritance');

    result = await window.focusChristHistoryAsk('When was the First Vision movie released?');
    assert(remoteCalls === 4, 'First Vision movie negative control must use external research');
    assert(result === undefined, 'remote Church History controller should complete without exposing an unreviewed local receipt');

    const pending = window.focusChristHistoryAsk('Tell me a delayed history detail');
    await Promise.resolve();
    assert(typeof delayedHistoryResponse === 'function', 'delayed Church History request did not start');
    window.focusChristResetHistoryAsk();
    delayedHistoryResponse();
    await pending;
    const staleRendered = box.querySelectorAll('.fc-history-message-body').some((body) => body.textContent.includes('STALE REMOTE'));
    assert(!staleRendered, 'a response resolved after Church History reset must not render');

    assert(input.disabled === false && button.disabled === false && reset.disabled === false,
        'Church History controls must restore after local and remote answers');
    console.log('Church History Ask final-owner runtime QA PASS: reviewed facts made zero Worker requests; negative and stale-response controls passed');
})().catch((error) => { console.error(error); process.exit(1); });
