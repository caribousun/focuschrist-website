from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')
for old in ["const SOURCE_POLICY_VERSION = '2026-09-03.37';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.37';"]:
    if old not in w:
        raise SystemExit('Worker baseline anchor missing: ' + old)
w = w.replace("const SOURCE_POLICY_VERSION = '2026-09-03.37';", "const SOURCE_POLICY_VERSION = '2026-09-03.38';", 1)
w = w.replace("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.37';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.38';", 1)

old_relevance = """    const content = relevantParagraphText(paragraphs, question, candidate);
    if (!content || normalizeDiscoveryTokens(content).filter((token) => normalizeDiscoveryTokens(question).includes(token)).length < 2) return null;
"""
new_relevance = """    const content = relevantParagraphText(paragraphs, question, candidate);
    if (!content) return null;
    const questionTokenSet = new Set(normalizeDiscoveryTokens(question));
    const uniqueContentOverlap = new Set(
      normalizeDiscoveryTokens(content).filter((token) => questionTokenSet.has(token)),
    );
    if (uniqueContentOverlap.size < 2) return null;
"""
if old_relevance not in w:
    raise SystemExit('Official evidence relevance anchor missing')
w = w.replace(old_relevance, new_relevance, 1)
worker.write_text(w, encoding='utf-8')

for path in ['tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.37', '2026-09-03.38'), encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.37';" not in mt:
    raise SystemExit('Matrix policy anchor missing')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.37';", "const POLICY_VERSION = '2026-09-03.38';", 1)
matrix.write_text(mt, encoding='utf-8')

policy = Path('groq-proxy/source-policy.test.js')
pt = policy.read_text(encoding='utf-8').replace("focuschrist_source_policy === '2026-09-03.37'", "focuschrist_source_policy === '2026-09-03.38'")
policy.write_text(pt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Ask evidence relevance receipt correction - candidate 2026-09-03.38\n\n- Production .37 fixed the prior GPT-OSS truncation and false-negative problems: doctrine, scripture, Relief Society, grace, general knowledge, and most Pioneer cases passed live. One Pioneer holdout exposed a real receipt mismatch: fetch acceptance counted repeated occurrences of one query word, while the publication matrix correctly required two unique overlapping concepts.\n- Candidate .38 makes official evidence admission use the same unique-token relevance standard as the final evidence receipt. A source with one repeated matching word is rejected, allowing the next genuinely relevant indexed official source to be selected instead.\n- This does not weaken any answer gate. It tightens evidence admission so the retrieval stage and final production relevance receipt use the same standard.\n"
if 'Ask evidence relevance receipt correction - candidate 2026-09-03.38' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
