const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

class Element {
    constructor() {
        this.listeners = {};
        this.dataset = {};
        this.attributes = {};
        this.children = [];
        this.classList = { contains: () => false };
    }
    addEventListener(name, fn) { this.listeners[name] = fn; }
    setAttribute(name, value) { this.attributes[name] = value; }
    removeAttribute(name) { delete this.attributes[name]; }
    replaceChildren() { this.children = []; }
    appendChild(node) { this.children.push(node); }
    focus(options) { this.focused = true; this.focusOptions = options; }
}

const selectors = {};
for (const selector of [
    'img', 'h2', '.fc-artwork-detail-copy', '[data-hero-source-link]',
    '[data-hero-study-link]', '[data-hero-ask-link]', '[data-full-image-viewer]'
]) selectors[selector] = new Element();
const closeTop = new Element();
const closeAction = new Element();
const dialog = new Element();
dialog.querySelector = selector => selector === '[data-hero-close]' ? closeTop : selectors[selector];
dialog.querySelectorAll = selector => selector === '[data-hero-close]' ? [closeTop, closeAction] : [];
dialog.showModal = () => { dialog.open = true; };
dialog.close = () => { dialog.open = false; dialog.listeners.close(); };

const cases = [
    ['joseph-gateway-20261004', '/assets/heroes/joseph-gateway-20261004.png', 'Joseph beside the river', '/joseph-smith-likeness.html#joseph-study-entrance'],
    ['joseph-research-20261004', '/assets/heroes/joseph-research-20261004.png', 'Looking closely at Joseph', '/joseph-smith-portrait-research.html#portrait-section-1'],
    ['birth-of-christ', '/assets/page-art/birth-of-christ/12-nativity-hero-full.webp', 'Mary lays her newborn Son in a manger', '/birth-of-christ.html#promised-son'],
    ['topic-living-christ', '/assets/heroes/topics/living-christ-full.webp', 'He lives and ministers', '/art-study/the-living-christ.html#scripture-study'],
    ['good-shepherd-art', '/art/The-Good-Shephard.jpg', 'The Good Shepherd', '/art-study/the-good-shepherd.html#scripture-study'],
    ['little-children-art', '/art/Suffer-the-Little-Children-approved-20260929.webp', 'Suffer the Little Children', '/art-study/suffer-the-little-children.html#scripture-study'],
    ['be-still-art', '/art/Be-Still.png', 'Be Still', '/art-study/be-still.html#psalm-context'],
];
const triggers = cases.map(([record, href, title]) => {
    const trigger = new Element();
    trigger.dataset = {
        heroRecord: record,
        fullImageAlt: `${title} artwork`,
        heroAsk: `/ask.html?topic=${encodeURIComponent(title)}`,
    };
    trigger.href = `https://focuschrist.com${href}`;
    return trigger;
});
const bodyClasses = new Set();
const document = {
    currentScript: { src: 'https://focuschrist.com/hero-details.js?v=test' },
    getElementById: () => null,
    createElement: () => new Element(),
    querySelectorAll: selector => selector === 'a[data-hero-viewer]' ? triggers : [],
    querySelector: () => null,
    body: {
        appendChild(node) { assert.strictEqual(node, dialog); },
        classList: { add: name => bodyClasses.add(name), remove: name => bodyClasses.delete(name) },
    },
};
document.createElement = tag => tag === 'dialog' ? dialog : new Element();

const window = { location: { href: 'https://focuschrist.com/art-study/the-good-shepherd.html', pathname: '/art-study/the-good-shepherd.html' } };
// Controller integration tests use a bounded helper stub. The helper's real
// allowlist and browser source selection have their own independent regression.
window.fcHeroImageSource = trigger => trigger.selectedArtwork || trigger.href;
window.fcHeroImageOptions = trigger => trigger.imageOptions || [];
vm.runInNewContext(fs.readFileSync('hero-details.js', 'utf8'), {
    document, window, URL, URLSearchParams, HTMLDialogElement: function () {},
});

cases.forEach(([record, href, expectedTitle, expectedStudy], index) => {
    window.location.pathname = record.startsWith('joseph-') ? expectedStudy.split('#')[0] : record === 'birth-of-christ' ? '/birth-of-christ.html' : '/art-study/the-good-shepherd.html';
    let prevented = false;
    triggers[index].listeners.click({ button: 0, preventDefault() { prevented = true; } });
    assert(prevented && dialog.open, `${record} must open the hero detail dialog`);
    assert.strictEqual(selectors['img'].src, `https://focuschrist.com${href}`);
    assert.strictEqual(selectors['h2'].textContent, expectedTitle);
    assert.strictEqual(selectors['.fc-artwork-detail-copy'].children.length, 2);
    assert.strictEqual(new URL(selectors['[data-hero-study-link]'].href).pathname + new URL(selectors['[data-hero-study-link]'].href).hash, expectedStudy);
    assert.strictEqual(selectors['[data-full-image-viewer]'].href, `https://focuschrist.com${href}`);
    assert.strictEqual(new URL(selectors['[data-hero-ask-link]'].href).searchParams.get('return'), window.location.pathname + '?hero=1');
    if(record.startsWith('joseph-')) assert.strictEqual(selectors['[data-hero-source-link]'].href,'https://history.churchofjesuschrist.org/media-exhibit/sutcliffe-maudsley/joseph-smith-in-black-suit-and-top-hat?from=home&lang=eng');
    if (record === 'birth-of-christ') {
        assert.strictEqual(selectors['[data-hero-source-link]'].href, 'https://www.churchofjesuschrist.org/study/scriptures/nt/luke/2?lang=eng&id=p6-p7#p6');
        assert(new URL(selectors['[data-hero-ask-link]'].href).searchParams.get('topic').includes('newborn'));
    }
    dialog.close();
    assert(triggers[index].focused, `${record} must restore focus when closed`);
});

