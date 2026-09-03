from pathlib import Path


def replace(path, old, new, count=None):
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f'missing expected text in {path}: {old[:120]!r}')
    if count is None:
        text = text.replace(old, new)
    else:
        text = text.replace(old, new, count)
    p.write_text(text)

# Advance the Worker/source-policy release wherever the executable gates pin it.
for path in [
    'groq-proxy/src/index.js',
    'groq-proxy/source-policy.test.js',
    'tools/live_ai_response_matrix.js',
    'tools/pioneer_local_first_qa.py',
    'tools/scripture_grounding_qa.py',
]:
    p = Path(path)
    text = p.read_text()
    text = text.replace('2026-09-03.48', '2026-09-03.49')
    p.write_text(text)

index_path = Path('groq-proxy/src/index.js')
index = index_path.read_text()
needle = """      if ((!draft && retrievalDiagnostic.focuschrist_retrieval_route !== 'church-source-index') || !evidence.length) {
        return jsonResponse(fallbackPayload(
          'research-insufficient-evidence',
          { ...(sanitized.scope.lowRiskDiagnostic || {}), ...retrievalDiagnostic },
          sanitized.scope,
        ), 200, origin);
      }

      const verifierPrompt = sanitized.scope.selectedPioneer ? [
"""
replacement = """      if ((!draft && retrievalDiagnostic.focuschrist_retrieval_route !== 'church-source-index') || !evidence.length) {
        return jsonResponse(fallbackPayload(
          'research-insufficient-evidence',
          { ...(sanitized.scope.lowRiskDiagnostic || {}), ...retrievalDiagnostic },
          sanitized.scope,
        ), 200, origin);
      }

      // Exact reviewed recoveries do not need a stochastic model verdict once the
      // Worker has already retrieved and validated their pinned official source.
      // This keeps these narrow owner journeys available during provider faults or
      // rate pressure without weakening the fail-closed contract for any other ask.
      const reviewedDeterministic = retrievalDiagnostic.focuschrist_retrieval_route === 'church-source-index'
        ? reviewedDeterministicEvidenceRecovery(sanitized.scope.retrievalQuestion, evidence)
        : null;
      if (reviewedDeterministic) {
        const recoveryIndexes = reviewedDeterministic.sourceIndexes
          .filter((sourceIndex) => Number.isInteger(sourceIndex) && sourceIndex >= 1 && sourceIndex <= evidence.length);
        const recoveryEvidence = recoveryIndexes.map((sourceIndex) => evidence[sourceIndex - 1]);
        const recoveryAnswer = guardVerifiedAnswer(
          reviewedDeterministic.answer,
          recoveryEvidence,
          sanitized.scope,
          recoveryEvidence.length > 0,
        );
        if (recoveryAnswer !== SOURCE_INTEGRITY_FALLBACK && recoveryEvidence.length > 0) {
          return jsonResponse({
            id: 'focuschrist-reviewed-deterministic-evidence',
            choices: [{
              index: 0,
              message: { role: 'assistant', content: recoveryAnswer },
              finish_reason: 'stop',
            }],
            focuschrist_sources: recoveryEvidence.map((source) => ({
              text: source.title || 'Source',
              url: source.url,
            })),
            focuschrist_source_integrity_verified: true,
            focuschrist_source_policy: SOURCE_POLICY_VERSION,
            focuschrist_gateway_mode: 'retrieval-researched-and-verified',
            focuschrist_resolved_profile: sanitized.scope.faith ? 'faith-study' : (sanitized.scope.profile || 'general-knowledge'),
            focuschrist_classification_mode: sanitized.scope.classificationMode || 'request-scope',
            focuschrist_answer_word_count: recoveryAnswer.split(/\\s+/).filter(Boolean).length,
            focuschrist_evidence_relevance: evidenceRelevanceReceipt(sanitized.scope.retrievalQuestion, recoveryEvidence),
            focuschrist_verifier_route: 'reviewed-deterministic',
            focuschrist_cloudflare_verifier_calls: 0,
            focuschrist_groq_verifier_calls: 0,
            focuschrist_openai_verifier_calls: 0,
            focuschrist_verifier_conservative_unmetered_neurons: 0,
            focuschrist_reviewed_deterministic_recovery: reviewedDeterministic.recoveryId,
            ...retrievalDiagnostic,
          }, 200, origin);
        }
      }

      const verifierPrompt = sanitized.scope.selectedPioneer ? [
"""
if needle not in index:
    raise SystemExit('could not locate deterministic pre-verifier insertion point')
