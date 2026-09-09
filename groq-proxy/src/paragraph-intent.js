// These words retrieve existing paragraphs only. They are not evidence and
// must never be inserted into the visitor's question or an answer prompt.
export function paragraphRetrievalTerms(question) {
  const text = String(question || '').toLowerCase();
  const terms = new Set();
  const add = value => value.split(' ').forEach(term => terms.add(term));
  if (/\b(?:how long|duration|time (?:did|does|to|taken)|years? (?:did|to))\b/.test(text)
      && /\b(?:construct\w*|build\w*|built|erect\w*)\b/.test(text)) {
    // Keep start and end vocabulary together. Do not silently equate a
    // dedication date with the completion of every part of a building.
    add('begin began beginning start started groundbreaking ground broken dedication dedicated completion complete completed finish finished construction');
  }
  if (/\b(?:clothing|clothes|dress|dressed|garments?|attire|wear|wore|wearing)\b/.test(text)) {
    add('clothing clothes dress dressed coat coats shoes shoe garment garments attire wore wearing');
  }
  if (/\b(?:childhood|boyhood|girlhood|early life|growing up|grew up|as a (?:child|boy|girl))\b/.test(text)) {
    add('child childhood young boy girl born birth grew growing family parents mother father');
  }
  if (/\b(?:weather|storms?|snow|blizzards?|cold)\b/.test(text)) add('weather storm storms snow snowstorm blizzard cold winter');
  if (/\b(?:arriv\w*|reach\w*|enter\w*)\b/.test(text) && /\b(?:when|which|first|date|year|month)\b/.test(text)) add('arrived arrival reached entered');
  return [...terms];
}
