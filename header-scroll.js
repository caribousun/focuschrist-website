/* Opaque navigation with a subtle reading-state edge. */
(function () {
    'use strict';
    if (window.focusChristHeaderScrollReady) return;
    window.focusChristHeaderScrollReady = true;
    var pending = false;

    function update() {
        pending = false;
        var header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        if (!header) return;
        header.classList.toggle('fc-header-scrolled', window.scrollY > 24);
    }

    function schedule() {
        if (pending) return;
        pending = true;
        window.requestAnimationFrame(update);
    }

    // Native navigation/history uses the shared instant root scroll behavior.
    // After delegated controllers, softly reveal only a distant content destination.
    var jumpToken = 0;
    var fade = null;
    window.addEventListener('click', function (event) {
        if (event.defaultPrevented || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        var link = event.target.closest && event.target.closest('a[href]');
        if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self') || link.closest('dialog, [role="dialog"], .nav')) return;
        var url;
        try { url = new URL(link.href, window.location.href); } catch (_) { return; }
        if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash || /\/ask\.html$/.test(location.pathname)) return;
        var target;
        try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); } catch (_) { return; }
        if (!target || target.closest('dialog, [role="dialog"]')) return;
        var distance = Math.abs(target.getBoundingClientRect().top);
        if (distance <= Math.max(320, window.innerHeight / 2)) return;
        var token = ++jumpToken;
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                if (token !== jumpToken) return;
                // A chapter, disclosure or study-dialog controller may own this click.
                if (event.defaultPrevented || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
                var content = target.closest('section, article') || target;
                if (content.closest('.nav, dialog, [role="dialog"], [hidden]') || !content.getClientRects().length) return;
                if (typeof content.animate !== 'function') return;
                if (fade) fade.cancel();
                fade = content.animate([{ opacity: 0.72 }, { opacity: 1 }], { duration: 200, easing: 'ease-out' });
            });
        });
    });

    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('pageshow', schedule);
    window.addEventListener('hashchange', schedule);
    window.addEventListener('load', schedule, { once: true });
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', update, { once: true });
    } else {
        update();
    }
})();
