"""Synthetic-only boundary tests; no human/release acceptance is inferred."""
import copy,hashlib,json,sys,tempfile,types,unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
import emma_journey_closure_successor as j
import artwork_owner_closure as old
ROOT=HERE.parent; ACTUAL=ROOT/'history/emma-hale-smith.html'; REG=ROOT/'docs/exclusive-artwork-ownership.json'
class PublicClosureProjectionTests(unittest.TestCase):
 """Structural checks only; fixture mutations never approve a release."""
 @classmethod
 def setUpClass(cls):
  cls.record=json.loads((ROOT/'docs/emma-journey-owner-closure/current-review.json').read_bytes())
 def run_projection(self,record):
  return j.check_public_reviews(ROOT,record,record['reviewers'],record['root_review'])
 def test_actual_projection_structure(self):
  self.assertIsNone(self.run_projection(copy.deepcopy(self.record)))
 def test_actor_output_and_evidence_drift_fail(self):
  for change in (lambda x:x['reviewers'][0].update(actual_actor='wrong'),
                 lambda x:x['reviewers'].reverse(),
                 lambda x:x['gallery'].update(sha256='0'*64),
                 lambda x:x['current_confirmation_evidence'].update(sha256='0'*64),
                 lambda x:x['assets_manifest'].update(sha256='0'*64)):
   x=copy.deepcopy(self.record);change(x)
   if x['reviewers']==list(reversed(self.record['reviewers'])):
    x['reviewers'][0]['actual_actor'],x['reviewers'][1]['actual_actor']=x['reviewers'][1]['actual_actor'],x['reviewers'][0]['actual_actor']
   with self.assertRaises((ValueError,KeyError)):self.run_projection(x)
 def test_confirmation_must_preserve_nonwithdrawal_and_root_signoff(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'confirmation.json';original=j.local
   src=ROOT/'docs/emma-journey-public/closure-confirmations.json'
   for change in (lambda x:x['fermi'].update(withdrawn=True),
                  lambda x:x['albert'].update(withdrawn=True),
                  lambda x:x['albert'].update(verdict='HOLD'),
                  lambda x:x['albert'].update(section_panel_mandate_personally_read=False)):
    proof=json.loads(src.read_bytes());change(proof);raw=json.dumps(proof).encode();path.write_bytes(raw)
    row=copy.deepcopy(self.record);row['current_confirmation_evidence']['sha256']=hashlib.sha256(raw).hexdigest()
    def use_test_file(root,name):return path if name=='docs/emma-journey-public/closure-confirmations.json' else original(root,name)
    with patch.object(j,'local',side_effect=use_test_file),self.assertRaises(ValueError):self.run_projection(row)
 def test_public_path_invokes_release_and_preserves_owner_conditions(self):
  import emma_public_commitments as public
  import timeline_current_index_closure as timeline
  import timeline_search_index_successor as search
  import timeline_51_search_successor as events
  current=(ROOT/'site-search-index.json').read_bytes()
  # Reconstruct each exact predecessor in order; neither successor accepts
  # unknown current bytes, even in this synthetic owner-condition test.
  with self.assertRaisesRegex(ValueError,'Unreviewed event search index'):
   events.restore(current+b' ')
  with patch.object(events,'MANIFEST_SHA','0'*64),self.assertRaisesRegex(ValueError,'Changed event search delta manifest'):
   events.restore(current)
  previous=search.restore(events.restore(current))
  # Synthetic injection exercises the historical owner checks; the separate
  # current-index tests require real evidence before the actual gate can pass.
  self.enterContext(patch.object(timeline,'prepare',return_value={'historical_search':previous}))
  original=j.local;record=self.record;raw=json.dumps(record).encode();ownerpath=record['owner_acceptance']['path']
  with tempfile.TemporaryDirectory() as folder:
   tmp=Path(folder);recordfile=tmp/'record.json';recordfile.write_bytes(raw)
   def route(root,name):return recordfile if name==j.REVIEW_RECORD else original(root,name)
   with patch.object(j,'APPROVED_REVIEW_SHA256',hashlib.sha256(raw).hexdigest()),patch.object(j,'local',side_effect=route),patch.object(public,'validate_release') as gate:
    j.check_review(ROOT);gate.assert_called_once_with(ROOT)
   owner=json.loads(original(ROOT,ownerpath).read_bytes())
   for field,value,expected in [('acceptance_mode','unconditional','conditional owner evidence'),('accepted_at_commitment','0'*64,'conditional owner evidence'),('metadata_commitment','0'*64,'conditional owner evidence'),('reviewed_at','synthetic-private-time','conditional owner commitment'),('actual_actor','synthetic-owner','conditional owner commitment')]:
    bad=copy.deepcopy(owner);bad[field]=value;ownerfile=tmp/'owner.json';ownerbytes=json.dumps(bad).encode();ownerfile.write_bytes(ownerbytes)
    mutated=copy.deepcopy(record);mutated['owner_acceptance']['sha256']=hashlib.sha256(ownerbytes).hexdigest();mutatedbytes=json.dumps(mutated).encode();recordfile.write_bytes(mutatedbytes)
    def route_bad(root,name):return recordfile if name==j.REVIEW_RECORD else ownerfile if name==ownerpath else original(root,name)
    with patch.object(j,'APPROVED_REVIEW_SHA256',hashlib.sha256(mutatedbytes).hexdigest()),patch.object(j,'local',side_effect=route_bad),patch.object(public,'validate_release') as gate,self.assertRaisesRegex(ValueError,expected):
     j.check_review(ROOT)
    gate.assert_not_called()

class CurrentClosureTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
  (self.root/'history').mkdir();(self.root/'docs').mkdir();(self.root/j.HUB).write_bytes(ACTUAL.read_bytes());(self.root/j.OLD_REGISTRY).write_bytes(REG.read_bytes());(self.root/'sitemap.xml').write_text('<urlset/>')
  self.scope=[{'path':x,'sha256':'old-'+x} for x in old.CURRENT_CONSUMER_SCOPE];self.assets={f'a{i}' for i in range(73)};self.expected=Counter(old.H2_REMOVED);self.expected[('index.html','asset')] = 2
  self.current=Counter(self.expected)
  for k in old.H2_REMOVED:del self.current[k]
  self.owner=types.ModuleType('owner_journey_successor');self.owner.validate_hub=lambda *a:True;self.owner.validate_canonical=lambda *a:True
  self.index=types.ModuleType('emma_journey_indices_contract');self.index.validate_full_tree=lambda *a:{'new_emma_images':10,'additional_person_free_origins':1,'retained_emma_images':9}
  self.modules=patch.dict(sys.modules,{'owner_journey_successor':self.owner,'emma_journey_indices_contract':self.index});self.modules.start();self.addCleanup(self.modules.stop)
  self.base=patch.object(j,'validated_baseline',return_value=None);self.base.start();self.addCleanup(self.base.stop)
  self.review=patch.object(j,'check_review',return_value={});self.review.start();self.addCleanup(self.review.stop)
  self.ref=patch.object(old,'references',side_effect=self.refs);self.ref.start();self.addCleanup(self.ref.stop)
 def refs(self,root,scope,assets,origin,*,current_emma=False):
  self.assertTrue(current_emma)
  row=next(x for x in scope if x['path']==j.HUB);self.assertEqual(row['sha256'],j.CURRENT_HUB_SHA256)
  self.assertEqual({x['path']:x['sha256'] for x in scope if x['path']!=j.HUB},{x['path']:x['sha256'] for x in self.scope if x['path']!=j.HUB})
  self.assertGreater(len(assets),73);return self.current
 def run_gate(self):return j.current_census(self.root,self.scope,self.assets,'https://focuschrist.com',self.expected)
 def test_synthetic_current_census_and_no_scope_mutation(self):
  original=copy.deepcopy(self.scope);self.assertEqual(self.run_gate(),self.current);self.assertEqual(self.scope,original)
 def test_duplicate_missing_unknown_scope(self):
  for bad in (self.scope[:-1],self.scope+[self.scope[0]],self.scope[:-1]+[{'path':'unknown.html','sha256':'x'}]):
   original=self.scope;self.scope=bad
   with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,'scope drift'):self.run_gate()
   self.scope=original
 def test_current_hub_registry_and_old_h2_fail_closed(self):
  path=self.root/j.HUB;before=path.read_bytes();path.write_bytes(before+b'changed')
  with self.assertRaisesRegex(ValueError,'current hub bytes drift'):self.run_gate()
  path.write_bytes(before);path=self.root/j.OLD_REGISTRY;before=path.read_bytes();path.write_bytes(before+b'changed')
  with self.assertRaisesRegex(ValueError,'registry changed'):self.run_gate()
  path.write_bytes(before);self.expected[next(iter(old.H2_REMOVED))]+=1
  with self.assertRaisesRegex(ValueError,'historical H2 census'):self.run_gate()
 def test_missing_generated_data_and_changed_census(self):
  self.index.validate_full_tree=lambda *a:{}
  with self.assertRaisesRegex(ValueError,'index completeness'):self.run_gate()
  self.index.validate_full_tree=lambda *a:{'new_emma_images':10,'additional_person_free_origins':1,'retained_emma_images':9};self.current[('index.html','unrelated-asset')]=1
  with self.assertRaisesRegex(ValueError,'consumer census'):self.run_gate()
 def test_no_review_is_not_a_pass(self):
  self.review.stop()
  with patch.object(j,'APPROVED_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING actual current closure and owner review'):self.run_gate()
 def test_unknown_asset_count_or_origin(self):
  self.assets.remove('a0')
  with self.assertRaisesRegex(ValueError,'asset scope/origin drift'):self.run_gate()
