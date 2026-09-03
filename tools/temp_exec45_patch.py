from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')

for old, new in [
    ("const SOURCE_POLICY_VERSION = '2026-09-03.44';", "const SOURCE_POLICY_VERSION = '2026-09-03.45';"),
    ("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.44';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.45';"),
]:
    if old not in w:
        raise SystemExit('Missing version anchor: ' + old)
    w = w.replace(old, new, 1)

const_anchor = "const GROQ_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions';\n"
const_insert = const_anchor + "const OPENAI_VERIFIER_MODEL = 'gpt-5.6-luna';\nconst OPENAI_ENDPOINT = 'https://api.openai.com/v1/chat/completions';\n"
if const_anchor not in w:
    raise SystemExit('Missing Groq endpoint anchor')
w = w.replace(const_anchor, const_insert, 1)

call_groq_end = """  return { response, data, callCount: 1 };
}

function verifierContent(result) {
"""
openai_func = """  return { response, data, callCount: 1 };
}

async function callOpenAIVerifier(apiKey, body, deadline) {
  if (!apiKey) return { ...providerFailure(503, 'service_unavailable'), openaiCallCount: 0 };
  const available = remainingBudget(deadline);
  if (available < 250) return { ...providerFailure(504, 'timeout'), openaiCallCount: 0 };
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutMs = Math.max(200, Math.min(PROVIDER_CALL_LIMIT_MS, available - 50));
  const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
  let response;
  try {
    response = await fetch(OPENAI_ENDPOINT, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: OPENAI_VERIFIER_MODEL,
        messages: body.messages,
        reasoning_effort: 'low',
        max_completion_tokens: Math.max(300, Number(body.max_tokens || 0)),
        response_format: body.response_format || { type: 'json_object' },
        store: false,
      }),
      signal: controller ? controller.signal : undefined,
    });
  } catch (error) {
    return {
      ...providerFailure(error && error.name === 'AbortError' ? 504 : 503,
        error && error.name === 'AbortError' ? 'timeout' : 'service_unavailable'),
      openaiCallCount: 1,
    };
  } finally {
    if (timer) clearTimeout(timer);
  }
  let data = null;
  try { data = await response.json(); } catch (_error) {}
  return {
    response,
    data,
    openaiCallCount: 1,
    openaiRequestId: String(response.headers.get('x-request-id') || ''),
  };
}

function verifierContent(result) {
"""
if call_groq_end not in w:
    raise SystemExit('Missing callGroq end anchor')
w = w.replace(call_groq_end, openai_func, 1)

route_anchor = """  const groqCalls = Number(result && result.totalGroqVerifierCalls
    || (route === 'groq-fallback' ? result && result.callCount || 0 : 0));
  diagnostic.focuschrist_cloudflare_verifier_calls = Math.max(0, cloudflareCalls);
  diagnostic.focuschrist_groq_verifier_calls = Math.max(0, groqCalls);
"""
route_insert = """  const groqCalls = Number(result && result.totalGroqVerifierCalls
    || (route === 'groq-fallback' ? result && result.callCount || 0 : 0));
  const openaiCalls = Number(result && result.totalOpenAIVerifierCalls
    || result && result.openaiCallCount
    || (route === 'openai-fallback' ? 1 : 0));
  diagnostic.focuschrist_cloudflare_verifier_calls = Math.max(0, cloudflareCalls);
  diagnostic.focuschrist_groq_verifier_calls = Math.max(0, groqCalls);
  diagnostic.focuschrist_openai_verifier_calls = Math.max(0, openaiCalls);
"""
if route_anchor not in w:
    raise SystemExit('Missing verifier route accounting anchor')
w = w.replace(route_anchor, route_insert, 1)

acc_anchor = """  target.totalGroqVerifierCalls = results.reduce((sum, result) => {
    const diagnostic = verifierRouteDiagnostic(result);
    return sum + Number(diagnostic.focuschrist_groq_verifier_calls || 0);
  }, 0);
  target.totalCloudflareEstimatedNeurons = results.reduce((sum, result) => sum + Number(
"""
acc_insert = """  target.totalGroqVerifierCalls = results.reduce((sum, result) => {
    const diagnostic = verifierRouteDiagnostic(result);
    return sum + Number(diagnostic.focuschrist_groq_verifier_calls || 0);
  }, 0);
  target.totalOpenAIVerifierCalls = results.reduce((sum, result) => {
    const diagnostic = verifierRouteDiagnostic(result);
    return sum + Number(diagnostic.focuschrist_openai_verifier_calls || 0);
  }, 0);
  target.totalCloudflareEstimatedNeurons = results.reduce((sum, result) => sum + Number(
"""
if acc_anchor not in w:
    raise SystemExit('Missing verifier accumulation anchor')
