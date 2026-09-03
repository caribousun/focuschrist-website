from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')

for old, new in [
    ("const SOURCE_POLICY_VERSION = '2026-09-03.42';", "const SOURCE_POLICY_VERSION = '2026-09-03.43';"),
    ("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.42';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.43';"),
]:
    if old not in w:
        raise SystemExit('Missing version anchor: ' + old)
    w = w.replace(old, new, 1)

old_history = """function deterministicHistoryTopicSource(question, page) {
  if (page !== 'church-history') return null;
  const queryTokens = normalizeDiscoveryTokens(question);
"""
new_history = """function deterministicHistoryTopicSource(question, page) {
  if (!['ask', 'church-history'].includes(page)) return null;
  const queryTokens = normalizeDiscoveryTokens(question);
"""
if old_history not in w:
    raise SystemExit('Missing history page-scope anchor')
w = w.replace(old_history, new_history, 1)

old_history_prompt = """          : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
            ? 'The visitor explicitly named an indexed Church History topic. EVIDENCE contains that exact official Church History topic and no competing research source. If its excerpt directly describes the requested event, date, purpose, or historical setting, compose the supported answer from it and approve it.'
"""
new_history_prompt = """          : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
            ? 'The visitor explicitly named, or the bounded conversation context resolved to, an indexed Church History topic. EVIDENCE contains that exact official Church History topic and no competing research source. If its excerpt directly describes the requested identity, role, event, date, purpose, or historical setting, compose the supported answer from it and approve it. For a faith or Church-history answer, aim for 100 to 170 words and at least four complete sentences so the response clears the publication-depth floor with margin.'
"""
if old_history_prompt not in w:
    raise SystemExit('Missing deterministic history verifier prompt anchor')
w = w.replace(old_history_prompt, new_history_prompt, 1)

old_requirements = """        const requirements = answerSubstanceRequirements(sanitized.scope);
        const expansionPrompt = [
"""
new_requirements = """        const requirements = answerSubstanceRequirements(sanitized.scope);
        const repairMinimumWords = requirements.minimumWords
          + (sanitized.scope.selectedPioneer ? 30 : (sanitized.scope.faith ? 25 : 10));
        const repairMinimumSentences = requirements.minimumSentences + (sanitized.scope.faith ? 1 : 0);
        const expansionPrompt = [
"""
if old_requirements not in w:
    raise SystemExit('Missing depth repair requirements anchor')
w = w.replace(old_requirements, new_requirements, 1)

old_depth = """            : needsDepthRepair
            ? `Rewrite it using at least ${requirements.minimumWords} words, ${requirements.minimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s).`
"""
new_depth = """            : needsDepthRepair
            ? `Rewrite it using at least ${repairMinimumWords} words, ${repairMinimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s). The publication gate is lower, but this repair target deliberately includes safety margin. Do not stop at the minimum.`
"""
if old_depth not in w:
    raise SystemExit('Missing depth repair instruction anchor')
w = w.replace(old_depth, new_depth, 1)

old_history_reconsider = """              : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
                ? 'This is the exact official Church History topic named by the visitor. Re-read its excerpt for the requested historical event or setting. If the excerpt supports a responsible answer, write it and set approved true with source_indexes [1]. Keep approved false only if that exact topic excerpt truly lacks the requested material.'
"""
new_history_reconsider = """              : retrievalDiagnostic.focuschrist_deterministic_history_topic === true
                ? 'This is the exact official Church History topic named by the visitor or resolved from bounded conversation context. Re-read its excerpt for the requested identity, leadership role, event, or setting. If the excerpt supports a responsible answer, write a complete answer of roughly 100 to 170 words with at least four sentences and set approved true with source_indexes [1]. Keep approved false only if that exact topic excerpt truly lacks the requested material.'
"""
if old_history_reconsider not in w:
    raise SystemExit('Missing history reconsideration anchor')
w = w.replace(old_history_reconsider, new_history_reconsider, 1)
worker.write_text(w, encoding='utf-8')

# Advance policy assertions.
for path in ['groq-proxy/source-policy.test.js', 'groq-proxy/church-source-index.test.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.42', '2026-09-03.43'), encoding='utf-8')

