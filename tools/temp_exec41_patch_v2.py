from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')

for old, new in [
    ("const SOURCE_POLICY_VERSION = '2026-09-03.40';", "const SOURCE_POLICY_VERSION = '2026-09-03.41';"),
    ("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.40';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.41';"),
]:
    if old not in w:
        raise SystemExit('Missing version anchor: ' + old)
    w = w.replace(old, new, 1)

old_normalized = r"  const normalized = `${OFFICIAL_EXCERPT_CACHE_VERSION}\n${variant}\n${candidate.url}`;"
new_normalized = r"""  const deterministicQuestionKey = candidate && candidate.deterministic === true
    ? normalizeDiscoveryTokens(question).slice(0, 12).join('-')
    : '';
  const normalized = `${OFFICIAL_EXCERPT_CACHE_VERSION}\n${variant}\n${deterministicQuestionKey}\n${candidate.url}`;"""
if old_normalized not in w:
    raise SystemExit('Missing cache normalized line')
w = w.replace(old_normalized, new_normalized, 1)

old_retrieve = """async function retrieveIndexedChurchEvidence(question, page, deadline) {
  const candidates = rankChurchSourceCandidates(question, page);
  const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
  const fetched = await Promise.all(candidates.slice(0, 2).map((candidate) => fetchOfficialSource(candidate, question, deadline, counters)));
  const evidence = fetched.filter(Boolean).slice(0, 2);
  return { candidates, evidence, fetchCalls: counters.attempts, cacheHits: counters.cacheHits, cacheMisses: counters.cacheMisses };
}
"""
new_retrieve = """async function retrieveIndexedChurchEvidence(question, page, deadline) {
  const rankedCandidates = rankChurchSourceCandidates(question, page);
  const deterministicScripture = deterministicScriptureSource(question);
  const candidates = deterministicScripture
    ? [{ ...deterministicScripture, score: 1000, overlapCount: normalizeDiscoveryTokens(question).length }]
    : rankedCandidates;
  const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
  const fetchCandidates = deterministicScripture ? candidates.slice(0, 1) : candidates.slice(0, 2);
  const fetched = await Promise.all(fetchCandidates.map((candidate) => fetchOfficialSource(candidate, question, deadline, counters)));
  const evidence = fetched.filter(Boolean).slice(0, deterministicScripture ? 1 : 2);
  return {
    candidates,
    evidence,
    fetchCalls: counters.attempts,
    cacheHits: counters.cacheHits,
    cacheMisses: counters.cacheMisses,
    deterministicScripture: Boolean(deterministicScripture),
  };
}
"""
if old_retrieve not in w:
    raise SystemExit('Missing retrieveIndexedChurchEvidence block')
w = w.replace(old_retrieve, new_retrieve, 1)

old_diag = "        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;\n        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;"
new_diag = "        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;\n        retrievalDiagnostic.focuschrist_deterministic_scripture = indexed.deterministicScripture === true;\n        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;"
if old_diag not in w:
    raise SystemExit('Missing retrieval diagnostic anchor')
w = w.replace(old_diag, new_diag, 1)

prompt_line = "        'Interpret ordinary awkward grammar by its clear intended meaning. Do not reject a scripture, doctrine, or history question merely because its wording is imperfect. If the named official source directly addresses the named topic or concept, answer from that evidence.',"
prompt_extra = prompt_line + "\n        retrievalDiagnostic.focuschrist_deterministic_scripture === true\n          ? 'The visitor explicitly named a canonical scripture chapter. EVIDENCE contains that exact official scripture source and no competing research source. If its excerpt directly addresses the requested concept, compose the supported answer from it and approve it. Do not reject merely because the visitor asks for an explanation rather than a quotation.'\n          : 'Evaluate the supplied official evidence normally under the source-integrity contract.',"
if prompt_line not in w:
    raise SystemExit('Missing verifier prompt line')
w = w.replace(prompt_line, prompt_extra, 1)

old_reconsider = "            ? 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.'"
new_reconsider = "            ? (retrievalDiagnostic.focuschrist_deterministic_scripture === true\n              ? 'This is the exact canonical scripture source named by the visitor. Re-read its excerpt for the requested concept. If the excerpt supports a responsible explanation, write that explanation and set approved true with source_indexes [1]. Keep approved false only if the excerpt truly lacks the requested concept.'\n              : 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.')"
if old_reconsider not in w:
    raise SystemExit('Missing reconsideration line')
w = w.replace(old_reconsider, new_reconsider, 1)
worker.write_text(w, encoding='utf-8')

for path in ['groq-proxy/source-policy.test.js', 'groq-proxy/church-source-index.test.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.40', '2026-09-03.41'), encoding='utf-8')

index_test = Path('groq-proxy/church-source-index.test.js')
it = index_test.read_text(encoding='utf-8')
scripture_anchor = """assert(deterministicScriptureSource('Tell me about Alma Smith') === null,
  'a person name must not be misclassified as a scripture reference');
"""
scripture_tests = scripture_anchor + """const almaChapterQuestion = 'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?';
const almaChapterVariant = 'What lesson does Alma chapter 32 give about faith growing?';
const almaChapterCandidate = deterministicScriptureSource(almaChapterQuestion);
assert(almaChapterCandidate && almaChapterCandidate.deterministic === true,
  'the exact production Alma 32 regression must resolve to a deterministic canonical scripture source');
const almaCacheKeyA = await evidenceCacheKey(almaChapterCandidate, almaChapterQuestion);
const almaCacheKeyARepeat = await evidenceCacheKey(almaChapterCandidate, almaChapterQuestion);
const almaCacheKeyB = await evidenceCacheKey(deterministicScriptureSource(almaChapterVariant), almaChapterVariant);
assert(almaCacheKeyA && almaCacheKeyARepeat && almaCacheKeyB
  && almaCacheKeyA.url === almaCacheKeyARepeat.url
  && almaCacheKeyA.url !== almaCacheKeyB.url,
  'deterministic scripture cache keys must be stable for the same question but isolated across different question wording');
"""
if scripture_anchor not in it:
    raise SystemExit('Missing scripture test anchor')
