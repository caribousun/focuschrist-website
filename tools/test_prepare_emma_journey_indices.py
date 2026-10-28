"""Synthetic orchestration tests only; not producer or release evidence."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import prepare_emma_journey_indices as p

class RunnerTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)/'root';self.root.mkdir();self.out=Path(self.t.name)/'out'
  self.raw={name:('baseline '+name).encode() for name in p.BASE_BLOBS}
  self.patch=patch.object(p,'BASE_BLOBS',{name:p.blob_id(raw) for name,raw in self.raw.items()});self.patch.start();self.addCleanup(self.patch.stop)
  self.calls=[];self.fail='';self.bad_baseline=False
 def invoke(self,root,cmd):
  self.calls.append(cmd)
  if cmd[:2]==['git','show']:
   name=cmd[2].split(':',1)[1];return (0, b'corrupt' if self.bad_baseline else self.raw[name])
  key=' '.join(cmd)
  if self.fail and self.fail in key:return 1,b'synthetic failure'
  if '--write-inventory' in cmd:
   q=root/'docs/section-panel-inventory.json';q.parent.mkdir(exist_ok=True);q.write_text('{}')
  elif cmd==['python','tools/build_art_gallery.py']:(root/'art-gallery.json').write_text('{}')
  elif cmd==['python','tools/build_site_search.py']:(root/'site-search-index.json').write_text('{}')
  return 0,b'synthetic success'
 def test_success_and_order(self):
  r=p.execute(self.root,self.out,self.invoke);self.assertTrue(all(r[x]=='success' for x in ('baseline','panel','gallery','search','semantic_delta')))
  self.assertLess(next(i for i,c in enumerate(self.calls) if 'tools/build_art_gallery.py' in c),next(i for i,c in enumerate(self.calls) if 'tools/build_site_search.py' in c))
  self.assertEqual(json.loads((self.out/'index-generation-status.json').read_text()),r)
  self.assertIn('gallery_sha256',r)
 def test_gallery_failure_skips_search_and_delta_even_if_stale_files_exist(self):
  (self.root/'art-gallery.json').write_text('stale');(self.root/'site-search-index.json').write_text('stale');self.fail='build_art_gallery.py'
  r=p.execute(self.root,self.out,self.invoke);self.assertEqual(r['gallery'],'failed');self.assertTrue(r['search'].startswith('skipped'));self.assertTrue(r['semantic_delta'].startswith('skipped'))
  self.assertFalse((self.out/'art-gallery.json').exists());self.assertFalse((self.out/'site-search-index.json').exists())
  self.assertFalse(any('build_site_search.py' in c for c in self.calls))
 def test_panel_failure_does_not_hide_gallery_or_search_failure(self):
  self.fail='section_panel_surface_qa.py';r=p.execute(self.root,self.out,self.invoke)
  self.assertEqual(r['panel'],'failed');self.assertEqual(r['gallery'],'success');self.assertEqual(r['search'],'success');self.assertTrue(r['semantic_delta'].startswith('skipped'))
 def test_wrong_baseline_does_not_become_evidence(self):
  self.bad_baseline=True;r=p.execute(self.root,self.out,self.invoke);self.assertEqual(r['baseline'],'failed');self.assertTrue(r['semantic_delta'].startswith('skipped'))
  self.assertFalse(any('tools/emma_journey_indices_contract.py' in c for c in self.calls))
 def test_existing_artifact_refused(self):
  self.out.mkdir();(self.out/'art-gallery.json').write_text('old evidence')
  with self.assertRaisesRegex(ValueError,'fresh directory'):p.execute(self.root,self.out,self.invoke)
  self.assertEqual((self.out/'art-gallery.json').read_text(),'old evidence')
if __name__=='__main__':unittest.main()
