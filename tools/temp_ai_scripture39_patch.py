from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')
for old in ["const SOURCE_POLICY_VERSION = '2026-09-03.38';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.38';"]:
    if old not in w:
        raise SystemExit('Worker baseline anchor missing: ' + old)
w = w.replace("const SOURCE_POLICY_VERSION = '2026-09-03.38';", "const SOURCE_POLICY_VERSION = '2026-09-03.39';", 1)
w = w.replace("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.38';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.39';", 1)

old_relevant = """function relevantParagraphText(paragraphs, question, candidate = null) {
  const queryTokens = normalizeDiscoveryTokens(question);
  const topicPinned = Boolean(candidate && candidate.topicPinned);
  return (Array.isArray(paragraphs) ? paragraphs : []).map((text) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const overlap = queryTokens.filter((token) => tokens.has(token)).length;
    const pinnedIrrigation = topicPinned && /\\birrigat\\w*\\b/i.test(text);
    const pinnedSettlement = topicPinned && /\\b(?:settlement\\w*|communit\\w*|pioneer\\w*|salt\\s+lake\\s+valley)\\b/i.test(text);
    const topicScore = (pinnedIrrigation ? 240 : 0) + (pinnedSettlement ? 40 : 0);
    return { text, overlap, topicScore, score: topicScore + overlap * 20 + Math.min(10, text.length / 180) };
  }).filter((item) => item.overlap > 0 || item.topicScore > 0)
    .sort((left, right) => right.score - left.score)
    .slice(0, 2).map((item) => item.text).join(' ').slice(0, 700);
}
"""
new_relevant = """function relevantParagraphText(paragraphs, question, candidate = null) {
  const sourceParagraphs = Array.isArray(paragraphs) ? paragraphs : [];
  const queryTokens = normalizeDiscoveryTokens(question);
  const topicPinned = Boolean(candidate && candidate.topicPinned);
  const selected = sourceParagraphs.map((text, position) => {
    const tokens = new Set(normalizeDiscoveryTokens(text));
    const overlap = queryTokens.filter((token) => tokens.has(token)).length;
    const pinnedIrrigation = topicPinned && /\\birrigat\\w*\\b/i.test(text);
    const pinnedSettlement = topicPinned && /\\b(?:settlement\\w*|communit\\w*|pioneer\\w*|salt\\s+lake\\s+valley)\\b/i.test(text);
    const topicScore = (pinnedIrrigation ? 240 : 0) + (pinnedSettlement ? 40 : 0);
    return { text, position, overlap, topicScore, score: topicScore + overlap * 20 + Math.min(10, text.length / 180) };
  }).filter((item) => item.overlap > 0 || item.topicScore > 0)
    .sort((left, right) => right.score - left.score)
    .slice(0, 2);
  if (candidate && candidate.deterministic === true && selected.length) {
    const positions = new Set();
    selected.forEach((item) => {
      for (let offset = 0; offset <= 3; offset += 1) {
        const position = item.position + offset;
        if (position >= 0 && position < sourceParagraphs.length) positions.add(position);
      }
    });
    return Array.from(positions).sort((left, right) => left - right)
      .map((position) => sourceParagraphs[position]).join(' ').slice(0, 700);
  }
  return selected.map((item) => item.text).join(' ').slice(0, 700);
}

function uniqueEvidenceOverlapCount(content, question) {
  const questionTokenSet = new Set(normalizeDiscoveryTokens(question));
  return new Set(normalizeDiscoveryTokens(content).filter((token) => questionTokenSet.has(token))).size;
}
"""
if old_relevant not in w:
    raise SystemExit('Relevant paragraph function anchor missing')
w = w.replace(old_relevant, new_relevant, 1)

old_cache = """          const content = relevantParagraphText(payload.paragraphs, question, candidate);
          if (content) {
            if (counters) counters.cacheHits += 1;
            const source = canonicalSource(candidate.url, candidate.title, content);
            if (source) source.cacheStatus = 'hit';
            return source;
          }
"""
new_cache = """          const content = relevantParagraphText(payload.paragraphs, question, candidate);
          if (content && uniqueEvidenceOverlapCount(content, question) >= 2) {
            if (counters) counters.cacheHits += 1;
            const source = canonicalSource(candidate.url, candidate.title, content);
            if (source) source.cacheStatus = 'hit';
            return source;
          }
"""
if old_cache not in w:
    raise SystemExit('Cache relevance anchor missing')