it = it.replace(scripture_anchor, scripture_tests, 1)

insert_anchor = "const approvedCandidate = rankChurchSourceCandidates('Who is Hyrum Smith?', 'ask')[0];\n"
deterministic_test = """const exactAlmaQuestion = 'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?';
const exactAlmaCandidate = deterministicScriptureSource(exactAlmaQuestion);
let exactAlmaFetchCalls = 0;
const savedCachesForAlma = globalThis.caches;
const savedFetchForAlma = globalThis.fetch;
delete globalThis.caches;
globalThis.fetch = async (url) => {
  exactAlmaFetchCalls += 1;
  assert(String(url).includes('/study/scriptures/bofm/alma/32'),
    'explicit Alma 32 retrieval must not fetch a competing indexed source');
  return new Response('<p>Faith is not to have a perfect knowledge of things; if people have faith they hope for things which are not seen, which are true.</p><p>Alma compares the word unto a seed and invites hearers to give place that a seed may be planted in the heart and nourished as it grows.</p>', {
    status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' },
  });
};
const exactAlmaEvidence = await retrieveIndexedChurchEvidence(exactAlmaQuestion, 'ask', Date.now() + 4000);
assert(exactAlmaCandidate
  && exactAlmaEvidence.deterministicScripture === true
  && exactAlmaEvidence.evidence.length === 1
  && exactAlmaEvidence.evidence[0].url.includes('/study/scriptures/bofm/alma/32')
  && exactAlmaFetchCalls === 1,
  'explicit canonical scripture retrieval must fetch exactly one deterministic official scripture source');
globalThis.fetch = savedFetchForAlma;
if (savedCachesForAlma === undefined) delete globalThis.caches;
else globalThis.caches = savedCachesForAlma;

const approvedCandidate = rankChurchSourceCandidates('Who is Hyrum Smith?', 'ask')[0];
"""
if insert_anchor not in it:
    raise SystemExit('Missing deterministic retrieval insertion anchor')
it = it.replace(insert_anchor, deterministic_test, 1)
index_test.write_text(it, encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.40';" not in mt:
    raise SystemExit('Missing matrix policy anchor')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.40';", "const POLICY_VERSION = '2026-09-03.41';", 1)
reg_close = """    specimen('regression-pioneer-irrigation-displayed-source', 'pioneers', 'pioneer-study',
        'What did cooperative irrigation contribute to settlement life?',
        'faith-study', true, 'pioneer', /(?:chapter-twenty-six|a-brief-history|irrigat)/i, 'pioneer'),
];
"""
reg_new = """    specimen('regression-pioneer-irrigation-displayed-source', 'pioneers', 'pioneer-study',
        'What did cooperative irrigation contribute to settlement life?',
        'faith-study', true, 'pioneer', /(?:chapter-twenty-six|a-brief-history|irrigat)/i, 'pioneer'),
    specimen('regression-alma32-deterministic-source', 'ask', 'faith-study',
        'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?',
        'faith-study', true, 'alma', /\\/alma\\/32/i, 'scripture'),
];
"""
if reg_close not in mt:
    raise SystemExit('Missing production regression list anchor')
mt = mt.replace(reg_close, reg_new, 1)
result_line = "            evidenceRelevance: Array.isArray(payload.focuschrist_evidence_relevance) ? payload.focuschrist_evidence_relevance : [],"
if result_line not in mt:
    raise SystemExit('Missing matrix result line')
mt = mt.replace(result_line, result_line + "\n            deterministicScripture: payload.focuschrist_deterministic_scripture === true,", 1)
validation_line = "        assert(result.retrievalRoute === 'church-source-index' && result.groqResearchCalls === 0 && result.indexSources > 0 && result.officialFetchCalls <= 2, test.id + ' did not prove bounded zero-Groq research');"
if validation_line not in mt:
    raise SystemExit('Missing matrix validation line')
mt = mt.replace(validation_line, validation_line + "\n        if (test.id === 'regression-alma32-deterministic-source') {\n            assert(result.deterministicScripture === true && result.indexSources === 1 && result.officialFetchCalls <= 1,\n                test.id + ' did not prove single-source deterministic scripture retrieval');\n        }", 1)
matrix.write_text(mt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Executive AI deterministic scripture closeout - candidate 2026-09-03.41\n\n- Production .40 fixed the exact Pioneer displayed-source defect. The next live failure was an intermittent Alma 32 rejection: the same concept passed in rounds 1 and 3 but failed in round 2 after two verifier calls.\n- Explicit canonical scripture questions were still retrieving up to two indexed sources, and the chapter excerpt cache was keyed only by source URL, allowing an excerpt compacted for one wording to be reused for materially different wording.\n- Candidate .41 makes explicit scripture references deterministic end to end: one canonical official scripture source, a question-specific deterministic scripture cache key with warm reuse for the identical question, a deterministic-source receipt, and verifier instructions recognizing that the evidence is the exact canonical source named by the visitor.\n- The exact failing Alma 32 wording is now a permanent production regression. All source-integrity, official-domain, answer-depth, paraphrase, 700-character evidence, latency, request-budget, rate-limit, and fail-closed controls remain unchanged.\n"
if 'Executive AI deterministic scripture closeout - candidate 2026-09-03.41' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