class SyntheticReviewRecordTests(unittest.TestCase):
 """All people and evidence in this class are invented test fixtures only."""
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
  def write(name,raw):
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return {'path':name,'sha256':j.sha(raw)}
  self.write=write
  self.refs={n:write(n,('synthetic '+n).encode()) for n in ('art-gallery.json','site-search-index.json','docs/section-panel-inventory.json','docs/assets.json','docs/fermi.json','docs/newton.json','docs/owner-source.json','docs/desktop.jpg','docs/phone.jpg')}
  mapped={'gallery':'art-gallery.json','search':'site-search-index.json','panel':'docs/section-panel-inventory.json','assets_manifest':'docs/assets.json'}
  self.bindings={k:self.refs[v] for k,v in mapped.items()};self.pins={k+'_sha256':v['sha256'] for k,v in self.bindings.items()};time='2026-10-28T17:00:00Z'
  owner={'kind':'direct_owner_acceptance','actual_actor':'synthetic-owner','decision':'ACCEPT','withdrawn':False,'page_sha256':j.CURRENT_HUB_SHA256,'reviewed_at':time,'source_evidence':self.refs['docs/owner-source.json'],**self.pins}
  self.owner=self.write('docs/owner.json',json.dumps(owner).encode())
  mandates={'AGENTS.md':'8517aa734f89b5fb1d6cb62fa1c870ec2f5959c8','docs/historical-character-identity.md':'a2af09fc97c9205139ed0621075fb5d189cf93c5','docs/section-panel-design-mandate.md':'dd0db449995f1f636abd0b84b0da4820630c87c8'}
  reviews=[{'reviewer':name,'actual_actor':'fixture-'+name,'decision':'CONCUR','withdrawn':False,'page_sha256':j.CURRENT_HUB_SHA256,'mandate_blobs':mandates,'observations':'synthetic test only','reviewed_at':time,'evidence':self.refs['docs/'+name.lower()+'.json'],**self.pins} for name in ('Fermi','Newton')]
  root={'reviewer':'Albert','decision':'CONCUR','withdrawn':False,'page_sha256':j.CURRENT_HUB_SHA256,'mandate_blobs':mandates,'observations':'synthetic test only','reviewed_at':time,'desktop_inspected':True,'phone_inspected':True,'desktop_evidence':self.refs['docs/desktop.jpg'],'phone_evidence':self.refs['docs/phone.jpg'],**self.pins}
  self.record={'schema':1,'status':'owner_accepted','current_hub_sha256':j.CURRENT_HUB_SHA256,**self.bindings,'owner_acceptance':self.owner,'reviewers':reviews,'root_review':root}
 def check(self,r):
  raw=json.dumps(r).encode();self.write(j.REVIEW_RECORD,raw)
  with patch.object(j,'APPROVED_REVIEW_SHA256',j.sha(raw)),patch.object(j,'LEGACY_OWNER_COMMITMENT',j.sha(b'synthetic-owner')):return j.check_review(self.root)
 def test_positive_synthetic_and_unknown_record_pin(self):
  self.assertEqual(self.check(self.record),self.record)
  with patch.object(j,'APPROVED_REVIEW_SHA256','0'*64),self.assertRaisesRegex(ValueError,'unreviewed'):j.check_review(self.root)
 def test_missing_duplicate_wrong_binding_reviews(self):
  for change in ('missing','duplicate','subject','mandate','withdrawn'):
   r=copy.deepcopy(self.record)
   if change=='missing':r['reviewers'].pop()
   if change=='duplicate':r['reviewers'][1]['actual_actor']=r['reviewers'][0]['actual_actor']
   if change=='subject':r['reviewers'][0]['gallery_sha256']='0'*64
   if change=='mandate':r['reviewers'][0]['mandate_blobs']={}
   if change=='withdrawn':r['reviewers'][0]['withdrawn']=True
   with self.subTest(change=change),self.assertRaises(ValueError):self.check(r)
 def test_missing_owner_or_rendered_evidence(self):
  for change in ('owner','desktop','phone','stale'):
   r=copy.deepcopy(self.record)
   if change=='owner':r['owner_acceptance']=None
   if change=='desktop':r['root_review']['desktop_evidence']=None
   if change=='phone':r['root_review']['phone_inspected']=False
   if change=='stale':r['gallery']['sha256']='0'*64
   with self.subTest(change=change),self.assertRaises(ValueError):self.check(r)
 def test_owner_subject_mismatch(self):
  r=copy.deepcopy(self.record);owner=json.loads((self.root/r['owner_acceptance']['path']).read_bytes());owner['page_sha256']='0'*64;r['owner_acceptance']=self.write('docs/owner.json',json.dumps(owner).encode())
  with self.assertRaisesRegex(ValueError,'owner acceptance subject mismatch'):self.check(r)
 def test_legacy_owner_commitment_and_actor_mismatch(self):
  self.assertEqual(j.LEGACY_OWNER_COMMITMENT,'f190d2ae997ec531a16e422d424eb756af1249ff4b88f5f29ab191b59fd6397a')
  r=copy.deepcopy(self.record);owner=json.loads((self.root/r['owner_acceptance']['path']).read_bytes());owner['actual_actor']='different-owner';r['owner_acceptance']=self.write('docs/owner.json',json.dumps(owner).encode())
  with self.assertRaisesRegex(ValueError,'direct owner acceptance missing'):self.check(r)

