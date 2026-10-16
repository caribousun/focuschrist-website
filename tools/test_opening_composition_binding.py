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
    'church-history.html': '20261010-emma-identity-links-1',
    'answers/who-was-joseph-smith.html': '20261010-final-art-links-1',
    'art-gallery.html': '20261010-emma-identity-links-1',
    'book-of-mormon-evidences.html': '20261010-emma-identity-links-1',
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
    deeper = re.findall(r'/\* Continue appearance B.*?/\* End Continue appearance B\. \*/\n\n', css, re.S)
    assert len(deeper) == 1 and digest(deeper[0]) == '5f7c21bbcc8ec14e07c1ecc0a93360c58d11838a23c92bae83bd3fd74c531862', 'Exact owner-selected B skin required'
    css = css.replace(deeper[0], '', 1)
    # Wyatt selected E on 2026-10-16. Remove only its exact reviewed skin;
    # every original geometry/composition byte remains bound below.
    skin = re.findall(r'/\* Continue appearance E.*?/\* End Continue appearance E\. \*/\n\n', css, re.S)
    assert len(skin) == 1 and digest(skin[0]) == '572a36763b0bf0af9e8b9d3fdfd5748dde395bb28b22bb756dd80c191c35e068', 'Exact owner-selected Continue skin required'
    css = css.replace(skin[0], '', 1)
    assert css.count(DELTA) == 1 and css.endswith(DELTA), 'Exact appended composition rule required'
    assert digest(css.removesuffix(DELTA)) == BASE_CSS, 'Unrelated CSS or cue geometry changed'
    assert digest(css) == FINAL_CSS, 'Unreviewed composition stylesheet'
    return css


ORIGINAL_JS = '3745ded2cb4e92e7b876bb8c8cd217d808da0a933575cf30c3712dc9f35d6dbe'
ARROWLESS_JS = '0268e3ff1586ce4d29fb77441bcf14f6b2244078c8e96a532a62cba4663143f8'


def assert_js(script):
    blocks = re.findall(r'\n/\* Begin owner-selected arrowless Continue label .*?/\* End owner-selected arrowless Continue label\. \*/\n', script, re.S)
    assert len(blocks) == 1 and digest(blocks[0]) == ARROWLESS_JS, 'Exact owner-selected arrowless append required'
    assert script.endswith(blocks[0]), 'Arrowless append must remain last'
    original = script[:-len(blocks[0])]
    assert digest(original) == ORIGINAL_JS, 'Original opening behavior changed'
    return original


def reviewed_opening_bytes(p):
    data = p.read_bytes()
    verifier = {'unified-opening.css': assert_css, 'unified-opening.js': assert_js}.get(p.name)
    if verifier:
        try:
            return verifier(data.decode('utf-8').replace('\r\n', '\n')).encode('utf-8')
        except (AssertionError, UnicodeError):
            pass
    return data


