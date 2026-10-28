"""Synthetic acceptance receipts plus actual local source bytes. Not an approval."""
import copy, hashlib, json, shutil, tempfile, unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import owner_journey_successor as s
import artwork_emma_journey_delivery as art
from artwork_emma_story_delivery import canonical
PROJECT=Path(__file__).resolve().parents[1]

def jsonbytes(o):return (json.dumps(o,sort_keys=True,indent=2)+'\n').encode()
class ReleaseReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)/'site'
  for name in (s.HUB,s.RETIRED,s.HYMNS,'sitemap.xml'):
   target=cls.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PROJECT/name,target)
  shutil.copytree(PROJECT/'assets/page-art/emma-journey',cls.root/'assets/page-art/emma-journey')
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def write(self,name,data):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
  if p.is_symlink():p.unlink()
  p.write_bytes(data)
  return {'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 def writej(self,name,obj):return self.write(name,jsonbytes(obj))
 def png(self,w,h):
  output=BytesIO();Image.new('RGB',(w,h),'white').save(output,format='PNG');return output.getvalue()
 def setup_records(self,mutate=None):
  evidence=self.write('docs/emma-journey-release/synthetic-evidence.txt',b'synthetic fixture only')
  binding={'source_manifest_sha256':s.MANIFEST_SHA256,'delivery_spec_sha256':canonical({'fixture':'synthetic'}),
   'page_sha256':s.sha((self.root/s.HUB).read_bytes()),'redirect_sha256':s.sha((self.root/s.RETIRED).read_bytes()),
   'hymns_sha256':s.sha((self.root/s.HYMNS).read_bytes()),'sitemap_sha256':s.sha((self.root/'sitemap.xml').read_bytes()),
   'rendered':{}}
  for name,w in [('desktop',1100),('phone',300)]:binding['rendered'][name]={'image':self.write('docs/emma-journey-release/'+name+'.png',self.png(w,300)),'viewport_width':w,'viewport_height':300}
  reviews=[{'reviewer':who,'actual_actor':who+' synthetic actor','stage':'final_source_and_render','verdict':'PASS','withdrawn':False,'binding_sha256':'',
   'checks':{k:'synthetic observation' for k in s.RELEASE_CHECKS},'evidence':[evidence],'reviewed_at':'2026-10-28T12:00:00+00:00'} for who in ('Fermi','Newton','Albert')]
  assembled=[{'reviewer':who,'actual_actor':who+' synthetic actor','stage':'assembled','verdict':'PASS','withdrawn':False} for who in ('Fermi','Newton','Albert')]
  owner={'kind':'direct_owner_acceptance','actor':'Wyatt','verdict':'ACCEPT','withdrawn':False,'subject_sha256':binding['delivery_spec_sha256'],'release_review_sha256':'','accepted_at':'2026-10-28T13:00:00+00:00','evidence':[evidence]}
  if mutate:mutate(binding,reviews,assembled,owner)
  for x in reviews:x['binding_sha256']=s._canonical(binding)
  review_pointers=[self.writej('docs/emma-journey-release/review-'+str(i)+'.json',x) for i,x in enumerate(reviews)]
  final={'schema':1,'status':'REVIEWED_EXACT_CURRENT','bindings':binding,'reviews':review_pointers}
  finalpointer=self.writej(s.FINAL_SOURCE_REVIEW_PATH,final);owner['release_review_sha256']=finalpointer['sha256']
  ownerpointer=self.writej(s.OWNER_ACCEPTANCE_PATH,owner)
  artpointers=[self.writej('docs/emma-journey-release/art-review-'+str(i)+'.json',x) for i,x in enumerate(assembled)]
  delivery={'spec':{'fixture':'synthetic'},'owner_acceptance':ownerpointer,'assembled_reviews':artpointers}
  self.writej('docs/emma-journey-artwork/delivery.json',delivery)
  return delivery,ownerpointer['sha256'],finalpointer['sha256']
 def gate(self,mutate=None):
  delivery,owner,final=self.setup_records(mutate)
  with patch.object(s,'OWNER_ACCEPTANCE_SHA256',owner),patch.object(s,'FINAL_SOURCE_REVIEW_SHA256',final),patch.object(art,'APPROVED_RECORD_SHA256',canonical(delivery)):
   return s.release_gate(self.root,delivery)
 def test_synthetic_complete_path_and_actual_current_bytes(self):
  self.assertIn('validated exact source',self.gate()['status'])
 def test_unset_real_pins_and_wrong_caller_fail_closed(self):
  with patch.object(s,'OWNER_ACCEPTANCE_SHA256',None),self.assertRaisesRegex(AssertionError,'PENDING'):s.release_gate()
  delivery,owner,final=self.setup_records()
  with patch.object(s,'OWNER_ACCEPTANCE_SHA256',owner),patch.object(s,'FINAL_SOURCE_REVIEW_SHA256',final),patch.object(art,'APPROVED_RECORD_SHA256',None),self.assertRaisesRegex(AssertionError,'unreviewed current artwork'):s.release_gate(self.root,delivery)
 def test_current_page_and_original_tamper_rejected(self):
  for name in (s.HUB,'assets/page-art/emma-journey/originals/emma-journey-03-source.png'):
   f=self.root/name;raw=f.read_bytes();f.write_bytes(raw+b' ')
   try:
    with self.subTest(name=name),self.assertRaises(AssertionError):self.gate()
   finally:f.write_bytes(raw)
 def test_bad_humans_or_acceptance_rejected_even_with_rebound_hashes(self):
  changes=[lambda b,r,a,o:r[1].update(reviewer='Fermi'),lambda b,r,a,o:r[1].update(actual_actor=r[0]['actual_actor']),
    lambda b,r,a,o:r[0].update(withdrawn=True),lambda b,r,a,o:r[0]['checks'].pop('phone_render'),
    lambda b,r,a,o:a[0].update(actual_actor='other'),lambda b,r,a,o:o.update(actor='not Wyatt'),
    lambda b,r,a,o:o.update(withdrawn=True),lambda b,r,a,o:o.update(accepted_at='2026-10-28T11:00:00Z'),
    lambda b,r,a,o:o.update(subject_sha256='0'*64)]
  for i,change in enumerate(changes):
   with self.subTest(i=i),self.assertRaises(AssertionError):self.gate(change)
 def test_wrong_binding_and_render_fail_closed_even_with_rebound_hashes(self):
  changes=[lambda b,r,a,o:b.update(page_sha256='0'*64),lambda b,r,a,o:b.update(delivery_spec_sha256='0'*64),
   lambda b,r,a,o:b['rendered'].pop('phone'),lambda b,r,a,o:b['rendered']['phone'].update(viewport_width=1100),
   lambda b,r,a,o:b['rendered']['desktop']['image'].update(sha256='0'*64)]
  for i,change in enumerate(changes):
   with self.subTest(i=i),self.assertRaises(AssertionError):self.gate(change)
 def test_pin_and_evidence_mutation_fail_closed(self):
  delivery,owner,final=self.setup_records()
  for name in (s.OWNER_ACCEPTANCE_PATH,s.FINAL_SOURCE_REVIEW_PATH,'docs/emma-journey-release/desktop.png'):
   path=self.root/name;raw=path.read_bytes();path.write_bytes(raw+b'changed')
   try:
    with patch.object(s,'OWNER_ACCEPTANCE_SHA256',owner),patch.object(s,'FINAL_SOURCE_REVIEW_SHA256',final),patch.object(art,'APPROVED_RECORD_SHA256',canonical(delivery)),self.subTest(name=name),self.assertRaises(AssertionError):s.release_gate(self.root,delivery)
   finally:path.write_bytes(raw)
 def test_source_evidence_path_must_not_escape(self):
  with self.assertRaisesRegex(AssertionError,'unsafe evidence path'):
   s._bound(self.root,{'path':'../outside','bytes':1,'sha256':'0'*64})
 def test_symlink_or_missing_evidence_rejected(self):
  def mutate(b,r,a,o):
   p=self.root/r[0]['evidence'][0]['path'];p.unlink();p.symlink_to(self.root/'docs/emma-journey-release/desktop.png')
  with self.assertRaisesRegex(AssertionError,'symlink'):self.gate(mutate)
if __name__=='__main__':unittest.main()
