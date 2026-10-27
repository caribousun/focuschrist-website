"""Verify the explicit historical projection closes opening-inventory dependencies."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch
import owner_integration_test_fixtures as fixture

ROOT = Path(__file__).resolve().parents[1]
PATH = 'docs/unified-opening-inventory.json'
BASE_BLOB = '1b8a8fcd180c95591caff7a8cc26f90d8817942b'

class HistoricalFixtureClosureTests(unittest.TestCase):
    def test_exact_shared_baseline_inventory_is_projected(self):
        raw = (ROOT / PATH).read_bytes()
        self.assertEqual(fixture.SHARED[PATH], BASE_BLOB)
        self.assertEqual(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(), BASE_BLOB)
        projected = fixture.historical_root(ROOT)
        self.assertEqual((projected / PATH).read_bytes(), raw)

    def test_changed_baseline_pin_is_rejected_before_projection(self):
        previous = fixture._roots.pop(ROOT.resolve(), None)
        try:
            with patch.dict(fixture.SHARED, {PATH: '0' * 40}):
                with self.assertRaisesRegex(AssertionError, 'Shared historical fixture source drift'):
                    fixture.historical_root(ROOT)
        finally:
            if previous is not None:
                fixture._roots[ROOT.resolve()] = previous

    def test_changed_current_inventory_bytes_are_rejected(self):
        previous = fixture._roots.pop(ROOT.resolve(), None)
        original_read = Path.read_bytes
        def modified_read(path):
            raw = original_read(path)
            return raw + b' ' if path == ROOT / PATH else raw
        try:
            with patch.object(Path, 'read_bytes', modified_read):
                with self.assertRaisesRegex(AssertionError, 'Shared historical fixture source drift'):
                    fixture.historical_root(ROOT)
        finally:
            if previous is not None:
                fixture._roots[ROOT.resolve()] = previous

if __name__ == '__main__':
    unittest.main()
