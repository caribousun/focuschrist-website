/* One chapter at a time, with the complete study and every bookmark preserved. */
(function () {
    'use strict';
    const nav = document.querySelector('.jj-local-nav');
    if (!nav) return;
    const root = nav.parentElement;
    const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
    const chapters = links.map(link => document.getElementById(link.hash.slice(1)));
    if (!chapters.length || chapters.some(chapter => !chapter || chapter.parentElement !== root)) return;
    let current = 0;
    let whole = false;
    const toolbar = document.createElement('div');
    toolbar.className = 'jj-chapter-controls';
    const picker = document.createElement('details');
    picker.className = 'jj-chapter-picker';
    const summary = document.createElement('summary');
    summary.textContent = 'Choose a chapter';
    const position = document.createElement('p');
    position.className = 'jj-chapter-position';
    position.setAttribute('aria-live', 'polite');
    const mode = document.createElement('button');
    mode.type = 'button';
    mode.className = 'jj-mode';
    mode.textContent = 'Read the whole study';
    mode.setAttribute('aria-pressed', 'false');
    nav.before(toolbar);
    picker.append(summary, nav);
    toolbar.append(position, picker, mode);
    const steps = document.createElement('nav');
    steps.className = 'jj-chapter-steps';
    steps.setAttribute('aria-label', 'Continue through the chapters');
    function button(text) {
        const item = document.createElement('button');
        item.type = 'button';
        item.textContent = text;
        steps.append(item);
        return item;
    }
    const previous = button('← Previous chapter');
    const next = button('Next chapter →');
    chapters.at(-1).after(steps);
    function chapterForHash() {
        let id;
        try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return -1; }
        const target = document.getElementById(id);
        return chapters.findIndex(chapter => chapter === target || chapter.contains(target));
    }
    function paint() {
        chapters.forEach((chapter, index) => {
            chapter.hidden = !whole && index !== current;
            if (index === current) links[index].setAttribute('aria-current', 'step');
            else links[index].removeAttribute('aria-current');
        });
        position.textContent = whole ? 'The complete study' : 'Chapter ' + (current + 1) + ' of ' + chapters.length;
        mode.textContent = whole ? 'Read one chapter at a time' : 'Read the whole study';
        mode.setAttribute('aria-pressed', String(whole));
        previous.disabled = current === 0;
        next.disabled = current === chapters.length - 1;
        steps.hidden = whole;
        root.classList.toggle('jj-whole-study', whole);
        if (chapters.some(chapter => chapter.hidden && chapter.contains(document.activeElement))) {
            const heading = chapters[current].querySelector('h2');
            heading.tabIndex = -1;
            heading.focus({ preventScroll: true });
        }
    }
    function show(index, focusHeading, updateHistory) {
        current = index;
        whole = false;
        paint();
        picker.open = false;
        if (updateHistory) history.pushState(null, '', '#' + chapters[current].id);
        if (focusHeading) {
            const heading = chapters[current].querySelector('h2');
            heading.tabIndex = -1;
            heading.focus({ preventScroll: true });
            toolbar.scrollIntoView({ block: 'start', behavior: 'instant' });
        }
    }
    links.forEach((link, index) => link.addEventListener('click', event => {
        if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        show(index, true, true);
    }));
    previous.addEventListener('click', () => show(current - 1, true, true));
    next.addEventListener('click', () => show(current + 1, true, true));
    mode.addEventListener('click', () => {
        whole = !whole;
        paint();
        if (!whole) toolbar.scrollIntoView({ block: 'start', behavior: 'instant' });
    });
    function restoreBookmark() {
        const index = chapterForHash();
        const destination = index < 0 && !location.hash ? 0 : index;
        if (destination >= 0 && destination !== current) {
            document.querySelectorAll('.fc-full-image-viewer[open], #fc-scripture-reader[open], #topicArtworkDetailDialog[open]').forEach(dialog => {
                dialog.addEventListener('close', () => {
                    if (document.querySelector('dialog[open]')) return;
                    const heading = chapters[current].querySelector('h2');
                    heading.tabIndex = -1;
                    heading.focus({ preventScroll: true });
                }, { once: true });
                dialog.close();
            });
        }
        if (index < 0) {
            if (!location.hash) { current = 0; paint(); }
            return;
        }
        current = index;
        paint();
        let target;
        try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (_) { return; }
        requestAnimationFrame(() => {
            if (target) target.scrollIntoView({ block: 'start', behavior: 'instant' });
        });
    }
    // Reveal bookmarked pictures before the shared gallery/reader follows their anchors.
    window.addEventListener('hashchange', restoreBookmark);
    window.addEventListener('popstate', restoreBookmark);
    document.addEventListener('click', event => {
        if (event.defaultPrevented || event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const link = event.target.closest('a[href]');
        if (!link || nav.contains(link)) return;
        const url = new URL(link.href, location.href);
        if (url.pathname !== location.pathname || url.origin !== location.origin || !url.hash) return;
        let target;
        try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); } catch (_) { return; }
        const index = chapters.findIndex(chapter => chapter === target || chapter.contains(target));
        if (index >= 0 && chapters[index].hidden) { current = index; paint(); }
    }, true);
    root.classList.add('jj-chapter-reader');
    document.body.classList.add('jj-enhanced');
    const initial = chapterForHash();
    if (initial >= 0) current = initial;
    paint();
    if (initial >= 0) restoreBookmark();
    // Printing always includes the full journey, regardless of the reading mode.
    window.addEventListener('beforeprint', () => chapters.forEach(chapter => { chapter.hidden = false; }));
    window.addEventListener('afterprint', paint);
}());
