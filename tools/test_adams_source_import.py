"""Exact Adams family tests; no browser, supplied JS, generation or full-site PASS.

One owned temporary fixture copies the 331 existing JPEGs once. Every source
input is hashed before copying and again after tests; only fixture files mutate.
ADAMS_TEST_INPUT_MAP supports the separately reviewed local source locations.
Without it, ordinary hosted CI reads the complete checked-out repository.
"""
import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import adams_source_import as family
import artwork_creation_gate as creation

ROOT = Path(__file__).resolve().parents[1]
BASE_GATE_SHA256 = '6b1ec432e8407af008dee4cc59db28b6d78aba60d472bf9c456f1cf98452f168'
DISPATCH = """    # Exact existing Adams chart import; no generated-art preflight is claimed.
    from adams_source_import import MANIFEST as ADAMS_IMPORT, validate as validate_adams_import
    if (root / ADAMS_IMPORT).exists() or any(p.startswith('assets/adams-chart/') for p in added):
        covered |= validate_adams_import(root, added, covered, rejected)
"""


class AdamsSourceImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((ROOT / family.MANIFEST).read_text(encoding='utf-8'))
        spec = cls.original['spec']
        items = [spec['page'], spec['landing'], spec['qa']['helper'], spec['qa']['report'], spec['qa']['run_identity'], *spec['assets']]
        items += [item for review in cls.original['reviews'] for item in review['evidence']]
        expected = {}
        for item in items:
            if item['path'] in expected:
                assert expected[item['path']] == {k: item[k] for k in ('bytes', 'sha256')}
            expected[item['path']] = {k: item[k] for k in ('bytes', 'sha256')}
        for name in (family.MANIFEST, 'tools/artwork_creation_gate.py'):
            raw = (ROOT / name).read_bytes()
            expected[name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        source_map = None
        if os.environ.get('ADAMS_TEST_INPUT_MAP'):
            source_map = json.loads(Path(os.environ['ADAMS_TEST_INPUT_MAP']).read_text(encoding='utf-8'))
            assert set(source_map) == set(expected), 'Unexpected source-map paths'
        cls.temp = tempfile.TemporaryDirectory(prefix='adams-import-', dir=os.environ.get('ADAMS_TEST_TEMP_PARENT'))
        cls.root = Path(cls.temp.name)
        cls.inputs = []
        try:
            for name, pin in expected.items():
                source = Path(source_map[name]['source']) if source_map else ROOT / name
                if source_map:
                    assert source_map[name]['bytes'] == pin['bytes'] and source_map[name]['sha256'] == pin['sha256']
                assert source.is_file() and not source.is_symlink(), 'Source must be regular'
                raw = source.read_bytes()
                assert len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Source input drift: ' + name
                dest = cls.root / name
                assert not Path(name).is_absolute() and '..' not in Path(name).parts and dest.resolve().is_relative_to(cls.root.resolve())
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open('xb') as handle:
                    handle.write(raw)
                cls.inputs.append((source, pin))
        except BaseException:
            cls.temp.cleanup()
            raise
        cls.paths = {r['path'] for r in spec['assets']}
        cls.first = spec['assets'][0]
        cls.report = json.loads((cls.root / spec['qa']['report']['path']).read_text())
        cls.identity = json.loads((cls.root / spec['qa']['run_identity']['path']).read_text())
        capture = next(e for e in cls.original['reviews'][0]['evidence'] if e['path'].endswith('/capture-manifest.json'))
        cls.captures = json.loads((cls.root / capture['path']).read_text())

    @classmethod
    def tearDownClass(cls):
        try:
            for source, pin in cls.inputs:
                raw = source.read_bytes()
                assert len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Original source changed: ' + str(source)
            print(json.dumps({'source_inputs_unchanged': len(cls.inputs), 'copied_tile_bytes': 119541095, 'scope': 'Adams source family only; no full-site release'}))
        finally:
            cls.temp.cleanup()

    def setUp(self):
        self.record = copy.deepcopy(self.original)

    def review_rejects(self, mutate):
        mutate(self.record)
        with self.assertRaises(ValueError):
            family.validate_reviews(self.root, self.record)

    @contextmanager
    def altered_file(self, name, transform=None, missing=False):
        path = self.root / name
        raw = path.read_bytes()
        if missing:
            path.unlink()
        else:
            path.write_bytes(transform(raw))
        try:
            yield
        finally:
            path.write_bytes(raw)

    def test01_exact_source(self):
        self.assertEqual(family.validate_source(self.root, self.record, self.paths, set(), set()), self.paths)

    def test02_exact_finished_import(self):
        self.assertEqual(family.validate(self.root, self.paths, set(), set()), self.paths)

    def test03_pending_status(self):
        self.review_rejects(lambda r: r.update(status='PENDING_FINISHED_REVIEW'))

    def test04_missing_root_or_independent(self):
        for name in ('Albert', 'Newton'):
            self.record = copy.deepcopy(self.original)
            self.review_rejects(lambda r: r.update(reviews=[v for v in r['reviews'] if v['reviewer'] != name]))

    def test05_duplicate_reviewer(self):
        self.review_rejects(lambda r: r['reviews'].append(copy.deepcopy(r['reviews'][0])))

    def test06_stale_or_negative_review(self):
        for key, value in [('spec_sha256', '0' * 64), ('decision', 'REJECT')]:
            self.record = copy.deepcopy(self.original)
            self.review_rejects(lambda r: r['reviews'][0].update({key: value}))

    def test07_unperformed_review(self):
        for key in ('finished_pixels', 'source_rights_checked', 'desktop_phone_inspected'):
            self.record = copy.deepcopy(self.original)
            self.review_rejects(lambda r: r['reviews'][0].update({key: False}))

    def test08_changed_review_evidence(self):
        self.review_rejects(lambda r: r['reviews'][0].update(evidence=[]))

    def test09_viewer_bytes(self):
        with self.altered_file(self.record['spec']['page']['path'], lambda b: b + b' '):
            with self.assertRaises(ValueError):
                family.validate_source(self.root, self.record, self.paths, set(), set())

    def test10_landing_bytes(self):
        with self.altered_file(self.record['spec']['landing']['path'], lambda b: b + b' '):
            with self.assertRaises(ValueError):
                family.validate_source(self.root, self.record, self.paths, set(), set())

    def test11_missing_tile(self):
        with self.altered_file(self.first['path'], missing=True):
            with self.assertRaises(ValueError):
                family.validate_source(self.root, self.record, self.paths, set(), set())

    def test12_changed_tile(self):
        with self.altered_file(self.first['path'], lambda b: bytes([b[0] ^ 1]) + b[1:]):
            with self.assertRaises(ValueError):
                family.validate_source(self.root, self.record, self.paths, set(), set())

    def test13_extra_chart_raster(self):
        with self.assertRaises(ValueError):
            family.validate_source(self.root, self.record, self.paths | {'assets/adams-chart/unreviewed.jpg'}, set(), set())

    def test14_absent_added_path(self):
        with self.assertRaises(ValueError):
            family.validate_source(self.root, self.record, self.paths - {self.first['path']}, set(), set())

    def test15_overlapping_coverage(self):
        with self.assertRaises(ValueError):
            family.validate_source(self.root, self.record, self.paths, {self.first['path']}, set())

    def test16_rejected_bytes(self):
        with self.assertRaises(ValueError):
            family.validate_source(self.root, self.record, self.paths, set(), {self.first['sha256']})

    def test17_spec_asset_drift(self):
        changes = [('key', '1:999:999'), ('path', '../outside.jpg'), ('bytes', 1), ('dimensions', [1, 1]), ('sha256', '0' * 64)]
        for key, value in changes:
            r = copy.deepcopy(self.original); r['spec']['assets'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                family.validate_source(self.root, r, self.paths, set(), set())
        for mutation in ('duplicate', 'missing', 'total'):
            r = copy.deepcopy(self.original)
            if mutation == 'duplicate': r['spec']['assets'].append(copy.deepcopy(r['spec']['assets'][0]))
            elif mutation == 'missing': r['spec']['assets'].pop()
            else: r['spec']['total_bytes'] += 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                family.validate_source(self.root, r, self.paths, set(), set())

    def test18_wrong_creation_class(self):
        for key, value in [('kind', 'GENERATED'), ('precreation_claim', True)]:
            r = copy.deepcopy(self.original); r['spec'][key] = value
            with self.assertRaises(ValueError):
                family.validate_source(self.root, r, self.paths, set(), set())

    def test19_credit_drift(self):
        with self.altered_file(self.record['spec']['page']['path'], lambda b: b.replace(b'The image is in the public domain.', b'CC BY-NC-SA')):
            with self.assertRaises(ValueError):
                family.validate_source(self.root, self.record, self.paths, set(), set())

    def test20_bound_evidence_drift(self):
        names = [e['path'] for e in self.record['reviews'][0]['evidence']] + [self.record['spec']['qa']['helper']['path']]
        for name in names:
            for missing in (False, True):
                with self.subTest(name=name, missing=missing), self.altered_file(name, lambda b: b + b' ', missing=missing):
                    with self.assertRaises(ValueError):
                        family.validate(self.root, self.paths, set(), set())

    def test21_qa_semantic_failures(self):
        # Pure semantic unit tests do not repin or approve mutated file evidence.
        mutations = [lambda r: r.update(timedOut=True), lambda r: r.update(sourceSHA256='0' * 64), lambda r: r['results'].pop(), lambda r: r['results'][0].update(pass_=False), lambda r: r['results'][0]['states'].pop(), lambda r: r.update(screenshots=23), lambda r: r['network'][0].update(sha256='0' * 64), lambda r: r['results'][0].update(initialFitOverlayOverlap=[{'area': 1}])]
        # The report field is literally "pass", not Python's reserved keyword.
        mutations[3] = lambda r: r['results'][0].update({'pass': False})
        for i, mutation in enumerate(mutations):
            r = copy.deepcopy(self.report); mutation(r)
            with self.subTest(case=i), self.assertRaises(ValueError):
                family.validate_qa_report(self.record['spec'], r, self.identity, self.captures)

    def test22_path_safety(self):
        for name in ('', '.', '../outside', '/absolute', 'C:bad', 'bad\\name'):
            with self.subTest(name=name), self.assertRaises(ValueError): family.local(self.root, name)
        link = self.root / 'owned-link.jpg'; link.symlink_to(self.root / self.first['path'])
        try:
            with self.assertRaises(ValueError): family.local(self.root, 'owned-link.jpg')
        finally: link.unlink()
        link = self.root / 'owned-dir'; link.symlink_to(self.root / 'assets/adams-chart', target_is_directory=True)
        try:
            with self.assertRaises(ValueError): family.local(self.root, 'owned-dir/' + Path(self.first['path']).name)
        finally: link.unlink()

    def test23_dispatch_preserves_emma_and_all_families(self):
        raw = (self.root / 'tools/artwork_creation_gate.py').read_text()
        self.assertEqual(raw.count(DISPATCH), 1)
        self.assertEqual(hashlib.sha256(raw.replace(DISPATCH, '').encode()).hexdigest(), BASE_GATE_SHA256)
        self.assertLess(raw.index('from artwork_emma_story_delivery'), raw.index(DISPATCH))
        self.assertLess(raw.index(DISPATCH), raw.index('from artwork_display_delivery import ASSETS'))
        self.assertIn("require(added == covered, 'New artwork missing exact review coverage: '", raw)

    def test24_unrelated_raster_is_not_covered(self):
        added = self.paths | {'assets/unrelated-new.jpg'}
        covered = family.validate_source(self.root, self.record, added, set(), set())
        self.assertEqual(covered, self.paths)
        with self.assertRaises(ValueError): creation.require(added == covered, 'Unrelated raster remains uncovered')

    def test25_no_public_review_rasters(self):
        extra = self.root / 'docs/adams-chart-import/unapproved-review.jpg'
        with extra.open('xb') as handle: handle.write(b'not an approved source tile')
        try:
            with self.assertRaises(ValueError): family.validate_source(self.root, self.record, self.paths, set(), set())
        finally: extra.unlink()


    def test26_current_heading_semantics(self):
        mutations = [('selector', 'div.title'), ('tag', 'DIV'), ('text', 'Changed'), ('fontWeight', '400'), ('fontFamily', 'Arial'), ('margins', ['1px'] * 4), ('fontSize', 10), ('visible', False), ('hit', False), ('width', 0), ('x', -10), ('right', 2000)]
        for field, value in mutations:
            r = copy.deepcopy(self.report); r['results'][0]['semantics']['heading'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): family.validate_qa_report(self.record['spec'], r, self.identity, self.captures)
        for changed in (None, {}):
            r = copy.deepcopy(self.report); r['results'][0]['semantics'] = changed
            with self.assertRaises(ValueError): family.validate_qa_report(self.record['spec'], r, self.identity, self.captures)

    def test27_current_continuation_semantics(self):
        for index in (0, 1):
            for field, value in [('tag', 'SPAN'), ('text', 'focusChrist Home'), ('href', '../unknown.html'), ('visible', False), ('hit', False), ('height', 0), ('bottom', 2000)]:
                r = copy.deepcopy(self.report); r['results'][0]['semantics']['continuations'][index][field] = value
                with self.subTest(index=index, field=field), self.assertRaises(ValueError): family.validate_qa_report(self.record['spec'], r, self.identity, self.captures)
        for changed in ([], [self.report['results'][0]['semantics']['continuations'][0]] * 2):
            r = copy.deepcopy(self.report); r['results'][0]['semantics']['continuations'] = changed
            with self.assertRaises(ValueError): family.validate_qa_report(self.record['spec'], r, self.identity, self.captures)

    def test28_current_producer_identity(self):
        for field, value in [('run_id', 40466288323), ('artifact_id', 12717295205), ('artifact_bytes', 2076475), ('head_sha', '0' * 40), ('timeline_job_id', 122062368456), ('timeline_conclusion', 'failure'), ('repository', 'other/repo'), ('event', 'push'), ('producer_ref', 'refs/heads/main'), ('producer_checkout_sha', '0' * 40), ('producer_base_sha', '0' * 40), ('release_claim', True), ('workflow_conclusion', 'success')]:
            identity = copy.deepcopy(self.identity); identity[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): family.validate_qa_report(self.record['spec'], self.report, identity, self.captures)

    def test29_home_return_journey_required(self):
        for index in range(4):
            r = copy.deepcopy(self.report)
            state = next(s for s in r['results'][index]['states'] if s['label'] == 'home-history-back-viewer')
            state['label'] = 'unreviewed-extra-state'
            with self.subTest(profile=index), self.assertRaises(ValueError): family.validate_qa_report(self.record['spec'], r, self.identity, self.captures)

    def test30_old_v6_spec_and_reviews_are_stale(self):
        self.assertNotEqual(family.APPROVED_SPEC, 'de9b54b09064fb7d8b9ccbe55a46298538e3bc29db68f0c805a40f8187dc45ac')
        self.review_rejects(lambda r: r['reviews'][0].update(spec_sha256='de9b54b09064fb7d8b9ccbe55a46298538e3bc29db68f0c805a40f8187dc45ac'))
        r = copy.deepcopy(self.original); r['spec']['page']['sha256'] = 'cce1020771c9f8d626ca000feb93153e189d78cf40f0110fa37174b019920a7b'
        with self.assertRaises(ValueError): family.validate_source(self.root, r, self.paths, set(), set())


if __name__ == '__main__':
    unittest.main()
