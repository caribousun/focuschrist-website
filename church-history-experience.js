/* focusChrist Church History study experience.
 * Keeps historical questions bound to verified official Church History routes.
 */
(function () {
    'use strict';

    const MAX_HISTORY_MESSAGES = 14;

    function byId(id) { return document.getElementById(id); }

    function historyRouter() {
        return window.focusChristSourceRouter || null;
    }

    function normalizeQuestion(value) {
        return String(value || '').replace(/\s+/g, ' ').trim();
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

    function promptContextFor(question, sources) {
        const router = historyRouter();
        if (router && typeof router.historyPromptContext === 'function') return router.historyPromptContext(question);
        return [
            'CHURCH HISTORY PAGE SOURCE CONTRACT:',
            '- Treat official Church History materials at ChurchofJesusChrist.org and the Saints volumes as the governing source family for this answer.',
            '- Do not invent historical details, quotations, dates, motives, private revelations, or source claims.',
            '- If the official source family does not clearly establish a detail, state that limitation instead of filling the gap from model memory.',
            '- Distinguish documented history, recollection, tradition, interpretation, and disputed claims when relevant.',
            '- The visitor will receive verified official source links after the answer.',
            '',
            'VERIFIED SOURCE ROUTES FOR THIS QUESTION:',
            sources.map(function (item) { return '- ' + item.label + ': ' + item.url; }).join('\n')
        ].join('\n');
    }

    async function waitForHistoryAI() {
        for (let attempt = 0; attempt < 50; attempt += 1) {
            if (typeof window.focusChristStudyAskV3 === 'function') return window.focusChristStudyAskV3;
            if (typeof window.askAI === 'function') return window.askAI;
            await new Promise(function (resolve) { window.setTimeout(resolve, 100); });
        }
        throw new Error('History study intelligence did not initialize.');
    }

    async function answerQuestion(rawQuestion) {
        const question = normalizeQuestion(rawQuestion);
        if (!question) return;

        const input = byId('historyQuestion');
        const button = byId('historyAskButton');
        const status = byId('historyStatus');
        if (input) input.disabled = true;
        if (button) {
            button.disabled = true;
            button.textContent = 'Reviewing Sources...';
        }
        if (status) status.textContent = 'Matching the question to official Church History sources.';

        appendMessage(createMessage('user', question));
        const loading = loadingMessage();
        appendMessage(loading);

        const sources = sourcePathsFor(question);
        const promptContext = promptContextFor(question, sources);
        const groundedQuestion = 'Latter-day Saint Church history question: ' + question;

        try {
            const ask = await waitForHistoryAI();
            const result = await ask(groundedQuestion, promptContext);
            if (loading.isConnected) loading.remove();
            const answer = result && typeof result === 'object' && result.answer ? result.answer : String(result || '');
            const message = createMessage('assistant', answer || 'I could not complete that history answer. Please use the official source paths below.');
            appendVerifiedSources(message, sources);
            appendMessage(message);
            if (status) status.textContent = 'Answer complete. Verify details in the official Church History links shown with the response.';
        } catch (error) {
            console.error('focusChrist Church History question error:', error);
            if (loading.isConnected) loading.remove();
            const message = createMessage('assistant', 'I could not complete the summary just now. The official Church History source paths below remain available for direct study.');
            appendVerifiedSources(message, sources);
            appendMessage(message);
            if (status) status.textContent = 'The AI summary was unavailable; official Church History source paths are still provided.';
        } finally {
            if (input) {
                input.disabled = false;
                input.value = '';
            }
            if (button) {
                button.disabled = false;
                button.textContent = 'Ask History';
            }
            if (input) {
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }
        }
    }

    function initSuggestions() {
        document.querySelectorAll('[data-history-question]').forEach(function (button) {
            button.addEventListener('click', function () {
                const question = button.getAttribute('data-history-question') || '';
                const input = byId('historyQuestion');
                if (input) input.value = question;
                answerQuestion(question);
            });
        });
    }

    function initForm() {
        const form = byId('historyAskForm');
        const input = byId('historyQuestion');
        if (!form || !input) return;
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            answerQuestion(input.value);
        });
        input.addEventListener('keydown', function (event) {
            if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                event.preventDefault();
                form.requestSubmit();
            }
        });
    }

    function init() {
        initSuggestions();
        initForm();
        document.documentElement.setAttribute('data-focuschrist-history-experience-ready', 'true');
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
