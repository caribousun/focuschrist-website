"""One exact reviewed chart opening, separate from historical hero consumers."""
import hashlib
from html.parser import HTMLParser

ADAMS_ROUTE = 'timelines/adams-1881-chart.html'
ADAMS_SHA256 = '95802a989d818d0ff7297660274c62f18140950b0bf58fc96a90277ef1e1cb90'


class OpeningTags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.semantic_nodes = []
        self.active_semantic_nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ('h1', 'a'):
            node = {'tag': tag, 'attrs': dict(attrs), 'text': ''}
            self.semantic_nodes.append(node)
            self.active_semantic_nodes.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.active_semantic_nodes) - 1, -1, -1):
            if self.active_semantic_nodes[index]['tag'] == tag:
                del self.active_semantic_nodes[index:]
                break

    def handle_data(self, data):
        for node in self.active_semantic_nodes:
            node['text'] += data


def assert_adams_semantics(parsed):
    """Inert required identities; actual rendered visibility is separate evidence."""
    nodes = parsed.semantic_nodes
    headings = [n for n in nodes if n['tag'] == 'h1']
    assert len(headings) == 1, 'Adams requires one semantic H1'
    heading = headings[0]
    assert 'title' in heading['attrs'].get('class', '').split() and heading['text'].strip() == 'Adams’ Chart · 1881', 'Adams H1 identity changed'
    continuations = []
    for name, href, label in [('fc-adams-back', '../timeline.html#choose-timeline', 'Back to timelines'), ('fc-adams-home', '../index.html', 'FocusChrist Home')]:
        selected = [n for n in nodes if name in n['attrs'].get('class', '').split()]
        assert len(selected) == 1 and selected[0]['tag'] == 'a', 'Adams continuation identity missing or duplicated'
        node = selected[0]
        assert node['attrs'].get('href') == href and node['text'].strip() == label, 'Adams continuation target or label changed'
        continuations.append(node)
    assert len({n['attrs']['href'].split('#')[0] for n in continuations}) == 2, 'Adams continuations must be distinct'
    for node in [heading, *continuations]:
        attrs = node['attrs']
        assert 'hidden' not in attrs and attrs.get('aria-hidden') != 'true', 'Required Adams semantic element hidden'
    commons = [n for n in nodes if n['attrs'].get('href') == 'https://commons.wikimedia.org/wiki/File:Adams_Synchronological_Chart,_1881.jpg']
    assert len(commons) == 1, 'Adams Commons credit target changed'
    attrs = commons[0]['attrs']
    assert attrs.get('target') == '_blank' and set(attrs.get('rel', '').split()) == {'noopener', 'noreferrer'}, 'Adams external-link protection changed'


def assert_adams_opening(route, data):
    assert route == ADAMS_ROUTE, 'Unknown Adams opening owner'
    assert len(data) == 62030 and hashlib.sha256(data).hexdigest() == ADAMS_SHA256, 'Adams reviewed opening bytes changed'
    text = data.decode('utf-8')
    parsed = OpeningTags(text)
    tags = parsed.tags
    assert_adams_semantics(parsed)
    ids = [a['id'] for _, a in tags if 'id' in a]
    assert len(ids) == len(set(ids)), 'Adams duplicate element id'
    for name in ('toolbar', 'viewport', 'tiles', 'overview', 'mini', 'navDock', 'showNav', 'hideNav', 'toggleMini', 'fit', 'fillScreen', 'full', 'in', 'out', 'slider', 'homeBtn', 'zoom100'):
        assert ids.count(name) == 1, 'Adams opening/control missing: ' + name
    assert [(t, a.get('href')) for t, a in tags if 'fc-adams-back' in a.get('class', '').split()] == [('a', '../timeline.html#choose-timeline')], 'Adams return link changed'
    assert [a.get('href') for t, a in tags if t == 'link' and a.get('rel') == 'canonical'] == ['https://focuschrist.com/' + ADAMS_ROUTE], 'Adams canonical owner changed'
    assert [a.get('content') for t, a in tags if t == 'meta' and a.get('name') == 'viewport'] == ['width=device-width,initial-scale=1,viewport-fit=cover'], 'Adams browser zoom contract changed'
    assert not any(t == 'iframe' or (t == 'script' and a.get('src')) for t, a in tags), 'Adams standalone loader changed'
    assert all(token not in text for token in ('site-system.css', 'site-common.js', 'full-image-viewer.')), 'Adams unexpectedly consumes shared opening/viewer assets'
    assert 'courtesy of the David Rumsey Map Collection' in text and 'The image is in the public domain.' in text, 'Adams credit missing'


def without_adams_route(pages, data):
    """Validate before removing only this owner; unknown routes remain rejected
    by the unchanged historical count and exact inventory equality at the caller.
    """
    assert len(pages) == len(set(pages)), 'Duplicate canonical route'
    assert list(pages).count(ADAMS_ROUTE) == 1, 'Missing exact Adams opening owner'
    assert_adams_opening(ADAMS_ROUTE, data)
    return [page for page in pages if page != ADAMS_ROUTE]
