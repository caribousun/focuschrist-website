"""Synthetic binding negatives; no claim of actual finished product approval."""
import base64,copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import world_companion_successor as g
class WorldSuccessorTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.old=b'before page';self.new=b'before NEW page';self.asset=b'map';self.proof=b'test-only proof'
  self.patch=patch.multiple(g,BEFORE=g.sha(self.old),ASSET_SHA=g.sha(self.asset));self.patch.start();self.addCleanup(self.patch.stop)
  self.row={'schema':1,'page':g.PAGE,'before_sha256':g.BEFORE,'after_sha256':g.sha(self.new),'asset':g.ASSET,'asset_sha256':g.ASSET_SHA,'spans':[{'start':7,'end':11,'previous_b64':'','current_b64':base64.b64encode(b'NEW ').decode()}]}
  self.record={'source_sha256':g.canonical(self.row),'page_sha256':g.sha(self.new),'reviews':[{'reviewer':who,'decision':'CONCUR','finished_pixels':True,'finished_behavior':True,'page_sha256':g.sha(self.new),'evidence':{'path':'proof.txt','sha256':g.sha(self.proof)}} for who in ['Albert','Fermi','Newton']]}
  for name,raw in [(g.PAGE,self.new),(g.ASSET,self.asset),('proof.txt',self.proof),(g.MANIFEST,json.dumps(self.row).encode()),(g.REVIEWS,json.dumps(self.record).encode())]:self.write(name,raw)
  self.pins=patch.multiple(g,SOURCE_SHA=g.canonical(self.row),APPROVED_REVIEWS=g.canonical(self.record));self.pins.start();self.addCleanup(self.pins.stop)
 def write(self,name,raw):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 def test_exact_round_trip_and_gate(self):
  self.assertEqual(g.restore(g.PAGE,self.new,self.root),self.old);self.assertEqual(g.advance(g.PAGE,self.old,self.root),self.new);self.assertEqual(g.check(self.root)['status'],'WORLD_SUCCESSOR_EVIDENCE_PASS')
 def test_unknown_mixed_and_duplicate_bytes_not_normalized(self):
  for raw in [self.new+b' ',self.new.replace(b'NEW',b'OLD'),self.new.replace(b'NEW ',b'NEW NEW ')]:
   self.assertEqual(g.restore(g.PAGE,raw,self.root),raw);self.write(g.PAGE,raw)
   with self.assertRaises(ValueError):g.check(self.root)
  self.assertEqual(g.restore('unknown.html',self.new,self.root),self.new);self.assertEqual(g.advance(g.PAGE,self.old+b' ',self.root),self.old+b' ')
 def test_missing_files_and_changed_asset_evidence(self):
  for name in [g.MANIFEST,g.REVIEWS,g.ASSET,'proof.txt']:
   p=self.root/name;raw=p.read_bytes();p.unlink()
   with self.assertRaises((ValueError,OSError)):g.check(self.root)
   p.write_bytes(raw+b'!')
   with self.assertRaises((ValueError,OSError,json.JSONDecodeError)):g.check(self.root)
   p.write_bytes(raw)
 def test_pending_review_blocks(self):
  with patch.object(g,'APPROVED_REVIEWS',None):
   with self.assertRaisesRegex(ValueError,'PENDING'):g.check(self.root)
  with patch.object(g,'SOURCE_SHA',None):
   with self.assertRaisesRegex(ValueError,'PENDING'):g.check(self.root)
 def test_wrong_asset_and_duplicate_spans_even_if_resealed(self):
  for field,value in [('asset','wrong.png'),('before_sha256','0'*64),('spans',self.row['spans']*2)]:
   row=copy.deepcopy(self.row);row[field]=value;self.write(g.MANIFEST,json.dumps(row).encode())
   with patch.object(g,'SOURCE_SHA',g.canonical(row)):
    with self.assertRaises(ValueError):g.mapping(self.root)
 def test_duplicate_unfinished_wrong_bound_review_even_if_resealed(self):
  for edit in ['duplicate','unfinished','wrongpage','outside']:
   row=copy.deepcopy(self.record)
   if edit=='duplicate':row['reviews'][2]=row['reviews'][0]
   if edit=='unfinished':row['reviews'][0]['finished_pixels']=False
   if edit=='wrongpage':row['reviews'][0]['page_sha256']='0'*64
   if edit=='outside':row['reviews'][0]['evidence']['path']='../outside'
   self.write(g.REVIEWS,json.dumps(row).encode())
   with patch.object(g,'APPROVED_REVIEWS',g.canonical(row)):
    with self.assertRaises(ValueError):g.check(self.root)
if __name__=='__main__':unittest.main()