index = index.replace(needle, replacement, 1)
index_path.write_text(index)

# Teach the live acceptance matrix that a reviewed deterministic source-gated
# answer is intentionally provider-free. All other official-only answers retain
# the existing model-usage receipt requirements.
matrix_path = Path('tools/live_ai_response_matrix.js')
matrix = matrix_path.read_text()
old = """            deterministicScripture: payload.focuschrist_deterministic_scripture === true,
            deterministicHistoryTopic: payload.focuschrist_deterministic_history_topic === true,
        };
"""
new = """            deterministicScripture: payload.focuschrist_deterministic_scripture === true,
            deterministicHistoryTopic: payload.focuschrist_deterministic_history_topic === true,
            reviewedRecovery: String(payload.focuschrist_reviewed_deterministic_recovery || ''),
        };
"""
if old not in matrix:
    raise SystemExit('could not locate live matrix receipt fields')
matrix = matrix.replace(old, new, 1)
old = """        assert(['groq-primary', 'groq-primary-repair', 'openai-fallback', 'openai-repair', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute), test.id + ' omitted a verifier route');
"""
new = """        assert(['reviewed-deterministic', 'groq-primary', 'groq-primary-repair', 'openai-fallback', 'openai-repair', 'cloudflare-primary', 'cloudflare-fast-fallback', 'groq-fallback'].includes(result.verifierRoute), test.id + ' omitted a verifier route');
"""
if old not in matrix:
    raise SystemExit('could not locate verifier route allowlist')
matrix = matrix.replace(old, new, 1)
old = """        assert(result.verifierInputTokens > 0 && result.verifierOutputTokens > 0, test.id + ' omitted verifier usage receipts');
        const verifierCallTotal = result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls;
        assert(result.cloudflareVerifierCalls >= 0 && result.cloudflareVerifierCalls <= 2
            && result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2
            && result.openaiVerifierCalls >= 0 && result.openaiVerifierCalls <= 2
            && verifierCallTotal >= 1 && verifierCallTotal <= 3,
        test.id + ' returned invalid per-provider verifier call accounting');
        assert(!(result.openaiVerifierCalls > 0 && result.cloudflareVerifierCalls > 0),
            test.id + ' mixed Cloudflare and OpenAI verifier routes');
        assert(!(result.openaiVerifierCalls === 2 && result.groqVerifierCalls !== 1),
            test.id + ' used two Luna calls without one failed Groq primary attempt');
        assert(!(result.groqVerifierCalls > 0 && result.cloudflareVerifierCalls > 1),
            test.id + ' stacked verifier fallback with depth repair');
        if (result.verifierRoute.startsWith('cloudflare-')) assert(result.estimatedNeurons > 0, test.id + ' omitted Cloudflare neuron accounting');
"""
new = """        const reviewedDeterministic = result.verifierRoute === 'reviewed-deterministic';
        const verifierCallTotal = result.cloudflareVerifierCalls + result.groqVerifierCalls + result.openaiVerifierCalls;
        if (reviewedDeterministic) {
            assert(result.reviewedRecovery.length > 0,
                test.id + ' used the deterministic verifier route without an audited recovery receipt');
            assert(result.verifierInputTokens === 0 && result.verifierOutputTokens === 0 && verifierCallTotal === 0,
                test.id + ' deterministic reviewed recovery unexpectedly consumed a verifier provider');
        } else {
            assert(result.verifierInputTokens > 0 && result.verifierOutputTokens > 0, test.id + ' omitted verifier usage receipts');
            assert(result.cloudflareVerifierCalls >= 0 && result.cloudflareVerifierCalls <= 2
                && result.groqVerifierCalls >= 0 && result.groqVerifierCalls <= 2
                && result.openaiVerifierCalls >= 0 && result.openaiVerifierCalls <= 2
                && verifierCallTotal >= 1 && verifierCallTotal <= 3,
            test.id + ' returned invalid per-provider verifier call accounting');
            assert(!(result.openaiVerifierCalls > 0 && result.cloudflareVerifierCalls > 0),
                test.id + ' mixed Cloudflare and OpenAI verifier routes');
            assert(!(result.openaiVerifierCalls === 2 && result.groqVerifierCalls !== 1),
                test.id + ' used two Luna calls without one failed Groq primary attempt');
            assert(!(result.groqVerifierCalls > 0 && result.cloudflareVerifierCalls > 1),
                test.id + ' stacked verifier fallback with depth repair');
            if (result.verifierRoute.startsWith('cloudflare-')) assert(result.estimatedNeurons > 0, test.id + ' omitted Cloudflare neuron accounting');
        }
"""
if old not in matrix:
    raise SystemExit('could not locate verifier receipt assertions')
