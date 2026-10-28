"""Validate the current diagnostic's source bindings; this does not run a browser."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / 'tools/emma_story_journey_browser_qa.js'
OLD = ROOT / 'tools/emma_story_browser_qa.js'

class BrowserContractTests(unittest.TestCase):
    def test_historical_renderer_is_preserved_and_current_sources_are_exact(self):
        self.assertEqual(hashlib.sha256(OLD.read_bytes()).hexdigest(), '0132427d0edc952456515afc61eec5d355dded5f0bf95e6ae27563d5349b5947')
        source = NEW.read_text(encoding='utf8')
        match = re.search(r' const expectedSources=(\[.*?\]);\n', source)
        self.assertIsNotNone(match)
        rows = json.loads(match.group(1))
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r['path'] for r in rows}), 6)
        for row in rows:
            raw = (ROOT / row['path']).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']), row['path'])

    def test_hosted_guard_and_legacy_and_current_coverage_remain(self):
        source = NEW.read_text(encoding='utf8')
        self.assertIn("assert.equal(process.env.CI,'true','Hosted CI only')", source)
        self.assertIn('const ACTIVE_STORIES=STORIES.slice(1)', source)
        self.assertIn('legacy-query-fragments-and-no-js', source)
        self.assertIn('dialog-fullsize-close-focus', source)
        self.assertIn('skip-link-tab-enter-main', source)
        self.assertIn('scripture-expanded-artwork-actions-fullsize-close-continue', source)
        self.assertIn('assert.equal(footerEvidence.length,12);assert.equal(shots.length,69);assert.equal(results.length,62)', source)

if __name__ == '__main__':
    unittest.main()
