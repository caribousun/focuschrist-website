"""Mission enrichment preservation and source/interaction contracts (draft until applied)."""
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / 'missionary.html').exists():
    ROOT = ROOT / 'focus-jesus'
sys.path.insert(0, str(ROOT / 'tools'))
from answer_study_qa import Document
BASELINE = '4b4b15069feb83c6ae9ea659bde2e3b94278f26a'
NEW = {'seventy-return': ('nt/luke/10','p17-p20'), 'samaritans-stay': ('nt/john/4','p39-p42'),
       'peace-to-this-house': ('nt/luke/10','p5-p7'), 'beside-his-missionaries': ('dc-testament/dc/84','p88')}
CHRIST = {'commission','missionary-purpose','worldwide-work','seventy-return','samaritans-stay','beside-his-missionaries'}

def parse(text):
    doc=Document();doc.feed(text);return list(doc.root.walk())

def tree(n):
    return n.tag,tuple(sorted(n.attrs.items())),tuple(x if isinstance(x,str) else tree(x) for x in n.content)

def errors(text,baseline,root=ROOT):
    out=[];nodes=parse(text);old=parse(baseline)
    figures=[n for n in nodes if n.tag=='figure'];records=[n for n in nodes if 'data-missionary-detail-content'in n.attrs]
    for label,predicate,count in [('figures',lambda n:n.tag=='figure',7),('detail records',lambda n:'data-missionary-detail-content'in n.attrs,9),('hero',lambda n:n.has('fc-visual-hero'),1),('opening',lambda n:n.has('fc-page-intro'),1)]:
        before=[tree(n) for n in old if predicate(n)];after=Counter(tree(n)for n in nodes if predicate(n))
        if len(before)!=count or any(after[t]!=1 for t in before):out.append('Original '+label+' changed/missing/duplicated')
    figure_keys=[a.attrs['data-missionary-detail'] for f in figures for a in f.walk() if 'data-missionary-detail'in a.attrs]
    if len(figures)!=11 or len(set(figure_keys))!=11 or len(figure_keys)!=11:out.append('Eleven unique owned figures required')
    if not CHRIST<=set(figure_keys):out.append('Six independently reviewed Christ figure identities missing')
    sources=[n.attrs.get('src')for f in figures for n in f.walk()if n.tag=='img']
    if len(sources)!=len(set(sources)):out.append('Repeated owned image')
    ids=Counter(n.attrs['id']for n in nodes if n.attrs.get('id'))
    for n in old:
        if n.attrs.get('id') and ids[n.attrs['id']]!=1:out.append('Original anchor lost: '+n.attrs['id'])
    nav=[n for n in nodes if n.has('fc-mission-directory')]
    links=[a for n in nav for a in n.walk()if a.tag=='a']
    if len(nav)!=1 or len(links)!=6 or len({a.attrs.get('href')for a in links})!=6:out.append('Six unique chapter choices required')
    if any(not a.attrs.get('href','').startswith('#') or ids[a.attrs['href'][1:]]!=1 for a in links):out.append('Chapter target missing')
    if len(records)!=13:out.append('Original nine plus four new detail records required')
    for key,(passage,verses) in NEW.items():
        secs=[n for n in nodes if n.attrs.get('id')=='mission-'+key]
        recs=[n for n in records if n.attrs['data-missionary-detail-content']==key]
        if len(secs)!=1 or len(recs)!=1:out.append(key+': study or detail missing');continue
        sec,record=secs[0],recs[0];parts=list(sec.walk())
        if sum(n.has('fc-mission-reflection')for n in parts)!=1:out.append(key+': reflection required')
        source=record.attrs.get('data-detail-source','')
        if '/study/scriptures/'+passage not in source or verses not in source:out.append(key+': exact source passage missing')
        if not any(n.tag=='a' and n.attrs.get('href')==source and n.parent.tag=='p' for n in parts):out.append(key+': inline source citation missing')
        trigger=[n for n in parts if n.attrs.get('data-missionary-detail')==key]
        full=record.attrs.get('data-detail-full','');thumb=record.attrs.get('data-detail-image','')
        if len(trigger)!=1 or trigger[0].attrs.get('href')!=full:out.append(key+': full-size picture interaction missing')
        for asset in [thumb,full]:
            p=root/urlsplit(asset).path
            if not p.is_file():out.append(key+': missing image '+asset);continue
            with Image.open(p)as im:
                if im.width*2!=im.height*3:out.append(key+': image must retain native3:2')
        image=next((n for n in parts if n.tag=='img'),None)
        if image is None or image.attrs.get('src')!=thumb:out.append(key+': thumbnail does not match detail')
        elif (root/urlsplit(thumb).path).is_file():
            with Image.open(root/urlsplit(thumb).path) as im:
                if (image.attrs.get('width'),image.attrs.get('height'))!=tuple(map(str,im.size)):out.append(key+': reserved thumbnail dimensions incorrect')
    return out

class MissionEnrichment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=(ROOT/'missionary.html').read_text(encoding='utf-8')
        cls.baseline=subprocess.check_output(['git','show',BASELINE+':missionary.html'],cwd=ROOT).decode('utf-8')
    def test_actual(self):self.assertEqual(errors(self.page,self.baseline),[])
    def test_missing_image(self):
        broken=self.page.replace('seventy-return-960.webp','missing-fixture.webp')
        self.assertNotEqual(broken,self.page);self.assertTrue(errors(broken,self.baseline))
    def test_duplicate_image(self):
        broken=self.page.replace('samaritans-stay-960.webp','seventy-return-960.webp')
        self.assertNotEqual(broken,self.page);self.assertTrue(errors(broken,self.baseline))
    def test_missing_target(self):
        broken=self.page.replace('href="#commission-heading"','href="#missing-fixture"')
        self.assertNotEqual(broken,self.page);self.assertTrue(errors(broken,self.baseline))

if __name__=='__main__':unittest.main()
