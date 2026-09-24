const fs = require('fs');
const vm = require('vm');

global.window = { location: { pathname: '/ask.html', hash: '', search: '' }, addEventListener() {} };
global.document = { readyState: 'loading', addEventListener() {} };
vm.runInThisContext(fs.readFileSync('site-common.js', 'utf8'), { filename: 'site-common.js' });

const integrity = window.focusChristSourceIntegrity;
const guard = integrity.guardGeneratedAnswer;
function assert(condition, message) { if (!condition) throw new Error(message); }

for (const safeMessage of [
    'focusChrist is here to help you learn of Jesus Christ and draw closer to Him. I couldn’t find a supported answer to this question in our study library or approved LDS sources. You’re welcome to ask about Jesus Christ, scripture, faith, or Church history.',
    'I’m unable to check our approved study sources right now. Please try again in a moment.',
    'Which Joseph do you mean? Please include the last name or a little more context.'
]) {
    const result = guard(safeMessage, { sourceDependent: true, serverVerified: false });
    assert(result.ok && result.answer === safeMessage, 'scope and outage messages must retain their distinct wording');
    assert(!guard(safeMessage + ' Genesis 99:99 proves this.', {
        sourceDependent: true, serverVerified: false
    }).ok, 'safe wording must not allow an appended unsupported claim');
}

assert(!guard('2 Corinthians 12:2 teaches this.', { trustedReferenceText: '1 Corinthians 12:2' }).ok,
    'numbered books must not collapse into the same citation');
assert(!guard('D&C 76:31-34 teaches colored degrees of glory.', {
    trustedReferenceText: 'D&C 76:31-34', sourceDependent: true
}).ok, 'same-reference text is not semantic claim verification');
assert(!guard('Latter-day Saint scripture assigns red to celestial glory.', { sourceDependent: true }).ok,
    'uncited canon attribution must fail closed');
assert(!guard('A generated pioneer overview.', { sourceDependent: true }).ok,
    'all unreviewed source-dependent generation must fail closed');
assert(guard('D&C 18:15 calls all people to repentance.', {
    trustedReferenceText: 'D&C 18:15 Official Gospel Library',
    sourceDependent: true,
    serverVerified: true
}).ok, 'server-verified retrieval answers must pass the browser guard');
assert(!guard('D&C 76 says red, white, and black lights represent three kingdoms.', {
    trustedReferenceText: 'D&C 76 Official Gospel Library',
    sourceDependent: true,
    serverVerified: true
}).ok, 'known false claims must remain blocked even with a server receipt');
assert(guard('Doctrine and Covenants 76 does not teach that red, white, and black lights represent three kingdoms.', {
    trustedReferenceText: 'Doctrine and Covenants 76 Official Gospel Library',
    sourceDependent: true,
    serverVerified: true
}).ok, 'a verified correction of the known false claim must remain answerable');
assert(guard('Rayleigh scattering makes the daytime sky appear blue.', { sourceDependent: false }).ok,
    'ordinary non-source-dependent answers should remain available');
assert(guard('Yes, we know the exact time of Abraham Lincoln\'s death. He was shot at about 10:15 p.m. on April 14, 1865, and died at 7:22 a.m. on April 15, 1865, after being carried to the Petersen House in Washington, D.C.', {
    sourceDependent: false,
    serverVerified: false
}).ok, 'a person named Abraham followed by the ordinary word "about" must not be mistaken for a Book of Abraham attribution');
assert(guard('John Adams wrote about independence, and Mark Twain wrote about American life.', {
    sourceDependent: false,
    serverVerified: false
}).ok, 'ordinary full names that match scripture-book titles must remain general knowledge');
for (const ordinaryPersonAnswer of [
    'Ruth Bader Ginsburg spoke about equality.',
    'Joshua Jackson talked about acting.',
    'Samuel Adams wrote about independence.',
    'Timothy Snyder writes about history.',
    'Titus Welliver spoke about television.',
    'Job Smith wrote about his childhood.'
]) {
    assert(guard(ordinaryPersonAnswer, { sourceDependent: false, serverVerified: false }).ok,
        'a canon-title given name must not create scripture attribution: ' + ordinaryPersonAnswer);
}

for (const query of ['D&C 18:15', 'Doctrine and Covenants 76:31', 'Isaiah 1:18', 'Matthew 5:3', '2 Corinthians 12:2', 'Alma 32:21', 'Moses 1:1', 'Song of Solomon 1:1', 'Words of Mormon 1:1', 'Joseph Smith—Matthew 1:1', 'what is Genesis about?', 'tell me about Genesis', 'what is the Book of Abraham about?', 'what does Genesis say about creation?', 'what does Isaiah teach about color?', 'what does Matthew say about prayer?', 'what does Mark say about baptism?', 'what does genesis creation account teach?', 'what is genesis creation story about?', 'what does alma faith sermon teach?', 'what does ruth loyalty story teach?', 'what is the book of abraham creation account about?', 'tell me about genesis creation', 'What did Alma and Amulek say?', 'what did alma and amulek say?']) {
    assert(integrity.isScriptureDependent(query), 'scripture query not detected: ' + query);
}
for (const personQuery of ['what did abraham lincoln write about government?', 'what did ruth bader ginsburg say about equality?', 'who was alma mahler?', 'who was moroni olsen?', 'Tell me about Abraham Lincoln.', 'tell me about abraham lincoln.', 'Tell me about Ruth Bader Ginsburg.', 'tell me about alma mahler']) {
    assert(!integrity.isScriptureDependent(personQuery),
        'ordinary person query must not be classified as scripture: ' + personQuery);
}

