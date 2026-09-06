// Run every visible Pioneer topic against production; never count a fallback as a pass.
(async () => {
    const { PIONEER_TOPIC_SOURCES } = await import('../groq-proxy/src/pioneer-topic-sources.js');
    const { OFFICIAL_EXCERPT_CACHE_VERSION } = await import('../groq-proxy/src/index.js');
    const results = [];
    for (const [key, topic] of Object.entries(PIONEER_TOPIC_SOURCES)) {
        if (results.length) await new Promise(resolve => setTimeout(resolve, 5000));
        try {
            const response = await fetch('https://focuschrist-groq-proxy.caribousun.workers.dev', {
                method: 'POST', headers: { Origin: 'https://focuschrist.com', 'Content-Type': 'application/json' },
                body: JSON.stringify({ focuschrist_page: 'pioneers', focuschrist_profile: 'pioneer-study',
                    focuschrist_pioneer_topic: key, messages: [{ role: 'user', content: 'Explain ' + topic.subject }] }),
                signal: AbortSignal.timeout(26000)
            });
            const data = await response.json();
            const answer = data.choices?.[0]?.message?.content || '';
            const words = answer.trim().split(/\s+/).length;
            const urls = (data.focuschrist_sources || []).map(source => source.url);
            const passed = response.ok && data.focuschrist_source_integrity_verified === true
                && data.focuschrist_source_policy === OFFICIAL_EXCERPT_CACHE_VERSION
                && data.focuschrist_pioneer_disclosure === true && words >= 70
                && urls.includes(topic.url) && data.focuschrist_index_sources === 1
                && data.focuschrist_official_fetch_calls <= 1;
            const result = { key, passed, words, urls, answer, reason: data.focuschrist_verifier_publication_failure || data.focuschrist_gateway_mode };
            results.push(result); console.log(JSON.stringify(result));
        } catch (error) {
            const result = { key, passed: false, error: error.message };
            results.push(result); console.log(JSON.stringify(result));
        }
    }
    const failures = results.filter(result => !result.passed);
    console.log('Pioneer disclosure live QA: ' + (failures.length ? 'FAIL' : 'PASS') + ', ' + (results.length - failures.length) + '/' + results.length);
    if (failures.length) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
