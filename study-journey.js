/* focusChrist shared study-journey controller.
 * Removes small navigation/friction defects across the site:
 * - content CTAs to Ask deep-link to the composer
 * - Ask honors #ask-question with header-safe scroll + focus
 * - the active Ask conversation exposes a nearby Start Over control
 * - Art and Pioneers receive a clear continuation bridge instead of ending abruptly
 * - faith/history conversations load the verified source router
 * - Art loads study/video connections without altering artwork
 * - Watch loads theme-based YouTube and official video enrichment
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

    function scrollToTarget(target, focusInput, behaviorOverride) {
        if (!target) return;
        const top = target.getBoundingClientRect().top + window.scrollY - headerOffset();
        window.scrollTo({ top: Math.max(0, top), behavior: behaviorOverride || (reducedMotion() ? 'auto' : 'smooth') });
        if (focusInput) {
            window.setTimeout(function () {
                const input = document.getElementById('userInput');
                if (!input) return;
                try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            }, reducedMotion() ? 0 : 180);
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
        document.querySelectorAll('a[href]').forEach(function (link) {
            if (link.closest('.nav, .hamburger-menu')) return;
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
        function position(focusInput, behavior) { scrollToTarget(target, focusInput, behavior); }
        window.requestAnimationFrame(function () { position(false, 'auto'); });
        window.setTimeout(function () { position(true); }, 120);
        window.setTimeout(function () {
            if (window.location.hash === '#ask-question') position(false, 'auto');
        }, 520);
        if (document.readyState !== 'complete') {
            window.addEventListener('load', function () {
                if (window.location.hash === '#ask-question') position(false, 'auto');
            }, { once: true });
        }
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

    function continuationCard(href, titleText, copyText, primary) {
        const link = document.createElement('a');
        link.className = 'fc-card fc-card--interactive';
        link.href = href;
        if (primary) link.setAttribute('data-focuschrist-primary-continuation', 'true');
        const title = document.createElement('h3');
        title.className = 'fc-card-title';
        title.textContent = titleText;
        const copy = document.createElement('p');
        copy.textContent = copyText;
        link.appendChild(title);
        link.appendChild(copy);
        return link;
    }

    function ensureContinuationBridge() {
        const path = window.location.pathname.toLowerCase();
        if (!path.endsWith('/art.html') && !path.endsWith('/pioneers.html')) return;
        const main = document.querySelector('main, [role="main"]');
        if (!main || main.querySelector('[data-focuschrist-continuation-bridge]')) return;

        const section = document.createElement('section');
        section.className = 'fc-section fc-section--warm';
        section.setAttribute('data-focuschrist-continuation-bridge', 'true');
        const container = document.createElement('div');
        container.className = 'fc-container--standard';

        const eyebrow = document.createElement('p');
        eyebrow.className = 'fc-eyebrow';
        eyebrow.style.textAlign = 'center';
        eyebrow.textContent = 'Continue studying';
        const heading = document.createElement('h2');
        heading.className = 'fc-section-heading fc-section-heading--center';
        heading.textContent = 'Where would you like to go next?';
        const intro = document.createElement('p');
        intro.className = 'fc-section-intro fc-section-intro--center';
        intro.textContent = path.endsWith('/art.html')
            ? 'Carry the theme of an image into a question, a permanent answer, or video study.'
            : 'Continue from pioneer history into a question, a doctrinal topic, or related video and scripture study.';

        const grid = document.createElement('div');
        grid.className = 'fc-grid';
        grid.style.marginTop = '30px';
        grid.appendChild(continuationCard('ask.html#ask-question', 'Ask a Follow-up Question', 'Move directly into the question composer and continue exploring what the page raised for you.', true));
        grid.appendChild(continuationCard('answers.html', 'Explore the Answer Library', 'Study permanent Christ-centered explanations with direct pathways to scripture and authoritative sources.', false));
        grid.appendChild(continuationCard('watch.html', 'Watch & Continue Study', 'Move between focusChrist study themes, official Church media, and @theRisen636 video pathways.', false));

        container.appendChild(eyebrow);
        container.appendChild(heading);
        container.appendChild(intro);
        container.appendChild(grid);
        section.appendChild(container);
        main.appendChild(section);
    }

    function appendDynamicScript(src, marker) {
        if (document.querySelector('script[' + marker + ']')) return;
        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.setAttribute(marker, 'true');
        script.addEventListener('error', function () { console.error('focusChrist study journey asset failed to load: ' + src); }, { once: true });
        document.body.appendChild(script);
    }

    function loadVerifiedSourceRouter() {
        const path = window.location.pathname.toLowerCase();
        if (path.endsWith('/ask.html') || path.endsWith('/pioneers.html')) appendDynamicScript('study-source-router.js?v=20260901-2', 'data-focuschrist-source-router');
    }

    function loadArtStudyRouter() {
        if (window.location.pathname.toLowerCase().endsWith('/art.html')) appendDynamicScript('art-study-router.js?v=20260830-3', 'data-focuschrist-art-study-router');
    }

    function loadWatchStudyEnrichment() {
        if (window.location.pathname.toLowerCase().endsWith('/watch.html')) appendDynamicScript('watch-study-enrichment.js?v=20260830-3', 'data-focuschrist-watch-enrichment');
    }

    function init() {
        rewriteContentAskLinks();
        const target = ensureAskTarget();
        honorAskDeepLink(target);
        ensureConversationResetFallback();
        observeFollowupReset();
        ensureContinuationBridge();
        window.setTimeout(loadVerifiedSourceRouter, 0);
        window.setTimeout(loadArtStudyRouter, 0);
        window.setTimeout(loadWatchStudyEnrichment, 0);
        document.documentElement.setAttribute('data-focuschrist-study-journey-ready', 'true');
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