vm.runInThisContext(fs.readFileSync('study-source-router.js', 'utf8'), { filename: 'study-source-router.js' });
for (const query of ['what does Mark say about baptism?', 'what does Song of Solomon teach?', 'what does Words of Mormon say?', 'what does Joseph Smith—Matthew teach?']) {
    assert(window.focusChristSourceRouter.isFaithQuestion(query), 'router did not classify scripture query: ' + query);
    const sources = window.focusChristSourceRouter.sourcesForQuestion(query);
    assert(sources.some((source) => source.url.includes('/study/scriptures?')), 'router omitted Scriptures hub: ' + query);
}
const jesusStudy = window.focusChristSourceRouter.answerStudySourceForQuestion('Who is Jesus Christ?');
assert(jesusStudy && jesusStudy.url === 'answers/jesus-christ-latter-day-saint-beliefs.html', 'Jesus question did not map to the internal Answers study');
const griefStudy = window.focusChristSourceRouter.answerStudySourceForQuestion('How can I support someone grieving after the death of a child?');
assert(griefStudy && griefStudy.url === 'answers/death-of-a-child.html', 'specific child-loss question did not win its internal Answers study match');
assert(!window.focusChristSourceRouter.answerStudySourceForQuestion('Why is the sky blue?'), 'unrelated question received an internal Answers study link');
for (const query of ['What is the Abrahamic covenant?', 'How does the covenant of Abraham bless families?', "What is Abraham's covenant?", 'What is Abraham’s covenant?', "What does Jacob's ladder teach?", 'Explain Jacob’s ladder', 'Why did Jacob wrestle with God?', 'What does Jacob wrestling at Peniel mean?']) {
    const related = window.focusChristSourceRouter.answerStudySourceForQuestion(query);
    assert(related && related.url === 'answers/abrahamic-covenant.html', 'covenant query omitted its permanent study: ' + query);
    assert(fs.existsSync(related.url), 'covenant related study must resolve to a published local page');
}
for (const query of ['How was the Book of Abraham translated?', 'What happened to the Book of Abraham papyri?', 'What did Joseph Smith say about the Book of Abraham?', 'Tell me about Abraham Lincoln', 'What does the Book of Mormon prophet Jacob teach?']) {
    const related = window.focusChristSourceRouter.answerStudySourceForQuestion(query);
    assert(!related || related.url !== 'answers/abrahamic-covenant.html', 'unrelated Abraham or Jacob query acquired a covenant study: ' + query);
}
assert(window.focusChristSourceRouter.isChurchHistoryQuestion('How was the Book of Abraham translated?'), 'Book of Abraham history must preserve its historical routing');
const routerVersion = 'study-source-router.js?v=20260923-sensitive-welcome-1';
for (const page of ['ask.html', 'pioneers.html', 'church-history.html']) {
    const tags = fs.readFileSync(page, 'utf8').match(/<script\b[^>]*study-source-router\.js[^>]*>/g) || [];
    assert(tags.length === 1 && tags[0].includes(routerVersion), 'router consumer version or count differs: ' + page);
    if (page !== 'church-history.html') assert(tags[0].includes('data-focuschrist-source-router'), 'dynamic router page lacks duplicate guard marker: ' + page);
}
const journeySource = fs.readFileSync('study-journey.js', 'utf8');
assert(journeySource.includes("appendDynamicScript('" + routerVersion + "', 'data-focuschrist-source-router')"), 'router fallback version differs from explicit consumers');
const appendRouter = journeySource.match(/function appendDynamicScript\(src, marker\) \{[\s\S]*?\n    \}/)[0];
for (const existing of [true, false]) {
    let tagged = existing;
    const inserted = [];
    const context = { console, document: {
        querySelector(selector) { assert(selector === 'script[data-focuschrist-source-router]', 'unexpected duplicate check'); return tagged ? {} : null; },
        createElement(tag) { assert(tag === 'script', 'unexpected loader element'); return { setAttribute(name) { assert(name === 'data-focuschrist-source-router', 'unexpected marker'); }, addEventListener() {} }; },
        body: { appendChild(script) { inserted.push(script.src); tagged = true; } }
    } };
    vm.runInNewContext(appendRouter + '\nappendDynamicScript(' + JSON.stringify(routerVersion) + ', "data-focuschrist-source-router");\nappendDynamicScript("study-source-router.js?v=20260923-self-help-1", "data-focuschrist-source-router");', context);
    assert(inserted.length === (existing ? 0 : 1), 'current or cached wrapper duplicated the explicit router');
    if (!existing) assert(inserted[0] === routerVersion, 'fallback did not install current router');
}
console.log('Source integrity runtime QA PASS');
