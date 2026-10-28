"""Current semantics and explicit historical inverse tests; no rendered approval."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import owner_integration_successor as s

class IntegrationSuccessorTests(unittest.TestCase):
    def test_all_eight_actual_forward_and_inverse_endpoints(self):
        for name in s.NAMES:
            raw=(s.ROOT/name).read_bytes();old=s.restore(name,raw)
            if name == s.LANDING:
                s.validate_file(name,raw)
                fixture=(s.ROOT/'docs/timeline-selector/historical-c910.txt').read_bytes()
                self.assertEqual(s.sha(fixture),s.CURRENT[name])
            else:
                self.assertEqual(s.sha(raw),s.CURRENT[name])
            self.assertEqual(s.sha(old),s.BEFORE[name])
            self.assertEqual(s.advance(name,old),raw)

    def test_unknown_and_changed_inputs_are_not_projected(self):
        with tempfile.TemporaryDirectory() as td:
            empty=Path(td)
            for name in s.NAMES:
                raw=(s.ROOT/name).read_bytes();old=s.restore(name,raw)
                if name == s.LANDING:
                    changed=raw.replace(b'Explore the story of the Restoration.',b'Changed copy.',1)
                    self.assertNotEqual(changed,raw)
                    with self.assertRaises(AssertionError):s.restore(name,changed,empty)
                else:
                    self.assertEqual(s.restore(name,raw+b' ',empty),raw+b' ')
                self.assertEqual(s.advance(name,old+b' ',empty),old+b' ')
                self.assertEqual(s.restore('unknown/'+name,raw,empty),raw)
                self.assertEqual(s.advance('unknown/'+name,old,empty),old)
                if name == s.LANDING:
                    with self.assertRaises(AssertionError):s.restore(name,old,empty)
                else:
                    self.assertEqual(s.restore(name,old,empty),old)

    def test_current_endpoint_requires_real_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            for name in s.NAMES:
                raw=(s.ROOT/name).read_bytes();old=s.restore(name,raw)
                if name == s.LANDING:
                    root=Path(td)
                    (root/'docs/timeline-selector').mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(s.ROOT/'docs/timeline-selector/historical-c910.txt',root/'docs/timeline-selector/historical-c910.txt')
                    (root/name).write_bytes(raw)
                with self.assertRaises(OSError):s.restore(name,raw,Path(td))
                with self.assertRaises(OSError):s.advance(name,old,Path(td))

    def test_timeline_historical_fixture_tampering_rejected(self):
        raw=(s.ROOT/s.LANDING).read_bytes()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'docs/timeline-selector').mkdir(parents=True)
            (root/'docs/owner-integration-contract').mkdir(parents=True)
            shutil.copyfile(s.ROOT/'docs/owner-integration-contract/source-manifest.json',root/'docs/owner-integration-contract/source-manifest.json')
            fixture=root/'docs/timeline-selector/historical-c910.txt'
            fixture.write_bytes((s.ROOT/'docs/timeline-selector/historical-c910.txt').read_bytes()+b' ')
            with self.assertRaises(AssertionError):s.restore(s.LANDING,raw,root)

    def test_full_exact_source_registration_has_no_acceptance_claim(self):
        result=s.check();self.assertEqual(result['files'],11)
        self.assertIn('no current artwork/rendered/release approval',result['limits'])

if __name__=='__main__':unittest.main()
