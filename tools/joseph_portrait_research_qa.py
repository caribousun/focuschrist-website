"""Structural research acceptance; never substitutes for mandate/browser review."""
import hashlib, html, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from joseph_research_acceptance import ROUTE, REJECTED_GENERIC_SCENES, REJECTED_GENERIC_HASHES, check_entry_and_brevity, check_reading_cadence, check_original_manifest, check_reference_scope, check_exact_review, check_evidence_inventory, check_feature_studies, check_original_page_exclusivity

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'docs/joseph-portrait-research-content.json').read_text(encoding='utf-8'))
editorial=json.loads((ROOT/'docs/joseph-research-editorial-map.json').read_text(encoding='utf-8'))
# Individually reviewed semantic edit, not a general license to rewrite evidence.
approved_editorial={'The unchanged owner-approved portrait. A modern artistic interpretation, not an authenticated photograph or a forensic identification. [20]': 'Our adopted portrait remains unchanged. It is a modern artistic interpretation, not an authenticated photograph or a forensic identification. [20]', 'Retain the approved Joseph': 'Why we kept this likeness', 'EVIDENCE, INTERPRETATION AND THE CASE FOR RETAINING HIM': 'A portrait informed by history', 'A consolidated study of the approved portrait: what the historical record supports, what it leaves uncertain, and what would justify a change.': 'What did Joseph Smith look like? No single surviving source answers the whole question. A cast preserves contours; a portrait records an artist’s choices; a description captures what one observer noticed. Here we follow those records to see what supports our portrait, what remains uncertain, and what could justify a change.', 'Joseph death-mask reference as used in the current focusChrist study. The mask photograph is provided for source context, not as a pose-matched overlay or proof of agreement. [1, 20]': 'The <a href="joseph-smith-likeness.html#joseph-mask-comparison">mask comparison in the portrait study</a> now uses this same newly consulted BYU photograph. It supplies source context, not a pose-matched overlay or proof of agreement, and is not established as an original creation input. [1,20]'}
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
features=json.loads((ROOT/'docs/joseph-research-feature-studies.json').read_text(encoding='utf-8'))
traits={b['title'].split()[0]:b for section in data['sections'] for b in section['blocks'] if b['kind']=='trait'}
verified_features=check_feature_studies(root,features,traits)
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
        canonical=img.get('data-source-original',src)
        image_records.append({'src':canonical,'sha256':hashlib.sha256((ROOT/canonical).read_bytes()).hexdigest(),'original_id':figure.get('data-research-art')})
cadence_path=ROOT/'docs/joseph-research-cadence-exceptions.json'
cadence_exceptions=json.loads(cadence_path.read_text(encoding='utf-8'))['records'] if cadence_path.is_file() else []
reading_block_count=check_reading_cadence(root,cadence_exceptions,verified_features)
# Later direct owner correction explicitly requires new relevant artwork.
# References stay distinct and cannot satisfy the required ten originals.
art_manifest=ROOT/'docs/joseph-portrait-research-art-review.json'
assert art_manifest.is_file(), 'OWNER CORRECTION: missing ten-original artwork and exact preflight/finished review manifest'
originals=json.loads(art_manifest.read_text(encoding='utf-8'))['originals']
check_original_manifest(originals,require_half_christ=False)
# Verify exact-byte exclusivity across actual rendered image references, including
# renamed copies. Full-size hyperlinks to the sole owning study remain allowed.
from urllib.parse import unquote, urlsplit
original_sizes={(ROOT/r['asset']).stat().st_size for r in originals}
rendered_images={}
image_hash_cache={}
for html_path in ROOT.rglob('*.html'):
    relative=html_path.relative_to(ROOT).as_posix()
    if any(part.startswith('.') or part in {'node_modules','work','outputs'} for part in html_path.relative_to(ROOT).parts):
        continue
    image_hashes=[]
    other=BeautifulSoup(html_path.read_text(encoding='utf-8'),'html.parser')
    for img in other.select('img[src]'):
        parsed=urlsplit(img['src'])
        if parsed.scheme or parsed.netloc: continue
        target=(ROOT/unquote(parsed.path.lstrip('/'))) if parsed.path.startswith('/') else (html_path.parent/unquote(parsed.path))
        if not target.is_file() or target.stat().st_size not in original_sizes: continue
        target=target.resolve()
        if target not in image_hash_cache: image_hash_cache[target]=hashlib.sha256(target.read_bytes()).hexdigest()
        image_hashes.append(image_hash_cache[target])
    rendered_images[relative]=image_hashes
