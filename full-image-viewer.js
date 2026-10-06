(function () {
    'use strict';

    if (typeof HTMLDialogElement === 'undefined') return;

    const dialog = document.createElement('dialog');
    dialog.className = 'fc-full-image-viewer';
    dialog.setAttribute('aria-label', 'Full-size artwork');
    dialog.innerHTML = '<button class="fc-full-image-close" type="button" aria-label="Close full-size image"></button><div class="fc-full-image-stage"><img alt=""></div><div class="fc-full-image-tools"><label class="fc-full-image-version" hidden>Image version <select aria-label="Image version"></select></label><a class="fc-full-image-download" download hidden>Download image</a></div>';
    document.body.appendChild(dialog);

    const stage = dialog.querySelector('.fc-full-image-stage');
    const image = dialog.querySelector('img');
    const closeButton = dialog.querySelector('.fc-full-image-close');
    const versionLabel = dialog.querySelector('.fc-full-image-version');
    const versionSelect = dialog.querySelector('select');
    const download = dialog.querySelector('.fc-full-image-download');
    let returnFocus = null;
    let versions = [];

    function localImage(value) {
        try {
            const url = new URL(value, window.location.href);
            return /^https?:$/.test(url.protocol) && url.origin === window.location.origin
                && /\.(?:avif|gif|jpe?g|png|webp)$/i.test(url.pathname) ? url.href : null;
        } catch (_) { return null; }
    }

    function selectImage(src) {
        image.src = src;
        const downloadable = localImage(src);
        download.hidden = !downloadable;
        if (downloadable) {
            download.href = downloadable;
            download.setAttribute('download', new URL(downloadable).pathname.split('/').pop());
        } else download.removeAttribute('href');
    }

    function imageVersions(trigger) {
        versionSelect.replaceChildren();
        versions = [];
        try {
            const supplied = JSON.parse(trigger.dataset.fullImageVersions || '[]');
            if (Array.isArray(supplied) && supplied.length <= 10) {
                supplied.forEach(function (option) {
                    const src = option && typeof option.src === 'string' && localImage(option.src);
                    if (src && typeof option.label === 'string' && option.label.trim()
                            && option.label.length <= 60 && !versions.some(function (item) { return item.src === src; })) {
                        versions.push({ src: src, label: option.label.trim() });
                    }
                });
            }
        } catch (_) { /* A malformed optional list must not prevent viewing. */ }
        const selected = localImage(trigger.href);
        if (!versions.some(function (option) { return option.src === selected; })) versions = [];
        versionLabel.hidden = versions.length < 2;
        versions.forEach(function (option) {
            const node = document.createElement('option');
            node.value = option.src;
            node.textContent = option.label;
            versionSelect.appendChild(node);
        });
        versionSelect.value = selected || '';
    }

    versionSelect.addEventListener('change', function () {
        const option = versions.find(function (item) { return item.src === versionSelect.value; });
        if (option) selectImage(option.src);
    });

    function imageAlt(trigger) {
        const childImage = trigger.querySelector('img');
        const parentDialog = trigger.closest('dialog');
        const detailImage = parentDialog
            ? parentDialog.querySelector('.fc-artwork-detail-media img, .fc-missionary-detail-media img')
            : null;

        return trigger.dataset.fullImageAlt
            || (childImage ? childImage.alt : '')
            || (detailImage ? detailImage.alt : '')
            || 'Full-size artwork';
    }

    function openImage(trigger) {
        if (!image || !closeButton || !trigger.href) return;
        returnFocus = trigger;
        imageVersions(trigger);
        selectImage(trigger.href);
        image.alt = imageAlt(trigger);
        document.body.classList.add('fc-full-image-open');
        dialog.showModal();
        dialog.scrollTop = 0;
        closeButton.focus({ preventScroll: true });
    }

    document.addEventListener('click', function (event) {
        const eventElement = event.target instanceof Element ? event.target : null;
        const trigger = eventElement ? eventElement.closest('a[data-full-image-viewer]') : null;
        if (!trigger || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        openImage(trigger);
    });

    closeButton.addEventListener('click', function () {
        dialog.close();
    });

    dialog.addEventListener('click', function (event) {
        if (event.target === dialog || event.target === stage) dialog.close();
    });

    dialog.addEventListener('cancel', function () {
        document.body.classList.remove('fc-full-image-open');
    });

    dialog.addEventListener('close', function () {
        // Ignore a queued close from an earlier opening of this shared viewer.
        if (dialog.open) return;
        document.body.classList.remove('fc-full-image-open');
        image.removeAttribute('src');
        image.alt = '';
        versions = [];
        versionSelect.replaceChildren();
        versionLabel.hidden = true;
        download.hidden = true;
        download.removeAttribute('href');
        if (returnFocus && typeof returnFocus.focus === 'function') returnFocus.focus({ preventScroll: true });
        returnFocus = null;
    });
}());
