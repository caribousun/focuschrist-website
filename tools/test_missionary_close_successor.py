"""Synthetic binding negatives plus real-candidate round trip; A002 split scopes, no claim of approval beyond recorded evidence."""
import base64,copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import missionary_close_successor as g
REAL_BEFORE=g.BEFORE;REAL_AFTER=g.AFTER;REAL_SOURCE_SHA=g.SOURCE_SHA
class MissionaryCloseSuccessorTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.old=b'before page';self.new=b'before NEW page';self.proof=b'test-only Jeff proof';self.script=b'test-only details script';self.capd=b'test-only desktop capture';self.capp=b'test-only phone capture';self.revproof=b'test-only rendered review proof'
  self.patch=patch.multiple(g,BEFORE=g.sha(self.old),AFTER=g.sha(self.new));self.patch.start();self.addCleanup(self.patch.stop)
  self.row={'schema':1,'page':g.PAGE,'before_sha256':g.sha(self.old),'after_sha256':g.sha(self.new),'spans':[{'start':7,'end':11,'previous_b64':'','current_b64':base64.b64encode(b'NEW ').decode()}]}
  self.record={'source_sha256':g.canonical(self.row),'page_sha256':g.sha(self.new),'status':'FINISHED','required_reviewers':['Jeff'],
   'registration_review':{'reviewer':'Jeff','review_id':'J-TEST-001','scope':'registration-source','decision':'CONCUR','finished_pixels':False,'finished_behavior':True,'page_sha256':g.sha(self.new),'evidence':{'path':'proof.txt','sha256':g.sha(self.proof)}},
   'rendered_evidence':{'status':'COLLECTED','collected_by':'Merlin','page_sha256':g.sha(self.new),'served_git_head':'a'*40,'details_js_sha256':g.sha(self.script),'captures':[{'path':'cap-desktop.txt','sha256':g.sha(self.capd),'viewport':'desktop'},{'path':'cap-phone.txt','sha256':g.sha(self.capp),'viewport':'phone'}]},
   'rendered_review':{'status':'FINISHED','reviewer':'Jeff','scope':'rendered','decision':'CONCUR','finished_pixels':True,'finished_behavior':True,'page_sha256':g.sha(self.new),'capture_sha256':[g.sha(self.capd),g.sha(self.capp)],'evidence':{'path':'revproof.txt','sha256':g.sha(self.revproof)}}}
  for name,raw in [(g.PAGE,self.new),('proof.txt',self.proof),('missionary-details.js',self.script),('cap-desktop.txt',self.capd),('cap-phone.txt',self.capp),('revproof.txt',self.revproof),(g.MANIFEST,json.dumps(self.row).encode()),(g.REVIEWS,json.dumps(self.record).encode())]:self.write(name,raw)
  self.pins=patch.multiple(g,SOURCE_SHA=g.canonical(self.row),APPROVED_REVIEWS=g.canonical(self.record));self.pins.start();self.addCleanup(self.pins.stop)
 def write(self,name,raw):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 def resealed(self,record):
  self.write(g.REVIEWS,json.dumps(record).encode());return patch.object(g,'APPROVED_REVIEWS',g.canonical(record))
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
 def test_pending_pin_blocks_even_when_all_scopes_complete(self):
  with patch.object(g,'APPROVED_REVIEWS',None):
   with self.assertRaisesRegex(ValueError,'PENDING'):g.check(self.root)
 def test_jeff_record_accepted_but_gate_blocks_only_on_rendered(self):
  for slot in ['rendered_evidence','rendered_review']:
   record=copy.deepcopy(self.record)
   if slot=='rendered_evidence':record['rendered_evidence']={'status':'PENDING','collected_by':None,'captures':[]}
   else:record['rendered_review']={'status':'PENDING','reviewer':None,'decision':None,'finished_pixels':False,'finished_behavior':False}
   with self.resealed(record):
    with self.assertRaisesRegex(ValueError,'rendered review MISSING'):g.check(self.root)
  record=copy.deepcopy(self.record);del record['rendered_review']
  with self.resealed(record):
   with self.assertRaisesRegex(ValueError,'rendered review MISSING'):g.check(self.root)
 def test_real_candidate_record_truthful_and_completed(self):
  record=json.loads((g.ROOT/g.REVIEWS).read_text(encoding='utf-8'))
  self.assertEqual(record.get('status'),'COMPLETE');self.assertEqual(record.get('required_reviewers'),['Jeff'])
  reg=record.get('registration_review')
  self.assertEqual(reg.get('reviewer'),'Jeff');self.assertEqual(reg.get('review_id'),'J-2026-10-23-007');self.assertEqual(reg.get('scope'),'registration-source');self.assertEqual(reg.get('decision'),'CONCUR')
  self.assertIs(reg.get('finished_pixels'),False);self.assertIs(reg.get('finished_behavior'),True)
  self.assertEqual(reg.get('page_sha256'),REAL_AFTER)
  item=reg['evidence'];self.assertEqual(g.sha((g.ROOT/item['path']).read_bytes()),item['sha256'])
  ev=record['rendered_evidence'];self.assertEqual(ev.get('status'),'COLLECTED');self.assertEqual(ev.get('collected_by'),'Merlin')
  self.assertEqual(len(ev.get('captures')),5)
  for cap in ev['captures']:self.assertEqual(g.sha((g.ROOT/cap['path']).read_bytes()),cap['sha256'])
  rv=record['rendered_review'];self.assertEqual(rv.get('status'),'FINISHED');self.assertEqual(rv.get('reviewer'),'Jeff')
  self.assertEqual(rv.get('review_id'),'J-2026-10-23-009');self.assertEqual(rv.get('scope'),'rendered');self.assertEqual(rv.get('decision'),'CONCUR')
  self.assertIs(rv.get('finished_pixels'),True);self.assertIs(rv.get('finished_behavior'),True)
  self.assertEqual(rv.get('capture_sha256'),[cap['sha256'] for cap in ev['captures']])
  item=rv['evidence'];self.assertEqual(g.sha((g.ROOT/item['path']).read_bytes()),item['sha256'])
  source=(g.ROOT/'tools/missionary_close_successor.py').read_text(encoding='utf-8')
  self.assertIn("APPROVED_REVIEWS='"+g.canonical(record)+"'",source)
  self.assertIsNotNone(g.APPROVED_REVIEWS)
  manifest=json.loads((g.ROOT/g.MANIFEST).read_text(encoding='utf-8'))
  self.assertEqual(record.get('source_sha256'),g.canonical(manifest));self.assertIn(record.get('source_sha256'),source)
  with patch.multiple(g,BEFORE=REAL_BEFORE,AFTER=REAL_AFTER,SOURCE_SHA=REAL_SOURCE_SHA,APPROVED_REVIEWS=None):
   with self.assertRaisesRegex(ValueError,'finished review PENDING'):g.check(g.ROOT)
 def test_tampered_jeff_record_rejected_even_if_resealed(self):
  for edit in ['pending','fabricatedpixels','unfinished','wrongreviewer','wrongscope','wrongpage','wronghash','badhash']:
   row=copy.deepcopy(self.record)
   if edit=='pending':row['registration_review']['decision']='PENDING'
   if edit=='fabricatedpixels':row['registration_review']['finished_pixels']=True
   if edit=='unfinished':row['registration_review']['finished_behavior']=False
   if edit=='wrongreviewer':row['registration_review']['reviewer']='Albert'
   if edit=='wrongscope':row['registration_review']['scope']='rendered'
   if edit=='wrongpage':row['registration_review']['page_sha256']='0'*64
   if edit=='wronghash':row['page_sha256']='0'*64
   if edit=='badhash':row['registration_review']['evidence']['sha256']='0'*64
   with self.resealed(row):
    with self.assertRaises(ValueError):g.check(self.root)
  self.write(g.REVIEWS,json.dumps(self.record).encode())
 def test_fabricated_or_wrong_rendered_review_rejected(self):
  row=copy.deepcopy(self.record);row['rendered_evidence']={'status':'PENDING','collected_by':None,'captures':[]}
  with self.resealed(row):
   with self.assertRaisesRegex(ValueError,'rendered review MISSING'):g.check(self.root)
  for edit in ['wrongactor','unfinished','wrongscope','unbound','badhash']:
   row=copy.deepcopy(self.record)
   if edit=='wrongactor':row['rendered_review']['reviewer']='Merlin'
   if edit=='unfinished':row['rendered_review']['decision']='PENDING'
   if edit=='wrongscope':row['rendered_review']['scope']='registration-source'
   if edit=='unbound':row['rendered_review']['capture_sha256']=['0'*64,'0'*64]
   if edit=='badhash':row['rendered_review']['evidence']['sha256']='0'*64
   with self.resealed(row):
    with self.assertRaises(ValueError):g.check(self.root)
  row=copy.deepcopy(self.record);row['rendered_evidence']['collected_by']='Jeff'
  with self.resealed(row):
   with self.assertRaises(ValueError):g.check(self.root)
  row=copy.deepcopy(self.record);del row['rendered_evidence']['captures'][1]
  with self.resealed(row):
   with self.assertRaises(ValueError):g.check(self.root)
  self.write(g.REVIEWS,json.dumps(self.record).encode())
 def test_tampered_rendered_evidence_file_rejected(self):
  raw=(self.root/'cap-desktop.txt').read_bytes();self.write('cap-desktop.txt',raw+b'x')
  with self.assertRaisesRegex(ValueError,'Changed successor rendered evidence'):g.check(self.root)
  self.write('cap-desktop.txt',raw)
  self.assertEqual(g.check(self.root)['status'],'MISSIONARY_CLOSE_SUCCESSOR_EVIDENCE_PASS')
 def test_wrong_manifest_hashes_rejected_even_if_resealed(self):
  for field in ['before_sha256','after_sha256']:
   row=copy.deepcopy(self.row);row[field]='0'*64;self.write(g.MANIFEST,json.dumps(row).encode())
   with patch.object(g,'SOURCE_SHA',g.canonical(row)):
    with self.assertRaises(ValueError):g.mapping(self.root)
  self.write(g.MANIFEST,json.dumps(self.row).encode())
 def test_evidence_path_escaping_repository_rejected(self):
  row=copy.deepcopy(self.record);row['registration_review']['evidence']['path']='../outside.txt'
  with self.resealed(row):
   with self.assertRaisesRegex(ValueError,'outside'):g.check(self.root)
  row=copy.deepcopy(self.record);row['rendered_evidence']['captures'][0]['path']='/tmp/outside.txt'
  with self.resealed(row):
   with self.assertRaisesRegex(ValueError,'outside'):g.check(self.root)
  self.write(g.REVIEWS,json.dumps(self.record).encode())
if __name__=='__main__':unittest.main()
