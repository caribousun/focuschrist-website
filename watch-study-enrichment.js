/* focusChrist Watch production enrichment.
 * The Watch page is media-first. This layer verifies that concrete video cards expose a visual thumbnail
 * and strengthens accessible labels without inventing or redirecting to unverified videos.
 */
(function () {
    'use strict';

    function labelMiniMedia() {
        document.querySelectorAll('.watch-mini-media').forEach(function (card) {
            const title = card.querySelector('strong');
            if (!title) return;
            card.setAttribute('aria-label', 'Watch ' + title.textContent.trim() + ' on ChurchofJesusChrist.org');
            card.setAttribute('data-watch-thumbnail-ready', 'true');
        });
    }

    function labelThemeWatch() {
        const card = document.querySelector('[data-watch-path="watch"]');
        if (!card) return;
        const title = card.querySelector('.watch-path-title');
        const apply = function () {
            if (!title) return;
            card.setAttribute('aria-label', 'Watch ' + title.textContent.trim() + ' on ChurchofJesusChrist.org');
        };
        apply();
        if (title) new MutationObserver(apply).observe(title, { childList: true, characterData: true, subtree: true });
    }

    function init() {
        labelMiniMedia();
        labelThemeWatch();
        document.documentElement.setAttribute('data-focuschrist-watch-enrichment-ready', 'true');
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
