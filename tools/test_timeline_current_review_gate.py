"""Synthetic negatives for current review binding; no human approval is implied."""
import contextlib
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import continue_motion_binding as motion
import static_content_audit as audit
import timeline_nazareth_successor as nazareth
import timeline_world_controls_successor as world
import timeline_world_mobile_successor as mobile


class CurrentTimelineReviewGateTests(unittest.TestCase):
    def test_current_sources_need_exact_review_binding(self):
        for name, expected in ((world.PAGE, world.AFTER),
                               ('answers/jesus-christ-latter-day-saint-beliefs.html', nazareth.AFTER)):
            actual = (audit.ROOT / name).read_bytes()
            historical = mobile.restore(actual) if name == world.PAGE else actual
            self.assertEqual(hashlib.sha256(historical).hexdigest(), expected)
            temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
            root = Path(temporary.name); path = root / name; path.parent.mkdir(parents=True); path.write_bytes(historical)
            old = b'historical source'
            record = {'path': name, 'status': 'non-source-dependent', 'reviewed_on': 'synthetic',
                      'review_standard': 'synthetic test only', 'published_text_sha256': 'test',
                      'reviewed_inline_script_sha256': 'test', 'reviewed_source_sha256': hashlib.sha256(old).hexdigest()}
            with patch.object(audit, 'ROOT', root), \
                 patch.object(audit, 'load_ledger', return_value={'documents': [record]}), \
                 patch.object(audit, 'html_files', return_value=[path]), \
                 patch.object(audit, 'published_text', return_value='fixture'), \
                 patch.object(audit, 'content_hash', return_value='test'), \
                 patch.object(audit, 'inline_script_hash', return_value='test'), \
                 patch.object(motion, 'restore', return_value=old):
                for value in (None, '0'*64, expected):
                    if value is None: record.pop('reviewed_current_timeline_sha256', None)
                    else: record['reviewed_current_timeline_sha256'] = value
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output): result = audit.validate()
                    self.assertEqual(result, 0 if value == expected else 1, output.getvalue())
                    if value != expected: self.assertIn('review pending', output.getvalue())

    def test_current_mobile_candidate_requires_separate_review(self):
        page = audit.ROOT / world.PAGE
        record = next(r for r in audit.load_ledger()['documents'] if r['path'] == world.PAGE)
        with patch.object(audit, 'load_ledger', return_value={'documents': [record]}), \
             patch.object(audit, 'html_files', return_value=[page]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): result = audit.validate()
        self.assertEqual(result, 1)
        self.assertIn('current mobile controls independent review pending', output.getvalue())


if __name__ == '__main__':
    unittest.main()
