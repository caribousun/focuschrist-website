(function () {
    'use strict';

    if (typeof HTMLDialogElement === 'undefined') return;

    const dialog = document.createElement('dialog');
    dialog.className = 'fc-full-image-viewer';
    dialog.setAttribute('aria-label', 'Full-size artwork');
    dialog.innerHTML = '<button class="fc-full-image-close" type="button" aria-label="Close full-size image"></button><div class="fc-full-image-stage"><img alt=""></div>';
    document.body.appendChild(dialog);

    const stage = dialog.querySelector('.fc-full-image-stage');
    const image = dialog.querySelector('img');
    const closeButton = dialog.querySelector('.fc-full-image-close');
    let returnFocus = null;

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
        image.src = trigger.href;
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
        document.body.classList.remove('fc-full-image-open');
        image.removeAttribute('src');
        image.alt = '';
        if (returnFocus && typeof returnFocus.focus === 'function') returnFocus.focus({ preventScroll: true });
        returnFocus = null;
    });
}());
