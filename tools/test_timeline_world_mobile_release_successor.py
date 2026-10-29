"""Actual predecessor checks and explicitly synthetic current-review negatives."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import timeline_current_index_closure as old
import timeline_world_mobile_release_successor as gate
import timeline_world_mobile_successor as mobile
ROOT=Path(__file__).resolve().parents[1]
class MobileReleaseSuccessorTests(unittest.TestCase):
 def setUp(self):self.current=old.tool_tree(ROOT)
 def test_exact_historical_tree_and_unknown_changes_fail(self):
  previous=gate.project_tree(ROOT,self.current);self.assertEqual(old.canonical(previous),gate.PRIOR_TREE)
  with self.assertRaisesRegex(ValueError,'historical tool tree differs'):gate.project_tree(ROOT,dict(self.current,**{'tools/unreviewed.py':'0'*64}))
  with patch.object(gate,'TREE_MANIFEST_SHA256','0'*64),self.assertRaisesRegex(ValueError,'manifest changed'):gate.project_tree(ROOT,self.current)
 def test_actual_missing_code_review_stays_pending(self):
  with patch.object(gate,'MOBILE_CODE_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING independently verified current mobile code review'):
   gate.project_reviewed_tree(ROOT,self.current)
 def test_synthetic_current_review_subjects_and_negatives(self):
  synthetic={'schema':'timeline-mobile-current-code-review-v1','scope':'mobile_visual_gate_and_tool_tree_successor','verdict':'CONCUR_WITHIN_BOUNDED_CODE_SCOPE','reviewer_commitment':'1'*64,'implementer_commitment':'3'*64,'receipt_sha256':'2'*64,'page_sha256':mobile.AFTER,'controller_sha256':mobile.CONTROLLER_SHA,'browser_test_sha256':mobile.BROWSER_TEST_SHA,'albert_review_sha256':mobile.ALBERT_CONTENT_REVIEW_SHA,'newton_review_sha256':mobile.NEWTON_VISUAL_REVIEW_SHA,'prior_code_review_sha256':gate.PRIOR_CODE_REVIEW_SHA256,'tree_manifest_sha256':gate.TREE_MANIFEST_SHA256,'current_tool_tree_sha256':old.canonical(self.current),'reviewed_at':'2026-10-29T17:49:00Z'}
  original=gate.source
  def run(row):
   raw=json.dumps(row).encode()
   def read(root,name):return raw if name==gate.CODE_REVIEW else original(root,name)
   with patch.object(gate,'source',side_effect=read),patch.object(gate,'MOBILE_CODE_REVIEW_SHA256',gate.sha(raw)),patch.object(gate,'MOBILE_CODE_REVIEWER_COMMITMENT',row['reviewer_commitment']),patch.object(gate,'MOBILE_CODE_REVIEW_RECEIPT_SHA256','2'*64),patch.object(gate,'MOBILE_IMPLEMENTER_COMMITMENT','3'*64):return gate.project_reviewed_tree(ROOT,self.current)
  self.assertEqual(old.canonical(run(synthetic)),gate.PRIOR_TREE)
  for field,value in [('verdict','RELEASE_APPROVED'),('implementer_commitment','0'*64),('page_sha256','0'*64),('controller_sha256','0'*64),('browser_test_sha256','0'*64),('newton_review_sha256','0'*64),('prior_code_review_sha256','0'*64),('tree_manifest_sha256','0'*64),('current_tool_tree_sha256','0'*64),('reviewed_at','2026-10-29T17:00:00Z')]:
   bad=copy.deepcopy(synthetic);bad[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):run(bad)
  bad=copy.deepcopy(synthetic);bad['reviewer_commitment']='3'*64
  with self.assertRaisesRegex(ValueError,'code reviewer must be distinct from implementer'):run(bad)
  # An alternative independent reviewer commitment remains acceptable.
  other_role=copy.deepcopy(synthetic);other_role['reviewer_commitment']='4'*64
  self.assertEqual(old.canonical(run(other_role)),gate.PRIOR_TREE)
  raw=json.dumps(synthetic).encode()
  def read(root,name):return raw if name==gate.CODE_REVIEW else original(root,name)
  for missing in ('MOBILE_IMPLEMENTER_COMMITMENT',):
   with self.subTest(missing=missing),patch.object(gate,'source',side_effect=read),patch.object(gate,'MOBILE_CODE_REVIEW_SHA256',gate.sha(raw)),patch.object(gate,'MOBILE_CODE_REVIEWER_COMMITMENT','1'*64),patch.object(gate,'MOBILE_CODE_REVIEW_RECEIPT_SHA256','2'*64),patch.object(gate,'MOBILE_IMPLEMENTER_COMMITMENT','3'*64),patch.object(gate,missing,None),self.assertRaisesRegex(ValueError,'PENDING independently verified mobile implementer commitment'):
    gate.project_reviewed_tree(ROOT,self.current)
if __name__=='__main__':unittest.main()
