'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'hero-image-source.js'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'docs/hero-image-source-map.json'), 'utf8'));
const rules = JSON.parse(source.match(/const SOURCE_RULES = (\[[^\n]+\]);/)[1]);
assert.deepEqual(rules, manifest.records.map(row => ({route: '/' + row.route, selector: row.selector, original: '/' + row.href, alternates: row.confirmed_variants.map(v => '/' + v.asset), versions: {
    phone: '/' + (row.confirmed_variants.find(v => v.condition.includes('max-width'))?.asset || row.href),
    wide: '/' + (row.confirmed_variants.find(v => v.condition.includes('min-width'))?.asset || row.href)
}})), 'Embedded rules and version choices must exactly match the reviewed map');
assert.equal(rules.length, 45);
assert.equal(new Set(rules.map(x => x.route)).size, 39);
assert.equal(rules.reduce((n, x) => n + x.alternates.length, 0), 49);
assert.equal(new Set(rules.map(x => x.route + '|' + x.original)).size, rules.length, 'No ambiguous original mapping');
const expectedRoutes = new Set(manifest.records.map(row => row.route));
const canonicalRoutes = [...fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => new URL(match[1]).pathname.slice(1) || 'index.html');
for (const route of canonicalRoutes) {
    const html = fs.readFileSync(path.join(root, route), 'utf8');
    const scripts = [...html.matchAll(/<script\b[^>]*\bsrc="([^"]+)"[^>]*>/g)];
    const helpers = scripts.filter(match => /(?:^|\/)hero-image-source\.js(?:\?|$)/.test(match[1]));
    assert.equal(helpers.length, expectedRoutes.has(route) ? 1 : 0, route + ': exact helper consumer set');
    if (!expectedRoutes.has(route)) continue;
    assert(helpers[0][1].endsWith('hero-image-source.js?v=20261006-visible-art-1'));
    assert(/\bdefer\b/.test(helpers[0][0]) && !/\basync\b/.test(helpers[0][0]));
    for (const row of manifest.records.filter(row => row.route === route)) {
        const controller = scripts.find(match => match[1].includes(row.controller + '.js?'));
        assert(controller && helpers[0].index < controller.index, route + ': helper loads before controller');
        assert(controller[1].endsWith(row.controller + '.js?v=20261006-visible-art-1'));
    }
}
for (const row of manifest.records) {
    assert(fs.existsSync(path.join(root, row.route)));
    assert(fs.existsSync(path.join(root, row.href)));
    for (const variant of row.confirmed_variants) {
        assert(fs.existsSync(path.join(root, variant.asset)));
        assert(variant.condition && variant.mechanism && variant.evidence);
    }
}
const origin = 'https://focuschrist.com';
const style = values => Object.assign({display: 'block', visibility: 'visible', opacity: '1', content: '""', backgroundImage: 'none'}, values);
const window = {location: {origin, href: origin + '/', pathname: '/'}, getComputedStyle: (element, pseudo) => pseudo ? element.before : element.style};
vm.runInNewContext(source, {window, URL});
function element() {
    return {isConnected: true, nodeType: 1, parentElement: null, style: style(), before: style(), getClientRects() { return [{}]; }};
}
function fixture(rule, selected, mechanism = 'picture') {
    window.location.pathname = rule.route;
    window.location.href = origin + rule.route;
    const trigger = element(); trigger.href = origin + rule.original;
    trigger.matches = selector => selector === rule.selector;
    trigger.picture = null;
    trigger.querySelector = selector => selector === 'picture img' ? trigger.picture : null;
    if (mechanism === 'picture') {
        trigger.picture = element(); trigger.picture.parentElement = trigger; trigger.picture.currentSrc = selected;
    } else trigger.before.backgroundImage = 'url("' + selected + '")';
    return trigger;
}
let choices = 0;
for (const rule of rules) {
    for (const selected of rule.alternates) {
        const record = manifest.records.find(x => '/' + x.route === rule.route && '/' + x.href === rule.original);
        const variant = record.confirmed_variants.find(x => '/' + x.asset === selected);
        const mechanism = variant.mechanism.includes('currentSrc') ? 'picture' : 'background';
        const trigger = fixture(rule, origin + selected, mechanism);
        const original = trigger.href;
        assert.equal(window.fcHeroImageSource(trigger), origin + selected, rule.route + ': selected composition');
        assert.equal(trigger.href, original, 'Original no-JS fallback is never mutated');
        const options = JSON.parse(JSON.stringify(window.fcHeroImageOptions(trigger)));
        assert.deepEqual(options, [{label: 'Phone version', src: origin + rule.versions.phone}, {label: 'Wide version', src: origin + rule.versions.wide}]);
        for (const option of options) assert([rule.original, ...rule.alternates].includes(new URL(option.src).pathname), 'Version choices stay within exact reviewed assets');
        assert.equal(trigger.href, original, 'Version options never mutate fallback');
        if (mechanism === 'picture') trigger.picture.currentSrc = origin + rule.original;
        else trigger.before.backgroundImage = 'url("' + origin + rule.original + '")';
        assert.equal(window.fcHeroImageSource(trigger), original, 'Reopened original composition retains full original');
        choices++;
    }
}
const rule = rules.find(r => r.route === '/art-study/suffer-the-little-children.html');
let trigger = fixture(rule, origin + rule.alternates[0]);
trigger.href += '?version=original'; trigger.picture.currentSrc += '?version=selected#image';
assert.equal(window.fcHeroImageSource(trigger), origin + rule.alternates[0] + '?version=selected#image', 'Known source path preserves selected query/hash');
assert(window.fcHeroImageOptions(trigger).some(option => option.src === window.fcHeroImageSource(trigger)), 'Selected alternate query/hash remains an exact viewer option');
const askRule = rules.find(r => r.route === '/ask.html');
trigger = fixture(askRule, origin + askRule.original);
trigger.href += '?v=20260905-approved-red#image';
assert(window.fcHeroImageOptions(trigger).some(option => option.src === trigger.href), 'Original query/hash remains an exact viewer option');
for (const selected of ['', origin + '/unknown.webp', 'https://external.example' + rule.alternates[0], 'data:image/png,abc', 'javascript:alert(1)', origin + '/answers.html']) {
    trigger = fixture(rule, selected); assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Unlisted/nonlocal/nonimage stays original');
}
trigger = fixture(rule, origin + rule.alternates[0]);trigger.href = origin + '/different-original.webp';
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Exact original pair required');
trigger = fixture(rule, origin + rule.alternates[0]);window.location.pathname = '/unlisted.html';
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Exact route required');
trigger = fixture(rule, origin + rule.alternates[0]);trigger.matches = () => false;
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Exact trigger required');
for (const property of ['display', 'visibility', 'opacity']) {
    trigger = fixture(rule, origin + rule.alternates[0]);trigger.picture.style[property] = {display:'none', visibility:'hidden', opacity:'0'}[property];
    assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Hidden picture not selected');
}
trigger = fixture(rule, origin + rule.alternates[0]);trigger.picture.getClientRects = () => [];
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Unrendered picture not selected');
trigger = fixture(rule, origin + rule.alternates[0]);trigger.getClientRects = () => [];
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Unrendered trigger not selected');
trigger = fixture(rule, origin + rule.alternates[0]);
const hiddenPicture = element();hiddenPicture.style.display = 'none';hiddenPicture.parentElement = trigger;
trigger.picture.parentElement = hiddenPicture;
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Hidden picture ancestor not selected');
trigger.before.backgroundImage = 'url("' + origin + rule.alternates[1] + '")';
assert.equal(window.fcHeroImageSource(trigger), origin + rule.alternates[1], 'Visible background can own scene when picture is hidden');
for (const state of [{display:'none'}, {visibility:'hidden'}, {opacity:'0'}, {content:'none'}]) {
    trigger = fixture(rule, origin + rule.alternates[0], 'background');Object.assign(trigger.before, state);
    assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Hidden pseudo-element not selected');
}
trigger = fixture(rule, origin + rule.original);trigger.before.backgroundImage = 'url("' + origin + rule.alternates[0] + '")';
assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Visible original picture takes priority over background');
for (const original of ['/assets/heroes/joseph-gateway-20261004.png', '/assets/heroes/topics/living-christ-full.webp', '/assets/heroes/topics/melchizedek-full.webp']) {
    trigger = fixture(rule, origin + rule.alternates[0]);trigger.href = origin + original;
    assert.equal(window.fcHeroImageSource(trigger), trigger.href, 'Intentional high-resolution original preserved');
}
assert.equal(window.fcHeroImageSource(null), null);
assert.equal(window.fcHeroImageOptions(null).length, 0);
for (const mutation of ['route', 'selector', 'original', 'origin']) {
    trigger = fixture(rule, origin + rule.alternates[0]);
    if (mutation === 'route') window.location.pathname = '/unlisted.html';
    if (mutation === 'selector') trigger.matches = () => false;
    if (mutation === 'original') trigger.href = origin + '/different-original.webp';
    if (mutation === 'origin') trigger.href = 'https://external.example' + rule.original;
    assert.equal(window.fcHeroImageOptions(trigger).length, 0, 'Unlisted version scope: ' + mutation);
}
console.log(`Hero image source QA PASS: ${rules.length} exact bindings, ${choices} selected compositions, fallback/visibility/origin/query guards.`);
