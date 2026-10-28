"""Guard the archive/current split; failures must not hide live protections."""
import unittest
import run_current_mixed_regressions as runner

class Dummy:
    def __init__(self, name): self.name = name
    def id(self): return self.name

class SelectionTests(unittest.TestCase):
    def test_actual_discovery_keeps_current_protections(self):
        all_tests=list(runner.flatten(unittest.defaultTestLoader.loadTestsFromNames(runner.MODULES)))
        current,historical=runner.partition(all_tests)
        ids={test.id() for test in current}
        self.assertEqual(set(historical),runner.HISTORICAL_ONLY)
        for required in (
            'test_continue_motion_binding.MotionBindingTests.test_pending_review_cannot_pass',
            'test_continue_motion_binding.MotionBindingTests.test_mapping_tamper_rejected',
            'test_continue_motion_binding.MotionBindingTests.test_prospective_override_uses_exact_same_historical_chain',
            'test_continue_motion_binding.MotionBindingTests.test_all_six_existing_delivery_context_records',
            'test_continue_motion_binding.MotionBindingTests.test_display_review_evidence_including_page_snapshots',
            'test_timeline_source_import.TimelineImportTests.test_forged_finished_review_rejected',
            'test_timeline_source_import.TimelineImportTests.test_missing_license_rejected',
            'test_timeline_source_import.TimelineImportTests.test_rejected_source_rejected',
            'test_timeline_source_import.TimelineImportTests.test_wrong_dimensions_rejected',
            'test_timeline_source_import.TimelineImportTests.test_wrong_owner_page_rejected',
        ): self.assertIn(required,ids)
        self.assertFalse(ids.intersection(runner.HISTORICAL_ONLY))
        self.assertEqual(len(ids)+len(historical),len(all_tests))
    def test_new_test_is_current_by_default(self):
        tests=[Dummy(n) for n in runner.HISTORICAL_ONLY]+[Dummy('future.NewTest.test_new')]
        current,_=runner.partition(tests)
        self.assertEqual([x.id() for x in current],['future.NewTest.test_new'])
    def test_missing_or_duplicate_name_fails_closed(self):
        tests=[Dummy(n) for n in runner.HISTORICAL_ONLY]+[Dummy('future.NewTest.test_new')]
        with self.assertRaisesRegex(ValueError,'Historical selection drift'):runner.partition(tests[1:])
        with self.assertRaisesRegex(ValueError,'Duplicate test identity'):runner.partition(tests+[tests[-1]])

if __name__=='__main__':unittest.main()
