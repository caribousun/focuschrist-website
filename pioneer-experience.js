/* focusChrist Pioneer conversation experience.
   Uses the existing Pioneer knowledge functions while providing visible
   contextual follow-up behavior and safe message rendering. */
(function () {
    'use strict';

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
        if (!rawText.includes('\n') && rawText.length > 100) {
            rawText = rawText.replace(/([.!?])\s+/g, '$1\n');
        }
        const paragraphs = rawText.split('\n').map(function (item) { return item.trim(); }).filter(Boolean);

        if (isUser) {
            const p = document.createElement('p');
            const strong = document.createElement('strong');
            strong.textContent = 'You asked: ';
            p.appendChild(strong);
            p.appendChild(document.createTextNode(paragraphs[0] || rawText));
            message.appendChild(p);
        } else {
            (paragraphs.length ? paragraphs : [rawText]).forEach(function (paragraph) {
                appendTextParagraph(message, paragraph);
            });
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

    function trimConversationHistory() {
        if (typeof conversationHistory === 'undefined' || typeof MAX_CONVERSATION_LENGTH === 'undefined') return;
        while (conversationHistory.length > MAX_CONVERSATION_LENGTH * 2) conversationHistory.shift();
    }

    function rememberLocalExchange(question, answer) {
        if (typeof conversationHistory === 'undefined') return;
        conversationHistory.push({ role: 'user', content: question });
        conversationHistory.push({ role: 'assistant', content: String(answer || '') });
        trimConversationHistory();
    }

    function setConversationMode(active) {
        const label = composerLabel();
        const input = userInput();
        if (label) label.textContent = active ? 'Continue the conversation' : 'Ask a pioneer question';
        if (input) input.placeholder = active ? 'Ask a follow-up question...' : 'Ask a sincere pioneer question...';
        document.body.classList.toggle('pioneer-conversation-active', !!active);
    }

    function removeWelcome() {
        const box = chatBox();
        if (!box) return;
        const welcome = box.querySelector('.welcome');
        if (welcome) welcome.remove();
    }

    function showLoading() {
        const box = chatBox();
        if (!box) return null;
        const loading = document.createElement('div');
        loading.className = 'loading';
        loading.setAttribute('role', 'status');
        loading.textContent = 'Searching pioneer history and study sources…';
        box.appendChild(loading);
        box.scrollTop = box.scrollHeight;
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
                const answer = window.addMessage('We welcome all who seek truth with respect and love. How can I help you learn about Jesus Christ and pioneer history?', false, [{ text: 'Come Unto Christ', url: 'https://www.churchofjesuschrist.org/comeuntochrist' }]);
                setConversationMode(true);
                positionAnswer(answer);
                return;
            }

            let response;
            let localExchange = false;
            let storyDriven = false;

            const storyMatch = typeof searchTellMyStory === 'function' ? await searchTellMyStory(question) : null;
            if (storyMatch && storyMatch[0] && (storyMatch[0].full || storyMatch[0].choices)) {
                storyDriven = true;
                response = await askAI(question);
            } else {
                const localAnswer = typeof findAnswer === 'function' ? findAnswer(question) : null;
                if (localAnswer && localAnswer.found) {
                    response = localAnswer;
                    localExchange = true;
                } else {
                    response = await askAI(question);
                }
            }

            if (loading && loading.isConnected) loading.remove();

            if (response && response.alreadyDisplayed) {
                if (storyDriven && response.answer) rememberLocalExchange(question, response.answer);
                const messages = chatBox().querySelectorAll('.bot-message');
                const latest = messages.length ? messages[messages.length - 1] : null;
                setConversationMode(true);
                positionAnswer(latest);
                return;
            }

            if (localExchange && response) rememberLocalExchange(question, response.answer);
            const answer = window.addMessage(response && response.answer ? response.answer : 'I could not complete that answer. Please try again.', false, response && response.sources ? response.sources : []);
            setConversationMode(true);
            positionAnswer(answer);
        } catch (error) {
            console.error('Pioneer conversation error:', error);
            if (loading && loading.isConnected) loading.remove();
            const answer = window.addMessage('I could not complete that answer just now. Please try again or continue with the linked Church history resources.', false);
            setConversationMode(true);
            positionAnswer(answer);
        } finally {
            button.disabled = false;
            input.disabled = false;
            input.focus({ preventScroll: true });
        }
    };

    window.clearChat = function () {
        if (typeof conversationHistory !== 'undefined') conversationHistory = [];
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
        if (input) input.focus({ preventScroll: true });
    };

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
        setConversationMode(false);
    });
})();
