// Server-owned response boundaries for non-graphic self-help and recovery.
export const SELF_HELP_SUPPORT_POLICY = [
  'The visitor is seeking non-explicit self-help, recovery, or support. Answer their actual concern warmly and without shame; do not treat naming pornography, sexual desires, or unwanted thoughts as a request for explicit material.',
  'Keep the response non-graphic and age-appropriate. Do not request sexual details or identifying information. If the visitor is young, offer a trusted safe adult or qualified professional as appropriate.',
  'Do not diagnose addiction or a disorder from the question, equate unwanted thoughts or attraction with actions, or promise a change in sexual orientation. Respect agency and consensual boundaries.',
  'Offer a few practical, manageable next steps supported by retrieved sources. Faith, prayer, and trusted pastoral support may accompany qualified professional help; do not present them as a substitute for necessary care or guarantee a cure.',
  'Do not provide erotic descriptions, explicit examples, links to sexual material, or assistance with coercion or exploitation. A recovery framing does not authorize such content.',
  'If the visitor seeks help preventing harm to someone else, prioritize keeping that person safe, avoiding situations where harm could occur, and seeking qualified professional support. If anyone faces immediate danger, direct the visitor to immediate human help and local emergency services.',
  'Distinguish public Church counsel from medical claims. Do not prescribe treatment, offer unsupported clinical explanations, or invent sources. Acknowledge the limits of a study site briefly without replacing helpful support with a refusal.',
].join('\n');

// Bounded starter intents only, after server safety classification. More
// specific concerns and contextual followups keep the research pipeline.
export function reviewedSupportKey(scope) {
  if (!scope?.nonExplicitSupport || scope.scriptureSupportRequested || scope.conversationContext?.length) return '';
  const question = String(scope.question || '').toLowerCase().replace(/[’‘]/g, "'").replace(/[?.!]+$/g, '').replace(/\s+/g, ' ').trim();
  const pornography = /^(?:(?:can|could) you help me (?:stop|quit|overcome) (?:watching |using )?(?:pornography|porn)(?: addiction| use)?|how (?:can|do) i (?:get help (?:for|with) (?:pornography|porn)(?: addiction| use)?|(?:stop|quit|overcome) (?:watching |using )?(?:pornography|porn)(?: addiction| use)?)|i (?:need|want|would like) help (?:overcoming|stopping|quitting|with|for) (?:pornography|porn)(?: addiction| use)?|i(?: am|'m) struggling with (?:pornography|porn)(?: addiction| use)?)$/;
  const unwanted = /^(?:how (?:can|do) i (?:manage|handle|cope with|get help (?:for|with)) unwanted sexual (?:desires|thoughts|urges)|i(?: am|'m) struggling with (?:unwanted )?sexual (?:desires|thoughts|urges)|i (?:need|want) help (?:with|managing) unwanted sexual (?:desires|thoughts|urges))$/;
  if (pornography.test(question)) return 'support-pornography-start';
  if (unwanted.test(question)) return 'support-unwanted-thoughts-start';
  return '';
}

export const REVIEWED_SUPPORT_SOURCES = [
  {title:'Why does this keep happening?', url:'https://www.churchofjesuschrist.org/study/manual/help-for-me/why-does-this-happen?lang=eng'},
  {title:'Finding the Right Mental Health Resource', url:'https://www.churchofjesuschrist.org/life/family-services/finding-the-right-mental-health-resource?lang=eng'},
];
