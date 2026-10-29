"""Exact-source, receipt and preservation tests; not a provider or browser test."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import timeline_world_tooltip_visual_successor as gate
import timeline_world_mobile_successor as mobile
ROOT=Path(__file__).resolve().parents[1]
class TooltipVisualSuccessorTests(unittest.TestCase):
 def test_actual_receipt_and_predecessors(self):
  result=gate.validate_visual_review();self.assertEqual(gate.sha(result['previous_sources'][mobile.PAGE]),mobile.AFTER);self.assertEqual(gate.sha(result['previous_sources'][mobile.BROWSER_TEST]),mobile.BROWSER_TEST_SHA)
  self.assertIn('not release or owner approval',result['review']['verdict'])
 def test_resize_test_successor_reconstructs_exact_reviewed_bytes(self):
  current=mobile.source(ROOT,mobile.BROWSER_TEST)
  self.assertEqual(gate.sha(current),gate.RESIZE_TEST_AFTER)
  old=gate.restore_browser_test(current,ROOT);self.assertEqual(gate.sha(old),gate.TEST_AFTER)
  self.assertEqual(gate.restore_browser_test(old,ROOT),old)
  with patch.object(gate,'sha',return_value=mobile.BROWSER_TEST_SHA):self.assertEqual(gate.restore_browser_test(b'historical fixture',ROOT),b'historical fixture')
  for bad in (current+b' ',current[:-1]):
   with self.assertRaisesRegex(ValueError,'Unreviewed tooltip source'):gate.restore_browser_test(bad,ROOT)
  with patch.object(gate,'RESIZE_TEST_MANIFEST_SHA','0'*64),self.assertRaisesRegex(ValueError,'Changed resize test manifest'):gate.restore_browser_test(current,ROOT)
 def test_changed_sources_are_rejected(self):
  original=mobile.source
  for target in (mobile.PAGE,mobile.BROWSER_TEST,mobile.CONTROLLER,gate.MANIFEST,gate.REVIEW):
   def altered(root,name):
    raw=original(root,name)
    return raw+b' ' if name==target else raw
   with self.subTest(target=target),patch.object(mobile,'source',side_effect=altered),self.assertRaises(ValueError):gate.validate_visual_review()
 def test_receipt_scope_and_subject_are_bound_even_with_patched_digest(self):
  original=mobile.source;receipt=json.loads(original(ROOT,gate.REVIEW))
  changes=[('verdict','release approved'),('reviewer_role','other')]
  for field,value in changes:
   record=dict(receipt,**{field:value});raw=json.dumps(record).encode()
   def altered(root,name):return raw if name==gate.REVIEW else original(root,name)
   with self.subTest(field=field),patch.object(mobile,'source',side_effect=altered),patch.object(gate,'REVIEW_SHA',gate.sha(raw)),self.assertRaises(ValueError):gate.validate_visual_review()
 def test_actual_standalone_code_review_and_mutation(self):
  review=gate.validate_code_review()['code_review'];self.assertEqual(review['scope'],'tooltip_source_delta_and_standalone_visual_successor')
  original=mobile.source
  def altered(root,name):
   raw=original(root,name)
   return raw+b' ' if name==gate.CODE_REVIEW else raw
  with patch.object(mobile,'source',side_effect=altered),self.assertRaisesRegex(ValueError,'Tooltip code review changed'):gate.validate_code_review()
  with patch('timeline_world_mobile_release_successor.MOBILE_IMPLEMENTER_COMMITMENT',review['reviewer_commitment']),self.assertRaisesRegex(ValueError,'must differ from implementer'):gate.validate_code_review()
  for invalid in (None,'','not-a-hash','A'*64,'0'*63):
   with self.subTest(implementer=invalid),patch('timeline_world_mobile_release_successor.MOBILE_IMPLEMENTER_COMMITMENT',invalid),self.assertRaisesRegex(ValueError,'valid commitment'):gate.validate_code_review()
  receipt=json.loads(original(ROOT,gate.REVIEW))
  for field in ('candidate','hosted_evidence','limits'):
   record=copy.deepcopy(receipt)
   if field=='candidate':record[field]['page_sha256']='0'*64
   elif field=='hosted_evidence':record[field]['timeline_job_conclusion']='failure'
   else:record[field]=[]
   raw=json.dumps(record).encode()
   def altered(root,name):return raw if name==gate.REVIEW else original(root,name)
   with self.subTest(field=field),patch.object(mobile,'source',side_effect=altered),patch.object(gate,'REVIEW_SHA',gate.sha(raw)),self.assertRaises(ValueError):gate.validate_visual_review()
if __name__=='__main__':unittest.main()
