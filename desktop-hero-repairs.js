/* One artwork element, with its existing study interaction, in two responsive
   locations. Mobile retains the original chapter placement and full artwork. */
document.addEventListener('DOMContentLoaded', () => {
    const picture = document.getElementById('picture-ac-jacob-ladder');
    const opening = document.querySelector('[data-covenant-hero-slot]');
    const chapter = document.querySelector('[data-covenant-art-slot]');
    if (!picture || !opening || !chapter) return;
    const desktop = window.matchMedia('(min-width: 701px)');
    const place = () => desktop.matches ? opening.append(picture) : chapter.after(picture);
    desktop.addEventListener('change', place);
    place();
});
