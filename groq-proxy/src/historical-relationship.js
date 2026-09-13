// The official Winter Quarters topic identifies St. Louis as the place of
// purchase, not the destination storehouse. Detect this observed relation swap
// before publication and ask the normal evidence verifier to repair it.
export function hasWinterQuartersLocationSwap(answer) {
  const text = String(answer || '');
  const swaps = [
    /\bWinter\s+Quarters(?:['’]s)?\s+storehouse\s+(?:(?:was|is)\s+)?(?:located\s+)?(?:in|at)\s+St[.\s]+Louis\b/gi,
    /\bstorehouse\s+(?:in|at)\s+St[.\s]+Louis\s*(?:,\s*)?(?:at|in|for|of)\s+Winter\s+Quarters\b/gi,
    /\bSt[.\s]+Louis\s+storehouse\s+(?:at|in|for|of)\s+Winter\s+Quarters\b/gi,
    /\bWinter\s+Quarters\b[^.!?\n]{0,100}\bits\s+storehouse\s+(?:(?:was|is)\s+)?(?:located\s+)?(?:in|at)\s+St[.\s]+Louis\b/gi,
  ];
  for (const pattern of swaps) for (const match of text.matchAll(pattern)) {
    const before = text.slice(0, match.index);
    const after = text.slice(match.index + match[0].length);
    // Only a correction attached to this exact relation can excuse it; a
    // separate negative statement elsewhere must not disable the check.
    if (/\b(?:no|never\s+(?:a|the)|not\s+(?:a|the))\s*$/i.test(before)) continue;
    if (/^[”"']?\s+(?:is|was)\s+(?:an?\s+)?(?:incorrect|false|mistaken|inaccurate)\s+(?:description|claim|statement|location)\b/i.test(after)) continue;
    return true;
  }
  return false;
}
