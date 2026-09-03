from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')
for old in ["const SOURCE_POLICY_VERSION = '2026-09-03.36';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.36';"]:
    if old not in w:
        raise SystemExit('Worker baseline anchor missing: ' + old)
w = w.replace("const SOURCE_POLICY_VERSION = '2026-09-03.36';", "const SOURCE_POLICY_VERSION = '2026-09-03.37';", 1)
w = w.replace("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.36';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.37';", 1)

old_body = """  const { response_format: _providerEnforcedFormat, ...plainJsonBody } = body;
  const groqFallbackBody = { ...plainJsonBody, model: VERIFIER_MODEL };
"""
new_body = """  const plainJsonBody = { ...body };
  const groqFallbackBody = {
    ...body,
    model: VERIFIER_MODEL,
    reasoning_effort: 'low',
    include_reasoning: false,
  };
"""
if old_body not in w:
    raise SystemExit('Groq verifier request body anchor missing')
w = w.replace(old_body, new_body, 1)

old_budget = "sanitized.scope.selectedPioneer ? 900 : (sanitized.scope.faith ? 700 : 500)"
if w.count(old_budget) < 2:
    raise SystemExit('Faith verifier budget anchors missing')
w = w.replace(old_budget, "sanitized.scope.selectedPioneer ? 900 : (sanitized.scope.faith ? 1000 : 500)")

prompt_anchor = "'Set approved true whenever the evidence contains material that can responsibly answer the question, including when DRAFT is empty. Set approved false only when the evidence is empty, unrelated, or cannot support a responsible answer. source_indexes must list the 1-based evidence sources that directly support the final answer.',"
prompt_new = prompt_anchor + "\n        'Interpret ordinary awkward grammar by its clear intended meaning. Do not reject a scripture, doctrine, or history question merely because its wording is imperfect. If the named official source directly addresses the named topic or concept, answer from that evidence.',"
if prompt_anchor not in w:
    raise SystemExit('Verifier approval prompt anchor missing')
w = w.replace(prompt_anchor, prompt_new, 1)

reconsider_anchor = "? 'Your previous rejection may be a false negative because the indexed official evidence has direct lexical relevance. Re-evaluate it once without presuming either approval or rejection.'"
reconsider_new = "? 'Your previous rejection may be a false negative because the indexed official evidence has direct lexical relevance. Re-evaluate it once without presuming either approval or rejection. Interpret awkward but understandable grammar naturally. A named scripture chapter or Church-history topic that directly addresses the requested concept is usable evidence and should not be rejected merely because the visitor phrased the question imperfectly.'"
if reconsider_anchor not in w:
    raise SystemExit('Reconsideration prompt anchor missing')
w = w.replace(reconsider_anchor, reconsider_new, 1)
worker.write_text(w, encoding='utf-8')

for path in ['tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    text = p.read_text(encoding='utf-8').replace('2026-09-03.36', '2026-09-03.37')
    p.write_text(text, encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.36';" not in mt:
    raise SystemExit('Matrix policy anchor missing')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.36';", "const POLICY_VERSION = '2026-09-03.37';", 1)
matrix.write_text(mt, encoding='utf-8')

policy = Path('groq-proxy/source-policy.test.js')
pt = policy.read_text(encoding='utf-8')
pt = pt.replace("focuschrist_source_policy === '2026-09-03.36'", "focuschrist_source_policy === '2026-09-03.37'")
old_assert = "assert(requestBody.model === 'openai/gpt-oss-20b', 'production Groq verifier must use GPT-OSS 20B');"
new_assert = "assert(requestBody.model === 'openai/gpt-oss-20b'\n    && requestBody.reasoning_effort === 'low'\n    && requestBody.include_reasoning === false\n    && requestBody.response_format && requestBody.response_format.type === 'json_object',\n    'production Groq verifier must use GPT-OSS 20B with low reasoning and JSON mode');"
if old_assert not in pt:
    raise SystemExit('Groq production verifier assertion anchor missing')
pt = pt.replace(old_assert, new_assert, 1)
policy.write_text(pt, encoding='utf-8')

index_test = Path('groq-proxy/church-source-index.test.js')
it = index_test.read_text(encoding='utf-8')
if 'max_tokens === 700' not in it:
    raise SystemExit('Indexed verifier 700-token assertions missing')
it = it.replace('max_tokens === 700', 'max_tokens === 1000')
index_test.write_text(it, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Ask verifier JSON and reasoning control - candidate 2026-09-03.37\n\n- Production .36 eliminated most prior failures but showed GPT-OSS verifier completions repeatedly exhausting the 700-token cap on some Relief Society and grace questions, while a directly relevant Alma 32 variant was still over-rejected.\n- Candidate .37 uses Groq-supported GPT-OSS controls: low reasoning effort, reasoning excluded from the response, and JSON response mode. Faith verification gets a 1,000-token completion ceiling. The verifier instructions explicitly interpret understandable awkward grammar and prohibit rejecting a named official scripture/history topic merely because the visitor phrased the question imperfectly.\n- Source integrity remains fail-closed. Official-domain restriction, source indexes, evidence relevance, depth, paraphrase, known-false-claim checks, and bounded reconsideration remain mandatory.\n"
if 'Ask verifier JSON and reasoning control - candidate 2026-09-03.37' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
