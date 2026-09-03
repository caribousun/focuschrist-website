from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

study_path = ROOT / 'study-intelligence-v3.js'
study = study_path.read_text(encoding='utf-8')
study = study.replace(
    "    const MAX_TOKENS = 1500;\n    const POLICY_VERSION = '2026-09-03.16';",
    "    const MAX_TOKENS = 1500;\n    const CLIENT_REQUEST_BUDGET_MS = 25000;\n    const CLIENT_FIRST_ATTEMPT_MS = 12000;\n    const CLIENT_RETRY_DELAY_MS = 400;\n    const CLIENT_MIN_RETRY_BUDGET_MS = 3000;\n    const POLICY_VERSION = '2026-09-03.16';"
)
start_marker = "    async function request(messages, timeoutMs, profile) {"
end_marker = "    function removeBoilerplateClosing(answer, profile) {"
start = study.index(start_marker)
end = study.index(end_marker, start)
replacement = r'''    function requestFailure(message, retryable, status) {
        const error = new Error(message);
        error.focusChristRetryable = retryable !== false;
        if (status) error.focusChristStatus = Number(status);
        return error;
    }

    function isRetryableRequestFailure(error) {
        return !error || error.focusChristRetryable !== false;
    }

    async function request(messages, timeoutMs, profile) {
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timer = controller ? window.setTimeout(function () { controller.abort(); }, Math.max(1, timeoutMs)) : null;
        try {
            const response = await fetch(PROXY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: MODEL,
                    messages: messages,
                    focuschrist_page: currentMode(),
                    focuschrist_profile: profile,
                    temperature: 0.25,
                    max_tokens: MAX_TOKENS
                }),
                signal: controller ? controller.signal : undefined
            });
            if (!response.ok) {
                const status = Number(response.status || 0);
                const retryable = status === 408 || status === 425 || status === 429 || status >= 500;
                throw requestFailure('Study service returned ' + status, retryable, status);
            }
            let data;
            try {
                data = await response.json();
            } catch (error) {
                const malformed = requestFailure('Study service returned invalid JSON', true);
                malformed.cause = error;
                throw malformed;
            }
            const content = data && data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : '';
            if (!content) throw requestFailure('Empty study response', true);
            return {
                content: String(content).trim(),
                sources: Array.isArray(data.focuschrist_sources) ? data.focuschrist_sources : [],
                serverVerified: data.focuschrist_source_integrity_verified === true,
                gatewayMode: String(data.focuschrist_gateway_mode || ''),
                policyVersion: String(data.focuschrist_source_policy || ''),
                resolvedProfile: String(data.focuschrist_resolved_profile || ''),
                classificationMode: String(data.focuschrist_classification_mode || ''),
                providerStatus: Number(data.focuschrist_provider_status || 0),
                providerCode: String(data.focuschrist_provider_code || '')
            };
        } finally {
            if (timer) window.clearTimeout(timer);
        }
    }

    async function requestWithRetry(messages, profile) {
        const started = Date.now();
        const remainingBudget = function () {
            return Math.max(0, CLIENT_REQUEST_BUDGET_MS - (Date.now() - started));
        };
        let firstError = null;
        try {
            const first = await request(messages, Math.min(CLIENT_FIRST_ATTEMPT_MS, remainingBudget()), profile);
            first.clientAttempts = 1;
            return first;
        } catch (error) {
            firstError = error;
            if (!isRetryableRequestFailure(error)) throw error;
        }

        if (remainingBudget() <= CLIENT_RETRY_DELAY_MS + CLIENT_MIN_RETRY_BUDGET_MS) throw firstError;
        await new Promise(function (resolve) { window.setTimeout(resolve, CLIENT_RETRY_DELAY_MS); });
        const retryBudget = remainingBudget();
        if (retryBudget < CLIENT_MIN_RETRY_BUDGET_MS) throw firstError;

        try {
            const second = await request(messages, retryBudget, profile);
            second.clientAttempts = 2;
            return second;
        } catch (error) {
            error.focusChristClientAttempts = 2;
            throw error;
        }
    }

'''
study = study[:start] + replacement + study[end:]
study = study.replace(
    "                const researched = await request(messages, 25000, profile);",
    "                const researched = await requestWithRetry(messages, profile);"
)
study = study.replace(
    "                    providerCode: researched.providerCode,\n                    contextResolved:",
    "                    providerCode: researched.providerCode,\n                    clientAttempts: researched.clientAttempts || 1,\n                    contextResolved:"
)
study_path.write_text(study, encoding='utf-8')

qa_path = ROOT / 'tools/study_intelligence_qa.py'
qa = qa_path.read_text(encoding='utf-8')
qa = qa.replace('"request(messages, 25000, profile)",', '"requestWithRetry(messages, profile)",\n        "CLIENT_FIRST_ATTEMPT_MS = 12000",\n        "CLIENT_RETRY_DELAY_MS = 400",')
qa = qa.replace('one bounded browser request, safe rendering, serialized cache-versioned loading', 'one bounded automatic browser retry for transient failures, safe rendering, serialized cache-versioned loading')
qa_path.write_text(qa, encoding='utf-8')

