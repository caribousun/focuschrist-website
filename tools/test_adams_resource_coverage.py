"""Finite exact Adams resource registration negatives; full scanner unchanged."""
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from adams_resource_coverage import ADAMS_ROUTE, Cards, without_adams_resource_owner

ROOT = Path(__file__).resolve().parents[1]


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, 'Duplicate coverage owner'
        result[key] = value
    return result


class AdamsResourceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = json.loads((ROOT/'docs/resource-page-coverage.json').read_text(), object_pairs_hook=strict_object)
        self.routes = [urlsplit(x.text).path.lstrip('/') or 'index.html' for x in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')]
        self.source = (ROOT/ADAMS_ROUTE).read_bytes()

    def check(self, coverage=None, routes=None, source=None):
        return without_adams_resource_owner(self.coverage if coverage is None else coverage, self.routes if routes is None else routes, self.source if source is None else source)

    def test_actual_zero_and_existing137(self):
        old, routes = self.check(); self.assertEqual(len(old),137); self.assertEqual(set(old),set(routes))

    def test_missing_owner(self):
        changed=dict(self.coverage); del changed[ADAMS_ROUTE]
        with self.assertRaises(AssertionError): self.check(coverage=changed)

    def test_nonempty_mapping(self):
        with self.assertRaises(AssertionError): self.check(coverage={**self.coverage,ADAMS_ROUTE:['unreviewed']})

    def test_changed_source(self):
        with self.assertRaises(AssertionError): self.check(source=self.source+b' ')

    def test_added_actual_card(self):
        changed=self.source+b'<article data-resource-key="unreviewed"></article>'
        parser=Cards();parser.feed(changed.decode());self.assertEqual(parser.keys,['unreviewed'])
        with self.assertRaises(AssertionError): self.check(source=changed)

    def test_unknown_owner(self):
        with self.assertRaises(AssertionError): self.check(coverage={**self.coverage,'unknown.html':[]})

    def test_duplicate_route(self):
        with self.assertRaises(AssertionError): self.check(routes=self.routes+[ADAMS_ROUTE])

    def test_duplicate_json_owner(self):
        with self.assertRaises(AssertionError): json.loads('{"timelines/adams-1881-chart.html":[],"timelines/adams-1881-chart.html":[]}',object_pairs_hook=strict_object)

    def test_existing_mapping_drift(self):
        with self.assertRaises(AssertionError): self.check(coverage={**self.coverage,'index.html':[]})

    def test_unknown_replacement_route(self):
        with self.assertRaises(AssertionError): self.check(routes=['unknown.html' if x==ADAMS_ROUTE else x for x in self.routes])


if __name__ == '__main__':
    unittest.main()
