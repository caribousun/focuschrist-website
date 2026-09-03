from pathlib import Path

worker = Path('groq-proxy/src/index.js')
w = worker.read_text(encoding='utf-8')

for old, new in [
    ("const SOURCE_POLICY_VERSION = '2026-09-03.43';", "const SOURCE_POLICY_VERSION = '2026-09-03.44';"),
    ("const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.43';", "const OFFICIAL_EXCERPT_CACHE_VERSION = '2026-09-03.44';"),
]:
    if old not in w:
        raise SystemExit('Missing version anchor: ' + old)
    w = w.replace(old, new, 1)

contract_anchor = """function answerMeetsSubstanceContract(answer, scope) {
  const text = String(answer || '').replace(/\\s+/g, ' ').trim();
  const original = String(answer || '').trim();
  const requirements = answerSubstanceRequirements(scope);
  const words = text ? text.split(' ').filter(Boolean).length : 0;
  const sentences = countCompleteSentences(text);
  const paragraphs = original ? original.split(/\\n\\s*\\n/).filter((value) => value.trim()).length : 0;
  return words >= requirements.minimumWords
    && sentences >= requirements.minimumSentences
    && paragraphs >= requirements.minimumParagraphs;
}

function countCompleteSentences(answer) {
"""
contract_replacement = """function answerMeetsSubstanceContract(answer, scope) {
  const text = String(answer || '').replace(/\\s+/g, ' ').trim();
  const original = String(answer || '').trim();
  const requirements = answerSubstanceRequirements(scope);
  const words = text ? text.split(' ').filter(Boolean).length : 0;
  const sentences = countCompleteSentences(text);
  const paragraphs = original ? original.split(/\\n\\s*\\n/).filter((value) => value.trim()).length : 0;
  return words >= requirements.minimumWords
    && sentences >= requirements.minimumSentences
    && paragraphs >= requirements.minimumParagraphs;
}

function answerMeetsRepairMargin(answer, scope) {
  const text = String(answer || '').replace(/\\s+/g, ' ').trim();
  const original = String(answer || '').trim();
  const words = text ? text.split(' ').filter(Boolean).length : 0;
  const sentences = countCompleteSentences(text);
  const paragraphs = original ? original.split(/\\n\\s*\\n/).filter((value) => value.trim()).length : 0;
  if (scope && scope.selectedPioneer) return words >= 120 && sentences >= 4 && paragraphs >= 2;
  if (scope && scope.faith) return words >= 95 && sentences >= 4 && paragraphs >= 1;
  return words >= 55 && sentences >= 3 && paragraphs >= 1;
}

function countCompleteSentences(answer) {
"""
if contract_anchor not in w:
    raise SystemExit('Missing answer contract insertion anchor')
w = w.replace(contract_anchor, contract_replacement, 1)

old_depth = """      const needsDepthRepair = Boolean(verdict && verdict.approved === true && indexes.length
        && !answerMeetsSubstanceContract(verdict.answer, sanitized.scope));
"""
new_depth = """      const needsDepthRepair = Boolean(verdict && verdict.approved === true && indexes.length
        && (!answerMeetsSubstanceContract(verdict.answer, sanitized.scope)
          || ((retrievalDiagnostic.focuschrist_deterministic_history_topic === true
            || sanitized.scope.classificationMode === 'conversation-context')
            && !answerMeetsRepairMargin(verdict.answer, sanitized.scope))));
"""
if old_depth not in w:
    raise SystemExit('Missing needsDepthRepair anchor')
w = w.replace(old_depth, new_depth, 1)

old_depth_prompt = """            ? `Rewrite it using at least ${repairMinimumWords} words, ${repairMinimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s). The publication gate is lower, but this repair target deliberately includes safety margin. Do not stop at the minimum.`
"""
new_depth_prompt = """            ? `Rewrite it using at least ${repairMinimumWords} words, ${repairMinimumSentences} complete sentences, and ${requirements.minimumParagraphs} paragraph(s). The publication gate is lower, but this repair target deliberately includes safety margin. Do not stop at the minimum. For a conversation-context or deterministic Church History answer, treat this margin as mandatory for the repaired draft.`
"""
if old_depth_prompt not in w:
    raise SystemExit('Missing depth repair prompt anchor')
w = w.replace(old_depth_prompt, new_depth_prompt, 1)

export_anchor = "  answerMeetsSubstanceContract,\n"
pos = w.rfind(export_anchor)
if pos < 0:
    raise SystemExit('Missing answerMeetsSubstanceContract export anchor')
w = w[:pos] + w[pos:].replace(export_anchor, export_anchor + "  answerMeetsRepairMargin,\n", 1)
worker.write_text(w, encoding='utf-8')

for path in ['groq-proxy/source-policy.test.js', 'groq-proxy/church-source-index.test.js', 'tools/pioneer_local_first_qa.py', 'tools/scripture_grounding_qa.py']:
    p = Path(path)
    p.write_text(p.read_text(encoding='utf-8').replace('2026-09-03.43', '2026-09-03.44'), encoding='utf-8')

index_test = Path('groq-proxy/church-source-index.test.js')
it = index_test.read_text(encoding='utf-8')
import_anchor = "  compactParagraphPack,\n"
if import_anchor not in it:
    raise SystemExit('Missing unit-test import anchor')
