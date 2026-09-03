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
                position: relative;
                width: 100%;
                margin: 0;
                max-height: 0;
                overflow: hidden;
                opacity: 0;
                pointer-events: none;
                transform: translateY(10px);
                transition: opacity .22s ease, transform .22s ease, max-height .22s ease, margin .22s ease;
            }
            .ask-followup-dock.visible {
                margin-top: 14px;
                max-height: 190px;
                opacity: 1;
                pointer-events: auto;
                transform: translateY(0);
            }
            .ask-followup-shell {
                padding: 12px 14px 11px;
                border: 1px solid rgba(201,169,97,.42);
                border-radius: 16px;
                background: linear-gradient(145deg, rgba(31,24,17,.98), rgba(18,14,10,.99));
                box-shadow: 0 10px 28px rgba(0,0,0,.34);
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
            @media (max-width: 640px) {
                .ask-followup-dock.visible { margin-top: 10px; }
                .ask-followup-shell { padding: 10px; border-radius: 13px; }
                .ask-followup-label { font-size: .68rem; }
                .ask-followup-form { grid-template-columns: minmax(0, 1fr) auto; gap: 7px; }
                .ask-followup-input { padding: 12px 14px; font-size: .9rem; }
                .ask-followup-button { min-height: 42px; padding: 0 14px; font-size: .82rem; }
                .ask-followup-note { display: none; }
            }
        `;
        document.head.appendChild(style);
    }

    function setFollowupVisible(visible) {
        const dock = document.getElementById('askFollowupDock');
        if (!dock) return;
        dock.classList.toggle('visible', Boolean(visible));
        dock.setAttribute('aria-hidden', visible ? 'false' : 'true');
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
        note.textContent = 'Your previous questions and answers remain part of this conversation. Use Clear Conversation above when you want to start over.';
        shell.appendChild(note);

        dock.appendChild(shell);

        const chatBox = document.getElementById('chatBox');
        if (chatBox) {
            chatBox.insertAdjacentElement('beforebegin', dock);
        } else {
            document.body.appendChild(dock);
        }

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

    function ensureAskEntryStyles() {
        if (document.getElementById('ask-entry-styles')) return;
        const style = document.createElement('style');
        style.id = 'ask-entry-styles';
        style.textContent = `
            html[data-focuschrist-ask-entry-active] .ask-study-card {
                border-color: rgba(240,195,106,.70);
                box-shadow: 0 24px 70px rgba(4,17,23,.36), 0 0 0 3px rgba(240,195,106,.10);
            }
        `;
        document.head.appendChild(style);
    }

    function focusAskComposer(updateHash) {
        const card = document.querySelector('.ask-study-card');
        const input = document.getElementById('userInput');
        if (!card || !input) return;

        card.id = 'ask-question';
        document.documentElement.setAttribute('data-focuschrist-ask-entry-active', 'true');
        scrollPageToElement(card);

        window.setTimeout(function () {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }, 260);

        if (updateHash && window.history && typeof window.history.replaceState === 'function') {
            window.history.replaceState(null, '', '#ask-question');
        }
    }

    function initTopAskEntry() {
        const card = document.querySelector('.ask-study-card');
        const intro = document.querySelector('.fc-page-intro .fc-container--standard');
        const input = document.getElementById('userInput');
        if (!card || !intro || !input) return;

        ensureAskEntryStyles();
        card.id = 'ask-question';

        if (!intro.querySelector('[data-focuschrist-top-ask-cta]')) {
            const actions = document.createElement('div');
            actions.className = 'fc-actions fc-actions--center';
            actions.setAttribute('data-focuschrist-top-ask-cta', 'true');

            const link = document.createElement('a');
            link.className = 'fc-button fc-button--primary';
            link.href = '#ask-question';
            link.textContent = 'Ask a Question';
            link.addEventListener('click', function (event) {
                event.preventDefault();
                focusAskComposer(true);
            });
            actions.appendChild(link);
            intro.appendChild(actions);
        }

        input.addEventListener('focus', function () {
            document.documentElement.setAttribute('data-focuschrist-ask-entry-active', 'true');
        });

        window.addEventListener('hashchange', function () {
            if (window.location.hash === '#ask-question') focusAskComposer(false);
        });

        if (window.location.hash === '#ask-question') {
            window.setTimeout(function () { focusAskComposer(false); }, 90);
        }
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

        const followupDock = document.getElementById('askFollowupDock');
        scrollPageToElement(followupDock && followupDock.classList.contains('visible') ? followupDock : chatBox);
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
    window.focusChristInitAskStarters = initStarterQuestions;

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
                // Route topics through the same final controller as typed questions.
                // The legacy inline askTopic path bypasses request ownership and the
                // shared reviewed-local first lane.
                submitQuestion('Tell me about ' + topic);
            });
        });
    }
    window.focusChristInitAskTopicCards = initTopicCards;

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
        const conversationButton = document.getElementById('conversationClearBtn');
        if (!button) return;
        const originalClear = typeof window.clearChat === 'function' ? window.clearChat : null;
        if (originalClear) {
            window.clearChat = function () {
                if (typeof window.focusChristCancelAskRequests === 'function') window.focusChristCancelAskRequests();
                originalClear();
                const primaryInput = document.getElementById('userInput');
                const primaryButton = document.getElementById('sendBtn');
                if (primaryInput) primaryInput.disabled = false;
                if (primaryButton) {
                    primaryButton.disabled = false;
                    primaryButton.textContent = 'Ask';
                }
                restoreRefinedWelcome();
                setFollowupVisible(false);
                setFollowupBusy(false);
                if (followupInput) followupInput.value = '';
            };
        }
        button.addEventListener('click', function () {
            window.setTimeout(function () {
                focusAskComposer(false);
            }, 0);
        });
        if (conversationButton) {
            conversationButton.addEventListener('click', function () {
                if (typeof window.clearChat === 'function') window.clearChat();
                window.setTimeout(function () {
                    focusAskComposer(false);
                }, 0);
            });
        }
    }

    function initInputLabeling() {
        const input = document.getElementById('userInput');
        if (!input) return;
        input.setAttribute('aria-label', 'Ask a question about Jesus Christ, scripture, or Latter-day Saint belief');
        input.setAttribute('autocomplete', 'off');
    }

    document.addEventListener('DOMContentLoaded', function () {
        initTopAskEntry();
        initFollowupComposer();
        initStarterQuestions();
        initTopicCards();
        initAutomaticConversationFollow();
        initRelatedStudyObserver();
        initNewQuestionButton();
        initInputLabeling();
    });
})();