w = w.replace(old_cache, new_cache, 1)

old_fresh = """    if (!content) return null;
    const questionTokenSet = new Set(normalizeDiscoveryTokens(question));
    const uniqueContentOverlap = new Set(
      normalizeDiscoveryTokens(content).filter((token) => questionTokenSet.has(token)),
    );
    if (uniqueContentOverlap.size < 2) return null;
"""
new_fresh = """    if (!content || uniqueEvidenceOverlapCount(content, question) < 2) return null;
"""
if old_fresh not in w:
    raise SystemExit('Fresh relevance anchor missing')
w = w.replace(old_fresh, new_fresh, 1)
worker.write_text(w, encoding='utf-8')

for path in ['tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.38', '2026-09-03.39'), encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.38';" not in mt:
    raise SystemExit('Matrix policy anchor missing')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.38';", "const POLICY_VERSION = '2026-09-03.39';", 1)
matrix.write_text(mt, encoding='utf-8')

policy = Path('groq-proxy/source-policy.test.js')
pt = policy.read_text(encoding='utf-8').replace("focuschrist_source_policy === '2026-09-03.38'", "focuschrist_source_policy === '2026-09-03.39'")
policy.write_text(pt, encoding='utf-8')

index_test = Path('groq-proxy/church-source-index.test.js')
it = index_test.read_text(encoding='utf-8')
it = it.replace("""const cachedPioneerParagraphs = [
  'Pioneer families planned water channels as the settlement took root in the valley.',
];
const cachedPioneerResponse = () => new Response(JSON.stringify({ paragraphs: cachedPioneerParagraphs }), {
  headers: { 'Content-Type': 'application/json' },
});
""", """const cachedPioneerParagraphs = [
  'Pioneer families planned water channels as the settlement took root in the valley.',
];
const cachedRelevantPioneerParagraphs = [
  'Cooperative irrigation supported settlement life as pioneer families planned shared water channels in the valley.',
];
const cachedPioneerResponse = (paragraphs = cachedPioneerParagraphs) => new Response(JSON.stringify({ paragraphs }), {
  headers: { 'Content-Type': 'application/json' },
});
""", 1)
it = it.replace("""async function runPioneerReconsiderationCase({ page, profile, question, omitPinnedSource = false, approveSecond = false }) {""", """async function runPioneerReconsiderationCase({ page, profile, question, omitPinnedSource = false, approveSecond = false, cacheParagraphs = cachedPioneerParagraphs }) {""", 1)
it = it.replace("""        : cachedPioneerResponse()),""", """        : cachedPioneerResponse(cacheParagraphs)),""", 1)
old_positive = """try {
  const positive = await runPioneerReconsiderationCase({
    page: 'pioneers',
    profile: 'pioneer-study',
    question: 'Why did cooperative irrigation contribute to settlement life?',
    approveSecond: true,
  });
  assert(positive.verifierCalls === 2
    && positive.groqCalls === 0
    && positive.officialFetchCalls === 0
    && positive.payload.focuschrist_source_integrity_verified === true
    && positive.payload.focuschrist_cloudflare_verifier_calls === 2
    && positive.payload.focuschrist_groq_verifier_calls === 0
    && positive.payload.focuschrist_sources.some((entry) => entry.url.includes('/chapter-twenty-six'))
    && positive.payload.focuschrist_evidence_relevance.length > 0
    && positive.payload.focuschrist_evidence_relevance.every((entry) => entry.overlap_count < 2)
    && REQUEST_BUDGET_MS === 22000,
  'cached sub-threshold chapter 26 evidence must alone enable one bounded Cloudflare reconsideration inside the unchanged request budget');

  const askNegative = await runPioneerReconsiderationCase({
"""
new_positive = """try {
  const subThreshold = await runPioneerReconsiderationCase({
    page: 'pioneers',
    profile: 'pioneer-study',
    question: 'Why did cooperative irrigation contribute to settlement life?',
  });
  assert(subThreshold.verifierCalls === 0
    && subThreshold.groqCalls === 0
    && subThreshold.officialFetchCalls >= 1
    && subThreshold.payload.focuschrist_source_integrity_verified !== true
    && subThreshold.payload.focuschrist_gateway_mode === 'research-unavailable',
  'cached evidence below the two-unique-concept relevance floor must be rejected before verification');

  const positive = await runPioneerReconsiderationCase({
    page: 'pioneers',
    profile: 'pioneer-study',
    question: 'Why did cooperative irrigation contribute to settlement life?',
    approveSecond: true,
    cacheParagraphs: cachedRelevantPioneerParagraphs,
  });
  assert(positive.verifierCalls === 2
    && positive.groqCalls === 0
    && positive.officialFetchCalls === 0
    && positive.payload.focuschrist_source_integrity_verified === true
    && positive.payload.focuschrist_cloudflare_verifier_calls === 2
    && positive.payload.focuschrist_groq_verifier_calls === 0
    && positive.payload.focuschrist_sources.some((entry) => entry.url.includes('/chapter-twenty-six'))
    && positive.payload.focuschrist_evidence_relevance.length > 0
    && positive.payload.focuschrist_evidence_relevance.every((entry) => entry.overlap_count >= 2)
    && REQUEST_BUDGET_MS === 22000,
  'cached relevant chapter 26 evidence must enable one bounded reconsideration inside the unchanged request budget');

  const askNegative = await runPioneerReconsiderationCase({
"""
if old_positive not in it:
    raise SystemExit('Pioneer reconsideration positive test anchor missing')
