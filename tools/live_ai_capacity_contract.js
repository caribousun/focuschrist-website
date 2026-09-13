const assert = require('node:assert/strict');

// Compose, independent source audit, optional repair, and audit of that repair.
// This is a request-count ceiling, not a price or spend estimate.
const MAX_EXTERNAL_VERIFIER_CALLS = 4;
const DAILY_INDEXED_QUESTIONS = 50;
const REQUIRED_EXTERNAL_BURST_IDS = ['burst-temples', 'burst-prayer'];

function validateExternalVerifierCapacity(indexed, burstResults) {
    const samples = indexed.filter(result => result.verifierRoute !== 'reviewed-deterministic');
    for (const id of REQUIRED_EXTERNAL_BURST_IDS) {
        const matches = burstResults.filter(result => result.id === id);
        assert(matches.length === 1 && samples.includes(matches[0]),
            `${id}: missing unique indexed external-verifier concurrency sample`);
    }
    assert(samples.length >= REQUIRED_EXTERNAL_BURST_IDS.length,
        'insufficient external-verifier usage samples');
    const counts = samples.map(result => {
        assert(['openai-primary', 'openai-repair'].includes(result.verifierRoute),
            `${result.id}: unsupported external verifier route`);
        assert(Number.isInteger(result.openaiVerifierCalls)
            && result.openaiVerifierCalls >= 1 && result.openaiVerifierCalls <= MAX_EXTERNAL_VERIFIER_CALLS,
            `${result.id}: expected 1..${MAX_EXTERNAL_VERIFIER_CALLS} OpenAI verifier calls, received ${result.openaiVerifierCalls}`);
        assert(result.cloudflareVerifierCalls === 0 && result.groqVerifierCalls === 0,
            `${result.id}: missing zero-call receipts or unexpected non-OpenAI verifier usage`);
        assert(Number.isFinite(result.verifierInputTokens) && result.verifierInputTokens > 0
            && Number.isFinite(result.verifierOutputTokens) && result.verifierOutputTokens > 0,
            `${result.id}: incomplete external-verifier token receipts`);
        return result.openaiVerifierCalls;
    }).sort((a, b) => a - b);
    const p95VerifierCalls = counts[Math.ceil(counts.length * 0.95) - 1];
    return {
        externalVerifierSamples: samples.length,
        p95VerifierCalls,
        projectedVerifierCallsAt50Daily: p95VerifierCalls * DAILY_INDEXED_QUESTIONS,
        maxVerifierCallsPerQuestion: MAX_EXTERNAL_VERIFIER_CALLS,
        maxVerifierCallsAt50Daily: MAX_EXTERNAL_VERIFIER_CALLS * DAILY_INDEXED_QUESTIONS,
    };
}

module.exports = { MAX_EXTERNAL_VERIFIER_CALLS, validateExternalVerifierCapacity };
