"""Structural research acceptance; never substitutes for mandate/browser review."""
import hashlib, html, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from joseph_research_acceptance import ROUTE, REJECTED_GENERIC_SCENES, REJECTED_GENERIC_HASHES, check_entry_and_brevity, check_reading_cadence, check_original_manifest, check_reference_scope, check_exact_review, check_evidence_inventory

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'docs/joseph-portrait-research-content.json').read_text(encoding='utf-8'))
editorial=json.loads((ROOT/'docs/joseph-research-editorial-map.json').read_text(encoding='utf-8'))
# Individually reviewed semantic edit, not a general license to rewrite evidence.
approved_editorial={'The unchanged owner-approved portrait. A modern artistic interpretation, not an authenticated photograph or a forensic identification. [20]': 'Our adopted portrait remains unchanged. It is a modern artistic interpretation, not an authenticated photograph or a forensic identification. [20]', 'Retain the approved Joseph': 'Why we kept this likeness', 'EVIDENCE, INTERPRETATION AND THE CASE FOR RETAINING HIM': 'A portrait informed by history', 'A consolidated study of the approved portrait: what the historical record supports, what it leaves uncertain, and what would justify a change.': 'What did Joseph Smith look like? No single surviving source answers the whole question. A cast preserves contours; a portrait records an artist’s choices; a description captures what one observer noticed. Here we follow those records to see what supports our portrait, what remains uncertain, and what could justify a change.', 'Joseph death-mask reference as used in the current focusChrist study. The mask photograph is provided for source context, not as a pose-matched overlay or proof of agreement. [1, 20]': 'The <a href="joseph-smith-likeness.html#joseph-mask-comparison">Joseph death-mask photograph in the original portrait study</a> remains available for source context, not as a pose-matched overlay or proof of agreement. The photograph displayed here is a different, newly consulted BYU reference. [1,20]'}
assert {e['original']:e['replacement'] for e in editorial['changes']}==approved_editorial, 'New editorial mapping requires independent semantic review'
main_page=(ROOT/'joseph-smith-likeness.html').read_text(encoding='utf-8')
assert (ROOT/ROUTE).is_file(), 'Research requires its own HTML route'
page=(ROOT/ROUTE).read_text(encoding='utf-8')
assert not any(bad in page for bad in ('\ufffd', '\u00e2\u20ac\u2122', '\u00c3\u00a9')), 'Encoding corruption in research page'
main_doc=BeautifulSoup(main_page,'html.parser')
doc=BeautifulSoup(page,'html.parser')
root=doc.select_one('#portrait-research')
assert root is not None,'Separate page lacks complete research'
research=str(root)

check_entry_and_brevity(main_doc)
def norm(s):
    s=html.unescape(re.sub('<[^>]+>',' ',s))
    s=re.sub(r'\[\s*[0-9]+(?:\s*[-,]\s*[0-9]+)*\s*\]','',s)
    return re.sub(r'\s+',' ',s).strip()
flat=norm(research)
checked=0
omitted=[]
for section in data['sections']:
    for block in section['blocks']:
        if section['id']=='section-2' and block['kind']!='box':continue
        if block['kind']=='paragraph':
            if block['style']=='title':continue
            if block['html'].startswith('Prepared for Wyatt. Use the navigation bar'):
                omitted.append('Paper navigation instruction replaced by HTML navigation');continue
            values=[block['html']]
        elif block['kind']=='box':values=[block['title'],block['html']]
        elif block['kind']=='trait':values=[block['title'],block['observed'],block['evidence'],block['verdict']]
        elif block['kind']=='table':values=block['headers']+[x for row in block['rows'] for x in row]
        elif block['kind']=='image':values=[block['caption']] if block.get('caption') else []
        else:raise AssertionError(block['kind'])
        for value in values:
            value=approved_editorial.get(value,value)
            assert norm(value) in flat,'Missing research text: '+value[:100]
            checked+=1
