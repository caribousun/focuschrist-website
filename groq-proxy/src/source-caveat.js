// Preserve an author's qualification when a relevant cited note could otherwise
// be read as the author's own unqualified factual assertion.
export function qualifyingBodyPositions(paragraphs, queryTokens, normalizeTokens, selectedPositions = null) {
  const query = new Set(queryTokens);
  const overlaps = text => normalizeTokens(text).some(token=>query.has(token));
  const selected = selectedPositions ? new Set(selectedPositions) : null;
  const noteIds = new Set();
  paragraphs.forEach((text,position)=>{
    const match = /^\s*\[(\d+)\]\s*[.]?\s+/.exec(text);
    if (match && (selected ? selected.has(position) : overlaps(text))) noteIds.add(match[1]);
  });
  const positions = new Set();
  paragraphs.forEach((text,position)=>{
    if (/^\s*\[\d+\]/.test(text) || !overlaps(text)) return;
    const qualifies = /\b(?:unsubstantiated|unverified|disputed|uncertain|unreliable|contradict\w*|no evidence|not supported|cannot (?:confirm|establish|verify)|does not (?:support|confirm|establish)|do not (?:support|confirm|establish))\b/i.test(text);
    if (qualifies && [...text.matchAll(/\[(\d+)\]/g)].some(match=>noteIds.has(match[1]))) positions.add(position);
  });
  return positions;
}
