(function () {
    'use strict';

    const relatedStudyRules = [
        { terms: ['jesus christ', 'savior', 'redeemer', 'atonement', 'resurrection'], label: 'What Do Latter-day Saints Believe About Jesus Christ?', url: 'answers/jesus-christ-latter-day-saint-beliefs.html' },
        { terms: ['christian', 'christians'], label: 'Are Latter-day Saints Christian?', url: 'answers/are-latter-day-saints-christian.html' },
        { terms: ['book of mormon', 'another testament'], label: 'What Is the Book of Mormon?', url: 'answers/what-is-the-book-of-mormon.html' },
        { terms: ['bible', 'scripture together', 'two witnesses'], label: 'How Do the Bible and Book of Mormon Work Together?', url: 'answers/bible-and-book-of-mormon-together.html' },
        { terms: ['temple', 'temples', 'endowment', 'sealing'], label: 'Why Do Latter-day Saints Build Temples?', url: 'answers/why-latter-day-saints-build-temples.html' },
        { terms: ['death', 'after death', 'spirit world', 'life after death'], label: 'What Do Latter-day Saints Believe Happens After Death?', url: 'answers/what-happens-after-death.html' },
        { terms: ['joseph smith', 'first vision', 'restoration'], label: 'Who Was Joseph Smith?', url: 'answers/who-was-joseph-smith.html' },
        { terms: ['prayer', 'revelation', 'holy ghost', 'spirit', 'answer from god', 'answers from god'], label: 'How Do Prayer and Personal Revelation Work?', url: 'answers/prayer-and-personal-revelation.html' },
        { terms: ['family', 'families', 'children', 'eternal family'], label: 'Why Are Families Important in Latter-day Saint Belief?', url: 'answers/why-families-are-important.html' },
        { terms: ['trial', 'trials', 'adversity', 'suffering', 'grief', 'hard time', 'difficult time'], label: 'How Can Faith in Jesus Christ Help During Trials?', url: 'answers/faith-in-jesus-christ-during-trials.html' }
    ];

    let followupInput = null;
    let followupButton = null;
    let followupBusy = false;

    function createWelcome() {
        const welcome = document.createElement('div');
        welcome.className = 'welcome ask-welcome';

        const heading = document.createElement('h3');
        heading.textContent = 'Begin with a sincere question.';
        welcome.appendChild(heading);

        const copy = document.createElement('p');
        copy.textContent = 'You can type your own question above or choose one of the suggested questions. The purpose is to help you study more deeply and keep Jesus Christ at the center.';
        welcome.appendChild(copy);

        const sub = document.createElement('p');
        sub.className = 'welcome-sub';
        sub.textContent = 'Scripture and official Church resources are linked whenever available.';
        welcome.appendChild(sub);
        return welcome;
    }

    function restoreRefinedWelcome() {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox) return;
        chatBox.replaceChildren(createWelcome());
    }

    function ensureFollowupStyles() {
        if (document.getElementById('ask-followup-styles')) return;
        const style = document.createElement('style');
        style.id = 'ask-followup-styles';
        style.textContent = `
            .ask-followup-dock {
                position: fixed;
                left: 50%;
                bottom: max(18px, env(safe-area-inset-bottom));
                width: min(900px, calc(100% - 32px));
                z-index: 950;
                opacity: 0;
                pointer-events: none;
                transform: translate(-50%, calc(100% + 36px));
                transition: opacity .22s ease, transform .22s ease;
            }
            .ask-followup-dock.visible {
                opacity: 1;
                pointer-events: auto;
                transform: translate(-50%, 0);
            }
            .ask-followup-shell {
                padding: 12px 14px 11px;
                border: 1px solid rgba(201,169,97,.48);
                border-radius: 16px;
                background: rgba(18,14,10,.97);
                box-shadow: 0 14px 42px rgba(0,0,0,.55);
                backdrop-filter: blur(12px);
            }
            .ask-followup-label {
                margin: 0 0 7px 4px;
                color: #c9a961;
                font-size: .72rem;
                font-weight: 700;
                letter-spacing: 1.4px;
                text-transform: uppercase;
            }
            .ask-followup-form {
                display: grid;
                grid-template-columns: minmax(0, 1fr) auto;
                gap: 9px;
                align-items: center;
            }
            .ask-followup-input {
                width: 100%;
                min-width: 0;
                padding: 13px 17px;
                border: 1px solid rgba(201,169,97,.42);
                border-radius: 999px;
                background: rgba(255,255,255,.05);
                color: #fff;
                font: inherit;
                font-size: .95rem;
            }
            .ask-followup-input::placeholder { color: #8f8477; }
            .ask-followup-input:focus {
                outline: none;
                border-color: #e0c982;
                box-shadow: 0 0 0 3px rgba(201,169,97,.10);
            }
            .ask-followup-button {
                min-height: 44px;
                padding: 0 20px;
                border: 1px solid #c9a961;
                border-radius: 999px;
                background: #c9a961;
                color: #171109;
                font-weight: 700;
                white-space: nowrap;
                cursor: pointer;
            }
            .ask-followup-button:hover,
            .ask-followup-button:focus-visible { background: #e0c982; outline: none; }
            .ask-followup-button:disabled {
                opacity: .62;
                cursor: wait;
            }
            .ask-followup-note {
                margin: 7px 4px 0;
                color: #8f8477;
                font-size: .72rem;
                line-height: 1.35;
            }
            body.ask-followup-active .ask-chat-box { padding-bottom: 112px; }
            body.ask-followup-active { padding-bottom: 104px; }
            @media (max-width: 640px) {
                .ask-followup-dock {
                    bottom: max(8px, env(safe-area-inset-bottom));
                    width: calc(100% - 16px);
                }
                .ask-followup-shell { padding: 10px; border-radius: 13px; }
                .ask-followup-label { font-size: .68rem; }
                .ask-followup-form { grid-template-columns: minmax(0, 1fr) auto; gap: 7px; }
                .ask-followup-input { padding: 12px 14px; font-size: .9rem; }
                .ask-followup-button { min-height: 42px; padding: 0 14px; font-size: .82rem; }
                .ask-followup-note { display: none; }
                body.ask-followup-active .ask-chat-box { padding-bottom: 96px; }
                body.ask-followup-active { padding-bottom: 88px; }
            }
        `;
        document.head.appendChild(style);
    }

    function setFollowupVisible(visible) {
        const dock = document.getElementById('askFollowupDock');
        if (!dock) return;
        dock.classList.toggle('visible', Boolean(visible));
        dock.setAttribute('aria-hidden', visible ? 'false' : 'true');
        document.body.classList.toggle('ask-followup-active', Boolean(visible));
    }

    function setFollowupBusy(busy) {
        followupBusy = Boolean(busy);
        if (followupInput) followupInput.disabled = followupBusy;
        if (followupButton) {
            followupButton.disabled = followupBusy;
            followupButton.textContent = followupBusy ? 'Thinking…' : 'Ask';
        }
    }

    function submitFollowup() {
        if (!followupInput || followupBusy) return;
        const question = followupInput.value.trim();
        if (!question) {
            followupInput.focus();
            return;
        }

        const primaryInput = document.getElementById('userInput');
        if (!primaryInput || typeof window.sendMessage !== 'function') return;

        primaryInput.value = question;
        followupInput.value = '';
        setFollowupBusy(true);
        window.sendMessage();
        window.setTimeout(focusConversation, 80);
    }

    function initFollowupComposer() {
        if (document.getElementById('askFollowupDock')) return;
        ensureFollowupStyles();

        const dock = document.createElement('aside');
        dock.id = 'askFollowupDock';
        dock.className = 'ask-followup-dock';
        dock.setAttribute('data-focuschrist-followup-composer', 'true');
        dock.setAttribute('aria-label', 'Ask a follow-up question');
        dock.setAttribute('aria-hidden', 'true');

        const shell = document.createElement('div');
        shell.className = 'ask-followup-shell';

        const label = document.createElement('div');
        label.className = 'ask-followup-label';
        label.textContent = 'Continue the conversation';
        shell.appendChild(label);

        const form = document.createElement('form');
        form.className = 'ask-followup-form';
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            submitFollowup();
        });

        followupInput = document.createElement('input');
        followupInput.id = 'followupInput';
        followupInput.className = 'ask-followup-input';
        followupInput.type = 'text';
        followupInput.placeholder = 'Ask a follow-up question…';
        followupInput.autocomplete = 'off';
        followupInput.setAttribute('aria-label', 'Ask a follow-up question in the current conversation');
        form.appendChild(followupInput);

        followupButton = document.createElement('button');
        followupButton.className = 'ask-followup-button';
        followupButton.type = 'submit';
        followupButton.textContent = 'Ask';
        form.appendChild(followupButton);

        shell.appendChild(form);

        const note = document.createElement('div');
        note.className = 'ask-followup-note';
        note.textContent = 'Your previous questions and answers remain part of this conversation. Use New Question above when you want to start over.';
        shell.appendChild(note);

        dock.appendChild(shell);
        document.body.appendChild(dock);

        const chatBox = document.getElementById('chatBox');
        if (chatBox && chatBox.querySelector('.bot-message')) setFollowupVisible(true);
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
        window.scrollTo({
            top: Math.max(0, top),
            behavior: preferredScrollBehavior()
        });
    }

    function focusConversation() {
        const conversation = document.getElementById('conversation-heading');
        if (conversation) scrollPageToElement(conversation);
    }

    function focusLatestAnswer() {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox) return;
        const answers = chatBox.querySelectorAll('.bot-message');
        if (!answers.length) return;

        const answer = answers[answers.length - 1];
        const answerTopInsideChat = answer.getBoundingClientRect().top - chatBox.getBoundingClientRect().top + chatBox.scrollTop;
        chatBox.scrollTo({
            top: Math.max(0, answerTopInsideChat - 18),
            behavior: preferredScrollBehavior()
        });

        scrollPageToElement(chatBox);
    }

    function submitQuestion(question) {
        const input = document.getElementById('userInput');
        if (!input || !question) return;
        input.value = question;
        input.focus();
        if (typeof window.sendMessage === 'function') {
            window.sendMessage();
            window.setTimeout(focusConversation, 80);
        }
    }

    function initStarterQuestions() {
        document.querySelectorAll('[data-ask-starter]').forEach(function (button) {
            button.addEventListener('click', function () {
                submitQuestion(button.getAttribute('data-question') || button.textContent.trim());
            });
        });
    }

    function initTopicCards() {
        document.querySelectorAll('.ask-topic-toggle').forEach(function (toggle) {
            toggle.addEventListener('click', function () {
                const card = toggle.closest('.ask-topic-card');
                if (!card) return;
                const open = !card.classList.contains('open');
                document.querySelectorAll('.ask-topic-card.open').forEach(function (other) {
                    if (other !== card) {
                        other.classList.remove('open');
                        const otherToggle = other.querySelector('.ask-topic-toggle');
                        if (otherToggle) otherToggle.setAttribute('aria-expanded', 'false');
                    }
                });
                card.classList.toggle('open', open);
                toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
        });

        document.querySelectorAll('[data-ask-topic]').forEach(function (button) {
            button.addEventListener('click', function () {
                const topic = button.getAttribute('data-ask-topic');
                if (!topic) return;
                if (typeof window.askTopic === 'function') {
                    window.askTopic(topic);
                    window.setTimeout(focusConversation, 80);
                } else {
                    submitQuestion(topic);
                }
            });
        });
    }

    function initAutomaticConversationFollow() {
        const sendButton = document.getElementById('sendBtn');
        const input = document.getElementById('userInput');

        if (sendButton) {
            sendButton.addEventListener('click', function () {
                window.setTimeout(focusConversation, 80);
            });
        }

        if (input) {
            input.addEventListener('keypress', function (event) {
                if (event.key === 'Enter') {
                    window.setTimeout(focusConversation, 80);
                }
            });
        }
    }

    function findRelatedStudy(questionText) {
        const normalized = (questionText || '').toLowerCase();
        return relatedStudyRules.find(function (rule) {
            return rule.terms.some(function (term) { return normalized.includes(term); });
        }) || null;
    }

    function addRelatedStudyToLatestAnswer() {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox) return;
        const answers = chatBox.querySelectorAll('.bot-message');
        if (!answers.length) return;
        const answer = answers[answers.length - 1];
        if (answer.querySelector('.ask-related-study')) return;

        const userMessages = chatBox.querySelectorAll('.user-message');
        if (!userMessages.length) return;
        const question = userMessages[userMessages.length - 1].textContent || '';
        const related = findRelatedStudy(question);
        if (!related) return;

        const wrap = document.createElement('div');
        wrap.className = 'ask-related-study';
        wrap.setAttribute('data-focuschrist-related-study', 'true');
        wrap.appendChild(document.createTextNode('Continue studying: '));
        const link = document.createElement('a');
        link.href = related.url;
        link.textContent = related.label;
        wrap.appendChild(link);
        answer.appendChild(wrap);
    }

    function initRelatedStudyObserver() {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox || typeof MutationObserver === 'undefined') return;
        const observer = new MutationObserver(function (mutations) {
            const addedAnswer = mutations.some(function (mutation) {
                return Array.from(mutation.addedNodes || []).some(function (node) {
                    if (node.nodeType !== 1) return false;
                    if (node.classList && node.classList.contains('bot-message')) return true;
                    return typeof node.querySelector === 'function' && Boolean(node.querySelector('.bot-message'));
                });
            });
            if (addedAnswer) {
                window.setTimeout(function () {
                    addRelatedStudyToLatestAnswer();
                    setFollowupVisible(true);
                    setFollowupBusy(false);
                    focusLatestAnswer();
                    if (followupInput && window.matchMedia && window.matchMedia('(pointer: fine)').matches) {
                        try { followupInput.focus({ preventScroll: true }); } catch (_error) { followupInput.focus(); }
                    }
                }, 60);
            }
        });
        observer.observe(chatBox, { childList: true, subtree: true });
    }

    function initNewQuestionButton() {
        const button = document.getElementById('clearBtn');
        if (!button) return;
        const originalClear = typeof window.clearChat === 'function' ? window.clearChat : null;
        if (originalClear) {
            window.clearChat = function () {
                originalClear();
                restoreRefinedWelcome();
                setFollowupVisible(false);
                setFollowupBusy(false);
                if (followupInput) followupInput.value = '';
            };
        }
        button.addEventListener('click', function () {
            window.setTimeout(function () {
                const input = document.getElementById('userInput');
                if (input) input.focus();
            }, 0);
        });
    }

    function initInputLabeling() {
        const input = document.getElementById('userInput');
        if (!input) return;
        input.setAttribute('aria-label', 'Ask a question about Jesus Christ, scripture, or Latter-day Saint belief');
        input.setAttribute('autocomplete', 'off');
    }

    document.addEventListener('DOMContentLoaded', function () {
        initFollowupComposer();
        initStarterQuestions();
        initTopicCards();
        initAutomaticConversationFollow();
        initRelatedStudyObserver();
        initNewQuestionButton();
        initInputLabeling();
    });
})();
