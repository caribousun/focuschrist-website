/* focusChrist contextual artwork study bridge for Ask.
 * Activated only when Ask receives ?art=... from the Art modal.
 * Keeps the selected artwork/topic visible and provides an exact return path.
 */
(function () {
    'use strict';

    function safeReturnUrl(raw, art) {
        const fallback = 'art.html?art=' + encodeURIComponent(art || 'This artwork');
        if (!raw) return fallback;
        try {
            const url = new URL(raw, window.location.href);
            if (url.origin !== window.location.origin) return fallback;
            if (url.pathname === '/index.html') {
                const key = url.searchParams.get('artwork');
                const homeArtwork = ['home-come-and-see', 'home-seek-study', 'home-light-through-study'];
                if (!homeArtwork.includes(key)) return fallback;
                return url.pathname + '?artwork=' + encodeURIComponent(key);
            }
            if (!url.pathname.toLowerCase().endsWith('/art.html')) return fallback;
            return url.pathname.split('/').pop() + url.search + url.hash;
        } catch (_error) {
            return fallback;
        }
    }

    function ensureStyles() {
        if (document.getElementById('focuschrist-art-ask-context-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-art-ask-context-styles';
        style.textContent = `
            .ask-art-context{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:14px;align-items:center;margin:0 0 20px;padding:14px 16px;border:1px solid rgba(201,169,97,.38);border-radius:16px;background:linear-gradient(145deg,rgba(35,56,62,.96),rgba(20,38,46,.98));box-shadow:0 12px 34px rgba(4,17,23,.18)}
            .ask-art-context-kicker{display:block;margin-bottom:3px;color:#e0c982;font-size:.7rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}
            .ask-art-context-title{display:block;color:#f5efe2;font-family:Georgia,'Times New Roman',serif;font-size:1.1rem;line-height:1.2}
            .ask-art-context-topic{display:block;margin-top:4px;color:#b8c7ca;font-size:.78rem;line-height:1.4}
            .ask-art-context-return,.ask-art-return-float{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 13px;border:1px solid rgba(224,201,130,.68);border-radius:999px;background:rgba(224,201,130,.10);color:#f1d990!important;text-decoration:none!important;font-size:.78rem;font-weight:800}
            .ask-art-context-return:hover,.ask-art-context-return:focus-visible,.ask-art-return-float:hover,.ask-art-return-float:focus-visible{background:#e0c982;color:#17262d!important;outline:none}
            .ask-art-return-float{position:fixed;right:18px;bottom:18px;z-index:1100;max-width:min(310px,calc(100vw - 36px));background:rgba(20,38,46,.96);box-shadow:0 10px 32px rgba(0,0,0,.30);backdrop-filter:blur(10px)}
            @media(max-width:640px){.ask-art-context{grid-template-columns:1fr}.ask-art-context-return{width:100%}.ask-art-return-float{right:12px;bottom:12px;max-width:calc(100vw - 24px);font-size:.74rem}}
        `;
        document.head.appendChild(style);
    }

    function createContext(art, topic, returnUrl) {
        const card = document.querySelector('.ask-study-card');
        if (!card || card.querySelector('[data-focuschrist-art-context]')) return;

        const context = document.createElement('aside');
        context.className = 'ask-art-context';
        context.setAttribute('data-focuschrist-art-context', 'true');
        context.setAttribute('aria-label', 'Artwork study context');

        const copy = document.createElement('div');
        const kicker = document.createElement('span');
        kicker.className = 'ask-art-context-kicker';
        kicker.textContent = 'Studying artwork';
        copy.appendChild(kicker);

        const title = document.createElement('strong');
        title.className = 'ask-art-context-title';
        title.textContent = art;
        copy.appendChild(title);

        if (topic && topic.toLowerCase() !== art.toLowerCase()) {
            const topicLine = document.createElement('span');
            topicLine.className = 'ask-art-context-topic';
            topicLine.textContent = 'Study focus: ' + topic;
            copy.appendChild(topicLine);
        }
        context.appendChild(copy);

        const back = document.createElement('a');
        back.className = 'ask-art-context-return';
        back.href = returnUrl;
        back.textContent = 'Return to this artwork';
        back.setAttribute('data-focuschrist-art-return', 'true');
        context.appendChild(back);
        card.insertBefore(context, card.firstChild);
    }

    function createPersistentReturn(art, returnUrl) {
        if (document.querySelector('[data-focuschrist-art-return-float]')) return;
        const back = document.createElement('a');
        back.className = 'ask-art-return-float';
        back.href = returnUrl;
        back.textContent = '← Return to artwork: ' + art;
        back.setAttribute('data-focuschrist-art-return-float', 'true');
        document.body.appendChild(back);
    }

    function prefillQuestion(art, topic) {
        const input = document.getElementById('userInput');
        if (!input || input.value.trim()) return;
        const subject = topic || art;
        input.value = 'Help me study the artwork "' + art + '". What do the scriptures and official Church resources teach about ' + subject + '?';
        input.setAttribute('data-focuschrist-art-prefill', 'true');
        window.setTimeout(function () {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }, 240);
    }

    function init() {
        const params = new URLSearchParams(window.location.search);
        const art = (params.get('art') || '').trim();
        if (!art) return;
        const topic = (params.get('topic') || art).trim();
        const returnUrl = safeReturnUrl(params.get('return'), art);
        ensureStyles();
        createContext(art, topic, returnUrl);
        createPersistentReturn(art, returnUrl);
        prefillQuestion(art, topic);
        document.documentElement.setAttribute('data-focuschrist-art-ask-context', 'ready');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
