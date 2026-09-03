from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')

for old, new in [
    ("const SOURCE_POLICY_VERSION = '2026-09-03.41';", "const SOURCE_POLICY_VERSION = '2026-09-03.42';"),
    ("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.41';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.42';"),
]:
    if old not in w:
        raise SystemExit('Missing version anchor: ' + old)
    w = w.replace(old, new, 1)

scripture_end = """  return {
    url,
    title: `${ordinal}${ordinal ? ' ' : ''}${match[2]} ${chapter}${startVerse ? `:${startVerse}${endVerse > startVerse ? `-${endVerse}` : ''}` : ''}`,
    kind: 'canonical-scripture',
    priority: 250,
    tokens: normalizeDiscoveryTokens(`${match[2]} ${chapter} ${question}`).join(' '),
    deterministic: true,
  };
}

function isPioneerIrrigationIntent(question, page) {
"""
history_insert = """  return {
    url,
    title: `${ordinal}${ordinal ? ' ' : ''}${match[2]} ${chapter}${startVerse ? `:${startVerse}${endVerse > startVerse ? `-${endVerse}` : ''}` : ''}`,
    kind: 'canonical-scripture',
    priority: 250,
    tokens: normalizeDiscoveryTokens(`${match[2]} ${chapter} ${question}`).join(' '),
    deterministic: true,
  };
}

function deterministicHistoryTopicSource(question, page) {
  if (page !== 'church-history') return null;
  const queryTokens = normalizeDiscoveryTokens(question);
  if (queryTokens.length < 2) return null;
  const matches = CHURCH_SOURCE_INDEX.map((entry) => {
    if (entry.kind !== 'history-topic') return null;
    const titleTokens = normalizeDiscoveryTokens(entry.title);
    if (titleTokens.length < 2 || !titleTokens.every((token) => queryTokens.includes(token))) return null;
    return {
      ...entry,
      deterministicHistoryTopic: true,
      titleTokenCount: titleTokens.length,
      score: 900 + titleTokens.length * 25 + Number(entry.priority || 0) / 20,
      overlapCount: queryTokens.filter((token) => new Set(normalizeDiscoveryTokens(entry.tokens)).has(token)).length,
    };
  }).filter(Boolean);
  return matches.sort((left, right) => right.titleTokenCount - left.titleTokenCount
    || right.score - left.score
    || String(left.url).localeCompare(String(right.url)))[0] || null;
}

function isPioneerIrrigationIntent(question, page) {
"""
if scripture_end not in w:
    raise SystemExit('Missing deterministic scripture insertion anchor')
w = w.replace(scripture_end, history_insert, 1)

old_cache_question = """  const deterministicQuestionKey = candidate && candidate.deterministic === true
    ? normalizeDiscoveryTokens(question).slice(0, 12).join('-')
    : '';
"""
new_cache_question = """  const deterministicQuestionKey = candidate
    && (candidate.deterministic === true || candidate.deterministicHistoryTopic === true)
    ? normalizeDiscoveryTokens(question).slice(0, 12).join('-')
    : '';
"""
if old_cache_question not in w:
    raise SystemExit('Missing deterministic cache-key anchor')
w = w.replace(old_cache_question, new_cache_question, 1)

old_pack = """  const queryTokens = normalizeDiscoveryTokens(question);
  const topicPinned = Boolean(candidate && candidate.topicPinned);
  let size = 0;
  return (Array.isArray(paragraphs) ? paragraphs : []).map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const discoveryOverlap = discoveryTokens.filter((token) => tokens.has(token)).length;
    const queryOverlap = topicPinned ? queryTokens.filter((token) => tokens.has(token)).length : 0;
"""
new_pack = """  const queryTokens = normalizeDiscoveryTokens(question);
  const topicPinned = Boolean(candidate && candidate.topicPinned);
  const questionFocused = topicPinned || Boolean(candidate && candidate.deterministicHistoryTopic === true);
  let size = 0;
  return (Array.isArray(paragraphs) ? paragraphs : []).map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const discoveryOverlap = discoveryTokens.filter((token) => tokens.has(token)).length;
    const queryOverlap = questionFocused ? queryTokens.filter((token) => tokens.has(token)).length : 0;
"""
if old_pack not in w:
    raise SystemExit('Missing compact cache pack anchor')
w = w.replace(old_pack, new_pack, 1)

