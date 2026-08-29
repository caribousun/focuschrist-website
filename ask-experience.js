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

    function focusConversation() {
        const conversation = document.getElementById('conversation-heading');
        if (conversation) {
            conversation.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function focusLatestAnswer() {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox) return;
        const answers = chatBox.querySelectorAll('.bot-message');
        if (!answers.length) return;
        const answer = answers[answers.length - 1];
        answer.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
                    focusLatestAnswer();
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
        initStarterQuestions();
        initTopicCards();
        initAutomaticConversationFollow();
        initRelatedStudyObserver();
        initNewQuestionButton();
        initInputLabeling();
    });
})();
