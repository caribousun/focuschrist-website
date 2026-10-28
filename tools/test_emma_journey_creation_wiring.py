"""Static/executed narrow branch checks; NOT a full site gate test."""
import ast,json,tempfile,textwrap,unittest
from pathlib import Path
from artwork_emma_story_delivery import require
import artwork_emma_journey_delivery as v
SOURCE=Path(__file__).with_name('artwork_creation_gate.py').read_text()
START='    # Exact current Emma journey generation.';END='    # Exact existing Adams chart import;'
BLOCK=textwrap.dedent(SOURCE[SOURCE.index(START):SOURCE.index(END)])
class Wiring(unittest.TestCase):
 def env(self,root,added):return {'root':root,'added':added,'covered':set(),'rejected':set(),'pixel_hash':lambda p:'','page_dependencies':lambda r,p:set(),'originals':set(),'original_pixels':set(),'require':require,'json':json}
 def test_triggered_with_missing_record_fails(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'record missing'):exec(BLOCK,self.env(Path(d),{next(iter(v.ASSETS))}))
 def test_present_record_without_actual_pin_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/v.MANIFEST;p.parent.mkdir(parents=True);p.write_text('{}')
   with self.assertRaisesRegex(ValueError,'pending'):exec(BLOCK,self.env(root,set(v.ASSETS)))
 def test_absent_family_does_not_touch_other_coverage(self):
  with tempfile.TemporaryDirectory() as d:
   e=self.env(Path(d),set());exec(BLOCK,e);self.assertEqual(e['journey'],set());self.assertEqual(e['covered'],set())
 def test_real_release_hold_and_aggregate_dedup_are_wired(self):
  ast.parse(SOURCE);self.assertIn('emma_journey_owner_release_gate(root, journey_record)',BLOCK);self.assertIn('journey_hashes & originals',BLOCK);self.assertIn('journey_pixels & original_pixels',BLOCK)
  self.assertIn("require(added == covered, 'New artwork missing exact review coverage",SOURCE);self.assertIn('or three or journey:',SOURCE)
if __name__=='__main__':unittest.main()
