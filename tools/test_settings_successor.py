"""Exact successor tests; synthetic reviews stay isolated in temporary fixtures."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import settings_successor as g
BASE=Path(__file__).resolve().parent
class SettingsTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.row=g.mapping()
  for name in g.BEFORE:
   raw=(g.ROOT/name).read_bytes()
   from timeline_51_source_successor import project_exact
   raw=project_exact(name,raw,g.ROOT)
   if name=='timelines/world-and-scripture-timeline.html':
    from timeline_world_controls_successor import restore
    raw=restore(raw,g.ROOT)
   self.write(name,g.advance(name,raw))
  self.write(g.MANIFEST,json.dumps(self.row).encode());self.write('proof.txt',b'synthetic unit-test evidence')
  hashes={n:r['after_sha256'] for n,r in self.row['files'].items()}
  self.reviews={'source_sha256':g.SOURCE_SHA,'page_hashes':hashes,'reviews':[{'reviewer':who,'decision':'CONCUR','finished_pixels':True,'finished_behavior':True,'page_hashes':hashes,'evidence':{'path':'proof.txt','sha256':g.sha(b'synthetic unit-test evidence')}} for who in ['Albert','Fermi','Newton']]}
  self.write(g.REVIEWS,json.dumps(self.reviews).encode())
 def write(self,name,raw):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 def test_actual_candidate_exact_roundtrip(self):
  for name in g.BEFORE:
   raw=(self.root/name).read_bytes();old=g.restore(name,raw,self.root)
   self.assertEqual(g.sha(old),g.BEFORE[name]);self.assertEqual(g.advance(name,old,self.root),raw)
 def test_wrongbyte_route_and_changed_data_not_normalized(self):
  for name in g.BEFORE:
   raw=(self.root/name).read_bytes()
   changes=[raw+b' ',raw.replace(b'<title>',b'<title>changed',1)]
   if b'const DATA = ' in raw:changes.append(raw.replace(b'const DATA = ',b'const DATA = ["changed-data"]; const OLD_DATA = ',1))
   for changed in changes:
    self.assertNotEqual(changed,raw);self.assertEqual(g.restore(name,changed,self.root),changed)
    self.write(name,changed)
    with self.assertRaisesRegex(ValueError,'Changed settings page'):g.check(self.root)
   self.write(name,raw);self.assertEqual(g.restore('unknown/'+name,raw,self.root),raw)
 def test_missing_approval_pin_is_pending(self):
  with patch.object(g,'APPROVED_REVIEWS',None):
   with self.assertRaisesRegex(ValueError,'PENDING'):g.check(self.root)
 def test_missing_review_file_is_rejected(self):
  (self.root/g.REVIEWS).unlink()
  with patch.object(g,'APPROVED_REVIEWS',g.canonical(self.reviews)):
   with self.assertRaisesRegex(ValueError,'Missing/outside settings evidence'):g.check(self.root)
 def test_synthetic_bound_positive_and_changed_review_evidence(self):
  with patch.object(g,'APPROVED_REVIEWS',g.canonical(self.reviews)):
   self.assertEqual(g.check(self.root)['status'],'SETTINGS_SUCCESSOR_EVIDENCE_PASS')
   self.write('proof.txt',b'changed')
   with self.assertRaisesRegex(ValueError,'evidence'):g.check(self.root)
 def test_missing_changed_manifest(self):
  p=self.root/g.MANIFEST;p.unlink()
  with self.assertRaises(ValueError):g.mapping(self.root)
  row=copy.deepcopy(self.row);row['schema']=2;self.write(g.MANIFEST,json.dumps(row).encode())
  with self.assertRaises(ValueError):g.mapping(self.root)
 def test_duplicate_review_wrong_page_and_span_rejected(self):
  row=copy.deepcopy(self.reviews);row['reviews'][2]=row['reviews'][0];self.write(g.REVIEWS,json.dumps(row).encode())
  with patch.object(g,'APPROVED_REVIEWS',g.canonical(row)):
   with self.assertRaisesRegex(ValueError,'duplicate'):g.check(self.root)
  row=copy.deepcopy(self.row);name=next(iter(row['files']));row['files'][name]['spans']*=2;self.write(g.MANIFEST,json.dumps(row).encode())
  with patch.object(g,'SOURCE_SHA',g.canonical(row)):
   with self.assertRaisesRegex(ValueError,'duplicate'):g.mapping(self.root)
if __name__=='__main__':unittest.main()
