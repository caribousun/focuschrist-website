from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')
for old in ["const VERIFIER_MODEL = 'groq/compound-mini';", "const SOURCE_POLICY_VERSION = '2026-09-03.35';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.35';"]:
    if old not in w:
        raise SystemExit('Worker baseline anchor missing: ' + old)
w = w.replace("const VERIFIER_MODEL = 'groq/compound-mini';", "const VERIFIER_MODEL = 'openai/gpt-oss-20b';", 1)
w = w.replace("const SOURCE_POLICY_VERSION = '2026-09-03.35';", "const SOURCE_POLICY_VERSION = '2026-09-03.36';", 1)
w = w.replace("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.35';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.36';", 1)

old_parse = """function parseVerifierJson(text) {
  const raw = String(text || '').trim().replace(/^```(?:json)?\\s*/i, '').replace(/\\s*```$/i, '');
  try { return JSON.parse(raw); } catch (_error) { return null; }
}
"""
new_parse = """function parseVerifierJson(text) {
  const raw = String(text || '').trim().replace(/^```(?:json)?\\s*/i, '').replace(/\\s*```$/i, '');
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (_error) {}
  const firstBrace = raw.indexOf('{');
  const lastBrace = raw.lastIndexOf('}');
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    try { return JSON.parse(raw.slice(firstBrace, lastBrace + 1)); } catch (_error) {}
  }
  return null;
}
"""
if old_parse not in w:
    raise SystemExit('parseVerifierJson anchor missing')
w = w.replace(old_parse, new_parse, 1)

old_groq = """  if (String(env && env.VERIFIER_PROVIDER || '').toLowerCase() === 'groq') {
    const primary = validateGroqVerifierResult(
      await callGroq(env && env.GROQ_KEY_NEW, groqFallbackBody, deadline, false),
      requireSourceIndexes,
    );
    return {
      ...primary,
      verifierRoute: 'groq-primary',
      fallbackReason: primary.response && primary.response.ok ? null : 'groq-primary-error',
      totalCloudflareVerifierCalls: 0,
      totalCloudflareEstimatedNeurons: 0,
      totalCloudflareUnmeteredNeurons: 0,
      totalGroqVerifierCalls: Number(primary.callCount || 1),
      verifierDurationMs: Date.now() - started,
    };
  }
"""
new_groq = """  if (String(env && env.VERIFIER_PROVIDER || '').toLowerCase() === 'groq') {
    const primaryRaw = await callGroq(env && env.GROQ_KEY_NEW, groqFallbackBody, deadline, false);
    const primary = validateGroqVerifierResult(primaryRaw, requireSourceIndexes);
    if (primary.response && primary.response.ok) {
      return {
        ...primary,
        verifierRoute: 'groq-primary',
        fallbackReason: null,
        totalCloudflareVerifierCalls: 0,
        totalCloudflareEstimatedNeurons: 0,
        totalCloudflareUnmeteredNeurons: 0,
        totalGroqVerifierCalls: Number(primary.callCount || 1),
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
  }
"""
if old_groq not in w:
    raise SystemExit('Groq primary verifier anchor missing')
w = w.replace(old_groq, new_groq, 1)
w = w.replace("max_tokens: sanitized.scope.selectedPioneer ? 900 : 400,", "max_tokens: sanitized.scope.selectedPioneer ? 900 : (sanitized.scope.faith ? 700 : 500),", 2)
w = w.replace("&& verifierResult.verifierRoute === 'cloudflare-primary'", "&& ['cloudflare-primary', 'groq-primary'].includes(verifierResult.verifierRoute)", 1)
worker.write_text(w, encoding='utf-8')

for path in ['tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.35', '2026-09-03.36'), encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.35';", "const POLICY_VERSION = '2026-09-03.36';", 1)
mt = mt.replace("['groq-primary', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute)", "['groq-primary', 'groq-primary-repair', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute)")
mt = mt.replace("result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 1", "result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2")
matrix.write_text(mt, encoding='utf-8')

policy = Path('groq-proxy/source-policy.test.js')
pt = policy.read_text(encoding='utf-8')
pt = pt.replace("focuschrist_source_policy === '2026-09-03.35'", "focuschrist_source_policy === '2026-09-03.36'")
pt = pt.replace("requestBody.model === 'groq/compound-mini'", "requestBody.model === 'openai/gpt-oss-20b'", 1)
pt = pt.replace("'production Groq verifier must use Compound Mini'", "'production Groq verifier must use GPT-OSS 20B'", 1)
policy.write_text(pt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Ask final verifier hardening - candidate 2026-09-03.36\n\n- Production .35 proved the provider-route correction worked: Groq verification returned successful source-grounded answers for several doctrine, general, scripture, and Pioneer cases with zero Cloudflare calls. The remaining matrix failures were verifier-format failures and false-negative rejections, not source-index failure.\n- Candidate .36 separates research and verification models again: Compound Mini remains research-only; Groq GPT-OSS 20B is the verification model. The verifier parser now tolerates harmless wrapper text, one bounded JSON-format repair is permitted, faith answers receive a larger completion budget, and the existing evidence-reconsideration/depth-repair path now works on Groq primary as well as Cloudflare primary.\n- Quality gates remain fail-closed. Final source indexes, official-domain rules, substance requirements, overlap controls, and known-false-claim guards remain mandatory.\n"
if 'Ask final verifier hardening - candidate 2026-09-03.36' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