matrix = matrix.replace(old, new, 1)
matrix_path.write_text(matrix)

# Permanent source-policy contract: the deterministic pre-verifier lane must be
# explicitly present, source-gated, and provider-free.
test_path = Path('groq-proxy/source-policy.test.js')
test = test_path.read_text()
anchor = """assert(reviewedDeterministicEvidenceRecovery(
  'Tell me about the Kirtland Temple.',
  [{ url: 'https://www.churchofjesuschrist.org/study/history/topics/kirtland-temple?lang=eng', content: 'Kirtland Temple history.' }],
) === null, 'reviewed Relief Society recovery must not activate for unrelated Church History topics');

"""
addition = anchor + """const workerSourceForDeterministicLane = await import('node:fs').then((fs) => fs.readFileSync(new URL('./src/index.js', import.meta.url), 'utf8'));
const deterministicLanePosition = workerSourceForDeterministicLane.indexOf("const reviewedDeterministic = retrievalDiagnostic.focuschrist_retrieval_route === 'church-source-index'");
const verifierPromptPosition = workerSourceForDeterministicLane.indexOf('const verifierPrompt = sanitized.scope.selectedPioneer');
assert(deterministicLanePosition >= 0 && verifierPromptPosition > deterministicLanePosition
  && workerSourceForDeterministicLane.includes("focuschrist_verifier_route: 'reviewed-deterministic'")
  && workerSourceForDeterministicLane.includes('focuschrist_groq_verifier_calls: 0')
  && workerSourceForDeterministicLane.includes('focuschrist_openai_verifier_calls: 0'),
  'audited deterministic evidence recoveries must resolve before verifier providers are invoked');

"""
if anchor not in test:
    raise SystemExit('could not locate deterministic recovery test anchor')
test = test.replace(anchor, addition, 1)
test_path.write_text(test)

memory = Path('MEMORY.md')
mem = memory.read_text()
note = """
- 2026-09-03 policy `.49` candidate: the final `.48` production matrix passed all doctrine, scripture, pioneer, Relief Society, regression, and burst cases but failed only the final warm-cache Enos check after sustained provider traffic. Root cause: exact audited deterministic evidence was still sent through stochastic verifier providers before recovery. `.49` moves the existing Enos 1 and Relief Society source-gated reviewed recoveries ahead of verifier invocation once the exact official indexed evidence has been fetched. Those narrow lanes now use `reviewed-deterministic`, consume zero verifier calls, and retain exact Church source, evidence-relevance, cache, classification, and source-integrity receipts. Every unrelated question remains on the existing fail-closed verifier contract.
"""
if note.strip() not in mem:
    memory.write_text(mem.rstrip() + '\n' + note)
