"""Synthetic review-data negatives; only actual receipts may authorize release."""
import copy, unittest
from unittest.mock import patch
import timeline_current_index_closure as gate
import timeline_search_index_successor as index
import timeline_51_current_successor as event
import timeline_51_search_successor as event_search

class CurrentIndexClosureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # The older synthetic review receives the exact event successor inputs;
  # actual event review and producer checks have their own dedicated tests.
  cls.previous_search=event_search.restore((index.ROOT/'site-search-index.json').read_bytes())
  cls.previous_ledger=event.project_ledger(index.ROOT,event.validate_content(index.ROOT))
 def setUp(self):
  self.review={'schema':'timeline-current-index-review-v1','scope':'three_changed_records_and_unchanged_emma_indices','verdict':'CONCUR','reviewer_commitment':'1'*64,'private_receipt_sha256':'2'*64,'reviewed_at':'2026-01-01T00:00:00Z','prior_search_sha256':index.BEFORE,'current_search_sha256':index.AFTER,'source_sha256':index.SOURCES,'changed_urls':sorted(index.CHANGED),'emma_records_unchanged':True,'panel_sha256':gate.PANEL,'gallery_sha256':gate.GALLERY}
  self.code={'schema':'timeline-index-successor-code-review-v1','scope':'current_successor_and_exact_tool_tree','verdict':'CONCUR','reviewer_commitment':'3'*64,'private_receipt_sha256':'4'*64,'reviewed_at':'2026-01-01T00:00:01Z','current_tool_tree_sha256':gate.canonical({'synthetic':'tree'}),'index_review_sha256':gate.INDEX_REVIEW_SHA256,'search_manifest_sha256':gate.sha(index.source(index.ROOT,index.MANIFEST)),'historical_tree_manifest_sha256':gate.sha(index.source(index.ROOT,gate.TREE_PROJECTION))}
  self.tree={'synthetic':'tree'};self.prior={'tools/emma_public_commitments.py':'5'*64,'old':'tree'}
 def call(self,review=None,code=None):
  review=self.review if review is None else review;code=self.code if code is None else code
  extension={'previous_search':self.previous_search,'previous_ledger':self.previous_ledger,'previous_tool_tree':self.tree}
  with patch.object(event,'prepare',return_value=extension) as event_prepare,patch.object(gate,'pinned',side_effect=lambda root,name,pin:review if name==gate.INDEX_REVIEW else code),patch.object(gate,'project_old_tree',return_value=self.prior):
   result=gate.prepare(index.ROOT);event_prepare.assert_called_once_with(index.ROOT);return result
 def test_real_review_pin_absence_fails_closed(self):
  extension={'previous_search':self.previous_search,'previous_ledger':self.previous_ledger,'previous_tool_tree':self.tree}
  with patch.object(event,'prepare',return_value=extension),patch.object(gate,'CODE_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING'):
   gate.prepare(index.ROOT)
 def test_synthetic_exact_review_projection(self):
  r=self.call();self.assertEqual(index.sha(r['historical_search']),index.BEFORE)
 def test_altered_review_fails(self):
  for field,value in [('verdict','HOLD'),('emma_records_unchanged',False),('current_search_sha256','0'*64),('source_sha256',{}),('changed_urls',sorted(index.CHANGED)+[sorted(index.CHANGED)[0]]),('panel_sha256','0'*64),('private_receipt_sha256',''),('reviewed_at','unknown')]:
   bad=copy.deepcopy(self.review);bad[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.call(review=bad)
 def test_independent_code_review_and_current_tree_required(self):
  for field,value in [('verdict','HOLD'),('reviewer_commitment','1'*64),('current_tool_tree_sha256','0'*64),('index_review_sha256','0'*64),('search_manifest_sha256','0'*64),('historical_tree_manifest_sha256','0'*64),('private_receipt_sha256',''),('reviewed_at','unknown'),('reviewed_at','2025-01-01T00:00:00Z')]:
   bad=copy.deepcopy(self.code);bad[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.call(code=bad)
if __name__=='__main__':unittest.main()