check_original_page_exclusivity(originals,rendered_images)

placed=root.select('figure[data-research-art]')
assert len(placed)==len(originals), 'Original artwork placement count differs from review'
assert {f['data-research-art'] for f in placed}=={r['id'] for r in originals}, 'Original placement identities differ from manifest'
for record in originals:
    matches=[f for f in placed if f['data-research-art']==record['id']]
    assert len(matches)==1, 'Original repeated within page'
    figure=matches[0]
    assert figure.find_parent(id=record['owning_section'].lstrip('#')), 'Original placed outside owning section'
    asset=ROOT/record['asset']
    assert asset.is_file() and hashlib.sha256(asset.read_bytes()).hexdigest()==record['sha256'], 'Original bytes differ from finished review'
    assert any(a.get('href','').split('?')[0]==record['asset'] for a in figure.select('a[href]')), 'Original full-size link missing'
    assert record.get('source_urls') and record.get('preflight_prompt_sha256'), 'Missing original source/preflight provenance'
    check_reference_scope(record)
    for key in ('fermi_preflight','newton_preflight','fermi_finished_pixels','newton_finished_pixels'):
        assert record.get(key) and (ROOT/record[key]).is_file(), 'Missing actual review receipt: '+key
        check_exact_review(record,json.loads((ROOT/record[key]).read_text(encoding='utf-8')),finished=key.endswith('finished_pixels'))
reference_records=[dict(r,kind='historical_document') for r in json.loads((ROOT/'docs/joseph-research-document-sources.json').read_text(encoding='utf-8'))['records']]
pelton=json.loads((ROOT/'docs/joseph-research-pelton-source.json').read_text(encoding='utf-8'))
assert pelton['sha256']=='6eb0a2759c0e78e6c934db0465b5d26b6c9b674e983679c3c3105a2925c01c3b', 'Pelton derivative bytes require renewed source review'
reference_records.append(dict(pelton,kind='historical_document'))
reference_records += [
    {'asset':'assets/identities/joseph-smith-owner-approved-20260914.png','sha256':'518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827','kind':'existing_reference','owning_study':'joseph-smith-likeness.html#our-portrait'},
    {'asset':'assets/research/joseph-documents/byu-reled-4109-mask-pair.jpg','sha256':'f69d497dc7bceeab0c3b459e30e4f31c7d1173e1fd56ddd7179783db105ce8b0','kind':'existing_reference','source_url':'https://contentdm.lib.byu.edu/digital/collection/RelEd/id/4109/rec/5'},
]
assert len(image_records)>=20, 'Owner requires at least twenty meaningful pictures in this research study; raw placement count is not sufficient acceptance'
evidence_inventory=check_evidence_inventory([r for r in image_records if not r['original_id']],reference_records,ROUTE)
for figure in root.select('figure'):
    if not figure.has_attr('data-research-art'):
        assert figure.get('data-research-reference') == 'true', 'Source imagery must remain explicitly classified as references'
    else:
        assert not figure.has_attr('data-research-reference'), 'New original artwork must not be labelled a historical reference'
assert hashlib.sha256((ROOT/'assets/identities/joseph-smith-owner-approved-20260914.png').read_bytes()).hexdigest()=='518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827'
pdf=ROOT/'assets/research/focuschrist-joseph-evidence.pdf'
assert pdf.read_bytes().startswith(b'%PDF-'),'Download is not a PDF'
print(json.dumps({'result':'STRUCTURAL_CHECKS_PASS_NOT_READY_CERTIFICATION','research_route':ROUTE,'research_text_items':checked,'trait_audits':16,'sections':len(data['sections']),'image_placements':image_records,'evidence_inventory':evidence_inventory,'original_artworks':len(originals),'christ_originals':sum(r['depicts_christ'] for r in originals),'reading_blocks':reading_block_count,'document_navigation_adaptation':omitted,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'limits':'Metadata count and placement checks are not pixel proof. Image relevance, visual cadence, actual identities/Christ depiction, full mandate compliance, browser interaction and owner visual acceptance require separate recorded checks. Reference images do not count as new originals.'},indent=2))
