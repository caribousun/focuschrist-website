"""Exact current-to-historical Watch record correspondence, not release."""
import hashlib,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import watch_search_historical_projection as p
ROOT=Path(__file__).resolve().parents[1]
class WatchSearchProjection(unittest.TestCase):
 def setUp(self):
  self.raw=(ROOT/'site-search-index.json').read_bytes()
 def test_exact_immutable_predecessor(self):
  # Sparse local test checks the index inverse; CI separately validates real
  # Watch artwork/source inputs and the actual full-tree producer.
  with patch('watch_current_source_qa.check_sources') as source_check:
   old=p.restore(self.raw,ROOT)
  source_check.assert_called_once_with(ROOT)
  expected=subprocess.check_output(['git','-C',str(ROOT),'show','4fb9e51deda2997d6974e80a5dce86a65167841c:site-search-index.json'])
  self.assertEqual(old,expected)
  a=json.loads(old);b=json.loads(self.raw)
  self.assertEqual(a['pages'],b['pages'])
  changed={x['url'] for x,y in zip(a['records'],b['records']) if x!=y}
  self.assertEqual(changed,p.CHANGED)
 def test_unknown_or_mutated_current_rejected(self):
  for raw in (self.raw+b' ',self.raw.replace(b'watch',b'watcx',1)):
   with patch('watch_current_source_qa.check_sources'),self.assertRaisesRegex(AssertionError,'Unknown current'):
    p.restore(raw,ROOT)
 def test_source_failure_not_swallowed(self):
  with patch('watch_current_source_qa.check_sources',side_effect=ValueError('source changed')),self.assertRaisesRegex(ValueError,'source changed'):
   p.restore(self.raw,ROOT)
 def test_manifest_failure_not_swallowed(self):
  with patch('watch_current_source_qa.check_sources'),patch.object(p,'MANIFEST_SHA','0'*64),self.assertRaisesRegex(AssertionError,'Changed Watch projection'):
   p.restore(self.raw,ROOT)
if __name__=='__main__':unittest.main()
