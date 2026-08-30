/* focusChrist Watch enrichment.
 * Strengthens verified official video routes and theme-based @theRisen636 continuation
 * without inventing exact video IDs.
 */
(function () {
    'use strict';

    const CHANNEL = 'https://www.youtube.com/@theRisen636';
    const BIBLE_VIDEOS = 'https://www.churchofjesuschrist.org/study/videos-and-images/bible-videos?lang=eng';
    const BOM_VIDEOS = 'https://www.churchofjesuschrist.org/study/videos-and-images/book-of-mormon-videos?lang=eng';

    function channelSearch(query) {
        return CHANNEL + '/search?query=' + encodeURIComponent(query);
    }

    function findSectionByHeading(text) {
        return Array.from(document.querySelectorAll('section')).find(function (section) {
            const heading = section.querySelector('h2');
            return heading && heading.textContent.trim() === text;
        }) || null;
    }

    function ensureOfficialVideoRoutes() {
        const section = findSectionByHeading('Official Church Video & Study');
        if (!section) return;
        const grid = section.querySelector('.fc-grid');
        if (!grid) return;

        Array.from(grid.querySelectorAll('a.fc-card')).forEach(function (card) {
            const title = card.querySelector('.fc-card-title');
            if (title && title.textContent.trim() === 'Bible Videos') card.href = BIBLE_VIDEOS;
        });

        const hasBom = Array.from(grid.querySelectorAll('.fc-card-title')).some(function (title) {
            return title.textContent.trim() === 'Book of Mormon Videos';
        });
        if (hasBom) return;

        const card = document.createElement('a');
        card.className = 'fc-card fc-card--interactive';
        card.href = BOM_VIDEOS;
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
        card.setAttribute('data-focuschrist-book-of-mormon-videos', 'true');

        const title = document.createElement('h3');
        title.className = 'fc-card-title';
        title.textContent = 'Book of Mormon Videos';
        card.appendChild(title);

        const copy = document.createElement('p');
        copy.textContent = 'Official dramatized Book of Mormon scenes organized for learning, teaching, and sharing faith in Jesus Christ.';
        card.appendChild(copy);
        grid.appendChild(card);
    }

    function createThemeLink(label, query) {
        const link = document.createElement('a');
        link.className = 'fc-button';
        link.href = channelSearch(query);
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = label;
        return link;
    }

    function ensureChannelThemeBridge() {
        const section = findSectionByHeading('Continue from Featured Art');
        if (!section || section.querySelector('[data-focuschrist-channel-theme-bridge]')) return;
        const container = section.querySelector('.fc-container--standard');
        if (!container) return;

        const bridge = document.createElement('div');
        bridge.setAttribute('data-focuschrist-channel-theme-bridge', 'true');
        bridge.style.marginTop = '34px';
        bridge.style.paddingTop = '28px';
        bridge.style.borderTop = '1px solid rgba(211,170,98,.20)';
        bridge.style.textAlign = 'center';

        const eyebrow = document.createElement('p');
        eyebrow.className = 'fc-eyebrow';
        eyebrow.style.textAlign = 'center';
        eyebrow.textContent = 'Continue in video';
        bridge.appendChild(eyebrow);

        const heading = document.createElement('h3');
        heading.className = 'fc-section-heading fc-section-heading--center';
        heading.style.fontSize = 'clamp(1.45rem,3vw,2rem)';
        heading.textContent = 'Find the same themes on @theRisen636';
        bridge.appendChild(heading);

        const copy = document.createElement('p');
        copy.className = 'fc-section-intro fc-section-intro--center';
        copy.textContent = 'These links search the channel by study theme. Exact individual video links are used only when they have been verified.';
        bridge.appendChild(copy);

        const actions = document.createElement('div');
        actions.className = 'fc-actions fc-actions--center';
        actions.style.marginTop = '20px';
        actions.appendChild(createThemeLink('The Living Christ', 'The Living Christ'));
        actions.appendChild(createThemeLink('The Good Shepherd', 'The Good Shepherd'));
        actions.appendChild(createThemeLink('Little Children', 'Suffer the Little Children'));
        actions.appendChild(createThemeLink('Be Still', 'Be Still'));

        const all = document.createElement('a');
        all.className = 'fc-button fc-button--primary';
        all.href = CHANNEL;
        all.target = '_blank';
        all.rel = 'noopener noreferrer';
        all.textContent = 'Browse @theRisen636';
        actions.appendChild(all);
        bridge.appendChild(actions);
        container.appendChild(bridge);
    }

    document.addEventListener('DOMContentLoaded', function () {
        ensureOfficialVideoRoutes();
        ensureChannelThemeBridge();
    });
})();
