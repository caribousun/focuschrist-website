/* One reference and quotation contract for the reader, Ask and Pioneer. */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory;
    else {
        root.focusChristLoadScriptureLibrary = function () {
            root.focusChristScriptureReady = fetch('/scripture-data/catalog.json', { cache: 'no-cache' })
            .then(function (r) { if (!r.ok) throw new Error('catalog-unavailable'); return r.json(); })
            .then(function (catalog) { return root.focusChristScriptureLibrary = factory(catalog, root.fetch.bind(root)); });
            root.focusChristScriptureReady.catch(function () {});
            return root.focusChristScriptureReady;
        };
        root.focusChristLoadScriptureLibrary();

    }
})(typeof window !== 'undefined' ? window : globalThis, function (catalog, fetcher) {
    'use strict';
    const base = 'https://www.churchofjesuschrist.org/study/scriptures/';
    const normalize = value => String(value).normalize('NFC').replace(/[’‘]/g, "'").replace(/[“”]/g, '"').replace(/\s+/g, ' ').trim();
    const aliasKey = value => normalize(value).toLowerCase().replace(/[.]/g, '').replace(/[–—]/g, '-').replace(/\s+/g, ' ');
    const aliases = new Map();
    for (const book of catalog.books) for (const alias of [book.name, ...book.aliases]) aliases.set(aliasKey(alias), book.key);
    const names = Array.from(aliases.keys()).sort((a,b) => b.length-a.length).map(x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/ /g, '\\s+'));
    const pattern = new RegExp('\\b(' + names.join('|') + ')\\.?\\s+(?:chapter\\s+|section\\s+)?(\\d+)(?:\\s*:\\s*(\\d+(?:\\s*[-–]\\s*\\d+)?(?:\\s*,\\s*\\d+(?:\\s*[-–]\\s*\\d+)?)*))?(?:\\s*[-–]\\s*(\\d+)(?:\\s*:\\s*(\\d+))?)?', 'gi');
    function selection(value, maximum) {
        if (!value) return null;
        const result = new Set();
        for (const part of value.replace(/p/g, '').split(',')) {
            if (!/^\s*\d+(?:\s*[-–]\s*\d+)?\s*$/.test(part)) throw new Error('invalid-verse-selection');
            const ends = part.split(/[-–]/).map(Number), end = ends[1] === undefined ? ends[0] : ends[1];
            if (ends[0] < 1 || end < ends[0] || end > maximum) throw new Error('invalid-verse-selection');
            for (let n=ends[0]; n<=end; n++) result.add(n);
        }
        return [...result].sort((a,b)=>a-b);
    }
    function references(text) {
        const found = [];
        for (const match of String(text).replace(/[\u2010-\u2015\u2212]/g, '-').matchAll(pattern)) {
            const book = aliases.get(aliasKey(match[1])), bookInfo = catalog.books.find(b=>b.key===book);
            const shorthand = bookInfo.chapters === 1 && !match[3] && !/\b(?:chapter|section)\b/i.test(match[0]) && (Number(match[2]) > 1 || !!match[4]);
            const chapter = shorthand ? 1 : Number(match[2]), key = book + '/' + chapter;
            const entry = catalog.chapters[key];
            if (!entry) throw new Error('invalid-scripture-reference');
            if (/^\s*:\s*\d/.test(String(text).slice(match.index+match[0].length))) throw new Error('cross-chapter-reference-requires-separate-citations');
            if (match[5]) throw new Error('cross-chapter-reference-requires-separate-citations');
            const end = match[4] && !shorthand ? Number(match[4]) : chapter;
            if (end < chapter || end-chapter > 150) throw new Error('invalid-chapter-range');
            if (match[3] && end !== chapter) throw new Error('ambiguous-scripture-range');
            for (let c=chapter; c<=end; c++) {
                const current = book + '/' + c, meta = catalog.chapters[current];
                if (!meta) throw new Error('invalid-scripture-reference');
                const verses = selection(shorthand ? match[2]+(match[4] ? '-'+match[4] : '') : match[3], meta.verse_count);
                found.push({ key: current, verses, text: match[0], index: match.index, end: match.index+match[0].length, url: base+current+'?lang=eng'+(verses ? '&id='+verses.map(n=>'p'+n).join(',')+'#p'+verses[0] : '') });
            }
        }
        // Generated answers must spell out each reference. Unknown books and
        // shorthand continuations cannot disappear from validation silently.
        for (const suspect of String(text).matchAll(/\b(?:[1-9]\s+)?[A-Za-z]+\s+\d+:\d+/g)) {
            if (/^(?:at|after|before|about|around|by|from|until)\s+(?:[0-1]?\d|2[0-3]):[0-5]\d$/i.test(suspect[0])) continue;
            if (!found.some(ref=>suspect.index>=ref.index && suspect.index<ref.end)) throw new Error('unrecognized-scripture-reference');
        }
        for (const suspect of String(text).matchAll(/\b[1-9]\s+(?:Nephi|John|Samuel|Kings|Chronicles|Corinthians|Thessalonians|Timothy|Peter)\s+\d+/gi)) {
            if (!found.some(ref=>suspect.index===ref.index)) throw new Error('invalid-numbered-scripture-book');
        }
        if (found.length && /(?:;\s*\d+:\d+|\bverses?\s+\d+(?:[-–]\d+)?)/i.test(text)) throw new Error('spell-out-scripture-references');
        return found;
    }
    function fromURL(value) {
        const url = new URL(value);
        if (url.protocol !== 'https:' || !['www.churchofjesuschrist.org','churchofjesuschrist.org'].includes(url.hostname) || url.port) throw new Error('invalid-scripture-source');
        const match = url.pathname.match(/^\/study\/scriptures\/(.+?\/\d+)(?:\.([\d-]+))?\/?$/);
        if (!match || !catalog.chapters[match[1]]) throw new Error('invalid-scripture-source');
        if (url.searchParams.has('lang') && url.searchParams.get('lang') !== 'eng') throw new Error('scripture-edition-mismatch');
        if (url.searchParams.getAll('id').length > 1 || (url.searchParams.has('id') && !url.searchParams.get('id'))) throw new Error('invalid-verse-selection');
        const selected = url.searchParams.get('id') || (/^#p\d/.test(url.hash) ? url.hash.slice(1) : match[2]);
        if (catalog.chapters[match[1]].kind === 'document') {
            if (selected && !catalog.chapters[match[1]].paragraph_ids.includes(selected)) throw new Error('invalid-document-paragraph');
            return {key:match[1],verses:null,paragraph:selected || null};
        }
        return { key: match[1], verses: selection(selected, catalog.chapters[match[1]].verse_count) };
    }
    const chapterCache = new Map();
    function chapter(key) {
        if (!chapterCache.has(key)) {
            const request = loadChapter(key);
            if (chapterCache.size >= 32) chapterCache.delete(chapterCache.keys().next().value);
            chapterCache.set(key,request);
            request.catch(()=>{ if(chapterCache.get(key)===request) chapterCache.delete(key); });
        }
        return chapterCache.get(key);
    }
    async function loadChapter(key) {
        const meta = catalog.chapters[key];
        if (!meta) throw new Error('invalid-scripture-reference');
        const response = await fetcher('/scripture-data/'+key+'.json');
        if (!response.ok) throw new Error('scripture-library-unavailable');
        const reader = response.body.getReader(), chunks = []; let size = 0;
        while (true) {
            const part = await reader.read(); if (part.done) break;
            size += part.value.length;
            if (size > 250000) { await reader.cancel(); throw new Error('scripture-data-too-large'); }
            chunks.push(part.value);
        }
        const bytes = new Uint8Array(size); let offset = 0;
        for (const chunk of chunks) { bytes.set(chunk,offset); offset += chunk.length; }
        const raw = new TextDecoder().decode(bytes);
        const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw));
        if ([...new Uint8Array(digest)].map(n=>n.toString(16).padStart(2,'0')).join('') !== meta.sha256) throw new Error('scripture-integrity-mismatch');
        const data = JSON.parse(raw);
        if (data.source_url !== base+key+'?lang=eng' || data.verses.length !== meta.verse_count) throw new Error('scripture-source-mismatch');
        return data;
    }
    async function checkAnswer(answer, sources) {
        let text = String(answer || '');
        try {
            // Exact library reading is source text, including historical quotations
            // inside declarations. Prove complete byte-normalized wording here;
            // a caller flag can never authorize this exception.
            for (const source of sources || []) {
                const value = source.url || '';
                if (!/\/study\/scriptures\/(?:ot|nt|bofm|dc-testament|pgp)\/[^/]+\/\d/.test(value)) continue;
                const ref = fromURL(value);
                if (catalog.chapters[ref.key].kind !== 'document') continue;
                const data = await chapter(ref.key), title = text.split('\n')[0];
                const heading = references(title);
                if (heading.length === 1 && heading[0].key === ref.key && heading[0].text === title && text === title+'\n\n'+data.paragraphs.map(p=>p.text).join('\n\n')) return {ok:true,answer:text,references:heading,version:catalog.version};
            }
            // The model selects an ID; only library text supplies its quotation.
            for (const token of [...text.matchAll(/\[\[SCRIPTURE:([^\]\n]+)\]\]/g)]) {
                const selected = references(token[1]);
                if (selected.length !== 1 || !selected[0].verses || selected[0].text.length !== token[1].trim().length) throw new Error('invalid-scripture-token');
                const ref = selected[0], data = await chapter(ref.key);
                const words = data.verses.filter(v=>ref.verses.includes(v.number)).map(v=>v.text).join(' ');
                text = text.replace(token[0], '“'+words+'” ('+token[1]+')');
            }
            const refs = references(text);
            const unique = [...new Set(refs.map(r=>r.key))];
            if (unique.length > 12) throw new Error('too-many-scripture-chapters');
            for (const source of sources || []) {
                const url = source.url || source.href || '';
                if (!/\/study\/scriptures\/.+\/\d/.test(url)) continue;
                const linked = fromURL(url), labeled = references(source.text || source.title || '');
                if (labeled.some(ref=>ref.key !== linked.key || (ref.verses && linked.verses && ref.verses.join() !== linked.verses.join()))) throw new Error('scripture-label-link-mismatch');
            }
            const data = new Map(await Promise.all(unique.map(async key=>[key, await chapter(key)])));
            const paragraphs = [text];
            let offset = 0;
            for (const paragraph of paragraphs) {
                const local = references(paragraph);
                const quotes = [...paragraph.matchAll(/[“"]([^“”"]+)[”"]|(?:^|[\s:(])[‘']([^‘’']+)[’'](?=[\s.,;:!?) ]|$)/g)].map(q => Object.assign(q, {1:q[1] || q[2]}));
                for (const quote of quotes) {
                    if (!local.length) {
                        if (/\b(?:scripture|bible|Book of Mormon|Doctrine and Covenants|Pearl of Great Price)\b|\b(?:Jesus(?: Christ)?|Christ|(?:the )?Lord)\s+(?:says?|said|declares?|promises?|taught|teaches)\b/i.test(paragraph)) throw new Error('unattributed-scripture-quotation');
                        continue;
                    }
                    const ref = local.reduce((a,b)=> Math.min(Math.abs(b.index-quote.index),Math.abs(b.end-quote.index)) < Math.min(Math.abs(a.index-quote.index),Math.abs(a.end-quote.index)) ? b : a);
                    const verses = data.get(ref.key).verses.filter(v=>!ref.verses || ref.verses.includes(v.number));
                    const original = normalize((data.get(ref.key).kind === 'document' ? data.get(ref.key).paragraphs : verses).map(v=>v.text).join(' '));
                    const quoted = normalize(quote[1]);
                    let position = original.indexOf(quoted), matched = false;
                    while (position !== -1) {
                        const before = original[position-1] || '', after = original[position+quoted.length] || '';
                        if (!(/[\p{L}\p{N}]/u.test(before) && /^[\p{L}\p{N}]/u.test(quoted)) && !(/[\p{L}\p{N}]/u.test(after) && /[\p{L}\p{N}]$/u.test(quoted))) { matched = true; break; }
                        position = original.indexOf(quoted,position+1);
                    }
                    if (!matched) throw new Error('scripture-quotation-mismatch');
                }
                offset += paragraph.length + 2;
            }
            return { ok: true, answer: text, references: refs, version: catalog.version };
        } catch (error) {
            return { ok: false, answer: 'I could not confirm the scripture reference or wording. Please open the official Gospel Library to check the passage, or ask about one specific chapter or verse.', reason: error.message, references: [], version: catalog.version };
        }
    }
    async function lookupRequest(question) {
        const candidate = String(question).trim().replace(/^please\s+/i,'').replace(/^(?:quote|read|show(?:\s+me)?|give\s+me(?:\s+the\s+text\s+of)?)\s+/i,'').replace(/^what\s+does\s+/i,'').replace(/\s+say\??$/i,'').replace(/[?.]$/,'');
        try {
            const refs = references(candidate);
            if (refs.length !== 1 || refs[0].text.length !== candidate.length) return null;
            const ref = refs[0], data = await chapter(ref.key);
            const rows = data.kind === 'document' ? data.paragraphs : data.verses.filter(v=>!ref.verses || ref.verses.includes(v.number));
            return { answer: candidate+'\n\n'+rows.map(v=>v.text).join('\n\n'), sources:[{text:candidate,url:ref.url}], verifiedGrounding:true, scriptureLibraryVersion:catalog.version, sourceIntegrityPassed:true, sourceIntegrityStatus:'local-scripture-library' };
        } catch (_) { return null; }
    }
    function linkify(element) {
        if (!element || !element.ownerDocument) return;
        const doc = element.ownerDocument, walker = doc.createTreeWalker(element, 4), nodes = [];
        while (walker.nextNode()) if (!walker.currentNode.parentElement.closest('a,button,script,style')) nodes.push(walker.currentNode);
        for (const node of nodes) {
            const refs = references(node.textContent); if (!refs.length) continue;
            const fragment = doc.createDocumentFragment(); let start = 0;
            for (let i=0;i<refs.length;i++) {
                const ref=refs[i]; if (ref.index < start) continue;
                fragment.appendChild(doc.createTextNode(node.textContent.slice(start,ref.index)));
                const group=refs.filter(r=>r.index===ref.index);
                group.forEach((item,index)=>{ if(index) fragment.appendChild(doc.createTextNode(', ')); const a=doc.createElement('a');a.href=item.url;a.textContent=group.length===1 ? ref.text : catalog.books.find(b=>item.key.startsWith(b.key+'/')).name+' '+item.key.split('/').pop();fragment.appendChild(a); });
                start=ref.end;
            }
            fragment.appendChild(doc.createTextNode(node.textContent.slice(start)));node.replaceWith(fragment);
        }
    }
    return Object.freeze({ references, fromURL, chapter, checkAnswer, selection, lookupRequest, linkify, version: catalog.version });
});
