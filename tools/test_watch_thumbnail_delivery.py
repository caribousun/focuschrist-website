"""Exact positive coverage and targeted rejection cases for the approved cover."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from artwork_creation_gate import pixel_hash, page_dependencies
from artwork_watch_thumbnail_delivery import ASSET, SOURCE_SHA256, bound, canonical, validate

ROOT = Path(__file__).resolve().parents[1]

class WatchThumbnailDelivery(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'docs/watch-spannaus-thumbnail/delivery.json').read_text(encoding='utf8'))

    def run_record(self, record, binding=None):
        return validate(ROOT, record, binding or canonical(record['spec']), {ASSET}, set(), set(), pixel_hash, page_dependencies)

    def test_exact_current_record_passes(self):
        assets, hashes, pixels = self.run_record(self.record)
        self.assertEqual(assets, {ASSET})
        self.assertEqual(hashes, {SOURCE_SHA256})
        self.assertEqual(len(pixels), 1)

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

    def test_changed_evidence_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'evidence.json').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'changed evidence: evidence.json'):
                bound(root, {'path': 'evidence.json', 'sha256': '0' * 64})

if __name__ == '__main__':
    unittest.main()
