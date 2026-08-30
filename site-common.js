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
        ['General Conference', 'https://www.churchofjesuschrist.org/study/general-conference?lang=eng'],
        ['Jesus Christ Videos', 'https://www.churchofjesuschrist.org/comeuntochrist/believe/jesus/videos'],
        ['Bible Videos', 'https://www.churchofjesuschrist.org/comeuntochrist/believe/bible/videos'],
        ['Gospel Video & Image Resources', 'https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng']
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

    function appendScript(src, marker, onload) {
        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.setAttribute(marker, 'true');
        if (onload) script.addEventListener('load', onload, { once: true });
        script.addEventListener('error', function () {
            console.error('focusChrist Study Intelligence asset failed to load: ' + src);
        }, { once: true });
        document.body.appendChild(script);
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
        ensurePrimaryStudyNavigation();
        initOfficialResourceMenu();
        initNavigation();
        initPioneerDisclosures();
        window.setTimeout(loadStudyIntelligence, 0);
    });
})();
