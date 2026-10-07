const fs = require('fs');
const vm = require('vm');

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

class MockElement {
    constructor() {
        this.listeners = {};
        this.dataset = {};
        this.attributes = {};
        this.children = [];
    }

    addEventListener(type, handler) {
        this.listeners[type] = handler;
    }

    setAttribute(name, value) {
        this.attributes[name] = value;
    }

    removeAttribute(name) {
        delete this.attributes[name];
        if (name === 'src') this.src = '';
    }

    focus(options) {
        this.focusOptions = options;
        this.focused = true;
    }
    replaceChildren() { this.children = []; }
    appendChild(node) { this.children.push(node); }
}

global.Element = MockElement;
global.HTMLDialogElement = class {};

const bodyClasses = new Set();
const image = new MockElement();
image.alt = '';
image.src = '';
const stage = new MockElement();
const closeButton = new MockElement();
const versionLabel = new MockElement();
const versionSelect = new MockElement();
const download = new MockElement();
global.window = {location: {href:'https://focuschrist.com/art.html', origin:'https://focuschrist.com'}};
const dialog = new MockElement();
dialog.open = false;
dialog.showCount = 0;
dialog.querySelector = function (selector) {
    if (selector === '.fc-full-image-stage') return stage;
    if (selector === 'img') return image;
    if (selector === '.fc-full-image-close') return closeButton;
    if (selector === '.fc-full-image-version') return versionLabel;
    if (selector === 'select') return versionSelect;
    if (selector === '.fc-full-image-download') return download;
    return null;
};
dialog.showModal = function () {
    this.open = true;
    this.showCount += 1;
};
dialog.close = function () {
    this.open = false;
    if (this.listeners.close) this.listeners.close();
};

const documentListeners = {};
global.document = {
    body: {
        appendChild(element) {
            this.appended = element;
        },
        classList: {
            add(name) { bodyClasses.add(name); },
            remove(name) { bodyClasses.delete(name); },
        },
    },
    createElement(name) {
        if (name === 'option') return new MockElement();
        assert(name === 'dialog', 'viewer must create a native dialog');
        return dialog;
    },
    addEventListener(type, handler) {
        documentListeners[type] = handler;
    },
};

vm.runInThisContext(fs.readFileSync('full-image-viewer.js', 'utf8'));

assert(document.body.appended === dialog, 'viewer dialog was not added to the page');
assert(dialog.attributes['aria-label'] === 'Full-size artwork', 'viewer dialog lacks its accessible name');
assert(typeof documentListeners.click === 'function', 'viewer click delegation is missing');

const trigger = new MockElement();
trigger.href = 'https://focuschrist.com/assets/example.webp';
trigger.dataset.fullImageAlt = 'Sacred artwork of Jesus Christ';
trigger.querySelector = () => null;
trigger.closest = selector => selector === 'a[data-full-image-viewer]' ? trigger : null;

dialog.scrollTop = 250;
let prevented = false;
documentListeners.click({
    target: trigger,
    defaultPrevented: false,
    button: 0,
    metaKey: false,
    ctrlKey: false,
    shiftKey: false,
    altKey: false,
    preventDefault() { prevented = true; },
});

assert(prevented, 'ordinary activation must remain on the current page');
assert(dialog.open, 'ordinary activation did not open the full-image dialog');
assert(dialog.scrollTop === 0, 'new image must open at the top of its viewer');
assert(image.src === trigger.href, 'viewer did not use the exact existing image destination');
assert(image.alt === trigger.dataset.fullImageAlt, 'viewer did not preserve meaningful alternative text');
assert(bodyClasses.has('fc-full-image-open'), 'viewer did not lock page scrolling');
assert(closeButton.focused, 'focus did not move to the close control');
assert(closeButton.focusOptions.preventScroll === true, 'opening focus must not shift the page');
assert(versionLabel.hidden, 'No supplied versions must hide selection');
assert(download.href === trigger.href && !download.hidden, 'Download must use the current local image');

