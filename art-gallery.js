(function () {
    'use strict';
    const grid = document.getElementById('artGalleryGrid');
    const search = document.getElementById('artGallerySearch');
    const category = document.getElementById('artGalleryCategory');
    const count = document.getElementById('artGalleryCount');
    const dialog = document.getElementById('artGalleryDialog');
    const frame = document.getElementById('artGalleryFrame');
    const loading = document.getElementById('artGalleryLoading');
    const fallback = document.getElementById('artGalleryFallback');
    let artworks = [], returnFocus = null, timer, active = null;
    const clean = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    function originalURL(source) {
        const url = new URL(source.page, location.origin);
        url.searchParams.set('gallery-art', source.id);
        return url;
    }
    function reset() {
        clearTimeout(timer);
        frame.src = 'about:blank';
        active = null;
        document.body.classList.remove('fc-dialog-open');
        grid.removeAttribute('aria-busy');
        const url = new URL(location.href); url.searchParams.delete('picture'); history.replaceState(null, '', url);
        render();
        if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
    }
    function close() { if (dialog.open) dialog.close(); else reset(); }
    function show() {
        if (!dialog.open) dialog.showModal();
        document.body.classList.add('fc-dialog-open');
    }
    function open(art, trigger, source) {
        source = source || art.occurrences[0];
        active = { art, source };
        returnFocus = trigger;
        const url = originalURL(source);
        fallback.href = url.href;
        frame.title = art.title + ' — artwork and study';
        frame.hidden = true;
        loading.hidden = false;
        document.getElementById('artGalleryLoadingText').textContent = 'Opening ' + art.title + '…';
        // Keep the gallery visible until the original panel is ready, avoiding
        // a flash of the recovery controls during an ordinary picture opening.
        grid.setAttribute('aria-busy', 'true');
        count.textContent = 'Opening ' + art.title + '…';
        const share = new URL(location.href);
        share.searchParams.set('picture', art.id);
        history.replaceState(null, '', share);
        url.searchParams.set('gallery-embed', '1');
        frame.src = url.href;
        clearTimeout(timer);
        timer = setTimeout(function () {
            document.getElementById('artGalleryLoadingText').textContent = 'This picture is taking a little longer. You can open its original study below.';
            show();
        }, 15000);
    }
    function render() {
        const terms = clean(search.value).split(/\s+/).filter(Boolean);
        let shown = 0;
        grid.querySelectorAll('[data-gallery-card]').forEach(card => {
            const match = (!category.value || JSON.parse(card.dataset.categories).includes(category.value))
                && terms.every(term => card.dataset.search.includes(term));
            card.hidden = !match;
            if (match) shown++;
        });
        count.textContent = shown + (shown === 1 ? ' artwork' : ' artworks') + (shown !== artworks.length ? ' of ' + artworks.length : '');
        document.getElementById('artGalleryEmpty').hidden = shown !== 0;
    }
    search.addEventListener('input', render);
    category.addEventListener('change', render);
    document.getElementById('artGalleryReset').addEventListener('click', function () {
        search.value = ''; category.value = ''; render(); search.focus();
    });
    document.querySelectorAll('[data-gallery-close]').forEach(button => button.addEventListener('click', close));
    dialog.addEventListener('close', reset);
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && active && !dialog.open) { event.preventDefault(); close(); }
    });
    window.addEventListener('message', async function (event) {
        if (event.origin !== location.origin || event.source !== frame.contentWindow || !active) return;
        const data = event.data;
        if (!data || data.channel !== 'focuschrist-art-gallery') return;
        if (data.action === 'ready') {
            if (frame.contentDocument?.documentElement.dataset.galleryArtworkReady !== active.source.id) return;
            clearTimeout(timer); frame.hidden = false; loading.hidden = true;
            grid.removeAttribute('aria-busy'); render(); show();
            frame.contentWindow.focus();
        } else if (data.action === 'selected') {
            const art = artworks.find(item => item.occurrences.some(source => source.id === data.source));
            if (art) {
                active = {art, source: art.occurrences.find(source => source.id === data.source)};
                const url = new URL(location.href); url.searchParams.set('picture', art.id); history.replaceState(null, '', url);
            }
        } else if (data.action === 'close') close();
        else if (data.action === 'navigate') {
            const url = new URL(data.url, location.origin);
            if (url.origin === location.origin && /\.html$/.test(url.pathname)) location.assign(url.href);
        } else if (data.action === 'share') {
            try {
                await navigator.clipboard.writeText(location.href);
                frame.contentWindow.postMessage({channel: 'focuschrist-art-gallery', action: 'shared'}, location.origin);
            } catch (_) {
                frame.contentWindow.postMessage({channel: 'focuschrist-art-gallery', action: 'share-fallback', url: location.href}, location.origin);
            }
        } else if (data.action === 'error') {
            clearTimeout(timer);
            document.getElementById('artGalleryLoadingText').textContent = 'The artwork panel could not open here. Please visit its original study.';
            show();
        }
    });
    fetch('art-gallery.json').then(response => {
        if (!response.ok) throw new Error('Gallery unavailable');
        return response.json();
    }).then(catalog => {
        artworks = catalog.artworks;
        [...new Set(artworks.flatMap(art => art.categories))].sort().forEach(label => {
            const option = document.createElement('option'); option.value = label; option.textContent = label; category.appendChild(option);
        });
        const fragment = document.createDocumentFragment();
        artworks.forEach(art => {
            const card = document.createElement('article');
            card.className = 'fc-gallery-card'; card.dataset.galleryCard = art.id;
            card.dataset.categories = JSON.stringify(art.categories);
            card.dataset.search = clean([art.title, art.alt, ...art.categories, ...art.occurrences.map(source => source.pageTitle)].join(' '));
            const link = document.createElement('a');
            link.className = 'fc-gallery-picture'; link.href = originalURL(art.occurrences[0]);
            link.setAttribute('aria-label', 'Explore artwork: ' + art.title);
            link.setAttribute('aria-haspopup', 'dialog');
            const image = document.createElement('img');
            image.src = art.thumbnail; image.alt = art.alt || art.title; image.loading = 'lazy'; image.decoding = 'async';
            link.appendChild(image);
            link.addEventListener('click', event => {
                if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                event.preventDefault(); open(art, link);
            });
            const heading = document.createElement('h2'); heading.textContent = art.title;
            const origin = document.createElement('p'); origin.textContent = art.occurrences[0].pageTitle;
            card.append(link, heading, origin);
            if (art.occurrences.length > 1) {
                const details = document.createElement('details');
                const summary = document.createElement('summary'); summary.textContent = 'Also appears in ' + (art.occurrences.length - 1) + ' other ' + (art.occurrences.length === 2 ? 'study' : 'studies');
                details.appendChild(summary);
                art.occurrences.slice(1).forEach(source => {
                    const other = document.createElement('a'); other.href = originalURL(source); other.textContent = source.pageTitle;
                    other.addEventListener('click', event => { if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return; event.preventDefault(); open(art, other, source); });
                    details.appendChild(other);
                });
                card.appendChild(details);
            }
            fragment.appendChild(card);
        });
        grid.replaceChildren(fragment); render();
        const requested = new URLSearchParams(location.search).get('picture');
        if (requested) {
            const art = artworks.find(item => item.id === requested);
            if (art) open(art, grid.querySelector('[data-gallery-card="' + art.id + '"] a'));
            else count.textContent += ' — That shared picture is no longer in the gallery.';
        }
    }).catch(() => { count.textContent = 'The gallery could not load. Please refresh or return to Art & Study.'; });
}());
