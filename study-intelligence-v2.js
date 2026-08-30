/* focusChrist Study Intelligence v2
 * Adaptive answer policy layered over the shared Study Intelligence foundation.
 * General questions are answered normally; faith connections are optional,
 * specific, and invitation-based rather than forced devotional closings.
 */
(function () {
    'use strict';

    const PROXY_URL = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
    const MODEL = 'openai/gpt-oss-20b';
    const MAX_TOKENS = 1400;
    const POLICY_VERSION = '2026-08-30.2';

    const FAITH_TERMS = new Set([
        'jesus','christ','savior','redeemer','god','heavenly','father','holy','ghost','spirit',
        'scripture','scriptures','bible','biblical','book','mormon','nephi','alma','mosiah','moroni',
        'doctrine','covenants','dc','temple','temples','prophet','prophets','apostle','apostles',
        'church','latter-day','saint','saints','lds','mormon','atonement','resurrection','revelation',
        'prayer','pray','faith','repentance','baptism','ordinance','ordinances','priesthood','gospel',
        'testimony','commandment','commandments','conference','restoration','joseph','smith'
    ]);

    const HIGH_STAKES_TERMS = new Set([
        'suicide','suicidal','kill','dying','abuse','abused','violence','violent','emergency',
        'diagnosis','medication','medicine','legal','lawyer','court','crime','debt','bankruptcy'
    ]);

    function normalize(text) {
        return String(text || '').toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
    }

    function words(text) {
        return normalize(text).split(' ').filter(Boolean);
    }

    function currentMode() {
        return window.location.pathname.toLowerCase().endsWith('/pioneers.html') ? 'pioneers' : 'ask';
    }

    function classifyQuestion(query) {
        const tokens = words(query);
        if (tokens.some(function (word) { return HIGH_STAKES_TERMS.has(word); })) return 'high-stakes';
        if (currentMode() === 'pioneers') return 'pioneer-study';
        if (tokens.some(function (word) { return FAITH_TERMS.has(word); })) return 'faith-study';
        return 'general-knowledge';
    }

    function scoreLocalKey(query, key) {
        const q = normalize(query);
        const k = normalize(key);
        if (!q || !k) return 0;
        if (q === k) return 100;
        if (q.includes(k)) return 78 + Math.min(15, k.length / 4);

        const qSet = new Set(words(q).filter(function (w) { return w.length > 2; }));
        const kWords = words(k).filter(function (w) { return w.length > 2; });
        if (!kWords.length) return 0;
        let overlap = 0;
        kWords.forEach(function (word) { if (qSet.has(word)) overlap += 1; });
        return (overlap / kWords.length) * 52 + (overlap / Math.max(1, qSet.size)) * 22 + Math.min(12, overlap * 3);
    }

    function bestLocalReference(query) {
        if (typeof qaDatabase === 'undefined' || !qaDatabase) return { found: false, answer: '', sources: [] };
        let bestKey = null;
        let bestScore = 0;
        Object.keys(qaDatabase).forEach(function (key) {
            const score = scoreLocalKey(query, key);
            if (score > bestScore) {
                bestScore = score;
                bestKey = key;
            }
        });
        if (!bestKey || bestScore < 42) return { found: false, answer: '', sources: [], score: bestScore };
        const item = qaDatabase[bestKey] || {};
        return {
            found: true,
            key: bestKey,
            score: bestScore,
            answer: String(item.answer || ''),
            sources: Array.isArray(item.sources) ? item.sources : []
        };
    }

    function recentHistory() {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return [];
        return conversationHistory.slice(-10).filter(function (item) {
            return item && (item.role === 'user' || item.role === 'assistant') && item.content;
        });
    }

    function remember(question, answer) {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return;
        conversationHistory.push({ role: 'user', content: question });
        conversationHistory.push({ role: 'assistant', content: answer });
        if (conversationHistory.length > 20) conversationHistory.splice(0, conversationHistory.length - 20);
        try { sessionStorage.setItem('focuschrist_history', JSON.stringify(conversationHistory)); } catch (_error) {}
    }

    function modeInstructions(profile) {
        if (profile === 'general-knowledge') {
            return [
                'QUESTION MODE: GENERAL KNOWLEDGE.',
                '- Answer the ordinary factual/practical question completely in normal terms first.',
                '- Do NOT append a blessing, devotional phrase, testimony statement, or generic sentence about the love/peace of Jesus Christ.',
                '- Do NOT force religion into the factual answer.',
                '- After the factual answer, if there is a genuinely natural and accurate connection, you MAY add one short optional study bridge beginning with language such as "If you would like..." or "If you are interested...".',
                '- The optional bridge should name the SPECIFIC connection. Example: after explaining why the sky is blue, you might offer to explore how the heavens, light, or color imagery are used in scripture. Do not claim that blue has a fixed biblical meaning unless a reliable source supports that claim.',
                '- If no meaningful faith connection is apparent, simply invite the visitor to ask a follow-up question. Do not manufacture a spiritual analogy.'
            ].join('\n');
        }
        if (profile === 'faith-study') {
            return [
                'QUESTION MODE: FAITH / SCRIPTURE STUDY.',
                '- Answer from a Latter-day Saint perspective when that perspective is relevant.',
                '- Explain the reasoning and relevant scripture or doctrine instead of giving a slogan.',
                '- Jesus Christ may be central when the subject calls for it, but never append a canned devotional closing merely because this is focusChrist.',
                '- Where useful, offer one specific next scripture, Answer Library topic, or follow-up question.'
            ].join('\n');
        }
        if (profile === 'pioneer-study') {
            return [
                'QUESTION MODE: LATTER-DAY SAINT PIONEER / CHURCH HISTORY STUDY.',
                '- Answer the historical question first and distinguish well-established fact from tradition, recollection, inference, and disputed claims.',
                '- Connect history to faith only where historically and spiritually appropriate; do not romanticize suffering or manufacture miracles.',
                '- Suggest a useful source or follow-up only when it adds value.'
            ].join('\n');
        }
        return [
            'QUESTION MODE: HIGH-STAKES OR SENSITIVE.',
            '- Answer cautiously and directly.',
            '- Do not present spiritual counsel as a substitute for qualified medical, mental-health, legal, financial, emergency, or safety help.',
            '- Do not claim God has revealed a private diagnosis, command, or guaranteed outcome.',
            '- Spiritual context may be offered gently if relevant and requested.'
        ].join('\n');
    }

    function systemPrompt(profile, localReference, additionalReference) {
        let prompt = [
            'You are the conversational study assistant for focusChrist, an independent Latter-day Saint faith-based website.',
            'You may answer a very broad range of lawful user questions. The site has a Christ-centered mission, but that mission does NOT require attaching religious language to every answer.',
            '',
            'CORE INTELLIGENCE RULES:',
            '- Identify what the visitor actually asked and answer that first.',
            '- Adapt depth to the question: one or two sentences may be enough for a simple fact; nuanced questions deserve more context.',
            '- Preserve conversational context for follow-up questions and resolve references such as "that," "he," "why," or "what about..." from recent turns when reasonable.',
            '- Be clear, humane, calm, and intelligent. Avoid canned praise, repetitive closings, marketing language, or sermons that were not requested.',
            '- Never begin with "Great question" merely as filler.',
            '- Never end an ordinary answer with generic phrases such as "May the love of Jesus Christ bring you peace," "God bless you," or equivalent boilerplate unless the visitor explicitly asks for a prayer/blessing/devotional response.',
            '- If a question can lead naturally into Christ-centered study, make the connection OPTIONAL and SPECIFIC rather than compulsory.',
            '',
            modeInstructions(profile),
            '',
            'TRUTH / SOURCE DISCIPLINE:',
            '- Never invent scripture wording, quotations, Church teachings, historical details, URLs, statistics, scientific facts, or certainty.',
            '- Distinguish scripture/doctrine, official Church teaching, historical evidence, interpretation, symbolism, and personal application.',
            '- If the local study notes are supplied, treat them as reference notes to evaluate and synthesize, not text that must be repeated.',
            '- If unsure, state the uncertainty briefly instead of bluffing.',
            '- focusChrist is independent and must never be described as an official Church property or endorsed Church answer.',
            '',
            'WRITING:',
            '- Prefer short readable paragraphs.',
            '- Use a brief list only when it improves clarity.',
            '- Avoid unnecessary repetition.',
            '- End with a complete sentence.'
        ].join('\n');

        if (localReference && localReference.found) {
            const sourceText = (localReference.sources || []).map(function (source) {
                return (source.text || 'Source') + (source.url ? ' (' + source.url + ')' : '');
            }).join('; ');
            prompt += '\n\nCURATED LOCAL REFERENCE NOTE:\n' + localReference.answer;
            if (sourceText) prompt += '\nLOCAL LINKED SOURCES:\n' + sourceText;
        }
        if (additionalReference) prompt += '\n\nADDITIONAL PAGE REFERENCE:\n' + additionalReference;
        return prompt;
    }

    function buildMessages(query, profile, localReference, additionalReference) {
        const messages = [{ role: 'system', content: systemPrompt(profile, localReference, additionalReference) }];
        recentHistory().forEach(function (item) {
            messages.push({ role: item.role, content: String(item.content) });
        });
        messages.push({ role: 'user', content: query });
        return messages;
    }

    async function request(messages, timeoutMs) {
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timer = controller ? window.setTimeout(function () { controller.abort(); }, timeoutMs) : null;
        try {
            const response = await fetch(PROXY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: MODEL,
                    messages: messages,
                    temperature: 0.35,
                    max_tokens: MAX_TOKENS
                }),
                signal: controller ? controller.signal : undefined
            });
            if (!response.ok) throw new Error('Study service returned ' + response.status);
            const data = await response.json();
            const content = data && data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : '';
            if (!content) throw new Error('Empty study response');
            return String(content).trim();
        } finally {
            if (timer) window.clearTimeout(timer);
        }
    }

    function removeBoilerplateClosing(answer, profile) {
        if (profile !== 'general-knowledge') return answer;
        let cleaned = String(answer || '').trim();
        const patterns = [
            /\s*May (?:the )?(?:love|peace|grace|light) of Jesus Christ[^.!?]*[.!?]\s*$/i,
            /\s*May (?:God|the Lord) bless you[^.!?]*[.!?]?\s*$/i,
            /\s*God bless you[^.!?]*[.!?]?\s*$/i,
            /\s*Through Jesus Christ[^.!?]*peace[^.!?]*[.!?]\s*$/i
        ];
        patterns.forEach(function (pattern) { cleaned = cleaned.replace(pattern, '').trim(); });
        return cleaned;
    }

    async function askV2(query, additionalReference) {
        const profile = classifyQuestion(query);
        const localReference = bestLocalReference(query);
        const messages = buildMessages(query, profile, localReference, additionalReference || '');
        let lastError = null;

        for (const timeout of [24000, 17000]) {
            try {
                let answer = await request(messages, timeout);
                answer = removeBoilerplateClosing(answer, profile);
                if (!answer) throw new Error('Response removed as empty');
                remember(query, answer);
                return {
                    answer: answer,
                    sources: localReference.found ? localReference.sources : [],
                    profile: profile,
                    localMatch: localReference.found ? localReference.key : null
                };
            } catch (error) {
                lastError = error;
                console.warn('focusChrist Study Intelligence v2 attempt failed:', error && error.message ? error.message : error);
            }
        }

        console.error('focusChrist Study Intelligence v2 failed:', lastError);
        return {
            answer: 'I could not complete that answer just now. Please try again, rephrase the question, or continue with the study resources on this page.',
            sources: [],
            profile: profile,
            localMatch: null
        };
    }

    function loadingNode() {
        const node = document.createElement('div');
        node.className = 'loading';
        node.setAttribute('role', 'status');
        node.textContent = 'Thinking through your question…';
        return node;
    }

    function installAskSendMessage() {
        window.sendMessage = async function () {
            const input = document.getElementById('userInput');
            const button = document.getElementById('sendBtn');
            const box = document.getElementById('chatBox');
            if (!input || !button || !box || typeof window.addMessage !== 'function') return;

            const question = input.value.trim();
            if (!question) return;
            box.querySelectorAll('.welcome, .ask-welcome').forEach(function (node) { node.remove(); });
            window.addMessage(question, true, []);
            input.value = '';
            input.disabled = true;
            button.disabled = true;
            button.textContent = 'Thinking…';
            const loading = loadingNode();
            box.appendChild(loading);
            box.scrollTop = box.scrollHeight;

            try {
                if (typeof window.containsInappropriate === 'function' && window.containsInappropriate(question)) {
                    loading.remove();
                    window.addMessage('I can help with respectful and safe questions. Please rephrase the request in a way I can assist with.', false, []);
                    return;
                }
                const result = await askV2(question, '');
                if (loading.isConnected) loading.remove();
                window.addMessage(result.answer, false, result.sources);
            } catch (error) {
                console.error('focusChrist Ask v2 error:', error);
                if (loading.isConnected) loading.remove();
                window.addMessage('I could not complete that answer just now. Please try again.', false, []);
            } finally {
                input.disabled = false;
                button.disabled = false;
                button.textContent = 'Ask';
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }
        };
    }

    window.focusChristStudyAskV2 = askV2;
    window.askAI = function (query, contextEntries) {
        return askV2(query, contextEntries || '');
    };

    if (currentMode() === 'ask') installAskSendMessage();

    document.documentElement.setAttribute('data-focuschrist-study-intelligence-version', '2');
    console.info('focusChrist Study Intelligence policy ' + POLICY_VERSION + ' active.');
})();
