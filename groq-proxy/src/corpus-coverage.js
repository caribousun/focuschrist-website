// A citation coverage floor, not a substitute for semantic source verification.
const CORPORA = [
  [/\bnew testament\b/i, ['nt']], [/\bold testament\b/i, ['ot']],
  [/\bbook of mormon\b/i, ['bofm']], [/\bdoctrine (?:and|&) covenants\b|\bd\s*&\s*c\b/i, ['dc-testament']],
  [/\bpearl of great price\b/i, ['pgp']], [/\b(?:the )?bible\b/i, ['ot', 'nt']],
];
export function requestedTeachingCorpora(scope) {
  const current = String(scope?.question || '');
  let question = current;
  // Only an explicit supporting-scripture follow-up inherits its resolved user topic.
  if (scope?.scriptureSupportRequested && scope?.scriptureSupportAntecedent) question = scope.scriptureSupportAntecedent;
  // Bind corpus names to the source role, not merely their presence anywhere
  // near a teaching verb. A book can instead be the object of the question.
  let marked = String(question).replace(/@C\d+@/gi, '');
  CORPORA.forEach(([pattern], index) => {
    marked = marked.replace(new RegExp(pattern.source, 'gi'), `@C${index}@`);
  });
  const token = '@C\\d+@';
  const list = `(${token}(?:\\s*(?:,|and|&|versus|vs\\.?)\\s*(?:the\\s+)?${token})*)`;
  const sourcePatterns = [
    new RegExp(list + "(?:['’]s)?\\s+(?:teach(?:es|ings?)?|taught|say|says|reveal(?:s)?)\\b", 'gi'),
    new RegExp('\\baccording\\s+to\\s+(?:the\\s+)?' + list, 'gi'),
    new RegExp('\\bteachings?\\b[^.!?;]{0,100}?\\b(?:in|from)\\s+(?:the\\s+)?' + list, 'gi'),
  ];
  const selected = new Set();
  for (const pattern of sourcePatterns) for (const match of marked.matchAll(pattern)) {
    for (const id of match[1].matchAll(/@C(\d+)@/g)) if (CORPORA[Number(id[1])]) selected.add(Number(id[1]));
  }
  return [...selected].map(index => CORPORA[index][1]);
}
export function checkCorpusCoverage(scope, answer, evidence, library, approvedSource) {
  const required = requestedTeachingCorpora(scope);
  if (!required.length) return { ok: true, required: [] };
  let answerRefs;
  try { answerRefs = library.references(answer); }
  catch (_) { return { ok: false, reason: 'invalid-corpus-reference', required }; }
  const supported = [];
  for (const source of evidence || []) {
    if (!source?.content || !approvedSource(source.url)) continue;
    if (/\/study\/scriptures\//.test(source.url)) {
      try { supported.push(library.fromURL(source.url)); } catch (_) {}
    } else {
      // References in a search title/snippet do not count: only hydrated content.
      try { supported.push(...library.references(source.content || '')); } catch (_) {}
    }
  }
  const matches = answerRefs.filter(ref => supported.some(source => source.key === ref.key
    && (!ref.verses || !source.verses || ref.verses.every(verse => source.verses.includes(verse)))));
  const missing = required.filter(keys => !matches.some(ref => keys.includes(ref.key.split('/')[0])));
  return missing.length ? { ok: false, reason: 'missing-requested-corpus-evidence', required, missing }
    : { ok: true, required };
}
