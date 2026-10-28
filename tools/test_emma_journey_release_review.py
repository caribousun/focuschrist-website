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
SYNTHETIC_QUESTION='Synthetic conditional authorization question for test fixtures only.'
SYNTHETIC_QUESTION_SHA256=hashlib.sha256(SYNTHETIC_QUESTION.encode()).hexdigest()

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
 def conditional(self,binding,owner):
  # Synthetic values only; these are not actual authorization evidence.
  proof=self.write('docs/emma-journey-release/synthetic-conditional-evidence.txt',b'synthetic only')
  question={'actor':'Albert','message_id_sha256':s.sha(b'fake question id'),'sent_at_sha256':s.sha(b'fake question time'),'text_sha256':SYNTHETIC_QUESTION_SHA256}
  answer={'actor':'Wyatt','message_id_sha256':s.sha(b'fake answer id'),'sent_at_sha256':s.sha(b'fake answer time'),'text_sha256':s.sha(b'fake answer')}
  source={'schema':1,'kind':'privately_verified_conditional_authorization','question':question,'answer':answer,
   'verification':{'status':'VERIFIED','actual_actor':'synthetic verifier','verified_at':'2026-10-28T10:02:00Z','private_readback_sha256':'a'*64}}
  sourceptr=self.writej('docs/emma-journey-release/synthetic-conditional-source.json',source)
  pre={'schema':1,'kind':'independent_pre_release_artwork_validation','status':'PASS','source_manifest_sha256':binding['source_manifest_sha256'],
   'delivery_spec_sha256':binding['delivery_spec_sha256'],'final_release_command_used':False,'actual_actor':'synthetic verifier',
   'completed_at':'2026-10-28T12:05:00Z','evidence':[proof]}
  preptr=self.writej('docs/emma-journey-release/synthetic-pre-art.json',pre)
  report={'schema':1,'status':'PASS','binding_sha256':s._canonical(binding),'completed_at':'2026-10-28T12:30:00Z',
   'checks':{name:{'status':'PASS','completed_at':'2026-10-28T12:10:00Z','evidence':[proof]} for name in s.CONDITIONAL_CHECKS}}
  report['checks']['artwork_and_provenance'].update(method='independent_pre_release_artwork_validation',evidence=[preptr])
  reportptr=self.writej('docs/emma-journey-release/synthetic-conditional-checks.json',report)
  owner.update(accepted_at='2026-10-28T10:01:00Z',acceptance_mode='conditional_on_remaining_checks',
   conditional_scope={'kind':'publish_after_remaining_checks_pass','page_sha256':binding['page_sha256'],
    'source_manifest_sha256':binding['source_manifest_sha256'],'authorization_source':sourceptr,'checks_report':reportptr})
  return source,report,pre
 def synthetic_pins(self):
  q={'actor':'Albert','message_id_sha256':s.sha(b'fake question id'),'sent_at_sha256':s.sha(b'fake question time'),'text_sha256':SYNTHETIC_QUESTION_SHA256}
  a={'actor':'Wyatt','message_id_sha256':s.sha(b'fake answer id'),'sent_at_sha256':s.sha(b'fake answer time'),'text_sha256':s.sha(b'fake answer')}
  return patch.multiple(s,CONDITIONAL_QUESTION_SHA256=SYNTHETIC_QUESTION_SHA256,CONDITIONAL_SOURCE_METADATA_SHA256=s._canonical({'question':q,'answer':a}),
   CONDITIONAL_ACCEPTED_AT_SHA256=s.sha(b'2026-10-28T10:01:00.000000+00:00'),PRIVATE_READBACK_SHA256='a'*64)
 def test_synthetic_conditional_acceptance_keeps_real_order(self):
  def change(b,r,a,o):self.conditional(b,o)
  with self.synthetic_pins():self.assertIn('validated exact source',self.gate(change)['status'])
 def test_conditional_acceptance_rejects_changed_subject_or_missing_checks(self):
  modes=('page','art','scope','source_missing','answer_no','wrong_actor','answer_time','question_no_condition','raw_text','wrong_private_digest','no_verifier','unverified','future_verification','owner_time','missing_check','failed_check','missing_evidence','stale_report','early_report','future_check','early_source','unknown_mode','art_method','art_final_command','art_wrong_subject','art_wrong_delivery','art_no_evidence','art_future','art_fail')
  for mode in modes:
   def change(b,r,a,o):
    source,report,pre=self.conditional(b,o);scope=o['conditional_scope']
    if mode=='page':scope['page_sha256']='0'*64
    if mode=='art':scope['source_manifest_sha256']='0'*64
    if mode=='scope':scope['kind']='approve_now'
    if mode=='source_missing':scope['authorization_source']={'path':'missing.json','bytes':1,'sha256':'0'*64}
    if mode=='unknown_mode':o['acceptance_mode']='unknown'
    if mode=='answer_no':source['answer']['text_sha256']='0'*64
    if mode=='wrong_actor':source['answer']['actor']='other'
    if mode=='answer_time':source['answer']['sent_at_sha256']='0'*64
    if mode=='question_no_condition':source['question']['text_sha256']='0'*64
    if mode=='raw_text':source['question']['text']='private text must not be committed'
    if mode=='wrong_private_digest':source['verification']['private_readback_sha256']='0'*64
    if mode=='no_verifier':source['verification']['actual_actor']=''
    if mode=='unverified':source['verification']['status']='PENDING'
    if mode=='future_verification':source['verification']['verified_at']='2026-10-28T13:00:00Z'
    if mode=='owner_time':o['accepted_at']='2026-10-28T10:02:00Z'
    if mode in ('answer_no','wrong_actor','answer_time','question_no_condition','raw_text','wrong_private_digest','no_verifier','unverified','future_verification'):
     scope['authorization_source']=self.writej('docs/emma-journey-release/changed-conditional-source.json',source)
    if mode=='missing_check':report['checks'].pop('search')
    if mode=='failed_check':report['checks']['gallery']['status']='FAIL'
    if mode=='missing_evidence':report['checks']['search']['evidence']=[]
    if mode=='stale_report':report['binding_sha256']='0'*64
    if mode=='early_report':report['completed_at']='2026-10-28T11:00:00Z'
    if mode=='future_check':report['checks']['search']['completed_at']='2026-10-28T13:00:00Z'
    if mode=='early_source':report['checks']['source_and_prose']['completed_at']='2026-10-28T11:00:00Z'
    if mode=='art_method':report['checks']['artwork_and_provenance']['method']='final_release'
    if mode=='art_final_command':pre['final_release_command_used']=True
    if mode=='art_wrong_subject':pre['source_manifest_sha256']='0'*64
    if mode=='art_wrong_delivery':pre['delivery_spec_sha256']='0'*64
    if mode=='art_no_evidence':pre['evidence']=[]
    if mode=='art_future':pre['completed_at']='2026-10-28T13:00:00Z'
    if mode=='art_fail':pre['status']='FAIL'
    if mode.startswith('art_') and mode!='art_method':report['checks']['artwork_and_provenance']['evidence']=[self.writej('docs/emma-journey-release/changed-pre-art.json',pre)]
    if mode in ('missing_check','failed_check','missing_evidence','stale_report','early_report','future_check','early_source') or mode.startswith('art_'):
     scope['checks_report']=self.writej('docs/emma-journey-release/changed-conditional-checks.json',report)
   with self.synthetic_pins(),self.subTest(mode=mode),self.assertRaises((AssertionError,OSError)):self.gate(change)
 def test_conditional_unpinned_private_readback_fails_closed(self):
  def change(b,r,a,o):self.conditional(b,o)
  with self.synthetic_pins(),patch.object(s,'PRIVATE_READBACK_SHA256',None),self.assertRaisesRegex(AssertionError,'PENDING independently reviewed private readback'):self.gate(change)
 def test_conditional_subject_cannot_be_rebound_to_different_bytes(self):
  for key in ('page_sha256','source_manifest_sha256'):
   binding={'page_sha256':s.CONDITIONAL_PAGE_SHA256,'source_manifest_sha256':s.CONDITIONAL_SOURCE_MANIFEST_SHA256,'delivery_spec_sha256':'f'*64}
   owner={};self.conditional(binding,owner);binding[key]='0'*64;owner['conditional_scope'][key]='0'*64
   with self.subTest(key=key),self.assertRaisesRegex(AssertionError,'conditional acceptance subject changed'):
    s.validate_conditional_acceptance(self.root,owner,binding,[s._time('2026-10-28T12:00:00Z')])
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
