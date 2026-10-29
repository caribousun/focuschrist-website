"""Exact ledger reconstruction and rejection tests; not current-review evidence."""
import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import timeline_content_ledger_successor as gate

class ContentLedgerSuccessorTests(unittest.TestCase):
 def setUp(self):self.raw=gate.source(gate.ROOT,'content-audit.json')
 def test_current_to_exact_historical(self):self.assertEqual(gate.sha(gate.restore(self.raw)),gate.BEFORE)
 def test_modified_ledger_and_review_rejected(self):
  with self.assertRaisesRegex(AssertionError,'current content ledger'):gate.restore(self.raw+b' ')
  source=gate.source
  with patch.object(gate,'source',side_effect=lambda root,name:source(root,name)+(b' ' if name==gate.REVIEW else b'')):
   with self.assertRaisesRegex(AssertionError,'content review'):gate.restore(self.raw)
 def test_changed_source_rejected(self):
  source=gate.source
  for name in gate.ROUTES:
   with self.subTest(name=name),patch.object(gate,'source',side_effect=lambda root,n:source(root,n)+(b' ' if n==name else b'')):
    with self.assertRaisesRegex(AssertionError,'source changed'):gate.restore(self.raw)
 def test_owner_census_binds_exact_old_image_links_and_rejects_tampering(self):
  import artwork_owner_closure as closure
  import artwork_gabriel_owner_delivery as gabriel
  import timeline_image_links_successor as images
  current=gate.source(gate.ROOT,'timeline-images.js')
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);path=root/'timeline-images.js';path.write_bytes(current)
   from timeline_51_source_successor import MANIFEST
   manifest=root/MANIFEST;manifest.parent.mkdir(parents=True);manifest.write_bytes((gate.ROOT/MANIFEST).read_bytes())
   item={'path':'timeline-images.js','sha256':images.BEFORE}
   self.assertEqual(closure.bound(root,item),path)
   self.assertEqual(gabriel.digest(path),images.BEFORE)
   path.write_bytes(current+b' ')
   with self.assertRaisesRegex(ValueError,'Stale closure hash'):closure.bound(root,item)
   self.assertNotEqual(gabriel.digest(path),images.BEFORE)
 def test_adams_historical_source_binding_restores_exact_predecessor(self):
  import adams_source_import_v9 as adams
  import timeline_adams_diagnostic_successor as successor
  current=gate.source(gate.ROOT,'timelines/adams-1881-chart.html')
  item={'path':'timelines/adams-1881-chart.html','bytes':66076,'sha256':successor.BEFORE}
  self.assertEqual(gate.sha(adams.bound(gate.ROOT,item)),successor.BEFORE)
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);path=root/item['path'];path.parent.mkdir();path.write_bytes(current+b' ')
   with self.assertRaises(ValueError):adams.bound(root,item)
if __name__=='__main__':unittest.main()
