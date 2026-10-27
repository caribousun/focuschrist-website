"""Exact current owner integration, separate from historical source projections.

This checks source/DOM contracts, not rendered geometry, pixels or release approval.
Historical bytes are returned only by the explicitly named inverse function after
the actual current bytes have been checked. Unknown routes are never normalized.
"""
import base64
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'docs/owner-integration-contract/source-manifest.json'
MANIFEST_SHA256 = 'ede123415bdeda93becf9d1b88acd2b07fa2f80c985335624ef39ee4d8f00aca'
CANONICAL_SET_SHA256 = 'ba19da4af6ba32219ff9555ecf5ddd466077acd9a6ee09a7d49f29c07d1f4284'
CHART = 'timelines/adams-1881-chart.html'
INTRO = 'timelines/adams-1881-introduction.html'
LANDING = 'timeline.html'
HUB = 'history/emma-hale-smith.html'
ADAMS_ROUTES = frozenset((CHART, INTRO))
STORIES = {
    'history/emma-elect-lady.html': 'emma-story1-ride',
    'history/emma-hymns.html': 'emma-story2-hymnal',
    'history/emma-winter-crossing.html': 'emma-story3-quincy',
    'history/emma-relief-society.html': 'emma-story4-hospitality',
    'history/emma-last-testimony.html': 'emma-story5-testimony',
}
SYSTEM_REF = '../site-system.css?v=20261005-mobile-study-rows-1'
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.data = [], []

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def classes(self):
        return set(self.attrs.get('class', '').split())

    def text(self):
        return ' '.join((' '.join(self.data) + ' ' + ' '.join(c.text() for c in self.children)).split())


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.stack = [self.root]
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].data.append(data)


def one(nodes, predicate, label):
    found = [n for n in nodes if predicate(n)]
    require(len(found) == 1, 'Expected exactly one ' + label)
    return found[0]


def standard_chrome(nodes):
    header = one(nodes, lambda n: n.tag == 'nav' and n.attrs.get('data-focuschrist-header') == 'standard', 'canonical header')
    hn = list(header.walk())
    one(hn, lambda n: n.tag == 'a' and 'nav-logo' in n.classes(), 'header logo')
    search = one(hn, lambda n: n.tag == 'a' and 'data-site-search-trigger' in n.attrs, 'header Search')
    require(search.attrs.get('href') == '../search.html', 'Shared Search target changed')
    menu = one(hn, lambda n: 'hamburger' in n.classes(), 'header menu button')
    require(menu.attrs.get('role') == 'button' and menu.attrs.get('tabindex') == '0' and menu.attrs.get('aria-controls') == 'hamburgerMenu', 'Menu accessibility binding changed')
    one(hn, lambda n: n.attrs.get('id') == 'hamburgerMenu', 'menu target')
    footer = one(nodes, lambda n: n.tag == 'footer' and n.attrs.get('data-focuschrist-footer') == 'standard', 'standard footer')
    fn = list(footer.walk())
    independence = one(fn, lambda n: n.attrs.get('data-focuschrist-independence') == 'footer', 'independence notice')
    disclosure = one(fn, lambda n: n.attrs.get('data-focuschrist-artwork-disclosure') == 'footer', 'artwork notice')
    require(independence.parent is disclosure.parent and independence.parent.children.index(disclosure) == independence.parent.children.index(independence) + 1, 'Footer notices must remain adjacent')


