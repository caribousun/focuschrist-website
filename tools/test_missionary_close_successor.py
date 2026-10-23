"""Synthetic binding negatives plus real-candidate round trip; no claim of actual finished review approval."""
import base64,copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import missionary_close_successor as g
REAL_BEFORE=g.BEFORE;REAL_AFTER=g.AFTER;REAL_SOURCE_SHA=g.SOURCE_SHA
class MissionaryCloseSuccessorTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.old=b'before page';self.new=b'before NEW page';self.proof=b'test-only Jeff proof'
  self.patch=patch.multiple(g,BEFORE=g.sha(self.old),AFTER=g.sha(self.new));self.patch.start();self.addCleanup(self.patch.stop)
  self.row={'schema':1,'page':g.PAGE,'before_sha256':g.sha(self.old),'after_sha256':g.sha(self.new),'spans':[{'start':7,'end':11,'previous_b64':'','current_b64':base64.b64encode(b'NEW ').decode()}]}
  self.record={'source_sha256':g.canonical(self.row),'page_sha256':g.sha(self.new),'status':'FINISHED','required_reviewers':['Jeff'],'reviews':[{'reviewer':'Jeff','decision':'CONCUR','finished_pixels':True,'finished_behavior':True,'page_sha256':g.sha(self.new),'evidence':{'path':'proof.txt','sha256':g.sha(self.proof)}}]}
  for name,raw in [(g.PAGE,self.new),('proof.txt',self.proof),(g.MANIFEST,json.dumps(self.row).encode()),(g.REVIEWS,json.dumps(self.record).encode())]:self.write(name,raw)
  self.pins=patch.multiple(g,SOURCE_SHA=g.canonical(self.row),APPROVED_REVIEWS=g.canonical(self.record));self.pins.start();self.addCleanup(self.pins.stop)
 def write(self,name,raw):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 def test_exact_round_trip_and_gate(self):
  self.assertEqual(g.restore(g.PAGE,self.new,self.root),self.old);self.assertEqual(g.advance(g.PAGE,self.old,self.root),self.new);self.assertEqual(g.check(self.root)['status'],'MISSIONARY_CLOSE_SUCCESSOR_EVIDENCE_PASS')
 def test_real_candidate_exact_round_trip(self):
  raw=(g.ROOT/g.PAGE).read_bytes()
  self.assertEqual(g.sha(raw),'e5696e60b60faef5f456647ff2a153b939871acb895a6671d3d95a718d2ad55a')
  with patch.multiple(g,BEFORE=REAL_BEFORE,AFTER=REAL_AFTER,SOURCE_SHA=REAL_SOURCE_SHA):
   old=g.restore(g.PAGE,raw,g.ROOT)
   self.assertEqual(g.sha(old),'028f7bc23aa9c7a21e8cc2def40c429ba5ea628880347653292974e8fe7caa31')
   self.assertEqual(g.advance(g.PAGE,old,g.ROOT),raw)
 def test_all_historical_map_files_still_round_trip(self):
  import continue_motion_binding as gate
  with patch.multiple(g,BEFORE=REAL_BEFORE,AFTER=REAL_AFTER,SOURCE_SHA=REAL_SOURCE_SHA):
   for name,row in gate.mapping()['files'].items():
    current=(gate.ROOT/name).read_bytes()
    self.assertEqual(gate.sha(gate.restore(name,current)),row['before_sha256'],name)
 def test_wrong_route_not_normalized(self):
  self.assertEqual(g.restore('unknown.html',self.new,self.root),self.new);self.assertEqual(g.advance('unknown.html',self.old,self.root),self.old)
  row=copy.deepcopy(self.row);row['page']='other.html';self.write(g.MANIFEST,json.dumps(row).encode())
  with patch.object(g,'SOURCE_SHA',g.canonical(row)):
   with self.assertRaisesRegex(ValueError,'route'):g.mapping(self.root)
 def test_unrelated_one_byte_page_change_not_normalized(self):
  for raw in [self.new+b' ',self.new.replace(b'page',b'paqe')]:
   self.assertNotEqual(raw,self.new);self.assertEqual(g.restore(g.PAGE,raw,self.root),raw);self.write(g.PAGE,raw)
   with self.assertRaisesRegex(ValueError,'Changed successor page'):g.check(self.root)
  self.write(g.PAGE,self.new)
 def test_removed_duplicate_altered_close_insertion(self):
  removed=self.old
  self.assertEqual(g.restore(g.PAGE,removed,self.root),removed);self.write(g.PAGE,removed)
  with self.assertRaisesRegex(ValueError,'Changed successor page'):g.check(self.root)
  duplicate=self.new[:7]+b'NEW '+self.new[7:]
  self.assertEqual(g.restore(g.PAGE,duplicate,self.root),duplicate);self.write(g.PAGE,duplicate)
  with self.assertRaisesRegex(ValueError,'Changed successor page'):g.check(self.root)
  altered=self.new.replace(b'NEW',b'NE X')
  self.assertEqual(g.restore(g.PAGE,altered,self.root),altered);self.write(g.PAGE,altered)
  with self.assertRaisesRegex(ValueError,'Changed successor page'):g.check(self.root)
  self.write(g.PAGE,self.new)
 def test_changed_span_manifest_and_pin_rejected(self):
  raw=(self.root/g.MANIFEST).read_bytes()
  changed=copy.deepcopy(self.row);changed['spans'][0]['start']=1;self.write(g.MANIFEST,json.dumps(changed).encode())
  with self.assertRaisesRegex(ValueError,'Changed successor manifest'):g.mapping(self.root)
  self.write(g.MANIFEST,raw)
  with patch.object(g,'SOURCE_SHA','0'*64):
   with self.assertRaisesRegex(ValueError,'Changed successor manifest'):g.mapping(self.root)
  for field,value in [('start',8),('end',12),('current_b64',base64.b64encode(b'NEWX').decode()),('previous_b64',base64.b64encode(b'x').decode())]:
   row=copy.deepcopy(self.row);row['spans'][0][field]=value;self.write(g.MANIFEST,json.dumps(row).encode())
   with patch.object(g,'SOURCE_SHA',g.canonical(row)):
    with self.assertRaises(ValueError):g.mapping(self.root);g.restore(g.PAGE,self.new,self.root)
  self.write(g.MANIFEST,raw)
 def test_missing_manifest_page_and_reviews_rejected(self):
  for name in [g.MANIFEST,g.PAGE,g.REVIEWS]:
   p=self.root/name;raw=p.read_bytes();p.unlink()
   with self.assertRaises((ValueError,OSError)):g.check(self.root)
   self.write(name,raw)
 def test_pending_and_absent_review_blocks_real_gate(self):
  with patch.object(g,'APPROVED_REVIEWS',None):
   with self.assertRaisesRegex(ValueError,'PENDING'):g.check(self.root)
 def test_real_candidate_reviews_stay_pending(self):
  record=json.loads((g.ROOT/g.REVIEWS).read_text(encoding='utf-8'))
  self.assertEqual(record.get('status'),'PENDING');self.assertEqual(record.get('required_reviewers'),['Jeff']);self.assertEqual(record.get('reviews'),[])
  source=(g.ROOT/'tools/missionary_close_successor.py').read_text(encoding='utf-8')
  self.assertIn('APPROVED_REVIEWS=None',source)
  manifest=json.loads((g.ROOT/g.MANIFEST).read_text(encoding='utf-8'))
  self.assertEqual(record.get('source_sha256'),g.canonical(manifest));self.assertIn(record.get('source_sha256'),source)
 def test_incorrect_reviewer_evidence_rejected_even_if_resealed(self):
  for edit in ['pending','unfinished','wrongreviewer','extra','wrongpage','wronghash','badhash']:
   row=copy.deepcopy(self.record)
   if edit=='pending':row['reviews'][0]['decision']='PENDING'
   if edit=='unfinished':row['reviews'][0]['finished_behavior']=False
   if edit=='wrongreviewer':row['reviews'][0]['reviewer']='Albert'
   if edit=='extra':row['reviews'].append(copy.deepcopy(row['reviews'][0]))
   if edit=='wrongpage':row['reviews'][0]['page_sha256']='0'*64
   if edit=='wronghash':row['page_sha256']='0'*64
   if edit=='badhash':row['reviews'][0]['evidence']['sha256']='0'*64
   self.write(g.REVIEWS,json.dumps(row).encode())
   with patch.object(g,'APPROVED_REVIEWS',g.canonical(row)):
    with self.assertRaises(ValueError):g.check(self.root)
  self.write(g.REVIEWS,json.dumps(self.record).encode())
 def test_wrong_manifest_hashes_rejected_even_if_resealed(self):
  for field in ['before_sha256','after_sha256']:
   row=copy.deepcopy(self.row);row[field]='0'*64;self.write(g.MANIFEST,json.dumps(row).encode())
   with patch.object(g,'SOURCE_SHA',g.canonical(row)):
    with self.assertRaises(ValueError):g.mapping(self.root)
  self.write(g.MANIFEST,json.dumps(self.row).encode())
 def test_evidence_path_escaping_repository_rejected(self):
  row=copy.deepcopy(self.record);row['reviews'][0]['evidence']['path']='../outside.txt';self.write(g.REVIEWS,json.dumps(row).encode())
  with patch.object(g,'APPROVED_REVIEWS',g.canonical(row)):
   with self.assertRaisesRegex(ValueError,'outside'):g.check(self.root)
  row=copy.deepcopy(self.record);row['reviews'][0]['evidence']['path']='/tmp/outside.txt';self.write(g.REVIEWS,json.dumps(row).encode())
  with patch.object(g,'APPROVED_REVIEWS',g.canonical(row)):
   with self.assertRaisesRegex(ValueError,'outside'):g.check(self.root)
if __name__=='__main__':unittest.main()
