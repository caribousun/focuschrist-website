from pathlib import Path

matrix = Path('tools/live_ai_response_matrix.js')
text = matrix.read_text(encoding='utf-8')
old = """    const indexedNeuronCosts = indexed.map((result) =>
        Number(result.estimatedNeurons || 0) + Number(result.conservativeUnmeteredNeurons || 0));
    assert(indexedNeuronCosts.length >= 15 && indexedNeuronCosts.every((cost) => cost > 0),
        'insufficient complete indexed usage samples for capacity proof');
    const p95IndexedNeurons = percentile(indexedNeuronCosts, 0.95);
    assert(indexed.some((result) => result.cacheMisses > 0), 'no cold official-source cache miss was observed');
    const nightlyAuditNeurons = results.slice(0, 5).reduce((sum, result) => sum
        + Number(result.estimatedNeurons || 0) + Number(result.conservativeUnmeteredNeurons || 0), 0);
    const visitorReserve = Math.max(1, 8000 - nightlyAuditNeurons);
    const conservativeDailyCapacity = Math.floor(visitorReserve / Math.max(1, p95IndexedNeurons));
    assert(conservativeDailyCapacity >= 50, 'measured capacity after nightly audit is below 50 daily questions: ' + conservativeDailyCapacity);
    const p95 = percentile(times, 0.95);
    assert(p95 <= P95_LIMIT_MS, 'matrix p95 exceeded 20 seconds: ' + p95 + 'ms');
    assert(allMeasured.every((result) => !result.error), 'one or more matrix requests failed');
    console.log('Live AI response matrix PASS: ' + JSON.stringify({ count: allMeasured.length, indexed: indexed.length,
        groqResearchCalls: allMeasured.reduce((sum, result) => sum + Number(result.groqResearchCalls || 0), 0),
        p95Ms: p95, maxMs: Math.max(...times), burst: burstResults.length, p95IndexedNeurons,
        nightlyAuditNeurons, conservativeDailyCapacity, warmCacheHits: warmSecond.cacheHits }));
"""
new = """    const indexedNeuronCosts = indexed.map((result) =>
        Number(result.estimatedNeurons || 0) + Number(result.conservativeUnmeteredNeurons || 0));
    assert(indexed.length >= 15, 'insufficient indexed usage samples for capacity proof');
    assert(indexedNeuronCosts.every((cost) => cost === 0),
        'indexed faith traffic unexpectedly consumed Cloudflare AI neurons');
    const externalVerifierSamples = indexed.filter((result) => result.verifierRoute !== 'reviewed-deterministic');
    const externalVerifierCallCounts = externalVerifierSamples.map((result) =>
        Number(result.cloudflareVerifierCalls || 0) + Number(result.groqVerifierCalls || 0) + Number(result.openaiVerifierCalls || 0));
    assert(externalVerifierCallCounts.length >= 15
        && externalVerifierCallCounts.every((count) => count >= 1 && count <= 3),
        'insufficient complete external-verifier usage samples for bounded-capacity proof');
    const p95VerifierCalls = percentile(externalVerifierCallCounts, 0.95);
    const projectedVerifierCallsAt50Daily = p95VerifierCalls * 50;
    assert(projectedVerifierCallsAt50Daily <= 150,
        'bounded verifier fan-out exceeds 150 calls for 50 daily indexed questions: ' + projectedVerifierCallsAt50Daily);
    assert(indexed.some((result) => result.cacheMisses > 0), 'no cold official-source cache miss was observed');
    const p95 = percentile(times, 0.95);
    assert(p95 <= P95_LIMIT_MS, 'matrix p95 exceeded 20 seconds: ' + p95 + 'ms');
    assert(allMeasured.every((result) => !result.error), 'one or more matrix requests failed');
    console.log('Live AI response matrix PASS: ' + JSON.stringify({ count: allMeasured.length, indexed: indexed.length,
        groqResearchCalls: allMeasured.reduce((sum, result) => sum + Number(result.groqResearchCalls || 0), 0),
        p95Ms: p95, maxMs: Math.max(...times), burst: burstResults.length,
        cloudflareIndexedNeurons: indexedNeuronCosts.reduce((sum, cost) => sum + cost, 0),
        p95VerifierCalls, projectedVerifierCallsAt50Daily, warmCacheHits: warmSecond.cacheHits }));
"""
if old not in text:
    raise SystemExit('target capacity block not found')
matrix.write_text(text.replace(old, new), encoding='utf-8')

memory = Path('MEMORY.md')
mem = memory.read_text(encoding='utf-8')
note = "\n- 2026-09-03 production acceptance accounting: the old 8,000-Cloudflare-neuron capacity proof became invalid after faith verification moved to Groq/OpenAI and reviewed deterministic answers began correctly reporting zero verifier usage. The live matrix now requires zero Cloudflare AI neuron consumption on indexed faith traffic, at least 15 complete external-verifier samples with one to three bounded verifier calls, and a 50-question/day projection of no more than 150 verifier calls. Worker policy remains .53 because this is an acceptance-harness correction, not a runtime policy change.\n"
if note.strip() not in mem:
    memory.write_text(mem + note, encoding='utf-8')
