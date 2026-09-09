// Recognize only questions whose grammatical subject is an unresolved pronoun.
// User turns establish an antecedent; assistant assertions never establish one.
function bareSubjectQuestion(value) {
  const text = String(value || '').split(/\n\nThe immediately preceding user question was:/)[0]
    .trim().replace(/[?.!]+$/g, '').toLowerCase();
  if (/^what does it mean (?:to|that|when|if)\b/.test(text)
      || /^why is it (?:important|necessary|helpful|good|possible) (?:to|that)\b/.test(text)
      || /\b[a-z]+\s+\d+:\d+/.test(text)) return false;
  return /^(?:when|where|why|how)\s+(?:did|does|do|was|were|is|are|will|would|could|can|has|have)\s+(?:he|she|they|it)\b/.test(text)
    || /^what\s+(?:did|does|do|was|were|is|are|will|would|could|can)\s+(?:he|she|they|it)\b/.test(text)
    || /^which\s+(?:pioneer\s+|handcart\s+|wagon\s+)?company\s+(?:was|were|is|are)\s+(?:he|she|they)\s+(?:in|with)$/.test(text)
    || /^what\s+(?:he|she|they)\s+meant$/.test(text);
}

export function needsMissingSubjectClarification(scope = {}) {
  if (scope.selectedPioneer || String(scope.selectedPioneerName || '').trim()) return false;
  if (!bareSubjectQuestion(scope.question)) return false;
  const prior = Array.isArray(scope.conversationContext) ? scope.conversationContext : [];
  // A reset starts a fresh topic even if older messages were accidentally retained.
  let hasAntecedent = false;
  for (const item of prior) {
    let question = String(item || '').trim();
    const reset = question.match(/^(?:new (?:topic|question)|unrelated (?:topic|question)|switch(?:ing)? (?:topics|subjects))\b[\s:.-]*/i);
    if (reset) {
      hasAntecedent = false;
      question = question.slice(reset[0].length).trim();
    }
    if (question && !bareSubjectQuestion(question)
        && !/^(?:why|how so|tell me more|go on|continue|what else|which of (?:the|those|these) two.*)[?.!]*$/i.test(question)) {
      hasAntecedent = true;
    }
  }
  return !hasAntecedent;
}
