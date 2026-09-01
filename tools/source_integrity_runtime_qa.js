const fs = require('fs');
const vm = require('vm');

global.window = { location: { pathname: '/ask.html' } };
global.document = { readyState: 'loading', addEventListener() {} };
vm.runInThisContext(fs.readFileSync('site-common.js', 'utf8'), { filename: 'site-common.js' });

const integrity = window.focusChristSourceIntegrity;
const guard = integrity.guardGeneratedAnswer;
function assert(condition, message) { if (!condition) throw new Error(message); }

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
console.log('Source integrity runtime QA PASS');
