"""Pure exact current/previous source inverse tests; no rendered approval."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import owner_integration_successor as s

class IntegrationSuccessorTests(unittest.TestCase):
    def test_all_eight_actual_forward_and_inverse_endpoints(self):
        for name in s.NAMES:
            raw=(s.ROOT/name).read_bytes();old=s.restore(name,raw)
            self.assertEqual(s.sha(raw),s.CURRENT[name]);self.assertEqual(s.sha(old),s.BEFORE[name])
            self.assertEqual(s.advance(name,old),raw)

    def test_unknown_and_changed_inputs_are_not_projected(self):
        with tempfile.TemporaryDirectory() as td:
            empty=Path(td)
            for name in s.NAMES:
                raw=(s.ROOT/name).read_bytes();old=s.restore(name,raw)
                self.assertEqual(s.restore(name,raw+b' ',empty),raw+b' ')
                self.assertEqual(s.advance(name,old+b' ',empty),old+b' ')
                self.assertEqual(s.restore('unknown/'+name,raw,empty),raw)
                self.assertEqual(s.advance('unknown/'+name,old,empty),old)
                self.assertEqual(s.restore(name,old,empty),old)

    def test_current_endpoint_requires_real_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            for name in s.NAMES:
                raw=(s.ROOT/name).read_bytes();old=s.restore(name,raw)
                with self.assertRaises(OSError):s.restore(name,raw,Path(td))
                with self.assertRaises(OSError):s.advance(name,old,Path(td))

    def test_full_exact_source_registration_has_no_acceptance_claim(self):
        result=s.check();self.assertEqual(result['files'],11)
        self.assertIn('no current artwork/rendered/release approval',result['limits'])

if __name__=='__main__':unittest.main()
