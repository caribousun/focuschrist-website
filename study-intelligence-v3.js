/* focusChrist Study Intelligence v3
 * Hardened response hygiene + broader LDS intent + verified core grounding.
 * Loaded after v2 and owns the final Ask/Pioneer AI functions when ready.
 */
(function () {
    'use strict';

    const PROXY_URL = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
    const MODEL = 'openai/gpt-oss-20b';
    const MAX_TOKENS = 1500;
    const POLICY_VERSION = '2026-08-31.4';

    const FAITH_TERMS = new Set([
        'jesus','christ','savior','redeemer','god','heavenly','father','holy','ghost','spirit','scripture','scriptures','bible','biblical',
        'book','mormon','nephi','alma','mosiah','moroni','ether','helaman','doctrine','covenants','pearl','great','price','temple','temples',
        'prophet','prophets','apostle','apostles','church','latter-day','saint','saints','lds','atonement','resurrection','revelation','prayer',
        'pray','faith','repentance','baptism','ordinance','ordinances','priesthood','gospel','testimony','commandment','commandments','conference',
        'restoration','joseph','smith','cowdery','oliver','emma','brigham','young','nelson','monson','hinckley','ward','stake','bishop','relief',
        'society','quorum','elder','elders','seventy','missionary','missionaries','mission','sacrament','tithing','garment','garments','endowment',
        'sealing','sealings','celestial','terrestrial','telestial','exaltation','salvation','premortal','premortality','preexistence','spirit-world',
        'patriarch','patriarchal','blessing','anointing','keys','dispensation','zion','conference','modesty','fasting','fast','ministering','calling',
        'callings','genealogy','familysearch','family','eternal','plural','polygamy','marriage','first','vision','kirtland','nauvoo','pioneer','pioneers'
    ]);

    const HIGH_STAKES_TERMS = new Set([
        'suicide','suicidal','kill','dying','abuse','abused','violence','violent','emergency','diagnosis','medication','medicine','legal','lawyer',
        'court','crime','debt','bankruptcy','overdose','self-harm','selfharm'
    ]);

    const VERIFIED_CONTEXTS = [
        {
            terms: ['restoration','first vision','priesthood','joseph smith'],
            text: [
                'VERIFIED CORE RESTORATION FACTS:',
                '- In the spring of 1820, Joseph Smith said he prayed to know which church he should join and for forgiveness of sins; he reported that God the Father and Jesus Christ appeared to him. Do not say he asked why he had not been chosen as a prophet.',
                '- On May 15, 1829, John the Baptist conferred the Aaronic Priesthood on Joseph Smith and Oliver Cowdery.',
                '- Peter, James, and John later conferred the Melchizedek Priesthood on Joseph Smith and Oliver Cowdery.',
                '- Do not identify the Three Witnesses, the Two Witnesses, or Moroni as the messengers who restored the Aaronic or Melchizedek Priesthood.',
                '- The Church was organized on April 6, 1830, in Fayette, New York.',
                'Official anchors: First Vision topic; Restoration of the Priesthood topic; Restoration of the Church topic on ChurchofJesusChrist.org.'
            ].join('\n')
        },
        {
            terms: ['book of mormon','nephi','alma','moroni','mosiah','ether','helaman'],
            text: [
                'VERIFIED CORE BOOK OF MORMON FRAME:',
                '- Latter-day Saints regard the Book of Mormon as scripture and another testament of Jesus Christ, used together with the Bible.',
                '- Joseph Smith said he translated the record by the gift and power of God from plates delivered by the angel Moroni.',
                '- Avoid inventing quotations, archaeology claims, translation mechanics, or official positions not supplied by a reliable source.'
            ].join('\n')
        },
        {
            terms: ['temple','endowment','sealing','garment','garments'],
            text: [
                'VERIFIED CORE TEMPLE FRAME:',
                '- Latter-day Saint temples are houses of the Lord used for sacred ordinances and covenants, including endowment and sealing ordinances.',
                '- Temple garments are connected with temple covenants. Discuss them respectfully and avoid sensationalism or unsupported symbolism.',
                '- Distinguish public Church teaching from details Latter-day Saints consider sacred.'
            ].join('\n')
        },
        {
            terms: ['celestial','terrestrial','telestial','premortal','premortality','spirit world','after death','plan of salvation','exaltation'],
            text: [
                'VERIFIED CORE PLAN OF SALVATION FRAME:',
                '- Latter-day Saint teaching includes premortal life, mortal life, the spirit world after death, resurrection through Jesus Christ, judgment, and degrees of glory.',
                '- Salvation from physical death comes through the Resurrection of Jesus Christ; exaltation is associated with receiving the fulness of God’s blessings through Christ and covenant faithfulness.',
                '- Avoid claiming a private person’s eternal destination.'
            ].join('\n')
        },
        {
            terms: ['ward','stake','bishop','relief society','quorum','calling','callings'],
            text: [
                'VERIFIED CORE CHURCH ORGANIZATION FRAME:',
                '- A ward is a local congregation; a stake is a group of wards or branches in a geographic area.',
                '- Bishops preside over wards. Relief Society is the Church organization for adult women. Priesthood quorums organize priesthood holders for service and ministry.',
                '- Local callings are generally lay service assignments rather than paid clergy positions.'
            ].join('\n')
        },
        {
            terms: ['baptism','sacrament','confirmation','holy ghost'],
            text: [
                'VERIFIED CORE ORDINANCE FRAME:',
                '- Latter-day Saints teach faith in Jesus Christ, repentance, baptism by immersion by proper priesthood authority, and confirmation to receive the gift of the Holy Ghost.',
                '- The sacrament is a weekly ordinance using bread and water to remember Jesus Christ and renew covenant commitment.'
            ].join('\n')
        }
    ];

    function normalize(text) {
        return String(text || '').toLowerCase().replace(/[^a-z0-9\s'-]/g, ' ').replace(/\s+/g, ' ').trim();
    }

    function words(text) {
        return normalize(text).split(' ').filter(Boolean);
    }

    function phraseMatch(query, phrase) {
        return normalize(query).includes(normalize(phrase));
    }

    function currentMode() {
        return window.location.pathname.toLowerCase().endsWith('/pioneers.html') ? 'pioneers' : 'ask';
    }

    function classifyQuestion(query) {
        const tokens = words(query);
        if (tokens.some(function (word) { return HIGH_STAKES_TERMS.has(word); })) return 'high-stakes';
        if (currentMode() === 'pioneers') return 'pioneer-study';
        if (tokens.some(function (word) { return FAITH_TERMS.has(word); })) return 'faith-study';
        if (['church of jesus christ','latter day saints','first vision','plan of salvation','word of wisdom','relief society','book of mormon'].some(function (phrase) { return phraseMatch(query, phrase); })) return 'faith-study';
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
            if (score > bestScore) { bestScore = score; bestKey = key; }
        });
        if (!bestKey || bestScore < 42) return { found: false, answer: '', sources: [], score: bestScore };
        const item = qaDatabase[bestKey] || {};
        return {
            found: true,
            key: bestKey,
            score: bestScore,
            answer: String(item.answer || ''),
            sources: Array.isArray(item.sources) ? item.sources : [],
            verified: item.verified === true
        };
    }

    function verifiedContextFor(query) {
        const q = normalize(query);
        const matches = VERIFIED_CONTEXTS.filter(function (entry) {
            return entry.terms.some(function (term) { return q.includes(normalize(term)); });
        });
        return matches.map(function (entry) { return entry.text; }).join('\n\n');
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
                '- Answer the ordinary factual or practical question completely in normal terms first.',
                '- Do NOT append a blessing, devotional phrase, testimony statement, or generic sentence about the love or peace of Jesus Christ.',
                '- Do NOT force religion into the factual answer.',
                '- After the factual answer, if there is a genuinely natural and accurate connection, you MAY add one short optional study bridge.',
                '- Example: after explaining why the sky is blue, offer to explore how the heavens, light, or color imagery are used in scripture if the visitor wants that connection.',
                '- If no meaningful faith connection is apparent, simply invite a follow-up. Do not manufacture a spiritual analogy.'
            ].join('\n');
        }
        if (profile === 'faith-study') {
            return [
                'QUESTION MODE: FAITH / SCRIPTURE STUDY.',
                '- Answer from a Latter-day Saint perspective and distinguish scripture, official Church teaching, history, interpretation, and application.',
                '- Prefer the verified core context and curated local notes supplied below over model memory when they overlap.',
                '- If a precise historical name, messenger, date, quotation, or sequence is not grounded in supplied context and you are uncertain, say so instead of guessing.',
                '- Never substitute similar Church-history figures for the actual people involved in an event.',
                '- Jesus Christ may be central when the subject calls for it, but do not append canned devotional language.',
                '- The page will provide verified Church/BYU study links after the answer; do not invent URLs.'
            ].join('\n');
        }
        if (profile === 'pioneer-study') {
            return [
                'QUESTION MODE: LATTER-DAY SAINT PIONEER / CHURCH HISTORY STUDY.',
                '- Answer the historical question first and distinguish established fact from tradition, recollection, inference, and disputed claims.',
                '- Do not romanticize suffering or manufacture miracles, dates, quotations, or participants.',
                '- The page will provide verified study links after the answer; do not invent URLs.'
            ].join('\n');
        }
        return [
            'QUESTION MODE: HIGH-STAKES OR SENSITIVE.',
            '- Answer cautiously and directly.',
            '- Do not present spiritual counsel as a substitute for qualified medical, mental-health, legal, financial, emergency, or safety help.',
            '- Do not claim God has revealed a private diagnosis, command, or guaranteed outcome.'
        ].join('\n');
    }

    function systemPrompt(profile, localReference, verifiedContext, additionalReference) {
        let prompt = [
            'You are the conversational study assistant for focusChrist, an independent Latter-day Saint faith-based website.',
            'You may answer a very broad range of lawful user questions. The site is Christ-centered, but that does not require attaching religious language to every answer.',
            '',
            'CORE INTELLIGENCE RULES:',
            '- Identify what the visitor actually asked and answer that first.',
            '- Adapt depth to the question. Simple facts can be brief; nuanced questions deserve context.',
            '- Preserve conversational context for follow-up questions.',
            '- Never begin with filler such as "Great question."',
            '- Never end an ordinary answer with generic phrases such as "May the love of Jesus Christ bring you peace," "God bless you," or equivalent boilerplate.',
            '- If a question can lead naturally into Christ-centered study, make that connection optional and specific.',
            '',
            modeInstructions(profile),
            '',
            'TRUTH / SOURCE DISCIPLINE:',
            '- Never invent scripture wording, quotations, Church teachings, historical details, people, messenger identities, dates, URLs, statistics, or certainty.',
            '- If verified context conflicts with model memory, follow verified context.',
            '- If unsure, state the uncertainty briefly instead of bluffing.',
            '- focusChrist is independent and must never be described as an official Church property or endorsed Church answer.',
            '',
            'DISPLAY / FORMAT DISCIPLINE:',
            '- Write clean plain text for a safe DOM renderer.',
            '- Do not use Markdown tables or pipe-table syntax. Use short paragraphs or simple hyphen bullets instead.',
            '- Use normal spaces and ordinary hyphens. Avoid non-breaking spaces, non-breaking hyphens, narrow no-break spaces, decorative Unicode punctuation, and formatting artifacts.',
            '- Prefer short readable paragraphs and brief lists only when useful.',
            '- End with a complete sentence.'
        ].join('\n');

        if (verifiedContext) prompt += '\n\nVERIFIED CORE CONTEXT:\n' + verifiedContext;
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

    function buildMessages(query, profile, localReference, verifiedContext, additionalReference) {
        const messages = [{ role: 'system', content: systemPrompt(profile, localReference, verifiedContext, additionalReference) }];
        recentHistory().forEach(function (item) { messages.push({ role: item.role, content: String(item.content) }); });
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
                body: JSON.stringify({ model: MODEL, messages: messages, temperature: 0.25, max_tokens: MAX_TOKENS }),
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

    function convertMarkdownTables(text) {
        const lines = String(text || '').split('\n');
        const output = [];
        let i = 0;
        while (i < lines.length) {
            const line = lines[i].trim();
            const next = i + 1 < lines.length ? lines[i + 1].trim() : '';
            if (line.includes('|') && /^\|?\s*:?-{3,}/.test(next.replace(/\s+/g, ''))) {
                const headers = line.split('|').map(function (cell) { return cell.trim(); }).filter(Boolean);
                i += 2;
                while (i < lines.length && lines[i].includes('|')) {
                    const cells = lines[i].split('|').map(function (cell) { return cell.trim(); }).filter(Boolean);
                    if (cells.length) {
                        output.push('- ' + (cells[0] || 'Item'));
                        for (let c = 1; c < cells.length; c += 1) {
                            output.push('  ' + (headers[c] || 'Detail') + ': ' + cells[c]);
                        }
                    }
                    i += 1;
                }
                continue;
            }
            output.push(lines[i]);
            i += 1;
        }
        return output.join('\n');
    }

    function normalizeDisplayText(answer) {
        let text = convertMarkdownTables(answer);
        text = text
            .replace(/[\u00A0\u2007\u202F]/g, ' ')
            .replace(/[\u2010\u2011\u2012\u2013\u2014\u2212]/g, '-')
            .replace(/[\u2018\u2019]/g, "'")
            .replace(/[\u201C\u201D]/g, '"')
            .replace(/\u2026/g, '...')
            .replace(/^\s*:\s*/, '')
            .replace(/[ \t]+\n/g, '\n')
            .replace(/[ \t]{2,}/g, ' ')
            .replace(/\n{3,}/g, '\n\n')
            .trim();
        return text;
    }

    async function askV3(query, additionalReference) {
        const profile = classifyQuestion(query);
        const localReference = bestLocalReference(query);
        const verifiedContext = profile === 'faith-study' || profile === 'pioneer-study' ? verifiedContextFor(query) : '';

        // Curated entries marked verified have been checked against their linked
        // official sources. Serve them unchanged; model rewriting can reintroduce
        // citations or claims that the source text does not contain.
        if (localReference.found && localReference.verified) {
            remember(query, localReference.answer);
            return {
                answer: localReference.answer,
                sources: localReference.sources,
                profile: profile,
                localMatch: localReference.key,
                verifiedGrounding: true
            };
        }

        const messages = buildMessages(query, profile, localReference, verifiedContext, additionalReference || '');
        let lastError = null;

        for (const timeout of [25000, 18000]) {
            try {
                let answer = await request(messages, timeout);
                answer = removeBoilerplateClosing(answer, profile);
                answer = normalizeDisplayText(answer);
                if (/red,?\s+white,?\s+and\s+black\s+lights?|["']?(?:red|black|golden)\s+light["']?.{0,180}(?:D&C|Doctrine and Covenants)\s+76/i.test(answer)) {
                    throw new Error('Blocked known false Doctrine and Covenants color claim');
                }
                if (!answer) throw new Error('Response removed as empty');
                remember(query, answer);
                return {
                    answer: answer,
                    sources: localReference.found ? localReference.sources : [],
                    profile: profile,
                    localMatch: localReference.found ? localReference.key : null,
                    verifiedGrounding: Boolean(verifiedContext)
                };
            } catch (error) {
                lastError = error;
                console.warn('focusChrist Study Intelligence v3 attempt failed:', error && error.message ? error.message : error);
            }
        }

        console.error('focusChrist Study Intelligence v3 failed:', lastError);
        return {
            answer: 'I could not complete that answer just now. Please try again, rephrase the question, or use the verified study links shown with the conversation.',
            sources: [],
            profile: profile,
            localMatch: null,
            verifiedGrounding: false
        };
    }

    function loadingNode() {
        const node = document.createElement('div');
        node.className = 'loading';
        node.setAttribute('role', 'status');
        node.textContent = 'Thinking through your question...';
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
            button.textContent = 'Thinking...';
            const loading = loadingNode();
            box.appendChild(loading);
            box.scrollTop = box.scrollHeight;

            try {
                if (typeof window.containsInappropriate === 'function' && window.containsInappropriate(question)) {
                    loading.remove();
                    window.addMessage('I can help with respectful and safe questions. Please rephrase the request in a way I can assist with.', false, []);
                    return;
                }
                const result = await askV3(question, '');
                if (loading.isConnected) loading.remove();
                window.addMessage(result.answer, false, result.sources);
            } catch (error) {
                console.error('focusChrist Ask v3 error:', error);
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

    function installWhenReady(attempt) {
        if (typeof window.focusChristStudyAskV2 !== 'function' && attempt < 30) {
            window.setTimeout(function () { installWhenReady(attempt + 1); }, 100);
            return;
        }
        window.focusChristStudyAskV3 = askV3;
        window.askAI = function (query, contextEntries) { return askV3(query, contextEntries || ''); };
        if (currentMode() === 'ask') installAskSendMessage();
        document.documentElement.setAttribute('data-focuschrist-study-intelligence-version', '3');
        console.info('focusChrist Study Intelligence policy ' + POLICY_VERSION + ' active.');
    }

    installWhenReady(0);
})();
