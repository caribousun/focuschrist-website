"""Timeline references retain route scope and must prove an actual owning artwork."""
import json, tempfile, unittest
from pathlib import Path
from PIL import Image
from answer_study_qa import Document
from topic_artwork_uniqueness_qa import scan, is_owning_page_reference

class TimelineOwnershipTests(unittest.TestCase):
 def test_registry_scope_and_negative_ownership(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'timelines').mkdir();(root/'art').mkdir()
   Image.new('RGB',(3,3),'red').save(root/'art/owner.png')
   Image.new('RGB',(3,3),'blue').save(root/'art/other.png')
   (root/'owner.html').write_text('<section id="scene"><figure><img src="art/owner.png"></figure></section>')
   route=root/'timelines/life-of-christ-journey-map.html';route.write_text('<script src="../timeline-images.js"></script>')
   registry={'life':{'0':{'src':'../art/owner.png','href':'../owner.html#scene'}},'history':{'0':{'src':'../art/other.png','href':'../owner.html#scene'}},'handcart':{}}
   (root/'timeline-images.js').write_text('var registry='+json.dumps(registry)+';var route="";')
   result=scan(root)
   # Scan result is the production identity/ownership graph, not a parallel parser.
   refs=[ref for usage in result['familyUsages'].values() for ref in usage['references']]
   self.assertIsNotNone(refs)
   selected=[r for r in refs if r['page']==route.relative_to(root).as_posix()]
   self.assertEqual([r['asset'] for r in selected],['art/owner.png'])
   ref=selected[0]
   doc=Document();doc.feed((root/'owner.html').read_text());parsed={'owner.html':list(doc.root.walk())};identities={'art/owner.png':ref['family']}
   self.assertTrue(is_owning_page_reference(ref,'owner.html',parsed,identities,root))
   for destination in [{'owner':'owner.html','fragment':'missing'},{'owner':'wrong.html','fragment':'scene'},None]:
    altered=dict(ref,linked_reference=destination)
    self.assertFalse(is_owning_page_reference(altered,'owner.html',parsed,identities,root))
   self.assertFalse(is_owning_page_reference(dict(ref,family='wrong-family'),'owner.html',parsed,identities,root))

if __name__=='__main__':unittest.main()
