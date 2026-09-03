const ENDPOINT = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
const ORIGIN = 'https://focuschrist.com';
const HARD_LIMIT_MS = 25000;
const P95_LIMIT_MS = 20000;
const BASELINE_MODE = process.argv.includes('--baseline');
const INTER_REQUEST_DELAY_MS = BASELINE_MODE ? 0 : 5000;

const specimens = [
    {
        id: 'ask-church-person',
        page: 'ask', profile: 'general-knowledge',
        question: 'Who is Hyrum Smith?',
        expectedProfile: 'faith-study', officialOnly: true, minimumWords: 70
    },
    {
        id: 'ask-stable-general',
        page: 'ask', profile: 'general-knowledge',
        question: 'Why do seasons change on Earth?',
        expectedProfile: 'general-knowledge', officialOnly: false, minimumWords: 45
    },
    {
        id: 'ask-scripture',
        page: 'ask', profile: 'faith-study',
        question: 'What does Alma 32 teach about faith?',
        expectedProfile: 'faith-study', officialOnly: true, minimumWords: 70
    },
    {
        id: 'pioneer-free-form',
        page: 'pioneers', profile: 'pioneer-study',
        question: 'How did Latter-day Saint pioneer communities organize irrigation?',
        expectedProfile: 'faith-study', officialOnly: true, minimumWords: 70
    },
    {
        id: 'history-free-form',
        page: 'church-history', profile: 'faith-study',
        question: 'How did the Relief Society begin?',
        expectedProfile: 'faith-study', officialOnly: true, minimumWords: 70
    }
];

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

function percentile(values, fraction) {
    const ordered = values.slice().sort((a, b) => a - b);
    return ordered[Math.max(0, Math.ceil(ordered.length * fraction) - 1)] || 0;
}

async function submit(specimen) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), HARD_LIMIT_MS + 1000);
    const started = performance.now();
    try {
        const response = await fetch(ENDPOINT, {
            method: 'POST',
            headers: { Origin: ORIGIN, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                focuschrist_page: specimen.page,
                focuschrist_profile: specimen.profile,
                messages: [{ role: 'user', content: specimen.question }]
            }),
            signal: controller.signal
        });
        const elapsedMs = Math.round(performance.now() - started);
        const payload = await response.json();
        const answer = String(payload && payload.choices && payload.choices[0]
            && payload.choices[0].message && payload.choices[0].message.content || '').trim();
        const sources = Array.isArray(payload.focuschrist_sources) ? payload.focuschrist_sources : [];
        const sourceHosts = sources.map((source) => {
            try { return new URL(source.url).hostname.toLowerCase(); } catch (_error) { return 'invalid'; }
        });
        return {
            id: specimen.id,
            status: response.status,
            elapsedMs,
            gatewayMode: String(payload.focuschrist_gateway_mode || ''),
            policyVersion: String(payload.focuschrist_source_policy || ''),
            providerStatus: Number(payload.focuschrist_provider_status || 0),
            providerCode: String(payload.focuschrist_provider_code || ''),
            verifierRoute: String(payload.focuschrist_verifier_route || ''),
            verifierFallbackReason: String(payload.focuschrist_verifier_fallback_reason || ''),
            verifierPrimaryStatus: Number(payload.focuschrist_verifier_primary_status || 0),
            verifierPrimaryCode: String(payload.focuschrist_verifier_primary_code || ''),
            verifierDurationMs: Number(payload.focuschrist_verifier_duration_ms || 0),
            resolvedProfile: String(payload.focuschrist_resolved_profile || ''),
            classificationMode: String(payload.focuschrist_classification_mode || ''),
            verified: payload.focuschrist_source_integrity_verified === true,
            wordCount: answer.split(/\s+/).filter(Boolean).length,
            sourceHosts,
            answer
        };
    } finally {
        clearTimeout(timer);
    }
}

(async () => {
    const results = [];
    for (let specimenIndex = 0; specimenIndex < specimens.length; specimenIndex += 1) {
        const specimen = specimens[specimenIndex];
        if (specimenIndex > 0 && INTER_REQUEST_DELAY_MS) {
            await new Promise((resolve) => setTimeout(resolve, INTER_REQUEST_DELAY_MS));
        }
        try {
            const result = await submit(specimen);
            results.push(result);
            console.log(JSON.stringify({ ...result, answer: undefined }));
        } catch (error) {
            results.push({ id: specimen.id, elapsedMs: HARD_LIMIT_MS + 1000, error: error.name || error.message });
            console.log(JSON.stringify(results.at(-1)));
        }
    }

    if (BASELINE_MODE) {
        const baselineTimes = results.map((result) => result.elapsedMs);
        const fallbacks = results.filter((result) => result.error
            || /could not complete|temporarily unavailable|could not verify|please rephrase/i.test(result.answer || '')).length;
        console.log('Live AI response matrix BASELINE COMPLETE: '
            + JSON.stringify({ count: results.length, fallbacks, p95Ms: percentile(baselineTimes, 0.95), maxMs: Math.max(...baselineTimes) }));
        return;
    }

    for (let index = 0; index < specimens.length; index += 1) {
        const specimen = specimens[index];
        const result = results[index];
        assert(result.status === 200, specimen.id + ' returned HTTP ' + result.status);
        assert(result.policyVersion === '2026-09-03.19',
            specimen.id + ' returned Worker policy ' + result.policyVersion + ' instead of 2026-09-03.19');
        assert(result.elapsedMs <= HARD_LIMIT_MS, specimen.id + ' exceeded the 25-second visitor ceiling');
        assert(result.wordCount >= specimen.minimumWords, specimen.id + ' returned an incomplete answer');
        assert(!/could not complete|temporarily unavailable|could not verify|please rephrase/i.test(result.answer),
            specimen.id + ' returned a known fallback instead of an answer');
        assert(result.resolvedProfile === specimen.expectedProfile,
            specimen.id + ' resolved to ' + result.resolvedProfile + ' instead of ' + specimen.expectedProfile);
        assert(result.verifierRoute === 'cloudflare-primary' || result.verifierRoute === 'groq-fallback',
            specimen.id + ' did not return a recognized verifier route');
        if (specimen.officialOnly) {
            assert(result.verified && result.sourceHosts.length > 0
                && result.sourceHosts.every((host) => host === 'churchofjesuschrist.org' || host.endsWith('.churchofjesuschrist.org')),
            specimen.id + ' did not return an official-only verified answer');
        }
    }

    const times = results.map((result) => result.elapsedMs);
    const p95 = percentile(times, 0.95);
    const primaryCount = results.filter((result) => result.verifierRoute === 'cloudflare-primary').length;
    const fallbackCount = results.filter((result) => result.verifierRoute === 'groq-fallback').length;
    assert(primaryCount >= 4,
        'Cloudflare primary verifier handled only ' + primaryCount + '/5 specimens; routes=' + JSON.stringify(
            results.map((result) => ({ id: result.id, route: result.verifierRoute, reason: result.verifierFallbackReason }))
        ));
    assert(p95 <= P95_LIMIT_MS, 'matrix p95 exceeded 20 seconds: ' + p95 + 'ms');
    console.log('Live AI response matrix PASS: ' + JSON.stringify({
        count: results.length,
        cloudflarePrimary: primaryCount,
        groqFallback: fallbackCount,
        p95Ms: p95,
        maxMs: Math.max(...times)
    }));
})().catch((error) => {
    console.error('Live AI response matrix FAIL:', error.message);
    process.exit(1);
});
