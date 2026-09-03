/* focusChrist Church History study experience.
 * Keeps historical questions bound to verified official Church History routes.
 * Mirrors the main Ask page's conversation, follow-up, reset, and auto-follow behavior.
 */
(function () {
    'use strict';

    const MAX_HISTORY_MESSAGES = 14;
    const MAX_CONTEXT_TURNS = 6;
    const HISTORY_HERO_URL = 'assets/heroes/church-history.webp';
    const historyConversation = [];
    let historyBusy = false;
    let historyRequestSerial = 0;

    function byId(id) { return document.getElementById(id); }

    function historyRouter() {
        return window.focusChristSourceRouter || null;
    }

    function normalizeQuestion(value) {
        return String(value || '').replace(/\s+/g, ' ').trim();
    }

    function resolveHistoryContext(question) {
        const registry = window.focusChristReviewedKnowledge;
        if (!registry || typeof registry.resolveFollowup !== 'function') {
            return { query: question, resolved: false, entryId: null, contextQuestion: null };
        }
        return registry.resolveFollowup(question, { profile: 'church-history', history: historyConversation });
    }

    function reviewedHistoryKnowledge(question, suppliedResolution) {
        const registry = window.focusChristReviewedKnowledge;
        if (!registry || typeof registry.match !== 'function') return null;
        const resolution = suppliedResolution || (typeof registry.resolveFollowup === 'function'
            ? registry.resolveFollowup(question, { profile: 'church-history', history: historyConversation })
            : { query: question, resolved: false, entryId: null });
        if (resolution.genericContext === true) return null;
        const reviewed = registry.match(resolution.query, {
            profile: 'church-history',
            contextVariant: resolution.contextVariant
        });
        if (!reviewed) return null;
        return Object.assign({}, reviewed, {
            contextResolved: resolution.resolved === true,
            contextEntryId: resolution.entryId || null,
            contextQuestion: resolution.contextQuestion || null
        });
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

    function scrollComposerIntoView() {
        const form = byId('historyAskForm');
        if (!form) return;
        const top = form.getBoundingClientRect().top + window.scrollY - fixedHeaderOffset() - 14;
        window.scrollTo({ top: Math.max(0, top), behavior: preferredScrollBehavior() });
    }

    function ensureAskEntryStyles() {
        if (byId('focuschrist-history-entry-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-history-entry-styles';
        style.textContent = `
            html[data-focuschrist-history-ask-entry-active] #historyConversation {
                border-color: rgba(240,195,106,.58) !important;
                box-shadow: 0 0 0 2px rgba(240,195,106,.10), 0 24px 70px rgba(4,17,23,.38) !important;
            }
            html[data-focuschrist-history-ask-entry-active] #historyAskForm {
                background:
                    radial-gradient(circle at 82% 0%, rgba(240,195,106,.08), transparent 18rem),
                    linear-gradient(180deg, rgba(18,44,54,.88), rgba(11,29,37,.96)) !important;
            }
            html[data-focuschrist-history-ask-entry-active] #historyQuestion {
                border-color: var(--fc-gold-light) !important;
                box-shadow: 0 0 0 3px rgba(240,195,106,.12) !important;
            }
            html[data-focuschrist-history-ask-entry-active] #historyQuestionLabel {
                color: var(--fc-gold-light) !important;
            }
        `;
        document.head.appendChild(style);
    }

    function setAskEntryActive(active) {
        document.documentElement.toggleAttribute('data-focuschrist-history-ask-entry-active', Boolean(active));
    }

    function activateHistoryAskEntry(options) {
        const settings = options || {};
        const input = byId('historyQuestion');
        ensureAskEntryStyles();
        setAskEntryActive(true);

        if (settings.updateHash !== false && window.location.hash !== '#ask-history') {
            try {
                window.history.pushState(null, '', '#ask-history');
            } catch (_error) {
                window.location.hash = 'ask-history';
            }
        }

        window.setTimeout(function () {
            scrollComposerIntoView();
            window.setTimeout(function () {
                if (!input) return;
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }, preferredScrollBehavior() === 'smooth' ? 260 : 20);
        }, 20);
    }

    function initAskEntryNavigation() {
        document.querySelectorAll('a[href="#ask-history"]').forEach(function (link) {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                activateHistoryAskEntry({ updateHash: true });
            });
        });

        window.addEventListener('hashchange', function () {
            if (window.location.hash === '#ask-history') activateHistoryAskEntry({ updateHash: false });
            else setAskEntryActive(false);
        });

        if (window.location.hash === '#ask-history') {
            window.setTimeout(function () {
                activateHistoryAskEntry({ updateHash: false });
            }, 80);
        }
    }

    function focusConversation() {
        scrollPageToElement(byId('historyConversation') || byId('ask-history'));
    }

    function focusLatestAnswer() {
        const box = byId('historyChatBox');
        if (!box) return;
        const answers = box.querySelectorAll('.bot-message');
        if (!answers.length) return;
        const answer = answers[answers.length - 1];
        const answerTopInsideChat = answer.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;
        box.scrollTo({ top: Math.max(0, answerTopInsideChat - 16), behavior: preferredScrollBehavior() });
        scrollPageToElement(byId('historyConversation') || box);
    }

    function initHero() {
        const hero = document.querySelector('.fc-history-hero');
        const image = hero ? hero.querySelector('img') : null;
        if (!hero || !image) return;

        hero.setAttribute('aria-label', 'Sacred Grove inspired Church history scene');
        image.src = HISTORY_HERO_URL;
        image.alt = 'A peaceful wooded grove at dawn with warm sunlight filtering through the trees';
        image.loading = 'eager';
        image.decoding = 'async';
        image.referrerPolicy = 'no-referrer';
        try { image.fetchPriority = 'high'; } catch (_error) { /* unsupported browser */ }

        image.addEventListener('load', function () {
            hero.classList.remove('fc-history-hero--image-error');
            image.hidden = false;
            document.documentElement.setAttribute('data-focuschrist-history-hero', 'sacred-grove-restoration');
        }, { once: true });

        image.addEventListener('error', function () {
            image.hidden = true;
            hero.classList.add('fc-history-hero--image-error');
            document.documentElement.setAttribute('data-focuschrist-history-hero', 'fallback-no-broken-bitmap');
        }, { once: true });
    }

    function createWelcome() {
        const welcome = document.createElement('div');
        welcome.className = 'fc-history-welcome';

        const strong = document.createElement('strong');
        strong.textContent = 'Ask about a person, event, place, practice, date, or historical question.';
        welcome.appendChild(strong);

        const span = document.createElement('span');
        span.textContent = 'Official Church History sources will be shown with the response. Follow-up questions stay in the same conversation until you choose New Question.';
        welcome.appendChild(span);
        return welcome;
    }

    function createMessage(kind, text) {
        const wrap = document.createElement('div');
        wrap.className = 'fc-history-message fc-history-message--' + kind;
        if (kind === 'user') wrap.classList.add('user-message');
        if (kind === 'assistant') wrap.classList.add('bot-message');

        const label = document.createElement('div');
        label.className = 'fc-history-message-label';
        label.textContent = kind === 'user' ? 'Your question' : 'focusChrist history study';
        wrap.appendChild(label);

        const body = document.createElement('div');
        body.className = 'fc-history-message-body';
        renderPlainText(body, text);
        wrap.appendChild(body);
        return wrap;
    }

    function renderPlainText(target, text) {
        target.textContent = '';
        const clean = String(text || '').trim();
        if (!clean) return;
        const blocks = clean.split(/\n{2,}/).filter(Boolean);
        blocks.forEach(function (block) {
            const lines = block.split('\n').map(function (line) { return line.trim(); }).filter(Boolean);
            const isList = lines.length > 0 && lines.every(function (line) { return /^[-*]\s+/.test(line); });
            if (isList) {
                const ul = document.createElement('ul');
                lines.forEach(function (line) {
                    const li = document.createElement('li');
                    li.textContent = line.replace(/^[-*]\s+/, '');
                    ul.appendChild(li);
                });
                target.appendChild(ul);
                return;
            }
            const p = document.createElement('p');
            p.textContent = lines.join(' ');
            target.appendChild(p);
        });
    }

    function appendVerifiedSources(messageNode, sources) {
        if (!messageNode || !Array.isArray(sources) || !sources.length) return;
        const body = messageNode.querySelector('.fc-history-message-body');
        if (!body) return;

        const panel = document.createElement('aside');
        panel.className = 'fc-history-verified-sources';
        panel.setAttribute('aria-label', 'Official Church History sources');

        const title = document.createElement('div');
        title.className = 'fc-history-verified-sources-title';
        title.textContent = 'Official Church History study paths';
        panel.appendChild(title);

        sources.forEach(function (item) {
            if (!item || !item.url) return;
            const link = document.createElement('a');
            link.href = item.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';

            const strong = document.createElement('strong');
            strong.textContent = item.label || 'Official Church History source';
            link.appendChild(strong);

            const detail = document.createElement('span');
            detail.textContent = item.note || item.tier || 'Official Church source';
            link.appendChild(detail);
            panel.appendChild(link);
        });
        body.appendChild(panel);
    }

    function appendMessage(node) {
        const box = byId('historyChatBox');
        if (!box || !node) return;
        box.querySelectorAll('.fc-history-welcome').forEach(function (welcome) { welcome.remove(); });
        box.appendChild(node);
        const messages = box.querySelectorAll('.fc-history-message');
        if (messages.length > MAX_HISTORY_MESSAGES) {
            for (let i = 0; i < messages.length - MAX_HISTORY_MESSAGES; i += 1) messages[i].remove();
        }
        box.scrollTop = box.scrollHeight;
    }

    function loadingMessage() {
        const node = createMessage('assistant', 'Reviewing the question against the indexed official Church History source paths...');
        const body = node.querySelector('.fc-history-message-body');
        if (body) body.classList.add('fc-history-loading');
        node.setAttribute('data-history-loading', 'true');
        return node;
    }

    function sourcePathsFor(question) {
        const router = historyRouter();
        if (router && typeof router.sourcesForHistoryQuestion === 'function') return router.sourcesForHistoryQuestion(question);
        return [
            {
                label: 'Official Church History',
                url: 'https://www.churchofjesuschrist.org/study/church-history?lang=eng',
                tier: 'Official Church',
                note: 'Primary Church History source hub.'
            },
            {
                label: 'Saints',
                url: 'https://www.churchofjesuschrist.org/study/church-history/saints?lang=eng',
                tier: 'Official Church',
                note: 'Current four-volume narrative Church history.'
            }
        ];
    }

    function recentConversationContext() {
        if (!historyConversation.length) return '';
        return historyConversation.slice(-MAX_CONTEXT_TURNS).map(function (turn, index) {
            return [
                'Turn ' + (index + 1) + ' question: ' + turn.question,
                'Turn ' + (index + 1) + ' answer: ' + turn.answer
            ].join('\n');
        }).join('\n\n');
    }

    function promptContextFor(question, sources) {
        const router = historyRouter();
        const base = router && typeof router.historyPromptContext === 'function'
            ? router.historyPromptContext(question)
            : [
                'CHURCH HISTORY PAGE SOURCE CONTRACT:',
                '- Treat official Church History materials at ChurchofJesusChrist.org and the Saints volumes as the governing source family for this answer.',
                '- Do not invent historical details, quotations, dates, motives, private revelations, or source claims.',
                '- If the official source family does not clearly establish a detail, state that limitation instead of filling the gap from model memory.',
                '- Give a direct, developed answer. A simple fact still needs enough context to be useful; a nuanced question normally needs two to five short paragraphs.',
                '- Never answer a sincere question with only one or two words.',
                '- Distinguish documented history, recollection, tradition, interpretation, and disputed claims when relevant.',
                '- The visitor will receive verified official source links after the answer.',
                '',
                'OFFICIAL STUDY ROUTES (LINKS ONLY; NOT CLAIM VERIFICATION):',
                sources.map(function (item) { return '- ' + item.label + ': ' + item.url; }).join('\n')
            ].join('\n');

        const prior = recentConversationContext();
        if (!prior) return base;
        return base + '\n\nCURRENT CHURCH HISTORY CONVERSATION CONTEXT:\nUse this only to understand follow-up references. Current official source rules still govern.\n' + prior;
    }

    async function waitForHistoryAI() {
        for (let attempt = 0; attempt < 50; attempt += 1) {
            if (typeof window.focusChristStudyAskV3 === 'function') return window.focusChristStudyAskV3;
            if (typeof window.askAI === 'function') return window.askAI;
            await new Promise(function (resolve) { window.setTimeout(resolve, 100); });
        }
        throw new Error('History study intelligence did not initialize.');
    }

    function setConversationMode(active) {
        const label = byId('historyQuestionLabel');
        const input = byId('historyQuestion');
        if (label) label.textContent = active ? 'Continue the conversation' : 'Your Church history question';
        if (input) input.placeholder = active ? 'Ask a follow-up question...' : 'For example: What happened after the Saints left Nauvoo?';
        document.documentElement.toggleAttribute('data-focuschrist-history-conversation-active', Boolean(active));
    }

    function setBusy(busy) {
        historyBusy = Boolean(busy);
        const input = byId('historyQuestion');
        const button = byId('historyAskButton');
        const reset = byId('historyResetButton');
        if (input) input.disabled = historyBusy;
        if (button) {
            button.disabled = historyBusy;
            button.textContent = historyBusy ? 'Reviewing Sources...' : (historyConversation.length ? 'Ask Follow-up' : 'Ask History');
        }
        if (reset) reset.disabled = historyBusy;
    }

    async function answerQuestion(rawQuestion) {
        const question = normalizeQuestion(rawQuestion);
        if (!question || historyBusy) return;
        const safety = window.focusChristQuestionSafety && typeof window.focusChristQuestionSafety.evaluate === 'function'
            ? window.focusChristQuestionSafety.evaluate(question)
            : { allowed: !(typeof window.containsInappropriate === 'function' && window.containsInappropriate(question)), response: '' };
        if (!safety.allowed) {
            const input = byId('historyQuestion');
            const status = byId('historyStatus');
            if (input) input.value = '';
            appendMessage(createMessage('assistant', safety.response || 'Please rephrase the question respectfully.'));
            setConversationMode(true);
            if (status) status.textContent = safety.kind === 'urgent-safety'
                ? 'Safety guidance provided. Ask a different question when you are ready.'
                : 'Please rephrase the question respectfully.';
            window.setTimeout(focusLatestAnswer, 70);
            if (input) {
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }
            return;
        }
        const requestId = ++historyRequestSerial;

        const input = byId('historyQuestion');
        const status = byId('historyStatus');
        setBusy(true);
        setAskEntryActive(true);
        if (status) status.textContent = historyConversation.length
            ? 'Continuing the conversation with official Church History source routing.'
            : 'Matching the question to official Church History sources.';

        appendMessage(createMessage('user', question));
        if (input) input.value = '';
        const contextResolution = resolveHistoryContext(question);
        const reviewed = reviewedHistoryKnowledge(question, contextResolution);
        if (reviewed) {
            const message = createMessage('assistant', reviewed.answer);
            appendVerifiedSources(message, reviewed.sources || []);
            appendMessage(message);
            historyConversation.push({
                question: question,
                answer: reviewed.answer,
                contextEntryId: reviewed.contextEntryId || reviewed.id || null,
                contextQuestion: reviewed.contextQuestion || null
            });
            if (historyConversation.length > MAX_CONTEXT_TURNS) historyConversation.shift();
            setConversationMode(true);
            setBusy(false);
            if (status) status.textContent = 'Reviewed local answer complete. Ask a follow-up below or choose New Question to start over.';
            window.setTimeout(focusLatestAnswer, 70);
            if (input) {
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }
            return reviewed;
        }
        const loading = loadingMessage();
        appendMessage(loading);
        window.setTimeout(focusConversation, 40);

        const sources = sourcePathsFor(question);
        const promptContext = promptContextFor(question, sources);
        const groundedQuestion = 'Latter-day Saint Church history question: ' + (contextResolution.query || question);

        try {
            const ask = await waitForHistoryAI();
            const result = await ask(groundedQuestion, promptContext);
            if (requestId !== historyRequestSerial) return;
            if (loading.isConnected) loading.remove();
            const answer = result && typeof result === 'object' && result.answer ? result.answer : String(result || '');
            const finalAnswer = answer || 'I could not complete that history answer. Please use the official source paths below.';
            const message = createMessage('assistant', finalAnswer);
            appendVerifiedSources(message, sources);
            appendMessage(message);
            historyConversation.push({
                question: question,
                answer: finalAnswer,
                contextEntryId: contextResolution.entryId || null,
                contextQuestion: contextResolution.contextQuestion || null
            });
            if (historyConversation.length > MAX_CONTEXT_TURNS) historyConversation.shift();
            setConversationMode(true);
            if (status) status.textContent = 'Answer complete. Ask a follow-up below or choose New Question to start over.';
            window.setTimeout(focusLatestAnswer, 70);
        } catch (error) {
            if (requestId !== historyRequestSerial) return;
            console.error('focusChrist Church History question error:', error);
            if (loading.isConnected) loading.remove();
            const fallback = 'I could not complete the summary just now. The official Church History source paths below remain available for direct study.';
            const message = createMessage('assistant', fallback);
            appendVerifiedSources(message, sources);
            appendMessage(message);
            if (status) status.textContent = 'The AI summary was unavailable; official Church History source paths are still provided.';
            window.setTimeout(focusLatestAnswer, 70);
        } finally {
            if (requestId !== historyRequestSerial) return;
            setBusy(false);
            if (input) {
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }
        }
    }

    function resetConversation() {
        historyRequestSerial += 1;
        historyConversation.length = 0;
        const box = byId('historyChatBox');
        const input = byId('historyQuestion');
        const status = byId('historyStatus');
        if (box) box.replaceChildren(createWelcome());
        if (input) input.value = '';
        setConversationMode(false);
        setBusy(false);
        setAskEntryActive(true);
        if (status) status.textContent = 'Official Church History source routing active.';
        if (input) {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }
        window.setTimeout(scrollComposerIntoView, 30);
    }

    function initSuggestions() {
        document.querySelectorAll('[data-history-question]').forEach(function (button) {
            button.addEventListener('click', function () {
                const question = button.getAttribute('data-history-question') || '';
                const input = byId('historyQuestion');
                if (input) input.value = question;
                setAskEntryActive(true);
                answerQuestion(question);
            });
        });
    }

    function initForm() {
        const form = byId('historyAskForm');
        const input = byId('historyQuestion');
        const reset = byId('historyResetButton');
        if (!form || !input) return;

        form.addEventListener('submit', function (event) {
            event.preventDefault();
            answerQuestion(input.value);
        });

        input.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                if (typeof form.requestSubmit === 'function') form.requestSubmit();
                else byId('historyAskButton').click();
            }
        });

        input.addEventListener('focus', function () {
            setAskEntryActive(true);
        });

        if (reset) reset.addEventListener('click', resetConversation);
    }

    function init() {
        initHero();
        ensureAskEntryStyles();
        initAskEntryNavigation();
        initSuggestions();
        initForm();
        setConversationMode(false);
        document.documentElement.setAttribute('data-focuschrist-history-experience-ready', 'true');
    }

    window.focusChristHistoryAsk = answerQuestion;
    window.focusChristResetHistoryAsk = resetConversation;

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
