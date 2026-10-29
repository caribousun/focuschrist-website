"""Mechanical source projection checks; no independent review implied."""
import hashlib,unittest
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
if __name__=='__main__':unittest.main()
