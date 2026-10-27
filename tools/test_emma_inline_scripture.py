"""Exact-owner and actual-page scripture regressions; no browser or network."""
import json, shutil, tempfile, unittest
from pathlib import Path
import topic_inline_scripture_qa as qa
ROOT=Path(__file__).resolve().parents[1]

class EmmaScriptureTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  for name in qa.EMMA_STORIES+('scripture-data/dc-testament/dc/25.json',):
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
 def check(self):return qa.check_scriptures(self.root,list(qa.EMMA_STORIES),[])
 def change(self,old,new):
  p=self.root/'history/emma-hymns.html';s=p.read_text();self.assertIn(old,s);p.write_text(s.replace(old,new))
 def test_actual_five_pages(self):self.assertEqual(self.check(),5)
 def test_exact_nine_owners(self):self.assertEqual(qa.checked_history_routes(list(qa.HISTORICAL_STORIES+qa.EMMA_STORIES)),list(qa.HISTORICAL_STORIES+qa.EMMA_STORIES))
 def test_each_missing_owner(self):
  for name in qa.HISTORICAL_STORIES+qa.EMMA_STORIES:
   with self.subTest(name=name),self.assertRaises(AssertionError):qa.checked_history_routes([x for x in qa.HISTORICAL_STORIES+qa.EMMA_STORIES if x!=name])
 def test_duplicate_owner(self):
  with self.assertRaises(AssertionError):qa.checked_history_routes(list(qa.HISTORICAL_STORIES+qa.EMMA_STORIES)+(list(qa.EMMA_STORIES[:1])))
 def test_unknown_owner(self):
  with self.assertRaises(AssertionError):qa.checked_history_routes(list(qa.HISTORICAL_STORIES+qa.EMMA_STORIES)+['history/unknown.html'])
 def test_unlinked_citation_each_new_owner(self):
  for name in qa.EMMA_STORIES:
   p=self.root/name;s=p.read_text();p.write_text(s.replace('</main>','<p>Doctrine and Covenants 25</p></main>'))
   with self.subTest(name=name),self.assertRaisesRegex(AssertionError,'unlinked'):self.check()
   p.write_text(s)
 def test_missing_chapter(self):
  self.change('/dc/25?','/dc/999?')
  with self.assertRaisesRegex(AssertionError,'unavailable'):self.check()
 def test_wrong_language(self):
  self.change('lang=eng','lang=fra')
  with self.assertRaises(AssertionError):self.check()
 def test_wrong_selection(self):
  self.change('id=p11-p12#p11','id=p10-p12#p10')
  with self.assertRaisesRegex(AssertionError,'selection differs'):self.check()
 def test_out_of_range(self):
  self.change('id=p11-p12#p11','id=p11-p999#p11')
  with self.assertRaises(AssertionError):self.check()
 def test_wrong_fragment(self):
  self.change('id=p11-p12#p11','id=p11-p12#p12')
  with self.assertRaises(AssertionError):self.check()
 def test_missing_selection_on_plain_new_link(self):
  self.change(' class="fc-inline-scripture"','');self.change('&amp;id=p11-p12#p11','')
  with self.assertRaisesRegex(AssertionError,'selection differs'):self.check()
 def test_nested_anchor(self):
  self.change('Doctrine and Covenants 25</a>','<a href="#nested">Doctrine and Covenants 25</a></a>')
  with self.assertRaisesRegex(AssertionError,'nested anchor'):self.check()
 def test_historical_same_safety(self):
  name=qa.HISTORICAL_STORIES[0];p=self.root/name;p.write_text('<main><p>Doctrine and Covenants 25</p></main>')
  with self.assertRaisesRegex(AssertionError,'unlinked'):qa.check_scriptures(self.root,[name],[])

if __name__=='__main__':unittest.main()
