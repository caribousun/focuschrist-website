"""The actual index and prior receipt are checked separately; no image approval."""
import hashlib, subprocess, unittest
from pathlib import Path
from unittest.mock import patch
import historical_generated_index_context as gate
ROOT=Path(__file__).resolve().parents[1]
ROWS={'art-gallery.json':'5fb9f428a7e4bbf63cd9b5721ca7e576b14bbfa8334c073343f84e49efb8fcb1',
      'site-search-index.json':'5744d3b23308c419732bac77811620c2ca68b30e4dc22a1eb0775a120ddbd103'}
class IndexContextTests(unittest.TestCase):
 def setUp(self):gate.historical_bytes.cache_clear()
 def test_both_actual_receipt_rows_and_current_indices(self):
  for name,pin in ROWS.items():self.assertTrue(gate.validate_context(ROOT,{'path':name,'sha256':pin}))
 def test_unknown_path_and_tampered_receipt_rejected(self):
  with self.assertRaises(ValueError):gate.validate_context(ROOT,{'path':'other.json','sha256':'0'*64})
  with self.assertRaisesRegex(ValueError,'historical receipt mismatch'):gate.validate_context(ROOT,{'path':'site-search-index.json','sha256':'0'*64})
 def test_missing_history_fails_closed(self):
  with patch.object(gate.subprocess,'check_output',side_effect=subprocess.CalledProcessError(1,'git')):
   with self.assertRaisesRegex(ValueError,'immutable source unavailable'):gate.validate_context(ROOT,{'path':'site-search-index.json','sha256':ROWS['site-search-index.json']})
 def test_current_invalid_json_and_old_bytes_mismatch_fail_closed(self):
  name='site-search-index.json';target=ROOT/name;original=Path.read_bytes
  def read(path):return b'{' if path==target else original(path)
  with patch.object(Path,'read_bytes',read):
   with self.assertRaisesRegex(ValueError,'Malformed current index'):gate.validate_context(ROOT,{'path':name,'sha256':ROWS[name]})
  gate.historical_bytes.cache_clear()
  with patch.object(gate.subprocess,'check_output',return_value=b'not historical'):
   with self.assertRaisesRegex(ValueError,'historical receipt mismatch'):gate.validate_context(ROOT,{'path':name,'sha256':ROWS[name]})
if __name__=='__main__':unittest.main()
