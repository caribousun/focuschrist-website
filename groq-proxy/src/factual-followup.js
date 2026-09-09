// This changes length expectations only. It supplies no facts, approvals or
// source exceptions, and never reads an earlier question as the current ask.
export function isNarrowFactualFollowup(scope) {
  if (scope?.classificationMode !== 'conversation-context') return false;
  const question = String(scope.question || '').trim().toLowerCase();
  if (!question || question.length > 180 || question.split(/\s+/).length > 26) return false;
  // Mixed requests and explanations retain the ordinary study-depth contract.
  if (/[;\n]/.test(question) || (question.match(/\?/g) || []).length > 1
      || /\b(?:why|explain|compare|contrast|teach\w*|meaning|significan\w*|interpret\w*|apply|application|lesson\w*|relationship|influenc\w*|impact|symbol\w*|summari\w*|describe|discuss|and|also)\b/.test(question)) return false;
  return /^(?:when|where|who|what year|how many|how long)\b/.test(question)
    && /^(?:(?:when|where)\s+(?:was|were|is|are|did|does|do|will|had|has)\b|who\s+(?:was|were|is|are|did|does|wrote|led|printed|published|accompanied)\b|what year\s+(?:was|were|did|is)\b|how many\s+[a-z]|how long\s+(?:was|were|did|does|is|has|had)\b)/.test(question);
}
