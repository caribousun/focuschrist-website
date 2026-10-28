#!/usr/bin/env python3
"""Run current protections in mixed suites; archive-only inverse tests are separate.

New tests remain current by default. The explicit historical-only list must
resolve exactly, or the runner fails rather than silently skipping coverage.
"""
import sys
import unittest

MODULES = ('test_continue_motion_binding', 'test_timeline_source_import')
HISTORICAL_ONLY = frozenset({
    'test_continue_motion_binding.MotionBindingTests.test_every_exact_predecessor',
    'test_continue_motion_binding.MotionBindingTests.test_exact_successors_and_unknown_input_rejected',
    'test_continue_motion_binding.MotionBindingTests.test_ask_html_citation_chain_composes',
    'test_continue_motion_binding.MotionBindingTests.test_entry_scroll_experience_chain',
    'test_continue_motion_binding.MotionBindingTests.test_site_common_decoupling_chain_composes',
    'test_continue_motion_binding.MotionBindingTests.test_pioneer_entry_scroll_chain_composes',
    'test_continue_motion_binding.MotionBindingTests.test_display_code_inverse_rejects_unrelated_bytes',
    'test_continue_motion_binding.MotionBindingTests.test_prior_bytes_not_changed',
    'test_timeline_source_import.GalleryBuilderEvidenceTests.test_gallery_builder_evidence_successor_is_exact_and_fail_closed',
    'test_timeline_source_import.TimelineImportTests.test_reviewed_code_evidence_restores_only_exact_hooks',
    'test_timeline_source_import.TimelineImportTests.test_reviewed_consumer_inverses_preserve_historical_pins',
    'test_timeline_source_import.GalleryBuilderEvidenceTests.test_historical_indices_restore_delivery_evidence_pins',
    'test_timeline_source_import.TimelineImportTests.test_exact_search_route_inverse_restores_frozen_predecessor',
})

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

def partition(tests):
    by_id = {test.id(): test for test in tests}
    if len(by_id) != len(tests):
        raise ValueError('Duplicate test identity')
    missing = HISTORICAL_ONLY - set(by_id)
    if missing:
        raise ValueError('Historical selection drift: ' + ', '.join(sorted(missing)))
    current = [test for test in tests if test.id() not in HISTORICAL_ONLY]
    if not current:
        raise ValueError('No current protections selected')
    return current, sorted(HISTORICAL_ONLY)

def main():
    tests = list(flatten(unittest.defaultTestLoader.loadTestsFromNames(MODULES)))
    current, historical = partition(tests)
    print('Current protections:', len(current), '; separately historical:', len(historical), flush=True)
    for name in historical:
        print('Historical only:', name, flush=True)
    if '--list' in sys.argv:
        for test in current:
            print('Current:', test.id())
        return 0
    result = unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(current))
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())