w = w.replace(acc_anchor, acc_insert, 1)

old_groq_branch = """    if (primary.formatContract && remainingBudget(deadline) >= MIN_RETRY_BUDGET_MS) {
      const repairPrompt = [
        String(plainJsonBody.messages && plainJsonBody.messages[0] && plainJsonBody.messages[0].content || ''),
        '',
        'FORMAT REPAIR: Return only one complete valid JSON object matching the requested schema. Do not use markdown fences, commentary, citations outside the JSON, or trailing text.'
      ].join('\\n');
      const repairBody = {
        ...groqFallbackBody,
        messages: [{ role: 'user', content: repairPrompt }],
        max_tokens: Math.max(Number(groqFallbackBody.max_tokens || 0), 700),
      };
      const repair = validateGroqVerifierResult(
        await callGroq(env && env.GROQ_KEY_NEW, repairBody, deadline, false),
        requireSourceIndexes,
      );
      repair.accumulatedUsage = combinedProviderUsage(primaryRaw, repair);
      return {
        ...repair,
        verifierRoute: 'groq-primary-repair',
        fallbackReason: repair.response && repair.response.ok ? 'format-repair' : 'format-repair-failed',
        totalCloudflareVerifierCalls: 0,
        totalCloudflareEstimatedNeurons: 0,
        totalCloudflareUnmeteredNeurons: 0,
        totalGroqVerifierCalls: Number(primaryRaw.callCount || 1) + Number(repair.callCount || 1),
        verifierDurationMs: Date.now() - started,
      };
    }
    return {
      ...primary,
      verifierRoute: 'groq-primary',
      fallbackReason: 'groq-primary-error',
      totalCloudflareVerifierCalls: 0,
      totalCloudflareEstimatedNeurons: 0,
      totalCloudflareUnmeteredNeurons: 0,
      totalGroqVerifierCalls: Number(primary.callCount || 1),
      verifierDurationMs: Date.now() - started,
    };
"""
new_groq_branch = """    const primaryStatus = Number(primary && primary.response && primary.response.status || 0);
    const primaryFallbackReason = primary.formatContract || (primary.response && primary.response.ok)
      ? 'format-contract'
      : (primaryStatus === 429
        ? 'primary-rate-limited'
        : (primaryStatus === 504 ? 'primary-timeout' : 'primary-unavailable'));
    if (env && env.OPENAI_API_KEY && remainingBudget(deadline) >= MIN_RETRY_BUDGET_MS) {
      const openaiRaw = await callOpenAIVerifier(env.OPENAI_API_KEY, plainJsonBody, deadline);
      const openaiFallback = validateVerifierResult(openaiRaw, requireSourceIndexes);
      openaiFallback.accumulatedUsage = combinedProviderUsage(primaryRaw, openaiFallback);
      return {
        ...openaiFallback,
        verifierRoute: 'openai-fallback',
        fallbackReason: primaryFallbackReason,
        primaryDiagnostic: providerDiagnostic(primary),
        accumulatedUsage: combinedProviderUsage(primaryRaw, openaiFallback),
        totalCloudflareVerifierCalls: 0,
        totalCloudflareEstimatedNeurons: 0,
        totalCloudflareUnmeteredNeurons: 0,
        totalGroqVerifierCalls: Number(primaryRaw.callCount || primary.callCount || 1),
        totalOpenAIVerifierCalls: Number(openaiRaw.openaiCallCount || 1),
        verifierDurationMs: Date.now() - started,
      };
    }
    if (primary.formatContract && remainingBudget(deadline) >= MIN_RETRY_BUDGET_MS) {
      const repairPrompt = [
        String(plainJsonBody.messages && plainJsonBody.messages[0] && plainJsonBody.messages[0].content || ''),
        '',
        'FORMAT REPAIR: Return only one complete valid JSON object matching the requested schema. Do not use markdown fences, commentary, citations outside the JSON, or trailing text.'
      ].join('\\n');
      const repairBody = {
        ...groqFallbackBody,
        messages: [{ role: 'user', content: repairPrompt }],
        max_tokens: Math.max(Number(groqFallbackBody.max_tokens || 0), 700),
      };
      const repair = validateGroqVerifierResult(
        await callGroq(env && env.GROQ_KEY_NEW, repairBody, deadline, false),
        requireSourceIndexes,
      );
      repair.accumulatedUsage = combinedProviderUsage(primaryRaw, repair);
      return {
        ...repair,
        verifierRoute: 'groq-primary-repair',
        fallbackReason: repair.response && repair.response.ok ? 'format-repair' : 'format-repair-failed',
        totalCloudflareVerifierCalls: 0,
        totalCloudflareEstimatedNeurons: 0,
        totalCloudflareUnmeteredNeurons: 0,
        totalGroqVerifierCalls: Number(primaryRaw.callCount || 1) + Number(repair.callCount || 1),
        totalOpenAIVerifierCalls: 0,
        verifierDurationMs: Date.now() - started,
      };
    }
    return {
      ...primary,
      verifierRoute: 'groq-primary',
      fallbackReason: 'groq-primary-error',
      totalCloudflareVerifierCalls: 0,
      totalCloudflareEstimatedNeurons: 0,
      totalCloudflareUnmeteredNeurons: 0,
      totalGroqVerifierCalls: Number(primary.callCount || 1),
      totalOpenAIVerifierCalls: 0,
      verifierDurationMs: Date.now() - started,
    };
"""
if old_groq_branch not in w:
    raise SystemExit('Missing Groq primary fallback branch')
