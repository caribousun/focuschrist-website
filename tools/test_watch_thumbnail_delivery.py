"""Exact positive coverage and targeted rejection cases for the approved cover."""
import copy
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from artwork_creation_gate import pixel_hash, page_dependencies
from artwork_watch_thumbnail_delivery import ASSET, SOURCE_SHA256, PREVIOUS_ASSET, PREVIOUS_SHA256, bound, canonical, validate
import artwork_bednar_watch_delivery as bednar

ROOT = Path(__file__).resolve().parents[1]

class WatchThumbnailDelivery(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'docs/watch-spannaus-portrait/delivery.json').read_text(encoding='utf8'))

    def run_record(self, record, binding=None):
        return validate(ROOT, record, binding or canonical(record['spec']), {ASSET, PREVIOUS_ASSET}, set(), set(), pixel_hash, page_dependencies)

    def test_exact_current_record_passes(self):
        assets, hashes, pixels = self.run_record(self.record)
        self.assertEqual(assets, {ASSET, PREVIOUS_ASSET})
        self.assertEqual(hashes, {SOURCE_SHA256, PREVIOUS_SHA256})
        self.assertEqual(len(pixels), 2)

    def test_changed_destination_and_asset_rejected(self):
        for field, value, message in [('video_id', 'xzAenmOZ1Yk', 'wrong destination'), ('route', 'index.html', 'wrong destination')]:
            changed = copy.deepcopy(self.record)
            changed['spec'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, message):
                self.run_record(changed)
        changed = copy.deepcopy(self.record)
        changed['spec']['asset']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'wrong approved asset'):
            self.run_record(changed)

    def test_missing_owner_approval_rejected(self):
        changed = copy.deepcopy(self.record)
        changed['spec']['owner_approval']['path'] = 'docs/watch-spannaus-thumbnail/absent.json'
        with self.assertRaisesRegex(ValueError, 'missing or escaped evidence'):
            self.run_record(changed)

    def test_missing_assembled_reviewer_rejected(self):
        self.record['reviews'] = self.record['reviews'][:2]
        with self.assertRaisesRegex(ValueError, 'three assembled reviews required'):
            self.run_record(self.record)

    def test_stale_specification_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unreviewed specification'):
            self.run_record(self.record, '0' * 64)

    def test_missing_retained_square_record_rejected(self):
        changed = copy.deepcopy(self.record)
        changed['spec']['retained_square_delivery']['path'] = 'docs/watch-spannaus-portrait/missing.json'
        with self.assertRaisesRegex(ValueError, 'missing or escaped evidence'):
            self.run_record(changed)

    def test_historical_context_cannot_be_claimed_current(self):
        changed = copy.deepcopy(self.record)
        changed['spec']['historical_square_scope'] = 'Current artwork acceptance'
        with self.assertRaisesRegex(ValueError, 'missing historical scope'):
            self.run_record(changed)

    def test_changed_evidence_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'evidence.json').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'changed evidence: evidence.json'):
                bound(root, {'path': 'evidence.json', 'sha256': '0' * 64})

class BednarWatchDelivery(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'docs/watch-bednar/delivery.json').read_text(encoding='utf8'))

    def run_record(self, record):
        return bednar.validate(ROOT, record, canonical(record['spec']), {bednar.ASSET}, set(), set(), pixel_hash, page_dependencies)

    def test_current_exact_delivery_passes(self):
        assets, hashes, pixels = self.run_record(self.record)
        self.assertEqual(assets, {bednar.ASSET})
        self.assertEqual(hashes, {bednar.ASSET_SHA256})
        self.assertEqual(len(pixels), 1)

    def test_changed_source_and_destination_rejected(self):
        for field, value, error in [('video_id', 'AGS45Fd9nmE', 'wrong Bednar destination'), ('route', 'index.html', 'wrong Bednar destination')]:
            record = copy.deepcopy(self.record)
            record['spec'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, error):
                self.run_record(record)
        record = copy.deepcopy(self.record)
        record['spec']['asset']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'wrong Bednar derivative'):
            self.run_record(record)

    def test_missing_current_review_rejected(self):
        self.record['reviews'] = self.record['reviews'][:2]
        with self.assertRaisesRegex(ValueError, 'three current Watch reviewers required'):
            self.run_record(self.record)

    def test_current_context_cannot_omit_player(self):
        self.record['spec']['context'] = [item for item in self.record['spec']['context'] if item['path'] != 'watch-shorts.js']
        with self.assertRaisesRegex(ValueError, 'missing current Watch context'):
            self.run_record(self.record)

    def test_private_publication_rejected(self):
        publication = self.record['spec']['publication']
        actual_bound = bednar.bound
        with tempfile.TemporaryDirectory() as folder:
            invalid = Path(folder) / 'private.json'
            value = json.loads((ROOT / publication['path']).read_text(encoding='utf8'))
            value['status'] = 'PRIVATE'
            invalid.write_text(json.dumps(value), encoding='utf8')
            def replacement(root, item):
                return invalid if item == publication else actual_bound(root, item)
            with patch.object(bednar, 'bound', side_effect=replacement):
                with self.assertRaisesRegex(ValueError, 'Bednar public verification missing'):
                    self.run_record(self.record)

    def test_changed_latest_selection_rejected(self):
        changed = copy.deepcopy(bednar.LATEST_IDS)
        changed[1], changed[2] = changed[2], changed[1]
        with patch.object(bednar, 'LATEST_IDS', changed):
            with self.assertRaisesRegex(ValueError, 'Bednar public verification missing'):
                self.run_record(self.record)

if __name__ == '__main__':
    unittest.main()
