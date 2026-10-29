"""Exact reconstruction and tamper negatives, without an approval claim."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import timeline_adams_diagnostic_successor as adams
import timeline_nazareth_successor as nazareth
import timeline_image_links_successor as images
import timeline_world_controls_successor as world

ROOT = Path(__file__).resolve().parents[1]


class TimelineSourceSuccessors(unittest.TestCase):
    def test_exact_adams_and_world_predecessors(self):
        for gate, path in ((adams, adams.PATH), (world, world.PAGE)):
            current = (ROOT / path).read_bytes()
            self.assertEqual(hashlib.sha256(gate.restore(current)).hexdigest(), gate.BEFORE)
            for changed in (current + b' ', current[:-1], current[:20] + b'X' + current[21:]):
                with self.subTest(path=path), self.assertRaises(AssertionError):
                    gate.restore(changed)
            with patch.object(gate, 'MANIFEST_SHA', '0' * 64), self.assertRaises(AssertionError):
                gate.restore(current)

    def test_nazareth_round_trip_and_tampering(self):
        current = (ROOT / 'answers/jesus-christ-latter-day-saint-beliefs.html').read_bytes()
        previous = nazareth.restore(current)
        self.assertEqual(nazareth.advance(previous), current)
        for changed in (current + b' ', current.replace(b'id="nazareth-childhood"', b'id="other"', 1)):
            with self.assertRaises(AssertionError): nazareth.restore(changed)
        with self.assertRaises(AssertionError): nazareth.advance(previous + b' ')

    def test_exact_image_links_and_tampering(self):
        from timeline_51_source_successor import restore as restore_current
        current = (ROOT / 'timeline-images.js').read_bytes()
        previous = restore_current('timeline-images.js',current)
        self.assertEqual(hashlib.sha256(images.restore(previous)).hexdigest(), images.BEFORE)
        for changed in (current+b' ', current.replace(b'picture=art-4f5759d8edad', b'picture=unreviewed', 1)):
            with self.assertRaises(ValueError): restore_current('timeline-images.js',changed)
        for changed in (previous+b' ', previous.replace(b'picture=art-4f5759d8edad', b'picture=unreviewed', 1)):
            with self.assertRaises(AssertionError): images.restore(changed)


if __name__ == '__main__':
    unittest.main()