it = it.replace(old_positive, new_positive, 1)
it = it.replace("""  assert(askNegative.verifierCalls === 1
    && askNegative.groqCalls === 0
    && askNegative.payload.focuschrist_cloudflare_verifier_calls === 1
    && askNegative.payload.focuschrist_source_integrity_verified !== true,
  'the same sub-threshold irrigation wording on general Ask must not receive the Pioneer reconsideration');
""", """  assert(askNegative.verifierCalls === 0
    && askNegative.groqCalls === 0
    && askNegative.officialFetchCalls >= 1
    && askNegative.payload.focuschrist_source_integrity_verified !== true,
  'sub-threshold cached irrigation evidence on general Ask must be rejected before verification');
""", 1)
it = it.replace("""  assert(unrelatedNegative.verifierCalls === 1
    && unrelatedNegative.groqCalls === 0
    && unrelatedNegative.payload.focuschrist_cloudflare_verifier_calls === 1
    && unrelatedNegative.payload.focuschrist_source_integrity_verified !== true,
  'unrelated Pioneer cooperation must not receive the irrigation reconsideration');
""", """  assert(unrelatedNegative.verifierCalls === 0
    && unrelatedNegative.groqCalls === 0
    && unrelatedNegative.officialFetchCalls >= 1
    && unrelatedNegative.payload.focuschrist_source_integrity_verified !== true,
  'unrelated cached Pioneer evidence must be rejected before verification');
""", 1)
it = it.replace("""  assert(missingPinnedNegative.verifierCalls === 1
    && missingPinnedNegative.groqCalls === 0
    && missingPinnedNegative.officialFetchCalls >= 1
    && missingPinnedNegative.payload.focuschrist_cloudflare_verifier_calls === 1
    && missingPinnedNegative.payload.focuschrist_source_integrity_verified !== true,
  'Pioneer irrigation without the exact chapter 26 evidence must not receive the pinned-source reconsideration');
""", """  assert(missingPinnedNegative.verifierCalls === 0
    && missingPinnedNegative.groqCalls === 0
    && missingPinnedNegative.officialFetchCalls >= 1
    && missingPinnedNegative.payload.focuschrist_source_integrity_verified !== true,
  'Pioneer irrigation without relevant cached chapter 26 evidence must fail before verification');
""", 1)
index_test.write_text(it, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Ask cached relevance and deterministic scripture context - candidate 2026-09-03.39\n\n- Production .38 confirmed the new unique-relevance rule on fresh official fetches, but live testing exposed that cached excerpts still bypassed that rule. The same run also showed a clear Alma 32 question can be over-rejected when retrieval returns only the two narrowest lexical matches rather than the surrounding verses that explain how faith develops.\n- Candidate .39 applies the same two-unique-concept relevance rule to both cache hits and fresh official fetches. Deterministic scripture routes now include a small bounded window of adjacent paragraphs around the strongest matches so the verifier receives the surrounding scriptural explanation rather than isolated verses. The canonical 700-character evidence cap remains unchanged.\n- Verification remains fail-closed and official-only for faith questions. This change improves evidence quality and cache consistency rather than relaxing approval standards.\n"
if 'Ask cached relevance and deterministic scripture context - candidate 2026-09-03.39' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