old_retrieve = """async function retrieveIndexedChurchEvidence(question, page, deadline) {
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
new_retrieve = """async function retrieveIndexedChurchEvidence(question, page, deadline) {
  const rankedCandidates = rankChurchSourceCandidates(question, page);
  const deterministicScripture = deterministicScriptureSource(question);
  const deterministicHistoryTopic = deterministicScripture ? null : deterministicHistoryTopicSource(question, page);
  const candidates = deterministicScripture
    ? [{ ...deterministicScripture, score: 1000, overlapCount: normalizeDiscoveryTokens(question).length }]
    : deterministicHistoryTopic
      ? [deterministicHistoryTopic]
      : rankedCandidates;
  const counters = { attempts: 0, cacheHits: 0, cacheMisses: 0 };
  const singleSource = Boolean(deterministicScripture || deterministicHistoryTopic);
  const fetchCandidates = singleSource ? candidates.slice(0, 1) : candidates.slice(0, 2);
  const fetched = await Promise.all(fetchCandidates.map((candidate) => fetchOfficialSource(candidate, question, deadline, counters)));
  const evidence = fetched.filter(Boolean).slice(0, singleSource ? 1 : 2);
  return {
    candidates,
    evidence,
    fetchCalls: counters.attempts,
    cacheHits: counters.cacheHits,
    cacheMisses: counters.cacheMisses,
    deterministicScripture: Boolean(deterministicScripture),
    deterministicHistoryTopic: Boolean(deterministicHistoryTopic),
  };
}
"""
if old_retrieve not in w:
    raise SystemExit('Missing indexed retrieval anchor')
w = w.replace(old_retrieve, new_retrieve, 1)

old_diag = """        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;
        retrievalDiagnostic.focuschrist_deterministic_scripture = indexed.deterministicScripture === true;
        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;
"""
new_diag = """        retrievalDiagnostic.focuschrist_index_sources = indexed.evidence.length;
        retrievalDiagnostic.focuschrist_deterministic_scripture = indexed.deterministicScripture === true;
        retrievalDiagnostic.focuschrist_deterministic_history_topic = indexed.deterministicHistoryTopic === true;
        retrievalDiagnostic.focuschrist_official_fetch_calls = indexed.fetchCalls;
"""
if old_diag not in w:
    raise SystemExit('Missing retrieval diagnostic anchor')
w = w.replace(old_diag, new_diag, 1)

old_prompt = """        retrievalDiagnostic.focuschrist_deterministic_scripture === true
          ? 'The visitor explicitly named a canonical scripture chapter. EVIDENCE contains that exact official scripture source and no competing research source. If its excerpt directly addresses the requested concept, compose the supported answer from it and approve it. Do not reject merely because the visitor asks for an explanation rather than a quotation.'
          : 'Evaluate the supplied official evidence normally under the source-integrity contract.',
"""
new_prompt = """        retrievalDiagnostic.focuschrist_deterministic_scripture === true
          ? 'The visitor explicitly named a canonical scripture chapter. EVIDENCE contains that exact official scripture source and no competing research source. If its excerpt directly addresses the requested concept, compose the supported answer from it and approve it. Do not reject merely because the visitor asks for an explanation rather than a quotation.'
          : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
            ? 'The visitor explicitly named an indexed Church History topic. EVIDENCE contains that exact official Church History topic and no competing research source. If its excerpt directly describes the requested event, date, purpose, or historical setting, compose the supported answer from it and approve it.'
            : 'Evaluate the supplied official evidence normally under the source-integrity contract.',
