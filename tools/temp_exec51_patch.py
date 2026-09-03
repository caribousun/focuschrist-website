from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'missing expected text in {path}: {old[:100]!r}')
    text = text.replace(old, new, 1)
    p.write_text(text, encoding='utf-8')

p = Path('groq-proxy/src/index.js')
text = p.read_text(encoding='utf-8')
text = text.replace("const SOURCE_POLICY_VERSION = '2026-09-03.50';", "const SOURCE_POLICY_VERSION = '2026-09-03.51';")
text = text.replace("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.50';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.51';")
old_block = """  if (candidate && (candidate.deterministic === true || candidate.deterministicHistoryTopic === true) && selected.length) {
    const positions = new Set();
    // A deterministic history topic is an article-level match, not merely a
    // paragraph-level keyword match. Preserve its lead paragraphs so origin,
    // date, identity, and purpose are not displaced by a later heading that
    // happens to share more query tokens (for example \"organization\").
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
new_block = """  if (candidate && candidate.deterministic === true && selected.length) {
    // A named scripture chapter is already pinned to one canonical source.
    // Keep both highest-relevance anchor paragraphs before surrounding context.
    // This prevents a long early paragraph from truncating a later paragraph
    // that supplies a second concept in the visitor's question (for example
    // Enos 1 prayer plus forgiveness) on a cold, uncached fetch.
    const anchorPositions = Array.from(new Set(selected.map((item) => item.position)))
      .sort((left, right) => left - right);
    const contextPositions = new Set();
    selected.forEach((item) => {
      for (let offset = -1; offset <= 3; offset += 1) {
        const position = item.position + offset;
        if (position >= 0 && position < sourceParagraphs.length && !anchorPositions.includes(position)) {
          contextPositions.add(position);
        }
      }
    });
    return [
      ...anchorPositions,
      ...Array.from(contextPositions).sort((left, right) => left - right),
    ].map((position) => sourceParagraphs[position]).join(' ').slice(0, 4200);
  }
  if (candidate && candidate.deterministicHistoryTopic === true && selected.length) {
    const positions = new Set();
    // A deterministic history topic is an article-level match, not merely a
    // paragraph-level keyword match. Preserve its lead paragraphs so origin,
    // date, identity, and purpose are not displaced by a later heading that
    // happens to share more query tokens (for example \"organization\").
    for (let position = 0; position < Math.min(2, sourceParagraphs.length); position += 1) positions.add(position);
    selected.forEach((item) => {
      for (let offset = -1; offset <= 2; offset += 1) {
        const position = item.position + offset;
        if (position >= 0 && position < sourceParagraphs.length) positions.add(position);
      }
    });
    return Array.from(positions).sort((left, right) => left - right)
      .map((position) => sourceParagraphs[position]).join(' ').slice(0, 1200);
  }
"""
if old_block not in text:
    raise SystemExit('relevantParagraphText deterministic block not found')
text = text.replace(old_block, new_block, 1)
text = text.replace(
    "const questionFocused = topicPinned || Boolean(candidate && candidate.deterministicHistoryTopic === true);",
    "const questionFocused = topicPinned || Boolean(candidate && (candidate.deterministic === true || candidate.deterministicHistoryTopic === true));",
    1,
)
p.write_text(text, encoding='utf-8')

# Add a cold deterministic scripture regression that specifically fails under
# the old 700-character source-order truncation.
p = Path('groq-proxy/source-policy.test.js')
text = p.read_text(encoding='utf-8').replace('2026-09-03.50', '2026-09-03.51')
marker = "const reliefReviewedRecovery = reviewedDeterministicEvidenceRecovery(\n"
if marker not in text:
    raise SystemExit('source-policy Enos insertion marker not found')
insert = r"""
const coldEnosQuestion = 'What does Enos 1 teach about prayer and forgiveness?';
const coldEnosCandidate = {
  deterministic: true,
  title: 'Enos 1',
  tokens: 'Enos 1',
  url: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/enos/1?lang=eng',
};
const coldEnosParagraphs = [
  `Enos describes earnest prayer for his own soul before God. ${'This paragraph supplies surrounding narrative context without adding the later forgiveness statement. '.repeat(12)}`,
  'The narrative continues with additional setting and sequence before the answer to his pleading is stated.',
  'Another paragraph supplies intervening narrative context about the experience and its progression.',
  'The account continues before recording the Lord’s answer to Enos and the change that followed.',
  'The Lord tells Enos that his sins are forgiven, and Enos explains that his guilt is swept away because of faith in Christ.',
];
const coldEnosExcerpt = relevantParagraphText(coldEnosParagraphs, coldEnosQuestion, coldEnosCandidate);
assert(/\bpray\w*\b/i.test(coldEnosExcerpt) && /\bforgiv\w*\b/i.test(coldEnosExcerpt),
  'cold deterministic scripture extraction must preserve both high-relevance concepts before surrounding context');
const coldEnosRecovery = reviewedDeterministicEvidenceRecovery(coldEnosQuestion, [{
  url: coldEnosCandidate.url,
  content: coldEnosExcerpt,
}]);
assert(coldEnosRecovery && coldEnosRecovery.recoveryId === 'reviewed-enos-1-prayer-forgiveness',
  'cold Enos 1 official extraction must activate the same audited recovery as a warm-cache request');
const coldEnosCachePack = compactParagraphPack(coldEnosParagraphs, coldEnosCandidate, coldEnosQuestion);
assert(coldEnosCachePack.some((paragraph) => /\bpray\w*\b/i.test(paragraph))
  && coldEnosCachePack.some((paragraph) => /\bforgiv\w*\b/i.test(paragraph)),
  'deterministic scripture cache packing must prioritize the visitor question so warm retrieval preserves both concepts');

"""
text = text.replace(marker, insert + marker, 1)
p.write_text(text, encoding='utf-8')

for path in ['tools/live_ai_response_matrix.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    text = p.read_text(encoding='utf-8').replace('2026-09-03.50', '2026-09-03.51')
    p.write_text(text, encoding='utf-8')

# Print the two warm Enos payloads before validation so any future production
# failure has a direct cold/warm receipt instead of a generic assertion only.
p = Path('tools/live_ai_response_matrix.js')
text = p.read_text(encoding='utf-8')
old = """    const warmFirst = await submit(warmTest); const warmSecond = await submit(warmTest);
    validate(warmTest, warmFirst); validate(warmTest, warmSecond);
"""
new = """    const warmFirst = await submit(warmTest); const warmSecond = await submit(warmTest);
    console.log(JSON.stringify({ ...warmFirst, phase: 'cold-enos' }));
    console.log(JSON.stringify({ ...warmSecond, phase: 'warm-enos' }));
    validate(warmTest, warmFirst); validate(warmTest, warmSecond);
"""
if old not in text:
    raise SystemExit('warm Enos matrix block not found')
text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

p = Path('MEMORY.md')
text = p.read_text(encoding='utf-8')
entry = "\n- 2026-09-03 candidate .51: production replay isolated the last full-matrix failure to the first cold Enos 1 fetch. Deterministic scripture extraction now preserves both top relevance anchors before context, expands its bounded excerpt to 4,200 characters, and question-focuses deterministic scripture cache packing. The exact cold/warm Enos pair is permanently logged and unit-tested. Production remains unverified until the deployed .51 full matrix passes.\n"
if entry.strip() not in text:
    text += entry
p.write_text(text, encoding='utf-8')