ids=re.findall(r'\bid="([^"]+)"',page)
assert len(ids)==len(set(ids)),'Duplicate HTML ids'
for target in re.findall(r'href="#(portrait-[^"]+)"',research):assert target in ids,'Missing research target '+target
assert research.count('class="research-trait"')==16,'Expected sixteen trait audits'
assert not re.search(r'locket|daguerreotype|Curtis Weber',research,re.I),'Comparison research leaked into focused study'
assert root.select('figure img'), 'Research needs actual relevant imagery beside its reading, not only distant image links'
assert doc.select_one('a[href="joseph-smith-likeness.html#our-portrait"]'), 'Research needs a return to the owning portrait study'
assert len(root.select('.research-part[id]'))==15, 'All fifteen source sections remain navigable'
onward=root.select_one('.research-study-onward')
assert onward and len(onward.select('dl dd'))>=3, 'Research needs three meaningful guided reflections'
assert len({a.get('href') for a in onward.select('a[href]') if a.get('href','').endswith('.html')})>=3, 'Research needs three onward study paths'
assert any(a.get('href','').startswith('ask.html?topic=Joseph') for a in onward.select('a[href]')), 'Contextual Joseph Ask path missing'
assert root.select_one('a[download][href="assets/research/focuschrist-joseph-evidence.pdf"]'), 'Complete PDF download missing'
image_records=[]
for figure in root.select('figure'):
    imgs=figure.select('img')
    assert imgs, 'Empty figure is not evidence imagery'
    assert figure.select_one('figcaption'), 'Each image needs source/context caption'
    assert figure.select_one('a[href]'), 'Image reference needs its source/owning-study action'
    for img in imgs:
        src=img.get('src','').split('?')[0]
        assert src and not re.match(r'^(?:https?:|data:|#)',src), 'Research image must be a verified local asset'
        path=(ROOT/src.lstrip('/')).resolve()
        assert ROOT.resolve() in path.parents and path.is_file(), 'Missing/out-of-scope image asset '+src
        assert img.get('alt','').strip(), 'Image needs meaningful alternative text'
        assert int(img.get('width',0))>0 and int(img.get('height',0))>0, 'Reserve intrinsic image dimensions'
        with Image.open(path) as actual:
            assert actual.width>=160 and actual.height>=100, 'Tiny placeholder is not meaningful reading imagery'
            assert (int(img['width']),int(img['height']))==actual.size, 'Declared image dimensions differ from actual pixels: '+src
            actual.verify()
        assert not any(n.has_attr('hidden') or re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',n.get('style',''),re.I) for n in [img,*img.parents] if getattr(n,'attrs',None)), 'Hidden image cannot satisfy reading cadence'
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest not in REJECTED_GENERIC_HASHES and not any(name in src for name in REJECTED_GENERIC_SCENES), 'Owner-rejected generic method image present'
        image_records.append({'src':src,'sha256':digest})
cadence_path=ROOT/'docs/joseph-research-cadence-exceptions.json'
cadence_exceptions=json.loads(cadence_path.read_text(encoding='utf-8'))['records'] if cadence_path.is_file() else []
reading_block_count=check_reading_cadence(root,cadence_exceptions)
# Exact page-specific evidence study: authentic references remain references.
# Generated scenes cannot use this path; a new original needs separate owner-scope
# reconciliation and full preflight/finished-image reviews before integration.
assert not root.select('figure[data-research-art]'), 'New originals require separate exact review; do not disguise them as references'
reference_records=[dict(r,kind='historical_document') for r in json.loads((ROOT/'docs/joseph-research-document-sources.json').read_text(encoding='utf-8'))['records']]
pelton=json.loads((ROOT/'docs/joseph-research-pelton-source.json').read_text(encoding='utf-8'))
assert pelton['sha256']=='6eb0a2759c0e78e6c934db0465b5d26b6c9b674e983679c3c3105a2925c01c3b', 'Pelton derivative bytes require renewed source review'
reference_records.append(dict(pelton,kind='historical_document'))
reference_records += [
    {'asset':'assets/identities/joseph-smith-owner-approved-20260914.png','sha256':'518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827','kind':'existing_reference','owning_study':'joseph-smith-likeness.html#our-portrait'},
    {'asset':'assets/research/joseph-documents/byu-reled-4109-mask-pair.jpg','sha256':'f69d497dc7bceeab0c3b459e30e4f31c7d1173e1fd56ddd7179783db105ce8b0','kind':'existing_reference','source_url':'https://contentdm.lib.byu.edu/digital/collection/RelEd/id/4109/rec/5'},
]
evidence_inventory=check_evidence_inventory(image_records,reference_records,ROUTE)
for figure in root.select('figure'):
    assert figure.get('data-research-reference') == 'true', 'Source imagery must remain explicitly classified as references'
originals=[]
assert hashlib.sha256((ROOT/'assets/identities/joseph-smith-owner-approved-20260914.png').read_bytes()).hexdigest()=='518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827'
pdf=ROOT/'assets/research/focuschrist-joseph-evidence.pdf'
assert pdf.read_bytes().startswith(b'%PDF-'),'Download is not a PDF'
print(json.dumps({'result':'STRUCTURAL_CHECKS_PASS_NOT_READY_CERTIFICATION','research_route':ROUTE,'research_text_items':checked,'trait_audits':16,'sections':len(data['sections']),'image_placements':image_records,'evidence_inventory':evidence_inventory,'original_artworks':len(originals),'christ_originals':sum(r['depicts_christ'] for r in originals),'reading_blocks':reading_block_count,'document_navigation_adaptation':omitted,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'limits':'Metadata count and placement checks are not pixel proof. Image relevance, visual cadence, actual identities/Christ depiction, full mandate compliance, browser interaction and owner visual acceptance require separate recorded checks. Reference images do not count as new originals.'},indent=2))
