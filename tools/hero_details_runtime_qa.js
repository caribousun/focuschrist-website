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
    ['living-christ-art', '/art/The-Living-Christ.png', 'The Living Christ', '/art-study/the-living-christ.html#scripture-study'],
    ['good-shepherd-art', '/art/The-Good-Shephard.jpg', 'The Good Shepherd', '/art-study/the-good-shepherd.html#scripture-study'],
    ['little-children-art', '/art/Suffer-the-Little-Children.jpg', 'Suffer the Little Children', '/art-study/suffer-the-little-children.html#scripture-study'],
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
vm.runInNewContext(fs.readFileSync('hero-details.js', 'utf8'), {
    document, window, URL, URLSearchParams, HTMLDialogElement: function () {},
});

cases.forEach(([record, href, expectedTitle, expectedStudy], index) => {
    let prevented = false;
    triggers[index].listeners.click({ button: 0, preventDefault() { prevented = true; } });
    assert(prevented && dialog.open, `${record} must open the hero detail dialog`);
    assert.strictEqual(selectors['img'].src, `https://focuschrist.com${href}`);
    assert.strictEqual(selectors['h2'].textContent, expectedTitle);
    assert.strictEqual(selectors['.fc-artwork-detail-copy'].children.length, 2);
    assert.strictEqual(new URL(selectors['[data-hero-study-link]'].href).pathname + new URL(selectors['[data-hero-study-link]'].href).hash, expectedStudy);
    assert.strictEqual(selectors['[data-full-image-viewer]'].href, `https://focuschrist.com${href}`);
    assert(new URL(selectors['[data-hero-ask-link]'].href).searchParams.get('return').includes('/art-study/'));
    dialog.close();
    assert(triggers[index].focused, `${record} must restore focus when closed`);
});

assert(!bodyClasses.has('fc-dialog-open'));
console.log('Hero details runtime QA passed: all four art-study heroes open their own reflection, study, Ask, and full-size routes.');
