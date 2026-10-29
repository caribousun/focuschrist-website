"""Focused negative and synthetic fixture tests, not actual review evidence."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import static_content_audit as audit
import timeline_51_current_successor as gate
import timeline_51_search_successor as search
import timeline_current_index_closure as prior

ROOT=Path(__file__).resolve().parents[1]
class EventSuccessorTests(unittest.TestCase):
 def content_fixture(self):
  files={name:gate.sha((ROOT/name).read_bytes()) for name in gate.SOURCE_FILES}
  return {'schema':'timeline-51-content-review-v1','scope':'bounded_current_source_content','verdict':'CONCUR','source_head':gate.SOURCE_HEAD,'source_receipts':dict(gate.SOURCE_RECEIPTS),'reviewer_commitments':dict(gate.CONTENT_ACTORS),'role_scopes':dict(gate.CONTENT_ROLE_SCOPES),'reviewed_file_sha256':files,'verifier_commitment':'a'*64,'verification_receipt_sha256':'b'*64,'limits':{'needles':'unresolved','pacific_springs':'context_only','primary_exhaustive':False,'rights':False,'visual':False,'runtime':False,'whole_site':False,'code':False,'index':False,'owner':False,'release':False}}
 def index_fixture(self):
  old=json.loads(search.restore((ROOT/'site-search-index.json').read_bytes(),ROOT));cur=json.loads((ROOT/'site-search-index.json').read_bytes());a={r['url']:r for r in old['records']};b={r['url']:r for r in cur['records']}
  return {'schema':'timeline-51-index-review-v1','scope':'actual_current_index_delta','verdict':'CONCUR','reviewer_commitment':'c'*64,'receipt_sha256':'d'*64,'prior_search_sha256':search.BEFORE,'current_search_sha256':search.AFTER,'search_manifest_sha256':search.MANIFEST_SHA,'source_sha256':search.manifest(ROOT)['source_sha256'],'changed_urls':sorted(u for u in a.keys()|b.keys() if a.get(u)!=b.get(u)),'emma_unchanged_records':71,'panel_sha256':gate.PANEL,'gallery_sha256':gate.GALLERY,'reviewed_at':'2026-10-29T12:00:00Z'}
 def test_actual_producer_runs_but_missing_index_review_fails_closed(self):
  with patch.object(gate,'INDEX_REVIEW_SHA256',None),patch.object(search,'validate_current',wraps=search.validate_current) as producer:
   with self.assertRaisesRegex(ValueError,'PENDING independently verified'):gate.validate_index(ROOT)
   producer.assert_called_once()
  with patch.object(gate,'INDEX_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING independently verified'):prior.prepare(ROOT)
 def test_actual_content_and_index_are_bound_but_code_review_is_pending(self):
  content=gate.validate_content(ROOT);self.assertEqual(gate.sha(gate.project_ledger(ROOT,content)),gate.PRIOR_LEDGER)
  previous,_,result=gate.validate_index(ROOT);self.assertEqual(gate.sha(previous),search.BEFORE);self.assertEqual(result['current_sha256'],search.AFTER)
  with patch.object(gate,'CODE_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'code-review.json'):prior.prepare(ROOT)
 def test_both_emma_consumers_invoke_current_event_gate_before_old_evidence(self):
  import emma_public_commitments as public
  import emma_journey_closure_successor as journey
  with patch.object(gate,'prepare',side_effect=ValueError('event gate reached')) as check:
   with self.assertRaisesRegex(ValueError,'event gate reached'):public.validate_release(ROOT)
   check.assert_called_once()
  with patch.object(gate,'prepare',side_effect=ValueError('event gate reached')) as check:
   with self.assertRaisesRegex(ValueError,'event gate reached'):journey.check_review(ROOT)
   check.assert_called_once()

 def test_content_receipt_scope_and_independence_are_required(self):
  fixture=self.content_fixture()
  with patch.object(gate,'pinned',return_value=fixture),patch.object(gate,'CONTENT_VERIFIER_COMMITMENT','a'*64),patch.object(gate,'CONTENT_VERIFICATION_RECEIPT_SHA256','b'*64):
   self.assertEqual(gate.validate_content(ROOT),fixture)
   for key,mutation in [('source_receipts',lambda x:x.update(fermi='0'*64)),('reviewer_commitments',lambda x:x.update(fermi=x['newton'])),('role_scopes',lambda x:x.update(albert='full_archival_review')),('reviewed_file_sha256',lambda x:x.update({'pioneers.html':'0'*64})),('limits',lambda x:x.update(owner=True))]:
    changed=copy.deepcopy(fixture);mutation(changed[key])
    with self.subTest(key=key),patch.object(gate,'pinned',return_value=changed),self.assertRaises(ValueError):gate.validate_content(ROOT)
   with patch.object(gate,'CONTENT_VERIFICATION_RECEIPT_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING content receipt verification'):gate.validate_content(ROOT)
   for actor in gate.CONTENT_ACTORS.values():
    with self.subTest(verifier=actor),patch.object(gate,'CONTENT_VERIFIER_COMMITMENT',actor),self.assertRaisesRegex(ValueError,'verifier must be independent'):gate.validate_content(ROOT)
 def test_index_subject_and_independent_identity_are_required(self):
  fixture=self.index_fixture()
  with patch.object(gate,'pinned',return_value=fixture),patch.object(gate,'INDEX_REVIEWER_COMMITMENT','c'*64),patch.object(gate,'INDEX_RECEIPT_SHA256','d'*64):
   old,review,_=gate.validate_index(ROOT);self.assertEqual(gate.sha(old),search.BEFORE);self.assertEqual(review,fixture)
   for key,value in [('current_search_sha256','0'*64),('emma_unchanged_records',70),('receipt_sha256','0'*64),('changed_urls',fixture['changed_urls'][:-1]),('panel_sha256','0'*64)]:
    changed=copy.deepcopy(fixture);changed[key]=value
    with self.subTest(key=key),patch.object(gate,'pinned',return_value=changed),self.assertRaises(ValueError):gate.validate_index(ROOT)
   with patch.object(search,'validate_current',side_effect=ValueError('producer mismatch')),self.assertRaisesRegex(ValueError,'producer mismatch'):gate.validate_index(ROOT)
 def test_prior_ledger_reconstructed_only_after_exact_current_binding(self):
  original=gate.project_ledger(ROOT,gate.validate_content(ROOT));data=json.loads(original);review=self.content_fixture();out=[]
  for row in data['documents']:
   name=row['path']
   if name in gate.CONTENT_PAGES:
    current=copy.deepcopy(row);current['prior_timeline_51_content_review']=row;current['timeline_51_content_review']={'path':gate.CONTENT_REVIEW,'sha256':'e'*64};current['reviewed_timeline_51_source_sha256']=review['reviewed_file_sha256'][name];current['published_text_sha256']=audit.content_hash(ROOT/name)
    if name in audit.INLINE_SCRIPT_ROUTES:current['reviewed_inline_script_sha256']=audit.inline_script_hash(ROOT/name)
    out.append(current)
   else:out.append(row)
  actual=(json.dumps(dict(data,documents=out),ensure_ascii=False,indent=2)+'\n').encode();real=gate.prior_search.source
  def source(root,name):return actual if name=='content-audit.json' else real(root,name)
  with patch.object(gate,'CONTENT_REVIEW_SHA256','e'*64),patch.object(gate.prior_search,'source',side_effect=source),patch.object(audit,'validate',return_value=0):
   self.assertEqual(gate.project_ledger(ROOT,review),original)
   bad=json.loads(actual);next(x for x in bad['documents'] if x['path']=='pioneers.html')['published_text_sha256']='0'*64
   altered=(json.dumps(bad,ensure_ascii=False,indent=2)+'\n').encode()
   with patch.object(gate.prior_search,'source',side_effect=lambda root,name:altered if name=='content-audit.json' else real(root,name)),self.assertRaisesRegex(ValueError,'text binding'):gate.project_ledger(ROOT,review)
   bad=json.loads(actual);next(x for x in bad['documents'] if x['path']=='pioneers.html')['review_standard']='invented earlier review'
   altered=(json.dumps(bad,ensure_ascii=False,indent=2)+'\n').encode()
   with patch.object(gate.prior_search,'source',side_effect=lambda root,name:altered if name=='content-audit.json' else real(root,name)),self.assertRaisesRegex(ValueError,'Historical content metadata changed'):gate.project_ledger(ROOT,review)
 def test_exact_tree_projection_rejects_unknown_or_missing_paths(self):
  current=prior.tool_tree(ROOT);old=gate.project_tree(ROOT,current)
  self.assertEqual(prior.canonical(old),gate.PRIOR_TREE)
  with self.assertRaisesRegex(ValueError,'Historical Timeline tool tree mismatch'):
   gate.project_tree(ROOT,dict(current,**{'tools/unreviewed-extra.py':'0'*64}))
  manifest=gate.pinned(ROOT,gate.TREE_MANIFEST,gate.TREE_MANIFEST_SHA256);name=next(iter(manifest['previous']));missing=dict(current);del missing[name]
  with self.assertRaisesRegex(ValueError,'Tree projection path missing'):gate.project_tree(ROOT,missing)
  changed=copy.deepcopy(manifest);changed['previous'][name]='0'*64
  with patch.object(gate,'pinned',return_value=changed),self.assertRaisesRegex(ValueError,'Historical Timeline tool tree mismatch'):gate.project_tree(ROOT,current)

 def test_synthetic_current_reviews_are_all_bound_before_projection(self):
  index=self.index_fixture();current_tree={'tools/fixture.py':'f'*64};ledger=(ROOT/'content-audit.json').read_bytes();code={'schema':'timeline-51-code-review-v1','scope':'current_event_successor_and_tool_tree','verdict':'CONCUR','reviewer_commitment':'1'*64,'receipt_sha256':'2'*64,'content_review_sha256':'3'*64,'index_review_sha256':'4'*64,'content_ledger_sha256':gate.sha(ledger),'tree_manifest_sha256':gate.TREE_MANIFEST_SHA256,'reviewed_at':'2026-10-29T12:01:00Z','tool_tree_sha256':prior.canonical(current_tree)}
  with patch.object(gate,'validate_index',return_value=(b'previous',index,{})),patch.object(gate,'validate_content',return_value={}),patch.object(gate,'project_ledger',return_value=b'ledger'),patch.object(gate,'pinned',return_value=code),patch.object(gate,'INDEX_REVIEWER_COMMITMENT','c'*64),patch.object(gate,'CODE_REVIEWER_COMMITMENT','1'*64),patch.object(gate,'CODE_RECEIPT_SHA256','2'*64),patch.object(gate,'CONTENT_REVIEW_SHA256','3'*64),patch.object(gate,'INDEX_REVIEW_SHA256','4'*64),patch.object(prior,'tool_tree',return_value=current_tree),patch.object(gate,'project_tree',return_value={'old':'fixture'}):
   got=gate.prepare(ROOT);self.assertEqual(got,{'previous_search':b'previous','previous_ledger':b'ledger','previous_tool_tree':{'old':'fixture'}})
   for key,value in [('content_review_sha256','0'*64),('index_review_sha256','0'*64),('content_ledger_sha256','0'*64),('tool_tree_sha256','0'*64),('reviewed_at','2026-10-29T11:59:00Z')]:
    changed=copy.deepcopy(code);changed[key]=value
    with self.subTest(key=key),patch.object(gate,'pinned',return_value=changed),self.assertRaises(ValueError):gate.prepare(ROOT)

 def test_code_review_cannot_be_bypassed_by_index_reviewer(self):
  index=self.index_fixture();code={'schema':'timeline-51-code-review-v1','scope':'current_event_successor_and_tool_tree','verdict':'CONCUR','reviewer_commitment':'c'*64,'receipt_sha256':'d'*64}
  with patch.object(gate,'validate_index',return_value=(b'previous',index,{})),patch.object(gate,'validate_content',return_value={}),patch.object(gate,'project_ledger',return_value=b'ledger'),patch.object(gate,'pinned',return_value=code),patch.object(gate,'INDEX_REVIEWER_COMMITMENT','c'*64),patch.object(gate,'CODE_REVIEWER_COMMITMENT','c'*64),patch.object(gate,'CODE_RECEIPT_SHA256','d'*64):
   with self.assertRaisesRegex(ValueError,'Independent code reviewer'):gate.prepare(ROOT)
if __name__=='__main__':unittest.main()