w = w.replace(old_groq_branch, new_groq_branch, 1)

export_anchor = "  callGroq,\n"
pos = w.rfind(export_anchor)
if pos < 0:
    raise SystemExit('Missing callGroq export anchor')
w = w[:pos] + w[pos:].replace(export_anchor, export_anchor + "  callOpenAIVerifier,\n", 1)
worker.write_text(w, encoding='utf-8')

# Advance policy assertions.
for path in ['groq-proxy/source-policy.test.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.44', '2026-09-03.45'), encoding='utf-8')

# Add explicit OpenAI fallback policy test.
source_test = Path('groq-proxy/source-policy.test.js')
st = source_test.read_text(encoding='utf-8')
import_anchor = "  callGroq,\n  callCloudflareVerifier,\n"
if import_anchor not in st:
    raise SystemExit('Missing source-policy import anchor')
st = st.replace(import_anchor, "  callGroq,\n  callOpenAIVerifier,\n  callCloudflareVerifier,\n", 1)
insert_anchor = """assert(directGroqVerifierCalls === 1
  && directGroqVerifierResult.response.ok
  && directGroqVerifierResult.verifierRoute === 'groq-primary'
  && directGroqVerifierResult.totalCloudflareVerifierCalls === 0
  && directGroqVerifierResult.totalGroqVerifierCalls === 1,
  'production verifier route must use exactly one Groq Compound Mini call and zero Cloudflare calls');

"""
insert_test = insert_anchor + """const fetchBeforeOpenAIFallback = globalThis.fetch;
let groqThenOpenAICalls = 0;
let openAIBodyForFallback;
globalThis.fetch = async (url, init) => {
  groqThenOpenAICalls += 1;
  if (String(url).includes('api.groq.com')) {
    return new Response(JSON.stringify({ error: { code: 'service_unavailable' } }), {
      status: 503, headers: { 'Content-Type': 'application/json' },
    });
  }
  assert(String(url) === 'https://api.openai.com/v1/chat/completions',
    'Groq provider failure must fall back only to the OpenAI verifier endpoint');
  openAIBodyForFallback = JSON.parse(init.body);
  assert(init.headers.Authorization === 'Bearer openai-test-key',
    'OpenAI fallback must use the server-owned OpenAI secret');
  return new Response(JSON.stringify({
    choices: [{ message: { content: '{"approved":true,"answer":"Supported answer.","source_indexes":[1]}' } }],
    usage: { prompt_tokens: 180, completion_tokens: 28 },
  }), { status: 200, headers: { 'Content-Type': 'application/json', 'x-request-id': 'req_focus_test' } });
};
const openAIFallbackResult = await callVerifier({
  GROQ_KEY_NEW: 'groq-test-key',
  OPENAI_API_KEY: 'openai-test-key',
  VERIFIER_PROVIDER: 'groq',
}, verifierBodyForTest, Date.now() + 12000, { requireSourceIndexes: true });
globalThis.fetch = fetchBeforeOpenAIFallback;
assert(groqThenOpenAICalls === 2
  && openAIFallbackResult.response.ok
  && openAIFallbackResult.verifierRoute === 'openai-fallback'
  && openAIFallbackResult.fallbackReason === 'primary-unavailable'
  && openAIFallbackResult.totalGroqVerifierCalls === 1
  && openAIFallbackResult.totalOpenAIVerifierCalls === 1
  && openAIFallbackResult.totalCloudflareVerifierCalls === 0
  && openAIBodyForFallback.model === 'gpt-5.6-luna'
  && openAIBodyForFallback.reasoning_effort === 'low'
  && openAIBodyForFallback.response_format.type === 'json_object'
  && openAIBodyForFallback.store === false,
  'a true Groq provider failure must use exactly one GPT-5.6 Luna fallback call with the same verifier contract');

"""
if insert_anchor not in st:
    raise SystemExit('Missing direct Groq test anchor')
