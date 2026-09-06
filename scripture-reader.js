/* Verified, same-page scripture reading. Scripture text comes only from local source-checked JSON. */
(function (root) {
    'use strict';
    const hosts = new Set(['www.churchofjesuschrist.org', 'churchofjesuschrist.org']);
    function identify(value) {
        let url;
        try { url = new URL(value); } catch (_) { return null; }
        if (url.protocol !== 'https:' || !hosts.has(url.hostname) || url.port) return null;
        const match = url.pathname.match(/^\/study\/scriptures\/(ot|nt|bofm|dc-testament|pgp)\/([a-z0-9-]+)\/(\d+)(?:\.(\d+(?:-\d+)?))?\/?$/);
        if (!match || Number(match[3]) < 1) return null;
        return { url, key: match.slice(1, 4).join('/'), chapter: Number(match[3]), suffix: match[4] || null };
    }
    function parseSelection(value) {
        if (!value || !/^(?:p?\d+(?:-p?\d+)?)(?:\s*,\s*p?\d+(?:-p?\d+)?)*$/.test(value)) return null;
        const result = new Set();
        for (const part of value.split(',')) {
            const ends = part.trim().replace(/p/g, '').split('-').map(Number);
            const first = ends[0], last = ends.length === 2 ? ends[1] : first;
            if (first < 1 || last < first || last > 1000) return null;
            for (let n = first; n <= last; n++) result.add(n);
        }
        return Array.from(result).sort((a, b) => a - b);
    }
    function reference(href, label) {
        const found = identify(href);
        if (!found) return null;
        const id = found.url.searchParams.get('id');
        const hash = found.url.hash.slice(1);
        let selection = null, invalid = false;
        if (id !== null) { selection = parseSelection(id); invalid = !selection; }
        else if (/^p\d/.test(hash)) { selection = parseSelection(hash); invalid = !selection; }
        else {
            // Infer only a single complete verse citation for this chapter, never prose containing several references.
            const match = (label || '').trim().match(/^[1-4]?\s*[A-Za-z][A-Za-z .&’'-]*\s+(\d+):([\d,\s\-–]+)$/);
            if (match && Number(match[1]) === found.chapter) {
                selection = parseSelection(match[2].trim().replace(/–/g, '-'));
                invalid = !selection;
            }
        }
        if (!selection && !invalid && found.suffix) { selection = parseSelection(found.suffix); invalid = !selection; }
        return { ...found, selection, invalid };
    }
    function selectionLabel(numbers) {
        const parts = [];
        for (let i = 0; i < numbers.length; i++) {
            const first = numbers[i];
            while (i + 1 < numbers.length && numbers[i + 1] === numbers[i] + 1) i++;
            parts.push(first === numbers[i] ? String(first) : first + '–' + numbers[i]);
        }
        return parts.join(', ');
    }
    function validate(data, expected) {
        if (!data || typeof data.title !== 'string' || !data.title.trim() || data.title.length > 120 ||
            typeof data.verified_on !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(data.verified_on) ||
            !Array.isArray(data.verses) || !data.verses.length || data.verses.length > 1000) throw new Error('Invalid scripture data');
        const source = identify(data.source_url);
        if (!source || source.key !== expected.key || source.url.searchParams.get('lang') !== 'eng') throw new Error('Scripture source mismatch');
        let previous = 0;
        for (const verse of data.verses) {
            if (!verse || !Number.isInteger(verse.number) || verse.number <= previous || verse.number > 1000 ||
                typeof verse.text !== 'string' || !verse.text.trim() || verse.text.length > 20000) throw new Error('Invalid verse data');
            previous = verse.number;
        }
        return data;
    }
    function selectVerses(data, selection) {
        if (!selection) return data.verses;
        const verses = selection.map(number => data.verses.find(verse => verse.number === number));
        if (verses.some(verse => !verse)) throw new Error('Requested verse unavailable');
        return verses;
    }
    const api = { identify, parseSelection, reference, validate, selectVerses };
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    if (!root.document || !root.HTMLDialogElement || root.document.getElementById('fc-scripture-reader')) return;
    const document = root.document;
    const dialog = document.createElement('dialog');
    dialog.id = 'fc-scripture-reader';
    dialog.className = 'fc-scripture-reader';
    dialog.setAttribute('aria-labelledby', 'fc-scripture-title');
    dialog.innerHTML = '<div class="fc-scripture-shell"><header class="fc-scripture-header"><div><p class="fc-scripture-eyebrow">Scripture study</p><h2 id="fc-scripture-title">Scripture</h2><p class="fc-scripture-context"></p></div><button type="button" class="fc-scripture-x" aria-label="Close scripture" autofocus>×</button></header><div class="fc-scripture-body" tabindex="0" aria-label="Scripture passage"><p class="fc-scripture-status" role="status" aria-live="polite"></p><div class="fc-scripture-verses"></div></div><footer class="fc-scripture-footer"><a class="fc-scripture-source" data-scripture-source href="https://www.churchofjesuschrist.org/study/scriptures?lang=eng" target="_blank" rel="noopener noreferrer">Go to source <span aria-hidden="true">↗</span><span class="fc-scripture-sr"> (opens in a new tab)</span></a><button type="button" class="fc-scripture-close">Close</button></footer></div>';
    document.body.appendChild(dialog);
    const title = dialog.querySelector('#fc-scripture-title');
    const context = dialog.querySelector('.fc-scripture-context');
    const body = dialog.querySelector('.fc-scripture-body');
    const status = dialog.querySelector('.fc-scripture-status');
    const passage = dialog.querySelector('.fc-scripture-verses');
    const source = dialog.querySelector('.fc-scripture-source');
    const close = dialog.querySelector('.fc-scripture-x');
    const cache = new Map();
    let generation = 0, returnFocus = null, previouslyLocked = false;
    function getChapter(ref) {
        if (!cache.has(ref.key)) {
            const request = root.fetch('/scripture-data/' + ref.key + '.json', { credentials: 'same-origin' })
                .then(response => { if (!response.ok) throw new Error('Scripture unavailable'); return response.json(); })
                .then(data => validate(data, ref));
            cache.set(ref.key, request);
            request.catch(() => { if (cache.get(ref.key) === request) cache.delete(ref.key); });
        }
        return cache.get(ref.key);
    }
    async function open(ref, trigger) {
        const current = ++generation;
        returnFocus = trigger;
        title.textContent = (trigger.textContent || '').trim().slice(0, 120) || 'Scripture';
        context.textContent = 'Reading from the scriptures';
        source.href = ref.url.href;
        passage.replaceChildren();
        status.textContent = 'Loading scripture…';
        body.setAttribute('aria-busy', 'true');
        if (!dialog.open) {
            previouslyLocked = document.body.classList.contains('fc-scripture-open');
            dialog.showModal();
            document.body.classList.add('fc-scripture-open');
        }
        body.scrollTop = 0;
        close.focus({ preventScroll: true });
        try {
            if (ref.invalid) throw new Error('Unrecognized verse selection');
            const data = await getChapter(ref);
            const selected = selectVerses(data, ref.selection);
            if (generation !== current || !dialog.open) return;
            title.textContent = data.title + (ref.selection ? ':' + selectionLabel(ref.selection) : '');
            context.textContent = ref.selection ? (selected.length === 1 ? 'Selected verse' : selected.length + ' selected verses') : 'Complete chapter';
            const fragment = document.createDocumentFragment();
            for (const verse of selected) {
                const paragraph = document.createElement('p');
                paragraph.className = 'fc-scripture-verse';
                const number = document.createElement('span');
                number.className = 'fc-scripture-number';
                number.textContent = String(verse.number);
                paragraph.appendChild(number);
                paragraph.appendChild(document.createTextNode(' ' + verse.text));
                fragment.appendChild(paragraph);
            }
            passage.replaceChildren(fragment);
            status.textContent = '';
            body.removeAttribute('aria-busy');
        } catch (_) {
            if (generation !== current || !dialog.open) return;
            context.textContent = 'Read at the original source';
            status.textContent = 'This passage is not available in the reader right now. Use “Go to source” to read the scripture on the Church website.';
            body.removeAttribute('aria-busy');
        }
    }
    close.addEventListener('click', () => dialog.close());
    dialog.querySelector('.fc-scripture-close').addEventListener('click', () => dialog.close());
    let outsidePointer = false;
    dialog.addEventListener('pointerdown', event => { outsidePointer = event.target === dialog; });
    dialog.addEventListener('click', event => { if (event.target === dialog && outsidePointer) dialog.close(); outsidePointer = false; });
    dialog.addEventListener('cancel', event => { event.stopPropagation(); });
    dialog.addEventListener('close', () => {
        generation++;
        if (!previouslyLocked) document.body.classList.remove('fc-scripture-open');
        if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
        returnFocus = null;
    });
    document.addEventListener('click', event => {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const trigger = event.target && event.target.closest ? event.target.closest('a[href]') : null;
        if (!trigger || trigger.hasAttribute('download') || trigger.hasAttribute('data-scripture-source')) return;
        const ref = reference(trigger.href, trigger.textContent);
        if (!ref) return;
        event.preventDefault();
        open(ref, trigger);
    });
})(typeof window !== 'undefined' ? window : globalThis);