def assert_loader(common):
    calls = re.findall(r"relativeAssetHref\(['\"](unified-opening\.(?:css|js)[^'\"]*)['\"]\)", common)
    assert calls == ['unified-opening.css?v=' + NEW, 'unified-opening.js?v=20261006-introductions-1'], 'Exact opening loader versions required'
    inverse = common.replace('unified-opening.css?v=' + NEW, 'unified-opening.css?v=20260930-alignment-2')
    assert inverse.count('header-scroll.js?v=20261008-section-top-2') == 1, 'Exact navigation loader required'
    inverse = inverse.replace('header-scroll.js?v=20261008-section-top-2', 'header-scroll.js?v=20260927-anchor-fade-1', 1)
    assert inverse.count('art-gallery-bridge.js?v=20261010-emma-identity-links-1') == 1, 'Exact reviewed gallery bridge loader required'
    inverse = inverse.replace('art-gallery-bridge.js?v=20261010-emma-identity-links-1', 'art-gallery-bridge.js?v=20260915-sensitive-1', 1)
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
        cls.script = (ROOT / 'unified-opening.js').read_text(encoding='utf-8')
        cls.common = (ROOT / 'site-common.js').read_text(encoding='utf-8')
        cls.inventory = (ROOT / 'docs/unified-opening-inventory.json').read_text(encoding='utf-8')
        cls.documents = {r['path']: (ROOT/r['path']).read_text(encoding='utf-8') for r in json.loads(cls.inventory)['pages']}

    def test_exact_css_and_inverse(self):
        assert_css(self.css)

    def test_artwork_context_inverse_is_exact(self):
        from tempfile import TemporaryDirectory
        from artwork_six_scene_delivery import digest as context_digest
        with TemporaryDirectory() as folder:
            target = Path(folder) / 'unified-opening.css'
            target.write_bytes(self.css.encode('utf-8'))
            self.assertEqual(context_digest(target), FINAL_CSS)
            for candidate in [self.css.replace('#22b6b5', '#00ffff'),
                              self.css.replace('100svh', '95svh'),
                              self.css + '\nbody{display:none}\n']:
                target.write_bytes(candidate.encode('utf-8'))
                self.assertNotEqual(context_digest(target), FINAL_CSS)

    def test_exact_arrowless_script_and_rejected_changes(self):
        self.assertEqual(digest(assert_js(self.script)), ORIGINAL_JS)
        block = re.search(r'\n/\* Begin owner-selected arrowless Continue label .*?/\* End owner-selected arrowless Continue label\. \*/\n', self.script, re.S).group()
        for candidate in [self.script.replace(block, ''), self.script + block,
                          self.script.replace("'visibility', 'hidden'", "'visibility', 'visible'"),
                          self.script.replace('innerHeight - 20', 'innerHeight - 30'),
                          self.script + '\nalert(1);\n']:
            with self.assertRaises(AssertionError): assert_js(candidate)

    def test_all_artwork_context_inverses_reject_unreviewed_changes(self):
        from tempfile import TemporaryDirectory
        from artwork_six_scene_delivery import digest as six
        from artwork_gabriel_owner_delivery import digest as gabriel
        from artwork_three_reviewed_delivery import digest as three
        with TemporaryDirectory() as folder:
            target = Path(folder) / 'unified-opening.js'
            for context_digest in [six, gabriel, three]:
                target.write_bytes(self.script.encode('utf-8'))
                self.assertEqual(context_digest(target), ORIGINAL_JS)
                for candidate in [self.script.replace('innerHeight - 20', 'innerHeight - 30'),
                                  self.script.replace("'visibility', 'hidden'", "'visibility', 'visible'"),
                                  self.script + '\nalert(1);\n']:
                    target.write_bytes(candidate.encode('utf-8'))
                    self.assertNotEqual(context_digest(target), ORIGINAL_JS)
            target = Path(folder) / 'unrelated.js'
            target.write_bytes(self.script.encode('utf-8'))
            self.assertEqual(reviewed_opening_bytes(target), self.script.encode('utf-8'))

    def test_exact_shared_loader_inverse(self):
        assert_loader(self.common)

    def test_exact_51_hero_79_excluded_route_bindings(self):
        assert_routes(self.inventory, self.documents)

    def test_mutated_styles_fail(self):
        cases = {
            'edited B skin': self.css.replace('#148f91', '#00ffff'),
            'missing B skin': re.sub(r'/\* Continue appearance B.*?/\* End Continue appearance B\. \*/\n\n', '', self.css, flags=re.S),
            'duplicate B skin': self.css + re.search(r'/\* Continue appearance B.*?/\* End Continue appearance B\. \*/\n\n', self.css, re.S).group(),
            'edited skin': self.css.replace('#22b6b5', '#00ffff'),
            'edited halo': self.css.replace('#063c50', '#fff'),
            'missing skin': re.sub(r'/\* Continue appearance E.*?/\* End Continue appearance E\. \*/\n\n', '', self.css, flags=re.S),
            'duplicate skin': self.css + re.search(r'/\* Continue appearance E.*?/\* End Continue appearance E\. \*/\n\n', self.css, re.S).group(),
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
