/* focusChrist shared study-journey controller.
 * Removes small navigation/friction defects across the site:
 * - content CTAs to Ask deep-link to the composer
 * - Ask honors #ask-question with header-safe scroll + focus
 * - the active Ask conversation exposes a nearby Start Over control
 * - faith/history conversations load the verified source router
 * - Art loads study/video connections without altering artwork
 */
(function () {
    'use strict';

    function reducedMotion() {
        return Boolean(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    }

    function headerOffset() {
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        if (!header) return 20;
        const style = window.getComputedStyle(header);
        return style.position === 'fixed' ? Math.ceil(header.getBoundingClientRect().height) + 22 : 18;
    }

    function scrollToTarget(target, focusInput) {
        if (!target) return;
        const top = target.getBoundingClientRect().top + window.scrollY - headerOffset();
        window.scrollTo({
            top: Math.max(0, top),
            behavior: reducedMotion() ? 'auto' : 'smooth'
        });
        if (focusInput) {
            window.setTimeout(function () {
                const input = document.getElementById('userInput');
                if (!input) return;
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }, reducedMotion() ? 0 : 260);
        }
    }

    function isNestedPage() {
        const path = window.location.pathname;
        return path.includes('/answers/') || path.includes('/art-study/');
    }

    function askHref() {
        return (isNestedPage() ? '../ask.html' : 'ask.html') + '#ask-question';
    }

    function rewriteContentAskLinks() {
        document.querySelectorAll('main a[href], section a[href]').forEach(function (link) {
            const raw = link.getAttribute('href') || '';
            if (raw === 'ask.html' || raw === '../ask.html') link.setAttribute('href', askHref());
        });
    }

    function ensureAskTarget() {
        if (!window.location.pathname.toLowerCase().endsWith('/ask.html')) return null;
        const card = document.querySelector('.ask-study-card');
        if (!card) return null;
        card.id = 'ask-question';
        card.setAttribute('data-focuschrist-ask-target', 'true');
        return card;
    }

    function honorAskDeepLink(target) {
        if (!target || window.location.hash !== '#ask-question') return;
        window.setTimeout(function () { scrollToTarget(target, true); }, 90);
    }

    function resetConversation() {
        if (typeof window.clearChat === 'function') window.clearChat();
        const target = document.getElementById('ask-question') || document.querySelector('.ask-study-card');
        window.setTimeout(function () { scrollToTarget(target, true); }, 30);
    }

    function addResetToFollowup() {
        const dock = document.getElementById('askFollowupDock');
        if (!dock || dock.querySelector('[data-focuschrist-conversation-reset]')) return false;
        const shell = dock.querySelector('.ask-followup-shell') || dock;

        const row = document.createElement('div');
        row.className = 'ask-followup-actions';
        row.setAttribute('data-focuschrist-followup-actions', 'true');

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'ask-conversation-reset';
        button.setAttribute('data-focuschrist-conversation-reset', 'true');
        button.textContent = 'Clear & Start Over';
        button.addEventListener('click', resetConversation);
        row.appendChild(button);
        shell.appendChild(row);
        return true;
    }

    function observeFollowupReset() {
        if (!window.location.pathname.toLowerCase().endsWith('/ask.html')) return;
        if (addResetToFollowup()) return;
        if (typeof MutationObserver === 'undefined') return;
        const observer = new MutationObserver(function () {
            if (addResetToFollowup()) observer.disconnect();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    function ensureConversationResetFallback() {
        if (!window.location.pathname.toLowerCase().endsWith('/ask.html')) return;
        const section = document.querySelector('.ask-conversation-section');
        if (!section || section.querySelector('[data-focuschrist-conversation-reset-fallback]')) return;

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'ask-conversation-reset ask-conversation-reset--fallback';
        button.setAttribute('data-focuschrist-conversation-reset', 'true');
        button.setAttribute('data-focuschrist-conversation-reset-fallback', 'true');
        button.textContent = 'Clear Conversation';
        button.addEventListener('click', resetConversation);

        const heading = section.querySelector('.ask-section-heading');
        if (heading) heading.insertAdjacentElement('afterend', button);
        else section.insertBefore(button, section.firstChild);
    }

    function appendDynamicScript(src, marker) {
        if (document.querySelector('script[' + marker + ']')) return;
        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.setAttribute(marker, 'true');
        script.addEventListener('error', function () {
            console.error('focusChrist study journey asset failed to load: ' + src);
        }, { once: true });
        document.body.appendChild(script);
    }

    function loadVerifiedSourceRouter() {
        const path = window.location.pathname.toLowerCase();
        if (path.endsWith('/ask.html') || path.endsWith('/pioneers.html')) {
            appendDynamicScript('study-source-router.js?v=20260829-1', 'data-focuschrist-source-router');
        }
    }

    function loadArtStudyRouter() {
        if (window.location.pathname.toLowerCase().endsWith('/art.html')) {
            appendDynamicScript('art-study-router.js?v=20260829-1', 'data-focuschrist-art-study-router');
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        rewriteContentAskLinks();
        const target = ensureAskTarget();
        honorAskDeepLink(target);
        ensureConversationResetFallback();
        observeFollowupReset();
        window.setTimeout(loadVerifiedSourceRouter, 0);
        window.setTimeout(loadArtStudyRouter, 0);
    });
})();
