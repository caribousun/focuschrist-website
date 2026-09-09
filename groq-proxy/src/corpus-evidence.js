import { requestedTeachingCorpora } from './corpus-coverage.js';

// Expand citations actually present in admitted article bodies, never titles,
// snippets, answer drafts or guessed topical verses. Semantic relevance remains
// the verifier's responsibility after the complete passages are supplied.
export async function augmentRequestedCorpusEvidence(scope, evidence, library, approvedSource, hasBudget = () => true) {
  const required = requestedTeachingCorpora(scope).flat();
  if (!required.length || !hasBudget()) return [];
  const refs = new Map();
  const existing = new Set();
  const stop = new Set('a an the what does do did is are was were how why can could would should about teach teaches teaching teachings say says according to in from of and or for with that this scripture scriptures bible old new testament book mormon doctrine covenants pearl great price'.split(' '));
  const query = new Set((String(scope.question || '').toLowerCase().match(/[a-z]+/g) || []).filter(token => token.length > 2 && !stop.has(token)));
  for (const source of evidence || []) {
    if (!source?.content || !approvedSource(source.url)) continue;
    if (/\/study\/scriptures\//.test(source.url)) {
      try { existing.add(library.fromURL(source.url).key); } catch (_) {}
      continue;
    }
    try {
      for (const ref of library.references(source.content)) {
        if (!required.includes(ref.key.split('/')[0]) || !ref.verses) continue;
        // Rank the actual article context near each citation, not the whole
        // article title. A later relevant passage may precede the first two
        // incidental references without inventing a topical verse association.
        const start = Math.max(source.content.lastIndexOf('\n', ref.index) + 1, ref.index - 180);
        const nextBreak = source.content.indexOf('\n', ref.end);
        const end = Math.min(nextBreak < 0 ? source.content.length : nextBreak, ref.end + 180);
        const words = new Set((source.content.slice(start,end).toLowerCase().match(/[a-z]+/g) || []));
        const score = [...query].filter(token => words.has(token)).length;
        const previous = refs.get(ref.text);
        if (!previous || score > previous.score) refs.set(ref.text, {ref,score});
      }
    } catch (_) { /* Invalid article citations cannot become evidence. */ }
  }
  const added = [];
  let characters = 0;
  let attempts = 0;
  for (const {ref} of [...refs.values()].sort((a,b)=>b.score-a.score)) {
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