def assert_adams_semantics(route, text):
    require(route in ADAMS_ROUTES, 'Unknown integrated Adams owner')
    nodes = list(Document(text).root.walk())
    ids = [n.attrs['id'] for n in nodes if 'id' in n.attrs]
    require(len(ids) == len(set(ids)), 'Duplicate integrated id')
    standard_chrome(nodes)
    h1 = one(nodes, lambda n: n.tag == 'h1', 'page H1')
    canonical = one(nodes, lambda n: n.tag == 'link' and n.attrs.get('rel') == 'canonical', 'canonical URL')
    require(canonical.attrs.get('href') == 'https://focuschrist.com/' + route, 'Canonical owner changed')
    system = [n.attrs.get('href') for n in nodes if n.tag == 'link' and 'site-system.css' in n.attrs.get('href', '')]
    require(system == [SYSTEM_REF], 'Current shared stylesheet binding changed')
    require(not any('fc-adams-strip' in n.classes() for n in nodes), 'Rejected top strip returned')
    if route == CHART:
        require(h1.attrs.get('class') == 'title' and h1.text() == 'Adams’ Chart · 1881', 'Chart title changed')
        one(nodes, lambda n: n.tag == 'main' and n.attrs.get('id') == 'adams-chart-main', 'bounded chart main')
        for control in ('toolbar', 'viewport', 'tiles', 'zoom', 'fit', 'full', 'fillScreen', 'showNav', 'mini'):
            one(nodes, lambda n, c=control: n.attrs.get('id') == c, 'chart control ' + control)
    else:
        hero = one(nodes, lambda n: 'fc-visual-hero' in n.classes(), 'intro hero')
        require({'timeline-life-hero', 'timeline-history-hero'} <= hero.classes(), 'Shared reference hero geometry missing')
        image = one(list(hero.walk()), lambda n: n.tag == 'img', 'hero image')
        require(image.attrs.get('src') == '../assets/adams-chart/adams-16-0-0.jpg', 'Reviewed chart detail changed')
        opening = one(nodes, lambda n: n.tag == 'header' and 'fc-page-intro' in n.classes(), 'intro opening')
        require({'timeline-life-intro', 'timeline-history-intro'} <= opening.classes(), 'Shared reference opening missing')
        cue = one(list(opening.walk()), lambda n: 'timeline-opening-continue' in n.classes(), 'Continue')
        require(cue.tag == 'a' and cue.attrs.get('href') == '#adams-overview', 'Continue must target real overview')
        one(nodes, lambda n: n.tag == 'section' and n.attrs.get('id') == 'adams-overview', 'overview target')
        action = one(nodes, lambda n: n.attrs.get('id') == 'adams-open-chart', 'chart journey action')
        require(action.tag == 'a' and action.attrs.get('href') == 'adams-1881-chart.html', 'Chart journey target changed')


def assert_emma_semantics(route, text):
    """Current hub ownership/reference semantics, not a historical projection."""
    require(route == HUB or route in STORIES, 'Unknown integrated Emma owner')
    nodes = list(Document(text).root.walk())
    ids = [n.attrs['id'] for n in nodes if 'id' in n.attrs]
    require(len(ids) == len(set(ids)), 'Duplicate Emma id')
    standard_chrome(nodes)
    one(nodes, lambda n: n.tag == 'h1', 'Emma H1')
    owners = [n for n in nodes if n.tag == 'figure' and 'data-exclusive-artwork' in n.attrs]
    if route == HUB:
        expected = set(STORIES.values()) | {'emma-h1', 'emma-h3', 'emma-h4', 'emma-h5', 'emma-c1', 'emma-c3', 'emma-c4', 'emma-c5'}
        require(len(owners) == 13 and {n.attrs['data-exclusive-artwork'] for n in owners} == expected, 'Current hub must own exactly nine Emma and four retained Christ scenes')
        require(not any(n.attrs.get('id') == 'picture-emma-c2' for n in nodes), 'Removed weak-fit scene returned')
        for scene in STORIES.values():
            figure = one(owners, lambda n, s=scene: n.attrs.get('data-exclusive-artwork') == s, 'hub owner ' + scene)
            require(figure.attrs.get('id') == 'picture-' + scene and figure.attrs.get('data-topic-art') == scene, 'Hub owner/detail identity changed')
            links = [n for n in figure.children if n.tag == 'a']
            require(len(links) == 1 and links[0].attrs.get('href') == '/assets/page-art/emma-life/' + scene + '-review-1536.webp' and links[0].attrs.get('aria-haspopup') == 'dialog', 'Hub artwork must retain its detail trigger')
            captions = [n for n in figure.children if n.tag == 'figcaption' and 'data-picture-panel-copy' in n.attrs and 'hidden' in n.attrs]
            require(len(captions) == 1, 'Hub detail-panel copy missing')
        for target in ('elect-lady-right-person', 'hymns-book', 'crossing-words', 'relief-relieved', 'testimony-kept'):
            one(nodes, lambda n, t=target: n.tag == 'section' and n.attrs.get('id') == t, 'integrated story section ' + target)
    else:
        require(not owners, 'Reference story must not remain an independent picture owner')
        scene = STORIES[route]
        figure = one(nodes, lambda n: n.tag == 'figure' and n.attrs.get('data-artwork-reference') == scene, 'direct owner reference')
        require(figure.attrs.get('data-linked-picture-reference') == scene and figure.attrs.get('id') == 'picture-' + scene, 'Reference identity changed')
        require(not any(n.tag == 'a' for n in figure.children), 'Reference must not be captured as a separate picture detail trigger')
        links = [n for n in figure.walk() if n.tag == 'a' and any(c.tag == 'img' for c in n.children)]
        require(len(links) == 1 and links[0].attrs.get('href') == 'emma-hale-smith.html#picture-' + scene, 'Reference image must lead directly to the owning hub section')


