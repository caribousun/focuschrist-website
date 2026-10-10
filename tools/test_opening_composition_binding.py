"""Exact reviewed desktop-composition delta and cache scope; not visual approval."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE_CSS = '7fcb1456b4ff2c3372238e0baaccfa6083e4232e328956eff1e1d43f178c96e6'
FINAL_CSS = '722f64b471e3219bc3ec3c11bb0ceaec09fc55fa4d031dd1e52f1422d0d129ee'
BASE_COMMON = '4ef7e6851ebf885557d241aa389825f38585fe435fedc4454134d435482a30ad'
INVENTORY = '1e2a014c1a3b7fb3995855abaa4587441c95efdef640801d7bf49ee3d3239b78'
NEW = '20261006-balanced-opening-1'
OLD = '20261002-timeline-1'
COMMON_VERSION = '20261008-section-top-2'
ROUTE_COMMON_VERSIONS = {
    'church-history.html': '20261008-section-top-2-gallery-links-2',
    'answers/who-was-joseph-smith.html': '20261010-final-art-links-1',
    'art-gallery.html': '20261010-final-art-links-1',
    'book-of-mormon-evidences.html': '20261010-final-art-links-1',
}
DELTA = '''
/* Balance the introduction within the fixed hero-to-Continue interval. */
@media (min-width: 701px) {
  body.fc-site [data-unified-opening][data-unified-opening][data-unified-opening]:has(> .fc-unified-continue) > :is(.fc-container--standard,.jj-wrap,.fc-eyebrow):first-child:not([hidden]):not([data-unified-old-cue]) {
    margin-block-start: auto !important;
  }
}
'''
TIMELINES = frozenset({
    'timelines/latter-day-saint-church-history-timeline.html',
    'timelines/willie-and-martin-handcart-map.html',
    'timelines/life-of-christ-journey-map.html',
})


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def assert_css(css):
    assert css.count(DELTA) == 1 and css.endswith(DELTA), 'Exact appended composition rule required'
    assert digest(css.removesuffix(DELTA)) == BASE_CSS, 'Unrelated CSS or cue geometry changed'
    assert digest(css) == FINAL_CSS, 'Unreviewed composition stylesheet'


def assert_loader(common):
    calls = re.findall(r"relativeAssetHref\(['\"](unified-opening\.(?:css|js)[^'\"]*)['\"]\)", common)
    assert calls == ['unified-opening.css?v=' + NEW, 'unified-opening.js?v=20261006-introductions-1'], 'Exact opening loader versions required'
    inverse = common.replace('unified-opening.css?v=' + NEW, 'unified-opening.css?v=20260930-alignment-2')
    assert inverse.count('header-scroll.js?v=20261008-section-top-2') == 1, 'Exact navigation loader required'
    inverse = inverse.replace('header-scroll.js?v=20261008-section-top-2', 'header-scroll.js?v=20260927-anchor-fade-1', 1)
    assert inverse.count('art-gallery-bridge.js?v=20261010-final-art-links-1') == 1, 'Exact reviewed gallery bridge loader required'
    inverse = inverse.replace('art-gallery-bridge.js?v=20261010-final-art-links-1', 'art-gallery-bridge.js?v=20260915-sensitive-1', 1)
    assert digest(inverse) == BASE_COMMON, 'Unrelated shared loader change'


def assert_routes(inventory_text, documents):
    assert digest(inventory_text) == INVENTORY, 'Reviewed route/hero inventory changed'
    rows = json.loads(inventory_text)['pages']
    hero = {r['path'] for r in rows if r['hero']}
    other = {r['path'] for r in rows if not r['hero']}
    assert len(hero) == 51 and len(other) == 79 and not hero & other
    assert set(documents) == hero | other, 'Missing or out-of-scope route'
    for route, html in documents.items():
        assert_route(route, html, route in hero)


def assert_route(route, html, hero):
    doc = BeautifulSoup(html, 'html.parser')
    scripts = [s['src'] for s in doc.select('script[src]') if 'site-common.js' in s['src']]
    prefix = '/' if route.startswith('jesus-christ/') else '../' * route.count('/')
    expected = prefix + 'site-common.js?v=' + ROUTE_COMMON_VERSIONS.get(route, COMMON_VERSION)
    assert scripts == [expected], route + ': stale/mixed/duplicate/unknown/out-of-scope shared script'
    if route in TIMELINES:
        assert len(doc.select('.timeline-opening-continue')) == 1, route + ': authored timeline cue missing'
        assert not doc.select('.fc-unified-continue'), route + ': timeline entered balance rule'


class CompositionBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / 'unified-opening.css').read_text(encoding='utf-8')
        cls.common = (ROOT / 'site-common.js').read_text(encoding='utf-8')
        cls.inventory = (ROOT / 'docs/unified-opening-inventory.json').read_text(encoding='utf-8')
        cls.documents = {r['path']: (ROOT/r['path']).read_text(encoding='utf-8') for r in json.loads(cls.inventory)['pages']}

    def test_exact_css_and_inverse(self):
        assert_css(self.css)

    def test_exact_shared_loader_inverse(self):
        assert_loader(self.common)

    def test_exact_51_hero_79_excluded_route_bindings(self):
        assert_routes(self.inventory, self.documents)

    def test_mutated_styles_fail(self):
        cases = {
            'stale': self.css.removesuffix(DELTA),
            'duplicate': self.css + DELTA,
            'moved': DELTA + self.css.removesuffix(DELTA),
            'changed value': self.css.replace('margin-block-start: auto', 'margin-block-start: 20px'),
            'mobile leak': self.css.replace('min-width: 701px', 'min-width: 700px'),
            'timeline leak': self.css.replace(':has(> .fc-unified-continue)', ''),
            'hidden leak': self.css.replace(':not([hidden])', ''),
            'old cue leak': self.css.replace(':not([data-unified-old-cue])', ''),
            'cue move': self.css.replace('margin: auto 0 0', 'margin: 20px 0 0'),
            'bottom move': self.css.replace('calc(20px -', 'calc(21px -'),
            'hero move': self.css.replace('100svh', '95svh'),
            'unrelated': self.css + '\nbody { color: red; }\n',
        }
        for name, css in cases.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                assert_css(css)

    def test_mutated_loader_fails(self):
        for version in ['20260930-alignment-2', 'unknown', NEW + '&extra=1']:
            with self.subTest(version=version), self.assertRaises(AssertionError):
                assert_loader(self.common.replace(NEW, version))
        for suffix in ["\nrelativeAssetHref('unified-opening.css?v=" + NEW + "');", '\n/* unrelated change */']:
            with self.subTest(suffix=suffix), self.assertRaises(AssertionError):
                assert_loader(self.common + suffix)

    def test_each_route_rejects_wrong_version_and_duplicate(self):
        # Every route is tested, including nested absolute and relative references.
        for route, html in self.documents.items():
            doc = BeautifulSoup(html, 'html.parser')
            src = next(s['src'] for s in doc.select('script[src]') if 'site-common.js' in s['src'])
            expected = ROUTE_COMMON_VERSIONS.get(route, COMMON_VERSION)
            for invalid in [OLD, NEW, 'unknown', expected + '&extra=1']:
                candidate = dict(self.documents)
                candidate[route] = html.replace(src, src.replace(expected, invalid))
                with self.subTest(route=route, invalid=invalid), self.assertRaises(AssertionError):
                    assert_route(route, candidate[route], expected == NEW)
            for duplicate in [src, src.replace(expected, OLD)]:
                candidate = dict(self.documents)
                candidate[route] += '<script src="' + duplicate + '"></script>'
                with self.subTest(route=route, duplicate=duplicate), self.assertRaises(AssertionError):
                    assert_route(route, candidate[route], expected == NEW)

    def test_route_scope_cannot_drift(self):
        for candidate in [dict(list(self.documents.items())[1:]), dict(self.documents, **{'outside.html': ''})]:
            with self.assertRaises(AssertionError): assert_routes(self.inventory, candidate)
        with self.assertRaises(AssertionError): assert_routes(self.inventory.replace('"hero": true', '"hero": false', 1), self.documents)

    def test_timeline_cues_cannot_join_balancing(self):
        for route in TIMELINES:
            candidate = dict(self.documents)
            candidate[route] = candidate[route].replace('timeline-opening-continue', 'timeline-opening-continue fc-unified-continue')
            with self.subTest(route=route), self.assertRaises(AssertionError):
                assert_route(route, candidate[route], True)


if __name__ == '__main__':
    unittest.main()
