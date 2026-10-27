"""Standalone fail-closed contract tests; no network, subprocess or real gate run."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('emma_delivery', Path(__file__).with_name('artwork_emma_story_delivery.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class NegativeContract(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((Path(__file__).parents[1] / gate.MANIFEST).read_text())

    def call(self, record):
        return gate.validate(Path('.'), record, set(), set(), set(), lambda p:'', lambda r,p:set())

    def test_pending_approval_pin_blocks(self):
        with patch.object(gate, 'APPROVED_RECORD_SHA256', None):
            with self.assertRaisesRegex(ValueError, 'pending independent'):
                self.call(self.record)

    def test_whole_record_drift_blocks(self):
        with patch.object(gate, 'APPROVED_RECORD_SHA256', '0'*64):
            with self.assertRaisesRegex(ValueError, 'unreviewed record'):
                self.call(self.record)

    def test_pending_status_even_if_bound_blocks(self):
        pending = copy.deepcopy(self.record)
        pending['status'] = 'PENDING_FINISHED_REVIEW'
        with patch.object(gate, 'APPROVED_RECORD_SHA256', gate.canonical(pending)):
            with self.assertRaisesRegex(ValueError, 'unfinished record'):
                self.call(pending)

    def mutate_early(self, change, message):
        r=copy.deepcopy(self.record);r['status']='REVIEWED_EXACT_CURRENT_EQUIVALENCE';change(r)
        with patch.object(gate, 'APPROVED_RECORD_SHA256', gate.canonical(r)):
            with self.assertRaisesRegex(ValueError,message):self.call(r)

    def test_no_retroactive_preflight(self):
        self.mutate_early(lambda r:r['spec'].update(historical_canonical_preflight_claim=True),'false historical')

    def test_scene_omission_blocks(self):
        self.mutate_early(lambda r:r['spec']['scenes'].pop(),'scene expansion')

    def test_private_reference_publication_blocks(self):
        self.mutate_early(lambda r:r['spec'].update(private_reference_bytes_published=True),'private references')

    def test_hoof_limit_cannot_be_erased(self):
        self.mutate_early(lambda r:r['spec'].update(ride_limit='all four visible'),'hoof limit')

    def test_unknown_generation_time_honestly_allowed(self):
        gate.chronology({'status':'UNKNOWN_NOT_INFERRED','timestamp':None,'basis':'unknown in actual evidence','file_mtime_used':False},gate.stamp('2026-10-27T05:00:00Z'))

    def test_unknown_time_must_not_include_invented_timestamp(self):
        with self.assertRaisesRegex(ValueError,'falsely populated'):
            gate.chronology({'status':'UNKNOWN_NOT_INFERRED','timestamp':'2026-10-26T00:00:00Z','basis':'unknown','file_mtime_used':False},gate.stamp('2026-10-27T05:00:00Z'))

    def test_mtime_not_generation(self):
        with self.assertRaisesRegex(ValueError,'mtime'):
            gate.chronology({'status':'UNKNOWN_NOT_INFERRED','timestamp':None,'basis':'unknown','file_mtime_used':True},gate.stamp('2026-10-27T05:00:00Z'))

    def test_generation_after_normalization_blocks(self):
        with self.assertRaisesRegex(ValueError,'after normalization'):
            gate.chronology({'status':'DOCUMENTED','timestamp':'2026-10-28T00:00:00Z','basis':'synthetic','file_mtime_used':False},gate.stamp('2026-10-27T05:00:00Z'))

    def test_naive_timestamp_blocks(self):
        with self.assertRaisesRegex(ValueError,'timezone'):gate.stamp('2026-10-27T05:00:00')

    def test_traversal_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'unsafe path'):gate.local(Path(d),'../escape')

    def test_symlink_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'real').write_text('fixture');(p/'link').symlink_to('real')
            with self.assertRaisesRegex(ValueError,'symlink'):gate.local(p,'link')

    def test_changed_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'a').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'changed evidence'):
                gate.bound(p,{'path':'a','bytes':7,'sha256':'0'*64})


if __name__ == '__main__':
    unittest.main()
