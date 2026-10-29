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

    def test_current_scripture_links_and_historical_renderer(self):
        from bs4 import BeautifulSoup
        historical = ROOT / 'tools/emma_hub_scripture_browser_qa.js'
        self.assertEqual(hashlib.sha256(historical.read_bytes()).hexdigest(), 'ba724ab720ec5d59cf2872ae3dc8fe4342c3118295e32446c5f95571931df798')
        page = BeautifulSoup((ROOT / 'history/emma-hale-smith.html').read_text(encoding='utf8'), 'html.parser')
        href = 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/25?lang=eng'
        for section in ('hymns-charge', 'hymns-lasted'):
            links = page.select(f'section#{section} p > a.fc-inline-scripture')
            self.assertEqual(len(links), 1)
            self.assertEqual(links[0].get('href'), href)
            self.assertEqual(links[0].get_text(strip=True), 'Doctrine and Covenants 25')
        raw = (ROOT / 'scripture-data/dc-testament/dc/25.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), '78e21fb0e7ff9291cf68af8c29631c9a6646a41ec03dc816a0abbbe0388b1d79')
        self.assertEqual(len(json.loads(raw)['verses']), 16)

if __name__ == '__main__':
    unittest.main()
