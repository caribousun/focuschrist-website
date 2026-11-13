import tempfile
import unittest
from pathlib import Path
import hashlib
import search_historical_compatibility as compat
ROOT=Path(__file__).resolve().parents[1]
class SearchCompatibilityTests(unittest.TestCase):
 def setUp(self):
  self.root=Path(self.enterContext(tempfile.TemporaryDirectory()))
  for name in (*compat.DEPENDENCIES,'search.html','answer-bank-data.js'):
   (self.root/name).write_bytes((ROOT/name).read_bytes())
 def test_exact_current_projection(self):
  self.assertEqual(hashlib.sha256(compat.project(self.root)).hexdigest(),compat.HISTORICAL_SHA)
 def test_wrong_bank_data(self):
  with (self.root/'answer-bank-data.js').open('ab') as f:f.write(b' ')
  with self.assertRaisesRegex(ValueError,'cache mismatch'):compat.project(self.root)
 def test_second_html_edit(self):
  with (self.root/'search.html').open('ab') as f:f.write(b' ')
  with self.assertRaisesRegex(ValueError,'Unrelated'):compat.project(self.root)
 def test_duplicate_block(self):
  p=self.root/'search.html';raw=p.read_bytes();p.write_bytes(raw+compat.CURRENT.search(raw).group())
  with self.assertRaisesRegex(ValueError,'exactly one'):compat.project(self.root)
 def test_dependency_change(self):
  with (self.root/'site-search.js').open('ab') as f:f.write(b' ')
  with self.assertRaisesRegex(ValueError,'dependency drift'):compat.project(self.root)
 def test_wrong_script_name(self):
  p=self.root/'search.html';p.write_bytes(p.read_bytes().replace(b'answer-bank-guards.js',b'answer-bank-other.js'))
  with self.assertRaisesRegex(ValueError,'exactly one'):compat.project(self.root)
 def test_wrong_script_order(self):
  p=self.root/'search.html';raw=p.read_bytes();a=b'<script src="answer-bank-matcher.js?v=20261023-answer-bank-1" defer></script>';b=b'<script src="answer-bank-guards.js?v=20261023-answer-bank-1" defer></script>';self.assertEqual(raw.count(a+b),1);p.write_bytes(raw.replace(a+b,b+a))
  with self.assertRaisesRegex(ValueError,'exactly one'):compat.project(self.root)
if __name__=='__main__':unittest.main()
