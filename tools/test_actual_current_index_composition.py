"""Actual current Timeline index semantics; not a historical producer claim.

The configured generator --check jobs separately compare complete outputs to
actual current source. Historical mapping and receipts remain unmodified.
"""
import json, tempfile, unittest
from pathlib import Path
import adams_integration_indices as current
from timeline_current_indices import validate_current
ROOT=Path(__file__).resolve().parents[1]
class ActualCurrentIndexComposition(unittest.TestCase):
 def test_current_semantics_and_historical_mapping(self):
  self.assertEqual(current.check_current()['status'],'CURRENT_TIMELINE_INDEX_SEMANTICS_PASS')
  self.assertEqual(set(current.mapping()['files']),set(current.AFTER))
 def test_missing_and_duplicated_index_destinations_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   for name in ('timeline.html','art-gallery.json','site-search-index.json'):(root/name).write_bytes((ROOT/name).read_bytes())
   path=root/'site-search-index.json';original=json.loads(path.read_bytes())
   for kind in ('missing','duplicate','stale_text'):
    value=json.loads(json.dumps(original))
    if kind=='missing':value['records']=[r for r in value['records'] if r['url']!='/timeline.html#adams-1881']
    elif kind=='duplicate':value['records'].append(value['records'][0])
    else:next(r for r in value['records'] if r['url']=='/timeline.html#choose-timeline')['text']='stale' 
    path.write_text(json.dumps(value))
    with self.assertRaises(AssertionError):validate_current(root)
if __name__=='__main__':unittest.main()
