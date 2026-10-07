"""Exact reviewed introduction delta; source currentness is not rendered acceptance."""
from __future__ import annotations
import argparse
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'docs/hero-introductions-review.json'
BASELINE = 'ed81f01e2e40b81573bc1dec72a76da349ac7164'
ROUTES = frozenset((
    'index.html', 'watch.html', 'missionary.html', 'church-history.html',
    'pioneers.html', 'about.html', 'book-of-mormon-evidences.html', 'atonement.html',
    'timeline.html', 'timelines/latter-day-saint-church-history-timeline.html',
    'timelines/willie-and-martin-handcart-map.html', 'timelines/life-of-christ-journey-map.html',
    'answers/holy-ghost.html', 'answers/plan-of-salvation.html',
    'history/john-tanner.html', 'history/eleazer-miller.html', 'history/john-rowe-moyle.html',
    'general-conference.html', 'answers/god-our-heavenly-father.html',
    'answers/stand-forever.html', 'answers/settle-this-in-your-hearts.html',
    'joseph-smith-likeness.html', 'joseph-smith-portrait-research.html',
    'answers/who-was-joseph-smith.html',
))
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def scope_class(route):
    if route.startswith('answers/'):
        return 'fc-topic-opening'
    if route.startswith('history/'):
        return 'fc-life-opening'
    return {'general-conference.html': 'gc-page-opening',
            'joseph-smith-likeness.html': 'joseph-bridge-intro',
            'joseph-smith-portrait-research.html': 'research-opening'}.get(route, 'fc-page-intro')


class ScopeParser(HTMLParser):
    def __init__(self, text, token):
        super().__init__(convert_charrefs=False)
        self.text, self.token = text, token
        self.lines, self.stack, self.ranges = [0], [], []
        self.lines += [i + 1 for i, char in enumerate(text) if char == '\n']
        self.feed(text)
        assert not any(x[2] for x in self.stack), 'Unclosed reviewed opening'

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.source_offset(), self.token in dict(attrs).get('class', '').split()))

    def handle_startendtag(self, tag, attrs):
        assert self.token not in dict(attrs).get('class', '').split(), 'Self-closing opening'

    def handle_endtag(self, tag):
        matches = [i for i, x in enumerate(self.stack) if x[0] == tag]
        if not matches:
            return
        index = matches[-1]
        assert not any(x[2] for x in self.stack[index + 1:]), 'Malformed reviewed opening'
        item = self.stack[index]
        del self.stack[index:]
        if item[2]:
            end = self.text.index('>', self.source_offset()) + 1
            self.ranges.append((item[1], end))


def opening_range(route, text):
    assert route in ROUTES, 'Unregistered introduction route: ' + route
    ranges = ScopeParser(text, scope_class(route)).ranges
    assert len(ranges) == 1, route + ': opening missing or duplicated'
    return ranges[0]


def dom_digest(text):
    return digest(str(BeautifulSoup(text, 'html.parser')))


def protected_structure(text):
    """Paragraph-only authoring may not authorize title, artwork or control edits."""
    soup = BeautifulSoup(text, 'html.parser')
    for node in soup.select('p.fc-page-intro-copy,p.lede,p.fc-topic-subtitle,p.gc-opening-tagline,p.fc-conference-lead,.joseph-bridge-intro > p:not(.fc-eyebrow),.research-opening > p:not(.fc-eyebrow)'):
        node.decompose()
    def tree(node):
        if isinstance(node, str):
            return str(node) if str(node).strip() else None
        return (node.name, sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in node.attrs.items()),
                [value for child in node.children if (value := tree(child)) is not None])
    return tree(soup)


