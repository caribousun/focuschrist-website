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
      .map((position) => sourceParagraphs[position]).join(' ').slice(0, 1200);
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

old_slice = "content: String(content || '').replace(/\\s+/g, ' ').trim().slice(0, 700),"
new_slice = "content: String(content || '').replace(/\\s+/g, ' ').trim().slice(0, 1200),"
if old_slice not in w:
    raise SystemExit('Canonical source content slice anchor missing')
w = w.replace(old_slice, new_slice, 1)
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

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Ask cached relevance and deterministic scripture context - candidate 2026-09-03.39\n\n- Production .38 confirmed the new unique-relevance rule on fresh official fetches, but live testing exposed that cached excerpts still bypassed that rule. The same run also showed a clear Alma 32 question can be over-rejected when retrieval returns only the two narrowest lexical matches rather than the surrounding verses that explain how faith develops.\n- Candidate .39 applies the same two-unique-concept relevance rule to both cache hits and fresh official fetches. Deterministic scripture routes now include a small bounded window of adjacent paragraphs around the strongest matches so the verifier receives the surrounding scriptural explanation rather than isolated verses. Canonical evidence excerpts may carry up to 1,200 characters, still within the existing bounded verifier evidence budget.\n- Verification remains fail-closed and official-only for faith questions. This change improves evidence quality and cache consistency rather than relaxing approval standards.\n"
if 'Ask cached relevance and deterministic scripture context - candidate 2026-09-03.39' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
