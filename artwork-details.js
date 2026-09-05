(function () {
    'use strict';

    const dialog = document.getElementById('artworkDetailDialog');
    if (!dialog || typeof dialog.showModal !== 'function') return;

    const image = document.getElementById('artworkDetailImage');
    const eyebrow = document.getElementById('artworkDetailEyebrow');
    const title = document.getElementById('artworkDetailTitle');
    const copy = document.getElementById('artworkDetailCopy');
    const source = document.getElementById('artworkDetailSource');
    const study = document.getElementById('artworkDetailStudy');
    const fullImage = document.getElementById('artworkDetailFullImage');
    const closeButtons = dialog.querySelectorAll('[data-artwork-detail-close]');
    const isHome = window.location.pathname === '/' || window.location.pathname === '/index.html';
    const ask = document.createElement('a');
    ask.className = 'fc-button';
    ask.textContent = 'Ask About This Artwork';
    ask.hidden = true;
    if (fullImage) fullImage.before(ask);
    let returnFocus = null;

    function openDetail(key, trigger) {
        const record = document.querySelector('[data-artwork-detail-content="' + key + '"]');
        if (!record || !image || !eyebrow || !title || !copy || !source || !study || !fullImage) return;

        const detailEyebrow = record.querySelector('[data-detail-eyebrow]');
        const detailTitle = record.querySelector('[data-detail-title]');
        const paragraphs = record.querySelectorAll('[data-detail-paragraph]');

        eyebrow.textContent = detailEyebrow ? detailEyebrow.textContent : 'Explore the artwork';
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

        ask.hidden = true;
        ask.removeAttribute('href');
        if (isHome && record.dataset.detailTopic) {
            const params = new URLSearchParams();
            params.set('art', title.textContent);
            params.set('topic', record.dataset.detailTopic);
            params.set('return', 'index.html?artwork=' + encodeURIComponent(key));
            ask.href = 'ask.html?' + params.toString() + '#ask-question';
            ask.hidden = false;
        }

        if (record.dataset.detailStudy) {
            study.href = record.dataset.detailStudy;
            study.textContent = record.dataset.detailStudyLabel || 'Read the Art Study';
            study.hidden = false;
        } else {
            study.hidden = true;
            study.removeAttribute('href');
        }

        returnFocus = trigger;
        document.body.classList.add('fc-dialog-open');
        dialog.showModal();
        dialog.scrollTop = 0;
        const closeButton = dialog.querySelector('[data-artwork-detail-close]');
        if (closeButton) closeButton.focus({ preventScroll: true });
    }

    document.querySelectorAll('[data-artwork-detail]').forEach(function (trigger) {
        trigger.addEventListener('click', function (event) {
            if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            openDetail(trigger.dataset.artworkDetail, trigger);
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
        image.removeAttribute('src');
        if (returnFocus && typeof returnFocus.focus === 'function') returnFocus.focus({ preventScroll: true });
        returnFocus = null;
    });

    if (isHome) {
        const requested = new URLSearchParams(window.location.search).get('artwork');
        const trigger = Array.from(document.querySelectorAll('[data-artwork-detail]')).find(function (item) {
            return item.dataset.artworkDetail === requested;
        });
        if (trigger) openDetail(trigger.dataset.artworkDetail, trigger);
    }
}());
