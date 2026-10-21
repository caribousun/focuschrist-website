"""Exact navigation correction predecessors; historical source pins stay intact."""
import hashlib,unittest
from pathlib import Path
import timeline_source_import as t
class NavigationBindings(unittest.TestCase):
 def test_exact_predecessors_and_unknown_edits(self):
  root=Path(__file__).resolve().parents[1]
  for name,binding in t.POLISH_CONSUMER_INVERSES.items():
   raw=(root/name).read_bytes();prior=t.before_navigation_polish(name,raw)
   self.assertEqual(hashlib.sha256(prior).hexdigest(),binding['previous'])
   self.assertNotEqual(raw,prior)
   for altered in [raw+b' ',raw.replace(b'12px',b'13px',1),raw.replace(b'navigation-polish-1',b'unreviewed-1',1)]:
    if altered!=raw:self.assertEqual(t.before_navigation_polish(name,altered),altered)
   self.assertEqual(t.before_navigation_polish('unknown/'+name,raw),raw)
 def test_composition_retains_older_pins(self):
  root=Path(__file__).resolve().parents[1]
  for name in t.POLISH_CONSUMER_INVERSES:
   actual=t.restore_consumers(name,(root/name).read_bytes())
   self.assertEqual(hashlib.sha256(actual).hexdigest(),t.REVIEWED_CONSUMER_INVERSES[name]['previous'])
if __name__=='__main__':unittest.main()
