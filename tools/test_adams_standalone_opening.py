"""Focused standalone successor tests; no QA CLI/browser execution."""
import hashlib
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import adams_standalone_opening as a
import emma_story_consumers as e

ROOT = Path(__file__).resolve().parents[1]


class AdamsOpeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = (ROOT / a.ADAMS_ROUTE).read_bytes()
        cls.pages = [urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(ROOT / 'sitemap.xml').findall('{*}url/{*}loc')]
        inventory = json.loads((ROOT / 'docs/unified-opening-inventory.json').read_text())
        cls.historical = {p['path'] for p in inventory['pages']} | {'history/emma-hale-smith.html', 'timelines/world-and-scripture-timeline.html'}

    def composed_contract(self, pages, data):
        historical = e.historical_routes(a.without_adams_route(pages, data))
        self.assertEqual(len(historical), 132)
        self.assertEqual(historical, self.historical)
        return historical

    def test_actual_current_routes_and_exact_source(self):
        self.assertEqual(len(self.pages), 138)
        self.assertEqual(self.composed_contract(self.pages, self.data), self.historical)
        self.assertEqual(a.without_adams_route(self.pages, self.data), [p for p in self.pages if p != a.ADAMS_ROUTE])

    def test_missing_adams_rejected(self):
        with self.assertRaises(AssertionError):
            a.without_adams_route([p for p in self.pages if p != a.ADAMS_ROUTE], self.data)

    def test_duplicate_routes_rejected(self):
        for name in (a.ADAMS_ROUTE, sorted(self.historical)[0], sorted(e.EMMA_STORY_ROUTES)[0]):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                a.without_adams_route(self.pages + [name], self.data)

    def test_unknown_route_not_normalized_away(self):
        unknown = 'timelines/unreviewed-chart.html'
        self.assertIn(unknown, a.without_adams_route(self.pages + [unknown], self.data))
        with self.assertRaises(AssertionError):
            self.composed_contract(self.pages + [unknown], self.data)
        # Count alone is insufficient: replacing one old owner still fails equality.
        changed = [p for p in self.pages if p != sorted(self.historical)[0]] + [unknown]
        with self.assertRaises(AssertionError):
            self.composed_contract(changed, self.data)

    def test_changed_source_rejected(self):
        variants = [self.data + b' ', self.data.replace(b'../timeline.html#choose-timeline', b'../wrong.html', 1), self.data.replace(b'id="viewport"', b'id="missing"', 1), self.data.replace(b'<script>', b'<script src="../site-common.js">', 1)]
        for data in variants:
            self.assertNotEqual(data, self.data)
            with self.assertRaises(AssertionError): a.without_adams_route(self.pages, data)

    def test_missing_historical_owner_rejected(self):
        missing = sorted(self.historical)[0]
        with self.assertRaises(AssertionError):
            self.composed_contract([p for p in self.pages if p != missing], self.data)

    def test_emma_requirements_unchanged(self):
        for missing in e.EMMA_STORY_ROUTES:
            with self.subTest(missing=missing), self.assertRaises(AssertionError):
                self.composed_contract([p for p in self.pages if p != missing], self.data)

    def test_unknown_opening_owner_rejected(self):
        with self.assertRaises(AssertionError):
            a.assert_adams_opening('timelines/other.html', self.data)

    def test_exact_old_predicates_and_emma_helper_preserved(self):
        data = (ROOT / 'tools/unified_opening_qa.py').read_bytes()
        extra = b'from adams_standalone_opening import ADAMS_ROUTE, without_adams_route\r\n'
        current = b'historical_pages = historical_routes(without_adams_route(pages, (ROOT / ADAMS_ROUTE).read_bytes()))'
        previous = b'historical_pages = historical_routes(pages)'
        message = b'5 additional reading-first Emma stories and 1 exact Adams standalone, current shared versions'
        old_message = b'5 additional reading-first Emma stories, current shared versions'
        self.assertEqual(data.count(extra), 1); self.assertEqual(data.count(current), 1); self.assertEqual(data.count(message), 1)
        restored = data.replace(extra, b'').replace(current, previous).replace(message, old_message)
        self.assertEqual(hashlib.sha256(restored).hexdigest(), 'a494a6368416ce7a95c06d895f92cf3e06baf6159bab66ad095b4c3738b7759f')
        self.assertEqual(hashlib.sha256((ROOT / 'tools/emma_story_consumers.py').read_bytes()).hexdigest(), '502dc4311c1f5ee929f660cd466900c6c25dc90ba5ce4b05b304aaf08bce6f95')

    def test_no_new_shared_wrap_or_viewer_consumption(self):
        text = self.data.decode('utf-8')
        for token in ('site-system.css', 'site-common.js', 'full-image-viewer.'):
            self.assertNotIn(token, text)


    def semantic_rejects(self, before, after):
        text = self.data.decode('utf-8')
        self.assertEqual(text.count(before), 1)
        changed = text.replace(before, after, 1)
        # Exercise semantic guards independently; production still verifies SHA first.
        with self.assertRaises(AssertionError): a.assert_adams_semantics(a.OpeningTags(changed))
        with self.assertRaises(AssertionError): a.assert_adams_opening(a.ADAMS_ROUTE, changed.encode())

    def test_v9_semantic_positive(self):
        a.assert_adams_semantics(a.OpeningTags(self.data.decode()))

    def test_v9_heading_mutations(self):
        old = '<h1 class="title">Adams’ Chart · 1881</h1>'
        for changed in ('<div class="title">Adams’ Chart · 1881</div>', '<h1 class="title">Changed</h1>', old + old, old.replace('class="title"', 'class="title" hidden')):
            with self.subTest(changed=changed): self.semantic_rejects(old, changed)

    def test_v9_home_mutations(self):
        old = '<a class="fc-adams-home" href="../index.html">FocusChrist Home</a>'
        for changed in ('', old + old, old.replace('FocusChrist Home', 'focusChrist Home'), old.replace('../index.html', '../timeline.html#choose-timeline'), old.replace('class="fc-adams-home"', 'class="fc-adams-home" aria-hidden="true"')):
            with self.subTest(changed=changed): self.semantic_rejects(old, changed)

    def test_v9_back_mutations(self):
        old = '<a class="fc-adams-back" href="../timeline.html#choose-timeline">Back to timelines</a>'
        for changed in ('', old + old, old.replace('#choose-timeline', ''), old.replace('Back to timelines', 'Changed')):
            with self.subTest(changed=changed): self.semantic_rejects(old, changed)

    def test_v9_commons_protection_mutations(self):
        old = '<a href="https://commons.wikimedia.org/wiki/File:Adams_Synchronological_Chart,_1881.jpg" target="_blank" rel="noopener noreferrer">Wikimedia Commons</a>'
        for changed in (old.replace(' target="_blank"', ''), old.replace(' rel="noopener noreferrer"', ''), old.replace('noopener noreferrer', 'noopener'), old.replace('File:Adams_', 'File:Other_')):
            with self.subTest(changed=changed): self.semantic_rejects(old, changed)


if __name__ == '__main__':
    unittest.main()
