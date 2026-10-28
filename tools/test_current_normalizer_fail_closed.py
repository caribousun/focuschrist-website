"""Unknown bytes and unknown paths must never receive historical normalization."""
import unittest
from pathlib import Path
import timeline_source_import as gate
from artwork_display_delivery import inverse
ROOT=Path(__file__).resolve().parents[1]
class CurrentNormalizerSafety(unittest.TestCase):
 def test_unknown_consumer_bytes_and_paths_stay_unchanged(self):
  payload=b'unreviewed unique bytes, not a historical source\n'
  for name in gate.REVIEWED_CONSUMER_INVERSES:
   with self.subTest(name=name):
    self.assertEqual(gate.restore_consumers(name,payload),payload)
    self.assertEqual(gate.restore_consumers('unknown/'+name,payload),payload)
    path=ROOT/name
    if path.is_file():
     bad=path.read_bytes()+b'\n# unreviewed bytes'
     self.assertEqual(gate.restore_consumers(name,bad),bad)
 def test_unknown_code_bytes_and_paths_stay_unchanged(self):
  payload=b'unreviewed unique code, not a historical source\n'
  for name in gate.REVIEWED_CODE_INVERSES:
   with self.subTest(name=name):
    self.assertEqual(gate.restore_code_evidence(name,payload),payload)
    self.assertEqual(gate.restore_code_evidence('unknown/'+name,payload),payload)
    path=ROOT/name
    if path.is_file():
     bad=path.read_bytes()+b'\n# unreviewed bytes'
     self.assertEqual(gate.restore_code_evidence(name,bad),bad)
 def test_unknown_index_inverses_and_paths_stay_unchanged(self):
  import adams_delivery_successor, adams_integration_indices, emma_generated_indices_successor
  payload=b'unreviewed index bytes, not a historical source\n'
  for module in (adams_delivery_successor, adams_integration_indices, emma_generated_indices_successor):
   for name in module.AFTER:
    with self.subTest(module=module.__name__,name=name):
     self.assertEqual(module.restore(name,payload),payload)
     self.assertEqual(module.restore('unknown/'+name,payload),payload)
 def test_unknown_gallery_builder_bytes_stay_unchanged(self):
  name='tools/build_art_gallery.py';bad=(ROOT/name).read_bytes()+b'\n# unreviewed bytes'
  self.assertEqual(gate.before_current_gallery_builder(name,bad),bad)
  self.assertEqual(inverse(name,bad),bad)
  actual=(ROOT/name).read_bytes();wrong='other/build_art_gallery.py'
  self.assertEqual(gate.before_current_gallery_builder(wrong,actual),actual)
  self.assertEqual(inverse(wrong,actual),actual)
if __name__=='__main__':unittest.main()