index_test = Path('groq-proxy/church-source-index.test.js')
it = index_test.read_text(encoding='utf-8')
old_kirtland_ask = """assert(deterministicHistoryTopicSource(kirtlandQuestion, 'ask') === null,
  'named Church History topic determinism must remain scoped to the Church History page');
"""
new_kirtland_ask = """assert(deterministicHistoryTopicSource(kirtlandQuestion, 'ask')
  && /\/study\/history\/topics\/kirtland-temple/.test(deterministicHistoryTopicSource(kirtlandQuestion, 'ask').url),
  'an exact multi-token official history topic must remain deterministic on the main Ask page as well');
"""
if old_kirtland_ask not in it:
    raise SystemExit('Missing prior Ask history scope assertion')
it = it.replace(old_kirtland_ask, new_kirtland_ask, 1)

follow_anchor = """assert(followUpScope.faith && followUpScope.classificationMode === 'conversation-context'
  && followUpScope.retrievalQuestion.startsWith('hyrum smith:'),
  'bounded conversation context must resolve a Church-person pronoun before retrieval');
"""
follow_new = follow_anchor + """const hyrumAskTopic = deterministicHistoryTopicSource(
  'Who was Hyrum Smith and what service did he give in the early Church?',
  'ask',
);
const hyrumFollowTopic = deterministicHistoryTopicSource(followUpScope.retrievalQuestion, 'ask');
assert(hyrumAskTopic && hyrumFollowTopic
  && /\/study\/history\/topics\/hyrum-smith/.test(hyrumAskTopic.url)
  && hyrumAskTopic.url === hyrumFollowTopic.url,
  'Hyrum Smith seed and bounded pronoun follow-up must resolve to the same single official history topic');
"""
if follow_anchor not in it:
    raise SystemExit('Missing Hyrum follow-up context anchor')
it = it.replace(follow_anchor, follow_new, 1)
index_test.write_text(it, encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.42';" not in mt:
    raise SystemExit('Missing matrix policy anchor')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.42';", "const POLICY_VERSION = '2026-09-03.43';", 1)

initial_anchor = """    const initial = await submit(hyrumSeedTest); validate(hyrumSeedTest, initial);
    await validateActualOfficialEvidence(hyrumSeedTest, initial);
"""
initial_new = """    const initial = await submit(hyrumSeedTest); validate(hyrumSeedTest, initial);
    assert(initial.deterministicHistoryTopic === true && initial.indexSources === 1 && initial.officialFetchCalls <= 1,
        'Hyrum seed did not prove single-source deterministic official history retrieval');
    await validateActualOfficialEvidence(hyrumSeedTest, initial);
"""
if initial_anchor not in mt:
    raise SystemExit('Missing Hyrum initial matrix anchor')
mt = mt.replace(initial_anchor, initial_new, 1)
follow_matrix_anchor = """    validate(followUpTest, followUp);
    await validateActualOfficialEvidence(followUpTest, followUp);
"""
follow_matrix_new = """    validate(followUpTest, followUp);
    assert(followUp.deterministicHistoryTopic === true && followUp.indexSources === 1 && followUp.officialFetchCalls <= 1,
        'Hyrum contextual follow-up did not preserve single-source deterministic official history retrieval');
    await validateActualOfficialEvidence(followUpTest, followUp);
"""
if follow_matrix_anchor not in mt:
    raise SystemExit('Missing Hyrum follow-up matrix anchor')
mt = mt.replace(follow_matrix_anchor, follow_matrix_new, 1)
matrix.write_text(mt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Executive AI conversational history closeout - candidate 2026-09-03.43\n\n- Production .42 passed all three paced rounds, all permanent Pioneer/Alma/Kirtland regressions, and all burst questions. The next failure occurred later in the matrix at the Hyrum Smith contextual follow-up.\n- A direct live diagnostic reproduced the underlying intermittency: the Hyrum seed question could be rejected despite the exact official Hyrum Smith history topic existing, while the immediate pronoun follow-up could pass at only 71 words after two verifier calls.\n- Candidate .43 therefore extends exact multi-token official Church History topic determinism to the main Ask page as well as Church History. Both the Hyrum seed and its bounded conversation-context retrieval resolve to the same single official Hyrum Smith history topic.\n- Depth repair no longer aims exactly at the publication floor. Faith answers are repaired to at least 25 words and one sentence above the current minimum, and deterministic history-topic prompts explicitly target roughly 100 to 170 words with four sentences. The actual publication floor remains unchanged at 70 words and three sentences.\n- Existing Pioneer .40, Scripture .41, Kirtland .42, official-domain, fail-closed, source relevance, 700-character evidence, request-budget, latency, paraphrase, safety, and rate-limit controls remain unchanged.\n"
if 'Executive AI conversational history closeout - candidate 2026-09-03.43' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