closeButton.listeners.click();
assert(!dialog.open, 'close control did not close the viewer');
assert(!bodyClasses.has('fc-full-image-open'), 'scroll lock remained after close');
assert(trigger.focused, 'focus did not return to the invoking control');
assert(trigger.focusOptions.preventScroll === true, 'returning focus must not shift the page');
assert(image.src === '', 'full image source remained loaded after close');

const showsBeforeModifiedClick = dialog.showCount;
let modifiedPrevented = false;
documentListeners.click({
    target: trigger,
    defaultPrevented: false,
    button: 0,
    metaKey: false,
    ctrlKey: true,
    shiftKey: false,
    altKey: false,
    preventDefault() { modifiedPrevented = true; },
});
assert(!modifiedPrevented, 'modified click must retain the original browser behavior');
assert(dialog.showCount === showsBeforeModifiedClick, 'modified click incorrectly opened the viewer');

documentListeners.click({
    target: trigger,
    defaultPrevented: false,
    button: 0,
    metaKey: false,
    ctrlKey: false,
    shiftKey: false,
    altKey: false,
    preventDefault() {},
});
dialog.listeners.click({target: stage});
assert(!dialog.open, 'stage backdrop did not close the viewer');

documentListeners.click({
    target: trigger,
    defaultPrevented: false,
    button: 0,
    metaKey: false,
    ctrlKey: false,
    shiftKey: false,
    altKey: false,
    preventDefault() {},
});
dialog.listeners.cancel();
dialog.close();
assert(!bodyClasses.has('fc-full-image-open'), 'Escape cancellation did not clear scroll locking');

function open() {
    documentListeners.click({target:trigger, button:0, preventDefault(){}});
}
const phone = 'https://focuschrist.com/assets/example.webp';
const wide = 'https://focuschrist.com/assets/example-wide.webp';
trigger.dataset.fullImageVersions = JSON.stringify([{label:'Phone version',src:phone},{label:'Wide version',src:wide}]);
open();
assert(!versionLabel.hidden && versionSelect.children.length === 2, 'Two valid versions must be selectable');
assert(versionSelect.value === phone && image.src === phone, 'Opening must select clicked image');
versionSelect.value = wide;
versionSelect.listeners.change();
assert(image.src === wide && download.href === wide, 'Switching version must update image and download together');
assert(download.attributes.download === 'example-wide.webp', 'Download filename must match selected version');
assert(image.alt === trigger.dataset.fullImageAlt && dialog.open, 'Switching must preserve alt and open viewer');
versionSelect.value = 'javascript:alert(1)';
versionSelect.listeners.change();
assert(image.src === wide, 'Unlisted selection must be ignored');
closeButton.listeners.click();
open();
dialog.listeners.close();
assert(dialog.open && image.src === phone && !versionLabel.hidden, 'Queued prior close must not erase reopened viewer');
assert(versionSelect.value === phone && download.href === phone, 'Reopening starts at clicked source, not last selected version');
dialog.close();
for (const invalid of ['{broken', '{}', JSON.stringify([{label:'External',src:'https://example.com/a.webp'},{label:'Unsafe',src:'javascript:alert(1)'}]), JSON.stringify([{label:'HTML',src:'/index.html'}])]) {
    trigger.dataset.fullImageVersions = invalid;
    open();
    assert(versionLabel.hidden && image.src === phone, 'Invalid optional options must retain original viewing');
    dialog.close();
}
trigger.dataset.fullImageVersions = JSON.stringify([{label:'Phone version',src:phone},{label:'Wide version',src:wide},{label:'Duplicate',src:wide},{label:'External',src:'https://example.com/a.webp'}]);
open();
assert(versionSelect.children.length === 2, 'Duplicate and external options must be discarded');
dialog.close();
trigger.href = 'https://example.com/art.webp';
open();
assert(download.hidden && versionLabel.hidden, 'External fallback must not offer a local download or options');
dialog.close();

console.log('Full-image viewer runtime QA: PASS');
console.log('Same-page open, close/reopen focus, Escape, modifier fallback, version selection/download binding, malformed/external options and queued close verified');
