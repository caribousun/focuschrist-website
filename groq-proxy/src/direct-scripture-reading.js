// Narrow word-request routing only; all actual text and validity come from the
// shared canonical library. Interpretation requests remain with the verifier.
export async function directScriptureReading(question, library) {
  try {
    const text = String(question || '').trim();
    const refs = library.references(text);
    if (refs.length !== 1 || !refs[0].verses?.length) return null;
    const ref = refs[0];
    const before = text.slice(0, ref.index).trim();
    const after = text.slice(ref.end).trim();
    if (/^what\s+does$/i.test(before) && /^(?:state|say)(?:\s+(?:exactly|verbatim|for me))?[?.!]*$/i.test(after)) {
      return library.lookupRequest(ref.text);
    }
    // Existing reading grammar already bounds read/show/quote and courtesy.
    return library.lookupRequest(text);
  } catch (_) { return null; }
}
