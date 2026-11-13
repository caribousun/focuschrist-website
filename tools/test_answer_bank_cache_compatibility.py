"""Cache-only projection must never absorb unrelated HTML or bank drift."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import answer_bank_cache_compatibility as adapter

class CacheCompatibilityTests(unittest.TestCase):
 def setUp(self):
  self.temp=self.enterContext(tempfile.TemporaryDirectory());self.root=Path(self.temp)
  self.bank=(adapter.ROOT/'answer-bank-data.js').read_bytes();(self.root/'answer-bank-data.js').write_bytes(self.bank)
  self.tag=b'<script src="answer-bank-data.js?v=20261112-answer-bank-'+hashlib.sha256(self.bank).hexdigest()[:8].encode()+b'" defer></script>'
  for name,pin in adapter.HISTORICAL_HTML.items():
   raw=subprocess.check_output(['git','-C',str(adapter.ROOT),'show',adapter.HISTORICAL_COMMIT+':'+name])
   self.assertEqual(adapter.sha(raw),pin);self.assertEqual(raw.count(adapter.OLD_TAG),1)
   (self.root/name).write_bytes(raw.replace(adapter.OLD_TAG,self.tag))
 def test_actual_bank_and_exact_historical_html(self):
  r=adapter.validate_current(self.root);self.assertEqual(r['bank_sha256'],adapter.sha(self.bank))
  for name,item in r['pages'].items():self.assertEqual(adapter.sha(item['historical_bytes']),adapter.HISTORICAL_HTML[name])
 def test_wrong_token_rejected(self):
  p=self.root/'ask.html';p.write_bytes(p.read_bytes().replace(self.tag,self.tag.replace(adapter.sha(self.bank)[:8].encode(),b'00000000')))
  with self.assertRaisesRegex(ValueError,'does not match'):adapter.validate_current(self.root)
 def test_changed_data_with_old_token_rejected(self):
  (self.root/'answer-bank-data.js').write_bytes(self.bank+b' ')
  with self.assertRaisesRegex(ValueError,'does not match'):adapter.validate_current(self.root)
 def test_duplicate_loader_rejected(self):
  p=self.root/'ask.html';p.write_bytes(p.read_bytes()+self.tag)
  with self.assertRaisesRegex(ValueError,'Exactly one'):adapter.validate_current(self.root)
 def test_second_html_edit_rejected(self):
  p=self.root/'pioneers.html';p.write_bytes(p.read_bytes()+b' ')
  with self.assertRaisesRegex(ValueError,'Non-cache HTML drift'):adapter.validate_current(self.root)
 def test_wrong_script_path_rejected(self):
  p=self.root/'ask.html';p.write_bytes(p.read_bytes().replace(b'src="answer-bank-data.js',b'src="https://other.invalid/answer-bank-data.js'))
  with self.assertRaisesRegex(ValueError,'Exactly one'):adapter.validate_current(self.root)
 def test_stale_legacy_tag_not_current_approval(self):
  p=self.root/'ask.html';p.write_bytes(p.read_bytes().replace(self.tag,adapter.OLD_TAG))
  with self.assertRaisesRegex(ValueError,'Exactly one'):adapter.validate_current(self.root)
 def test_changed_bank_with_matching_token_is_coherence_not_approval(self):
  changed=self.bank+b' ';(self.root/'answer-bank-data.js').write_bytes(changed)
  for name in adapter.HISTORICAL_HTML:
   p=self.root/name;p.write_bytes(p.read_bytes().replace(adapter.sha(self.bank)[:8].encode(),adapter.sha(changed)[:8].encode()))
  self.assertEqual(adapter.validate_current(self.root)['bank_sha256'],adapter.sha(changed))
 def test_symlink_file_rejected(self):
  p=self.root/'answer-bank-data.js';p.rename(self.root/'bank-copy');p.symlink_to(self.root/'bank-copy')
  with self.assertRaisesRegex(ValueError,'unsafe'):adapter.validate_current(self.root)
 def test_symlink_directory_rejected(self):
  (self.root/'linked').symlink_to(self.root,target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'Symlink directory'):
   with adapter.historical_check_view(self.root):pass
 def test_copy_time_input_change_rejected(self):
  original=adapter.shutil.copy2
  for target in ('answer-bank-data.js','ask.html'):
   with self.subTest(target=target):
    def corrupt(source,dest):
     result=original(source,dest)
     if Path(source).name==target:Path(dest).write_bytes(Path(dest).read_bytes()+b' ')
     return result
    with patch.object(adapter.shutil,'copy2',corrupt),self.assertRaisesRegex(ValueError,'changed during validation snapshot'):
     with adapter.historical_check_view(self.root):pass
 def test_watch_projection_requires_current_validation(self):
  with patch('watch_current_source_qa.check',side_effect=ValueError('current Watch invalid')):
   with self.assertRaisesRegex(ValueError,'current Watch invalid'):
    with adapter.historical_check_view(self.root,include_watch=True):pass
 def test_watch_projection_rejects_wrong_historical_bytes(self):
  with patch('watch_current_source_qa.check',return_value={}),patch('subprocess.check_output',return_value=b'wrong'):
   with self.assertRaisesRegex(ValueError,'Historical Watch fixture changed'):
    with adapter.historical_check_view(self.root,include_watch=True):pass
 def test_watch_projection_rechecks_current_snapshot(self):
  historical=subprocess.check_output(['git','-C',str(adapter.ROOT),'show',adapter.HISTORICAL_COMMIT+':watch.html'])
  with patch('watch_current_source_qa.check',return_value={}),patch('subprocess.check_output',return_value=historical),patch('watch_current_source_qa.check_sources',side_effect=ValueError('changed snapshot')):
   with self.assertRaisesRegex(ValueError,'changed snapshot'):
    with adapter.historical_check_view(self.root,include_watch=True):pass
 def test_projection_does_not_change_original_files(self):
  before={p.name:p.read_bytes() for p in self.root.iterdir()}
  with adapter.historical_check_view(self.root) as (view,record):
   for n in adapter.HISTORICAL_HTML:self.assertEqual(adapter.sha((view/n).read_bytes()),adapter.HISTORICAL_HTML[n])
   self.assertEqual(adapter.sha((view/'answer-bank-data.js').read_bytes()),record['bank_sha256'])
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.iterdir()})
if __name__=='__main__':unittest.main()
