"""Synthetic contract wiring; no historical review or release is fabricated."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
import artwork_emma_journey_retained as r
import artwork_emma_story_delivery as story
import artwork_emma_hub_delivery as old

class CurrentScope(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.routes=[r.journey.HUB,*sorted(set(r.STORIES)-{r.journey.RETIRED}),'other.html']
  self.expected=r.journey.OLD|r.journey.NEW|{r.journey.ORIGIN}
  for route in [*self.routes,'sitemap.xml',r.journey.RETIRED]:
   p=self.root/route;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<html></html>')
  hub=self.root/r.journey.HUB
  hub.write_text('<html>'+''.join('<figure data-exclusive-artwork="'+k+'"></figure>' for k in sorted(self.expected))+'</html>')
  for name,value in [('validate_canonical',lambda b:self.routes),('validate_hub',lambda *a:None),('validate_redirect',lambda *a:None),('validate_hymns',lambda *a:None)]:
   p=patch.object(r.journey,name,value);p.start();self.addCleanup(p.stop)
  for name in ('validate_file','assert_emma_semantics'):
   p=patch.object(r,name,lambda *a:None);p.start();self.addCleanup(p.stop)
 def run_current(self):return r.validate_current(self.root)
 def test_exact_current_census(self):self.assertEqual(self.run_current(),self.routes)
 def test_missing_duplicate_wrong_element_and_offsite_owner(self):
  hub=self.root/r.journey.HUB;before=hub.read_text();key=next(iter(self.expected));piece='<figure data-exclusive-artwork="'+key+'"></figure>'
  for changed in (before.replace(piece,''),before.replace(piece,piece+piece),before.replace(piece,piece.replace('figure','div'))):
   hub.write_text(changed)
   with self.assertRaisesRegex(ValueError,'ownership|owner element'):self.run_current()
  hub.write_text(before);(self.root/'other.html').write_text(piece)
  with self.assertRaisesRegex(ValueError,'duplicate'):self.run_current()
 def test_historical_validation_only_follows_current(self):
  sentinel=object();hp=Mock(return_value=sentinel)
  with patch.object(r,'validate_current',side_effect=ValueError('bad current')),patch.object(old,'validate_explicit_historical',hp):
   with self.assertRaisesRegex(ValueError,'bad current'):r.validate(self.root,{},set(),set(),set(),None,None,None)
   hp.assert_not_called()
  with patch.object(r,'validate_current'),patch.object(r.journey,'historical_fixture',side_effect=lambda route,raw,root:route.encode()),patch.object(old,'validate_explicit_historical',hp):
   self.assertIs(r.validate(self.root,{},set(),set(),set(),None,None,None),sentinel)
   prior=hp.call_args.args[-1];self.assertEqual(set(prior),{r.journey.HUB,r.journey.RETIRED,r.journey.HYMNS})
 def test_historical_requires_exact_known_three_and_real_receipt_checks(self):
  with self.assertRaisesRegex(ValueError,'incomplete'):old.validate_explicit_historical(self.root,{},set(),set(),set(),None,None,None,{})
  prior={x:b'prior' for x in (r.journey.HUB,r.journey.RETIRED,r.journey.HYMNS)}
  with patch.object(r,'validate_current',side_effect=ValueError('bad current')),patch.object(old,'require_finished') as finished:
   with self.assertRaisesRegex(ValueError,'bad current'):old.validate_explicit_historical(self.root,{},set(),set(),set(),None,None,None,prior)
   finished.assert_not_called()
  with patch.object(r,'validate_current'),patch.object(old,'require_finished',side_effect=ValueError('record pin')):
   with self.assertRaisesRegex(ValueError,'record pin'):old.validate_explicit_historical(self.root,{},set(),set(),set(),None,None,None,prior)

class Dispatch(unittest.TestCase):
 def test_only_exact_current_hub_uses_successor(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);p=root/r.journey.HUB;p.parent.mkdir(parents=True);p.write_bytes(b'new')
   manifest={'files':{r.journey.HUB:{'current_sha256':story.sha(b'new')}}}
   new=Mock(return_value='current');pre=Mock(return_value='predecessor')
   with patch.object(r.journey,'read_manifest',return_value=manifest),patch.object(r,'validate',new),patch.object(old,'validate',pre):
    self.assertEqual(story.validate(root,{'schema':2},set(),set(),set(),None,None),'current');self.assertEqual(new.call_count,1)
    p.write_bytes(b'unknown');self.assertEqual(story.validate(root,{'schema':2},set(),set(),set(),None,None),'predecessor');self.assertEqual(pre.call_count,1)
class ActualSourceHistoricalComposition(unittest.TestCase):
 """Real source and record bindings; CSS/non-HTML evidence intentionally mocked."""
 def test_exact_predecessor_record_and_six_source_endpoints(self):
  import json
  root=Path(__file__).resolve().parents[1]
  record=json.loads((root/'docs/emma-story-artwork-import/delivery.json').read_bytes())
  predecessor=json.loads((root/old.PREDECESSOR_PATH).read_bytes())
  self.assertEqual(old.canonical(record),old.APPROVED_RECORD_SHA256)
  self.assertEqual(old.canonical(predecessor),old.PREDECESSOR_CANONICAL)
  prior={route:r.journey.historical_fixture(route,(root/route).read_bytes(),root)
         for route in (r.journey.HUB,r.journey.RETIRED,r.journey.HYMNS)}
  real_bound=old.bound
  def source_bound(root,item):
   if item['path'].endswith('.html'):return real_bound(root,item)
   return b'MOCKED NON-HTML CONTEXT; NOT A RECEIPT CHECK'
  # Check actual six historical source bindings and inverses, but deliberately
  # do not claim validation of CSS dependencies, real old artwork or reviews.
  with patch.object(old,'bound',side_effect=source_bound):
   pages=old.check_spec(root,record['spec'],predecessor,lambda _root,route:{route},prior)
   self.assertEqual(set(pages),set(r.STORIES))
   bad=dict(prior);bad[r.journey.HUB]+=b' '
   with self.assertRaisesRegex(ValueError,'historical hub source'):
    old.check_spec(root,record['spec'],predecessor,lambda _root,route:{route},bad)

if __name__=='__main__':unittest.main()
