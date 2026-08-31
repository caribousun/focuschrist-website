/* focusChrist Pioneer conversation experience.
 * Page-specific historical context hardening for Journey, Trail, Pioneer Topics,
 * Tell My Story, and free-form pioneer questions.
 */
(function () {
    'use strict';

    const PROXY_URL = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
    const MODEL = 'openai/gpt-oss-20b';
    const PIONEER_POLICY_VERSION = '2026-08-31.5';

    const PIONEER_PAGE_CONTEXT = [
        'PIONEER PAGE HARD CONTEXT:',
        '- This page is about 19th-century Latter-day Saint pioneer and related Church history.',
        '- UI-generated prompts from The Journey, The Trail, Willie & Martin Companies, and Pioneer Topics MUST be interpreted in Latter-day Saint pioneer context.',
        '- Ambiguous historical words on this page default to pioneer meaning unless the visitor explicitly asks for a different meaning.',
        '- In particular, "Exodus from Nauvoo" means the 1846 departure and westward migration of Latter-day Saints from Nauvoo, Illinois, across Iowa toward the Missouri River/Winter Quarters. It does NOT mean the biblical Book of Exodus.',
        '- Official Church history records that the first wagons left Nauvoo on February 4, 1846; thousands departed between February and September 1846; the difficult Iowa crossing led to the establishment of Winter Quarters; and the 1847 pioneer company later continued west toward the Salt Lake Valley.',
        '- Terms such as Nauvoo, Winter Quarters, Mormon Battalion, Mormon Trail, handcart company, Willie Company, Martin Company, rescue, Sweetwater, Martins Cove, Brigham Young, Salt Lake Valley, and pioneer exodus belong to this historical frame unless the visitor clearly says otherwise.'
    ].join('\n');

    const EXPLICIT_NON_PIONEER_RE = /\b(?:bible|biblical|old testament|book of exodus|moses|egypt|egyptian|israelites|ancient israel|sinai|pharaoh)\b/i;

    function chatBox() { return document.getElementById('chatBox'); }
    function userInput() { return document.getElementById('userInput'); }
    function sendButton() { return document.getElementById('sendBtn'); }
    function composerLabel() { return document.getElementById('pioneerComposerLabel'); }

    function appendTextParagraph(parent, text) {
        const p = document.createElement('p');
        p.textContent = text;
        parent.appendChild(p);
    }

    function safeSourceHref(value) {
        try {
            const url = new URL(value, window.location.href);
            if (url.protocol === 'http:' || url.protocol === 'https:' || url.origin === window.location.origin) return url.href;
        } catch (_error) {}
        return '#';
    }

    window.addMessage = function (text, isUser, sources = [], extraBtn = null) {
        const box = chatBox();
        if (!box) return null;

        const message = document.createElement('div');
        message.className = 'message ' + (isUser ? 'user-message' : 'bot-message');

        let rawText = String(text || '');
        if (!rawText.includes('\n') && rawText.length > 100) rawText = rawText.replace(/([.!?])\s+/g, '$1\n');
        const paragraphs = rawText.split('\n').map(function (item) { return item.trim(); }).filter(Boolean);

        if (isUser) {
            const p = document.createElement('p');
            const strong = document.createElement('strong');
            strong.textContent = 'You asked: ';
            p.appendChild(strong);
            p.appendChild(document.createTextNode(paragraphs[0] || rawText));
            message.appendChild(p);
        } else {
            (paragraphs.length ? paragraphs : [rawText]).forEach(function (paragraph) { appendTextParagraph(message, paragraph); });
        }

        if (!isUser && Array.isArray(sources) && sources.length) {
            const sourceWrap = document.createElement('div');
            sourceWrap.className = 'sources';
            const title = document.createElement('div');
            title.className = 'sources-title';
            title.textContent = 'Sources';
            sourceWrap.appendChild(title);
            sources.forEach(function (source) {
                const link = document.createElement('a');
                link.className = 'source-link';
                link.href = safeSourceHref(source.url || '#');
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.textContent = source.text || 'Source';
                sourceWrap.appendChild(link);
            });
            message.appendChild(sourceWrap);
        }

        if (!isUser && extraBtn && extraBtn.text) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'pioneer-extra-action';
            button.textContent = extraBtn.text;
            if (extraBtn.action === 'askTellMyStory()' && typeof window.askTellMyStory === 'function') {
                button.addEventListener('click', function () { window.askTellMyStory(); });
            }
            message.appendChild(button);
        }

        box.appendChild(message);
        return message;
    };

    function recentHistory() {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return [];
        return conversationHistory.slice(-10).filter(function (item) {
            return item && (item.role === 'user' || item.role === 'assistant') && item.content;
        });
    }

    function rememberExchange(question, answer) {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return;
        conversationHistory.push({ role: 'user', content: question });
        conversationHistory.push({ role: 'assistant', content: String(answer || '') });
        while (conversationHistory.length > 20) conversationHistory.shift();
        try { sessionStorage.setItem('focuschrist_history', JSON.stringify(conversationHistory)); } catch (_error) {}
    }

    function normalizeDisplayText(text) {
        return String(text || '')
            .replace(/[\u00A0\u2007\u202F]/g, ' ')
            .replace(/[\u2010\u2011\u2012\u2013\u2014\u2212]/g, '-')
            .replace(/[\u2018\u2019]/g, "'")
            .replace(/[\u201C\u201D]/g, '"')
            .replace(/\u2026/g, '...')
            .replace(/[ \t]+\n/g, '\n')
            .replace(/[ \t]{2,}/g, ' ')
            .replace(/\n{3,}/g, '\n\n')
            .trim();
    }

    function buildSystemPrompt(question, pageReference) {
        const explicitOtherContext = EXPLICIT_NON_PIONEER_RE.test(question);
        return [
            'You are the historical study assistant on the focusChrist Pioneers page.',
            PIONEER_PAGE_CONTEXT,
            '',
            explicitOtherContext
                ? 'The visitor has explicitly signaled a biblical or non-pioneer context. Answer that explicit request directly, while not confusing it with the Pioneer-page default.'
                : 'No explicit non-pioneer context was requested. Stay inside the Latter-day Saint pioneer/history frame.',
            '',
            'HISTORICAL DISCIPLINE:',
            '- Answer the exact historical topic first.',
            '- Never switch an ambiguous Pioneer-page label to an unrelated biblical, general-history, or modern topic merely because a keyword overlaps.',
            '- Distinguish well-established fact from recollection, tradition, inference, disputed interpretation, or devotional retelling.',
            '- Never invent dates, people, quotations, journal language, miracles, statistics, source titles, URLs, or certainty.',
            '- If a precise detail is not grounded by the page context supplied here and you are not confident, state that limitation briefly instead of guessing.',
            '- Do not romanticize suffering. Do not manufacture providential claims or miracles.',
            '- Do not portray focusChrist as an official Church website.',
            '- Do not invent source URLs. The page provides verified source-routing separately.',
            '',
            'FAITH AND TONE:',
            '- Explain faith when it is genuinely part of the historical record or the visitor asks about it.',
            '- Do not append a canned testimony, blessing, or forced devotional closing.',
            '- Be respectful, concise, readable, and historically focused.',
            '- Use plain text, short paragraphs, and simple hyphen bullets only when useful.',
            '- End with a complete sentence.',
            pageReference ? '\nPAGE-SUPPLIED CONTEXT FOR THIS INTERACTION:\n' + pageReference : ''
        ].filter(Boolean).join('\n');
    }

    async function requestPioneerAI(question, pageReference) {
        // Source-dependent pioneer answers remain blocked. Until the runtime can
        // retrieve and compare actual authoritative source text, fail closed and
        // let the page's official study routes carry the visitor forward.
        const fallback = window.focusChristSourceIntegrity
            ? window.focusChristSourceIntegrity.fallback
            : 'I cannot verify the source claim well enough to present it as authoritative.';
        rememberExchange(question, fallback);
        return {
            answer: fallback,
            sources: [],
            pioneerContext: true,
            sourceIntegrityPassed: false,
            sourceIntegrityStatus: 'unreviewed-source-dependent-generation-blocked'
        };

        /* istanbul ignore next -- retained for a future source-excerpt pipeline */
        const messages = [{ role: 'system', content: buildSystemPrompt(question, pageReference || '') }];
        recentHistory().forEach(function (item) { messages.push({ role: item.role, content: String(item.content) }); });
        messages.push({ role: 'user', content: question });

        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timer = controller ? window.setTimeout(function () { controller.abort(); }, 25000) : null;
        try {
            const response = await fetch(PROXY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: MODEL, messages: messages, temperature: 0.2, max_tokens: 1200 }),
                signal: controller ? controller.signal : undefined
            });
            if (!response.ok) throw new Error('Pioneer study service returned ' + response.status);
            const data = await response.json();
            const raw = data && data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : '';
            let answer = normalizeDisplayText(raw);
            if (!answer) throw new Error('Empty Pioneer study response');
            const integrity = window.focusChristSourceIntegrity && typeof window.focusChristSourceIntegrity.guardGeneratedAnswer === 'function'
                ? window.focusChristSourceIntegrity.guardGeneratedAnswer(answer, {
                    trustedReferenceText: '',
                    requireTrustedScripture: true,
                    sourceDependent: true
                })
                : { ok: false, answer: 'I cannot verify the source claim well enough to present it as authoritative.' };
            answer = integrity.answer;
            rememberExchange(question, answer);
            return { answer: answer, sources: [], pioneerContext: true, sourceIntegrityPassed: integrity.ok };
        } finally {
            if (timer) window.clearTimeout(timer);
        }
    }

    window.focusChristPioneerAskAI = requestPioneerAI;

    function setConversationMode(active) {
        const label = composerLabel();
        const input = userInput();
        if (label) label.textContent = active ? 'Continue the conversation' : 'Ask a pioneer question';
        if (input) input.placeholder = active ? 'Ask a follow-up question...' : 'Ask a sincere pioneer question...';
        document.body.classList.toggle('pioneer-conversation-active', !!active);
    }

    function preferredScrollBehavior() {
        return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
    }

    function fixedHeaderOffset() {
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        if (!header) return 20;
        const style = window.getComputedStyle(header);
        if (style.position !== 'fixed') return 20;
        return Math.ceil(header.getBoundingClientRect().height) + 24;
    }

    function scrollPageToElement(element) {
        if (!element) return;
        const top = element.getBoundingClientRect().top + window.scrollY - fixedHeaderOffset();
        window.scrollTo({ top: Math.max(0, top), behavior: preferredScrollBehavior() });
    }

    function ensurePioneerEntryStyles() {
        if (document.getElementById('pioneer-entry-styles')) return;
        const style = document.createElement('style');
        style.id = 'pioneer-entry-styles';
        style.textContent = `
            html[data-focuschrist-pioneer-entry-active] body.fc-site .qa-container {
                border-color: rgba(240,195,106,.68);
                box-shadow: var(--fc-shadow), 0 0 0 3px rgba(240,195,106,.10);
            }
        `;
        document.head.appendChild(style);
    }

    function focusPioneerComposer(updateHash) {
        const section = document.querySelector('.qa-section');
        const container = document.querySelector('.qa-container');
        const input = userInput();
        if (!section || !container || !input) return;

        section.id = 'ask-pioneers';
        document.documentElement.setAttribute('data-focuschrist-pioneer-entry-active', 'true');
        scrollPageToElement(container);

        window.setTimeout(function () {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }, 260);

        if (updateHash && window.history && typeof window.history.replaceState === 'function') {
            window.history.replaceState(null, '', '#ask-pioneers');
        }
    }

    function initTopPioneerAskEntry() {
        const section = document.querySelector('.qa-section');
        const intro = document.querySelector('.fc-page-intro .fc-container--standard');
        const input = userInput();
        if (!section || !intro || !input) return;

        ensurePioneerEntryStyles();
        section.id = 'ask-pioneers';

        if (!intro.querySelector('[data-focuschrist-top-pioneer-ask-cta]')) {
            const actions = document.createElement('div');
            actions.className = 'fc-actions fc-actions--center';
            actions.setAttribute('data-focuschrist-top-pioneer-ask-cta', 'true');

            const link = document.createElement('a');
            link.className = 'fc-button fc-button--primary';
            link.href = '#ask-pioneers';
            link.textContent = 'Ask a Pioneer Question';
            link.addEventListener('click', function (event) {
                event.preventDefault();
                focusPioneerComposer(true);
            });
            actions.appendChild(link);
            intro.appendChild(actions);
        }

        input.addEventListener('focus', function () {
            document.documentElement.setAttribute('data-focuschrist-pioneer-entry-active', 'true');
        });

        window.addEventListener('hashchange', function () {
            if (window.location.hash === '#ask-pioneers') focusPioneerComposer(false);
        });

        if (window.location.hash === '#ask-pioneers') {
            window.setTimeout(function () { focusPioneerComposer(false); }, 90);
        }
    }

    function removeWelcome() {
        const box = chatBox();
        if (!box) return;
        const welcome = box.querySelector('.welcome');
        if (welcome) welcome.remove();
    }

    function showLoading(container) {
        const box = container || chatBox();
        if (!box) return null;
        const loading = document.createElement('div');
        loading.className = 'loading';
        loading.setAttribute('role', 'status');
        loading.textContent = 'Searching pioneer history and study sources...';
        box.appendChild(loading);
        if (box === chatBox()) box.scrollTop = box.scrollHeight;
        return loading;
    }

    function positionAnswer(answerElement) {
        const box = chatBox();
        if (!box || !answerElement) return;
        const internalTop = Math.max(0, answerElement.offsetTop - box.offsetTop - 12);
        box.scrollTo({ top: internalTop, behavior: 'smooth' });
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        const headerHeight = header && getComputedStyle(header).position === 'fixed' ? header.getBoundingClientRect().height : 0;
        const safeTop = headerHeight + 18;
        const rect = box.getBoundingClientRect();
        if (rect.top < safeTop || rect.top > window.innerHeight * 0.72) {
            window.scrollTo({ top: window.scrollY + rect.top - safeTop, behavior: 'smooth' });
        }
    }

    function controlPageReference(control, kind, mappedTopic) {
        if (!control) return kind + ': ' + mappedTopic;
        const date = control.querySelector('.timeline-date, .map-date');
        const title = control.querySelector('.timeline-title, .map-content h4, .map-content h3');
        const desc = control.querySelector('.timeline-desc, .map-content p');
        return [
            kind + ': ' + mappedTopic,
            date && date.textContent.trim() ? 'Displayed date: ' + date.textContent.trim() : '',
            title && title.textContent.trim() ? 'Displayed title: ' + title.textContent.trim() : '',
            desc && desc.textContent.trim() ? 'Displayed description: ' + desc.textContent.trim() : ''
        ].filter(Boolean).join('\n');
    }

    function renderDisclosureAnswer(container, answer) {
        container.innerHTML = '';
        String(answer || '').split('\n').map(function (part) { return part.trim(); }).filter(Boolean).forEach(function (part) {
            const p = document.createElement('p');
            p.textContent = part;
            container.appendChild(p);
        });
        const collapse = document.createElement('button');
        collapse.type = 'button';
        collapse.className = 'pioneer-collapse-action';
        collapse.textContent = 'Collapse';
        collapse.addEventListener('click', function (event) {
            event.stopPropagation();
            container.style.display = 'none';
            const control = container.closest('[data-focus-expand]');
            if (control) {
                control.classList.remove('expanded');
                control.setAttribute('aria-expanded', 'false');
            }
        });
        container.appendChild(collapse);
    }

    async function runDisclosure(control, mappedTopic, kind) {
        const aiResponse = control ? control.querySelector('.ai-response') : null;
        if (!control || !aiResponse) return;

        document.querySelectorAll('[data-focus-expand].expanded').forEach(function (item) {
            if (item !== control) {
                item.classList.remove('expanded');
                item.setAttribute('aria-expanded', 'false');
                const response = item.querySelector('.ai-response');
                if (response) response.style.display = 'none';
            }
        });

        const isExpanding = !control.classList.contains('expanded');
        control.classList.toggle('expanded', isExpanding);
        control.setAttribute('aria-expanded', isExpanding ? 'true' : 'false');
        if (!isExpanding) {
            aiResponse.style.display = 'none';
            return;
        }

        aiResponse.style.display = 'block';
        if (aiResponse.dataset.focuschristLoaded === 'true') return;
        aiResponse.innerHTML = '';
        const loading = showLoading(aiResponse);
        try {
            const pageReference = controlPageReference(control, kind, mappedTopic);
            const query = 'Latter-day Saint pioneer history - ' + kind + ': ' + mappedTopic;
            const result = await requestPioneerAI(query, pageReference);
            if (loading && loading.isConnected) loading.remove();
            renderDisclosureAnswer(aiResponse, result.answer);
            aiResponse.dataset.focuschristLoaded = 'true';
        } catch (error) {
            console.error('Pioneer disclosure error:', error);
            if (loading && loading.isConnected) loading.remove();
            renderDisclosureAnswer(aiResponse, 'I could not complete this pioneer-history answer just now. Please try again or use the verified study resources on this page.');
        }
    }

    function disclosureTopic(control) {
        const key = control ? String(control.getAttribute('data-topic') || '') : '';
        const mode = control ? String(control.getAttribute('data-focus-expand') || '') : '';
        if (mode === 'trail') {
            const mapped = typeof trailTopicMap !== 'undefined' && trailTopicMap[key] ? trailTopicMap[key] : key;
            return { mapped: mapped || 'Pioneer trail', kind: 'Trail' };
        }
        const mapped = typeof topicMap !== 'undefined' && topicMap[key] ? topicMap[key] : key;
        const isHandcart = /^(?:willie|martin)-/i.test(key);
        return { mapped: mapped || 'Pioneer journey', kind: isHandcart ? 'Willie & Martin Companies' : 'Journey' };
    }

    function ownDisclosureEvent(event) {
        if (!event || !event.target || typeof event.target.closest !== 'function') return;
        const control = event.target.closest('[data-focus-expand]');
        if (!control) return;
        if (event.target.closest('.ai-response')) return;
        if (event.type === 'keydown' && event.key !== 'Enter' && event.key !== ' ') return;

        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        const topic = disclosureTopic(control);
        runDisclosure(control, topic.mapped, topic.kind);
    }

    function installDisclosureOwnership() {
        document.addEventListener('click', ownDisclosureEvent, true);
        document.addEventListener('keydown', ownDisclosureEvent, true);
        document.documentElement.setAttribute('data-focuschrist-pioneer-disclosure-controller', 'hardened');
    }

    window.expandTimelineItem = function (element, topic) {
        const mapped = typeof topicMap !== 'undefined' && topicMap[topic] ? topicMap[topic] : String(topic || 'Pioneer journey');
        const kind = /^(?:willie|martin)-/i.test(String(topic || '')) ? 'Willie & Martin Companies' : 'Journey';
        runDisclosure(element, mapped, kind);
    };

    window.expandTrailPoint = function (element, locationKey) {
        const mapped = typeof trailTopicMap !== 'undefined' && trailTopicMap[locationKey] ? trailTopicMap[locationKey] : String(locationKey || 'Pioneer trail');
        runDisclosure(element, mapped, 'Trail');
    };

    window.sendMessage = async function () {
        const input = userInput();
        const button = sendButton();
        if (!input || !button) return;
        const question = input.value.trim();
        if (!question) return;

        removeWelcome();
        window.addMessage(question, true);
        input.value = '';
        button.disabled = true;
        input.disabled = true;
        const loading = showLoading();

        try {
            if (typeof containsInappropriate === 'function' && containsInappropriate(question)) {
                if (loading) loading.remove();
                const answer = window.addMessage('I can help with respectful and safe questions about Latter-day Saint pioneer history. Please rephrase the request.', false);
                setConversationMode(true);
                positionAnswer(answer);
                return;
            }

            let pageReference = '';
            if (typeof searchTellMyStory === 'function') {
                const storyMatch = await searchTellMyStory(question);
                if (storyMatch && storyMatch[0] && storyMatch[0].full === false && storyMatch[0].choices) {
                    if (loading) loading.remove();
                    const answer = window.addMessage(storyMatch[0].story, false, [{ text: 'Tell My Story Too', url: 'tell-my-story-too.txt' }]);
                    window.storyChoices = storyMatch[0].choices;
                    setConversationMode(true);
                    positionAnswer(answer);
                    return;
                }
                if (storyMatch && storyMatch[0] && storyMatch[0].full === true) {
                    if (loading) loading.remove();
                    const storyContent = storyMatch[0].fullStory || storyMatch[0].story;
                    rememberExchange(question, storyContent);
                    const answer = window.addMessage(storyContent, false, [{ text: 'Tell My Story Too', url: 'tell-my-story-too.txt' }], { action: 'askTellMyStory()', text: 'Tell Me More' });
                    setConversationMode(true);
                    positionAnswer(answer);
                    return;
                }
                if (Array.isArray(storyMatch) && storyMatch.length && typeof storyMatch[0] === 'string') {
                    pageReference = 'Relevant excerpts located in the page Tell My Story collection:\n' + storyMatch.join('\n\n');
                }
            }

            const response = await requestPioneerAI(question, pageReference);
            if (loading && loading.isConnected) loading.remove();
            const answer = window.addMessage(response.answer, false, response.sources || []);
            setConversationMode(true);
            positionAnswer(answer);
        } catch (error) {
            console.error('Pioneer conversation error:', error);
            if (loading && loading.isConnected) loading.remove();
            const answer = window.addMessage('I could not complete that pioneer-history answer just now. Please try again or continue with the verified Church history resources.', false);
            setConversationMode(true);
            positionAnswer(answer);
        } finally {
            button.disabled = false;
            input.disabled = false;
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }
    };

    window.askTopic = async function (topic) {
        const box = chatBox();
        if (!box) return;
        box.innerHTML = '';
        window.addMessage(topic, true);
        const loading = showLoading();
        try {
            const query = 'Latter-day Saint pioneer history - Pioneer Topic: ' + topic;
            const response = await requestPioneerAI(query, 'Pioneer Topic button selected: ' + topic);
            if (loading && loading.isConnected) loading.remove();
            const answer = window.addMessage(response.answer, false, response.sources || []);
            setConversationMode(true);
            positionAnswer(answer);
        } catch (error) {
            console.error('Pioneer topic error:', error);
            if (loading && loading.isConnected) loading.remove();
            window.addMessage('I could not complete that pioneer-history topic just now. Please try again.', false);
        }
    };

    window.clearChat = function () {
        if (typeof conversationHistory !== 'undefined' && Array.isArray(conversationHistory)) conversationHistory.length = 0;
        try { sessionStorage.removeItem('focuschrist_history'); } catch (_error) {}
        const box = chatBox();
        if (box) {
            box.innerHTML = '';
            const welcome = document.createElement('div');
            welcome.className = 'welcome';
            const h3 = document.createElement('h3');
            h3.textContent = 'Ask About Pioneers';
            const p = document.createElement('p');
            p.textContent = 'Ask a sincere question about Latter-day Saint pioneers and their history, or choose a topic below.';
            welcome.appendChild(h3);
            welcome.appendChild(p);
            box.appendChild(welcome);
        }
        const input = userInput();
        if (input) input.value = '';
        setConversationMode(false);
        if (input) {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }
    };

    installDisclosureOwnership();

    document.addEventListener('DOMContentLoaded', function () {
        const inputArea = document.querySelector('.qa-container .input-area');
        if (inputArea && !document.getElementById('pioneerComposerLabel')) {
            const label = document.createElement('div');
            label.id = 'pioneerComposerLabel';
            label.className = 'pioneer-composer-label';
            label.textContent = 'Ask a pioneer question';
            inputArea.parentNode.insertBefore(label, inputArea);
        }
        const box = chatBox();
        if (box) {
            box.setAttribute('aria-live', 'polite');
            box.setAttribute('aria-label', 'Pioneer study conversation');
        }
        document.querySelectorAll('.category-btn').forEach(function (link) {
            link.addEventListener('click', function (event) { event.preventDefault(); });
        });
        initTopPioneerAskEntry();
        setConversationMode(false);
        document.documentElement.setAttribute('data-focuschrist-pioneer-policy', PIONEER_POLICY_VERSION);
    });
})();
