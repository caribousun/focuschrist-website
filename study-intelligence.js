/* focusChrist shared Study Intelligence layer.
 * Improves Ask/Pioneer AI depth, visible conversation continuity, grounding,
 * retries, and safe answer presentation without exposing secrets client-side.
 */
(function () {
    'use strict';

    const PROXY_URL = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
    const MODEL = 'openai/gpt-oss-20b';
    const MAX_OUTPUT_TOKENS = 1200;
    const FIRST_TIMEOUT_MS = 22000;
    const RETRY_TIMEOUT_MS = 16000;

    function pageMode() {
        const path = window.location.pathname.toLowerCase();
        return path.endsWith('/pioneers.html') ? 'pioneers' : 'ask';
    }

    function normalize(text) {
        return String(text || '')
            .toLowerCase()
            .replace(/[^a-z0-9\s'-]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function tokenize(text) {
        const stop = new Set(['a','an','and','are','as','at','be','but','by','for','from','how','i','in','is','it','of','on','or','that','the','their','this','to','what','when','where','which','who','why','with','you','your']);
        return normalize(text).split(' ').filter(function (word) {
            return word.length > 2 && !stop.has(word);
        });
    }

    function scoreKey(query, key) {
        const q = normalize(query);
        const k = normalize(key);
        if (!q || !k) return 0;
        if (q === k) return 100;
        if (q.includes(k)) return 70 + Math.min(20, k.length / 3);

        const qTokens = new Set(tokenize(q));
        const kTokens = tokenize(k);
        if (!kTokens.length) return 0;
        let overlap = 0;
        kTokens.forEach(function (token) {
            if (qTokens.has(token)) overlap += 1;
        });
        const coverage = overlap / kTokens.length;
        const precision = overlap / Math.max(1, qTokens.size);
        return (coverage * 45) + (precision * 20) + Math.min(12, overlap * 3);
    }

    function enhancedLocalMatch(query) {
        if (typeof qaDatabase === 'undefined' || !qaDatabase) {
            return typeof window.findAnswer === 'function' ? window.findAnswer(query) : { found: false, answer: '', sources: [] };
        }

        let bestKey = null;
        let bestScore = 0;
        Object.keys(qaDatabase).forEach(function (key) {
            const score = scoreKey(query, key);
            if (score > bestScore) {
                bestScore = score;
                bestKey = key;
            }
        });

        // Require a meaningful semantic/phrase match. Weak matches are more
        // dangerous than no match because local notes may be very specific.
        if (!bestKey || bestScore < 38) return { found: false, answer: '', sources: [], confidence: bestScore };
        const match = qaDatabase[bestKey] || {};
        return {
            found: true,
            answer: String(match.answer || ''),
            sources: Array.isArray(match.sources) ? match.sources : [],
            confidence: bestScore,
            key: bestKey
        };
    }

    function historyLimit() {
        if (typeof MAX_CONVERSATION_LENGTH !== 'undefined' && Number(MAX_CONVERSATION_LENGTH) > 0) {
            return Math.min(12, Number(MAX_CONVERSATION_LENGTH));
        }
        return 10;
    }

    function currentHistory() {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return [];
        return conversationHistory.slice(-historyLimit());
    }

    function rememberExchange(question, answer) {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return;
        conversationHistory.push({ role: 'user', content: question });
        conversationHistory.push({ role: 'assistant', content: answer });
        const max = historyLimit() * 2;
        if (conversationHistory.length > max) conversationHistory.splice(0, conversationHistory.length - max);
        try {
            sessionStorage.setItem('focuschrist_history', JSON.stringify(conversationHistory));
        } catch (_error) {}
    }

    function systemPrompt(mode, referenceContent) {
        const historyFocus = mode === 'pioneers'
            ? 'You are helping a visitor study Latter-day Saint pioneer and Church history while keeping the broader story connected to faith in Jesus Christ.'
            : 'You are helping a visitor study Jesus Christ, scripture, and Latter-day Saint belief.';

        let prompt = [
            'You are the study assistant for focusChrist, an independent Latter-day Saint faith-based website.',
            historyFocus,
            '',
            'ANSWER QUALITY:',
            '- Answer the exact question first. Do not begin with generic praise such as "great question."',
            '- Be warm, clear, thoughtful, and conversational rather than preachy or corporate.',
            '- For a simple factual question, be concise. For a doctrinal, scriptural, historical, or personal-study question, give enough context to genuinely help.',
            '- Use short paragraphs and, when useful, a brief list. Do not produce a wall of text.',
            '- Treat follow-up questions as part of the ongoing conversation. Resolve pronouns and references from recent context when reasonable.',
            '- Center Jesus Christ naturally when He is genuinely relevant; do not force the same closing sentence onto every answer.',
            '',
            'SOURCE AND DOCTRINE DISCIPLINE:',
            '- Represent the teachings of The Church of Jesus Christ of Latter-day Saints accurately and distinguish doctrine, scripture, historical fact, interpretation, and personal application.',
            '- Never invent a quotation, scripture wording, Church policy, historical detail, source URL, prophetic statement, or certainty you do not have.',
            '- If reference notes are supplied, use them as study notes, not as unquestionable authority. Correct or soften a note if it appears inconsistent or overconfident.',
            '- When you are uncertain, say so briefly and point the visitor toward scripture or official Church study resources rather than guessing.',
            '- Do not claim focusChrist is an official Church property or that the Church endorses the answer.',
            '',
            'PASTORAL AND SAFETY DISCIPLINE:',
            '- Do not tell a visitor that a private feeling definitely came from God or that you know God has commanded a specific personal action.',
            '- For serious medical, mental-health, abuse, legal, financial, or emergency matters, spiritual encouragement may accompany but must not replace qualified help.',
            '- If a request is unsafe, exploitative, illegal, or inappropriate, decline that part briefly and redirect to safe guidance.',
            '',
            'RESPONSE SHAPE:',
            '1. Direct answer.',
            '2. Helpful explanation, scripture/historical context, or distinctions as needed.',
            '3. A natural next study thought only when it adds value.',
            'End with a complete sentence.'
        ].join('\n');

        if (referenceContent) {
            prompt += '\n\nREFERENCE NOTES FROM THE LOCAL STUDY LIBRARY:\n' + referenceContent;
        }
        return prompt;
    }

    function buildMessages(query, referenceContent, mode) {
        const messages = [{ role: 'system', content: systemPrompt(mode, referenceContent) }];
        currentHistory().forEach(function (message) {
            if (!message || !message.role || !message.content) return;
            messages.push({ role: message.role, content: String(message.content) });
        });
        messages.push({ role: 'user', content: query });
        return messages;
    }

    async function requestOnce(messages, timeoutMs) {
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timer = controller ? window.setTimeout(function () { controller.abort(); }, timeoutMs) : null;
        try {
            const response = await fetch(PROXY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: MODEL,
                    messages: messages,
                    temperature: 0.45,
                    max_tokens: MAX_OUTPUT_TOKENS
                }),
                signal: controller ? controller.signal : undefined
            });
            if (!response.ok) throw new Error('Study service returned ' + response.status);
            const data = await response.json();
            if (!data || !data.choices || !data.choices[0] || !data.choices[0].message) {
                throw new Error('Study service returned an incomplete response');
            }
            return String(data.choices[0].message.content || '').trim();
        } finally {
            if (timer) window.clearTimeout(timer);
        }
    }

    async function askEnhanced(query, referenceContent, sources) {
        const mode = pageMode();
        const messages = buildMessages(query, referenceContent, mode);
        let lastError = null;

        for (const timeout of [FIRST_TIMEOUT_MS, RETRY_TIMEOUT_MS]) {
            try {
                let answer = await requestOnce(messages, timeout);
                if (typeof window.truncateToCompleteSentence === 'function') {
                    answer = window.truncateToCompleteSentence(answer);
                } else if (typeof truncateToCompleteSentence === 'function') {
                    answer = truncateToCompleteSentence(answer);
                }
                if (!answer) throw new Error('Empty study response');
                rememberExchange(query, answer);
                return { answer: answer, sources: Array.isArray(sources) ? sources : [] };
            } catch (error) {
                lastError = error;
                console.warn('focusChrist Study Intelligence attempt failed:', error && error.message ? error.message : error);
            }
        }

        console.error('focusChrist Study Intelligence failed after retry:', lastError);
        return {
            answer: 'I could not complete that study response just now. Please try the question again, or continue through the related study and official Church resources on this page.',
            sources: []
        };
    }

    function referenceFromMatch(match) {
        if (!match || !match.found) return '';
        const sourceText = (match.sources || []).map(function (source) {
            return (source.text || 'Source') + (source.url ? ' (' + source.url + ')' : '');
        }).join('; ');
        return 'LOCAL STUDY NOTE:\n' + match.answer + (sourceText ? '\nLINKED SOURCES:\n' + sourceText : '');
    }

    function removeInitialWelcome(box) {
        if (!box) return;
        box.querySelectorAll('.welcome, .ask-welcome').forEach(function (welcome) { welcome.remove(); });
    }

    function setBusy(busy) {
        const button = document.getElementById('sendBtn');
        const input = document.getElementById('userInput');
        if (button) {
            button.disabled = Boolean(busy);
            button.textContent = busy ? 'Studying…' : 'Ask';
        }
        if (input) input.disabled = Boolean(busy);
    }

    function loadingMessage(mode) {
        const loading = document.createElement('div');
        loading.className = 'loading';
        loading.setAttribute('role', 'status');
        loading.textContent = mode === 'pioneers'
            ? 'Reviewing pioneer history and study context…'
            : 'Studying the question and available sources…';
        return loading;
    }

    function cleanMarkdownArtifacts(text) {
        return String(text || '').replace(/\*\*(.*?)\*\*/g, '$1').replace(/^#{1,6}\s+/gm, '');
    }

    function appendAnswerText(message, rawText) {
        const text = cleanMarkdownArtifacts(rawText);
        const blocks = text.split(/\n{2,}/).map(function (item) { return item.trim(); }).filter(Boolean);
        (blocks.length ? blocks : [text]).forEach(function (block) {
            const lines = block.split('\n').map(function (item) { return item.trim(); }).filter(Boolean);
            const listLines = lines.filter(function (line) { return /^[-•]\s+/.test(line) || /^\d+[.)]\s+/.test(line); });
            if (listLines.length === lines.length && lines.length > 1) {
                const list = document.createElement('ul');
                list.className = 'fc-study-answer-list';
                lines.forEach(function (line) {
                    const li = document.createElement('li');
                    li.textContent = line.replace(/^[-•]\s+/, '').replace(/^\d+[.)]\s+/, '');
                    list.appendChild(li);
                });
                message.appendChild(list);
            } else {
                const paragraph = document.createElement('p');
                paragraph.textContent = lines.join(' ');
                message.appendChild(paragraph);
            }
        });
    }

    function safeHref(value) {
        try {
            const url = new URL(value, window.location.href);
            if (url.protocol === 'http:' || url.protocol === 'https:') return url.href;
        } catch (_error) {}
        return null;
    }

    function installSafeMessageRenderer() {
        window.addMessage = function (text, isUser, sources) {
            const box = document.getElementById('chatBox');
            if (!box) return null;
            const message = document.createElement('div');
            message.className = 'message ' + (isUser ? 'user-message' : 'bot-message');

            if (isUser) {
                const p = document.createElement('p');
                const label = document.createElement('strong');
                label.textContent = 'You asked: ';
                p.appendChild(label);
                p.appendChild(document.createTextNode(String(text || '')));
                message.appendChild(p);
            } else {
                appendAnswerText(message, text);
            }

            const validSources = (Array.isArray(sources) ? sources : []).filter(function (source) {
                return source && safeHref(source.url);
            });
            if (!isUser && validSources.length) {
                const wrap = document.createElement('div');
                wrap.className = 'sources';
                const title = document.createElement('div');
                title.className = 'sources-title';
                title.textContent = 'Study sources';
                wrap.appendChild(title);
                validSources.forEach(function (source) {
                    const link = document.createElement('a');
                    link.className = 'source-link';
                    link.href = safeHref(source.url);
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = String(source.text || 'Source').replace(/^[^A-Za-z0-9]+/, '');
                    wrap.appendChild(link);
                });
                message.appendChild(wrap);
            }

            box.appendChild(message);
            return message;
        };
    }

    async function sendAskMessage() {
        const input = document.getElementById('userInput');
        const box = document.getElementById('chatBox');
        if (!input || !box) return;
        const question = input.value.trim();
        if (!question) return;

        removeInitialWelcome(box);
        window.addMessage(question, true, []);
        input.value = '';
        setBusy(true);
        const loading = loadingMessage('ask');
        box.appendChild(loading);
        box.scrollTop = box.scrollHeight;

        try {
            if (typeof window.containsInappropriate === 'function' && window.containsInappropriate(question)) {
                loading.remove();
                window.addMessage('I can help with respectful questions about Jesus Christ, scripture, faith, and Latter-day Saint belief. Please rephrase the question in that direction.', false, []);
                return;
            }

            const match = enhancedLocalMatch(question);
            const result = await askEnhanced(question, referenceFromMatch(match), match.found ? match.sources : []);
            if (loading.isConnected) loading.remove();
            window.addMessage(result.answer, false, result.sources);
        } catch (error) {
            console.error('Ask conversation error:', error);
            if (loading.isConnected) loading.remove();
            window.addMessage('I could not complete that response just now. Please try again.', false, []);
        } finally {
            setBusy(false);
            input.focus({ preventScroll: true });
        }
    }

    function installAskConversation() {
        installSafeMessageRenderer();
        window.focusChristStudyAsk = askEnhanced;
        window.askAI = function (query, contextEntries) {
            return askEnhanced(query, contextEntries || '', []);
        };
        window.sendMessage = sendAskMessage;
    }

    function installPioneerIntelligence() {
        // Pioneer Experience already owns its excellent visible conversation
        // mechanics. Upgrade the underlying AI synthesis/retry layer without
        // duplicating those interaction controls.
        window.focusChristStudyAsk = askEnhanced;
        window.askAI = function (query, contextEntries) {
            const local = enhancedLocalMatch(query);
            const reference = contextEntries || referenceFromMatch(local);
            return askEnhanced(query, reference, local.found ? local.sources : []);
        };
    }

    function addStudyIntelligenceStyles() {
        if (document.getElementById('focuschrist-study-intelligence-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-study-intelligence-styles';
        style.textContent = `
            .fc-study-answer-list { margin: 10px 0 10px 1.25rem; color: #d9cbbb; line-height: 1.65; }
            .fc-study-answer-list li { margin: 6px 0; padding-left: 3px; }
            .bot-message .sources-title { text-transform: uppercase; letter-spacing: 1.2px; }
        `;
        document.head.appendChild(style);
    }

    function init() {
        const mode = pageMode();
        if (mode !== 'ask' && mode !== 'pioneers') return;
        addStudyIntelligenceStyles();
        if (mode === 'pioneers') installPioneerIntelligence();
        else installAskConversation();
        document.documentElement.setAttribute('data-focuschrist-study-intelligence', 'active');
    }

    init();
})();
