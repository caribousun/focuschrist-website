(function () {
    'use strict';
    const routes = {
    "/art-study/the-living-christ.html": {
        "scene": "#christ-under-countless-stars",
        "image": "/assets/page-art/christ-world/christ-under-countless-stars-full.webp",
        "destination": "#personal-study"
    },
    "/missionary.html": {
        "scene": "#christ-earthquake-community",
        "image": "/assets/page-art/christ-world/christ-earthquake-community-full.webp",
        "destination": "#ways-to-serve"
    },
    "/jesus-christ/miracles-and-compassion.html": {
        "scene": "#christ-hospital-corridor",
        "image": "/assets/page-art/christ-world/christ-hospital-corridor-full.webp",
        "destination": "#next-study"
    },
    "/art-study/be-still.html": {
        "scene": "#christ-caregiver-night",
        "image": "/assets/page-art/christ-world/christ-caregiver-night-full.webp",
        "destination": "#personal-study"
    },
    "/art-study/the-good-shepherd.html": {
        "scene": "#christ-last-bus",
        "image": "/assets/page-art/christ-world/christ-last-bus-full.webp",
        "destination": "#personal-study"
    },
    "/jesus-christ/parables/good-samaritan.html": {
        "scene": "#christ-responder-rest",
        "image": "/assets/page-art/christ-world/christ-responder-rest-full.webp",
        "destination": "#living-the-invitation"
    }
};
    const owned = routes[location.pathname];
    if (!owned) return;
    let cancelAlignment = function () {};
    function alignHeading(heading, hash, focus) {
        cancelAlignment();
        let stopped = false, focused = false;
        const timers = [], frames = [];
        const inputs = ['wheel', 'touchstart', 'touchmove', 'pointerdown', 'keydown'];
        function cancel() {
            stopped = true;
            timers.forEach(clearTimeout);
            frames.forEach(cancelAnimationFrame);
            inputs.forEach(function (name) { window.removeEventListener(name, cancel, true); });
        }
        cancelAlignment = cancel;
        inputs.forEach(function (name) { window.addEventListener(name, cancel, {capture:true,passive:true}); });
        function measure() {
            if (stopped || location.hash !== hash || document.querySelector('dialog[open]') || !heading.isConnected) { cancel(); return; }
            if (!heading.getClientRects().length) return;
            if (focus && !focused) {
                if (!heading.hasAttribute('tabindex')) {
                    heading.setAttribute('tabindex', '-1');
                    heading.addEventListener('blur', function () { heading.removeAttribute('tabindex'); }, {once:true});
                }
                heading.focus({preventScroll:true});
                focused = true;
            }
            const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
            const position = header && getComputedStyle(header).position;
            const clearance = (position === 'fixed' || position === 'sticky' ? Math.ceil(header.getBoundingClientRect().height) : 0) + 16;
            const margin = parseFloat(getComputedStyle(heading).scrollMarginTop) || 0;
            const maximum = Math.max(0, document.documentElement.scrollHeight - innerHeight);
            const top = Math.max(0, Math.min(scrollY + heading.getBoundingClientRect().top - Math.max(clearance, margin), maximum));
            if (Math.abs(scrollY-top)>1) window.scrollTo({top:top,behavior:'instant'});
        }
        frames.push(requestAnimationFrame(function () { frames.push(requestAnimationFrame(measure)); }));
        [120,350,800].forEach(function (delay) { timers.push(setTimeout(function () { measure(); if (delay===800) cancel(); },delay)); });
    }
    document.addEventListener('click', function (event) {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const link = event.target.closest && event.target.closest('a[href]');
        const dialog = link && link.closest('#topicArtworkDetailDialog[open]');
        if (!dialog) return;
        const image = dialog.querySelector('img');
        if (!image || new URL(image.src, location.href).pathname !== owned.image) return;
        const destination = new URL(link.href, location.href);
        if (destination.origin !== location.origin || destination.pathname !== location.pathname || destination.search !== location.search || destination.hash !== owned.destination) return;
        const section = document.getElementById(owned.destination.slice(1));
        const heading = section && section.querySelector('h2');
        if (!heading) return;
        // Keep the native fragment action and chapter handler. Let the existing
        // close listener restore its trigger first, then settle the destination.
        dialog.addEventListener('close', function () {
            alignHeading(heading,owned.destination,true);
        }, {once: true});
        dialog.close();
    }, true);
}());
