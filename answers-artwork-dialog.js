/* Loaded only by Answers; reopen each reflection at its beginning. */
(function () {
    'use strict';
    const dialog = document.getElementById('artworkDetailDialog');
    const copy = document.getElementById('artworkDetailCopy');
    if (!dialog || !copy) return;
    new MutationObserver(function () {
        if (dialog.open) copy.scrollTop = 0;
    }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
}());
