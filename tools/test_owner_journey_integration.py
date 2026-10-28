"""Exact Emma source successor integration; excludes rendered and release review."""
import shutil,tempfile,unittest
from pathlib import Path
import owner_integration_contract as current
import owner_journey_successor as successor
ROOT=Path(__file__).resolve().parents[1]
class CurrentOwnerJourney(unittest.TestCase):
 def test_exact_current_and_explicit_historical_inverse(self):
  for route in (successor.HUB,successor.RETIRED,successor.HYMNS):
   raw=(ROOT/route).read_bytes();result=current.validate_file(route,raw,ROOT);self.assertEqual(result['sha256'],successor.sha(raw))
   old=current.historical_bytes(route,raw,ROOT);self.assertEqual(successor.sha(old),current.manifest(ROOT)['files'][route]['historical']['sha256'])
   with self.assertRaises(AssertionError):current.validate_file(route,raw+b' ',ROOT)
   with self.assertRaises(AssertionError):current.historical_bytes(route,raw+b' ',ROOT)
 def test_new_canonical_set_and_exact_assets(self):
  routes=successor.validate_canonical((ROOT/'sitemap.xml').read_bytes());self.assertEqual(len(routes),138);self.assertNotIn(successor.RETIRED,routes);self.assertEqual(successor.validate_assets(ROOT),33)
  before=successor.historical_routes((ROOT/'sitemap.xml').read_bytes());self.assertIn(successor.RETIRED,before);self.assertEqual(set(before)-set(routes),{successor.RETIRED})
 def test_missing_or_tampered_asset_fails(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);shutil.copytree(ROOT/'assets/page-art/emma-journey',root/'assets/page-art/emma-journey')
   f=root/'assets/page-art/emma-journey/emma-journey-origin-960.webp';f.write_bytes(f.read_bytes()+b'x')
   with self.assertRaises(AssertionError):successor.validate_assets(root)
   f.unlink()
   with self.assertRaises(AssertionError):successor.validate_assets(root)
 def test_figure_hidden_by_disclosure_or_hidden_ancestor_rejected(self):
  # Bypass only the exact-byte pin to exercise this structural negative.
  # Neither a mock nor this source check establishes rendered visibility.
  from unittest.mock import patch
  raw=(ROOT/successor.HUB).read_bytes();fig=successor.figure_bytes(raw,'emma-journey-07')
  marker=b'</details>\n'+fig;self.assertEqual(raw.count(marker),1)
  mutations=[raw.replace(marker,fig+b'\n</details>',1),
             raw.replace(fig,b'<div hidden>'+fig+b'</div>',1),
             raw.replace(fig,b'<div aria-hidden="true">'+fig+b'</div>',1)]
  for changed in mutations:
   with self.subTest(changed=changed[:20]),patch.object(successor,'current_file',return_value={}),self.assertRaisesRegex(AssertionError,'figure hidden by ancestor'):
    successor.validate_hub(changed,ROOT)
 def test_no_release_claim(self):
  with self.assertRaisesRegex(AssertionError,'PENDING'):successor.release_gate()
if __name__=='__main__':unittest.main()
