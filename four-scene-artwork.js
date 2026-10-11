(function () {
    'use strict';
    const routes = {
        '/answers/divorce-and-faith.html': {
            scene: '#christ-moving-day',
            image: '/assets/page-art/christ-world/christ-moving-day-full.webp',
            destination: '#scripture-study'
        },
        '/answers/are-latter-day-saints-christian.html': {
            scene: '#christ-food-pantry',
            image: '/assets/page-art/christ-world/christ-food-pantry-full.webp',
            destination: '#guided-practice'
        },
        '/answers/faith-in-jesus-christ-during-trials.html': {
            scene: '#christ-homecoming-celebration',
            image: '/assets/page-art/christ-world/christ-homecoming-celebration-full.webp',
            destination: '#continue-study'
        },
        '/art-study/suffer-the-little-children.html': {
            scene: '#christ-children-colorful-day',
            image: '/assets/page-art/christ-world/christ-children-colorful-day-full.webp',
            destination: '#continue-study'
        }
    };
    const owned = routes[location.pathname];
    if (!owned) return;
    let cancelAlignment = function () {}, alignmentHash = '', userCancelledHash = '';
    ['wheel','touchstart','touchmove','pointerdown','keydown'].forEach(function (name) {
        window.addEventListener(name,function () { userCancelledHash = location.hash; cancelAlignment(); },{capture:true,passive:true});
    });
    function alignHeading(heading, hash, focus) {
        cancelAlignment();
        alignmentHash = hash;
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
    function alignOwnedEntry() {
        if (location.hash !== owned.scene || userCancelledHash === location.hash) return;
        const section = document.getElementById(owned.scene.slice(1));
        const heading = section && section.querySelector('h2');
        if (heading) alignHeading(heading,owned.scene,false);
    }
    window.addEventListener('hashchange',function () { userCancelledHash = ''; if(location.hash!==alignmentHash) cancelAlignment(); alignOwnedEntry(); });
    window.addEventListener('resize',alignOwnedEntry);
    window.addEventListener('load',alignOwnedEntry);
    if (document.readyState==='complete') alignOwnedEntry();
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