it = it.replace(import_anchor, "  answerMeetsRepairMargin,\n  compactParagraphPack,\n", 1)
margin_test_anchor = """function assert(condition, message) {
  if (!condition) throw new Error(message);
}

"""
margin_test = margin_test_anchor + """const boundaryFaithAnswer = [
  'Hyrum Smith held an important leadership responsibility in the early Church and assisted senior Church leadership during a demanding period of growth and change.',
  'He also carried other significant responsibilities that placed him near the center of Church administration and service during the Nauvoo period.',
  'These duties show that his role involved substantial leadership responsibility within the developing Church organization.'
].join(' ');
assert(!answerMeetsRepairMargin(boundaryFaithAnswer, { faith: true }),
  'faith repair margin must reject a three-sentence answer that sits near the publication boundary');

"""
if margin_test_anchor not in it:
    raise SystemExit('Missing unit-test insertion anchor')
it = it.replace(margin_test_anchor, margin_test, 1)
index_test.write_text(it, encoding='utf-8')

matrix = Path('tools/live_ai_response_matrix.js')
mt = matrix.read_text(encoding='utf-8')
if "const POLICY_VERSION = '2026-09-03.43';" not in mt:
    raise SystemExit('Missing matrix policy anchor')
mt = mt.replace("const POLICY_VERSION = '2026-09-03.43';", "const POLICY_VERSION = '2026-09-03.44';", 1)

follow_anchor = """    validate(followUpTest, followUp);
    assert(followUp.deterministicHistoryTopic === true && followUp.indexSources === 1 && followUp.officialFetchCalls <= 1,
        'Hyrum contextual follow-up did not preserve single-source deterministic official history retrieval');
    await validateActualOfficialEvidence(followUpTest, followUp);
"""
follow_replacement = """    validate(followUpTest, followUp);
    assert(followUp.deterministicHistoryTopic === true && followUp.indexSources === 1 && followUp.officialFetchCalls <= 1,
        'Hyrum contextual follow-up did not preserve single-source deterministic official history retrieval');
    await validateActualOfficialEvidence(followUpTest, followUp);
    const repeatedFollowUps = [];
    for (let repetition = 1; repetition <= 3; repetition += 1) {
        await new Promise((resolve) => setTimeout(resolve, INTER_REQUEST_DELAY_MS));
        const repeated = await submit({ ...followUpTest, id: `follow-up-context-repeat-${repetition}` }, [
            { role: 'user', content: hyrumSeedTest.question },
            { role: 'assistant', content: initial.answer },
            { role: 'user', content: followUpTest.question },
        ]);
        validate(followUpTest, repeated);
        assert(repeated.deterministicHistoryTopic === true && repeated.indexSources === 1 && repeated.officialFetchCalls <= 1,
            `Hyrum repeated contextual follow-up ${repetition} lost deterministic official-history retrieval`);
        await validateActualOfficialEvidence(followUpTest, repeated);
        repeatedFollowUps.push(repeated);
    }
"""
if follow_anchor not in mt:
    raise SystemExit('Missing follow-up matrix anchor')
mt = mt.replace(follow_anchor, follow_replacement, 1)
all_anchor = """    const allMeasured = [...results, ...regressionResults, ...burstResults, ...blockedResults, ...respectfulResults,
        invalidCorinthians, invalidAlma, initial, followUp, reset, warmFirst, warmSecond];
"""
all_replacement = """    const allMeasured = [...results, ...regressionResults, ...burstResults, ...blockedResults, ...respectfulResults,
        invalidCorinthians, invalidAlma, initial, followUp, ...repeatedFollowUps, reset, warmFirst, warmSecond];
"""
if all_anchor not in mt:
    raise SystemExit('Missing allMeasured anchor')
mt = mt.replace(all_anchor, all_replacement, 1)
matrix.write_text(mt, encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n\n### Executive AI depth-margin closeout - candidate 2026-09-03.44\n\n- Production .43 again reached the Hyrum Smith contextual follow-up and failed intermittently on answer depth. A fresh direct live diagnostic showed the seed stable at 102 words and the follow-up at exactly 70 words, proving the remaining defect is stochastic boundary-depth output rather than source routing.\n- Candidate .44 does not lower the 70-word/three-sentence faith publication floor. It adds a repair-margin contract of 95 words/four sentences for faith answers and 120 words/four sentences/two paragraphs for selected Pioneer biographies. The margin is used to trigger the existing bounded second verifier pass for deterministic Church History and conversation-context answers that sit too close to the floor.\n- The two-verifier-call ceiling remains unchanged. Official-source restrictions, fail-closed behavior, evidence relevance, 700-character evidence, deterministic Pioneer/Scripture/History routing, latency, safety, paraphrase, and rate-limit controls remain unchanged.\n- The production live matrix now repeats the Hyrum contextual follow-up three additional times and requires every repeat to preserve deterministic single-source official-history retrieval and the existing publication contract.\n"
if 'Executive AI depth-margin closeout - candidate 2026-09-03.44' not in mem:
    memory.write_text(mem + note, encoding='utf-8')
