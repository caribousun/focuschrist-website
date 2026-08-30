/* focusChrist shared interaction controller.
 * Keeps common navigation accessibility, verified resource routing, study paths,
 * and expandable-content behavior consistent across pages without a framework.
 */
(function () {
    'use strict';

    const OFFICIAL_RESOURCE_LINKS = [
        ['Church Website', 'https://www.churchofjesuschrist.org/?lang=eng'],
        ['Gospel Library', 'https://www.churchofjesuschrist.org/study?lang=eng&platform=web'],
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
        ['RSC Search', 'https://rsc.byu.edu/search'],
        ['Scripture Citation Index', 'https://scriptures.byu.edu/']
    ];

    window.toggleMenu = function () {
        const menu = document.getElementById('hamburgerMenu');
        const trigger = document.querySelector('.hamburger');
        if (!menu) return;
        menu.classList.toggle('show');
        if (trigger) {
            trigger.setAttribute('aria-expanded', menu.classList.contains('show') ? 'true' : 'false');
        }
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

    function relativeWatchHref() {
        const path = window.location.pathname;
        if (path.includes('/answers/') || path.includes('/art-study/')) return '../watch.html';
        return 'watch.html';
    }

    function relativeAssetHref(name) {
        const path = window.location.pathname;
        if (path.includes('/answers/') || path.includes('/art-study/')) return '../' + name;
        return name;
    }

    function onWatchPage() {
        return window.location.pathname.toLowerCase().endsWith('/watch.html');
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

    function ensurePrimaryStudyNavigation() {
        const desktop = document.querySelector('.nav[data-focuschrist-header="standard"] .nav-links');
        if (desktop && !desktop.querySelector('[data-focuschrist-primary-watch]')) {
            const watch = createWatchLink('WATCH');
            const about = Array.from(desktop.querySelectorAll('a')).find(function (link) {
                return link.textContent.trim().toUpperCase() === 'ABOUT';
            });
            if (about) desktop.insertBefore(watch, about);
            else desktop.appendChild(watch);
        }

        const menu = document.getElementById('hamburgerMenu');
        if (menu && !menu.querySelector('[data-focuschrist-primary-watch]')) {
            const watch = createWatchLink('WATCH & STUDY');
            const divider = menu.querySelector('hr');
            if (divider) menu.insertBefore(watch, divider);
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
        OFFICIAL_RESOURCE_LINKS.forEach(function (resource) {
            appendExternalMenuLink(menu, resource[0], resource[1]);
        });

        menu.appendChild(document.createElement('hr'));
        appendMenuLabel(menu, 'BYU Study Resources');
        BYU_RESOURCE_LINKS.forEach(function (resource) {
            appendExternalMenuLink(menu, resource[0], resource[1]);
        });

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

        new MutationObserver(syncExpanded).observe(menu, {
            attributes: true,
            attributeFilter: ['class']
        });
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

        if (kind === 'timeline' && typeof window.expandTimelineItem === 'function') {
            window.expandTimelineItem(control, topic);
        } else if (kind === 'trail' && typeof window.expandTrailPoint === 'function') {
            window.expandTrailPoint(control, topic);
        }
    }

    function initPioneerDisclosures() {
        const controls = document.querySelectorAll('[data-focus-expand][data-topic]');
        controls.forEach(function (control) {
            control.setAttribute('role', 'button');
            if (!control.hasAttribute('tabindex')) control.setAttribute('tabindex', '0');
            if (!control.hasAttribute('aria-expanded')) control.setAttribute('aria-expanded', 'false');

            const title = control.querySelector('.timeline-title, .map-content h4, .map-content h3');
            if (!control.hasAttribute('aria-label') && title) {
                control.setAttribute('aria-label', title.textContent.trim() + '. Expand for more information.');
            }

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

            new MutationObserver(function () {
                syncDisclosureState(control);
            }).observe(control, {
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
                if (window.history && window.history.replaceState) {
                    window.history.replaceState(null, '', '#' + main.id);
                }
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

    function appendScript(src, marker, onload) {
        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.setAttribute(marker, 'true');
        if (onload) script.addEventListener('load', onload, { once: true });
        script.addEventListener('error', function () {
            console.error('focusChrist shared asset failed to load: ' + src);
        }, { once: true });
        document.body.appendChild(script);
    }

    function loadStudyJourney() {
        if (document.querySelector('script[data-focuschrist-study-journey]')) return;
        appendScript(relativeAssetHref('study-journey.js?v=20260829-1'), 'data-focuschrist-study-journey');
    }

    function loadStudyIntelligence() {
        const path = window.location.pathname.toLowerCase();
        const eligible = path.endsWith('/ask.html') || path.endsWith('/pioneers.html');
        if (!eligible || document.querySelector('script[data-focuschrist-study-intelligence]')) return;

        appendScript('study-intelligence.js?v=20260830-2', 'data-focuschrist-study-intelligence', function () {
            if (document.querySelector('script[data-focuschrist-study-intelligence-v2]')) return;
            appendScript('study-intelligence-v2.js?v=20260830-2', 'data-focuschrist-study-intelligence-v2');
        });
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
