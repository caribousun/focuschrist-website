"""Timeline references retain route scope and must prove an actual owning artwork."""
import json, tempfile, unittest
from pathlib import Path
from PIL import Image
from answer_study_qa import Document
from topic_artwork_uniqueness_qa import scan, is_owning_page_reference, linked_reference
from artwork_details_qa import TIMELINE_STUDY_HEROES, TIMELINE_PANEL_RECORDS

class TimelineOwnershipTests(unittest.TestCase):
 def test_exact_panel_metadata_and_actual_record_required(self):
  site=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'timelines').mkdir()
   original_script=(site/'hero-details.js').read_text(encoding='utf-8')
   (root/'hero-details.js').write_text(original_script,encoding='utf-8')
   def reference(html,path):
    doc=Document();doc.feed(html)
    node=next(n for n in doc.root.walk() if n.tag=='img')
    return linked_reference(node,path,root)
   for route,(study,src,mobile) in TIMELINE_STUDY_HEROES.items():
    record,full=TIMELINE_PANEL_RECORDS[route];page=root/route
    picture=f'<picture><source srcset="{mobile}"><img src="{src}"></picture>' if mobile else f'<img src="{src}">'
    html=f'<a class="fc-visual-hero" data-hero-viewer data-hero-record="{record}" data-hero-study="{study}" aria-haspopup="dialog" href="{full}">{picture}</a>'
    expected={'owner':study.removeprefix('../').split('#')[0],'fragment':study.split('#')[1]}
    self.assertEqual(reference(html,page),expected)
    for old,new in [(study,'../index.html'),(record,'home'),(src,'../assets/heroes/home.webp'),('data-hero-viewer','data-full-image-viewer'),('aria-haspopup="dialog"','aria-haspopup="false"')]:
     self.assertIsNone(reference(html.replace(old,new),page),(route,old))
    self.assertIsNone(reference(html,root/'unrelated.html'))
    (root/'hero-details.js').write_text(original_script.replace('"study": "'+study.removeprefix('../')+'"','"study": "index.html"'),encoding='utf-8')
    self.assertIsNone(reference(html,page),'Spoofed metadata cannot override actual record')
    (root/'hero-details.js').write_text(original_script,encoding='utf-8')
    owner=Document();owner.feed(f'<section id="{expected["fragment"]}"><figure><img src="/art/owner.png"></figure></section>')
    ref={'family':'expected','linked_reference':expected};parsed={expected['owner']:list(owner.root.walk())}
    self.assertTrue(is_owning_page_reference(ref,expected['owner'],parsed,{'art/owner.png':'expected'},root))
    self.assertFalse(is_owning_page_reference(ref,expected['owner'],parsed,{'art/owner.png':'unrelated'},root),'Panel metadata never excuses unrelated owner artwork')

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
