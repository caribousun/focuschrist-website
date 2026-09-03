from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')
for old, new in [
    ("const SOURCE_POLICY_VERSION = '2026-09-03.45';", "const SOURCE_POLICY_VERSION = '2026-09-03.46';"),
    ("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.45';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.46';"),
]:
    if old not in w: raise SystemExit('missing version anchor ' + old)
    w = w.replace(old, new, 1)

options_anchor = """async function callVerifier(env, body, deadline, options = {}) {
  const started = Date.now();
  const requireSourceIndexes = options.requireSourceIndexes === true;
  const allowGroqFallback = options.allowGroqFallback !== false;
"""
options_new = """async function callVerifier(env, body, deadline, options = {}) {
  const started = Date.now();
  const requireSourceIndexes = options.requireSourceIndexes === true;
  const allowGroqFallback = options.allowGroqFallback !== false;
  const forceOpenAI = options.forceOpenAI === true;
"""
if options_anchor not in w: raise SystemExit('missing callVerifier option anchor')
w = w.replace(options_anchor, options_new, 1)

before_groq = """  const groqFallbackBody = {
    ...body,
    model: VERIFIER_MODEL,
    reasoning_effort: 'low',
    include_reasoning: false,
  };
  if (String(env && env.VERIFIER_PROVIDER || '').toLowerCase() === 'groq') {
"""
force_block = """  const groqFallbackBody = {
    ...body,
    model: VERIFIER_MODEL,
    reasoning_effort: 'low',
    include_reasoning: false,
  };
  if (forceOpenAI) {
    const forcedRaw = await callOpenAIVerifier(env && env.OPENAI_API_KEY, plainJsonBody, deadline);
    const forced = validateVerifierResult(forcedRaw, requireSourceIndexes);
    return {
      ...forced,
      verifierRoute: 'openai-repair',
      fallbackReason: 'bounded-reconsideration',
      totalCloudflareVerifierCalls: 0,
      totalCloudflareEstimatedNeurons: 0,
      totalCloudflareUnmeteredNeurons: 0,
      totalGroqVerifierCalls: 0,
      totalOpenAIVerifierCalls: Number(forcedRaw.openaiCallCount || 0),
      verifierDurationMs: Date.now() - started,
    };
  }
  if (String(env && env.VERIFIER_PROVIDER || '').toLowerCase() === 'groq') {
"""
if before_groq not in w: raise SystemExit('missing pre-Groq anchor')
w = w.replace(before_groq, force_block, 1)

condition_old = """      if ((needsDepthRepair || needsParaphraseRepair || needsRelevantEvidenceReconsideration)
        && ['cloudflare-primary', 'groq-primary'].includes(verifierResult.verifierRoute)
        && remainingBudget(deadline) >= 4500) {
"""
condition_new = """      if ((needsDepthRepair || needsParaphraseRepair || needsRelevantEvidenceReconsideration)
        && ['cloudflare-primary', 'groq-primary', 'openai-fallback'].includes(verifierResult.verifierRoute)
        && remainingBudget(deadline) >= 4500) {
"""
if condition_old not in w: raise SystemExit('missing expansion route condition')
w = w.replace(condition_old, condition_new, 1)

expand_opts = """        }, deadline, {
          requireSourceIndexes: true,
          allowGroqFallback: false,
        });
"""
expand_opts_new = """        }, deadline, {
          requireSourceIndexes: true,
          allowGroqFallback: false,
          forceOpenAI: verifierResult.verifierRoute === 'openai-fallback',
        });
"""
if expand_opts not in w: raise SystemExit('missing expansion options anchor')
w = w.replace(expand_opts, expand_opts_new, 1)

copy_anchor = """          totalCloudflareVerifierCalls: expansionResult.totalCloudflareVerifierCalls,
          totalGroqVerifierCalls: expansionResult.totalGroqVerifierCalls,
          totalCloudflareEstimatedNeurons: expansionResult.totalCloudflareEstimatedNeurons,
"""
copy_new = """          totalCloudflareVerifierCalls: expansionResult.totalCloudflareVerifierCalls,
          totalGroqVerifierCalls: expansionResult.totalGroqVerifierCalls,
          totalOpenAIVerifierCalls: expansionResult.totalOpenAIVerifierCalls,
          totalCloudflareEstimatedNeurons: expansionResult.totalCloudflareEstimatedNeurons,
"""
if copy_anchor not in w: raise SystemExit('missing accumulated copy anchor')
w = w.replace(copy_anchor, copy_new, 1)
worker.write_text(w, encoding='utf-8')

for path in ['groq-proxy/source-policy.test.js','tools/pioneer_local_first_qa.py','tools/scripture_grounding_qa.py']:
    p=Path(path); p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.45','2026-09-03.46'),encoding='utf-8')

