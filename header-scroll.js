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
    function isTimelineStoryBookmark(hash) {
        return (location.pathname === '/timelines/life-of-christ-journey-map.html' && hash === '#dTitle') ||
            (location.pathname === '/timelines/willie-and-martin-handcart-map.html' && hash === '#detail-title');
    }
    function isAskContentBookmark(hash) {
        return location.pathname === '/ask.html' && [
            '#ask-study-heading', '#conversation-heading', '#topic-heading',
            '#continue-heading', '#visual-resources-title', '#connected-study'
        ].indexOf(hash) !== -1;
    }
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
        if (isTimelineStoryBookmark(hash)) return target.closest('[data-timeline-pane="detail"]') || target;
        if (isAskContentBookmark(hash)) return target.closest('section') || target;
        return target;
    }
    function landingOffset(target, ownedTimelineLanding) {
        var header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        var position = header && window.getComputedStyle(header).position;
        // Timelines retain their sticky phone header; other phone pages use a
        // header in normal flow. Measure the actual rule, not a viewport guess.
        var offset = (position === 'fixed' || position === 'sticky' ? Math.ceil(header.getBoundingClientRect().height) : 0) + 16;
        if (ownedTimelineLanding && target.closest('[data-timeline-pane]')) {
            var dock = document.querySelector('.timeline-map-dock');
            var dockPosition = dock && window.getComputedStyle(dock).position;
            if (dock && (dockPosition === 'fixed' || dockPosition === 'sticky')) {
                var dockRect = dock.getBoundingClientRect();
                var targetRect = target.getBoundingClientRect();
                // On phones the map stays above the reading pane. A desktop
                // map beside the pane does not cover the subject's beginning.
                if (dockRect.height > 0 && dockRect.left < targetRect.right && dockRect.right > targetRect.left) {
                    // A freshly revealed story may still be below the viewport;
                    // use the dock's pinned top, not its current document position.
                    var dockTop = dockPosition === 'sticky' ? parseFloat(window.getComputedStyle(dock).top) : dockRect.top;
                    if (!Number.isFinite(dockTop)) dockTop = offset - 16;
                    offset = Math.max(offset, Math.ceil(Math.max(0, dockTop) + dockRect.height) + 16);
                }
            }
        }
        return offset;
    }

    // Only Continue controls animate. Ordinary navigation keeps an immediate landing.
    var motionFrame = 0, motionToken = 0;
    var immediateStyle = document.createElement('style');
    immediateStyle.textContent = 'html,.fc-history-chat{scroll-behavior:auto!important}';
    document.head.appendChild(immediateStyle);
    function isContinue(link) {
        return !!link && (link.matches('.fc-unified-continue,.fc-scroll-cue,.fc-mobile-scroll-cue,.fc-art-continue,.fc-covenant-continue,.timeline-opening-continue,.scrollcue') ||
            (link.matches('.fc-button,.cta') && /^Continue(?:\s|$)/i.test(link.textContent.trim())));
    }
    function cancelMotion() {
        motionToken++;
        cancelAnimationFrame(motionFrame);
    }
    function continueTo(target, options) {
        if (!target || !target.isConnected) return;
        options = options || {};
        cancelMotion(); cancelLanding();
        var token = motionToken;
        for (var parent = target.parentElement; parent; parent = parent.parentElement) {
            if (parent.tagName === 'DETAILS') parent.open = true;
        }
        // Focus without scrolling so keyboard reading resumes at the destination.
        if (options.focus !== false) {
            if (!target.hasAttribute('tabindex')) {
                target.setAttribute('tabindex', '-1');
                target.addEventListener('blur', function () { target.removeAttribute('tabindex'); }, { once: true });
            }
            target.focus({ preventScroll: true });
        }
        var start = window.scrollY, started = performance.now();
        var duration = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 560;
        function destination() {
            var offset = typeof options.offset === 'function' ? options.offset() : options.offset;
            if (offset == null) offset = Math.max(landingOffset(target, false), parseFloat(getComputedStyle(target).scrollMarginTop) || 0);
            return Math.max(0, Math.min(window.scrollY + target.getBoundingClientRect().top - offset,
                Math.max(0, document.documentElement.scrollHeight - window.innerHeight)));
        }
        function step(now) {
            if (token !== motionToken || !target.isConnected || document.querySelector('dialog[open]')) return;
            var progress = duration ? Math.min(1, (now - started) / duration) : 1;
            var eased = progress < .5 ? 4 * progress * progress * progress : 1 - Math.pow(-2 * progress + 2, 3) / 2;
            window.scrollTo({ top: start + (destination() - start) * eased, behavior: 'instant' });
            if (progress < 1) motionFrame = requestAnimationFrame(step);
        }
        if (duration) motionFrame = requestAnimationFrame(step); else step(started);
    }
    window.FocusContinueScroll = { to: continueTo, isContinue: isContinue, cancel: cancelMotion };
    window.addEventListener('click', function (event) {
        var link = event.target.closest && event.target.closest('a[href]');
        if (link && isContinue(link)) cancelLanding();
        else cancelMotion();
    }, true);
    ['wheel', 'touchstart', 'touchmove', 'pointerdown', 'popstate', 'hashchange', 'resize'].forEach(function (type) {
        window.addEventListener(type, cancelMotion, { capture: true, passive: true });
    });
    window.addEventListener('keydown', function (event) {
        if (['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' ','Tab','Escape'].indexOf(event.key) !== -1) cancelMotion();
    }, true);

    function canAlign(target, generatedSkip, storyBookmark, askContentBookmark) {
        var dialogs = document.querySelectorAll('dialog[open], [role="dialog"][aria-modal="true"]');
        for (var i = 0; i < dialogs.length; i++) {
            // Legacy viewers keep their modal semantics while display:none.
            // Only a rendered, visible overlay owns the reader's current view.
            if (dialogs[i].getClientRects().length && window.getComputedStyle(dialogs[i]).visibility !== 'hidden') return false;
        }
        return target && (generatedSkip || askContentBookmark || !/\/ask\.html$/.test(location.pathname)) &&
            !target.closest('dialog, [role="dialog"], [hidden], .nav') &&
            (generatedSkip || storyBookmark || !target.closest('[data-timeline-pane]')) &&
            target.getClientRects().length;
    }
    function alignLanding(hash, event, generatedSkip) {
        var token = ++landingToken;
        function align() {
            if (token !== landingToken || (event && event.defaultPrevented && !generatedSkip) || location.hash !== hash) return;
            var target = targetForHash(hash);
            var storyBookmark = isTimelineStoryBookmark(hash) && target && target.matches('[data-timeline-pane="detail"]');
            if (storyBookmark) {
                // These two published heading bookmarks belong to a story pane.
                // Let its controller reveal the pane before positioning.
                if (!window.TimelineWorkspace || typeof window.TimelineWorkspace.showStory !== 'function') return;
                window.TimelineWorkspace.showStory();
                target.scrollTop = 0;
            }
            if (!canAlign(target, generatedSkip, storyBookmark, isAskContentBookmark(hash))) return;
            var top = window.scrollY + target.getBoundingClientRect().top - landingOffset(target, generatedSkip || storyBookmark);
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
    // Continue alone animates after destination-specific controllers.
    window.addEventListener('click', function (event) {
        if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        var link = event.target.closest && event.target.closest('a[href]');
        if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self') || link.closest('dialog, [role="dialog"]')) return;
        var url;
        try { url = new URL(link.href, window.location.href); } catch (_) { return; }
        if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash) return;
        var target;
        try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); } catch (_) { return; }
        if (!target || target.closest('dialog, [role="dialog"]')) return;
        // The generated skip control already focuses main and replaces history.
        // Correct only its landing; other prevented controllers retain ownership.
        var generatedSkip = link.getAttribute('data-focuschrist-skip-link') === 'true' && target.matches('main, [role="main"]');
        if (event.defaultPrevented && !generatedSkip) return;
        if (!isContinue(link) && /\/ask\.html$/.test(location.pathname) && !generatedSkip && !isAskContentBookmark(url.hash)) return;
        if (isContinue(link)) {
            var continuation = targetForHash(url.hash);
            if (!continuation) return;
            event.preventDefault();
            if (location.hash !== url.hash) history.pushState(null, '', url.hash);
            continueTo(continuation);
            return;
        }
        cancelMotion();
        alignLanding(url.hash, event, generatedSkip);

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
