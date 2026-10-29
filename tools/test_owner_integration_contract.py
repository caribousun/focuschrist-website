"""Current integration semantics plus explicit historical inverse negatives.

Pure stdlib source tests. No HTML/JS execution, browser, network or project build.
"""
import copy
import hashlib
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit
import owner_integration_contract as c


class OwnerIntegrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = c.manifest()
        cls.raw = {p: (c.ROOT / p).read_bytes() for p in cls.record['files']}
        cls.pages = [urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(c.ROOT / 'sitemap.xml').getroot().findall('{*}url/{*}loc')]

    def test_all_actual_current_files_and_semantics(self):
        for path, raw in self.raw.items():
            with self.subTest(path=path):
                c.validate_file(path, raw)

    def test_non_timeline_changed_current_byte_rejected(self):
        for path, raw in self.raw.items():
            if path == c.LANDING:
                continue  # Current Timeline uses content/navigation semantics, not a whole-page hash.
            with self.subTest(path=path), self.assertRaises(AssertionError):
                c.validate_file(path, raw + b' ')

    def test_timeline_layout_tolerance_and_semantic_drift(self):
        from timeline_selector_check import DESTINATIONS
        raw = self.raw[c.LANDING]
        c.validate_file(c.LANDING, raw + b' ')
        layout = raw.replace(b'fc-timeline-choice__body', b'fc-timeline-choice__body layout-v2', 1)
        self.assertNotEqual(layout, raw)
        c.validate_file(c.LANDING, layout)
        mutations = [
            (b'Explore the story of the Restoration.', b'Changed copy.'),
            (DESTINATIONS[0][1].encode(), b'timelines/other.html'),
            (DESTINATIONS[2][2].encode(), b'assets/other.webp'),
            (b'Church History Timeline', b'Changed title'),
            (b'id="adams-1881"', b'id="other"'),
            (b'<article class="fc-timeline-choice">', b'<article class="fc-timeline-choice" hidden>'),
            (b'</main>', b'<p>Unapproved content</p></main>'),
        ]
        for before, after in mutations:
            self.assertIn(before, raw)
            with self.subTest(field=before), self.assertRaises(AssertionError):
                c.validate_file(c.LANDING, raw.replace(before, after, 1))
        start = raw.index(b'<article class="fc-timeline-choice">')
        stop = raw.index(b'</article>', start) + len(b'</article>')
        for changed in (raw[:start]+raw[stop:], raw[:stop]+raw[start:stop]+raw[stop:]):
            with self.assertRaises(AssertionError):
                c.validate_file(c.LANDING, changed)

    def test_css_successor_is_exact_and_historical_manifest_unchanged(self):
        current = self.raw['adams-integration.css']
        prior = current[:4965]
        suffix = current[4965:]
        self.assertEqual(len(current), 5292)
        self.assertEqual(hashlib.sha256(current).hexdigest(), '3c8a2390e93e94f5d67d3b7a4356f018d78df7ea5c654a3841366549df76d131')
        self.assertEqual(hashlib.sha256(prior).hexdigest(), self.record['files']['adams-integration.css']['sha256'])
        returned = c.validate_file('adams-integration.css', current)
        self.assertEqual((returned['bytes'], returned['sha256']), (len(current), hashlib.sha256(current).hexdigest()))
        for bad in (prior, current + b' ', current + suffix, current[:20] + b'X' + current[21:], prior + suffix.replace(b'row-gap:8px', b'row-gap:9px'), suffix + prior):
            with self.subTest(kind=hashlib.sha256(bad).hexdigest()), self.assertRaises(AssertionError):
                c.validate_file('adams-integration.css', bad)
        with self.assertRaises(AssertionError):
            c.validate_file('adams-integration.js', current)
        with self.assertRaises(AssertionError):
            c.validate_file('other/adams-integration.css', current)
        self.assertEqual(self.record['files']['adams-integration.css']['bytes'], 4965)

    def test_unknown_source_rejected(self):
        with self.assertRaises(AssertionError):
            c.validate_file('timelines/adams-other.html', self.raw[c.CHART])

    def test_new_intro_has_no_historical_predecessor(self):
        with self.assertRaises(AssertionError):
            c.historical_bytes(c.INTRO, self.raw[c.INTRO])

    def test_all_eight_historical_endpoints_exact(self):
        count = 0
        for path, item in self.record['files'].items():
            if 'historical' not in item:
                continue
            prior = c.historical_bytes(path, self.raw[path])
            self.assertEqual(len(prior), item['historical']['bytes'])
            self.assertEqual(hashlib.sha256(prior).hexdigest(), item['historical']['sha256'])
            count += 1
        self.assertEqual(count, 8)

    def test_altered_and_reversed_inverse_spans_rejected(self):
        for mode in ('after', 'before', 'order'):
            value = copy.deepcopy(self.record)
            spans = value['files'][c.HUB]['historical']['inverse_spans']
            if mode == 'order':
                self.assertGreater(len(spans), 1)
                spans.reverse()
            else:
                spans[0][mode] = 'eA=='
            with self.subTest(mode=mode), patch.object(c, 'manifest', return_value=value), self.assertRaises(AssertionError):
                c.historical_bytes(c.HUB, self.raw[c.HUB])

    def test_exact138_to136_partition_retains_every_other_route(self):
        old = c.without_integrated_adams_routes(self.pages, self.raw[c.CHART])
        self.assertEqual(len(old), 136)
        self.assertEqual(set(old), set(self.pages) - c.ADAMS_ROUTES)

    def test_missing_duplicate_unknown_or_replaced_route_rejected(self):
        cases = [self.pages[:-1], self.pages + [c.INTRO], [p for p in self.pages if p != c.INTRO], ['unknown.html' if p == c.INTRO else p for p in self.pages]]
        for pages in cases:
            with self.subTest(pages=len(pages)), self.assertRaises(AssertionError):
                c.without_integrated_adams_routes(pages, self.raw[c.CHART])

    def test_missing_search_menu_footer_or_notice_rejected(self):
        mutations = [('data-site-search-trigger', 'data-removed-search'), ('aria-controls="hamburgerMenu"', 'aria-controls="other"'), ('id="hamburgerMenu"', 'id="otherMenu"'), ('data-focuschrist-footer="standard"', 'data-focuschrist-footer="other"'), ('data-focuschrist-independence="footer"', 'data-removed-independence="footer"'), ('data-focuschrist-artwork-disclosure="footer"', 'data-removed-disclosure="footer"')]
        for route in c.ADAMS_ROUTES:
            source = self.raw[route].decode()
            for before, after in mutations:
                self.assertIn(before, source)
                with self.subTest(route=route, field=before), self.assertRaises(AssertionError):
                    c.assert_adams_semantics(route, source.replace(before, after, 1))

    def test_wrong_continue_or_hero_geometry_rejected(self):
        source = self.raw[c.INTRO].decode()
        for before, after in [('href="#adams-overview"', 'href="#absent"'), ('timeline-history-hero', 'invented-hero'), ('timeline-history-intro', 'invented-intro'), ('adams-16-0-0.jpg', 'adams-64-0-0.jpg')]:
            self.assertIn(before, source)
            with self.subTest(field=before), self.assertRaises(AssertionError):
                c.assert_adams_semantics(c.INTRO, source.replace(before, after, 1))

    def test_removed_or_duplicate_current_hub_owner_rejected(self):
        source = self.raw[c.HUB].decode()
        for scene in c.STORIES.values():
            token = 'data-exclusive-artwork="' + scene + '"'
            self.assertEqual(source.count(token), 1)
            with self.subTest(scene=scene), self.assertRaises(AssertionError):
                c.assert_emma_semantics(c.HUB, source.replace(token, 'data-reference-only="' + scene + '"', 1))
        with self.assertRaises(AssertionError):
            c.assert_emma_semantics(c.HUB, source + '<figure data-exclusive-artwork="emma-story1-ride"></figure>')

    def test_removed_weak_fit_scene_cannot_return(self):
        with self.assertRaises(AssertionError):
            c.assert_emma_semantics(c.HUB, self.raw[c.HUB].decode() + '<figure id="picture-emma-c2" data-exclusive-artwork="emma-c2"></figure>')

    def test_reference_wrong_owner_or_recaptured_trigger_rejected(self):
        for route, scene in c.STORIES.items():
            raw = self.raw[route]
            if route == 'history/emma-elect-lady.html':
                from owner_journey_successor import historical_fixture
                raw = historical_fixture(route, raw, c.ROOT)
            source = raw.decode()
            target = 'emma-hale-smith.html#picture-' + scene
            with self.subTest(route=route, kind='target'), self.assertRaises(AssertionError):
                c.assert_emma_semantics(route, source.replace(target, 'other.html#picture-' + scene))
            with self.subTest(route=route, kind='owner'), self.assertRaises(AssertionError):
                c.assert_emma_semantics(route, source.replace('data-artwork-reference="' + scene + '"', 'data-exclusive-artwork="' + scene + '"', 1))
            start = '<div><a href="' + target + '"'
            end = '</a></div><figcaption>'
            self.assertEqual(source.count(start), 1)
            self.assertEqual(source.count(end), 1)
            recaptured = source.replace(start, '<a href="' + target + '"', 1).replace(end, '</a><figcaption>', 1)
            with self.subTest(route=route, kind='direct-picture-trigger'), self.assertRaises(AssertionError):
                c.assert_emma_semantics(route, recaptured)

    def test_current_style_additions_and_unknown_preservation(self):
        source = {p: [c.SYSTEM_REF] for p in c.ADAMS_ROUTES}
        source['old.html'] = ['old.css']
        self.assertEqual(c.historical_wrap_consumers(source), {'old.html': ['old.css']})
        source['unknown.html'] = ['mystery.css']
        self.assertIn('unknown.html', c.historical_wrap_consumers(source))
        for route in c.ADAMS_ROUTES:
            value = copy.deepcopy(source)
            del value[route]
            with self.subTest(route=route), self.assertRaises(AssertionError):
                c.historical_wrap_consumers(value)


if __name__ == '__main__':
    unittest.main()
