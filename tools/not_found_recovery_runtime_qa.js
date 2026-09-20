// A custom 404 keeps the requested URL. Check recovery with and without shared JS.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { JSDOM, VirtualConsole } = require('jsdom');
const root = path.resolve(__dirname, '..');
const ref = process.argv.find(arg => arg.startsWith('--ref='))?.slice(6);
const read = file => ref ? execFileSync('git', ['show', `${ref}:${file}`], { cwd: root, encoding: 'utf8' }) : fs.readFileSync(path.join(root, file), 'utf8');
const origin = 'https://focuschrist.com';
const missing = ['/missing.html', '/answers/missing.html', '/missing/nested/page.html', '/answers/deeper/missing/'];
const virtualConsole = new VirtualConsole();
const runtimeErrors = [];
virtualConsole.on('jsdomError', error => runtimeErrors.push(error.message));
function checkLocalDestinations(document, context) {
    for (const node of document.querySelectorAll('a[href], link[href], script[src]')) {
        const raw = node.getAttribute('href') || node.getAttribute('src');
        if (raw.startsWith('#')) continue;
        const url = new URL(raw, document.URL);
        if (url.origin !== origin) continue;
        assert(fs.existsSync(path.join(root, decodeURIComponent(url.pathname))), `${context}: ${raw} resolves to missing ${url.pathname}`);
    }
    assert.equal(document.querySelector('.nav-logo').href, origin + '/index.html');
    assert.equal(document.querySelector('[aria-label="Page recovery links"] a').href, origin + '/index.html');
}
for (const location of missing) {
    const dom = new JSDOM(read('404.html'), { url: origin + location, runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole });
    const { window } = dom;
    checkLocalDestinations(window.document, 'Without JavaScript at ' + location);
    window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
    window.eval(read('site-common.js'));
    window.document.dispatchEvent(new window.Event('DOMContentLoaded'));
    assert.deepEqual(runtimeErrors, [], 'Shared controller initializes without exceptions');
    assert(window.document.querySelector('script[data-focuschrist-header-scroll]'), 'Shared initialization completed');
    checkLocalDestinations(window.document, 'With JavaScript at ' + location);
    assert.equal(window.document.querySelector('.fc-skip-link').getAttribute('href')[0], '#', 'Skip link remains on missing page');
    dom.window.close();
}
// Preserve normal page routing. Recovery changes must remain scoped to the 404.
for (const file of ['index.html', 'answers/stand-forever.html']) {
    const dom = new JSDOM(read(file), { url: origin + '/' + file, runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole });
    dom.window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
    dom.window.eval(read('site-common.js'));
    dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded'));
    assert.deepEqual(runtimeErrors, [], file + ': no runtime exceptions');
    const nav = dom.window.document.querySelector('.nav-logo');
    assert.equal(nav.href, origin + '/index.html');
    for (const script of dom.window.document.querySelectorAll('script[data-focuschrist-header-scroll], script[data-focuschrist-scripture-library]')) {
        assert.equal(new URL(script.src).pathname.split('/').length, 2, file + ': shared asset stays at root');
    }
    dom.window.close();
}
console.log('NOT FOUND RECOVERY QA PASS: four missing URL depths, before/after shared JS, local assets/recovery links, preserved skip links and two normal-page controls');
