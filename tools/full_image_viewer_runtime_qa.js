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

    focus() {
        this.focused = true;
    }
}

global.Element = MockElement;
global.HTMLDialogElement = class {};

const bodyClasses = new Set();
const image = new MockElement();
image.alt = '';
image.src = '';
const stage = new MockElement();
const closeButton = new MockElement();
const dialog = new MockElement();
dialog.open = false;
dialog.showCount = 0;
dialog.querySelector = function (selector) {
    if (selector === '.fc-full-image-stage') return stage;
    if (selector === 'img') return image;
    if (selector === '.fc-full-image-close') return closeButton;
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
assert(image.src === trigger.href, 'viewer did not use the exact existing image destination');
assert(image.alt === trigger.dataset.fullImageAlt, 'viewer did not preserve meaningful alternative text');
assert(bodyClasses.has('fc-full-image-open'), 'viewer did not lock page scrolling');
assert(closeButton.focused, 'focus did not move to the close control');

closeButton.listeners.click();
assert(!dialog.open, 'close control did not close the viewer');
assert(!bodyClasses.has('fc-full-image-open'), 'scroll lock remained after close');
assert(trigger.focused, 'focus did not return to the invoking control');
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

console.log('Full-image viewer runtime QA: PASS');
console.log('Same-page open, exact source, close, Escape cleanup, focus return, and modified-click fallback verified');
