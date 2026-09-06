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