class ProductionDispatchTests(unittest.TestCase):
 """Execute the real production dispatch branch with only callees mocked."""
 def test_current_exact_hub_dispatch_and_unknown_falls_back_fail_closed(self):
  import ast
  from unittest.mock import Mock
  tree=ast.parse((HERE/'artwork_owner_closure.py').read_text())
  function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate')
  branch=next(n for n in function.body if isinstance(n,ast.If) and ast.unparse(n.test)=='expected_contract == OWNER_CLOSURE_CONTRACT')
  code=compile(ast.Module(body=[branch],type_ignores=[]),'production-closure-dispatch','exec')
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);page=root/j.HUB;page.parent.mkdir(parents=True);page.write_bytes(ACTUAL.read_bytes())
   current=Mock(return_value=Counter({('actual','fixture'):1}));predecessor=Mock(side_effect=ValueError('predecessor rejected unknown bytes'))
   env={'expected_contract':old.OWNER_CLOSURE_CONTRACT,'OWNER_CLOSURE_CONTRACT':old.OWNER_CLOSURE_CONTRACT,
        'local':old.local,'hashlib':hashlib,'root':root,'scope':[],'assets':set(),'contract':{'site_origin':'https://focuschrist.com'},
        'expected':Counter(),'current_retirement_census':predecessor,'references':Mock()}
   with patch.object(j,'current_census',current):
    exec(code,env);self.assertEqual(env['current_expected'],Counter({('actual','fixture'):1}));current.assert_called_once();predecessor.assert_not_called()
    page.write_bytes(b'unknown current bytes')
    with self.assertRaisesRegex(ValueError,'predecessor rejected unknown bytes'):exec(code,env)
    self.assertEqual(current.call_count,1);predecessor.assert_called_once()

if __name__=='__main__':unittest.main()
