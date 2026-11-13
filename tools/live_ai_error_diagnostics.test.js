const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const { createRequire } = require('node:module');
const filename = path.join(__dirname, 'live_ai_response_matrix.js');
const source = fs.readFileSync(filename, 'utf8');
const test = { id: 'offline', question: 'Fixture question', page: 'ask', profile: 'faith-study' };
function fixture(implementation) {
    let now = 100, timer, cleared = 0, calls = 0, delay;
    const module = { exports: {} };
    const context = {
        module, require: createRequire(filename), process: { argv: ['node', 'fixture', '--baseline'] },
        performance: { now: () => now }, AbortController, URL,
        console: { log() {}, error() {} },
        setTimeout: (fn, ms) => { timer = fn; delay = ms; return 1; },
        clearTimeout: () => { cleared++; },
        fetch: async (...args) => { calls++; return implementation({
            advance: ms => { now += ms; }, expire: () => timer(), args,
        }); },
    };
    vm.runInNewContext(source, context, { filename });
    assert.equal(calls, 0, 'import must not run production requests');
    return { api: module.exports, stats: () => ({ calls, cleared, delay }) };
}
async function failure(implementation, expected) {
    const f = fixture(implementation);
    const [result] = await f.api.runSequential([test]);
    for (const [key, value] of Object.entries(expected)) assert.equal(result[key], value, key);
    assert.throws(() => f.api.validateResult(test, result), /failed at/);
    assert.equal(f.stats().cleared, 1);
    assert.equal(f.stats().calls, 1);
    assert.equal(f.stats().delay, 26000);
    assert.equal(result.gatewayMode, undefined, 'do not invent missing Worker receipts');
    return result;
}
(async () => {
    await failure(({ advance }) => { advance(17); throw new TypeError('offline network failure'); },
        { elapsedMs: 17, failureKind: 'request-error', failureStage: 'request', clientDeadlineExpired: false, status: undefined });
    await failure(({ advance, expire }) => { advance(26014); expire(); throw Object.assign(new Error('aborted'), { name: 'AbortError' }); },
        { elapsedMs: 26014, failureKind: 'client-deadline', failureStage: 'request', clientDeadlineExpired: true, status: undefined });
    await failure(({ advance }) => { advance(23); throw Object.assign(new Error('other abort'), { name: 'AbortError' }); },
        { elapsedMs: 23, failureKind: 'request-error', clientDeadlineExpired: false });
    await failure(({ advance }) => ({ status: 502, json: async () => { advance(41); throw new SyntaxError('invalid JSON'); } }),
        { elapsedMs: 41, status: 502, failureKind: 'response-body-error', failureStage: 'response-body', clientDeadlineExpired: false });
    await failure(({ advance, expire }) => ({ status: 200, json: async () => { advance(26003); expire(); throw Object.assign(new Error('body abort'), { name: 'AbortError' }); } }),
        { elapsedMs: 26003, status: 200, failureKind: 'client-deadline', failureStage: 'response-body', clientDeadlineExpired: true });
    const ok = fixture(({ advance }) => { advance(32); return { status: 200, json: async () => ({ choices: [{ message: { content: 'Fixture answer' } }], focuschrist_gateway_mode: 'fixture-mode' }) }; });
    const result = await ok.api.submit(test);
    assert.equal(result.elapsedMs, 32);
    assert.equal(result.headersElapsedMs, 32);
    assert.equal(result.status, 200);
    assert.equal(result.gatewayMode, 'fixture-mode');
    assert.equal(result.failureKind, undefined);
    assert.equal(ok.api.HARD_LIMIT_MS, 25000);
    assert.throws(() => ok.api.validateResult(test, { status: 200, policyVersion: '2026-09-13.94', elapsedMs: 25001 }), /25-second visitor ceiling/);
    assert.equal(ok.stats().cleared, 1);
    const delayed = fixture(({ advance }) => {
        advance(10);
        return { status: 200, json: async () => {
            advance(25010);
            return { focuschrist_source_policy: '2026-09-13.94' };
        } };
    });
    const delayedResult = await delayed.api.submit(test);
    assert.equal(delayedResult.headersElapsedMs, 10);
    assert.equal(delayedResult.elapsedMs, 25020, 'success timing must include full body parsing');
    assert.throws(() => delayed.api.validateResult(test, delayedResult), /25-second visitor ceiling/);
    assert.equal(delayed.stats().cleared, 1);
    assert.equal(delayed.stats().delay, 26000);
    console.log('Offline Ask error diagnostics PASS: 8 cases; no network calls');
})().catch(error => { console.error(error); process.exitCode = 1; });