st = st.replace(insert_anchor, insert_test, 1)
source_test.write_text(st, encoding='utf-8')

# Update live production matrix for OpenAI fallback accounting and route.
matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.44';", "const POLICY_VERSION = '2026-09-03.45';", 1)
result_anchor = """            groqVerifierCalls: Number(payload.focuschrist_groq_verifier_calls || 0),
            conservativeUnmeteredNeurons: Number(payload.focuschrist_verifier_conservative_unmetered_neurons || 0),
"""
result_insert = """            groqVerifierCalls: Number(payload.focuschrist_groq_verifier_calls || 0),
            openaiVerifierCalls: Number(payload.focuschrist_openai_verifier_calls || 0),
            conservativeUnmeteredNeurons: Number(payload.focuschrist_verifier_conservative_unmetered_neurons || 0),
"""
if result_anchor not in mt:
    raise SystemExit('Missing matrix provider receipt anchor')
mt = mt.replace(result_anchor, result_insert, 1)
route_validate = """        assert(['groq-primary', 'groq-primary-repair', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute), test.id + ' omitted a verifier route');
"""
route_new = """        assert(['groq-primary', 'groq-primary-repair', 'openai-fallback', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute), test.id + ' omitted a verifier route');
"""
if route_validate not in mt:
    raise SystemExit('Missing matrix route allowlist anchor')
mt = mt.replace(route_validate, route_new, 1)
account_anchor = """        assert(result.cloudflareVerifierCalls >= 0 && result.cloudflareVerifierCalls <= 2
            && result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2
            && result.cloudflareVerifierCalls + result.groqVerifierCalls >= 1,
        test.id + ' returned invalid per-provider verifier call accounting');
        assert(!(result.groqVerifierCalls > 0 && result.cloudflareVerifierCalls > 1),
            test.id + ' stacked verifier fallback with depth repair');
"""
account_new = """        assert(result.cloudflareVerifierCalls >= 0 && result.cloudflareVerifierCalls <= 2
            && result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2
            && result.openaiVerifierCalls >= 0 && result.openaiVerifierCalls <= 1
            && result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls >= 1
            && result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls <= 2,
        test.id + ' returned invalid per-provider verifier call accounting');
        assert(!(result.openaiVerifierCalls > 0 && (result.cloudflareVerifierCalls > 0 || result.groqVerifierCalls !== 1)),
            test.id + ' stacked OpenAI failover beyond the two-provider ceiling');
        assert(!(result.groqVerifierCalls > 0 && result.cloudflareVerifierCalls > 1),
            test.id + ' stacked verifier fallback with depth repair');
"""
if account_anchor not in mt:
    raise SystemExit('Missing matrix call-accounting anchor')
mt = mt.replace(account_anchor, account_new, 1)
matrix.write_text(mt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Executive AI independent verifier failover - candidate 2026-09-03.45\n\n- Production .44 confirmed the depth-margin repair but later encountered true Groq provider failures with zero verifier tokens on otherwise valid official-source questions. This identified Groq availability as the remaining single point of failure.\n- The owner created a dedicated FocusChrist OpenAI project, enforced a $5 monthly hard spend limit, restricted model use to GPT-5.6 Luna, created a project service account, and stored its key in the production Worker as the OPENAI_API_KEY secret.\n- Candidate .45 keeps Groq GPT-OSS 20B as the primary verifier. A genuine Groq provider failure, rate limit, timeout, or malformed verifier contract can use exactly one independent OpenAI GPT-5.6 Luna verifier call, preserving the overall two-provider-call ceiling. Valid Groq approvals and valid Groq rejections never shop for a second opinion.\n- OpenAI fallback uses the same source-index requirement and fail-closed verifier schema, low reasoning effort, JSON response mode, no response storage, and the existing shared request deadline. Source routing, official-domain requirements, evidence relevance, local-reviewed first routing, Pioneer/Scripture/History determinism, safety, and publication-depth gates remain unchanged.\n"
if 'Executive AI independent verifier failover - candidate 2026-09-03.45' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
