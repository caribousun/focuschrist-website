"""Synthetic producer/root protocol tests, not a real site regeneration."""
import copy,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import emma_journey_indices_contract as gate
from test_emma_journey_indices_contract import IndexTests

class SyntheticFullTreeProtocol(unittest.TestCase):
 def setUp(self):
  fixture=IndexTests('test_synthetic_happy_path');fixture.setUp();self.before=fixture.before;self.after=fixture.after
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)/'current';self.root.mkdir();self.base=Path(self.temp.name)/'base';self.base.mkdir()
  names={'art-gallery.json':'gallery','site-search-index.json':'search','docs/section-panel-inventory.json':'panel'};self.names=names
  hashes={}
  for name,key in names.items():
   for folder,source in ((self.base,self.before),(self.root,self.after)):
    p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(source[key]),encoding='utf-8')
   hashes[name]=gate.git_blob((self.base/name).read_bytes())
  (self.root/'docs/section-panel-surfaces.json').write_text('{}')
  self.patch=patch.object(gate,'BASE_BLOBS',hashes);self.patch.start();self.addCleanup(self.patch.stop)
  self.called=[]
  gallery=types.ModuleType('build_art_gallery');gallery.ROOT=self.root;gallery.build=lambda:copy.deepcopy(self.after['gallery'])
  search=types.ModuleType('build_site_search');search.ROOT=self.root;search.build=lambda:copy.deepcopy(self.after['search'])
  panel=types.ModuleType('section_panel_surface_qa');panel.ROOT=self.root;panel.inventory=lambda cfg:copy.deepcopy(self.after['panel']);panel.check=lambda cfg,data:self.called.append('panel_check')
  self.gallery,self.search,self.panel=gallery,search,panel
  self.patch=patch.dict(sys.modules,{'build_art_gallery':gallery,'build_site_search':search,'section_panel_surface_qa':panel});self.patch.start();self.addCleanup(self.patch.stop)
 def test_exact_fixture_outputs_use_all_producers_and_panel_check(self):
  self.assertEqual(gate.validate_full_tree(self.root,self.base)['new_emma_images'],10);self.assertEqual(self.called,['panel_check'])
 def test_wrong_root_wrong_baseline_and_stale_producer_fail(self):
  self.gallery.ROOT=self.base
  with self.assertRaisesRegex(AssertionError,'producer root mismatch'):gate.validate_full_tree(self.root,self.base)
  self.gallery.ROOT=self.root
  p=self.base/'art-gallery.json';data=p.read_bytes();p.write_bytes(data+b' ')
  with self.assertRaisesRegex(AssertionError,'baseline blob drift'):gate.validate_full_tree(self.root,self.base)
  p.write_bytes(data)
  self.gallery.build=lambda:{}
  with self.assertRaisesRegex(AssertionError,'gallery differs'):gate.validate_full_tree(self.root,self.base)
 def test_stale_search_and_panel_fail(self):
  self.search.build=lambda:{}
  with self.assertRaisesRegex(AssertionError,'search differs'):gate.validate_full_tree(self.root,self.base)
  self.search.build=lambda:copy.deepcopy(self.after['search']);self.panel.inventory=lambda cfg:{}
  with self.assertRaisesRegex(AssertionError,'panel inventory differs'):gate.validate_full_tree(self.root,self.base)
if __name__=='__main__':unittest.main()
