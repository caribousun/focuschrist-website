"""Mechanical projection and synthetic review negatives; no release acceptance."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import timeline_current_index_closure as old
import timeline_world_webgl_successor as gate
from timeline_world_mobile_release_successor import MOBILE_IMPLEMENTER_COMMITMENT
ROOT=Path(__file__).resolve().parents[1]
class WebglSuccessorTests(unittest.TestCase):
 def setUp(self):self.raw=(ROOT/gate.PAGE).read_bytes();self.current=old.tool_tree(ROOT)
 def test_exact_page_restore_and_mutations(self):
  restored=gate.restore_page(self.raw,ROOT);self.assertEqual(gate.sha(restored),gate.BEFORE);self.assertEqual(gate.restore_page(restored,ROOT),restored)
  for bad in (self.raw+b' ',self.raw[:-1]):
   with self.assertRaisesRegex(ValueError,'Unreviewed WebGL fallback page'):gate.restore_page(bad,ROOT)
  with patch.object(gate,'SOURCE_MANIFEST_SHA256','0'*64),self.assertRaisesRegex(ValueError,'source manifest changed'):gate.restore_page(self.raw,ROOT)
 def test_review_is_actually_pending(self):
  with patch.object(gate,'WEBGL_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'PENDING independent WebGL'):gate.validate_review(ROOT,self.current)
 def test_exact_prior_tree_and_mutations(self):
  self.assertEqual(old.canonical(gate.project_tree(ROOT,self.current)),gate.PRIOR_TREE)
  with self.assertRaisesRegex(ValueError,'WebGL historical tool tree differs'):gate.project_tree(ROOT,dict(self.current,**{'tools/unknown.py':'0'*64}))
  manifest=json.loads(gate.source(ROOT,gate.TREE_MANIFEST));name=next(iter(manifest['previous']));missing=dict(self.current);del missing[name]
  with self.assertRaisesRegex(ValueError,'projection path missing'):gate.project_tree(ROOT,missing)
  with patch.object(gate,'TREE_MANIFEST_SHA256','0'*64),self.assertRaisesRegex(ValueError,'tool-tree manifest changed'):gate.project_tree(ROOT,self.current)
 def test_synthetic_review_scope_and_mutations(self):
  fixture={'schema':'timeline-webgl-fallback-review-v1','scope':'webgl_source_test_and_tool_tree','verdict':'CONCUR_WITHIN_BOUNDED_CODE_SCOPE','reviewer_commitment':'1'*64,'implementer_commitment':MOBILE_IMPLEMENTER_COMMITMENT,'receipt_sha256':'2'*64,'source_review_receipt_sha256':'3'*64,'source_head':gate.SOURCE_HEAD,'page_before_sha256':gate.BEFORE,'page_after_sha256':gate.AFTER,'regression_test_sha256':gate.TEST_SHA256,'source_manifest_sha256':gate.SOURCE_MANIFEST_SHA256,'tree_manifest_sha256':gate.TREE_MANIFEST_SHA256,'previous_tool_tree_sha256':gate.PRIOR_TREE,'current_tool_tree_sha256':old.canonical(self.current)}
  original=gate.source
  def run(row,reviewer='1'*64):
   raw=json.dumps(row).encode()
   def read(root,name):return raw if name==gate.REVIEW else original(root,name)
   with patch.object(gate,'source',side_effect=read),patch.object(gate,'WEBGL_REVIEW_SHA256',gate.sha(raw)),patch.object(gate,'WEBGL_REVIEWER_COMMITMENT',reviewer),patch.object(gate,'WEBGL_RECEIPT_SHA256','2'*64),patch.object(gate,'WEBGL_SOURCE_RECEIPT_SHA256','3'*64):
    gate.validate_review(ROOT,self.current);return gate.project_reviewed_tree(ROOT,self.current)
  self.assertEqual(old.canonical(run(fixture)),gate.PRIOR_TREE)
  for key,value in [('verdict','RELEASE_APPROVED'),('source_review_receipt_sha256','0'*64),('page_after_sha256','0'*64),('regression_test_sha256','0'*64),('source_manifest_sha256','0'*64),('tree_manifest_sha256','0'*64),('current_tool_tree_sha256','0'*64)]:
   changed=copy.deepcopy(fixture);changed[key]=value
   with self.subTest(field=key),self.assertRaises(ValueError):run(changed)
  with self.assertRaisesRegex(ValueError,'reviewer must differ'):run(fixture,reviewer=MOBILE_IMPLEMENTER_COMMITMENT)
  with self.assertRaisesRegex(ValueError,'PENDING independent WebGL'):run(fixture,reviewer='invalid')
  def altered(root,name):
   data=original(root,name);return data+b' ' if name==gate.TEST else data
  with patch.object(gate,'source',side_effect=altered),self.assertRaisesRegex(ValueError,'source or regression changed'):gate.validate_review(ROOT,self.current)
if __name__=='__main__':unittest.main()
