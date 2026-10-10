/* Open the original artwork controller in its original document and CSS cascade.
 * This file is loaded only for an explicit gallery deep link. */
(async function () {
    'use strict';
    const params = new URLSearchParams(location.search);
    // Resolve only known retired sources; the catalog and page checks still apply.
    const sourceAliases = new Map([
        ['source-44bc8f90e9cf', 'source-0f854bc93cec'],
        ['source-b8f1acb4ee67', 'source-5ea3c750ad6d'],
        ['source-d203f8844981', 'source-41ace1913814'],
        ['source-b8fb45227bb3', 'source-0dadddbb503d'],
        ['source-9ef33a38a3ec', 'source-d8e9ad0fdf7c'],
        ['source-6d9341ce7a52', 'source-be42ad339302'],
        ['source-8dace3b6bf78', 'source-4a4ae352d87f'],
        ['source-94d28fae2282', 'source-6cd5e5535101'],
        ['source-a6b610e8d1ce', 'source-85cb8f284453'],
        ['source-e30c8ddd579a', 'source-d1ce88bbb045'],
        ['source-a3b8e155238a', 'source-12af89590691'],
        ['source-0b724121e66b', 'source-5ea3c750ad6d'],
        ['source-05cf7c0e2b6a', 'source-12af89590691'],
        ['source-5a24b826f3f4', 'source-0dadddbb503d']
    ]);
    const supplied = params.get('gallery-art') || params.get('gallery-position');
    const requested = sourceAliases.get(supplied) || supplied;
    if (!requested) return;
    let embedded = false;
    try { embedded = params.get('gallery-embed') === '1' && parent !== window && parent.location.origin === location.origin && parent.location.pathname.endsWith('/art-gallery.html'); } catch (_) {}
    function tell(action, extra) { if (embedded) parent.postMessage(Object.assign({ channel: 'focuschrist-art-gallery', action }, extra || {}), location.origin); }
    try {
        const response = await fetch('/art-gallery.json?v=20261010-emma-identity-links-1');
        if (!response.ok) throw new Error('Gallery index unavailable');
        const catalog = await response.json();
        const source = catalog.artworks.flatMap(art => art.occurrences).find(item => item.id === requested);
        if (!source || source.page !== (location.pathname === '/' ? '/index.html' : location.pathname)) throw new Error('Unknown artwork source');
        const trigger = document.querySelector(source.selector);
        if (!trigger) throw new Error('Artwork no longer on this page');
        const sensitiveGate = trigger.closest('details.atonement-sensitive');
        if (sensitiveGate) {
            // A shared/deep link must never count as consent to reveal the scene.
            if (embedded) { tell('navigate', {url: new URL(source.page + '#' + sensitiveGate.id, location.origin).href}); return; }
            sensitiveGate.open = false;
            sensitiveGate.scrollIntoView({block: 'center', behavior: 'instant'});
            sensitiveGate.querySelector('summary').focus({preventScroll: true});
            return;
        }
        if (params.has('gallery-position')) {
            trigger.scrollIntoView({block: 'center', behavior: 'instant'});
            trigger.focus({preventScroll: true});
            return;
        }
        const nativeSelector = {hero: '#heroDetailDialog', artwork: '#artworkDetailDialog', topic: '#topicArtworkDetailDialog', missionary: '#missionaryDetailDialog', legacy: '#imageModal', full: '.fc-full-image-viewer'}[source.kind];
        // Wait only for the owning controller; never repeatedly click an ambiguous action.
        const deadline = Date.now() + 10000;
        while (!document.querySelector(nativeSelector) || (source.kind === 'topic' && !trigger.hasAttribute('data-topic-artwork-detail')) || (source.kind === 'legacy' && !document.documentElement.hasAttribute('data-focuschrist-art-study-router'))) {
            if (Date.now() > deadline) throw new Error('Artwork controller unavailable');
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        if (!embedded) trigger.scrollIntoView({block: 'center', behavior: 'instant'});
        trigger.click();
        const panel = document.querySelector(nativeSelector);
        if (!(panel.open || panel.classList.contains('active'))) throw new Error('Original artwork panel did not open');
        document.documentElement.dataset.galleryArtworkReady = requested;
        if (!embedded) return;
        const style = document.createElement('style');
        style.textContent = 'body > * { visibility:hidden; } dialog, [role="dialog"], #imageModal { visibility:visible; } .fc-gallery-full-actions {position:absolute;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:10px;max-width:calc(100% - 28px);padding:10px;background:var(--fc-bg);border-radius:16px;}';
        document.head.appendChild(style);
        if (source.kind === 'legacy') panel.querySelector('[data-focuschrist-art-study-button]')?.click();
        let actions = panel.querySelector('.fc-artwork-detail-actions, .fc-missionary-detail-actions, .fc-art-study-links');
        if (source.kind === 'full') { actions = document.createElement('div'); actions.className = 'fc-gallery-full-actions'; panel.appendChild(actions); }
        const original = new URL(location.href); original.searchParams.delete('gallery-embed');
        original.searchParams.set('gallery-art', source.id);
        // Legacy Art also writes its own caption query; one source ID must be the
        // only restoration authority after moving to the next/previous picture.
        if (source.kind === 'legacy') original.searchParams.delete('art');
        if (actions) {
            const link = document.createElement('a'); link.href = original.href; link.className = 'fc-button'; link.textContent = 'View in Original Study'; link.dataset.galleryOriginal = '';
            actions.appendChild(link);
            const share = document.createElement(source.kind === 'legacy' ? 'a' : 'button');
            if (source.kind === 'legacy') {
                share.href = parent.location.href; share.setAttribute('role', 'button');
                share.addEventListener('keydown', event => { if (event.key === ' ') { event.preventDefault(); share.click(); } });
            } else share.type = 'button';
            share.className = 'fc-button'; share.textContent = 'Copy Picture Link'; share.dataset.galleryShare = '';
            share.addEventListener('click', event => { event.preventDefault(); tell('share'); }); actions.appendChild(share);
            window.addEventListener('message', event => {
                if (event.origin !== location.origin || event.source !== parent || event.data?.channel !== 'focuschrist-art-gallery') return;
                if (event.data.action === 'shared') { share.textContent = 'Link Copied'; setTimeout(() => { share.textContent = 'Copy Picture Link'; }, 2500); }
                if (event.data.action === 'share-fallback') {
                    const input = document.createElement('input'); input.type = 'text'; input.readOnly = true; input.value = event.data.url; input.setAttribute('aria-label', 'Picture link — copy to share'); actions.appendChild(input); input.focus(); input.select();
                }
            });
        }
        document.addEventListener('click', event => {
            const link = event.target.closest('a[href]');
            if (link?.hasAttribute('data-gallery-share')) return;
            const resume = event.target.closest('[data-artwork-detail-continue]');
            if (resume) {
                event.preventDefault(); event.stopImmediatePropagation();
                const lesson = new URL(original.href); lesson.searchParams.delete('gallery-art'); lesson.searchParams.set('gallery-position', requested);
                tell('navigate', {url: lesson.href}); return;
            }
            if (!link || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            const url = new URL(link.href);
            if (url.origin !== location.origin || !/\.html$/.test(url.pathname) || link.hasAttribute('data-full-image-viewer')) return;
            event.preventDefault(); event.stopImmediatePropagation();
            url.searchParams.delete('gallery-embed');
            if (link.hasAttribute('data-topic-art-continue')) url.searchParams.delete('gallery-art');
            tell('navigate', {url: url.href});
        }, true);
        if (source.kind === 'legacy') {
            // The legacy Art viewer owns its own close and scripture drawer.
            new MutationObserver(() => { if (!panel.classList.contains('active')) tell('close'); }).observe(panel, {attributes:true, attributeFilter:['class']});
            const extras = actions ? Array.from(actions.querySelectorAll('[data-gallery-original], [data-gallery-share]')) : [];
            const drawer = panel.querySelector('[data-focuschrist-art-study-drawer]');
            if (drawer) new MutationObserver(() => {
                const links = drawer.querySelector('.fc-art-study-links');
                if (!links || links.querySelector('[data-gallery-original]')) return;
                const image = panel.querySelector('#modalImage');
                const selected = catalog.artworks.flatMap(art => art.occurrences).find(item => {
                    if (item.kind !== 'legacy' || item.page !== source.page) return false;
                    const thumb = document.querySelector(item.selector + ' img');
                    return thumb && image && (thumb.src === image.src || new URL(thumb.dataset.fullSrc || thumb.src, location.href).href === image.src);
                });
                if (selected) {
                    original.searchParams.set('gallery-art', selected.id);
                    extras[0].href = original.href;
                    tell('selected', {source: selected.id});
                }
                extras.forEach(element => links.appendChild(element));
            }).observe(drawer, {childList:true, subtree:true});
        } else panel.addEventListener('close', () => tell('close'));
        tell('ready');
    } catch (error) {
        document.documentElement.dataset.galleryArtworkError = error.message;
        tell('error');
        if (!embedded) {
            const note = document.createElement('p'); note.className = 'fc-gallery-entry'; note.setAttribute('role', 'status'); note.textContent = 'This artwork link could not open automatically. You can still browse the pictures in this study.';
            (document.querySelector('main') || document.body).prepend(note);
        }
    }
}());
