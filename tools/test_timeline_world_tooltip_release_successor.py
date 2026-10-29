"""Actual predecessor checks and explicitly synthetic final-review negatives."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import timeline_current_index_closure as old
import timeline_world_mobile_successor as mobile
import timeline_world_tooltip_visual_successor as tooltip
import timeline_world_tooltip_release_successor as gate
ROOT=Path(__file__).resolve().parents[1]
class TooltipReleaseSuccessorTests(unittest.TestCase):
 def setUp(self):self.current=old.tool_tree(ROOT)
 def test_exact_historical_tree_and_unknown_changes_fail(self):
  prior=gate.project_tree(ROOT,self.current);self.assertEqual(old.canonical(prior),gate.PRIOR_TREE)
  with self.assertRaisesRegex(ValueError,'historical tool tree differs'):gate.project_tree(ROOT,dict(self.current,**{'tools/unreviewed.py':'0'*64}))
  with patch.object(gate,'MANIFEST_SHA256','0'*64),self.assertRaisesRegex(ValueError,'manifest changed'):gate.project_tree(ROOT,self.current)
 def test_actual_final_code_review_stays_pending(self):
  with patch.object(gate,'CODE_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING independent final tooltip integration code review'):gate.project_reviewed_tree(ROOT,self.current)
 def test_synthetic_final_review_subjects_and_negatives(self):
  synthetic={'schema':'timeline-tooltip-final-integration-code-v1','scope':'tooltip_integration_and_exact_tool_tree','verdict':'CONCUR_WITHIN_BOUNDED_CODE_SCOPE','reviewer_commitment':'1'*64,'implementer_commitment':'3'*64,'receipt_sha256':'2'*64,'page_sha256':tooltip.PAGE_AFTER,'browser_test_sha256':tooltip.TEST_AFTER,'controller_sha256':mobile.CONTROLLER_SHA,'visual_review_sha256':tooltip.REVIEW_SHA,'prior_code_review_sha256':tooltip.CODE_REVIEW_SHA,'source_manifest_sha256':tooltip.MANIFEST_SHA,'tree_manifest_sha256':gate.MANIFEST_SHA256,'provider_diagnostic_sha256':gate.sha(mobile.source(ROOT,'tools/world_provider_browser_diagnostic.js')),'provider_diagnostic_test_sha256':gate.sha(mobile.source(ROOT,'tools/test_world_provider_browser_diagnostic.js')),'current_tool_tree_sha256':old.canonical(self.current),'reviewed_at':'2026-10-29T19:10:00Z'}
  original=mobile.source
  def run(row,implementer='3'*64,reviewer='1'*64):
   raw=json.dumps(row).encode()
   def read(root,name):return raw if name==gate.CODE_REVIEW else original(root,name)
   with patch.object(mobile,'source',side_effect=read),patch.object(gate,'CODE_REVIEW_SHA256',gate.sha(raw)),patch.object(gate,'CODE_REVIEWER_COMMITMENT',reviewer),patch.object(gate,'CODE_RECEIPT_SHA256','2'*64),patch.object(gate,'MOBILE_IMPLEMENTER_COMMITMENT',implementer):return gate.project_reviewed_tree(ROOT,self.current)
  self.assertEqual(old.canonical(run(synthetic)),gate.PRIOR_TREE)
  for field,value in [('verdict','RELEASE_APPROVED'),('implementer_commitment','0'*64),('page_sha256','0'*64),('visual_review_sha256','0'*64),('prior_code_review_sha256','0'*64),('tree_manifest_sha256','0'*64),('provider_diagnostic_sha256','0'*64),('current_tool_tree_sha256','0'*64),('reviewed_at','2026-10-29T18:00:00Z')]:
   row=copy.deepcopy(synthetic);row[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):run(row)
  for bad in ('1'*64,'not-a-hash',None):
   with self.subTest(implementer=bad),self.assertRaises(ValueError):run(synthetic,implementer=bad)
  with self.assertRaises(ValueError):run(synthetic,reviewer='4'*64)
if __name__=='__main__':unittest.main()
