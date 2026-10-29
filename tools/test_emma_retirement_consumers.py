"""Current four-owner successor tests; predecessor suite is run separately.

Requires the actual full checkout, BeautifulSoup and reviewed successor wiring.
It does not confer independent source/artwork/owner approval.
"""
import copy,hashlib,unittest
from pathlib import Path
from unittest import mock
from bs4 import BeautifulSoup
import emma_story_consumers as prior
import emma_retirement_consumers_successor as successor
import illustrated_study_navigation_qa as illustrated
ROOT=Path(__file__).resolve().parents[1]

class ActualCurrentStories(unittest.TestCase):
 def test_four_exact_current_sources_and_unchanged_opening(self):
  self.assertEqual(len(successor.CURRENT),4);self.assertNotIn(successor.RETIRED,successor.CURRENT)
  for route in successor.CURRENT:
   raw=(ROOT/route).read_bytes();text=(ROOT/route).read_text(encoding='utf8');doc=BeautifulSoup(text,'html.parser')
   successor.assert_story_opening(route,text,doc,raw,prior.assert_story_opening)
   self.assertEqual(hashlib.sha256(raw).hexdigest(),successor.SOURCE_HASH[route])
   with self.assertRaises(AssertionError):successor.assert_story_opening(route,text,doc,raw+b' ',prior.assert_story_opening)
  with self.assertRaises(AssertionError):successor.assert_story_opening(successor.RETIRED,'',BeautifulSoup('','html.parser'),b'',prior.assert_story_opening)
 def test_four_partition_and_unknown_never_erased(self):
  bindings={route:['ref'] for route in successor.CURRENT};bindings['historical.html']=['older']
  self.assertEqual(successor.current_consumers(bindings,['ref']),{'historical.html':['older']})
  for route in successor.CURRENT:
   changed=copy.deepcopy(bindings);del changed[route];self.assertIsNone(successor.current_consumers(changed,['ref']))
   changed=copy.deepcopy(bindings);changed[route]=['ref','ref'];self.assertIsNone(successor.current_consumers(changed,['ref']))
  changed=dict(bindings,**{successor.RETIRED:['ref']});self.assertIsNone(successor.current_consumers(changed,['ref']))
  unknown=dict(bindings,**{'history/unknown.html':['ref']});self.assertIn('history/unknown.html',successor.current_consumers(unknown,['ref']))

class ActualControllerBindings(unittest.TestCase):
 def test_historical_registry_then_exact_124_live(self):
  previous=illustrated.current_controller_bindings();self.assertEqual(len(previous),125)
  retired=successor.RETIRED;self.assertIn(retired,previous)
  live=dict(previous);del live[retired];self.assertEqual(len(live),124)
  illustrated.assert_controller_bindings(live)
  for mutation in [previous,dict(live,**{'history/unknown.html':[illustrated.CONTROLLER_REF]})]:
   with self.assertRaises(AssertionError):illustrated.assert_controller_bindings(mutation)
  for owner in successor.CURRENT:
   for replacement in (None,[],[illustrated.CONTROLLER_REF,illustrated.CONTROLLER_REF],['unknown']):
    changed=copy.deepcopy(live)
    if replacement is None:del changed[owner]
    else:changed[owner]=replacement
    with self.assertRaises(AssertionError):illustrated.assert_controller_bindings(changed)
  unrelated=next(k for k in live if k not in successor.CURRENT)
  changed=copy.deepcopy(live);changed[unrelated]=['unknown']
  with self.assertRaises(AssertionError):illustrated.assert_controller_bindings(changed)
  # This patches only readback to simulate tampering; no repository file writes.
  original=Path.read_bytes
  def changed(path):
   value=original(path)
   return value+b'x' if path==ROOT/retired else value
  with mock.patch.object(Path,'read_bytes',changed),self.assertRaises(AssertionError):illustrated.assert_controller_bindings(live)
if __name__=='__main__':unittest.main()
