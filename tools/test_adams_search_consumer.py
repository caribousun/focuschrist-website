"""Exact Adams shared-search registration; no generator/site JS execution."""
import hashlib
import json
from pathlib import Path
import unittest
from adams_search_consumer import is_adams_standalone_search_owner
from adams_standalone_opening import ADAMS_ROUTE

ROOT = Path(__file__).resolve().parents[1]
OWNER = '/' + ADAMS_ROUTE


class AdamsSearchConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / ADAMS_ROUTE).read_bytes()
        cls.index = json.loads((ROOT / 'site-search-index.json').read_text())
        cls.pages = cls.index['pages']

    def test_actual_index_and_standalone(self):
        self.assertEqual(len(self.pages), 137)
        self.assertEqual(len(self.index['records']), 2465)
        self.assertEqual(sum(r['url'] == OWNER for r in self.index['records']), 1)
        self.assertTrue(is_adams_standalone_search_owner(OWNER, self.source, self.pages))

    def test_no_index_or_input_mutation(self):
        before = json.dumps(self.index, sort_keys=True)
        is_adams_standalone_search_owner(OWNER, self.source, self.pages)
        self.assertEqual(json.dumps(self.index, sort_keys=True), before)

    def test_all_other_indexed_pages_keep_standard_contract(self):
        for route in self.pages:
            if route != OWNER:
                with self.subTest(route=route): self.assertFalse(is_adams_standalone_search_owner(route, self.source, self.pages))
        # 136 other indexed pages plus search are 137 standard canonical pages.
        self.assertEqual(len(self.pages) - 1 + 1, 137)

    def test_search_and_404_keep_standard_contract(self):
        for route in ('/search.html', '/404.html'):
            self.assertFalse(is_adams_standalone_search_owner(route, self.source, self.pages))

    def test_unknown_or_similar_route_not_exempted(self):
        for route in ('/timelines/unknown.html', OWNER + '?q=1', OWNER + '#x', ADAMS_ROUTE):
            self.assertFalse(is_adams_standalone_search_owner(route, self.source, self.pages))

    def test_changed_source_rejected(self):
        for source in (self.source + b' ', self.source.replace(b'FocusChrist Home', b'Changed Home', 1)):
            with self.assertRaises(AssertionError): is_adams_standalone_search_owner(OWNER, source, self.pages)

    def test_missing_adams_index_owner(self):
        pages = ['/unknown.html' if p == OWNER else p for p in self.pages]
        with self.assertRaises(AssertionError): is_adams_standalone_search_owner(OWNER, self.source, pages)

    def test_duplicate_adams_index_owner(self):
        with self.assertRaises(AssertionError): is_adams_standalone_search_owner(OWNER, self.source, self.pages + [OWNER])

    def test_missing_home_continuation(self):
        pages = ['/unknown.html' if p == '/index.html' else p for p in self.pages]
        with self.assertRaises(AssertionError): is_adams_standalone_search_owner(OWNER, self.source, pages)

    def test_missing_timeline_continuation(self):
        pages = ['/unknown.html' if p == '/timeline.html' else p for p in self.pages]
        with self.assertRaises(AssertionError): is_adams_standalone_search_owner(OWNER, self.source, pages)

    def test_unknown_extra_or_duplicate_index_page(self):
        for extra in ('/unknown.html', self.pages[0]):
            with self.assertRaises(AssertionError): is_adams_standalone_search_owner(OWNER, self.source, self.pages + [extra])

    def test_exact_old_search_assertions_restored(self):
        text = (ROOT / 'tools/site_search_qa.py').read_text()
        extra = 'from adams_search_consumer import is_adams_standalone_search_owner\n'
        current = "    source=(ROOT/path.lstrip('/')).read_bytes()\n    if is_adams_standalone_search_owner(path, source, data['pages']): continue\n    d=Document();d.feed(source.decode('utf-8'));nodes=list(d.root.walk())\n"
        previous = "    d=Document();d.feed((ROOT/path.lstrip('/')).read_text(encoding='utf-8'));nodes=list(d.root.walk())\n"
        self.assertEqual(text.count(extra), 1); self.assertEqual(text.count(current), 1)
        restored = text.replace(extra, '').replace(current, previous)
        self.assertEqual(hashlib.sha256(restored.encode()).hexdigest(), '3e44e6448fa87e5bed2b66ade401f15f424c3ea82f75470fd1d473c5d92eae2d')


if __name__ == '__main__':
    unittest.main()
