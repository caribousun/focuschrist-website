"""Synthetic negatives for current review binding; no human approval is implied."""
import contextlib
import hashlib
import io
import unittest
from unittest.mock import patch

import continue_motion_binding as motion
import static_content_audit as audit
import timeline_nazareth_successor as nazareth
import timeline_world_controls_successor as world


class CurrentTimelineReviewGateTests(unittest.TestCase):
    def test_current_sources_need_exact_review_binding(self):
        for name, expected in ((world.PAGE, world.AFTER),
                               ('answers/jesus-christ-latter-day-saint-beliefs.html', nazareth.AFTER)):
            path = audit.ROOT / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
            old = b'historical source'
            record = {'path': name, 'status': 'non-source-dependent', 'reviewed_on': 'synthetic',
                      'review_standard': 'synthetic test only', 'published_text_sha256': 'test',
                      'reviewed_inline_script_sha256': 'test', 'reviewed_source_sha256': hashlib.sha256(old).hexdigest()}
            with patch.object(audit, 'load_ledger', return_value={'documents': [record]}), \
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


if __name__ == '__main__':
    unittest.main()
