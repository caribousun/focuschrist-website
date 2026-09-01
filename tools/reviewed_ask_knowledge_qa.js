const crypto = require('crypto');
const fs = require('fs');
const vm = require('vm');

global.window = {};
vm.runInThisContext(fs.readFileSync('reviewed-ask-knowledge.js', 'utf8'), { filename: 'reviewed-ask-knowledge.js' });

const registry = window.focusChristReviewedKnowledge;
const audit = JSON.parse(fs.readFileSync('answer-audit.json', 'utf8'));
const questionManifest = JSON.parse(fs.readFileSync('ask-question-contracts.json', 'utf8'));

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

function stable(value) {
    if (Array.isArray(value)) return value.map(stable);
    if (!value || typeof value !== 'object') return value;
    return Object.keys(value).sort().reduce((result, key) => {
        result[key] = stable(value[key]);
        return result;
    }, {});
}

function entryHash(entry) {
    return crypto.createHash('sha256').update(JSON.stringify(stable(entry))).digest('hex');
}

function entrySourceUrls(entry) {
    const sources = []
        .concat(entry.sources || [])
        .concat(entry.followup && Array.isArray(entry.followup.variants)
            ? entry.followup.variants.flatMap((variant) => variant.sources || [])
            : []);
    return [...new Set(sources.map((source) => source.url))];
}

assert(registry && registry.policyVersion === '2026-09-01.15', 'reviewed registry policy version mismatch');
assert(Array.isArray(registry.entries) && registry.entries.length >= 12, 'reviewed registry is unexpectedly small');
assert(questionManifest.release === registry.policyVersion, 'question-contract manifest release mismatch');

const extractedContracts = {
    ask_starters: [...fs.readFileSync('ask.html', 'utf8').matchAll(/data-ask-starter\s+data-question="([^"]+)"/g)].map((match) => match[1]),
    ask_topics: [...fs.readFileSync('ask.html', 'utf8').matchAll(/data-ask-topic="([^"]+)"/g)].map((match) => match[1]),
    pioneer_topics: [...fs.readFileSync('pioneers.html', 'utf8').matchAll(/onclick="askTopic\('([^']+)'\)"/g)].map((match) => match[1]),
    church_history_cards: [...fs.readFileSync('church-history.html', 'utf8').matchAll(/data-history-question="([^"]+)"/g)].map((match) => match[1])
};
Object.entries(extractedContracts).forEach(([key, values]) => {
    const contract = questionManifest.contracts[key];
    assert(contract && Array.isArray(contract.values), 'question-contract manifest section missing: ' + key);
    assert(JSON.stringify(contract.values) === JSON.stringify(values),
        'visible question controls changed without updating the machine-readable contract: ' + key);
    assert(contract.final_owner && contract.lane, 'question-contract owner or lane missing: ' + key);
});

