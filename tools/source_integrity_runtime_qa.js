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

for (const query of ['D&C 18:15', 'Doctrine and Covenants 76:31', 'Isaiah 1:18', 'Matthew 5:3', '2 Corinthians 12:2', 'Alma 32:21', 'Moses 1:1', 'Song of Solomon 1:1', 'Words of Mormon 1:1', 'Joseph Smith—Matthew 1:1', 'what does Genesis say about creation?', 'what does Isaiah teach about color?', 'what does Matthew say about prayer?', 'what does Mark say about baptism?']) {
    assert(integrity.isScriptureDependent(query), 'scripture query not detected: ' + query);
}

vm.runInThisContext(fs.readFileSync('study-source-router.js', 'utf8'), { filename: 'study-source-router.js' });
for (const query of ['what does Mark say about baptism?', 'what does Song of Solomon teach?', 'what does Words of Mormon say?', 'what does Joseph Smith—Matthew teach?']) {
    assert(window.focusChristSourceRouter.isFaithQuestion(query), 'router did not classify scripture query: ' + query);
    const sources = window.focusChristSourceRouter.sourcesForQuestion(query);
    assert(sources.some((source) => source.url.includes('/study/scriptures?')), 'router omitted Scriptures hub: ' + query);
}
console.log('Source integrity runtime QA PASS');