def manifest(root=ROOT):
    raw = (root / MANIFEST).read_bytes()
    require(sha(raw) == MANIFEST_SHA256, 'Unreviewed integration manifest')
    value = json.loads(raw)
    require(value.get('schema') == 1 and len(value['files']) == 11, 'Integration manifest shape')
    return value


def validate_file(route, raw, root=ROOT):
    item = manifest(root)['files'].get(route)
    require(item is not None, 'Unknown integration source')
    require(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'Current integration source drift: ' + route)
    if route in ADAMS_ROUTES:
        assert_adams_semantics(route, raw.decode('utf-8'))
    elif route == HUB or route in STORIES:
        assert_emma_semantics(route, raw.decode('utf-8'))
    return item


def historical_bytes(route, current, root=ROOT):
    """An explicit historical fixture, NEVER a current frontend/render claim."""
    item = validate_file(route, current, root)
    history = item.get('historical')
    require(history is not None, 'New route has no invented predecessor')
    raw = current
    for span in reversed(history['inverse_spans']):
        before, after = base64.b64decode(span['before'], validate=True), base64.b64decode(span['after'], validate=True)
        at = span['current_offset']
        require(raw[at:at + len(after)] == after, 'Historical inverse context changed')
        raw = raw[:at] + before + raw[at + len(after):]
    require(len(raw) == history['bytes'] and sha(raw) == history['sha256'], 'Historical inverse endpoint mismatch')
    return raw


def validate_current_adams(root=ROOT):
    for route in (CHART, INTRO, LANDING, 'adams-integration.css', 'adams-integration.js'):
        validate_file(route, (root / route).read_bytes(), root)


def without_integrated_adams_routes(pages, chart_source=None, root=ROOT):
    require(len(pages) == len(set(pages)) == 139, 'Expected 139 unique current canonical routes')
    require(sha('\n'.join(sorted(pages)).encode()) == CANONICAL_SET_SHA256, 'Current canonical route set changed')
    validate_current_adams(root)
    if chart_source is not None:
        validate_file(CHART, chart_source, root)
    return [p for p in pages if p not in ADAMS_ROUTES]


def historical_wrap_consumers(consumers, root=ROOT):
    """Validate both new shared owners, then retain every older owner unchanged."""
    validate_current_adams(root)
    require(all(consumers.get(route) == [SYSTEM_REF] for route in ADAMS_ROUTES), 'Both integrated owners must consume exact current shared styles')
    return {p: v for p, v in consumers.items() if p not in ADAMS_ROUTES}