"""
if old_prompt not in w:
    raise SystemExit('Missing verifier focused-source prompt anchor')
w = w.replace(old_prompt, new_prompt, 1)

old_reconsider = """            ? (retrievalDiagnostic.focuschrist_deterministic_scripture === true
              ? 'This is the exact canonical scripture source named by the visitor. Re-read its excerpt for the requested concept. If the excerpt supports a responsible explanation, write that explanation and set approved true with source_indexes [1]. Keep approved false only if the excerpt truly lacks the requested concept.'
              : 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.')
"""
new_reconsider = """            ? (retrievalDiagnostic.focuschrist_deterministic_scripture === true
              ? 'This is the exact canonical scripture source named by the visitor. Re-read its excerpt for the requested concept. If the excerpt supports a responsible explanation, write that explanation and set approved true with source_indexes [1]. Keep approved false only if the excerpt truly lacks the requested concept.'
              : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
                ? 'This is the exact official Church History topic named by the visitor. Re-read its excerpt for the requested historical event or setting. If the excerpt supports a responsible answer, write it and set approved true with source_indexes [1]. Keep approved false only if that exact topic excerpt truly lacks the requested material.'
                : 'If the evidence can responsibly answer the question, write the supported answer and set approved true with its source indexes. If it still cannot, keep approved false.')
"""
if old_reconsider not in w:
    raise SystemExit('Missing verifier reconsideration anchor')
w = w.replace(old_reconsider, new_reconsider, 1)

# Export the deterministic named history resolver.
export_anchor = "  deterministicScriptureSource,\n"
pos = w.rfind(export_anchor)
if pos < 0:
    raise SystemExit('Missing deterministic scripture export anchor')
w = w[:pos] + w[pos:].replace(export_anchor, export_anchor + "  deterministicHistoryTopicSource,\n", 1)
worker.write_text(w, encoding='utf-8')

# Advance policy assertions.
for path in ['groq-proxy/source-policy.test.js', 'groq-proxy/church-source-index.test.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.41', '2026-09-03.42'), encoding='utf-8')

index_test = Path('groq-proxy/church-source-index.test.js')
it = index_test.read_text(encoding='utf-8')
import_anchor = "  compactParagraphPack,\n  deterministicScriptureSource,\n"
if import_anchor not in it:
    raise SystemExit('Missing history resolver import anchor')
it = it.replace(import_anchor, "  compactParagraphPack,\n  deterministicHistoryTopicSource,\n  deterministicScriptureSource,\n", 1)

alma_anchor = """assert(almaCacheKeyA && almaCacheKeyARepeat && almaCacheKeyB
  && almaCacheKeyA.url === almaCacheKeyARepeat.url
  && almaCacheKeyA.url !== almaCacheKeyB.url,
  'deterministic scripture cache keys must be stable for the same question but isolated across different question wording');
"""
history_unit = alma_anchor + """const kirtlandQuestion = 'What occurred around the 1836 dedication of the Kirtland Temple?';
const kirtlandVariant = 'What should I know about the construction of the Kirtland Temple?';
const kirtlandCandidate = deterministicHistoryTopicSource(kirtlandQuestion, 'church-history');
const kirtlandVariantCandidate = deterministicHistoryTopicSource(kirtlandVariant, 'church-history');
assert(kirtlandCandidate && kirtlandCandidate.deterministicHistoryTopic === true
  && /\/study\/history\/topics\/kirtland-temple/.test(kirtlandCandidate.url),
  'the exact production Kirtland regression must resolve to the named official Kirtland Temple history topic');
assert(deterministicHistoryTopicSource(kirtlandQuestion, 'ask') === null,
  'named Church History topic determinism must remain scoped to the Church History page');
const kirtlandCacheA = await evidenceCacheKey(kirtlandCandidate, kirtlandQuestion);
const kirtlandCacheB = await evidenceCacheKey(kirtlandVariantCandidate, kirtlandVariant);
assert(kirtlandCacheA && kirtlandCacheB && kirtlandCacheA.url !== kirtlandCacheB.url,
  'deterministic history-topic cache keys must remain question-specific');
"""
if alma_anchor not in it:
    raise SystemExit('Missing history unit-test insertion anchor')
it = it.replace(alma_anchor, history_unit, 1)

alma_retrieval_end = """globalThis.fetch = savedFetchForAlma;
if (savedCachesForAlma === undefined) delete globalThis.caches;
else globalThis.caches = savedCachesForAlma;

const approvedCandidate = rankChurchSourceCandidates('Who is Hyrum Smith?', 'ask')[0];
"""
history_retrieval = """globalThis.fetch = savedFetchForAlma;
if (savedCachesForAlma === undefined) delete globalThis.caches;
else globalThis.caches = savedCachesForAlma;

const exactKirtlandQuestion = 'What occurred around the 1836 dedication of the Kirtland Temple?';
let exactKirtlandFetchCalls = 0;
const savedCachesForKirtland = globalThis.caches;
const savedFetchForKirtland = globalThis.fetch;
delete globalThis.caches;
globalThis.fetch = async (url) => {
  exactKirtlandFetchCalls += 1;
  assert(String(url).includes('/study/history/topics/kirtland-temple'),
    'explicit Kirtland Temple history retrieval must not fetch a competing indexed source');
  return new Response('<p>On March 27, 1836, the Saints assembled for the Kirtland Temple dedication. Joseph Smith offered the revealed dedicatory prayer, and the Saints gave the Hosanna Shout and sang The Spirit of God.</p><p>At the dedication and in meetings during the following weeks, Latter-day Saints experienced dramatic outpourings of the Holy Spirit and other spiritual events in the Kirtland Temple.</p>', {
    status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' },
  });
};
const exactKirtlandEvidence = await retrieveIndexedChurchEvidence(exactKirtlandQuestion, 'church-history', Date.now() + 4000);
assert(exactKirtlandEvidence.deterministicHistoryTopic === true
  && exactKirtlandEvidence.evidence.length === 1
  && exactKirtlandEvidence.evidence[0].url.includes('/study/history/topics/kirtland-temple')
  && exactKirtlandFetchCalls === 1,
  'explicit named Church History retrieval must fetch exactly one matching official history topic');
globalThis.fetch = savedFetchForKirtland;
if (savedCachesForKirtland === undefined) delete globalThis.caches;
else globalThis.caches = savedCachesForKirtland;

const approvedCandidate = rankChurchSourceCandidates('Who is Hyrum Smith?', 'ask')[0];
"""
if alma_retrieval_end not in it:
    raise SystemExit('Missing history retrieval-test insertion anchor')
it = it.replace(alma_retrieval_end, history_retrieval, 1)
index_test.write_text(it, encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.41';" not in mt:
    raise SystemExit('Missing matrix policy anchor')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.41';", "const POLICY_VERSION = '2026-09-03.42';", 1)
reg_anchor = """    specimen('regression-alma32-deterministic-source', 'ask', 'faith-study',
        'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?',
        'faith-study', true, 'alma', /\/alma\/32/i, 'scripture'),
];
"""
reg_new = """    specimen('regression-alma32-deterministic-source', 'ask', 'faith-study',
        'Using the official scripture text, explain the seed comparison in Alma 32 teach about faith and the word?',
        'faith-study', true, 'alma', /\/alma\/32/i, 'scripture'),
    specimen('regression-kirtland-deterministic-history-topic', 'church-history', 'faith-study',
        'What occurred around the 1836 dedication of the Kirtland Temple?',
        'faith-study', true, 'kirtland', /\/history\/topics\/kirtland-temple/i, 'church-history'),
];
"""
if reg_anchor not in mt:
    raise SystemExit('Missing Kirtland production-regression insertion anchor')
mt = mt.replace(reg_anchor, reg_new, 1)
result_anchor = """            deterministicScripture: payload.focuschrist_deterministic_scripture === true,
"""
if result_anchor not in mt:
    raise SystemExit('Missing deterministic matrix receipt anchor')
mt = mt.replace(result_anchor, result_anchor + "            deterministicHistoryTopic: payload.focuschrist_deterministic_history_topic === true,\n", 1)
validate_anchor = """        if (test.id === 'regression-alma32-deterministic-source') {
            assert(result.deterministicScripture === true && result.indexSources === 1 && result.officialFetchCalls <= 1,
                test.id + ' did not prove single-source deterministic scripture retrieval');
        }