stp=Path('groq-proxy/source-policy.test.js'); st=stp.read_text(encoding='utf-8')
unit_anchor = """assert(groqThenOpenAICalls === 2
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
unit_new = unit_anchor + """const fetchBeforeForcedOpenAIRepair = globalThis.fetch;
let forcedOpenAIRepairCalls = 0;
globalThis.fetch = async (url, init) => {
  forcedOpenAIRepairCalls += 1;
  assert(String(url) === 'https://api.openai.com/v1/chat/completions',
    'bounded Luna reconsideration must not return to Groq');
  const requestBody = JSON.parse(init.body);
  assert(requestBody.model === 'gpt-5.6-luna', 'bounded Luna reconsideration must remain on the allowed project model');
  return new Response(JSON.stringify({
    choices: [{ message: { content: '{"approved":true,"answer":"Supported reconsidered answer.","source_indexes":[1]}' } }],
    usage: { prompt_tokens: 210, completion_tokens: 34 },
  }), { status: 200, headers: { 'Content-Type': 'application/json' } });
};
const forcedOpenAIRepairResult = await callVerifier({
  OPENAI_API_KEY: 'openai-test-key',
  VERIFIER_PROVIDER: 'groq',
}, verifierBodyForTest, Date.now() + 12000, { requireSourceIndexes: true, forceOpenAI: true });
globalThis.fetch = fetchBeforeForcedOpenAIRepair;
assert(forcedOpenAIRepairCalls === 1
  && forcedOpenAIRepairResult.response.ok
  && forcedOpenAIRepairResult.verifierRoute === 'openai-repair'
  && forcedOpenAIRepairResult.totalGroqVerifierCalls === 0
  && forcedOpenAIRepairResult.totalOpenAIVerifierCalls === 1,
  'a relevant-evidence reconsideration after OpenAI failover must use exactly one additional Luna call and no Groq call');

"""
if unit_anchor not in st: raise SystemExit('missing OpenAI fallback unit anchor')
st=st.replace(unit_anchor,unit_new,1); stp.write_text(st,encoding='utf-8')

mp=Path('tools/live_ai_response_matrix.js'); mt=mp.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.45';" not in mt: raise SystemExit('missing matrix version')
mt=mt.replace("const POLICY_VERSION = '2026-09-03.45';","const POLICY_VERSION = '2026-09-03.46';",1)
route_old="""        assert(['groq-primary', 'groq-primary-repair', 'openai-fallback', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute), test.id + ' omitted a verifier route');
"""
route_new="""        assert(['groq-primary', 'groq-primary-repair', 'openai-fallback', 'openai-repair', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute), test.id + ' omitted a verifier route');
"""
if route_old not in mt: raise SystemExit('missing route allowlist')
mt=mt.replace(route_old,route_new,1)
acct_old="""        assert(result.cloudflareVerifierCalls >= 0 && result.cloudflareVerifierCalls <= 2
            && result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2
            && result.openaiVerifierCalls >= 0 && result.openaiVerifierCalls <= 1
            && result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls >= 1
            && result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls <= 2,
        test.id + ' returned invalid per-provider verifier call accounting');
        assert(!(result.openaiVerifierCalls > 0 && (result.cloudflareVerifierCalls > 0 || result.groqVerifierCalls !== 1)),
            test.id + ' stacked OpenAI failover beyond the two-provider ceiling');
"""
acct_new="""        const verifierCallTotal = result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls;
        assert(result.cloudflareVerifierCalls >= 0 && result.cloudflareVerifierCalls <= 2
            && result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2
            && result.openaiVerifierCalls >= 0 && result.openaiVerifierCalls <= 2
            && verifierCallTotal >= 1 && verifierCallTotal <= 3,
        test.id + ' returned invalid per-provider verifier call accounting');
        assert(!(result.openaiVerifierCalls > 0 && result.cloudflareVerifierCalls > 0),
            test.id + ' mixed Cloudflare and OpenAI verifier routes');
        assert(!(result.openaiVerifierCalls === 2 && result.groqVerifierCalls !== 1),
            test.id + ' used two Luna calls without one failed Groq primary attempt');
"""
if acct_old not in mt: raise SystemExit('missing matrix accounting block')
mt=mt.replace(acct_old,acct_new,1)
mp.write_text(mt,encoding='utf-8')

mem=Path('MEMORY.md'); text=mem.read_text(encoding='utf-8')
note="\n\n### Executive AI Luna reconsideration closeout - candidate 2026-09-03.46\n\n- Production .45 proved the OPENAI_API_KEY survives Worker deployment and that GPT-5.6 Luna successfully verifies official-source answers when Groq is unavailable. It also exposed false-negative Luna rejections on strongly relevant Church History and Pioneer evidence.\n- Candidate .46 extends the existing bounded evidence-reconsideration/depth-repair mechanism to an OpenAI failover verdict. After one failed Groq primary and one Luna fallback, a third and final provider call may be made only when the server already has strongly relevant indexed evidence or the Luna answer needs the existing depth/paraphrase repair. That repair call is forced directly to Luna and never returns to Groq.\n- Normal successful requests remain one verifier call. A simple provider failover remains two calls. Three calls are permitted only for failed-primary plus bounded Luna repair, under the same 22-second request deadline and $5 OpenAI project hard limit. Official-source restrictions, source indexes, fail-closed publication, deterministic routing, and all answer guards remain unchanged.\n"
if 'Executive AI Luna reconsideration closeout - candidate 2026-09-03.46' not in text: mem.write_text(text+note,encoding='utf-8')
