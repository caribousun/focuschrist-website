"""Finite additive-contract tests; no full-checkout or rendered PASS claim."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest
from bs4 import BeautifulSoup
import emma_story_consumers as e

ROOT = Path(__file__).resolve().parents[1]


def source_function(name):
    # Load only the selected pure predicate, never execute the QA CLI/module body.
    tree = ast.parse((ROOT / 'tools/sitewide_artwork_review_qa.py').read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(nodes) == 1
    scope = {'hashlib': hashlib, 'json': json, 'EMMA_STORY_ROUTES': e.EMMA_STORY_ROUTES,
             'STORY_REF': e.STORY_REF, 'RELEASE_STYLE_BINDINGS': {
                 'history-stories.css': ({'history/old.html'}, '../history-stories.css?v=fixture-old')},
             'VIEWER_BINDINGS_SHA256': '90de3afd9212c3548ad780ae8c067d32b90f33ca82ddacfd39f3035f8c72fa2f'}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<selected pure predicate>', 'exec'), scope)
    return scope[name]


class EmmaConsumerTests(unittest.TestCase):
    def setUp(self):
        self.route = sorted(e.EMMA_STORY_ROUTES)[0]
        self.system = {p: [e.SYSTEM_REF] for p in e.EMMA_STORY_ROUTES}
        self.system['old.html'] = ['old-ref']
        self.viewer = {p: copy.deepcopy(e.VIEWER_REFS) for p in e.EMMA_STORY_ROUTES}
        self.viewer['old.html'] = [['old', {}]]

    def test_exact_five_and_historical_remainder(self):
        self.assertEqual(e.historical_consumers(self.system, [e.SYSTEM_REF]), {'old.html': ['old-ref']})
        self.assertEqual(e.historical_consumers(self.viewer, e.VIEWER_REFS), {'old.html': [['old', {}]]})

    def test_each_missing_owner_rejected(self):
        for route in e.EMMA_STORY_ROUTES:
            for data, expected in ((self.system, [e.SYSTEM_REF]), (self.viewer, e.VIEWER_REFS)):
                changed = copy.deepcopy(data); del changed[route]
                self.assertIsNone(e.historical_consumers(changed, expected))

    def test_changed_and_duplicate_bindings_rejected(self):
        for bad in ([], ['stale'], [e.SYSTEM_REF, e.SYSTEM_REF]):
            changed = copy.deepcopy(self.system); changed[self.route] = bad
            self.assertIsNone(e.historical_consumers(changed, [e.SYSTEM_REF]))
        changed = copy.deepcopy(self.viewer); changed[self.route][1][1]['src'] += '-unknown'
        self.assertIsNone(e.historical_consumers(changed, e.VIEWER_REFS))

    def test_unknown_owner_reaches_historical_rejection(self):
        historical = lambda d, *_: d == {'old.html': ['old-ref']}
        version = e.SYSTEM_REF.split('?v=')[1]
        self.assertTrue(e.reviewed_wrap_additions(self.system, [], version, historical))
        changed = dict(self.system, **{'history/emma-unknown.html': [e.SYSTEM_REF]})
        self.assertFalse(e.reviewed_wrap_additions(changed, [], version, historical))
        self.assertFalse(e.reviewed_wrap_additions(self.system, [], 'stale', historical))

    def test_viewer_remainder_not_excused(self):
        historical = lambda d: d == {'old.html': [['old', {}]]}
        self.assertTrue(e.reviewed_viewer_additions(self.viewer, historical))
        changed = dict(self.viewer, **{'unknown.html': e.VIEWER_REFS})
        self.assertFalse(e.reviewed_viewer_additions(changed, historical))
        self.assertFalse(e.reviewed_viewer_additions(None, historical))
        # Actual unchanged old digest still rejects an arbitrary synthetic remainder.
        self.assertFalse(e.reviewed_viewer_additions(self.viewer, source_function('reviewed_viewer_bindings')))

    def test_history_style_exact_owners_and_versions(self):
        check = source_function('release_style_binding_allowed')
        tags = lambda ref: [('link', {'rel': 'stylesheet', 'href': ref})]
        for route in e.EMMA_STORY_ROUTES:
            self.assertTrue(check('history-stories.css', route, tags(e.STORY_REF)))
            for refs in ([], tags(e.STORY_REF + '-stale'), tags(e.STORY_REF) * 2):
                self.assertFalse(check('history-stories.css', route, refs))
        self.assertFalse(check('history-stories.css', 'history/emma-unknown.html', tags(e.STORY_REF)))
        self.assertTrue(check('history-stories.css', 'history/old.html', tags('../history-stories.css?v=fixture-old')))

    def test_routes_missing_duplicate_unknown(self):
        pages = list(e.EMMA_STORY_ROUTES) + ['old.html']
        self.assertEqual(e.historical_routes(pages), {'old.html'})
        with self.assertRaises(AssertionError): e.historical_routes(pages[:-2])
        with self.assertRaises(AssertionError): e.historical_routes(pages + [pages[0]])
        self.assertIn('unknown.html', e.historical_routes(pages + ['unknown.html']))

    def test_all_actual_reading_first_pages(self):
        for route in e.EMMA_STORY_ROUTES:
            text = (ROOT / route).read_text()
            e.assert_story_opening(route, text, BeautifulSoup(text, 'html.parser'))

    def test_unknown_opening_owner(self):
        text = (ROOT / self.route).read_text()
        with self.assertRaises(AssertionError):
            e.assert_story_opening('history/emma-unknown.html', text, BeautifulSoup(text, 'html.parser'))

    def test_header_body_art_structure_and_script_mutations(self):
        text = (ROOT / self.route).read_text()
        mutations = [text.replace('Primary navigation', 'Changed navigation', 1),
                     text.replace('fc-emma-study"', 'unknown-story"', 1),
                     text.replace('fc-life-opening"', 'missing-opening"', 1),
                     text.replace('fc-study-visual fc-life-picture', 'missing-picture', 1),
                     text.replace('id="sources"', 'id="missing-sources"', 1),
                     text.replace(e.COMMON_REF, e.COMMON_REF + '-stale', 1),
                     text.replace('<main>', '<main><div class="fc-visual-hero"></div>', 1)]
        for changed in mutations:
            self.assertNotEqual(text, changed)
            with self.assertRaises(AssertionError):
                e.assert_story_opening(self.route, changed, BeautifulSoup(changed, 'html.parser'))


if __name__ == '__main__':
    unittest.main()
