"""Focused additive registration tests; full resource-thumbnail QA remains required."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
OWNERS = tuple('history/emma-' + name + '.html' for name in (
    'elect-lady', 'hymns', 'winter-crossing', 'relief-society', 'last-testimony'))
HISTORICAL_SHA = 'ea7157cbddb5b62c0211f27ef1e8722a08764de947d874fa682eae25d400c8f2'

class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.keys = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'data-resource-key' in attrs:
            self.keys.append(attrs['data-resource-key'])

def strict_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, 'Duplicate coverage owner'
        result[key] = value
    return result

def validate(coverage, routes, sources):
    assert len(routes) == len(set(routes)) == 137
    assert set(coverage) == set(routes)
    assert set(sources) == set(OWNERS)
    for owner in OWNERS:
        assert coverage[owner] == []
        parser = Cards()
        parser.feed(sources[owner])
        assert parser.keys == coverage[owner]
    old = {key: value for key, value in coverage.items() if key not in OWNERS}
    assert len(old) == 132
    assert hashlib.sha256(json.dumps(old, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == HISTORICAL_SHA

class EmmaResourceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = json.loads((ROOT/'docs/resource-page-coverage.json').read_text(), object_pairs_hook=strict_object)
        self.routes = [urlsplit(x.text).path.lstrip('/') or 'index.html' for x in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')]
        self.sources = {owner: (ROOT/owner).read_text() for owner in OWNERS}
    def check(self, coverage=None, routes=None, sources=None):
        validate(self.coverage if coverage is None else coverage, self.routes if routes is None else routes, self.sources if sources is None else sources)
    def test_actual_five_pages_and_unchanged_historical132(self):
        self.check()
    def test_each_missing_owner(self):
        for owner in OWNERS:
            changed = dict(self.coverage); del changed[owner]
            with self.subTest(owner=owner), self.assertRaises(AssertionError): self.check(coverage=changed)
    def test_each_changed_new_mapping(self):
        for owner in OWNERS:
            changed = dict(self.coverage); changed[owner] = ['unreviewed']
            with self.subTest(owner=owner), self.assertRaises(AssertionError): self.check(coverage=changed)
    def test_each_actual_page_added_card(self):
        for owner in OWNERS:
            changed = dict(self.sources); changed[owner] += '<article data-resource-key="unreviewed"></article>'
            with self.subTest(owner=owner), self.assertRaises(AssertionError): self.check(sources=changed)
    def test_unknown_owner(self):
        with self.assertRaises(AssertionError): self.check(coverage={**self.coverage, 'unknown.html': []})
    def test_duplicate_route(self):
        with self.assertRaises(AssertionError): self.check(routes=self.routes + [OWNERS[0]])
    def test_duplicate_json_owner(self):
        with self.assertRaises(AssertionError): json.loads('{"history/emma-hymns.html": [], "history/emma-hymns.html": []}', object_pairs_hook=strict_object)
    def test_old_mapping_drift(self):
        changed = dict(self.coverage); changed['index.html'] = []
        with self.assertRaises(AssertionError): self.check(coverage=changed)

if __name__ == '__main__':
    unittest.main()
