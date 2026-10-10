/* Offline production-script regression for shared gallery links. No network. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(process.env.GALLERY_QA_ROOT || path.join(__dirname, '..'));
const dataRoot = path.resolve(process.env.GALLERY_QA_DATA_ROOT || root);
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const catalog = JSON.parse(fs.readFileSync(path.join(dataRoot, 'art-gallery.json'), 'utf8'));
const cases = [];
const picturePairs = [["art-c2a7f9036414", "art-fb9041593ebb"], ["art-e8aa2c14211e", "art-bf3eafcc71cc"], ["art-82ed9c00b587", "art-cfc810b044b3"], ["art-89e864cd34e4", "art-c4242967b8a6"], ["art-6c98467750b1", "art-37ba51e6c512"], ["art-30da387593ee", "art-629e01aebd7c"], ["art-d117f116ef39", "art-fe5e1ed41d9b"], ["art-71d0e77d29ca", "art-b02a6bb5283f"], ["art-b0d390116e40", "art-668c171076f3"], ["art-e3bea40c689d", "art-7fce6f8c3aab"], ["art-8626a0013555", "art-8b3bee192219"], ["art-88364b952e48", "art-f9e2fdf16d37"], ["art-01f5918c3164", "art-cfc810b044b3"], ["art-a034c9d00751", "art-f9e2fdf16d37"], ["art-d2d41e92a628", "art-37ba51e6c512"]];
const sourceOld = 'source-44bc8f90e9cf', sourceNew = 'source-0f854bc93cec';
const sourcePairs = [["source-44bc8f90e9cf", "source-0f854bc93cec"], ["source-b8f1acb4ee67", "source-5ea3c750ad6d"], ["source-d203f8844981", "source-41ace1913814"], ["source-b8fb45227bb3", "source-0dadddbb503d"], ["source-9ef33a38a3ec", "source-d8e9ad0fdf7c"], ["source-6d9341ce7a52", "source-be42ad339302"], ["source-8dace3b6bf78", "source-4a4ae352d87f"], ["source-94d28fae2282", "source-6cd5e5535101"], ["source-a6b610e8d1ce", "source-85cb8f284453"], ["source-e30c8ddd579a", "source-d1ce88bbb045"], ["source-a3b8e155238a", "source-12af89590691"], ["source-0b724121e66b", "source-5ea3c750ad6d"], ["source-05cf7c0e2b6a", "source-12af89590691"], ["source-5a24b826f3f4", "source-0dadddbb503d"]];
// Validate the actual production tables, not merely duplicate test data.
function guardAliases(file, name, expected, canonicalIds) {
    const match = read(file).match(new RegExp('const ' + name + ' = new Map\\((\\[[\\s\\S]*?\\])\\);'));
    assert(match, name + ' explicit table present');
    const pairs = JSON.parse(match[1].replace(/'/g, '"'));
    assert.deepEqual(pairs, expected, name + ' preserves exact reviewed mappings');
    const keys = pairs.map(p => p[0]), targets = pairs.map(p => p[1]);
    assert.equal(new Set(keys).size, keys.length, name + ' duplicate-key collision');
    // Exact reviewed successors intentionally preserve both earlier and immediate prior links.
    const allowedFanIn = name === 'pictureAliases' ? ["art-cfc810b044b3", "art-f9e2fdf16d37", "art-37ba51e6c512"] : ["source-5ea3c750ad6d", "source-12af89590691", "source-0dadddbb503d"];
    for (const target of new Set(targets)) assert.equal(targets.filter(v => v === target).length, allowedFanIn.includes(target) ? 2 : 1, name + ' exact reviewed fan-in');
    for (const [oldId, newId] of pairs) {
        assert(!keys.includes(newId), name + ' no chains or cycles');
        assert.equal(canonicalIds.filter(id => id === oldId).length, 0, name + ' retired key cannot shadow a current record');
        assert.equal(canonicalIds.filter(id => id === newId).length, 1, name + ' exact unique current target');
    }
}
guardAliases('art-gallery.js', 'pictureAliases', picturePairs, catalog.artworks.map(a => a.id));
guardAliases('art-gallery-bridge.js', 'sourceAliases', sourcePairs, catalog.artworks.flatMap(a => a.occurrences.map(s => s.id)));

const marriage = catalog.artworks.find(a => a.id === picturePairs[0][1]);
const portrait = catalog.artworks.find(a => a.id === picturePairs[1][1]);
assert(marriage && portrait);
assert.equal(marriage.occurrences.length, 1);
assert.equal(marriage.occurrences[0].page, '/answers/who-was-joseph-smith.html');
assert.equal(marriage.occurrences[0].id, sourceNew);
for (const [oldId, newId] of picturePairs) {
    assert.equal(catalog.artworks.filter(a => a.id === newId).length, 1);
    assert.equal(catalog.artworks.filter(a => a.id === oldId).length, 0);
}
assert.equal(catalog.artworks.flatMap(a => a.occurrences).filter(s => s.id === sourceOld).length, 0);
const settle = () => new Promise(resolve => setImmediate(resolve));

async function gallery(id, expected, removeTarget = false) {
    const dom = new JSDOM(read('art-gallery.html'), {url: 'https://focuschrist.com/art-gallery.html?picture=' + id, runScripts: 'outside-only'});
    const w = dom.window;
    w.fetch = async () => ({ok: true, json: async () => ({...catalog, artworks: removeTarget ? catalog.artworks.filter(a => a.id !== expected) : catalog.artworks})});
    w.eval(read('art-gallery.js'));
    await settle();
    const frame = w.document.getElementById('artGalleryFrame');
    if (expected && !removeTarget) {
        const art = catalog.artworks.find(a => a.id === expected);
        assert.equal(new URL(w.location.href).searchParams.get('picture'), expected, id + ' canonical share');
        assert.equal(new URL(frame.src).searchParams.get('gallery-art'), art.occurrences[0].id, id + ' exact source');
        assert.equal(new URL(frame.src).pathname, art.occurrences[0].page);
        assert.equal(w.document.getElementById('artGalleryFallback').href, 'https://focuschrist.com' + art.occurrences[0].page + '?gallery-art=' + art.occurrences[0].id);
        w.document.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
        assert.equal(frame.src, 'about:blank', 'pending open cancels');
        assert.equal(w.document.activeElement.closest('[data-gallery-card]').dataset.galleryCard, expected, 'focus returns to canonical card');
    } else {
        assert(w.document.getElementById('artGalleryCount').textContent.includes('no longer in the gallery'), id + ' rejected');
        assert(!frame.src || frame.src === 'about:blank', id + ' never selects another picture');
    }
    cases.push('gallery:' + id + (removeTarget ? ':missing-target' : ''));
    w.close();
}

async function bridge(id, query = 'gallery-art', wrongPage = false, removeTarget = false, embedded = false, artwork = marriage) {
    const source = artwork.occurrences[0];
    const page = wrongPage ? (source.page === '/church-history.html' ? '/answers/who-was-joseph-smith.html' : '/church-history.html') : source.page;
    const html = fs.readFileSync(path.join(dataRoot, source.page.slice(1)), 'utf8');
    const dom = new JSDOM(html, {url: 'https://focuschrist.com' + page + '?' + query + '=' + id + (embedded ? '&gallery-embed=1&keep=yes#study' : ''), runScripts: 'outside-only'});
    const w = dom.window, d = w.document;
    const messages = [];
    if (embedded) Object.defineProperty(w, 'parent', {value: {location: new URL('https://focuschrist.com/art-gallery.html'), postMessage: (data, origin) => messages.push({data, origin})}});
    const trigger = d.querySelector(source.selector);
    assert(trigger, 'actual source selector exists');
    trigger.setAttribute('data-topic-artwork-detail', '');
    const panelId = source.kind === 'artwork' ? 'artworkDetailDialog' : 'topicArtworkDetailDialog';
    const panel = d.getElementById(panelId) || d.createElement('dialog');
    panel.id = panelId;
    if (!panel.isConnected) d.body.append(panel);
    panel.innerHTML = '<div class="fc-artwork-detail-actions"><button data-artwork-detail-continue>Continue</button></div>';
    let clicks = 0, positioned = false;
    trigger.addEventListener('click', event => {event.preventDefault(); clicks++; panel.open = true;});
    trigger.scrollIntoView = () => {positioned = true;};
    w.fetch = async () => ({ok: true, json: async () => ({...catalog, artworks: removeTarget ? catalog.artworks.filter(a => a.id !== artwork.id) : catalog.artworks})});
    await w.eval(read('art-gallery-bridge.js'));
    const valid = (id === source.id || sourcePairs.some(([oldId, newId]) => oldId === id && newId === source.id)) && !wrongPage && !removeTarget;
    if (valid) {
        assert.equal(d.documentElement.dataset.galleryArtworkError, undefined);
        assert.equal(positioned, !embedded);
        if (query === 'gallery-position') {
            assert.equal(clicks, 0, 'position never opens a panel');
            assert.equal(d.activeElement, trigger);
        } else {
            assert.equal(clicks, 1, 'source opens exact trigger once');
            assert.equal(d.documentElement.dataset.galleryArtworkReady, source.id);
        }
        if (embedded) {
            const original = new URL(panel.querySelector('[data-gallery-original]').href);
            assert.equal(original.searchParams.get('gallery-art'), source.id, 'embedded original link canonical');
            assert.equal(original.searchParams.get('gallery-embed'), null);
            assert.equal(original.searchParams.get('keep'), 'yes');
            assert.equal(original.hash, '#study');
            assert(messages.some(m => m.origin === 'https://focuschrist.com' && m.data.action === 'ready'));
            panel.querySelector('[data-artwork-detail-continue]').click();
            const navigation = new URL(messages.find(m => m.data.action === 'navigate').data.url);
            assert.equal(navigation.searchParams.get('gallery-position'), source.id);
            assert.equal(navigation.searchParams.get('gallery-art'), null);
            assert.equal(navigation.searchParams.get('keep'), 'yes');
        }
    } else {
        assert.equal(clicks, 0);
        assert.equal(positioned, false);
        assert.equal(d.documentElement.dataset.galleryArtworkError, 'Unknown artwork source');
    }
    cases.push('bridge:' + query + ':' + id + (wrongPage ? ':wrong-page' : '') + (removeTarget ? ':missing-target' : '') + (embedded ? ':embedded' : ''));
    w.close();
}

(async () => {
    for (const [oldId, newId] of picturePairs) {
        await gallery(oldId, newId); await gallery(newId, newId); await gallery(oldId, newId, true);
    }
    for (const id of ['art-unknown', '__proto__', 'constructor']) await gallery(id);
    for (const query of ['gallery-art', 'gallery-position']) {
        for (const id of [sourceOld, sourceNew]) {
            await bridge(id, query); await bridge(id, query, true); await bridge(id, query, false, true);
        }
        for (const id of ['source-unknown', '__proto__', 'constructor']) await bridge(id, query);
    }
    await bridge(sourceOld, 'gallery-art', false, false, true);
    assert.equal(portrait.occurrences.length, 1);
    assert.equal(portrait.occurrences[0].id, 'source-b61354e94a0c');
    assert.equal(portrait.occurrences[0].page, '/church-history.html');
    for (const query of ['gallery-art', 'gallery-position'])
        await bridge(portrait.occurrences[0].id, query, false, false, false, portrait);
    for (const [oldId, newId] of sourcePairs.slice(1)) {
        const artwork = catalog.artworks.find(a => a.occurrences.some(s => s.id === newId));
        assert(artwork && artwork.occurrences.length === 1, 'one current owning record');
        for (const query of ['gallery-art', 'gallery-position']) {
            for (const id of [oldId, newId]) {
                await bridge(id, query, false, false, false, artwork);
                await bridge(id, query, true, false, false, artwork);
                await bridge(id, query, false, true, false, artwork);
            }
        }
        await bridge(oldId, 'gallery-art', false, false, true, artwork);
    }
    console.log(JSON.stringify({status: 'PASS', count: cases.length, cases}));
})().catch(error => {console.error(error); process.exitCode = 1;});
