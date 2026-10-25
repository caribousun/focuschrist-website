/* Citation-rendering census QA for the A047 correction.
 *
 * Extracts ask.html's addMessage verbatim and renders every reviewed
 * bank record's sources block through it (sources composed exactly as
 * answer-bank-lane.js mapSources composes them: site group first, then
 * church group, as {text, url}), in a vm whose window is the live Ask
 * page origin. Assertions per record:
 * - every anchor under the 'Official Church sources' group has an
 *   official Church host (churchofjesuschrist.org family, plus the
 *   Church-owned lds.org and josephsmithpapers.org domains);
 * - every church source in the record renders exactly once, in the
 *   official group;
 * - every focusChrist site source renders exactly once, in the
 *   'Related focusChrist study' group, carrying the
 *   data-focuschrist-answer-source marker the study-source router's
 *   dedupe guard keys off;
 * - no destination URL renders twice in the sources box;
 * - the official group renders only when the record has a church
 *   source (no empty group);
 * - no source is lost and none is invented.
 *
 * Usage: node tools/answer_bank_citation_rendering_runtime_qa.js [askHtmlPath] [--report]
 * With --report, violations are counted and printed instead of failing
 * (used to census a base tree). The flagged record
 * ask-what-do-latter-day-saints-believe-about-jesus-christ is probed
 * explicitly either way.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const args = process.argv.slice(2);
const reportOnly = args.includes('--report');
const askHtmlPath = args.find(a => a !== '--report') || path.join(root, 'ask.html');

/* ---------------- minimal DOM (FakeNode) ---------------- */
function textNode(text) { return { nodeType: 3, textContent: String(text), isConnected: false, parent: null }; }
class FakeNode {
    constructor(tag) {
        this.tagName = String(tag || 'div').toUpperCase();
        this.nodeType = 1;
        this.className = '';
        this.style = {};
        this._nodes = [];
        this.attributes = {};
        this.isConnected = false;
        this.parent = null;
        this.scrollTop = 0;
        this.scrollHeight = 0;
    }
    get childNodes() { return this._nodes; }
    get children() { return this._nodes.filter(n => n.nodeType === 1); }
    get textContent() { return this._nodes.map(c => c.textContent).join(''); }
    set textContent(value) {
        const text = String(value == null ? '' : value);
        this._nodes.forEach(c => { c.isConnected = false; c.parent = null; });
        this._nodes = text ? [textNode(text)] : [];
        this._nodes.forEach(c => { c.parent = this; c.isConnected = this.isConnected; });
    }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return name in this.attributes ? this.attributes[name] : null; }
    hasAttribute(name) { return name in this.attributes; }
    appendChild(node) {
        if (node.parent) node.parent._nodes = node.parent._nodes.filter(c => c !== node);
        node.parent = this; node.isConnected = true;
        this._nodes.push(node);
        return node;
    }
    _descendants(out) {
        for (const child of this._nodes) {
            if (child.nodeType === 1) { out.push(child); child._descendants(out); }
        }
        return out;
    }
    _matches(selector) {
        if (selector.startsWith('.')) {
            const wanted = selector.slice(1).split('.').filter(Boolean);
            const have = this.className.split(/\s+/).filter(Boolean);
            return wanted.every(c => have.includes(c));
        }
        if (selector.startsWith('[') && selector.endsWith(']')) return this.hasAttribute(selector.slice(1, -1));
        return this.tagName === selector.toUpperCase();
    }
    querySelectorAll(selector) { return this._descendants([]).filter(n => n._matches(selector)); }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

const chatBox = new FakeNode('div');
chatBox.className = 'chat-box';
const documentStub = {
    getElementById(id) { return id === 'chatBox' ? chatBox : null; },
    createElement(tag) { return new FakeNode(tag); },
    createTextNode(text) { return textNode(text); }
};
const windowStub = {
    location: { href: 'https://focuschrist.com/ask.html', origin: 'https://focuschrist.com', pathname: '/ask.html' },
    document: documentStub
};
const context = vm.createContext({
    window: windowStub,
    document: documentStub,
    console,
    URL,
    Set
});
windowStub.window = windowStub;

/* ---------------- load the bank data ---------------- */
vm.runInContext(read('answer-bank-data.js'), context, { filename: 'answer-bank-data.js' });
const bankData = windowStub.FocusChristAnswerBankData;
assert.ok(bankData && Array.isArray(bankData.records), 'bank data records missing');
const records = bankData.records;
assert.equal(records.length, 222, 'expected 222 records');

