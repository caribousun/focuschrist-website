/* Keep the existing unique Covenant artwork visible in the opening on every screen. */
document.addEventListener('DOMContentLoaded', () => {
    const picture = document.getElementById('picture-ac-jacob-ladder');
    const opening = document.querySelector('[data-covenant-hero-slot]');
    if (picture && opening) opening.append(picture);
});
