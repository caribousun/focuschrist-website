(function () {
    'use strict';

    const dialog = document.getElementById('missionaryDetailDialog');
    if (!dialog || typeof dialog.showModal !== 'function') return;

    const image = document.getElementById('missionaryDetailImage');
    const eyebrow = document.getElementById('missionaryDetailEyebrow');
    const title = document.getElementById('missionaryDetailTitle');
    const copy = document.getElementById('missionaryDetailCopy');
    const source = document.getElementById('missionaryDetailSource');
    const fullImage = document.getElementById('missionaryDetailFullImage');
    const closeButtons = dialog.querySelectorAll('[data-missionary-detail-close]');
    let returnFocus = null;

    function openDetail(key, trigger) {
        const record = document.querySelector('[data-missionary-detail-content="' + key + '"]');
        if (!record || !image || !eyebrow || !title || !copy || !source || !fullImage) return;

        const detailEyebrow = record.querySelector('[data-detail-eyebrow]');
        const detailTitle = record.querySelector('[data-detail-title]');
        const paragraphs = record.querySelectorAll('[data-detail-paragraph]');

        eyebrow.textContent = detailEyebrow ? detailEyebrow.textContent : 'Explore the story';
        title.textContent = detailTitle ? detailTitle.textContent : '';
        copy.replaceChildren();
        paragraphs.forEach(function (paragraph) {
            const copyParagraph = document.createElement('p');
            copyParagraph.textContent = paragraph.textContent;
            copy.appendChild(copyParagraph);
        });

        image.src = record.dataset.detailImage || '';
        image.alt = record.dataset.detailImageAlt || '';
        source.href = record.dataset.detailSource || trigger.href;
        source.textContent = record.dataset.detailSourceLabel || 'Study the Official Source';
        fullImage.href = record.dataset.detailFull || trigger.href;

        returnFocus = trigger;
        document.body.classList.add('fc-dialog-open');
        dialog.showModal();
        dialog.scrollTop = 0;
        const closeButton = dialog.querySelector('[data-missionary-detail-close]');
        if (closeButton) closeButton.focus({ preventScroll: true });
    }

    document.querySelectorAll('[data-missionary-detail]').forEach(function (trigger) {
        trigger.addEventListener('click', function (event) {
            if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            openDetail(trigger.dataset.missionaryDetail, trigger);
        });
    });

    closeButtons.forEach(function (button) {
        button.addEventListener('click', function () { dialog.close(); });
    });

    dialog.addEventListener('click', function (event) {
        if (event.target === dialog) dialog.close();
    });

    dialog.addEventListener('cancel', function () {
        document.body.classList.remove('fc-dialog-open');
    });

    dialog.addEventListener('close', function () {
        document.body.classList.remove('fc-dialog-open');
        if (returnFocus && typeof returnFocus.focus === 'function') returnFocus.focus({ preventScroll: true });
        returnFocus = null;
    });
}());
