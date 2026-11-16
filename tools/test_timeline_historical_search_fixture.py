"""Fixture isolation does not weaken either historical byte validator."""
import hashlib
from pathlib import Path
import unittest
from timeline_historical_search_fixture import historical_search_root
import timeline_51_search_successor as events
import timeline_search_index_successor as search
ROOT=Path(__file__).resolve().parents[1]
class HistoricalSearchFixtureTests(unittest.TestCase):
 def test_exact_chain_and_current_file_untouched(self):
  actual=(ROOT/'site-search-index.json').read_bytes()
  with historical_search_root(ROOT) as root:
   self.assertNotEqual(root,ROOT)
   raw=(root/'site-search-index.json').read_bytes()
   self.assertEqual(events.sha(raw),events.AFTER)
   previous=events.restore(raw,root)
   self.assertEqual(search.sha(search.restore(previous,root)),search.BEFORE)
  self.assertEqual((ROOT/'site-search-index.json').read_bytes(),actual)
 def test_corrupted_index_and_source_still_rejected(self):
  with historical_search_root(ROOT) as root:
   raw=(root/'site-search-index.json').read_bytes()
   with self.assertRaisesRegex(ValueError,'Unreviewed event search index'):
    events.restore(raw+b' ',root)
   source=next(iter(events.manifest(root)['source_sha256']))
   p=root/source;p.write_bytes(p.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'Changed event source'):
    events.restore(raw,root)
 def test_corrupted_manifest_still_rejected(self):
  with historical_search_root(ROOT) as root:
   raw=(root/'site-search-index.json').read_bytes()
   p=root/events.MANIFEST;p.write_bytes(p.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'Changed event search delta manifest'):
    events.restore(raw,root)
if __name__=='__main__':unittest.main()
