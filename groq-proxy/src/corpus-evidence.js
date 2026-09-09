import { requestedTeachingCorpora } from './corpus-coverage.js';

// Expand citations actually present in admitted article bodies, never titles,
// snippets, answer drafts or guessed topical verses. Semantic relevance remains
// the verifier's responsibility after the complete passages are supplied.
export async function augmentRequestedCorpusEvidence(scope, evidence, library, approvedSource, hasBudget = () => true) {
  const required = requestedTeachingCorpora(scope).flat();
  if (!required.length || !hasBudget()) return [];
  const refs = new Map();
  const existing = new Set();
  for (const source of evidence || []) {
    if (!source?.content || !approvedSource(source.url)) continue;
    if (/\/study\/scriptures\//.test(source.url)) {
      try { existing.add(library.fromURL(source.url).key); } catch (_) {}
      continue;
    }
    try {
      for (const ref of library.references(source.content)) {
        if (required.includes(ref.key.split('/')[0]) && ref.verses && !refs.has(ref.text)) refs.set(ref.text, ref);
      }
    } catch (_) { /* Invalid article citations cannot become evidence. */ }
  }
  const added = [];
  let characters = 0;
  let attempts = 0;
  for (const ref of refs.values()) {
    if (attempts >= 2 || !hasBudget()) break;
    if (existing.has(ref.key)) continue;
    attempts++;
    try {
      const passages = await library.evidenceRequest(ref.text);
      const size = passages.reduce((sum, source) => sum + source.content.length, 0);
      if (characters + size > 6000) continue;
      added.push(...passages);
      characters += size;
      existing.add(ref.key);
    } catch (_) { /* Unavailable canonical data never becomes guessed text. */ }
  }
  return added;
}