const ids = new Set();
registry.entries.forEach((entry) => {
    assert(!ids.has(entry.id), 'duplicate reviewed entry id: ' + entry.id);
    ids.add(entry.id);
    assert(Array.isArray(entry.positiveTests) && entry.positiveTests.length >= 2, 'positive tests missing: ' + entry.id);
    assert(Array.isArray(entry.negativeTests) && entry.negativeTests.length >= 2, 'negative tests missing: ' + entry.id);
    assert(Array.isArray(entry.sources) && entry.sources.length > 0, 'source missing: ' + entry.id);
    assert(entry.sources.every((source) => /^https:\/\//.test(source.url)), 'non-HTTPS source: ' + entry.id);

    entry.profiles.forEach((profile) => {
        entry.positiveTests.forEach((question) => {
            const result = registry.match(question, { profile });
            assert(result && result.id === entry.id, `positive intent failed: ${entry.id} / ${profile} / ${question}`);
        });
        entry.negativeTests.forEach((question) => {
            const result = registry.match(question, { profile });
            assert(!result || result.id !== entry.id, `negative intent false positive: ${entry.id} / ${profile} / ${question}`);
        });
    });

    ['ask', 'pioneers', 'church-history'].filter((profile) => !entry.profiles.includes(profile)).forEach((profile) => {
        entry.positiveTests.forEach((question) => {
            const result = registry.match(question, { profile });
            assert(!result || result.id !== entry.id, `profile boundary failed: ${entry.id} appeared on ${profile}`);
        });
    });
});

const handcart = registry.match('What year did the handcarts begin?', { profile: 'pioneers' });
assert(handcart && handcart.answer.includes('1856'), 'owner handcart regression did not answer 1856');
assert(handcart.mode === 'reviewed-local' && handcart.sourceIntegrityPassed === true, 'handcart answer lacks reviewed-local receipt');
assert(!registry.match('When did handcart racing begin?', { profile: 'pioneers' }), 'handcart racing false positive');
assert(!registry.match('When did shopping carts begin?', { profile: 'pioneers' }), 'shopping cart false positive');
assert(!registry.match('Tell me about the Exodus in the Bible', { profile: 'pioneers' }), 'biblical Exodus false positive');
const handcartCard = registry.match('Handcart Companies', { profile: 'pioneers' });
assert(handcartCard && handcartCard.id === 'pioneer-handcart-travel-1856' && handcartCard.answer.length >= 400,
    'visible Handcart Companies topic must return a substantive reviewed answer');

const starterQuestions = [...fs.readFileSync('ask.html', 'utf8').matchAll(/data-ask-starter\s+data-question="([^"]+)"/g)]
    .map((match) => match[1]);
assert(starterQuestions.length === 6, 'Ask starter-card inventory changed without updating the executable contract');
starterQuestions.forEach((question) => {
    const result = registry.match(question, { profile: 'ask' });
    assert(result && result.mode === 'reviewed-local', 'visible Ask starter is not reviewed-local: ' + question);
    assert(result.answer.split(/\s+/).length >= 70, 'visible Ask starter answer is not substantive: ' + question);
    assert(result.sources.length >= 1, 'visible Ask starter has no authoritative source: ' + question);
});

const historyQuestions = [...fs.readFileSync('church-history.html', 'utf8').matchAll(/data-history-question="([^"]+)"/g)]
    .map((match) => match[1]);
assert(historyQuestions.length === 10,
    'Church History question-card inventory changed without updating the executable contract');
historyQuestions.forEach((question) => {
    const result = registry.match(question, { profile: 'church-history' });
    assert(result && result.mode === 'reviewed-local', 'visible Church History card is not reviewed-local: ' + question);
    assert(result.answer.split(/\s+/).length >= 70, 'visible Church History card answer is not substantive: ' + question);
    assert(result.sources.length >= 1, 'visible Church History card has no authoritative source: ' + question);
});

const resolvedFollowup = registry.resolveFollowup('Do we know the time he died', {
    profile: 'ask',
    history: [
        { role: 'user', content: 'What date did Joseph Smith die?' },
        { role: 'assistant', content: 'Joseph Smith died on June 27, 1844.' }
    ]
});
assert(resolvedFollowup.resolved === true && resolvedFollowup.entryId === 'joseph-smith-death-1844',
    'Joseph Smith time follow-up did not resolve from conversation history');
assert(registry.match(resolvedFollowup.query, { profile: 'ask' }).answer.includes('5:00 p.m.'),
    'resolved Joseph Smith time follow-up did not reach the reviewed time answer');
for (const ellipticalQuestion of ['What time?', 'And what time?', 'When exactly?']) {
    const ellipticalResult = registry.resolveFollowup(ellipticalQuestion, {
        profile: 'ask', history: [{ role: 'user', content: 'When did Joseph Smith die?' }]
    });
    assert(ellipticalResult.resolved === true && ellipticalResult.entryId === 'joseph-smith-death-1844',
        'permitted subjectless Joseph Smith follow-up did not resolve: ' + ellipticalQuestion);
}
const chainedFollowup = registry.resolveFollowup('What time?', {
    profile: 'ask',
    history: [
        { role: 'user', content: 'What date did Joseph Smith die?', contextEntryId: 'joseph-smith-death-1844' },
        { role: 'assistant', content: 'June 27, 1844.' },
        { role: 'user', content: 'Do we know the time he died', contextEntryId: 'joseph-smith-death-1844' },
        { role: 'assistant', content: 'About 5:00 p.m.' }
    ]
});
assert(chainedFollowup.resolved === true && chainedFollowup.entryId === 'joseph-smith-death-1844',
    'context receipt did not preserve a chained subjectless follow-up');
assert(registry.resolveFollowup('Do we know the time he died', { profile: 'ask', history: [] }).resolved === false,
    'follow-up context leaked without history');
const genericSkyFollowup = registry.resolveFollowup('Do we know the time he died', {
    profile: 'ask', history: [{ role: 'user', content: 'Why is the sky blue?' }]
});
assert(genericSkyFollowup.resolved === true && genericSkyFollowup.entryId === null
    && genericSkyFollowup.query.includes('Why is the sky blue?'),
    'generic follow-up must use only the immediately preceding subject without inheriting a reviewed identity');
assert(registry.resolveFollowup('When did Joseph F. Smith die?', {
    profile: 'ask', history: [{ role: 'user', content: 'When did Joseph Smith die?' }]
}).resolved === false, 'explicit competing Joseph identity was incorrectly inherited');
for (const competingQuestion of ['What time did Abraham Lincoln die?', 'When did Stalin die?', 'What year did John F. Kennedy die?']) {
    assert(registry.resolveFollowup(competingQuestion, {
        profile: 'ask', history: [{ role: 'user', content: 'When did Joseph Smith die?' }]
    }).resolved === false, 'explicit competing person was incorrectly inherited: ' + competingQuestion);
}
for (const [interruption, expectedEntryId] of [
    ['What date did Abraham Lincoln die?', 'general-abraham-lincoln-death-1865'],
    ['Why is the sky blue?', null]
]) {
    const interruptionResult = registry.resolveFollowup('Do we know the time he died', {
        profile: 'ask',
        history: [
            { role: 'user', content: 'When did Joseph Smith die?' },
            { role: 'assistant', content: 'June 27, 1844.' },
            { role: 'user', content: interruption },
            { role: 'assistant', content: 'An intervening answer.' }
        ]
    });
    assert(interruptionResult.resolved === true && interruptionResult.entryId === expectedEntryId
        && (expectedEntryId
            ? interruptionResult.contextQuestion.includes(interruption)
            : interruptionResult.query.includes(interruption)),
        'resolver skipped the newer user subject: ' + interruption);
}
const reviewedLincolnFollowup = registry.resolveFollowup('Do we know the time he died?', {
    profile: 'ask', history: [{ role: 'user', content: 'What date did Abraham Lincoln die?', contextEntryId: 'general-abraham-lincoln-death-1865' }]
});
assert(reviewedLincolnFollowup.resolved === true && reviewedLincolnFollowup.genericContext === false
    && reviewedLincolnFollowup.entryId === 'general-abraham-lincoln-death-1865',
    'reviewed Lincoln follow-up did not retain the audited subject');
const reviewedLincolnAnswer = registry.match(reviewedLincolnFollowup.query, {
    profile: 'ask', contextVariant: reviewedLincolnFollowup.contextVariant
});
assert(reviewedLincolnAnswer && reviewedLincolnAnswer.answer.includes('7:22 a.m.')
    && reviewedLincolnAnswer.sources.some((source) => source.url.includes('loc.gov'))
    && reviewedLincolnAnswer.sources.some((source) => source.url.includes('nps.gov')),
    'reviewed Lincoln follow-up did not return its exact, federally sourced answer');
const reviewedLincolnChain = registry.resolveFollowup('What time?', {
    profile: 'ask',
    history: [
        { role: 'user', content: 'What date did Abraham Lincoln die?', contextEntryId: 'general-abraham-lincoln-death-1865' },
        { role: 'assistant', content: 'Abraham Lincoln died at 7:22 a.m. on April 15, 1865.' },
        { role: 'user', content: 'Do we know the time he died?', contextEntryId: 'general-abraham-lincoln-death-1865' },
        { role: 'assistant', content: 'Abraham Lincoln died at 7:22 a.m. on April 15, 1865.' }
    ]
});
assert(reviewedLincolnChain.resolved === true
    && reviewedLincolnChain.entryId === 'general-abraham-lincoln-death-1865',
    'reviewed Lincoln context receipt did not preserve the subject through a chained ellipsis');
const reviewedLincolnChainAnswer = registry.match(reviewedLincolnChain.query, { profile: 'ask' });
assert(reviewedLincolnChainAnswer && reviewedLincolnChainAnswer.answer.includes('7:22 a.m.'),
    'reviewed Lincoln chained ellipsis did not return the pinned answer');
for (const [contextQuestion, expectedVariant, expectedAnswer] of [
    ['How old was he?', 'age-at-death', '38 years old'],
    ['Why was he in Carthage?', 'carthage-imprisonment', 'awaiting legal proceedings'],
    ['Why was he in Carthage Jail?', 'carthage-imprisonment', 'awaiting legal proceedings'],
    ['Why was he killed at Carthage Jail?', 'carthage-attack-context', 'mounting opposition'],
    ['Who was with him?', 'carthage-companions', 'John Taylor'],
    ['Where did he live?', 'nauvoo-residence', 'Nauvoo, Illinois']
]) {
    const reviewedJosephFollowup = registry.resolveFollowup(contextQuestion, {
        profile: 'ask',
        history: [{ role: 'user', content: 'What date did Joseph Smith die?' }]
    });
    assert(reviewedJosephFollowup.resolved === true && reviewedJosephFollowup.genericContext === false
        && reviewedJosephFollowup.entryId === 'joseph-smith-death-1844'
        && reviewedJosephFollowup.contextVariant === expectedVariant,
    'reviewed contextual variant did not resolve: ' + contextQuestion);
    const contextualAnswer = registry.match(reviewedJosephFollowup.query, {
        profile: 'ask',
        contextVariant: reviewedJosephFollowup.contextVariant
    });
    assert(contextualAnswer && contextualAnswer.answer.includes(expectedAnswer)
        && contextualAnswer.sources.some((source) => source.url.includes('churchofjesuschrist.org')),
    'reviewed contextual variant did not return its specific sourced answer: ' + contextQuestion);
}
for (const [contextQuestion, expectedAnswer] of [
    ['Who killed him?', 'killed by a mob'],
    ['Where did he die?', 'Carthage Jail'],
    ['Where was he killed?', 'Carthage Jail']
]) {
    const reviewedJosephFollowup = registry.resolveFollowup(contextQuestion, {
        profile: 'ask',
        history: [{ role: 'user', content: 'What date did Joseph Smith die?' }]
    });
    assert(reviewedJosephFollowup.resolved === true && reviewedJosephFollowup.genericContext === false
        && reviewedJosephFollowup.entryId === 'joseph-smith-death-1844'
        && reviewedJosephFollowup.contextVariant === null,
    'death-location or assailant follow-up must use the base death answer: ' + contextQuestion);
    const contextualAnswer = registry.match(reviewedJosephFollowup.query, {
        profile: 'ask', contextVariant: reviewedJosephFollowup.contextVariant
    });
    assert(contextualAnswer && contextualAnswer.answer.includes(expectedAnswer),
        'base death answer did not answer the death-location or assailant follow-up: ' + contextQuestion);
}
const overlappingCompanionFollowup = registry.resolveFollowup('Who was in Carthage Jail with him?', {
    profile: 'ask', history: [{ role: 'user', content: 'What date did Joseph Smith die?' }]
});
assert(overlappingCompanionFollowup.contextVariant === 'carthage-companions',
    'companion intent lost to overlapping Carthage/Jail terms');
const motiveFollowup = registry.resolveFollowup('Why was he killed at Carthage Jail?', {
    profile: 'ask', history: [{ role: 'user', content: 'What date did Joseph Smith die?' }]
});
assert(motiveFollowup.contextVariant === 'carthage-attack-context',
    'death-motive question did not receive its dedicated sourced context answer');
const motiveAnswer = registry.match(motiveFollowup.query, {
    profile: 'ask', contextVariant: motiveFollowup.contextVariant
});
assert(motiveAnswer && motiveAnswer.answer.includes('not a lawful execution')
    && motiveAnswer.answer.split(/\s+/).length >= 70,
    'death-motive answer was not conclusive and substantive');
const unsupportedJosephFollowup = registry.resolveFollowup('What was his favorite food?', {
    profile: 'ask', history: [{ role: 'user', content: 'What date did Joseph Smith die?' }]
});
assert(unsupportedJosephFollowup.resolved === true && unsupportedJosephFollowup.genericContext === true,
    'unsupported Joseph follow-up must remain in contextual research instead of forcing a local variant');
for (const [competingQuestion, expectedEntryId] of [
    ['When did he die—Abraham Lincoln?', 'general-abraham-lincoln-death-1865'],
    ['Do we know what time he died, Abraham Lincoln?', 'general-abraham-lincoln-death-1865'],
    ['Do we know what time he died, john adams?', null],
    ['when did he die—george washington?', null],
    ['did john adams die?', null]
]) {
    const explicitSubject = registry.resolveFollowup(competingQuestion, {
        profile: 'ask',
        history: [{ role: 'user', content: 'What date did Joseph Smith die?', contextEntryId: 'joseph-smith-death-1844' }]
    });
    assert(explicitSubject.resolved === false && explicitSubject.entryId === expectedEntryId,
        'explicit current person inherited Joseph Smith context: ' + competingQuestion);
}
[
    ['When did Joseph F. Smith die?', 'ask'],
    ['When did Joseph Fielding Smith die?', 'ask'],
    ['When did Joseph Smith Sr. die?', 'ask'],
    ['Why is the sky blue song popular?', 'ask'],
    ['When did handcart use begin at the amusement park?', 'pioneers'],
    ['When was the Church of England organized?', 'church-history']
].forEach(([question, profile]) => {
    assert(!registry.match(question, { profile }), 'independent-review false positive survived: ' + question);
});

const auditRecords = Array.isArray(audit.reviewed_knowledge) ? audit.reviewed_knowledge : [];
const auditById = new Map(auditRecords.map((record) => [record.id, record]));
assert(auditById.size === registry.entries.length, 'reviewed knowledge ledger count mismatch');
registry.entries.forEach((entry) => {
    const record = auditById.get(entry.id);
    assert(record, 'reviewed knowledge ledger entry missing: ' + entry.id);
    assert(record.entry_sha256 === entryHash(entry), 'reviewed knowledge changed after approval: ' + entry.id);
    assert(JSON.stringify(record.authoritative_sources) === JSON.stringify(entrySourceUrls(entry)),
        'reviewed knowledge source ledger mismatch: ' + entry.id);
});

console.log(`Reviewed Ask knowledge QA PASS: ${registry.entries.length} entries; all positive, negative, profile, and hash checks passed`);
