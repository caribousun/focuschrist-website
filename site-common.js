/* focusChrist shared interaction controller.
 * Keeps common navigation accessibility, verified resource routing, study paths,
 * and expandable-content behavior consistent across pages without a framework.
 */
(function () {
    'use strict';

    const OFFICIAL_RESOURCE_LINKS = [
        ['Church Website', 'https://www.churchofjesuschrist.org/?lang=eng'],
        ['Gospel Library', 'https://www.churchofjesuschrist.org/study?lang=eng&platform=web'],
        ['Church History', 'https://www.churchofjesuschrist.org/study/church-history?lang=eng'],
        ['Saints', 'https://www.churchofjesuschrist.org/study/church-history/saints?lang=eng'],
        ['Scriptures', 'https://www.churchofjesuschrist.org/study/scriptures?lang=eng'],
        ['Topics & Questions', 'https://www.churchofjesuschrist.org/study/manual/gospel-topics?lang=eng'],
        ['Gospel Topics Essays', 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/essays?lang=eng'],
        ['General Conference', 'https://www.churchofjesuschrist.org/study/general-conference?lang=eng'],
        ['Jesus Christ Videos', 'https://www.churchofjesuschrist.org/comeuntochrist/believe/jesus/videos'],
        ['Bible Videos', 'https://www.churchofjesuschrist.org/study/videos-and-images/bible-videos?lang=eng'],
        ['Book of Mormon Videos', 'https://www.churchofjesuschrist.org/study/videos-and-images/book-of-mormon-videos?lang=eng'],
        ['Gospel Video & Image Resources', 'https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng']
    ];

    const BYU_RESOURCE_LINKS = [
        ['Religious Studies Center', 'https://rsc.byu.edu/'],
        ['Scripture Citation Index', 'https://scriptures.byu.edu/']
    ];

    window.toggleMenu = function () {
        const menu = document.getElementById('hamburgerMenu');
        const trigger = document.querySelector('.hamburger');
        if (!menu) return;
        menu.classList.toggle('show');
        if (trigger) trigger.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');
    };

    function appendMenuLabel(menu, text) {
        const label = document.createElement('div');
        label.className = 'menu-label';
        label.textContent = text;
        menu.appendChild(label);
    }

    function appendExternalMenuLink(menu, text, href) {
        const link = document.createElement('a');
        link.href = href;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = text;
        menu.appendChild(link);
    }

    function relativeRootHref(name) {
        const path = window.location.pathname;
        if (path.includes('/answers/') || path.includes('/art-study/')) return '../' + name;
        return name;
    }

    function relativeWatchHref() { return relativeRootHref('watch.html'); }
    function relativeHistoryHref() { return relativeRootHref('church-history.html'); }
    function relativeAssetHref(name) { return relativeRootHref(name); }

    function onWatchPage() {
        return window.location.pathname.toLowerCase().endsWith('/watch.html');
    }

    function onHistoryPage() {
        return window.location.pathname.toLowerCase().endsWith('/church-history.html');
    }

    function createWatchLink(text) {
        const link = document.createElement('a');
        link.href = relativeWatchHref();
        link.textContent = text;
        link.setAttribute('data-focuschrist-primary-watch', 'true');
        if (onWatchPage()) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
        return link;
    }

    function createHistoryLink(text) {
        const link = document.createElement('a');
        link.href = relativeHistoryHref();
        link.textContent = text;
        link.setAttribute('data-focuschrist-primary-history', 'true');
        if (onHistoryPage()) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
        return link;
    }

    function ensurePrimaryStudyNavigation() {
        const desktop = document.querySelector('.nav[data-focuschrist-header="standard"] .nav-links');
        if (desktop && !desktop.querySelector('[data-focuschrist-primary-history]')) {
            const history = createHistoryLink('HISTORY');
            const pioneers = Array.from(desktop.querySelectorAll('a')).find(function (link) {
                return link.textContent.trim().toUpperCase() === 'PIONEERS';
            });
            if (pioneers) desktop.insertBefore(history, pioneers);
            else desktop.appendChild(history);
        }
        if (desktop && !desktop.querySelector('[data-focuschrist-primary-watch]')) {
            const watch = createWatchLink('WATCH');
            const about = Array.from(desktop.querySelectorAll('a')).find(function (link) {
                return link.textContent.trim().toUpperCase() === 'ABOUT';
            });
            if (about) desktop.insertBefore(watch, about);
            else desktop.appendChild(watch);
        }

        const menu = document.getElementById('hamburgerMenu');
        if (menu && !menu.querySelector('[data-focuschrist-primary-history]')) {
            const history = createHistoryLink('CHURCH HISTORY');
            const pioneers = Array.from(menu.querySelectorAll('a')).find(function (link) {
                return link.textContent.trim().toUpperCase() === 'PIONEERS';
            });
            const divider = menu.querySelector('hr');
            if (pioneers) menu.insertBefore(history, pioneers);
            else if (divider) menu.insertBefore(history, divider);
            else menu.appendChild(history);
        }
        if (menu && !menu.querySelector('[data-focuschrist-primary-watch]')) {
            const watch = createWatchLink('WATCH & STUDY');
            const about = Array.from(menu.querySelectorAll('a')).find(function (link) {
                return link.textContent.trim().toUpperCase() === 'ABOUT';
            });
            const divider = menu.querySelector('hr');
            if (about) menu.insertBefore(watch, about);
            else if (divider) menu.insertBefore(watch, divider);
            else menu.appendChild(watch);
        }
    }

    function initOfficialResourceMenu() {
        const menu = document.getElementById('hamburgerMenu');
        if (!menu) return;
        const firstDivider = menu.querySelector('hr');
        if (!firstDivider) return;
        while (firstDivider.nextSibling) firstDivider.nextSibling.remove();

        appendMenuLabel(menu, 'Official Church Resources');
        OFFICIAL_RESOURCE_LINKS.forEach(function (resource) { appendExternalMenuLink(menu, resource[0], resource[1]); });

        menu.appendChild(document.createElement('hr'));
        appendMenuLabel(menu, 'BYU Study Resources');
        BYU_RESOURCE_LINKS.forEach(function (resource) { appendExternalMenuLink(menu, resource[0], resource[1]); });

        menu.appendChild(document.createElement('hr'));
        appendMenuLabel(menu, 'focusChrist Video');
        const watchLink = document.createElement('a');
        watchLink.href = relativeWatchHref();
        watchLink.textContent = 'Watch & Study';
        menu.appendChild(watchLink);
        appendExternalMenuLink(menu, '@theRisen636', 'https://www.youtube.com/@theRisen636');
    }

    function initNavigation() {
        const trigger = document.querySelector('.hamburger');
        const menu = document.getElementById('hamburgerMenu');
        if (!trigger || !menu) return;
        trigger.setAttribute('role', 'button');
        if (!trigger.hasAttribute('tabindex')) trigger.setAttribute('tabindex', '0');
        trigger.setAttribute('aria-label', 'Toggle navigation menu');
        trigger.setAttribute('aria-controls', 'hamburgerMenu');

        function syncExpanded() {
            trigger.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');
        }

        trigger.addEventListener('keydown', function (event) {
            if (event.target !== trigger) return;
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                window.toggleMenu();
            }
        });
        menu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                menu.classList.remove('show');
                syncExpanded();
            });
        });
        document.addEventListener('click', function (event) {
            if (!menu.classList.contains('show')) return;
            if (menu.contains(event.target) || trigger.contains(event.target)) return;
            menu.classList.remove('show');
            syncExpanded();
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && menu.classList.contains('show')) {
                menu.classList.remove('show');
                syncExpanded();
                trigger.focus();
            }
        });
        new MutationObserver(syncExpanded).observe(menu, { attributes: true, attributeFilter: ['class'] });
        syncExpanded();
    }

    function syncDisclosureState(control) {
        control.setAttribute('aria-expanded', control.classList.contains('expanded') ? 'true' : 'false');
        const response = control.querySelector('.ai-response');
        if (response) {
            response.setAttribute('role', 'status');
            response.setAttribute('aria-live', 'polite');
            response.setAttribute('aria-atomic', 'false');
        }
    }

    function activateDisclosure(control) {
        const kind = control.dataset.focusExpand;
        const topic = control.dataset.topic;
        if (!topic) return;
        if (kind === 'timeline' && typeof window.expandTimelineItem === 'function') window.expandTimelineItem(control, topic);
        else if (kind === 'trail' && typeof window.expandTrailPoint === 'function') window.expandTrailPoint(control, topic);
    }

    function initPioneerDisclosures() {
        document.querySelectorAll('[data-focus-expand][data-topic]').forEach(function (control) {
            control.setAttribute('role', 'button');
            if (!control.hasAttribute('tabindex')) control.setAttribute('tabindex', '0');
            if (!control.hasAttribute('aria-expanded')) control.setAttribute('aria-expanded', 'false');
            const title = control.querySelector('.timeline-title, .map-content h4, .map-content h3');
            if (!control.hasAttribute('aria-label') && title) control.setAttribute('aria-label', title.textContent.trim() + '. Expand for more information.');
            control.addEventListener('click', function (event) {
                if (event.target.closest('a, button') && event.target !== control) return;
                activateDisclosure(control);
            });
            control.addEventListener('keydown', function (event) {
                if (event.target !== control) return;
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    activateDisclosure(control);
                }
            });
            new MutationObserver(function () { syncDisclosureState(control); }).observe(control, {
                attributes: true,
                attributeFilter: ['class'],
                childList: true,
                subtree: true
            });
            syncDisclosureState(control);
        });
    }

    function ensureMainLandmark() {
        let main = document.querySelector('main, [role="main"]');
        const nav = document.querySelector('.nav[data-focuschrist-header="standard"]');
        const footer = document.querySelector('.fc-footer[data-focuschrist-footer="standard"]');
        if (!main && nav && footer && nav.parentNode === footer.parentNode) {
            main = document.createElement('main');
            main.className = 'fc-main-landmark';
            main.setAttribute('data-focuschrist-main', 'generated');
            let node = nav.nextSibling;
            while (node && node !== footer) {
                const next = node.nextSibling;
                main.appendChild(node);
                node = next;
            }
            footer.parentNode.insertBefore(main, footer);
        }
        if (!main) return;
        if (!main.id) main.id = 'main-content';
        if (!main.hasAttribute('tabindex')) main.setAttribute('tabindex', '-1');
        if (!document.querySelector('[data-focuschrist-skip-link]')) {
            const skip = document.createElement('a');
            skip.href = '#' + main.id;
            skip.className = 'fc-skip-link';
            skip.setAttribute('data-focuschrist-skip-link', 'true');
            skip.textContent = 'Skip to main content';
            skip.addEventListener('click', function (event) {
                event.preventDefault();
                main.focus({ preventScroll: true });
                main.scrollIntoView({ behavior: 'auto', block: 'start' });
                if (window.history && window.history.replaceState) window.history.replaceState(null, '', '#' + main.id);
            });
            document.body.insertBefore(skip, document.body.firstChild);
        }
    }

    function normalizeFooterIdentity() {
        const footer = document.querySelector('.fc-footer[data-focuschrist-footer="standard"]');
        if (!footer) return;
        const standardText = '© ' + new Date().getFullYear() + ' focusChrist. All are welcome here.';
        let identity = Array.from(footer.children).find(function (child) {
            return child.tagName === 'P' && !child.hasAttribute('data-focuschrist-independence');
        });
        if (!identity) {
            identity = document.createElement('p');
            footer.insertBefore(identity, footer.firstChild);
        }
        identity.textContent = standardText;
        identity.setAttribute('data-focuschrist-footer-identity', 'true');
    }

    /*
     * Shared source-integrity contract for every AI answer surface.
     * A list of links is not evidence that the model read those sources. Generated
     * scripture citations are therefore allowed only when the exact reference is
     * present in source content that the application has explicitly marked trusted.
     */
    const SCRIPTURE_CITATION_PATTERN = /\b(?:[1-4]\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Doctrine\s+and\s+Covenants|D&C|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History)|Articles\s+of\s+Faith)\s+\d+(?::\d+(?:[-–]\d+)?)?/gi;
    const SCRIPTURE_ATTRIBUTION_PATTERN = /\b(?:latter-day\s+saint\s+scripture|scripture|the\s+bible|the\s+book\s+of\s+mormon|the\s+doctrine\s+and\s+covenants|d&c|the\s+pearl\s+of\s+great\s+price)\b.{0,120}\b(?:assigns?|represents?|symbolizes?|means?|says|states|teach(?:es)?|declares|records|promises|describes)\b/i;
    const SCRIPTURE_BOOK_ATTRIBUTION_PATTERN = /\b(?:book\s+of\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History))\b.{0,100}\b(?:says?|states?|teach(?:es)?|declares?|records?|promises?|describes?|means?|about)\b/i;
    const SCRIPTURE_BOOK_STRONG_ATTRIBUTION_PATTERN = /\b(?:book\s+of\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History))\b.{0,100}\b(?:says?|states?|teach(?:es)?|declares?|records?|promises?|describes?|means?)\b/i;
    const SCRIPTURE_BOOK_IS_ABOUT_PATTERN = /\b(?:book\s+of\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History))\b.{0,60}\b(?:is|was)\s+(?:mainly\s+)?about\b/i;
    const ABOUT_SCRIPTURE_BOOK_PATTERN = /\babout\s+(?:the\s+)?(?:book\s+of\s+)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Words\s+of\s+Mormon|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham|Joseph\s+Smith(?:—|-|\s+)(?:Matthew|History))\b/i;
    const PERSON_NAME_SCRIPTURE_COLLISION_PATTERN = /\b(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Nephi|Jacob|Enos|Jarom|Omni|Mosiah|Alma|Helaman|Mormon|Ether|Moroni|Moses|Abraham)\s+[A-Z][\p{L}'’.-]+(?:\s+[A-Z][\p{L}'’.-]+){0,2}\b/gu;
    const CASELESS_CANON_NAME_PERSON_QUESTION_PATTERN = /(\bwho\s+(?:is|was)\s+)(?:Joshua|Ruth|Samuel|Ezra|Nehemiah|Esther|Job|Isaiah|Jeremiah|Ezekiel|Daniel|Hosea|Joel|Amos|Jonah|Micah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Timothy|Titus|Philemon|James|Peter|Jude|Nephi|Jacob|Enos|Mosiah|Alma|Helaman|Ether|Moroni|Moses|Abraham)\s+(?!the\b|and\b|or\b)[\p{L}'’.-]{2,}(?:\s+[\p{L}'’.-]{2,}){0,1}(?=\s*[?.!]*$)/giu;
    const CASELESS_CANON_NAME_PERSON_ACTION_PATTERN = /(\b(?:what|when|where|why|how)\s+(?:did|does|is|was)\s+)(?:Joshua|Ruth|Samuel|Ezra|Nehemiah|Esther|Job|Isaiah|Jeremiah|Ezekiel|Daniel|Hosea|Joel|Amos|Jonah|Micah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Timothy|Titus|Philemon|James|Peter|Jude|Nephi|Jacob|Enos|Mosiah|Alma|Helaman|Ether|Moroni|Moses|Abraham)\s+(?!the\b|and\b|or\b)[\p{L}'’.-]{2,}(?:\s+[\p{L}'’.-]{2,}){0,1}(?=\s+(?:act(?:ed|ing)?|became|become|composed?|did|died?|lived?|made|make|said|say|served?|spoke|talked?|writes?|wrote)\b)/giu;
    const CASELESS_CANON_NAME_PERSON_ABOUT_PATTERN = /(\btell\s+me\s+about\s+)(?:Joshua|Ruth|Samuel|Ezra|Nehemiah|Esther|Job|Isaiah|Jeremiah|Ezekiel|Daniel|Hosea|Joel|Amos|Jonah|Micah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Timothy|Titus|Philemon|James|Peter|Jude|Nephi|Jacob|Enos|Mosiah|Alma|Helaman|Ether|Moroni|Moses|Abraham)\s+(?!the\b|and\b|or\b|faith\b|sermon\b|story\b|account\b|creation\b|teachings?\b|prophecy\b|vision\b|chapter\b|book\b|gospel\b|loyalty\b)[\p{L}'’.-]{2,}(?:\s+[\p{L}'’.-]{2,}){0,1}(?=\s*[?.!]*$)/giu;
    const KNOWN_FALSE_SOURCE_PATTERNS = [
        /red,?\s+white,?\s+and\s+black\s+lights?/i,
        /["']?(?:red|black|golden)\s+light["']?.{0,180}(?:D&C|Doctrine\s+and\s+Covenants)\s+76/i
    ];

    function hasKnownFalseClaim(text) {
        const value = String(text || '');
        if (!KNOWN_FALSE_SOURCE_PATTERNS.some(function (pattern) { return pattern.test(value); })) return false;
        const explicitCorrection = /\b(?:does\s+not|do\s+not|doesn't|don't|is\s+not|are\s+not|never|no\s+such)\b.{0,180}\b(?:red|white|black|golden)\b/i.test(value)
            || /\b(?:red|white|black|golden)\b.{0,180}\b(?:does\s+not|do\s+not|is\s+not|are\s+not|never)\b/i.test(value);
        return !explicitCorrection;
    }
    const SOURCE_INTEGRITY_FALLBACK = 'I cannot verify the specific source claim well enough to present it as authoritative. Please confirm the subject in the official Gospel Library at ChurchofJesusChrist.org. I would rather acknowledge that limit than attach an incorrect passage or quotation to a teaching.';

    function normalizeSourceReference(text) {
        return String(text || '')
            .toLowerCase()
            .replace(/doctrine\s+and\s+covenants/g, 'd&c')
            .replace(/[–—]/g, '-')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function extractScriptureCitations(text) {
        return String(text || '').match(SCRIPTURE_CITATION_PATTERN) || [];
    }

    function withoutOutputPersonNameScriptureCollisions(text) {
        // Several canon titles are also ordinary given names. Evaluate book-title
        // attribution only after removing properly cased full personal names so
        // "Abraham Lincoln ... at about" cannot become a Book of Abraham claim.
        return String(text || '').replace(PERSON_NAME_SCRIPTURE_COLLISION_PATTERN, '');
    }

    function withoutQueryPersonNameScriptureCollisions(text) {
        return String(text || '')
            .replace(CASELESS_CANON_NAME_PERSON_QUESTION_PATTERN, '$1')
            .replace(CASELESS_CANON_NAME_PERSON_ACTION_PATTERN, '$1')
            .replace(CASELESS_CANON_NAME_PERSON_ABOUT_PATTERN, '$1');
    }

    function guardGeneratedAnswer(answer, options) {
        const settings = options || {};
        const text = String(answer || '').trim();
        const serverVerified = settings.serverVerified === true;
        const trustedReferenceText = normalizeSourceReference(settings.trustedReferenceText || '');
        const citations = extractScriptureCitations(text);
        const ungroundedCitations = citations.filter(function (citation) {
            return !trustedReferenceText.includes(normalizeSourceReference(citation));
        });
        const violations = [];

        // Source-dependent generation must either be a separately reviewed local
        // entry or carry the server-owned retrieval-and-verification receipt.
        // Client-supplied links or prompt excerpts never create that receipt.
        if (settings.sourceDependent === true && !serverVerified) violations.push('unreviewed-source-dependent-generation');
        if (hasKnownFalseClaim(text)) {
            violations.push('known-false-source-claim');
        }
        if (ungroundedCitations.length && !serverVerified) violations.push('ungrounded-scripture-citation');
        const attributionText = withoutOutputPersonNameScriptureCollisions(text);
        if (settings.requireTrustedScripture !== false && (SCRIPTURE_ATTRIBUTION_PATTERN.test(text)
            || SCRIPTURE_BOOK_STRONG_ATTRIBUTION_PATTERN.test(text)
            || SCRIPTURE_BOOK_IS_ABOUT_PATTERN.test(text)
            || SCRIPTURE_BOOK_ATTRIBUTION_PATTERN.test(attributionText)
            || ABOUT_SCRIPTURE_BOOK_PATTERN.test(attributionText)) && !trustedReferenceText && !serverVerified) {
            violations.push('ungrounded-scripture-attribution');
        }

        if (violations.length) {
            console.warn('focusChrist source-integrity guard blocked generated answer:', violations.join(', '));
            return {
                ok: false,
                answer: SOURCE_INTEGRITY_FALLBACK,
                citations: citations,
                ungroundedCitations: ungroundedCitations,
                violations: violations
            };
        }
        return { ok: true, answer: text, citations: citations, ungroundedCitations: [], violations: [] };
    }

    window.focusChristSourceIntegrity = Object.freeze({
        policyVersion: '2026-09-01.15',
        fallback: SOURCE_INTEGRITY_FALLBACK,
        extractScriptureCitations: extractScriptureCitations,
        isScriptureDependent: function (text) {
            const value = String(text || '');
            const attributionValue = withoutQueryPersonNameScriptureCollisions(value);
            return extractScriptureCitations(value).length > 0
                || SCRIPTURE_ATTRIBUTION_PATTERN.test(value)
                || SCRIPTURE_BOOK_STRONG_ATTRIBUTION_PATTERN.test(attributionValue)
                || SCRIPTURE_BOOK_IS_ABOUT_PATTERN.test(attributionValue)
                || SCRIPTURE_BOOK_ATTRIBUTION_PATTERN.test(attributionValue)
                || ABOUT_SCRIPTURE_BOOK_PATTERN.test(attributionValue);
        },
        guardGeneratedAnswer: guardGeneratedAnswer
    });

    function appendScript(src, marker, onload) {
        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.setAttribute(marker, 'true');
        if (onload) script.addEventListener('load', onload, { once: true });
        script.addEventListener('error', function () { console.error('focusChrist shared asset failed to load: ' + src); }, { once: true });
        document.body.appendChild(script);
    }

    function loadStudyJourney() {
        if (document.querySelector('script[data-focuschrist-study-journey]')) return;
        appendScript(relativeAssetHref('study-journey.js?v=20260901-15'), 'data-focuschrist-study-journey');
    }

    function loadStudyIntelligence() {
        const path = window.location.pathname.toLowerCase();
        const eligible = path.endsWith('/ask.html') || path.endsWith('/pioneers.html');
        if (!eligible || document.querySelector('script[data-focuschrist-study-intelligence-v3]')) return;
        appendScript('study-intelligence-v3.js?v=20260901-15', 'data-focuschrist-study-intelligence-v3');
    }

    document.addEventListener('DOMContentLoaded', function () {
        ensureMainLandmark();
        normalizeFooterIdentity();
        ensurePrimaryStudyNavigation();
        initOfficialResourceMenu();
        initNavigation();
        initPioneerDisclosures();
        window.setTimeout(loadStudyJourney, 0);
        window.setTimeout(loadStudyIntelligence, 0);
    });
})();
