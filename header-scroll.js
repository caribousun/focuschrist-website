/* Opaque navigation with a subtle reading-state edge. */
(function () {
    'use strict';
    if (window.focusChristHeaderScrollReady) return;
    window.focusChristHeaderScrollReady = true;
    var pending = false;

    // Keep native fragment/history behavior, then align the subject's beginning
    // after page controllers and responsive layout have finished their work.
    // Some caption headings deliberately retain their public bookmark IDs while
    // their pictured subject begins earlier. Only explicit mappings move those
    // bookmarks; a paragraph/source bookmark must never jump to a whole chapter.
    var landingToken = 0;
    var initialLandingAllowed = true;
    function targetForHash(hash) {
        var id;
        try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return null; }
        if (!id) return null;
        var target = document.getElementById(id);
        if (!target) return null;
        var starts = document.querySelectorAll('[data-fc-section-start]');
        for (var i = 0; i < starts.length; i++) {
            if (starts[i].getAttribute('data-fc-section-start').split(/\s+/).indexOf(id) !== -1) return starts[i];
        }
        return target;
    }
    function landingOffset() {
        var header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        if (!header) return 16;
        var position = window.getComputedStyle(header).position;
        // Timelines retain their sticky phone header; other phone pages use a
        // header in normal flow. Measure the actual rule, not a viewport guess.
        return (position === 'fixed' || position === 'sticky' ? Math.ceil(header.getBoundingClientRect().height) : 0) + 16;
    }
    function canAlign(target) {
        var dialogs = document.querySelectorAll('dialog[open], [role="dialog"][aria-modal="true"]');
        for (var i = 0; i < dialogs.length; i++) {
            // Legacy viewers keep their modal semantics while display:none.
            // Only a rendered, visible overlay owns the reader's current view.
            if (dialogs[i].getClientRects().length && window.getComputedStyle(dialogs[i]).visibility !== 'hidden') return false;
        }
        return target && !/\/ask\.html$/.test(location.pathname) &&
            !target.closest('dialog, [role="dialog"], [hidden], .nav, [data-timeline-pane]') &&
            target.getClientRects().length;
    }
    function alignLanding(hash, event) {
        var token = ++landingToken;
        function align() {
            if (token !== landingToken || (event && event.defaultPrevented) || location.hash !== hash) return;
            var target = targetForHash(hash);
            if (!canAlign(target)) return;
            var top = window.scrollY + target.getBoundingClientRect().top - landingOffset();
            var maximum = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
            var destination = Math.max(0, Math.min(top, maximum));
            if (Math.abs(window.scrollY - destination) > 1) window.scrollTo({ top: destination, behavior: 'instant' });
        }
        requestAnimationFrame(function () { requestAnimationFrame(align); });
        // A bounded follow-up covers font/image and disclosure layout shifts.
        // Any reader interaction or newer navigation cancels this landing.
        [120, 350, 800].forEach(function (delay) { window.setTimeout(align, delay); });
    }
    function cancelLanding() { landingToken++; initialLandingAllowed = false; }
    window.addEventListener('wheel', cancelLanding, { passive: true });
    window.addEventListener('touchmove', cancelLanding, { passive: true });
    window.addEventListener('pointerdown', cancelLanding, { passive: true });
    window.addEventListener('keydown', function (event) {
        if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' ', 'Tab', 'Escape'].indexOf(event.key) !== -1) cancelLanding();
    });
    // Native history restores its saved reading position. Programmatic hashes
    // belong to their chapter/map/dialog controller, not this click enhancer.
    function initialLanding() {
        // A restored back/forward page already has the browser's saved reading
        // position. Do not replace it merely because its URL has a fragment.
        var navigation = window.performance && performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
        if (initialLandingAllowed && location.hash && (!navigation || navigation.type === 'navigate')) alignLanding(location.hash);
    }
    window.addEventListener('load', initialLanding, { once: true });
    if (document.readyState === 'complete') initialLanding();

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
        if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self') || link.closest('dialog, [role="dialog"]')) return;
        var url;
        try { url = new URL(link.href, window.location.href); } catch (_) { return; }
        if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash || /\/ask\.html$/.test(location.pathname)) return;
        var target;
        try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); } catch (_) { return; }
        if (!target || target.closest('dialog, [role="dialog"]')) return;
        alignLanding(url.hash, event);
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