def make_record(route, before, after):
    """Authoring utility; callers must obtain final-source and independent review."""
    a, b = opening_range(route, before)
    c, d = opening_range(route, after)
    old, new = before[a:b], after[c:d]
    assert old != new, route + ': no changed introduction'
    assert protected_structure(old) == protected_structure(new), route + ': non-paragraph opening change'
    prefix = 0
    while prefix < min(len(old), len(new)) and old[prefix] == new[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(len(old), len(new)) - prefix and old[-suffix - 1] == new[-suffix - 1]:
        suffix += 1
    start = old.rfind('<', 0, prefix + 1)
    old_end = old.find('>', len(old) - suffix) + 1
    new_end = new.find('>', len(new) - suffix) + 1
    assert start >= 0 and old_end > start and new_end > start
    old_fragment, new_fragment = old[start:old_end], new[start:new_end]
    # Insertions include the preceding unchanged tag, so the old adjacency is
    # absent from current markup rather than mistaken for mixed old/new copy.
    if old_fragment in new_fragment:
        start = old.rfind('<', 0, start)
        assert start >= 0
        old_fragment, new_fragment = old[start:old_end], new[start:new_end]
    assert old.count(old_fragment) == new.count(new_fragment) == 1
    assert new.replace(new_fragment, old_fragment, 1) == old, route + ': exact inverse failed'
    return {'path': route, 'baseline_commit': BASELINE, 'scope_class': scope_class(route),
            'current_context_before': after[max(0, c - 120):c],
            'current_context_after': after[d:d + 120],
            'old_opening': old, 'new_opening': new,
            'old_opening_sha256': digest(old), 'new_opening_sha256': digest(new),
            'old_dom_sha256': dom_digest(old), 'new_dom_sha256': dom_digest(new),
            'old_fragment': old_fragment, 'new_fragment': new_fragment,
            'old_fragment_sha256': digest(old_fragment), 'new_fragment_sha256': digest(new_fragment)}


def load_registry():
    return json.loads(REGISTRY.read_text(encoding='utf-8'))


def validated_record(route, registry=None):
    data = load_registry() if registry is None else registry
    assert data['baseline_commit'] == BASELINE and data['version'] == 1
    records = data['pages']
    assert len(records) == len(ROUTES) and {r['path'] for r in records} == ROUTES, 'Exact 24-route registry required'
    assert route in ROUTES, 'Unregistered introduction route: ' + route
    record = next(r for r in records if r['path'] == route)
    assert record['baseline_commit'] == BASELINE and record['scope_class'] == scope_class(route)
    for key in ('old_opening', 'new_opening', 'old_fragment', 'new_fragment'):
        assert digest(record[key]) == record[key + '_sha256'], route + ': corrupt ' + key
    for prefix in ('old', 'new'):
        assert dom_digest(record[prefix + '_opening']) == record[prefix + '_dom_sha256']
        opening = record[prefix + '_opening']
        assert opening.count(record[prefix + '_fragment']) == 1
        assert opening_range(route, opening) == (0, len(opening))
    assert record['new_opening'].replace(record['new_fragment'], record['old_fragment'], 1) == record['old_opening']
    assert record['old_fragment'] != record['new_fragment']
    assert protected_structure(record['old_opening']) == protected_structure(record['new_opening'])
    return record


def restore_timeline_navigation(route, text, record):
    """Invert only the three owner-authorized navigation moves, not prose edits.

    Keep the original 24-route paragraph review and its hashes immutable. The
    current layout must match the exact reviewed removal and insertion before
    its opening can be compared with that original review.
    """
    routes = {name for name in ROUTES if name.startswith('timelines/')}
    if route not in routes:
        return text
    data = json.loads((ROOT / 'docs/timeline-introduction-context.json').read_text(encoding='utf-8'))
    assert data['version'] == 1 and set(data['pages']) == routes
    binding = data['pages'][route]
    line = binding['original_nav_line']
    nav = line.lstrip()
    assert nav.startswith('<nav class="timeline-navigation" ') and nav.endswith('</nav>')
    assert record['new_opening'].count(line) == 1
    expected = record['new_opening'].replace(line, '', 1)
    assert digest(expected) == binding['current_opening_sha256']
    start, end = opening_range(route, text)
    assert text[start:end] == expected, route + ': unreviewed timeline opening change'
    assert text.count(nav) == 1, route + ': timeline navigation missing or duplicated'
    soup = BeautifulSoup(text, 'html.parser')
    assert len(soup.select('nav.timeline-navigation')) == 1
    anchor = binding['overview_anchor']
    insertion = anchor + '\n    ' + nav
    assert text.count(insertion) == 1, route + ': navigation not after reviewed overview paragraph'
    assert text.index(insertion) >= end, route + ': navigation is not below opening'
    # Exact replacements preserve every unrelated byte for downstream guards.
    text = text.replace(insertion, anchor, 1)
    return text[:start] + record['new_opening'] + text[end:]


def assert_current_opening(route, text, registry=None):
    record = validated_record(route, registry)
    text = restore_timeline_navigation(route, text, record)
    start, end = opening_range(route, text)
    current = text[start:end]
    assert text[max(0, start - 120):start] == record['current_context_before'], route + ': opening relocated'
    assert text[end:end + 120] == record['current_context_after'], route + ': opening adjacency changed'
    assert digest(current) == record['new_opening_sha256'], route + ': current opening changed or stale'
    assert dom_digest(current) == record['new_dom_sha256']
    assert text.count(record['new_fragment']) == 1, route + ': changed fragment missing/duplicated/outside scope'
    assert record['old_fragment'] not in current, route + ': mixed old/new introduction'
    return record


def restore_reviewed_opening(route, text, registry=None):
    record = assert_current_opening(route, text, registry)
    text = restore_timeline_navigation(route, text, record)
    start, end = opening_range(route, text)
    restored = text[start:end].replace(record['new_fragment'], record['old_fragment'], 1)
    assert restored == record['old_opening']
    assert digest(restored) == record['old_opening_sha256']
    return text[:start] + restored + text[end:]


def self_test():
    data = load_registry()
    cases = 0
    for route in sorted(ROUTES):
        actual = (ROOT / route).read_text(encoding='utf-8')
        record = assert_current_opening(route, actual, data)
        restored = restore_reviewed_opening(route, actual, data)
        assert record['old_opening'] in restored
        start, end = opening_range(route, actual)
        mutations = {
            'stale': restored,
            'missing': actual[:start] + actual[end:],
            'duplicate-opening': actual + record['new_opening'],
            'duplicate-fragment': actual + record['new_fragment'],
            'modified-fragment': actual[:start] + actual[start:end].replace('<p', '<p data-unreviewed="true"', 1) + actual[end:],
            'title': actual[:start] + actual[start:end].replace('<h1', '<h1 data-unreviewed="true"', 1) + actual[end:],
            'unrelated-script-in-opening': actual[:end - 1] + '<script src="unknown.js"></script>' + actual[end - 1:],
            'relocated': actual[:start] + actual[end:] + record['new_fragment'],
        }
        if route.startswith('timelines/'):
            binding = json.loads((ROOT / 'docs/timeline-introduction-context.json').read_text(encoding='utf-8'))['pages'][route]
            nav = binding['original_nav_line'].lstrip()
            anchor = binding['overview_anchor']
            mutations.update({
                'missing-navigation': actual.replace(nav, '', 1),
                'duplicate-navigation': actual + nav,
                'altered-navigation': actual.replace(nav, nav.replace('All timelines', 'Other timelines'), 1),
                'navigation-in-old-position': actual.replace(actual[start:end], record['new_opening'], 1).replace(anchor + '\n    ' + nav, anchor, 1),
                'navigation-before-paragraph': actual.replace(anchor + '\n    ' + nav, nav + anchor, 1),
                'unrelated-overview-change': actual.replace(anchor, anchor.replace('</p>', 'UNREVIEWED</p>'), 1),
            })
        for label, broken in mutations.items():
            assert broken != actual, (route, label, 'inactive fixture')
            try:
                assert_current_opening(route, broken, data)
            except AssertionError:
                cases += 1
            else:
                raise AssertionError((route, label, 'mutation accepted'))
        # Normalization never erases an unrelated body mutation; legacy guards see it.
        marker = '<!-- unrelated body mutation remains -->'
        assert restore_reviewed_opening(route, actual + marker, data).endswith(marker)
    for bad in ('art-study/be-still.html', 'unknown.html'):
        try:
            assert_current_opening(bad, '<section></section>', data)
        except AssertionError:
            cases += 1
        else:
            raise AssertionError('Unregistered route accepted')
    for mutate in (lambda d: d['pages'].pop(), lambda d: d['pages'].append(copy.deepcopy(d['pages'][0])),
                   lambda d: d['pages'][0].update(path='unknown.html'),
                   lambda d: d['pages'][0].update(new_fragment='unreviewed')):
        bad = copy.deepcopy(data)
        mutate(bad)
        try:
            validated_record(data['pages'][0]['path'], bad)
        except AssertionError:
            cases += 1
        else:
            raise AssertionError('Corrupt registry accepted')
    print(f'HERO INTRODUCTIONS SELF-TEST PASS: {cases} negative cases; exact 24 routes and outside-body preservation')


def check():
    for route in sorted(ROUTES):
        assert_current_opening(route, (ROOT / route).read_text(encoding='utf-8'))
    print('HERO INTRODUCTIONS QA PASS: exact 24 current openings, paragraph-only inverses to ed81; rendering remains separate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    self_test() if args.self_test else check()