"""
validate_new = validate_anchor + """        if (test.id === 'regression-kirtland-deterministic-history-topic') {
            assert(result.deterministicHistoryTopic === true && result.indexSources === 1 && result.officialFetchCalls <= 1,
                test.id + ' did not prove single-source named Church History retrieval');
        }
"""
if validate_anchor not in mt:
    raise SystemExit('Missing Kirtland deterministic validation anchor')
mt = mt.replace(validate_anchor, validate_new, 1)
matrix.write_text(mt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Executive AI named Church History closeout - candidate 2026-09-03.42\n\n- Production .41 verified that both permanent Pioneer irrigation and Alma 32 deterministic regressions pass. The remaining live failure moved to the Kirtland burst question: What occurred around the 1836 dedication of the Kirtland Temple?\n- The official Kirtland Temple Church History topic directly documents the March 27, 1836 dedication, the revealed dedicatory prayer, Hosanna Shout, hymn, and subsequent spiritual manifestations. The failure was therefore source-selection/verifier ambiguity, not missing evidence.\n- Candidate .42 makes explicit multi-token Church History topic names deterministic on the Church History page. The exact named history topic becomes the single indexed source, uses a question-specific cache key, receives question-focused cache packing, exposes a deterministic-history receipt, and gets a focused verifier/reconsideration instruction.\n- The exact Kirtland failure is now a permanent production regression. Pioneer .40 behavior, Scripture .41 behavior, official-domain enforcement, fail-closed verification, answer-depth, paraphrase, 700-character evidence, request-budget, latency, and rate-limit controls remain unchanged.\n"
if 'Executive AI named Church History closeout - candidate 2026-09-03.42' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
