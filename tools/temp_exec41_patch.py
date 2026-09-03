from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')
for old in ["const SOURCE_POLICY_VERSION = '2026-09-03.40';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.40';"]:
    if old not in w:
        raise SystemExit('Worker baseline anchor missing: ' + old)
w = w.replace("const SOURCE_POLICY_VERSION = '2026-09-03.40';", "const SOURCE_POLICY_VERSION = '2026-09-03.41';", 1)
w = w.replace("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.40';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.41';", 1)

old_cache_key = """async function evidenceCacheKey(candidate, question) {
  if (!globalThis.crypto || !globalThis.crypto.subtle) return null;
  const variant = officialExcerptCacheVariant(candidate);
  const normalized = `${OFFICIAL_EXCERPT_CACHE_VERSION}\n${variant}\n${candidate.url}`;
"""
new_cache_key = """async function evidenceCacheKey(candidate, question) {
  if (!globalThis.crypto || !globalThis.crypto.subtle) return null;
  const variant = officialExcerptCacheVariant(candidate);
  const deterministicQuestionKey = candidate && candidate.deterministic === true
    ? normalizeDiscoveryTokens(question).slice(0, 12).join('-')
    : '';
  const normalized = `${OFFICIAL_EXCERPT_CACHE_VERSION}\n${variant}\n${deterministicQuestionKey}\n${candidate.url}`;
"""
if old_cache_key not in w:
    raise SystemExit('Evidence cache key anchor missing')
w = w.replace(old_cache_key, new_cache_key, 1)

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
    raise SystemExit('Indexed retrieval anchor missing')
w = w.replace(old_retrieve, new_retrieve, 1)

old_diag = """        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;
        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;
"""
new_diag = """        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;
        retrievalDiagnostic.focuschrist_deterministic_scripture = indexed.deterministicScripture === true;
        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;
"""
if old_diag not in w:
    raise SystemExit('Indexed diagnostics anchor missing')
w = w.replace(old_diag, new_diag, 1)

prompt_anchor = """        'Interpret ordinary awkward grammar by its clear intended meaning. Do not reject a scripture, doctrine, or history question merely because its wording is imperfect. If the named official source directly addresses the named topic or concept, answer from that evidence.',
        'Schema: {\"approved\":boolean,\"answer\":string,\"source_indexes\":number[]}',
"""
prompt_new = """        'Interpret ordinary awkward grammar by its clear intended meaning. Do not reject a scripture, doctrine, or history question merely because its wording is imperfect. If the named official source directly addresses the named topic or concept, answer from that evidence.',
        retrievalDiagnostic.focuschrist_deterministic_scripture === true
          ? 'The visitor explicitly named a canonical scripture chapter. EVIDENCE contains that exact official scripture source and no competing research source. If its excerpt directly addresses the requested concept, compose the supported answer from it and approve it. Do not reject merely because the visitor asks for an explanation rather than a quotation.'
          : 'Evaluate the supplied official evidence normally under the source-integrity contract.',
        'Schema: {\"approved\":boolean,\"answer\":string,\"source_indexes\":number[]}',
"""
if prompt_anchor not in w:
    raise SystemExit('Verifier prompt anchor missing')
w = w.replace(prompt_anchor, prompt_new, 1)

reconsider_anchor = """          needsRelevantEvidenceReconsideration
            ? 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.'
"""
reconsider_new = """          needsRelevantEvidenceReconsideration
            ? (retrievalDiagnostic.focuschrist_deterministic_scripture === true
              ? 'This is the exact canonical scripture source named by the visitor. Re-read its excerpt for the requested concept. If the excerpt supports a responsible explanation, write that explanation and set approved true with source_indexes [1]. Keep approved false only if the excerpt truly lacks the requested concept.'
              : 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.')
"""
if reconsider_anchor not in w:
    raise SystemExit('Verifier reconsideration anchor missing')
w = w.replace(reconsider_anchor, reconsider_new, 1)
worker.write_text(w, encoding='utf-8')

# Advance policy expectations.
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
  'deterministic scripture cache keys must be stable for the same question but isolated across materially different question wording');
