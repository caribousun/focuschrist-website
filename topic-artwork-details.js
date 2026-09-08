(function () {
    'use strict';

    function captionParagraphs(caption) {
        if (!caption) return [];
        const excluded = '.fc-study-visual-label, .fc-marriage-era__number, .fc-study-visual-sources, .fc-study-visual-actions';
        function proseOnly(paragraph) {
            if (paragraph.matches(excluded)) return false;
            const words = paragraph.cloneNode(true);
            words.querySelectorAll('a').forEach(function (link) { link.remove(); });
            return /[\p{L}\p{N}]/u.test(words.textContent);
        }
        function safeClone(node) {
            const clone = node.cloneNode(true);
            clone.querySelectorAll('script,style,iframe,object,embed').forEach(function (child) { child.remove(); });
            [clone].concat(Array.from(clone.querySelectorAll('*'))).forEach(function (child) {
                Array.from(child.attributes).forEach(function (attribute) {
                    if (attribute.name === 'id' || /^on/i.test(attribute.name)) child.removeAttribute(attribute.name);
                });
                if (child.tagName === 'A') {
                    try {
                        const url = new URL(child.getAttribute('href'), document.baseURI);
                        if (!['http:', 'https:'].includes(url.protocol)) child.removeAttribute('href');
                    } catch (error) { child.removeAttribute('href'); }
                }
            });
            return clone;
        }
        const paragraphs = Array.from(caption.querySelectorAll('p')).filter(proseOnly).map(safeClone);
        if (paragraphs.length) return paragraphs;
        const fallback = safeClone(caption);
        fallback.querySelectorAll('h2,h3,' + excluded).forEach(function (node) { node.remove(); });
        fallback.querySelectorAll('p').forEach(function (p) { if (!proseOnly(p)) p.remove(); });
        if (!fallback.textContent.trim()) return [];
        const paragraph = document.createElement('p');
        paragraph.append.apply(paragraph, Array.from(fallback.childNodes));
        return [paragraph];
    }

    function initialize() {
        if (typeof HTMLDialogElement === 'undefined' || document.getElementById('topicArtworkDetailDialog')) return;
        const main = document.querySelector('main');
        if (!main) return;
        const pictures = Array.from(main.querySelectorAll('figure > a[href], .fc-marriage-era__art[href]')).filter(function (link) {
            return link.querySelector('img') && !link.closest('.fc-resource-card, dialog')
                && !link.hasAttribute('data-artwork-detail') && !link.hasAttribute('data-hero-viewer');
        });
        if (!pictures.length) return;

        const dialog = document.createElement('dialog');
        dialog.id = 'topicArtworkDetailDialog';
        dialog.className = 'fc-artwork-detail-dialog fc-topic-artwork-detail';
        dialog.setAttribute('aria-labelledby', 'topicArtworkDetailTitle');
        dialog.innerHTML = '<div class="fc-artwork-detail-shell"><button class="fc-artwork-detail-close" type="button" data-topic-art-close aria-label="Close artwork study"></button><div class="fc-artwork-detail-media"><img alt=""></div><div class="fc-artwork-detail-body"><p class="fc-eyebrow">Explore and study</p><h2 id="topicArtworkDetailTitle"></h2><div class="fc-artwork-detail-copy" tabindex="0" role="region" aria-label="About this artwork"></div><div class="fc-actions fc-artwork-detail-actions" aria-label="Artwork study options"></div></div></div>';
        document.body.appendChild(dialog);
        const image = dialog.querySelector('img');
        const title = dialog.querySelector('h2');
        const copy = dialog.querySelector('.fc-artwork-detail-copy');
        const actions = dialog.querySelector('.fc-artwork-detail-actions');
        const close = dialog.querySelector('[data-topic-art-close]');
        let returnFocus = null;
        let continueTarget = null;

        function officialLinks(container) {
            if (!container) return [];
            return Array.from(container.querySelectorAll('a[href]')).filter(function (link) {
                try {
                    const url = new URL(link.href);
                    return url.hostname === 'www.churchofjesuschrist.org' && !link.querySelector('img');
                } catch (error) { return false; }
            });
        }

        function readingTarget(figure, index) {
            const section = figure.closest('.fc-marriage-era, section');
            let target = section && Array.from(section.querySelectorAll('h2,h3')).find(function (heading) {
                return !heading.closest('figure, .fc-resource-card');
            });
            if (!target) {
                const headings = Array.from(main.querySelectorAll('h2,h3')).filter(function (heading) {
                    return !heading.closest('figure, .fc-resource-card') && (heading.compareDocumentPosition(figure) & Node.DOCUMENT_POSITION_FOLLOWING);
                });
                target = headings[headings.length - 1] || main;
            }
            if (!target.id) target.id = 'topic-art-reading-' + index;
            target.setAttribute('data-topic-reading-target', '');
            return target;
        }

        function recordFor(trigger, index) {
            const figure = trigger.closest('figure, .fc-marriage-era');
            const caption = figure.querySelector('figcaption, .fc-marriage-era__copy');
            const target = readingTarget(figure, index);
            const heading = caption && caption.querySelector('h2,h3');
            const record = { title: heading ? heading.textContent.trim() : target.textContent.trim(), paragraphs: [], sources: [], target: target };
            record.paragraphs = captionParagraphs(caption);
            let sources = officialLinks(caption);
            if (!sources.length) sources = officialLinks(figure.closest('.fc-marriage-era'));
            if (!sources.length) sources = officialLinks(figure.closest('section, .gc-intro'));
            // The opening grief illustration precedes the John 11 study it introduces.
            if (!sources.length && location.pathname.endsWith('/grief-and-faith.html')) sources = officialLinks(document.getElementById('jesus-wept'));
            if (!sources.length && figure.closest('.gc-intro')) sources = officialLinks(main).filter(function (link) { return new URL(link.href).pathname === '/study/general-conference'; }).slice(0, 1);
            const seen = new Set();
            sources.forEach(function (link) {
                if (seen.has(link.href) || record.sources.length >= 3) return;
                seen.add(link.href);
                record.sources.push({ href: link.href, label: link.textContent.trim() || 'Read the official source' });
            });
            return record;
        }

        function pill(label, href, primary) {
            const link = document.createElement('a');
            link.className = 'fc-button' + (primary ? ' fc-button--primary' : '');
            link.textContent = label;
            link.href = href;
            actions.appendChild(link);
            return link;
        }

        function showStudy(trigger, record) {
            title.textContent = record.title;
            image.src = trigger.href;
            image.alt = trigger.dataset.fullImageAlt || trigger.querySelector('img').alt;
            copy.replaceChildren();
            record.paragraphs.forEach(function (paragraph) {
                copy.appendChild(paragraph.cloneNode(true));
            });
            actions.replaceChildren();
            record.sources.forEach(function (source, index) {
                const link = pill(source.label, source.href, index === 0);
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                if (new URL(source.href).pathname.includes('/study/scriptures/')) link.classList.add('fc-inline-scripture');
                link.dataset.topicArtSource = '';
            });
            const full = pill('View Full-Size Image', trigger.href);
            full.setAttribute('data-full-image-viewer', '');
            full.setAttribute('aria-haspopup', 'dialog');
            full.dataset.fullImageAlt = image.alt;

            const related = Array.from(main.querySelectorAll('#continue-study a[href], #conference-pathways a[href]')).find(function (link) {
                const url = new URL(link.href);
                return url.origin === location.origin && url.pathname !== location.pathname && !link.querySelector('img');
            });
            if (related) pill(related.textContent.trim() || 'Continue related study', related.href);

            const resume = pill('Continue Lesson', '#' + record.target.id);
            resume.dataset.topicArtContinue = '';
            resume.addEventListener('click', function (event) {
                if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                event.preventDefault();
                continueTarget = record.target;
                dialog.close();
            });
            const done = document.createElement('button');
            done.className = 'fc-button';
            done.type = 'button';
            done.textContent = 'Close';
            done.addEventListener('click', function () { dialog.close(); });
            actions.appendChild(done);
            returnFocus = trigger;
            continueTarget = null;
            document.body.classList.add('fc-dialog-open');
            dialog.showModal();
            dialog.scrollTop = 0;
            close.focus({ preventScroll: true });
        }

        pictures.forEach(function (trigger, index) {
            const record = recordFor(trigger, index);
            if (!record.sources.length || !record.paragraphs.length) return;
            trigger.removeAttribute('data-full-image-viewer');
            trigger.setAttribute('data-topic-artwork-detail', '');
            trigger.setAttribute('aria-haspopup', 'dialog');
            trigger.setAttribute('aria-label', 'Explore artwork: ' + record.title);
            trigger.addEventListener('click', function (event) {
                if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                event.preventDefault();
                showStudy(trigger, record);
            });
        });
        close.addEventListener('click', function () { dialog.close(); });
        dialog.addEventListener('click', function (event) { if (event.target === dialog) dialog.close(); });
        dialog.addEventListener('cancel', function (event) { event.stopPropagation(); });
        dialog.addEventListener('close', function () {
            if (!document.querySelector('dialog.fc-artwork-detail-dialog[open], dialog.fc-missionary-detail-dialog[open]')) document.body.classList.remove('fc-dialog-open');
            image.removeAttribute('src');
            if (continueTarget) {
                const target = continueTarget;
                if (!target.hasAttribute('tabindex')) {
                    target.setAttribute('tabindex', '-1');
                    target.addEventListener('blur', function () { target.removeAttribute('tabindex'); }, { once: true });
                }
                target.focus({ preventScroll: true });
                target.scrollIntoView({ block: 'start', behavior: 'auto' });
            } else if (returnFocus) returnFocus.focus({ preventScroll: true });
            returnFocus = null;
            continueTarget = null;
        });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
    else initialize();
}());
