/* Open the historical chapter surrounding a fragment without owning study controls. */
(function () {
    'use strict';
    let activeStory = null;
    function revealFragment(hash) {
        if (!hash || hash === '#') return;
        let id;
        try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return; }
        const target = document.getElementById(id);
        if (!target) return;
        let changed = false;
        for (let ancestor = target; ancestor; ancestor = ancestor.parentElement) {
            if (ancestor.tagName === 'DETAILS' && !ancestor.open) {
                ancestor.open = true;
                changed = true;
            }
        }
        if (changed) window.requestAnimationFrame(function () {
            target.scrollIntoView({ block: 'start', behavior: 'auto' });
        });
    }
    function revealCurrent() { revealFragment(window.location.hash); }
    window.addEventListener('hashchange', revealCurrent);
    document.addEventListener('click', function (event) {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const element = event.target.closest ? event.target : event.target.parentElement;
        if (!element) return;
        const trigger = element.closest('[data-artwork-detail]');
        const dialog = document.getElementById('artworkDetailDialog');
        if (trigger) {
            activeStory = null;
            if (!trigger.dataset.artworkDetail.startsWith('pioneer-story-') || !dialog || !dialog.open) return;
            const card = trigger.closest('.pioneer-story-card');
            const copy = document.getElementById('artworkDetailCopy');
            if (!card || !copy) return;
            activeStory = trigger.dataset.artworkDetail;
            const oldLinks = copy.querySelector('[data-pioneer-story-sources]');
            if (oldLinks) oldLinks.remove();
            const oldScriptures = copy.querySelector('[data-pioneer-scripture-links]');
            if (oldScriptures) oldScriptures.remove();
            const reflection = document.createElement('p');
            reflection.setAttribute('data-pioneer-scripture-links', '');
            reflection.appendChild(document.createTextNode('Reflect with '));
            const scriptureURLs = new Set();
            function addScripture(label, href) {
                const link = document.createElement('a');
                link.href = href;
                link.textContent = label;
                reflection.appendChild(link);
                scriptureURLs.add(link.href);
            }
            addScripture('Matthew 25:35–40', 'https://www.churchofjesuschrist.org/study/scriptures/nt/matt/25?lang=eng&id=p35-p40#p35');
            reflection.appendChild(document.createTextNode(' and '));
            addScripture('Mosiah 18:8–9', 'https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah/18?lang=eng&id=p8-p9#p8');
            reflection.appendChild(document.createTextNode('. Whose burden can you help carry?'));
            card.querySelectorAll('.pioneer-story-copy a[href*="/study/scriptures/"]').forEach(function (link) {
                if (scriptureURLs.has(link.href)) return;
                scriptureURLs.add(link.href);
                reflection.appendChild(document.createTextNode(' '));
                reflection.appendChild(link.cloneNode(true));
            });
            copy.appendChild(reflection);
            const primarySource = document.getElementById('artworkDetailSource');
            const links = Array.from(card.querySelectorAll('.pioneer-source-links a[href]')).filter(function (link) {
                return !primarySource || link.href !== primarySource.href;
            });
            if (links.length) {
                const paragraph = document.createElement('p');
                paragraph.className = 'pioneer-source-links';
                paragraph.setAttribute('data-pioneer-story-sources', activeStory);
                links.forEach(function (link) { paragraph.appendChild(link.cloneNode(true)); });
                copy.appendChild(paragraph);
            }
            return;
        }
        const returnLink = element.closest('#artworkDetailStudy');
        if (!activeStory || !returnLink || !dialog || !dialog.open || event.defaultPrevented) return;
        let destination;
        try { destination = new URL(returnLink.href, window.location.href); } catch (_) { return; }
        if (destination.origin !== window.location.origin || destination.pathname !== window.location.pathname || !destination.hash) return;
        let target;
        try { target = document.getElementById(decodeURIComponent(destination.hash.slice(1))); } catch (_) { return; }
        if (!target || target.id !== activeStory) return;
        event.preventDefault();
        dialog.addEventListener('close', function () {
            window.requestAnimationFrame(function () {
                // Preserve a gallery query and let the shared close handler restore focus first.
                window.location.hash = destination.hash;
                revealFragment(destination.hash);
                target.scrollIntoView({ block: 'start', behavior: 'auto' });
            });
        }, { once: true });
        dialog.close();
        activeStory = null;
    });
    document.addEventListener('click', function (event) {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const link = event.target.closest && event.target.closest('a[href]');
        if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
        // Leave the existing capture-phase controller and its response links untouched.
        if (link.closest('[data-focus-expand]')) return;
        let url;
        try { url = new URL(link.href, window.location.href); } catch (_) { return; }
        if (url.origin !== window.location.origin || url.pathname !== window.location.pathname || url.search !== window.location.search) return;
        revealFragment(url.hash);
    });
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', revealCurrent, { once: true });
    else revealCurrent();
})();
