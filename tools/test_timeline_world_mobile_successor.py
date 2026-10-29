"""Mechanical source projection checks; no independent review implied."""
import copy,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import timeline_world_mobile_successor as mobile
import timeline_world_controls_successor as prior
ROOT=Path(__file__).resolve().parents[1]
class WorldMobileSuccessorTests(unittest.TestCase):
 def test_exact_page_and_controller_restore_prior_bytes(self):
  current=(ROOT/mobile.PAGE).read_bytes();self.assertEqual(hashlib.sha256(mobile.restore(current)).hexdigest(),mobile.BEFORE)
  self.assertEqual(hashlib.sha256(prior.restore(current)).hexdigest(),prior.BEFORE)
 def test_unknown_page_controller_and_manifest_fail_closed(self):
  current=(ROOT/mobile.PAGE).read_bytes()
  for bad in (current+b' ',current[:-1],current[:20]+b'X'+current[21:]):
   with self.subTest(length=len(bad)),self.assertRaises(AssertionError):mobile.restore(bad)
  with patch.object(mobile,'MANIFEST_SHA','0'*64),self.assertRaisesRegex(AssertionError,'manifest changed'):mobile.restore(current)
  original=mobile.source
  def changed(root,name):
   data=original(root,name)
   return data+b' ' if name==mobile.CONTROLLER else data
  with patch.object(mobile,'source',side_effect=changed),self.assertRaisesRegex(AssertionError,'controller changed'):mobile.restore(current)
 def test_albert_wording_review_is_exact_and_does_not_claim_render_acceptance(self):
  review=mobile.validate_albert_content_review()
  self.assertEqual(review['verdict'],'CONCUR_UI_WORDING_AND_TARGET_SCOPE_ONLY')
  self.assertIn('not_render_acceptance',review['limits'])
  with patch.object(mobile,'ALBERT_CONTENT_REVIEW_SHA','0'*64),self.assertRaisesRegex(AssertionError,'review changed'):
   mobile.validate_albert_content_review()
 def test_actual_newton_visual_review_retains_its_limits(self):
  review=mobile.validate_newton_visual_review()
  self.assertEqual(review['candidate']['head'],'4680e7f9271aa6f85c0509af447e5245d3245555')
  self.assertTrue(any('not personally rerun' in x for x in review['limitations']))
  self.assertTrue(any('no like-for-like baseline' in x for x in review['limitations']))
  with patch.object(mobile,'NEWTON_VISUAL_REVIEW_SHA',None),self.assertRaisesRegex(AssertionError,'review changed'):
   mobile.validate_newton_visual_review()
 def test_newton_receipt_scope_and_subject_mutations_fail_closed(self):
  original=mobile.source;review=mobile.validate_newton_visual_review()
  for change in ('actor','head','page','test','artifact','conclusion','limitation','verdict'):
   row=copy.deepcopy(review)
   if change=='actor':row['reviewer_role']='other'
   if change=='head':row['candidate']['head']='0'*40
   if change=='page':row['candidate']['page_sha256']='0'*64
   if change=='test':row['candidate']['browser_test_sha256']='0'*64
   if change=='artifact':row['hosted_evidence']['artifact_sha256']='0'*64
   if change=='conclusion':row['hosted_evidence']['timeline_job_conclusion']='failure'
   if change=='limitation':row['limitations'].pop()
   if change=='verdict':row['verdict']='release approved'
   altered=json.dumps(row,ensure_ascii=False).encode()
   def use_altered(root,name):return altered if name==mobile.NEWTON_VISUAL_REVIEW else original(root,name)
   with self.subTest(change=change),patch.object(mobile,'source',side_effect=use_altered),patch.object(mobile,'NEWTON_VISUAL_REVIEW_SHA',mobile.sha(altered)),self.assertRaises(AssertionError):
    mobile.validate_newton_visual_review()
  def changed_test(root,name):
   data=original(root,name);return data+b' ' if name==mobile.BROWSER_TEST else data
  with patch.object(mobile,'source',side_effect=changed_test),self.assertRaisesRegex(AssertionError,'browser test changed'):
   mobile.validate_newton_visual_review()
if __name__=='__main__':unittest.main()
