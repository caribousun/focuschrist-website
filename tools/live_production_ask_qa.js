const fs = require('fs');
const vm = require('vm');

const ORIGIN = 'https://focuschrist.com';
const MAX_ATTEMPTS = 24;
const RETRY_MS = 10000;
const ROOT_ASSETS = [
    'ask.html',
    'pioneers.html',
    'church-history.html',
    'ask-question-contracts.json'
];
const REQUIRED_CONTROLLERS = [
    'site-common.js',
    'reviewed-ask-knowledge.js',
    'study-intelligence-v3.js',
    'study-journey.js',
    'study-source-router.js',
    'art-ask-context.js',
    'ask-experience.js',
    'pioneer-experience.js',
    'church-history-experience.js'
];

function localScriptReferences(text) {
    const references = new Set();
    const patterns = [
        /<script[^>]+src=["']([^"'?#]+\.js)(?:\?[^"']*)?["']/gi,
        /["']([a-z0-9][a-z0-9./-]*\.js)\?v=[^"']+["']/gi
    ];
    patterns.forEach((pattern) => {
        let match;
        while ((match = pattern.exec(text)) !== null) {
            const path = String(match[1] || '').replace(/^\.\//, '');
            if (!path || path.includes('://') || path.startsWith('/') || path.includes('..')) continue;
            if (fs.existsSync(path)) references.add(path);
        }
    });
    return [...references];
}

function discoverCriticalAssets() {
    const discovered = new Set(ROOT_ASSETS);
    const queue = ROOT_ASSETS.filter((path) => /\.html$/.test(path));

    while (queue.length > 0) {
        const path = queue.shift();
        const text = fs.readFileSync(path, 'utf8');
        localScriptReferences(text).forEach((reference) => {
            if (discovered.has(reference)) return;
            discovered.add(reference);
            queue.push(reference);
        });
    }

    REQUIRED_CONTROLLERS.forEach((path) => {
        assert(discovered.has(path), 'critical controller is no longer discoverable from production roots: ' + path);
    });
    return [...discovered].sort();
}

const ASSETS = discoverCriticalAssets();

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchAsset(path, attempt) {
    const delimiter = path.includes('?') ? '&' : '?';
    const response = await fetch(
        ORIGIN + '/' + path + delimiter + 'focuschrist_live_gate=' + Date.now() + '-' + attempt,
        {
            cache: 'no-store',
            headers: { 'cache-control': 'no-cache' },
            signal: AbortSignal.timeout(15000)
        }
    );
    if (!response.ok) throw new Error(path + ' returned HTTP ' + response.status);
    return response.text();
}

async function waitForExactDeployment() {
    const local = Object.fromEntries(ASSETS.map((path) => [
        path,
        fs.readFileSync(path, 'utf8')
    ]));
    let lastMismatches = [];

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
        try {
            const livePairs = await Promise.all(ASSETS.map(async (path) => [
                path,
                await fetchAsset(path, attempt)
            ]));
            const live = Object.fromEntries(livePairs);
            const mismatches = ASSETS.filter((path) => live[path] !== local[path]);
            if (mismatches.length === 0) return live;
            lastMismatches = mismatches;
            console.log('Production deployment not exact yet (attempt ' + attempt + '): ' + mismatches.join(', '));
        } catch (error) {
            lastMismatches = [String(error && error.message || error)];
            console.log('Production deployment check retry ' + attempt + ': ' + lastMismatches[0]);
        }
        if (attempt < MAX_ATTEMPTS) await wait(RETRY_MS);
    }

    throw new Error('Production did not converge to the tested release: ' + lastMismatches.join(', '));
}

function requireSubstantive(match, label, expected) {
    assert(match && typeof match.answer === 'string', label + ' did not match reviewed knowledge');
    assert(match.answer.trim().split(/\s+/).length >= 40, label + ' answer is not substantive');
    assert(!/cannot verify the specific source claim|please confirm the subject|could not complete/i.test(match.answer),
        label + ' rendered a refusal fallback');
    if (expected) assert(match.answer.includes(expected), label + ' omitted ' + expected);
    return match;
}

