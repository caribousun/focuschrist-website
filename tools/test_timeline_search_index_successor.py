"""Real-byte successor checks and negative fixtures, not a review receipt."""
import copy, json, unittest
from unittest.mock import patch
import timeline_search_index_successor as s

class SearchSuccessorTests(unittest.TestCase):
 def setUp(self):self.raw=s.source(s.ROOT,'site-search-index.json')
 def test_real_output_and_exact_previous(self):
  result=s.validate_current();self.assertEqual(result['current_sha256'],s.AFTER);self.assertEqual(result['previous_sha256'],s.BEFORE)
  old=json.loads(s.restore(self.raw));new=json.loads(self.raw)
  a={r['url']:r for r in old['records']};b={r['url']:r for r in new['records']}
  self.assertEqual({u for u in a.keys()|b.keys() if a.get(u)!=b.get(u)},s.CHANGED)
  self.assertEqual({u:r for u,r in a.items() if u.startswith('/history/emma-')},{u:r for u,r in b.items() if u.startswith('/history/emma-')})
 def test_changed_index_or_manifest_rejected(self):
  with self.assertRaisesRegex(AssertionError,'current search'):s.restore(self.raw+b' ')
  real=s.source
  with patch.object(s,'source',side_effect=lambda root,name:real(root,name)+(b' ' if name==s.MANIFEST else b'')):
   with self.assertRaisesRegex(AssertionError,'manifest'):s.restore(self.raw)
 def test_changed_sources_rejected(self):
  real=s.source
  for name in s.SOURCES:
   with self.subTest(name=name),patch.object(s,'source',side_effect=lambda root,n:real(root,n)+(b' ' if n==name else b'')):
    with self.assertRaisesRegex(AssertionError,'Changed current source'):s.restore(self.raw)
 def test_stale_producer_rejected(self):
  import build_site_search
  with patch.object(build_site_search,'build',return_value={}):
   with self.assertRaisesRegex(AssertionError,'full-tree producer'):s.validate_current()
 def test_same_count_unrelated_change_cannot_be_projected(self):
  data=json.loads(self.raw);m=copy.deepcopy(s.manifest());r=next(r for r in data['records'] if r['url'] not in s.CHANGED);r['text']+=' unrelated change'
  changed=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
  m['current_sha256']=s.sha(changed)
  with patch.object(s,'manifest',return_value=m),patch.object(s,'AFTER',s.sha(changed)):
   with self.assertRaisesRegex(AssertionError,'Prior exact search'):s.restore(changed)
 def test_missing_added_or_duplicate_destination_cannot_be_projected(self):
  data=json.loads(self.raw);added=next(r for r in data['records'] if r['url'].endswith('#nazareth-childhood'))
  for records in ([r for r in data['records'] if r is not added],data['records']+[added]):
   changed=(json.dumps(dict(data,records=records),ensure_ascii=False,separators=(',',':'))+'\n').encode()
   with self.subTest(count=len(records)),patch.object(s,'manifest',return_value=s.manifest()),patch.object(s,'AFTER',s.sha(changed)):
    with self.assertRaises(AssertionError):s.restore(changed)
if __name__=='__main__':unittest.main()
