"""Actual current generated indices and preserved predecessor composition.

These tests establish exact data/producer binding, not review or publication.
Run only after independent review, in an isolated hash-pinned test fixture.
"""
import tempfile
import unittest
from pathlib import Path

import adams_integration_indices as current
import adams_delivery_successor as previous
import emma_generated_indices_successor as emma
import timeline_source_import as timeline


class ActualCurrentIndexComposition(unittest.TestCase):
    def test_actual_current_producer_and_exact_three_pair_round_trip(self):
        self.assertEqual(current.check_current()['files'], sorted(current.AFTER))
        for name in current.AFTER:
            data = (current.ROOT / name).read_bytes()
            old = current.restore(name, data)
            self.assertEqual(current.sha(old), current.BEFORE[name])
            self.assertEqual(current.advance(name, old), data)

    def test_actual_composes_to_preserved_adams_emma_and_timeline_pins(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in current.AFTER:
                (root / name).write_bytes(current.restore(name, (current.ROOT / name).read_bytes()))
            for name in (previous.MANIFEST, emma.MANIFEST):
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((current.ROOT / name).read_bytes())
            self.assertEqual(previous.check(root)['files'], sorted(previous.AFTER))
            with previous.predecessor_view(root) as view:
                self.assertEqual(emma.check(view)['files'], sorted(emma.AFTER))
            restored_search = (root / 'site-search-index.json').read_bytes()
            self.assertEqual(previous.sha(timeline.restore_search(restored_search)),
                             '038391c9f469c4c7a24894c629b915851ec097d305e880bdfe12e6f24b3c9e0d')
            restored_gallery = (root / 'art-gallery.json').read_bytes()
            oldest_gallery = emma.restore('art-gallery.json', previous.restore('art-gallery.json', restored_gallery, root), root)
            self.assertEqual(previous.sha(oldest_gallery), timeline.REVIEWED_CONSUMER_INVERSES['art-gallery.json']['current'])

    def test_unknown_current_bytes_are_not_normalized(self):
        for name in current.AFTER:
            raw = (current.ROOT / name).read_bytes()
            for altered in (raw + b' ', bytes([raw[0] ^ 1]) + raw[1:]):
                self.assertEqual(current.restore(name, altered), altered)
                self.assertNotEqual(current.sha(altered), current.BEFORE[name])


if __name__ == '__main__':
    unittest.main()