/* ---------------- extract addMessage verbatim ---------------- */
const askHtml = fs.readFileSync(askHtmlPath, 'utf8');
const startMarker = 'function addMessage(text, isUser, sources = []) {';
const start = askHtml.indexOf(startMarker);
assert.ok(start >= 0, 'addMessage not found in ' + askHtmlPath);
let depth = 0;
let end = -1;
for (let i = askHtml.indexOf('{', start); i < askHtml.length; i++) {
    if (askHtml[i] === '{') depth++;
    else if (askHtml[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
}
assert.ok(end > start, 'addMessage brace match failed');
vm.runInContext(askHtml.slice(start, end), context, { filename: 'ask.html#addMessage' });
assert.equal(typeof context.addMessage, 'function', 'addMessage did not load');

/* ---------------- classification (the documented host sets) ---------------- */
const CHURCH_DOMAINS = ['churchofjesuschrist.org', 'lds.org', 'josephsmithpapers.org'];
function hostMatches(hostname, domain) { return hostname === domain || hostname.endsWith('.' + domain); }
function isChurchUrl(href) {
    const hostname = new URL(href).hostname;
    return CHURCH_DOMAINS.some(d => hostMatches(hostname, d));
}
function isSiteUrl(href) {
    const parsed = new URL(href);
    return parsed.origin === 'https://focuschrist.com' || hostMatches(parsed.hostname, 'focuschrist.com');
}
function normalize(url) { return new URL(url, 'https://focuschrist.com/ask.html').href; }

/* The lane's mapSources, replicated exactly (answer-bank-lane.js):
 * site group first, then church group, {text: label, url}. */
function laneSources(record) {
    const out = [];
    for (const list of [record.sources_site || [], record.sources_church || []]) {
        for (const source of list) {
            if (source && source.url) out.push({ text: source.label || 'Source', url: source.url });
        }
    }
    return out;
}

function groupOf(anchor) {
    let node = anchor.parent;
    while (node) {
        const tokens = (node.className || '').split(/\s+/).filter(Boolean);
        if (tokens.includes('sources-group--official')) return 'official';
        if (tokens.includes('sources-group--focuschrist')) return 'related';
        if (tokens.includes('sources-group--referenced')) return 'referenced';
        if (tokens.includes('sources')) return 'sources-box';
        node = node.parent;
    }
    return 'none';
}

function censusRecord(record) {
    const violations = [];
    chatBox._nodes = [];
    context.addMessage(record.answer || '', false, laneSources(record));
    const message = chatBox.children[chatBox.children.length - 1];
    assert.ok(message, 'no message rendered for ' + record.id);
    const box = message.querySelector('.sources');
    const anchors = box ? box.querySelectorAll('.source-link') : [];
    const rendered = anchors.map(a => ({ href: a.href, group: groupOf(a), marker: a.getAttribute('data-focuschrist-answer-source') }));

    const churchExpected = (record.sources_church || []).filter(s => s && s.url).map(s => normalize(s.url));
    const siteExpected = (record.sources_site || []).filter(s => s && s.url).map(s => normalize(s.url));
    const allExpected = [...siteExpected, ...churchExpected];
    const distinctExpected = [...new Set(allExpected)];

    // 1. Nothing non-Church under the official heading.
    for (const r of rendered) {
        if (r.group === 'official' && !isChurchUrl(r.href)) {
            violations.push('non-Church host under Official Church sources: ' + r.href);
        }
    }
    // 2. Each church source exactly once, in the official group.
    for (const url of churchExpected) {
        const hits = rendered.filter(r => r.href === url);
        if (hits.length !== 1) violations.push('church source rendered ' + hits.length + ' times: ' + url);
        else if (hits[0].group !== 'official') violations.push('church source outside official group (' + hits[0].group + '): ' + url);
    }
    // 3. Each site source exactly once, in the related group, with the router dedupe marker.
    for (const url of siteExpected) {
        const hits = rendered.filter(r => r.href === url);
        if (hits.length !== 1) violations.push('site source rendered ' + hits.length + ' times: ' + url);
        else {
            if (hits[0].group !== 'related') violations.push('site source outside related group (' + hits[0].group + '): ' + url);
            if (!hits[0].marker) violations.push('site source missing data-focuschrist-answer-source marker: ' + url);
        }
    }
    // 4. No destination twice.
    const counts = {};
    for (const r of rendered) counts[r.href] = (counts[r.href] || 0) + 1;
    for (const [href, n] of Object.entries(counts)) {
        if (n > 1) violations.push('destination rendered ' + n + ' times: ' + href);
    }
    // 5. Official group presence matches church-source presence (no empty group).
    const officialGroup = box ? box.querySelector('.sources-group--official') : null;
    if (churchExpected.length > 0 && !officialGroup) violations.push('official group missing despite church sources');
    if (churchExpected.length === 0 && officialGroup) violations.push('official group rendered with no church sources');
    // 6. Nothing lost, nothing invented.
    if (rendered.length !== distinctExpected.length) {
        violations.push('rendered ' + rendered.length + ' anchors, expected ' + distinctExpected.length + ' distinct sources');
    }
    for (const r of rendered) {
        if (!distinctExpected.includes(r.href)) violations.push('rendered source not in record data: ' + r.href);
    }
    return violations;
}

const failing = [];
let probeResult = null;
for (const record of records) {
    const violations = censusRecord(record);
    if (record.id === 'ask-what-do-latter-day-saints-believe-about-jesus-christ') probeResult = violations;
    if (violations.length) failing.push({ id: record.id, violations });
}

console.log('records censused:', records.length);
console.log('records with violations:', failing.length);
for (const f of failing.slice(0, 12)) console.log('  FAIL', f.id, '-', f.violations[0]);
console.log('flagged record (ask-what-do-latter-day-saints-believe-about-jesus-christ) violations:',
    probeResult === null ? 'RECORD NOT FOUND' : (probeResult.length ? probeResult : 'none'));

if (reportOnly) {
    console.log('REPORT ONLY: base-tree census complete; the flagged record is',
        probeResult && probeResult.length ? 'among the affected records.' : 'NOT among the affected records.');
} else {
    assert.equal(failing.length, 0, 'citation rendering census failed for ' + failing.length + ' records');
    assert.ok(probeResult !== null && probeResult.length === 0, 'flagged record must render clean');
    console.log('CITATION RENDERING CENSUS PASS');
}