assert(!bodyClasses.has('fc-dialog-open'));

// The responsive hero can use a different approved composition from its fallback
// link. The reflection panel and full-size destination must follow that selection.
function expectImage(trigger, expected, label) {
    trigger.listeners.click({ button: 0, preventDefault() {} });
    assert(dialog.open, `${label}: dialog must open`);
    assert.strictEqual(selectors.img.src, expected, `${label}: reflection image`);
    assert.strictEqual(selectors['[data-full-image-viewer]'].href, expected, `${label}: full-size destination`);
    assert.strictEqual(selectors['[data-full-image-viewer]'].dataset.fullImageVersions, JSON.stringify(trigger.imageOptions || []), `${label}: version metadata`);
    assert.strictEqual(selectors['[data-full-image-viewer]'].dataset.fullImageAlt, trigger.dataset.fullImageAlt);
    dialog.close();
    assert(trigger.focused, `${label}: focus returns to the hero`);
}
const responsiveCases = [
    ['good-shepherd-art', 'the-good-shepherd', 'shepherd-desktop-exact-20260929.webp'],
    ['little-children-art', 'suffer-the-little-children', 'children-responsive-desktop-20260929.webp'],
    ['be-still-art', 'be-still', 'be-still-responsive-desktop-20260929.webp'],
];
for (const [record, page, asset] of responsiveCases) {
    const markup = fs.readFileSync(`art-study/${page}.html`, 'utf8');
    assert(markup.includes(`/assets/heroes/${asset}`), `${page}: fixture matches page source`);
    const trigger = triggers.find(item => item.dataset.heroRecord === record);
    const originalHref = trigger.href;
    const selectedImage = { currentSrc: `https://focuschrist.com/assets/heroes/${asset}` };
    trigger.classList.contains = name => name === 'fc-art-study-hero';
    trigger.querySelector = selector => selector === 'picture.fc-exact-hero-picture > img' ? selectedImage : null;
    trigger.selectedArtwork = selectedImage.currentSrc;
    trigger.imageOptions = [{label:'Phone version',src:originalHref},{label:'Wide version',src:selectedImage.currentSrc}];
    expectImage(trigger, selectedImage.currentSrc, `${page} desktop`);
    assert.strictEqual(trigger.href, originalHref, `${page}: preserve fallback link`);
    if (record === 'little-children-art') {
        selectedImage.currentSrc = 'https://focuschrist.com/assets/heroes/children-phone-responsive-20260929.webp';
        trigger.selectedArtwork = selectedImage.currentSrc;
        assert(markup.includes('/assets/heroes/children-phone-responsive-20260929.webp'));
        expectImage(trigger, selectedImage.currentSrc, 'children resized to phone and reopened');
    }
    selectedImage.currentSrc = '';
    trigger.selectedArtwork = '';
    expectImage(trigger, originalHref, `${page} pending image fallback`);
    trigger.querySelector = () => null;
    expectImage(trigger, originalHref, `${page} absent picture fallback`);
}
// An incidental responsive image must not replace intentional full-size links
// on unrelated hero types, including the approved Joseph artwork.
for (const trigger of triggers.slice(0, 4)) {
    trigger.querySelector = () => ({ currentSrc: 'https://focuschrist.com/unrelated-preview.webp' });
    expectImage(trigger, trigger.href, `${trigger.dataset.heroRecord} retains explicit artwork`);
}
assert(!bodyClasses.has('fc-dialog-open'));
const birth = triggers.find(trigger => trigger.dataset.heroRecord === 'birth-of-christ');
birth.selectedArtwork = 'https://focuschrist.com/assets/heroes/birth-responsive-20260929.webp';
expectImage(birth, birth.selectedArtwork, 'Birth selected approved expanded composition');
delete window.fcHeroImageSource;
delete window.fcHeroImageOptions;
birth.imageOptions = [];
expectImage(birth, birth.href, 'Missing helper preserves explicit fallback');
console.log('Hero details runtime QA passed: seven existing routes; three responsive desktop compositions; children phone after resize/reopen; empty/missing image fallbacks; four unrelated heroes unchanged.');
