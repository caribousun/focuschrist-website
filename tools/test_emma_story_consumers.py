"""Finite additive-contract tests; no full-checkout or rendered PASS claim."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import emma_story_consumers as e
import emma_retirement_consumers_successor as current
from owner_journey_successor import historical_fixture, validate_redirect

ROOT = Path(__file__).resolve().parents[1]


def historical_source(route):
    raw = (ROOT / route).read_bytes()
    if route == current.RETIRED:
        raw = historical_fixture(route, raw, ROOT)
    return raw.decode('utf-8')


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
        self.route = sorted(current.CURRENT)[0]
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

    def test_all_actual_reading_first_pages_and_exact_redirect(self):
        validate_redirect((ROOT / current.RETIRED).read_bytes())
        for route in current.CURRENT:
            text = (ROOT / route).read_text()
            e.assert_story_opening(route, text, BeautifulSoup(text, 'html.parser'))

    def test_retired_predecessor_opening_is_preserved_as_a_fixture(self):
        # Match Path.read_text's universal-newline normalization for the old bytes.
        text = historical_source(current.RETIRED).replace('\r\n', '\n').replace('\r', '\n')
        e.assert_story_opening(current.RETIRED, text, BeautifulSoup(text, 'html.parser'))

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


class ActualViewerParserTests(unittest.TestCase):
    def parser(self):
        tree = ast.parse((ROOT / 'tools/sitewide_artwork_review_qa.py').read_text())
        nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in {'Tags', 'viewer_bindings'}]
        self.assertEqual(len(nodes), 2)
        scope = {'HTMLParser': HTMLParser}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual selected viewer parser>', 'exec'), scope)
        return scope['viewer_bindings']

    def sources(self):
        return {route: historical_source(route) for route in e.EMMA_STORY_ROUTES}

    def test_four_actual_viewer_bindings_and_verified_redirect(self):
        validate_redirect((ROOT / current.RETIRED).read_bytes())
        sources = {route: (ROOT / route).read_text() for route in current.CURRENT}
        bindings = self.parser()(sources)
        self.assertEqual(set(bindings), current.CURRENT)
        self.assertTrue(current.reviewed_viewer_additions(bindings, lambda historical: historical == {}))
        self.assertNotIn(current.RETIRED, self.parser()({current.RETIRED: (ROOT / current.RETIRED).read_text()}))
        for route in current.CURRENT:
            changed = dict(bindings); del changed[route]
            self.assertFalse(current.reviewed_viewer_additions(changed, lambda _: True))
            changed = copy.deepcopy(bindings); changed[route][1][1]['src'] += '-unknown'
            self.assertFalse(current.reviewed_viewer_additions(changed, lambda _: True))
        self.assertFalse(current.reviewed_viewer_additions(dict(bindings, **{current.RETIRED: e.VIEWER_REFS}), lambda _: True))

    def test_actual_five_parser_shapes_and_additive_acceptance(self):
        bindings = self.parser()(self.sources())
        self.assertEqual(set(bindings), e.EMMA_STORY_ROUTES)
        for refs in bindings.values():
            self.assertIsInstance(refs, list)
            self.assertEqual(refs, e.VIEWER_REFS)
            self.assertIsNone(refs[1][1]['defer'])
        self.assertTrue(e.reviewed_viewer_additions(bindings, lambda historical: historical == {}))

    def test_each_actual_omitted_or_changed_owner_rejected(self):
        parse = self.parser()
        for route in e.EMMA_STORY_ROUTES:
            missing = self.sources(); del missing[route]
            self.assertFalse(e.reviewed_viewer_additions(parse(missing), lambda _: True))
            for old, new in [('20260922-viewer-3', 'unknown'),
                             ('20260919-viewer-1', 'unknown'),
                             ('full-image-viewer.js?v=20260919-viewer-1" defer', 'full-image-viewer.js?v=20260919-viewer-1" async')]:
                changed = self.sources(); self.assertIn(old, changed[route]); changed[route] = changed[route].replace(old, new, 1)
                self.assertFalse(e.reviewed_viewer_additions(parse(changed), lambda _: True))

    def test_unknown_and_duplicate_actual_refs_rejected(self):
        sources = self.sources(); route = sorted(sources)[0]
        sources['history/emma-unreviewed.html'] = sources[route]
        self.assertFalse(e.reviewed_viewer_additions(self.parser()(sources), lambda historical: historical == {}))
        for route in e.EMMA_STORY_ROUTES:
            for extra in ['<script src="../full-image-viewer.js?v=20260919-viewer-1" defer></script>', '<!-- full-image-viewer.js -->']:
                sources = self.sources(); sources[route] += extra
                self.assertFalse(e.reviewed_viewer_additions(self.parser()(sources), lambda _: True))


class ActualHistoryOwnerTests(unittest.TestCase):
    def check(self):
        tree = ast.parse((ROOT / 'tools/sitewide_artwork_review_qa.py').read_text())
        nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in {'Tags', 'reviewed_owner_consumers'}]
        self.assertEqual(len(nodes), 2)
        scope = {'HTMLParser': HTMLParser, 'EMMA_STORY_ROUTES': e.EMMA_STORY_ROUTES, 'STORY_REF': e.STORY_REF}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual owner predicate>', 'exec'), scope)
        return scope['reviewed_owner_consumers']

    def sources(self):
        sources = {route: historical_source(route) for route in e.EMMA_STORY_ROUTES}
        for route in self.owners:
            sources[route] = '<link rel="stylesheet" href="../history-stories.css?v=historical">'
        return sources

    owners = {'history/john-tanner.html', 'history/eleazer-miller.html', 'history/john-rowe-moyle.html', 'history/emma-hale-smith.html'}

    def test_actual_five_plus_unchanged_four(self):
        self.assertTrue(self.check()('history-stories.css', self.sources(), self.owners))
        for route in self.owners | e.EMMA_STORY_ROUTES:
            sources = self.sources(); del sources[route]
            self.assertFalse(self.check()('history-stories.css', sources, self.owners))

    def test_each_actual_ref_mutation_and_unknown_owner(self):
        for route in e.EMMA_STORY_ROUTES:
            for change in ['missing.css?v=none', e.STORY_REF + '-unknown']:
                sources = self.sources(); self.assertIn(e.STORY_REF, sources[route]); sources[route] = sources[route].replace(e.STORY_REF, change, 1)
                self.assertFalse(self.check()('history-stories.css', sources, self.owners))
            for extra in ['<link rel="stylesheet" href="' + e.STORY_REF + '">', '<!-- history-stories.css -->']:
                sources = self.sources(); sources[route] += extra
                self.assertFalse(self.check()('history-stories.css', sources, self.owners))
        sources = self.sources(); sources['history/unknown.html'] = sources[sorted(e.EMMA_STORY_ROUTES)[0]]
        self.assertFalse(self.check()('history-stories.css', sources, self.owners))

    def test_other_styles_keep_exact_old_owner_set(self):
        sources = {'one.html': 'example.css'}
        self.assertTrue(self.check()('example.css', sources, {'one.html'}))
        self.assertFalse(self.check()('example.css', dict(sources, **{'unknown.html': 'example.css'}), {'one.html'}))


class ActualControllerRegistryTests(unittest.TestCase):
    def build(self):
        tree = ast.parse((ROOT / 'tools/illustrated_study_navigation_qa.py').read_text())
        nodes = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name == 'controller_bindings_from_registry') or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'CONTROLLER_REF', 'HISTORICAL_CONTROLLER_SHA256'} for t in n.targets))]
        scope = {'hashlib': hashlib, 'json': json, 'historical_consumers': e.historical_consumers, 'EMMA_STORY_ROUTES': e.EMMA_STORY_ROUTES}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual registry partition>', 'exec'), scope)
        return scope['controller_bindings_from_registry']

    def inputs(self):
        registry = json.loads((ROOT / 'docs/topic-artwork-controller-bindings.json').read_text())
        rows = json.loads((ROOT / 'docs/continue-motion/predecessors.json').read_text())['files']
        return registry, rows

    def test_actual_registry_and_five_parser_bindings(self):
        registry, rows = self.inputs(); expected = self.build()(registry, rows)
        self.assertEqual(len(expected), 125)
        validate_redirect((ROOT / current.RETIRED).read_bytes())
        for route in current.CURRENT:
            doc = BeautifulSoup((ROOT / route).read_text(), 'html.parser')
            refs = [x['src'] for x in doc.select('script[src]') if 'topic-artwork-details.js' in x['src']]
            self.assertEqual(refs, registry[route]); self.assertEqual(refs, expected[route])
        retired = BeautifulSoup((ROOT / current.RETIRED).read_text(), 'html.parser')
        self.assertFalse([x for x in retired.select('script[src]') if 'topic-artwork-details.js' in x['src']])
        live = dict(expected); del live[current.RETIRED]
        import illustrated_study_navigation_qa as illustrated
        illustrated.assert_controller_bindings(live)
        self.assertEqual(len(set(expected) - e.EMMA_STORY_ROUTES), 120)

    def test_each_new_registry_omission_duplicate_version_unknown(self):
        registry, rows = self.inputs()
        for route in e.EMMA_STORY_ROUTES:
            for value in (None, [], registry[route] * 2, [registry[route][0].replace('20261021-continue-motion-1', 'unknown')]):
                changed = copy.deepcopy(registry)
                if value is None: del changed[route]
                else: changed[route] = value
                with self.assertRaises(AssertionError): self.build()(changed, rows)
        changed = dict(registry, **{'history/unknown.html': registry[sorted(e.EMMA_STORY_ROUTES)[0]]})
        with self.assertRaises(AssertionError): self.build()(changed, rows)

    def test_historical_binding_and_predecessor_not_weakened(self):
        registry, rows = self.inputs(); old = sorted(set(registry) - e.EMMA_STORY_ROUTES)[0]
        changed = copy.deepcopy(registry); changed[old] = [changed[old][0].replace('20261009-settled-continue-2', 'unknown')]
        with self.assertRaises(AssertionError): self.build()(changed, rows)
        with self.assertRaises(AssertionError): self.build()(registry, set(rows) - {old})


if __name__ == '__main__':
    unittest.main()
