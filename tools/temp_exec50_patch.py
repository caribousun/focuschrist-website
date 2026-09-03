from pathlib import Path


def replace(path, old, new, count=1):
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f'missing expected text in {path}: {old[:120]!r}')
    p.write_text(text.replace(old, new, count))

for path in [
    'groq-proxy/src/index.js',
    'groq-proxy/source-policy.test.js',
    'tools/live_ai_response_matrix.js',
    'tools/pioneer_local_first_qa.py',
    'tools/scripture_grounding_qa.py',
]:
    p = Path(path)
    p.write_text(p.read_text().replace('2026-09-03.49', '2026-09-03.50'))

index = Path('groq-proxy/src/index.js')
text = index.read_text()
old = """  if (candidate && candidate.deterministic === true && selected.length) {
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
"""
new = """  if (candidate && (candidate.deterministic === true || candidate.deterministicHistoryTopic === true) && selected.length) {
    const positions = new Set();
    // A deterministic history topic is an article-level match, not merely a
    // paragraph-level keyword match. Preserve its lead paragraphs so origin,
    // date, identity, and purpose are not displaced by a later heading that
    // happens to share more query tokens (for example "organization").
    if (candidate.deterministicHistoryTopic === true) {
      for (let position = 0; position < Math.min(2, sourceParagraphs.length); position += 1) positions.add(position);
    }
    selected.forEach((item) => {
      const firstOffset = candidate.deterministicHistoryTopic === true ? -1 : 0;
      const lastOffset = candidate.deterministicHistoryTopic === true ? 2 : 3;
      for (let offset = firstOffset; offset <= lastOffset; offset += 1) {
        const position = item.position + offset;
        if (position >= 0 && position < sourceParagraphs.length) positions.add(position);
      }
    });
    const limit = candidate.deterministicHistoryTopic === true ? 1200 : 700;
    return Array.from(positions).sort((left, right) => left - right)
      .map((position) => sourceParagraphs[position]).join(' ').slice(0, limit);
  }
"""
if old not in text:
    raise SystemExit('relevantParagraphText deterministic block not found')
text = text.replace(old, new, 1)
old = """    const topicScore = (pinnedIrrigation ? 600 : 0) + (pinnedSettlement ? 100 : 0);
    return { text, position, score: topicScore + queryOverlap * 40 + discoveryOverlap * 20 - position / 1000 };
"""
new = """    const topicScore = (pinnedIrrigation ? 600 : 0) + (pinnedSettlement ? 100 : 0);
    const historyLeadScore = candidate && candidate.deterministicHistoryTopic === true && position < 2 ? 1200 : 0;
    return { text, position, score: historyLeadScore + topicScore + queryOverlap * 40 + discoveryOverlap * 20 - position / 1000 };
"""
if old not in text:
    raise SystemExit('compactParagraphPack score block not found')
text = text.replace(old, new, 1)
index.write_text(text)

# Add executable regression coverage for the exact production failure shape.
test = Path('groq-proxy/source-policy.test.js')
t = test.read_text()
old_import = """  collectSourceEvidence,
  extractSelectedPioneerName,
"""
new_import = """  collectSourceEvidence,
  compactParagraphPack,
  extractSelectedPioneerName,
"""
if old_import not in t:
    raise SystemExit('source-policy compact import anchor not found')
t = t.replace(old_import, new_import, 1)
old_import2 = """  providerDiagnostic,
  remainingBudget,
  reviewedDeterministicEvidenceRecovery,
"""
new_import2 = """  providerDiagnostic,
  relevantParagraphText,
  remainingBudget,
  reviewedDeterministicEvidenceRecovery,
"""
if old_import2 not in t:
    raise SystemExit('source-policy relevant import anchor not found')
t = t.replace(old_import2, new_import2, 1)
anchor = """assert(reviewedDeterministicEvidenceRecovery(
  'Tell me about the Kirtland Temple.',
  [{ url: 'https://www.churchofjesuschrist.org/study/history/topics/kirtland-temple?lang=eng', content: 'Kirtland Temple history.' }],
) === null, 'reviewed Relief Society recovery must not activate for unrelated Church History topics');

"""
addition = anchor + """const reliefHistoryQuestion = 'What should I know about the organization of the Relief Society when it began and why.';
const reliefHistoryCandidate = {
  url: 'https://www.churchofjesuschrist.org/study/history/topics/relief-society?lang=eng',
  title: 'Relief Society',
  tokens: 'relief society organization history women service',
  deterministicHistoryTopic: true,
};
const reliefHistoryParagraphs = [
  'The Female Relief Society of Nauvoo was organized in March 1842. Joseph Smith gave women a commission to relieve the poor and save souls, and women continued to pray, testify, and bless the sick and poor.',
  'In 1854 women began to organize again in local Relief Societies and assisted neighbors and poor Saints.',
  'By 1867 local societies were reestablished in Utah under Church direction.',
  'A Central Organization developed later as Relief Societies multiplied and greater coordination became necessary.',
];
const reliefHistoryExcerpt = relevantParagraphText(reliefHistoryParagraphs, reliefHistoryQuestion, reliefHistoryCandidate);
assert(/March 1842/i.test(reliefHistoryExcerpt)
  && /relieve the poor/i.test(reliefHistoryExcerpt)
  && /Central Organization/i.test(reliefHistoryExcerpt),
  'deterministic Church History evidence must preserve the article lead while including query-relevant later context');
const reliefHistoryPack = compactParagraphPack(reliefHistoryParagraphs, reliefHistoryCandidate, reliefHistoryQuestion);
assert(reliefHistoryPack.some((paragraph) => /March 1842/i.test(paragraph)),
  'cached deterministic Church History evidence must retain the article lead paragraph');
const reliefHistoryWarmExcerpt = relevantParagraphText(reliefHistoryPack, reliefHistoryQuestion, reliefHistoryCandidate);
assert(/March 1842/i.test(reliefHistoryWarmExcerpt) && /relieve the poor/i.test(reliefHistoryWarmExcerpt),
  'warm-cache deterministic Church History evidence must retain origin and purpose context');
const reliefGeneralRecovery = reviewedDeterministicEvidenceRecovery(reliefHistoryQuestion, [{
  url: reliefHistoryCandidate.url,
  content: reliefHistoryWarmExcerpt,
}]);
assert(reliefGeneralRecovery && reliefGeneralRecovery.recoveryId === 'reviewed-relief-society-nauvoo',
  'the exact broader Relief Society organization wording must reach the audited recovery from the general official topic');

"""
if anchor not in t:
    raise SystemExit('source-policy Relief Society regression anchor not found')
t = t.replace(anchor, addition, 1)
test.write_text(t)

memory = Path('MEMORY.md')
mem = memory.read_text()
note = """
- 2026-09-03 policy `.50` candidate: `.49` production proved the provider-independent reviewed lane works, but one broader Relief Society wording still failed because deterministic history retrieval ranked a later paragraph with the word “organization” and omitted the article lead containing the March 1842 origin and original purpose. `.50` treats a deterministic Church History topic as an article-level match: live extraction preserves the first two lead paragraphs plus nearby query-relevant context, cached paragraph packs pin those lead paragraphs, and the cache version is advanced so stale `.49` excerpts cannot survive. The exact broader Relief Society organization question is now a permanent cold- and warm-excerpt regression test. This strengthens evidence selection rather than relaxing verification.
"""
if note.strip() not in mem:
    memory.write_text(mem.rstrip() + '\n' + note)
