// Bounded predicate-scope check. A list of things offered for sale is not
// evidence that the sale of every thing failed. Only explicit outcome clauses
// contribute support here; the normal verifier still checks all other claims.
const canonicalWords = value => (String(value).toLowerCase().match(/[a-z]+/g) || [])
  .filter(word => !['the','a','an','other','their','its','both','neither'].includes(word))
  .map(word => word.replace(/ies$/, 'y').replace(/s$/, ''));

function outcomeObjects(text) {
  const outcomes = [];
  for (const clause of String(text || '').split(/[.;!?\n]+|\b(?:but|whereas|while)\b/i)) {
    const patterns = [
      {kind:'sale', re:/\b(?:unsuccessfully\s+(?:to\s+)?|failed\s+to\s+|unable\s+to\s+|could\s+not\s+|did\s+not\s+)(?:sell)\s+(.+)/gi},
      {kind:'purchase', re:/\b(?:unsuccessfully\s+(?:to\s+)?|failed\s+to\s+|unable\s+to\s+|could\s+not\s+|did\s+not\s+)(?:buy|purchase)\s+(.+)/gi},
      {kind:'sale', re:/\b(?:unable\s+to|could\s+not|did\s+not|failed\s+to)\s+find\s+(?:a\s+)?buyers?\s+for\s+(.+)/gi},
      {kind:'sale', re:/\bno\s+buyers?\s+(?:was\s+|were\s+)?found\s+for\s+(.+)/gi},
      {kind:'sale', re:/\b(.+?)\s+(?:remained\s+unsold|(?:was|were)\s+not\s+sold)\b/gi},
      {kind:'sale', re:/\b(?:efforts?|attempts?)\s+to\s+sell\s+(.+?)\s+(?:was|were|proved)\s+unsuccessful\b/gi},
      {kind:'purchase', re:/\b(?:efforts?|attempts?)\s+to\s+(?:buy|purchase)\s+(.+?)\s+(?:was|were|proved)\s+unsuccessful\b/gi},
    ];
    for (const {kind,re} of patterns) for (const match of clause.matchAll(re)) {
      const before = clause.slice(0, match.index);
      if (/\bnot\s*$/i.test(before)
        || /\b(?:false|incorrect|untrue|inaccurate)\s+that\s+(?:[a-z]+\s+){0,4}$/i.test(before)) continue;
      const objectList = match[1].split(/,|\b(?:for|to\s+help|in\s+order|because|despite)\b/i)[0].trim();
      if (objectList.length > 180) continue;
      const objects = objectList.split(/\b(?:and|nor|as\s+well\s+as)\b/i)
        .map(label => ({label:label.trim(), words:canonicalWords(label)})).filter(object=>object.words.length);
      if (objects.length) outcomes.push({kind, objects});
    }
  }
  return outcomes;
}

export function unsupportedJoinedTransactionOutcomes(answer, evidence) {
  const support = (Array.isArray(evidence) ? evidence : [])
    .flatMap(source => outcomeObjects(source.content || ''));
  const failures = [];
  for (const claim of outcomeObjects(answer)) {
    if (claim.objects.length < 2) continue;
    const unsupported = claim.objects.filter(object => !support.some(outcome => outcome.kind === claim.kind
      && outcome.objects.some(known => known.words.at(-1) === object.words.at(-1)
        && known.words.every(word => object.words.includes(word)))));
    if (unsupported.length) failures.push({transaction:claim.kind, unsupportedObjects:unsupported.map(object=>object.label)});
  }
  return failures;
}
