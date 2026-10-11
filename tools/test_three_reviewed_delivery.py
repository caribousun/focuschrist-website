import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import artwork_three_reviewed_delivery as target
from artwork_creation_gate import pixel_hash,page_dependencies
class ExactThree(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.record=json.loads((ROOT/'docs/artwork-three-reviewed-delivery-reviews.json').read_bytes())
  cls.assets={a['path']for s in cls.record['spec']['scenes']for a in s['assets']}
 def check(self,r=None,binding=None,covered=None):
  r=r or self.record
  return target.validate(ROOT,r,binding or target.canonical(r),self.assets,covered or set(),set(),pixel_hash,page_dependencies)
 def test_actual_reviewed_packet(self):self.assertEqual(self.check()[0],self.assets)
 def test_unknown_record_rejected(self):
  with self.assertRaisesRegex(ValueError,'unreviewed record'):self.check(binding='0'*64)
 def test_false_owner_acceptance_rejected(self):
  r=copy.deepcopy(self.record);r['spec']['owner_final_image_acceptance']='accepted'
  with self.assertRaisesRegex(ValueError,'invented owner'):self.check(r)
 def test_extra_family_rejected(self):
  r=copy.deepcopy(self.record);r['spec']['scenes'].append(copy.deepcopy(r['spec']['scenes'][0]))
  with self.assertRaisesRegex(ValueError,'family expansion'):self.check(r)
 def test_wrong_source_rejected(self):
  r=copy.deepcopy(self.record);r['spec']['scenes'][0]['source_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'wrong source'):self.check(r)
 def test_missing_derivative_rejected(self):
  r=copy.deepcopy(self.record);r['spec']['scenes'][0]['assets'].pop()
  with self.assertRaisesRegex(ValueError,'asset expansion'):self.check(r)
 def test_wrong_dimensions_rejected(self):
  r=copy.deepcopy(self.record);r['spec']['scenes'][0]['assets'][0]['width']+=1
  with self.assertRaisesRegex(ValueError,'dimensions drift'):self.check(r)
 def test_duplicate_asset_coverage_rejected(self):
  with self.assertRaisesRegex(ValueError,'coverage overlap'):self.check(covered=self.assets)
 def test_missing_current_review_rejected(self):
  r=copy.deepcopy(self.record);r['reviews'].pop()
  with self.assertRaisesRegex(ValueError,'three current reviews'):self.check(r)
if __name__=='__main__':unittest.main(verbosity=2)
