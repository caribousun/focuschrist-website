"""Exact standalone review and unknown panel discovery regressions."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import section_panel_surface_qa as q
class StandaloneTests(unittest.TestCase):
 def test_reviewed_bytes(self):q.assert_standalone(q.STANDALONE_ROUTE,(q.ROOT/q.STANDALONE_ROUTE).read_bytes())
 def test_unknown_route(self):
  with self.assertRaisesRegex(AssertionError,'Unknown standalone'):q.assert_standalone('other.html',(q.ROOT/q.STANDALONE_ROUTE).read_bytes())
 def test_unknown_bytes(self):
  data=(q.ROOT/q.STANDALONE_ROUTE).read_bytes()
  for value in (data+b' ',data.replace(b'class="topsec"',b'class="changed"',1)):
   with self.assertRaisesRegex(AssertionError,'binding drift'):q.assert_standalone(q.STANDALONE_ROUTE,value)
 def test_unknown_panel_fails_closed(self):
  config=json.loads(q.CONFIG.read_text(encoding='utf-8'))
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'fixture.html').write_text('<div class="new-study-panel">x</div>',encoding='utf-8')
   with patch.object(q,'ROOT',root),patch.object(q,'canonical',return_value=['fixture.html']):
    with self.assertRaisesRegex(AssertionError,'Unclassified panel-like class: new-study-panel'):q.inventory(config)
 def test_each_new_class_requires_explicit_classification(self):
  config=json.loads(q.CONFIG.read_text(encoding='utf-8'))
  for name in ('panelsub','cards','mapnote'):
   changed=copy.deepcopy(config);del changed['excluded_classes'][name]
   with self.assertRaisesRegex(AssertionError,'Unclassified panel-like class: '+name):q.inventory(changed)
class ReviewedTimelineStyleTests(unittest.TestCase):
 def test_exact_styles_and_unknown_mutations(self):
  import sitewide_artwork_review_qa as a
  for name,fn in [('timeline.css',a.reviewed_scoped_interface_style),('timeline-experiences.css',a.reviewed_owner_20260929_style)]:
   data=(q.ROOT/name).read_bytes()
   self.assertTrue(fn(name,data))
   for altered in (data+b' ',data.replace(b'16px',b'17px',1),data.replace(b'transparent',b'purple',1)):
    if altered!=data:self.assertFalse(fn(name,altered))
if __name__=='__main__':unittest.main()
