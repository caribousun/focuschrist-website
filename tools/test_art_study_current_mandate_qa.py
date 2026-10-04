"""Mutation tests verify strict rejection; passing tests do not accept real content."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from art_study_current_mandate_qa import PAGES, digest, evaluate


class StrictMandateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'art-study').mkdir()
        (self.root / 'assets').mkdir()
        (self.root / 'docs').mkdir()
        (self.root / 'art.html').write_text(''.join(
            f'<a data-artwork-detail href="{p}">Study</a>' for p in sorted(PAGES)))

    def tearDown(self):
        self.temp.cleanup()

    def evidence(self, name, value):
        path = self.root / 'docs' / (name + '.json')
        path.write_text(json.dumps(value), encoding='utf-8')
        return {'path': path.relative_to(self.root).as_posix(), 'sha256': digest(path)}

    def fixture(self, count=10, christ=5):
        registry = dict(schema_version=1, minimum_unique_originals=10,
                        christ_ratio='ceil(total/2)', pages={})
        for route in sorted(PAGES):
            slug = Path(route).stem
            entries, tags = [], []
            for i in range(count):
                asset = f'assets/{slug}-{i}.bin'
                (self.root / asset).write_bytes(asset.encode())
                section = f'scene-{i}'
                entry = dict(asset=asset, sha256=digest(self.root / asset),
                             kind='original', original_id=f'{slug}-{i}', owner_route=route,
                             owner_section=section, depicts_christ=i < christ)
                review = dict(entry, reviewers=['Fermi', 'Newton'],
                              lineage_and_cross_page_ownership_reviewed=True,
                              ownership_scope='all canonical site routes',
                              pixels_reviewed_for_christ_classification=True)
                entry['evidence'] = self.evidence(f'{slug}-{i}', review)
                entries.append(entry)
                tags.append(f'<section id="{section}"><a data-art-study-supporting href="../{asset}">Art</a></section>')
            (self.root / route).write_text(''.join(tags), encoding='utf-8')
            page_hash = digest(self.root / route)
            coverage = dict(route=route, html_sha256=page_hash,
                            complete_page_image_inventory_reviewed=True,
                            no_unregistered_qualifying_originals=True, reviewers=['Fermi', 'Newton'])
            registry['pages'][route] = dict(html_sha256=page_hash, placements=entries,
                                           coverage_evidence=self.evidence(slug + '-coverage', coverage))
        return registry

    def first(self, registry):
        return registry['pages'][sorted(PAGES)[0]]['placements'][0]

    def rebind(self, entry):
        reference = entry['evidence']
        path = self.root / reference['path']
        review = json.loads(path.read_text())
        for key in ('original_id', 'asset', 'sha256', 'owner_route', 'owner_section', 'depicts_christ'):
            review[key] = entry[key]
        path.write_text(json.dumps(review), encoding='utf-8')
        reference['sha256'] = digest(path)

    def check_fail(self, registry):
        result = evaluate(self.root, registry)
        self.assertEqual(result['status'], 'INCOMPLETE')
        return result

    def test_ten_half_christ_positive(self):
        self.assertEqual(evaluate(self.root, self.fixture())['status'], 'PASS')

    def test_six_actual_shape_fails_all_four(self):
        report = self.check_fail(self.fixture(6, 6))
        self.assertEqual([p['candidate_original_upper_bound_in_slots'] for p in report['pages']], [6]*4)
        self.assertTrue(all(p['status'] == 'FAIL' for p in report['pages']))

    def test_nine_fails(self):
        self.check_fail(self.fixture(9, 9))

    def test_eleven_rounds_up(self):
        self.check_fail(self.fixture(11, 5))
        self.assertEqual(evaluate(self.root, self.fixture(11, 6))['status'], 'PASS')

    def test_missing_or_nonboolean_christ_is_unverified(self):
        for value in (None, 'true', 1):
            registry = self.fixture()
            self.first(registry)['depicts_christ'] = value
            self.check_fail(registry)

    def test_changed_asset_bytes(self):
        registry = self.fixture()
        (self.root / self.first(registry)['asset']).write_bytes(b'changed')
        self.check_fail(registry)

    def test_changed_evidence_bytes(self):
        registry = self.fixture()
        (self.root / self.first(registry)['evidence']['path']).write_text('{}')
        self.check_fail(registry)

    def test_changed_page_bytes(self):
        registry = self.fixture()
        page = self.root / sorted(PAGES)[0]
        page.write_text(page.read_text() + '<img src="new.png">')
        self.check_fail(registry)

    def test_duplicate_original_derivative_different_bytes(self):
        registry = self.fixture()
        entries = registry['pages'][sorted(PAGES)[0]]['placements']
        entries[1]['original_id'] = entries[0]['original_id']
        self.rebind(entries[1])
        result = self.check_fail(registry)
        self.assertTrue(any('duplicate original or derivative' in d for d in result['pages'][0]['defects']))

    def test_renamed_same_bytes(self):
        registry = self.fixture()
        entries = registry['pages'][sorted(PAGES)[0]]['placements']
        (self.root / entries[1]['asset']).write_bytes((self.root / entries[0]['asset']).read_bytes())
        entries[1]['sha256'] = entries[0]['sha256']
        self.rebind(entries[1])
        result = self.check_fail(registry)
        self.assertTrue(any('duplicate original bytes' in d for d in result['pages'][0]['defects']))

    def test_wrong_existing_owning_section_even_with_rebound_review(self):
        registry = self.fixture()
        entry = self.first(registry)
        entry['owner_section'] = 'scene-1'
        self.rebind(entry)
        result = self.check_fail(registry)
        self.assertTrue(any('does not contain artwork' in d for d in result['pages'][0]['defects']))

    def test_reference_and_resource_do_not_count(self):
        for kind in ('reference', 'resource'):
            registry = self.fixture()
            entry = self.first(registry)
            entry['kind'] = kind
            entry['reference_target'] = 'other.html#owner'
            result = self.check_fail(registry)
            self.assertEqual(result['pages'][0]['evidenced_unique_originals'], 9)

    def test_reference_target_must_exist_and_be_in_picture_context(self):
        registry = self.fixture(11, 6)
        route = sorted(PAGES)[0]
        entry = self.first(registry)
        entry['kind'] = 'reference'
        entry['reference_target'] = '../owner.html#scene'
        (self.root / 'owner.html').write_text('<section id="scene">Owner</section>')
        result = self.check_fail(registry)
        self.assertTrue(any('link absent' in issue for issue in result['pages'][0]['unverified']))
        entry['reference_target'] = '../owner.html#missing'
        result = self.check_fail(registry)
        self.assertTrue(any('actual owning' in issue for issue in result['pages'][0]['unverified']))

    def test_fabricated_exclusion_cannot_reduce_ratio_denominator(self):
        registry = self.fixture(11, 6)
        entry = registry['pages'][sorted(PAGES)[0]]['placements'][-1]
        entry['kind'] = 'resource'
        result = self.check_fail(registry)
        self.assertTrue(any('exclusion evidence' in issue for issue in result['pages'][0]['unverified']))
        review = dict(entry, reviewers=['Fermi', 'Newton'], exclusion_classification_reviewed=True)
        review.pop('evidence')
        entry['evidence'] = self.evidence('resource-exclusion', review)
        result = evaluate(self.root, registry)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['pages'][0]['evidenced_unique_originals'], 10)
        self.assertEqual(result['pages'][0]['evidenced_christ_originals'], 6)

    def test_original_receipt_kind_mismatch(self):
        registry = self.fixture()
        entry = self.first(registry)
        path = self.root / entry['evidence']['path']
        review = json.loads(path.read_text())
        review['kind'] = 'resource'
        path.write_text(json.dumps(review))
        entry['evidence']['sha256'] = digest(path)
        result = self.check_fail(registry)
        self.assertTrue(any('does not bind kind' in issue for issue in result['pages'][0]['unverified']))

    def test_reviewed_reference_excluded_with_real_owner_link(self):
        registry = self.fixture(11, 6)
        route = sorted(PAGES)[0]
        entry = self.first(registry)
        entry.update(kind='reference', reference_target='../owner.html#scene')
        (self.root / 'owner.html').write_text('<section id="scene">Owner</section>')
        page = self.root / route
        page.write_text(page.read_text().replace('</section>',
            '<a href="../owner.html#scene">Owning study</a></section>', 1))
        data = registry['pages'][route]
        data['html_sha256'] = digest(page)
        ref = data['coverage_evidence']
        path = self.root / ref['path']
        coverage = json.loads(path.read_text())
        coverage['html_sha256'] = digest(page)
        path.write_text(json.dumps(coverage))
        ref['sha256'] = digest(path)
        review = dict(entry, reviewers=['Fermi', 'Newton'], exclusion_classification_reviewed=True)
        review.pop('evidence')
        entry['evidence'] = self.evidence('reference-exclusion', review)
        result = evaluate(self.root, registry)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['pages'][0]['evidenced_unique_originals'], 10)

    def test_missing_lineage_or_coverage(self):
        registry = self.fixture()
        self.first(registry)['original_id'] = None
        self.check_fail(registry)
        registry = self.fixture()
        registry['pages'][sorted(PAGES)[0]]['coverage_evidence'] = None
        self.check_fail(registry)

    def test_route_drift_and_exception_rejected(self):
        registry = self.fixture()
        registry['exceptions'] = {'art-study/be-still.html': 'waived'}
        self.check_fail(registry)
        registry = self.fixture()
        (self.root / 'art.html').write_text('<a data-artwork-detail href="art-study/new.html">New</a>')
        self.check_fail(registry)

    def test_lowered_threshold_rejected(self):
        registry = self.fixture()
        registry['minimum_unique_originals'] = 6
        self.check_fail(registry)


if __name__ == '__main__':
    unittest.main()