runtime_path = ROOT / 'tools/study_intelligence_v3_runtime_qa.js'
runtime = runtime_path.read_text(encoding='utf-8')
runtime = runtime.replace(
    'let forceWorkerRateLimit = false;\n',
    'let forceWorkerRateLimit = false;\nlet transientFailuresRemaining = 0;\nlet nonRetryableStatus = 0;\n'
)
runtime = runtime.replace(
    "    requestBodies.push(body);\n    if (forceWorkerRateLimit) {",
    "    requestBodies.push(body);\n    if (transientFailuresRemaining > 0) {\n        transientFailuresRemaining -= 1;\n        throw new TypeError('Injected transient network failure');\n    }\n    if (nonRetryableStatus) {\n        return { ok: false, status: nonRetryableStatus, statusText: 'Injected non-retryable failure' };\n    }\n    if (forceWorkerRateLimit) {"
)
anchor = "    assert(dom.userInput.disabled === false && dom.sendBtn.disabled === false && dom.sendBtn.textContent === 'Ask',\n        'question boundaries must leave Ask controls ready');\n"
retry_tests = r'''

    window.focusChristCancelAskRequests();
    const beforeTransientRetry = fetchCalls;
    transientFailuresRemaining = 1;
    result = await window.focusChristStudyAskV3('Tell me about Old Testament', '');
    assert(fetchCalls === beforeTransientRetry + 2
        && result.answer === 'RESEARCHED VERIFIED ANSWER'
        && result.clientAttempts === 2,
        'a transient first-request failure must retry once and return the successful verified answer');
    assert(!/temporarily unavailable/i.test(result.answer),
        'a recovered transient request must never render the unavailable message');

    const beforeVerifiedPolicyResult = fetchCalls;
    forceWorkerRateLimit = true;
    result = await window.focusChristStudyAskV3('What does Genesis teach about creation?', '');
    forceWorkerRateLimit = false;
    assert(fetchCalls === beforeVerifiedPolicyResult + 1 && result.clientAttempts === 1,
        'a completed HTTP 200 policy response must not trigger client verifier shopping');

    const beforeExhaustedRetry = fetchCalls;
    transientFailuresRemaining = 2;
    result = await window.focusChristStudyAskV3('Tell me about Old Testament history', '');
    assert(fetchCalls === beforeExhaustedRetry + 2
        && /answer service is temporarily unavailable/i.test(result.answer),
        'two transient failures must stop after one retry and return the visible bounded fallback');

    const beforeNonRetryable = fetchCalls;
    nonRetryableStatus = 400;
    result = await window.focusChristStudyAskV3('Tell me about Old Testament books', '');
    nonRetryableStatus = 0;
    assert(fetchCalls === beforeNonRetryable + 1
        && /answer service is temporarily unavailable/i.test(result.answer),
        'a non-retryable 4xx response must not create a duplicate request');
'''
if anchor not in runtime:
    raise SystemExit('runtime insertion anchor not found')
runtime = runtime.replace(anchor, anchor + retry_tests)
runtime_path.write_text(runtime, encoding='utf-8')

common_path = ROOT / 'site-common.js'
common = common_path.read_text(encoding='utf-8')
if "study-intelligence-v3.js?v=20260903-16" not in common:
    raise SystemExit('site-common v3 cache marker not found')
common = common.replace("study-intelligence-v3.js?v=20260903-16", "study-intelligence-v3.js?v=20260903-17")
common_path.write_text(common, encoding='utf-8')

for name in ['ask.html', 'pioneers.html']:
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    if 'site-common.js?v=20260903-16' not in text:
        raise SystemExit(f'{name} site-common cache marker not found')
    path.write_text(text.replace('site-common.js?v=20260903-16', 'site-common.js?v=20260903-17'), encoding='utf-8')

memory_path = ROOT / 'MEMORY.md'
memory = memory_path.read_text(encoding='utf-8')
note = "\n- 2026-09-03: Main Ask/Pioneer v3 client transport now performs one bounded automatic retry only for transient network/timeouts, HTTP 408/425/429/5xx, malformed JSON, or empty transport responses. Successful HTTP 200 policy/verifier outcomes are never retried, preserving fail-closed verification semantics. Total browser request budget remains 25 seconds; first attempt is capped at 12 seconds and the retry uses only the remaining budget after a 400 ms delay. Runtime QA permanently covers the owner-reported `Tell me about Old Testament` transient-failure recovery, two-attempt ceiling, no retry after completed policy responses, and no duplicate retry for non-retryable 4xx responses.\n"
if note.strip() not in memory:
    memory += note
memory_path.write_text(memory, encoding='utf-8')
