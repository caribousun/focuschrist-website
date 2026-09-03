const fs = require('fs');
const vm = require('vm');

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

global.window = {};
const source = fs.readFileSync('site-common.js', 'utf8');
const safetyOnly = source.slice(0, source.indexOf('    const OFFICIAL_RESOURCE_LINKS')) + '\n})();';
vm.runInThisContext(safetyOnly, { filename: 'site-common-question-safety.js' });

const safety = window.focusChristQuestionSafety;
assert(safety && typeof safety.evaluate === 'function', 'shared question-safety evaluator must be available');

for (const specimen of [
    'This is f.u.c.k.i.n.g ridiculous',
    'Can you provide pornography?',
    'Why are Catholics stupid?',
    'All Muslims are inferior',
    'Why are immigrants disgusting?',
    'Republicans are morons',
    'Democrats are trash'
]) {
    const result = safety.evaluate(specimen);
    assert(result.allowed === false && result.kind === 'respect-boundary',
        'profanity, explicit sexual content, and protected-group attacks must be blocked: ' + specimen);
    assert(result.response === safety.respectfulResponse,
        'blocked content must receive the approved respectful redirect');
    assert(!result.response.includes(specimen), 'the approved redirect must not echo blocked content');
}

for (const specimen of [
    'What do Latter-day Saints believe about religious freedom?',
    'What does the Church teach about political neutrality?',
    'How can Christians and Muslims show respect for one another?',
    'How did harmful political rhetoric affect immigrants historically?',
    'What does the Bible teach about chastity?',
    'How can I forgive someone who called my faith evil?'
]) {
    const result = safety.evaluate(specimen);
    assert(result.allowed === true,
        'respectful doctrine, history, and interfaith questions must remain answerable: ' + specimen);
}

for (const specimen of [
    'I am being sexually abused and need help',
    'Someone is threatening me and I may be in immediate danger'
]) {
    const result = safety.evaluate(specimen);
    assert(result.allowed === false && result.kind === 'urgent-safety'
        && result.response === safety.urgentSafetyResponse,
        'immediate abuse or danger disclosures must receive the urgent safety response');
}

const askHtml = fs.readFileSync('ask.html', 'utf8');
const pioneerHtml = fs.readFileSync('pioneers.html', 'utf8');
for (const [name, html] of [['Main Ask', askHtml], ['Pioneers', pioneerHtml]]) {
    assert(!/if\s*\(containsInappropriate\(q\)\)\s*\{\s*addMessage\(q,true\)/.test(html),
        name + ' legacy fallback must not echo prohibited input');
    assert(/focusChristQuestionSafety/.test(html) && /group&&attack/.test(html),
        name + ' legacy fallback must retain fail-closed profanity, sexual, and protected-group checks');
}
assert(!/console\.log\(['"]Calling askAI with:/.test(askHtml)
    && !/console\.log\(['"]askAI returned:/.test(askHtml),
    'Main Ask legacy fallback must not log raw questions or answers');

console.log('Question safety runtime QA PASS');