(async function () {
    const live = await waitForExactDeployment();
    console.log('Exact production dependency graph verified: ' + ASSETS.length + ' assets');

    assert(live['ask.html'].includes('reviewed-ask-knowledge.js?v=20260901-15')
        && live['ask.html'].includes('ask-experience.js?v=20260901-15'),
        'production Ask HTML does not load the .15 controllers');
    assert(live['pioneers.html'].includes('pioneer-experience.js?v=20260901-15'),
        'production Pioneer HTML does not load the .15 controller');
    assert(live['church-history.html'].includes('church-history-experience.js?v=20260901-15'),
        'production Church History HTML does not load the .15 controller');

    global.window = {};
    vm.runInThisContext(live['reviewed-ask-knowledge.js'], {
        filename: ORIGIN + '/reviewed-ask-knowledge.js'
    });
    const registry = window.focusChristReviewedKnowledge;
    assert(registry && registry.policyVersion === '2026-09-01.15',
        'production reviewed registry policy is not .15');

    const lincolnQuestion = 'What date did Abraham Lincoln die?';
    const lincolnMain = requireSubstantive(
        registry.match(lincolnQuestion, { profile: 'ask' }),
        'Lincoln main question',
        '7:22 a.m.'
    );
    const lincolnFollowup = registry.resolveFollowup('Do we know the time he died?', {
        profile: 'ask',
        history: [{ role: 'user', content: lincolnQuestion, contextEntryId: lincolnMain.id }]
    });
    assert(lincolnFollowup.resolved === true
        && lincolnFollowup.entryId === 'general-abraham-lincoln-death-1865',
        'Lincoln pronoun follow-up lost its reviewed context');
    requireSubstantive(
        registry.match(lincolnFollowup.query, { profile: 'ask' }),
        'Lincoln pronoun follow-up',
        '7:22 a.m.'
    );

    const lincolnChain = registry.resolveFollowup('What time?', {
        profile: 'ask',
        history: [
            { role: 'user', content: lincolnQuestion, contextEntryId: lincolnMain.id },
            { role: 'assistant', content: lincolnMain.answer },
            { role: 'user', content: 'Do we know the time he died?', contextEntryId: lincolnMain.id },
            { role: 'assistant', content: lincolnMain.answer }
        ]
    });
    assert(lincolnChain.resolved === true
        && lincolnChain.entryId === 'general-abraham-lincoln-death-1865',
        'Lincoln chained ellipsis lost its reviewed context');
    const lincolnChainAnswer = requireSubstantive(
        registry.match(lincolnChain.query, { profile: 'ask' }),
        'Lincoln chained ellipsis',
        '7:22 a.m.'
    );
    assert(!lincolnChainAnswer.answer.includes('10:00 p.m.'),
        'Lincoln chained ellipsis contains the known false death time');
    assert(registry.resolveFollowup('Do we know the time he died?', {
        profile: 'ask',
        history: []
    }).resolved === false, 'New Question/reset isolation leaked prior context');

    const josephMain = requireSubstantive(
        registry.match('What date did Joseph Smith die?', { profile: 'ask' }),
        'Joseph Smith main question',
        'June 27, 1844'
    );
    const josephTime = registry.resolveFollowup('Do we know the time he died?', {
        profile: 'ask',
        history: [{ role: 'user', content: 'What date did Joseph Smith die?', contextEntryId: josephMain.id }]
    });
    requireSubstantive(
        registry.match(josephTime.query, { profile: 'ask', contextVariant: josephTime.contextVariant }),
        'Joseph Smith time follow-up',
        '5:00 p.m.'
    );
    const josephAge = registry.resolveFollowup('How old was he?', {
        profile: 'ask',
        history: [{ role: 'user', content: 'What date did Joseph Smith die?', contextEntryId: josephMain.id }]
    });
    requireSubstantive(
        registry.match(josephAge.query, { profile: 'ask', contextVariant: josephAge.contextVariant }),
        'Joseph Smith age follow-up',
        '38 years old'
    );

    requireSubstantive(
        registry.match('Handcart Companies', { profile: 'pioneers' }),
        'Pioneer Handcart Companies card',
        '1856'
    );
    requireSubstantive(
        registry.match('How does the Church explain Joseph Smith and plural marriage?', { profile: 'church-history' }),
        'Church History plural marriage card',
        'early 1840s'
    );
    requireSubstantive(
        registry.match('Who is Jesus Christ, and why is He central to Latter-day Saint belief?', { profile: 'ask' }),
        'Jesus Christ card',
        'Savior and Redeemer'
    );

    for (const competing of [
        'Do we know what time he died, john adams?',
        'When did he die—washington?',
        'What time did he die, JFK?'
    ]) {
        const isolated = registry.resolveFollowup(competing, {
            profile: 'ask',
            history: [{ role: 'user', content: 'What date did Joseph Smith die?', contextEntryId: josephMain.id }]
        });
        assert(isolated.resolved === false && isolated.entryId === null,
            'production inherited Joseph Smith for competing identity: ' + competing);
    }

    console.log('LIVE PRODUCTION ASK QA PASS: exact deployed assets and critical conversations verified');
})().catch((error) => {
    console.error(error);
    process.exit(1);
});
