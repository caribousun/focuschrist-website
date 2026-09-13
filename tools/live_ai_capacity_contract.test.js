const assert = require('node:assert/strict');
const { validateExternalVerifierCapacity } = require('./live_ai_capacity_contract.js');

function sample(id, calls) {
    return { id, verifierRoute: 'openai-primary', openaiVerifierCalls: calls,
        cloudflareVerifierCalls: 0, groqVerifierCalls: 0,
        verifierInputTokens: 1000, verifierOutputTokens: 120 };
}
function fixture() {
    const burst = [sample('burst-temples', 4), sample('burst-prayer', 2)];
    return { burst, indexed: [...burst, { id: 'reviewed-kirtland', verifierRoute: 'reviewed-deterministic' }] };
}
const valid = fixture();
assert.deepEqual(validateExternalVerifierCapacity(valid.indexed, valid.burst), {
    externalVerifierSamples: 2, p95VerifierCalls: 4, projectedVerifierCallsAt50Daily: 200,
    maxVerifierCallsPerQuestion: 4, maxVerifierCallsAt50Daily: 200,
});
for (const calls of [0, undefined, 5, 1.5, NaN]) {
    const test = fixture(); test.burst[0].openaiVerifierCalls = calls;
    assert.throws(() => validateExternalVerifierCapacity(test.indexed, test.burst), /burst-temples: expected 1\.\.4/);
}
for (const field of ['verifierInputTokens', 'verifierOutputTokens', 'cloudflareVerifierCalls', 'groqVerifierCalls']) {
    const test = fixture(); delete test.burst[0][field];
    assert.throws(() => validateExternalVerifierCapacity(test.indexed, test.burst), /burst-temples:/);
}
for (const field of ['cloudflareVerifierCalls', 'groqVerifierCalls']) {
    const test = fixture(); test.burst[0][field] = 1;
    assert.throws(() => validateExternalVerifierCapacity(test.indexed, test.burst), /non-OpenAI/);
}
const missingBurst = fixture(); missingBurst.burst.pop();
assert.throws(() => validateExternalVerifierCapacity(missingBurst.indexed, missingBurst.burst), /burst-prayer: missing/);
const localBurst = fixture(); localBurst.burst[0].verifierRoute = 'reviewed-deterministic';
assert.throws(() => validateExternalVerifierCapacity(localBurst.indexed, localBurst.burst), /burst-temples: missing/);
const excessNonBurst = fixture(); excessNonBurst.indexed.push(sample('extra-indexed-answer', 5));
assert.throws(() => validateExternalVerifierCapacity(excessNonBurst.indexed, excessNonBurst.burst), /extra-indexed-answer: expected/);
const lowerObserved = fixture(); lowerObserved.burst[0].openaiVerifierCalls = 2;
const lower = validateExternalVerifierCapacity(lowerObserved.indexed, lowerObserved.burst);
assert.equal(lower.projectedVerifierCallsAt50Daily, 100);
assert.equal(lower.maxVerifierCallsAt50Daily, 200);
console.log('Live AI capacity contract PASS: bounded four-call repair accepted; incomplete, zero, excess and missing concurrency receipts rejected.');
