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

    function submitQuestion(question) {
        const input = document.getElementById('userInput');
        if (!input || !question) return;
        input.value = question;
        input.focus();
        if (typeof window.sendMessage === 'function') {
            window.sendMessage();
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
                } else {
                    submitQuestion(topic);
                }
            });
        });
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
                    return node.nodeType === 1 && (node.classList.contains('bot-message') || node.querySelector?.('.bot-message'));
                });
            });
            if (addedAnswer) {
                window.setTimeout(addRelatedStudyToLatestAnswer, 0);
            }
        });
        observer.observe(chatBox, { childList: true, subtree: true });
    }

    function initNewQuestionButton() {
        const button = document.getElementById('clearBtn');
        if (!button) return;
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
        initRelatedStudyObserver();
        initNewQuestionButton();
        initInputLabeling();
    });
})();
