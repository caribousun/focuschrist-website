/* focusChrist shared interaction controller.
 * Keeps common navigation accessibility, verified resource routing, and
 * expandable-content behavior consistent across pages without a framework.
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

    document.addEventListener('DOMContentLoaded', function () {
        initOfficialResourceMenu();
        initNavigation();
        initPioneerDisclosures();
    });
})();