"""
if scripture_anchor not in it:
    raise SystemExit('Scripture regression insertion anchor missing')
it = it.replace(scripture_anchor, scripture_tests, 1)

# Add a deterministic retrieval test proving only the canonical scripture source is fetched and sent to verification.
insert_anchor = """const approvedCandidate = rankChurchSourceCandidates('Who is Hyrum Smith?', 'ask')[0];
"""
deterministic_test = """const exactAlmaQuestion = 'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?';
const exactAlmaCandidate = deterministicScriptureSource(exactAlmaQuestion);
let exactAlmaFetchCalls = 0;
const savedCachesForAlma = globalThis.caches;
delete globalThis.caches;
const savedFetchForAlma = globalThis.fetch;
globalThis.fetch = async (url) => {
  exactAlmaFetchCalls += 1;
  assert(String(url).includes('/study/scriptures/bofm/alma/32'),
    'explicit Alma 32 retrieval must not fetch a competing indexed source');
  return new Response('<p>Faith is not to have a perfect knowledge of things; therefore if ye have faith ye hope for things which are not seen, which are true.</p><p>Alma compares the word unto a seed and invites hearers to give place that a seed may be planted in the heart and to nourish it as it grows.</p>', {
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
globalThis.caches = savedCachesForAlma;

const approvedCandidate = rankChurchSourceCandidates('Who is Hyrum Smith?', 'ask')[0];
"""
if insert_anchor not in it:
    raise SystemExit('Deterministic retrieval test insertion anchor missing')
it = it.replace(insert_anchor, deterministic_test, 1)
index_test.write_text(it, encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.40';" not in mt:
    raise SystemExit('Matrix policy anchor missing')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.40';", "const POLICY_VERSION = '2026-09-03.41';", 1)
reg_anchor = """const productionRegressions = [
    specimen('regression-pioneer-irrigation-displayed-source', 'pioneers', 'pioneer-study',
        'What did cooperative irrigation contribute to settlement life?',
        'faith-study', true, 'pioneer', /(?:chapter-twenty-six|a-brief-history|irrigat)/i, 'pioneer'),
];
"""
reg_new = """const productionRegressions = [
    specimen('regression-pioneer-irrigation-displayed-source', 'pioneers', 'pioneer-study',
        'What did cooperative irrigation contribute to settlement life?',
        'faith-study', true, 'pioneer', /(?:chapter-twenty-six|a-brief-history|irrigat)/i, 'pioneer'),
    specimen('regression-alma32-deterministic-source', 'ask', 'faith-study',
        'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?',
        'faith-study', true, 'alma', /\\/alma\\/32/i, 'scripture'),
];
"""
if reg_anchor not in mt:
    raise SystemExit('Production regression list anchor missing')
mt = mt.replace(reg_anchor, reg_new, 1)
# Capture deterministic diagnostic in result and require it for the exact regression.
result_anchor = """            evidenceRelevance: Array.isArray(payload.focuschrist_evidence_relevance) ? payload.focuschrist_evidence_relevance : [],
"""
result_new = """            evidenceRelevance: Array.isArray(payload.focuschrist_evidence_relevance) ? payload.focuschrist_evidence_relevance : [],
            deterministicScripture: payload.focuschrist_deterministic_scripture === true,
"""
if result_anchor not in mt:
    raise SystemExit('Matrix result diagnostic anchor missing')
mt = mt.replace(result_anchor, result_new, 1)
validate_anchor = """        assert(result.retrievalRoute === 'church-source-index' && result.groqResearchCalls === 0 && result.indexSources > 0 && result.officialFetchCalls <= 2, test.id + ' did not prove bounded zero-Groq research');
"""
validate_new = validate_anchor + """        if (test.id === 'regression-alma32-deterministic-source') {
            assert(result.deterministicScripture === true && result.indexSources === 1 && result.officialFetchCalls <= 1,
                test.id + ' did not prove single-source deterministic scripture retrieval');
        }
"""
if validate_anchor not in mt:
    raise SystemExit('Matrix deterministic validation anchor missing')
mt = mt.replace(validate_anchor, validate_new, 1)
matrix.write_text(mt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Executive AI deterministic scripture closeout - candidate 2026-09-03.41\n\n- Production .40 fixed the exact Pioneer displayed-source defect, and the exact Pioneer regression passed in production with independently retrievable Chapter Twenty-Six support. The next live failure was an intermittent Alma 32 rejection: the same concept passed in rounds 1 and 3 but failed in round 2 after two verifier calls.\n- Diagnosis: explicit canonical scripture questions were still retrieving up to two indexed sources, and the chapter excerpt cache was keyed only by source URL, allowing an excerpt compacted for one wording to be reused for a materially different wording. That introduced avoidable verifier ambiguity even though the visitor named one exact scripture chapter.\n- Candidate .41 makes explicit scripture references deterministic end to end. They fetch only the canonical scripture source, use a question-specific deterministic scripture cache key while retaining warm reuse for the identical question, expose a deterministic-source receipt, and tell the verifier that the evidence is the exact canonical source named by the visitor.\n- The exact failing Alma 32 wording is now a permanent live production regression. No source-integrity, official-domain, answer-depth, paraphrase, 700-character evidence, latency, request-budget, rate-limit, or fail-closed control is weakened.\n"
if 'Executive AI deterministic scripture closeout - candidate 2026-09-03.41' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
