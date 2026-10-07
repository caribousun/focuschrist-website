"""Meaningful rejection fixtures for artwork evidence, not aesthetic assertions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import artwork_creation_gate as gate


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in [*gate.MANDATES, 'prompt.txt', 'source.json', 'page.html', 'style.css', 'desktop.txt', 'phone.txt']:
            path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(name)
        for name, color in [('ref.png', 'red'), ('original.png', 'green'), ('desktop.webp', 'blue'), ('phone.webp', 'yellow')]:
            Image.new('RGB', (16, 16), color).save(self.root / name)
        (self.root / 'page.html').write_text('<link rel="stylesheet" href="style.css?v=1">')
        self.spec = {'id': 'scene', 'role': 'hero', 'route': 'page.html', 'prompt': self.file('prompt.txt'), 'mandates': [self.file(p) for p in sorted(gate.MANDATES)], 'references': [self.file('ref.png')], 'source_record': self.file('source.json'), 'scene_date': '1832-03-01', 'characters': [{'name': 'Eleazer', 'birth_date': '1795-11-04', 'age': 36, 'reference_path': 'ref.png', 'identity_authority': 'owner-linked-expression-correction', 'owner_evidence': 'Direct owner expression correction'}], 'period_clothing_setting': '1832 evidence', 'interaction': 'Teaching and listening'}
        self.preflight = {'spec': self.spec, 'reviews': self.receipts('preflight', gate.canonical(self.spec), '2026-10-07T01:00:00Z')}
        self.finished_spec = {'id': 'scene', 'role': 'hero', 'route': 'page.html', 'preflight_sha256': gate.canonical(self.spec), 'generated_at': '2026-10-07T01:01:00Z', 'owner_status': 'not-reviewed', 'ancestor_sha256': [self.file('ref.png')['sha256']], 'original': self.file('original.png', True), 'derivatives': [self.file('desktop.webp', True), self.file('phone.webp', True)], 'page_context': [self.file('page.html'), self.file('style.css')]}
        self.creation = {'spec': self.finished_spec, 'reviews': self.receipts('finished', gate.canonical(self.finished_spec), '2026-10-07T01:02:00Z'), 'root_review': {'reviewer': 'Albert', 'verdict': 'PASS', 'binding_sha256': gate.canonical(self.finished_spec), 'observations': 'Actual desktop and phone inspected', 'evidence': {'desktop': [self.file('desktop.txt')], 'phone': [self.file('phone.txt')]}}}

    def file(self, name, pixels=False):
        result = {'path': name, 'sha256': gate.digest(self.root / name)}
        if pixels: result['pixel_sha256'] = gate.pixel_hash(self.root / name)
        return result

    def receipts(self, stage, binding, time):
        records = []
        for who in ['Fermi', 'Newton']:
            r = {'reviewer': who, 'receipt_id': stage + who, 'stage': stage, 'verdict': 'PASS', 'withdrawn': False, 'binding_sha256': binding, 'reviewed_at': time, 'observations': 'Independent observations'}
            if stage == 'finished':
                r.update(checks={key: 'Observed exact pixels' for key in gate.CHECKS}, full_resolution_inspected=True, face_details_inspected=True, evidence=[self.file('desktop.txt')])
            records.append(r)
        return records

    def validate(self):
        return gate.validate_creation(self.root, self.creation, self.preflight, gate.REJECTED)

    def reject(self, text):
        with self.assertRaisesRegex(ValueError, text): self.validate()

    def rebind(self):
        value = gate.canonical(self.finished_spec)
        for r in self.creation['reviews']: r['binding_sha256'] = value
        self.creation['root_review']['binding_sha256'] = value

    def test_complete_exact_record(self): self.assertEqual(len(self.validate()), 3)
    def test_missing_reviewer(self): self.preflight['reviews'].pop(); self.reject('two reviewers')
    def test_duplicate_reviewer(self): self.preflight['reviews'][1]['reviewer'] = 'Fermi'; self.reject('distinct')
    def test_duplicate_receipt(self): self.preflight['reviews'][1]['receipt_id'] = self.preflight['reviews'][0]['receipt_id']; self.reject('receipt')
    def test_negative(self): self.creation['reviews'][0]['verdict'] = 'FAIL'; self.reject('negative')
    def test_withdrawn(self): self.creation['reviews'][0]['withdrawn'] = True; self.reject('withdrawn')
    def test_wrong_stage(self): self.creation['reviews'][0]['stage'] = 'preflight'; self.reject('wrong-stage')
    def test_prompt_changed(self): (self.root / 'prompt.txt').write_text('changed'); self.reject('Stale evidence')
    def test_reference_changed(self): (self.root / 'ref.png').write_bytes(b'changed'); self.reject('Stale evidence')
    def test_mandate_changed(self): (self.root / 'AGENTS.md').write_text('changed'); self.reject('Stale evidence')
    def test_original_changed(self): (self.root / 'original.png').write_bytes(b'changed'); self.reject('Stale evidence')
    def test_derivative_changed(self): (self.root / 'phone.webp').write_bytes(b'changed'); self.reject('Stale evidence')
    def test_page_changed(self): (self.root / 'page.html').write_text('changed'); self.reject('Stale evidence')
    def test_applicable_stylesheet_cannot_be_omitted_and_rebound(self):
        self.finished_spec['page_context'] = [self.file('page.html')]; self.rebind(); self.reject('Applicable page/CSS missing')
    def test_applicable_stylesheet_change_invalidates_review(self):
        (self.root / 'style.css').write_text('body { display:none }'); self.reject('Stale evidence')
    def test_imported_stylesheet_cannot_be_omitted(self):
        (self.root / 'nested.css').write_text('body { color:red }')
        (self.root / 'style.css').write_text('@import url("nested.css?v=2");')
        self.finished_spec['page_context'][1] = self.file('style.css'); self.rebind(); self.reject('nested.css')
    def test_inline_import_cannot_be_omitted(self):
        (self.root / 'nested.css').write_text('body { color:red }')
        (self.root / 'page.html').write_text('<style>@import "nested.css";</style>')
        self.finished_spec['page_context'][0] = self.file('page.html'); self.rebind(); self.reject('nested.css')
    def test_recursive_import_and_cycle_bound(self):
        (self.root / 'nested.css').write_text('@import "style.css";')
        (self.root / 'style.css').write_text('@import url("nested.css");')
        self.finished_spec['page_context'] = [self.file(p) for p in ['page.html', 'style.css', 'nested.css']]
        self.rebind(); self.assertEqual(len(self.validate()), 3)
    def test_age_mismatch(self): self.spec['characters'][0]['age'] = 30; self.reject('age mismatch')
    def test_scene_mismatch(self): self.finished_spec['id'] = 'other'; self.reject('preflight mismatch')
    def test_generation_before_preflight(self): self.finished_spec['generated_at'] = '2026-10-07T00:00:00Z'; self.reject('preceded')
    def test_finished_before_generation(self): self.creation['reviews'][0]['reviewed_at'] = '2026-10-07T00:00:00Z'; self.reject('predates')
    def test_owner_rejection_overrides_pass(self): self.finished_spec['owner_status'] = 'rejected'; self.rebind(); self.reject('Owner-rejected')
    def test_rejected_ancestor(self): self.finished_spec['ancestor_sha256'].extend(gate.REJECTED); self.rebind(); self.reject('rejected ancestor')
    def test_rejected_reference(self):
        with self.assertRaisesRegex(ValueError, 'Owner-rejected evidence'):
            gate.validate_creation(self.root, self.creation, self.preflight, {self.file('ref.png')['sha256']})
    def test_missing_lineage(self): self.finished_spec['ancestor_sha256'] = []; self.reject('lineage')
    def test_stale_decoded_pixels(self): self.finished_spec['original']['pixel_sha256'] = '0' * 64; self.reject('decoded')
    def test_missing_pixel_inspection(self): self.creation['reviews'][0]['face_details_inspected'] = False; self.reject('inspection')
    def test_missing_quality_dimension(self): del self.creation['reviews'][0]['checks']['atmosphere']; self.reject('pixel checks')
    def test_stale_root_review(self): self.creation['root_review']['binding_sha256'] = '0' * 64; self.reject('Albert')
    def test_missing_phone(self): del self.creation['root_review']['evidence']['phone']; self.reject('phone')
    def test_reuse_across_stages(self): self.creation['reviews'][0]['receipt_id'] = self.preflight['reviews'][0]['receipt_id']; self.reject('reused across')
    def test_path_escape(self): self.spec['prompt']['path'] = '../outside.txt'; self.reject('inside repository')
    def test_decoded_hash_detects_reencoding(self):
        Image.open(self.root / 'original.png').save(self.root / 'same.bmp')
        self.assertNotEqual(gate.digest(self.root / 'original.png'), gate.digest(self.root / 'same.bmp'))
        self.assertEqual(gate.pixel_hash(self.root / 'original.png'), gate.pixel_hash(self.root / 'same.bmp'))

    def setup_edit(self):
        edit_spec = copy.deepcopy(self.spec)
        edit_spec['id'] = 'wide-edit'
        edit_spec['edit_target'] = self.file('original.png')
        self.edit = {'spec': edit_spec, 'reviews': self.receipts('preflight', gate.canonical(edit_spec), '2026-10-07T01:03:00Z')}
        for r in self.edit['reviews']: r['receipt_id'] += '-edit'
        self.finished_spec['derivative_generations'] = [{'preflight_id': 'wide-edit', 'preflight_sha256': gate.canonical(edit_spec), 'generated_at': '2026-10-07T01:04:00Z', 'outputs': ['desktop.webp']}]
        for r in self.creation['reviews']: r['reviewed_at'] = '2026-10-07T01:05:00Z'
        self.rebind()

    def validate_edit(self):
        return gate.validate_creation(self.root, self.creation, self.preflight, gate.REJECTED, [self.preflight, self.edit])

    def reject_edit(self, message):
        with self.assertRaisesRegex(ValueError, message): self.validate_edit()

    def rebind_edit(self):
        binding = gate.canonical(self.edit['spec'])
        for r in self.edit['reviews']: r['binding_sha256'] = binding
        self.finished_spec['derivative_generations'][0]['preflight_sha256'] = binding
        self.rebind()

    def test_exact_two_generation_chain(self):
        self.setup_edit(); self.assertEqual(len(self.validate_edit()), 3)
    def test_missing_derivative_preflight(self):
        self.setup_edit()
        with self.assertRaisesRegex(ValueError, 'Missing unique derivative preflight'): self.validate()
    def test_stale_edit_prompt(self):
        self.setup_edit(); (self.root/'prompt.txt').write_text('changed'); self.reject_edit('Stale evidence')
    def test_missing_edit_reviewer(self):
        self.setup_edit(); self.edit['reviews'].pop(); self.reject_edit('two reviewers')
    def test_edit_target_changed(self):
        self.setup_edit(); self.edit['spec']['edit_target']['sha256'] = '0'*64; self.reject_edit('Stale evidence')
    def test_edit_target_unrelated(self):
        self.setup_edit(); self.edit['spec']['edit_target'] = self.file('ref.png'); self.rebind_edit(); self.reject_edit('not original')
    def test_edit_preflight_before_target(self):
        self.setup_edit(); self.edit['reviews'][0]['reviewed_at'] = '2026-10-07T01:00:00Z'; self.reject_edit('chronology')
    def test_edit_generation_before_preflight(self):
        self.setup_edit(); self.finished_spec['derivative_generations'][0]['generated_at'] = '2026-10-07T01:02:00Z'; self.reject_edit('chronology')
    def test_finished_before_edit(self):
        self.setup_edit(); self.creation['reviews'][0]['reviewed_at'] = '2026-10-07T01:03:30Z'; self.reject_edit('predates')
    def test_edit_cannot_redeclare_original_output(self):
        self.setup_edit(); self.finished_spec['derivative_generations'][0]['outputs'] = ['original.png']; self.reject_edit('new delivered')
    def test_duplicate_edit_output(self):
        self.setup_edit(); self.finished_spec['derivative_generations'][0]['outputs'] = ['desktop.webp','desktop.webp']; self.reject_edit('duplicate derivative')
    def test_edit_unknown_output(self):
        self.setup_edit(); self.finished_spec['derivative_generations'][0]['outputs'] = ['unknown.png']; self.reject_edit('new delivered')
    def test_duplicate_edit_record(self):
        self.setup_edit(); self.finished_spec['derivative_generations'] *= 2; self.reject_edit('Duplicate derivative')
    def test_edit_reused_receipt(self):
        self.setup_edit(); self.edit['reviews'][0]['receipt_id'] = self.preflight['reviews'][0]['receipt_id']; self.reject_edit('reused across generation')
    def test_edit_changes_identity(self):
        self.setup_edit(); self.edit['spec']['characters'][0]['owner_evidence'] = 'different'; self.rebind_edit(); self.reject_edit('character or event drift')
    def test_edit_changes_route(self):
        self.setup_edit(); self.edit['spec']['route'] = 'other.html'; self.rebind_edit(); self.reject_edit('placement mismatch')
    def test_stale_edit_binding(self):
        self.setup_edit(); self.finished_spec['derivative_generations'][0]['preflight_sha256'] = '0'*64; self.reject_edit('Stale derivative')
    def test_edit_changed_after_finished_review(self):
        self.setup_edit(); self.finished_spec['derivative_generations'][0]['generated_at'] = '2026-10-07T01:04:30Z'; self.reject_edit('stale review binding')

    def test_prospective_html_checks_exact_bytes_without_write(self):
        old = (self.root/'page.html').read_bytes()
        new = b'<p>New candidate</p><link rel="stylesheet" href="style.css">'
        self.finished_spec['page_context'][0]['sha256'] = gate.hashlib.sha256(new).hexdigest(); self.rebind()
        self.assertEqual(len(gate.validate_creation(self.root, self.creation, self.preflight, gate.REJECTED, page_overrides={'page.html': new})), 3)
        self.assertEqual((self.root/'page.html').read_bytes(), old)
        self.reject('Stale evidence')
    def test_prospective_html_rejects_old_binding(self):
        with self.assertRaisesRegex(ValueError, 'Stale evidence'):
            gate.validate_creation(self.root, self.creation, self.preflight, gate.REJECTED, page_overrides={'page.html': b'new'})
    def test_prospective_dependencies_use_new_page(self):
        (self.root/'new.css').write_text('body {color:red}')
        new = b'<link rel="stylesheet" href="new.css">'
        self.finished_spec['page_context'][0]['sha256'] = gate.hashlib.sha256(new).hexdigest(); self.rebind()
        with self.assertRaisesRegex(ValueError, 'new.css'):
            gate.validate_creation(self.root, self.creation, self.preflight, gate.REJECTED, page_overrides={'page.html': new})
    def test_override_rejects_noncanonical_or_nonhtml_path(self):
        for name in ['../page.html','/page.html','a/../page.html','page.html?x','style.css','original.png','docs/artwork-creation-reviews.json','C:/page.html','a\\page.html','.hidden/page.html']:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Invalid prospective'):
                gate.checked_overrides(self.root,{name:b'x'})
    def test_override_rejects_unknown_page(self):
        with self.assertRaisesRegex(ValueError,'Missing evidence'): gate.checked_overrides(self.root,{'unknown.html':b'x'})
    def test_override_rejects_text_and_invalid_utf8(self):
        with self.assertRaisesRegex(ValueError,'exact UTF-8 bytes'): gate.checked_overrides(self.root,{'page.html':'x'})
        with self.assertRaises(UnicodeDecodeError): gate.checked_overrides(self.root,{'page.html':bytes([255])})
    def test_release_cannot_use_overrides(self):
        with self.assertRaisesRegex(ValueError,'only supported in use'): gate.run(self.root, 'release', page_overrides={'page.html':b'x'})
    def test_preflight_cannot_use_overrides(self):
        with self.assertRaisesRegex(ValueError,'only supported in use'): gate.run(self.root, 'preflight', page_overrides={'page.html':b'x'})

    def registry(self, creations=None):
        docs = self.root / 'docs'; docs.mkdir(exist_ok=True)
        (docs / 'artwork-creation-baseline.json').write_text(json.dumps({'schema': 1, 'commit': gate.BASELINE, 'rejected_sha256': list(gate.REJECTED)}))
        (docs / 'artwork-creation-reviews.json').write_text(json.dumps({'schema': 1, 'preflights': [self.preflight] if creations else [], 'creations': creations or []}))

    def test_empty_registry_only_unchanged_baseline(self):
        self.registry()
        with patch.object(gate, 'baseline_check', return_value={'ref.png': 'blob'}), patch.object(gate.subprocess, 'check_output', return_value=b'ref.png\0'):
            self.assertEqual(gate.run(self.root)['new_rasters'], 0)

    def test_added_image_cannot_omit_registry(self):
        self.registry()
        with patch.object(gate, 'baseline_check', return_value={'ref.png': 'blob'}), patch.object(gate.subprocess, 'check_output', return_value=b'ref.png\0new.png\0'):
            with self.assertRaisesRegex(ValueError, 'missing exact review coverage'): gate.run(self.root)

    def test_hidden_public_rasters_cannot_omit_registry(self):
        self.registry()
        for name in ['assets/.new-hidden.png', 'assets/.new/hero.webp', '.public/hero.png']:
            with self.subTest(name=name), patch.object(gate, 'baseline_check', return_value={}), patch.object(gate.subprocess, 'check_output', return_value=(name+'\0').encode()):
                with self.assertRaisesRegex(ValueError, 'missing exact review coverage'): gate.run(self.root)

    def test_named_qa_output_excluded_but_nested_names_are_not(self):
        self.registry()
        with patch.object(gate, 'baseline_check', return_value={}), patch.object(gate.subprocess, 'check_output', return_value=b'.qa-artifacts/shot.png\0'):
            self.assertEqual(gate.run(self.root)['new_rasters'], 0)
        with patch.object(gate, 'baseline_check', return_value={}), patch.object(gate.subprocess, 'check_output', return_value=b'assets/.qa-artifacts/shot.png\0'):
            with self.assertRaisesRegex(ValueError, 'missing exact review coverage'): gate.run(self.root)

    def test_duplicate_creation_record(self):
        self.registry([self.creation, copy.deepcopy(self.creation)])
        with patch.object(gate, 'baseline_check', return_value={}):
            with self.assertRaisesRegex(ValueError, 'Duplicate scene'): gate.run(self.root)

    def test_valid_registered_creation_passes_run(self):
        self.registry([self.creation])
        with patch.object(gate, 'baseline_check', return_value={'ref.png': 'blob'}), patch.object(gate.subprocess, 'check_output', return_value=b'ref.png\0original.png\0desktop.webp\0phone.webp\0'):
            self.assertEqual(gate.run(self.root)['new_creations'], 1)

    def test_hero_cannot_reuse_frozen_body_path(self):
        self.registry([self.creation])
        with patch.object(gate, 'baseline_check', return_value={'ref.png': 'blob', 'original.png': 'blob'}), patch.object(gate.subprocess, 'check_output', return_value=b'ref.png\0original.png\0desktop.webp\0phone.webp\0'):
            with self.assertRaisesRegex(ValueError, 'not frozen body artwork'): gate.run(self.root)

    def test_derivative_duplicate_bytes_rejected(self):
        (self.root / 'phone.webp').write_bytes((self.root / 'ref.png').read_bytes())
        self.finished_spec['derivatives'][1] = self.file('phone.webp', True); self.rebind(); self.registry([self.creation])
        with patch.object(gate, 'baseline_check', return_value={'ref.png': 'blob'}), patch.object(gate.subprocess, 'check_output', return_value=b'ref.png\0original.png\0desktop.webp\0phone.webp\0'):
            with self.assertRaisesRegex(ValueError, 'duplicates existing artwork'): gate.run(self.root)

    def test_derivative_duplicate_pixels_rejected(self):
        Image.open(self.root / 'ref.png').save(self.root / 'phone.webp', lossless=True)
        self.finished_spec['derivatives'][1] = self.file('phone.webp', True); self.rebind(); self.registry([self.creation])
        with patch.object(gate, 'baseline_check', return_value={'ref.png': 'blob'}), patch.object(gate.subprocess, 'check_output', return_value=b'ref.png\0original.png\0desktop.webp\0phone.webp\0'):
            with self.assertRaisesRegex(ValueError, 'duplicates existing decoded'): gate.run(self.root)

    def test_baseline_anchor_cannot_advance(self):
        with self.assertRaisesRegex(ValueError, 'Immutable baseline'): gate.baseline_check(self.root, {'schema': 1, 'commit': 'HEAD'})

    def test_cannot_remove_rejection(self):
        with self.assertRaisesRegex(ValueError, 'rejection removed'): gate.baseline_check(self.root, {'schema': 1, 'commit': gate.BASELINE, 'rejected_sha256': []})

    def test_frozen_image_modified(self):
        with patch.object(gate, 'git_inventory', return_value={'ref.png': 'wrong'}):
            with self.assertRaisesRegex(ValueError, 'Frozen baseline'): gate.baseline_check(self.root, {'schema': 1, 'commit': gate.BASELINE, 'rejected_sha256': list(gate.REJECTED)})


if __name__ == '__main__': unittest.main()
