"""Check research text parity and the existing portrait's protected bytes."""
import hashlib, html, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'docs/joseph-portrait-research-content.json').read_text(encoding='utf-8'))
page=(ROOT/'joseph-smith-likeness.html').read_text(encoding='utf-8')
research=page.split('<!-- BEGIN JOSEPH PORTRAIT RESEARCH -->')[1].split('<!-- END JOSEPH PORTRAIT RESEARCH -->')[0]
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
            assert norm(value) in flat,'Missing research text: '+value[:100]
            checked+=1
ids=re.findall(r'\bid="([^"]+)"',page)
assert len(ids)==len(set(ids)),'Duplicate HTML ids'
for target in re.findall(r'href="#(portrait-[^"]+)"',research):assert target in ids,'Missing research target '+target
assert research.count('class="research-trait"')==16,'Expected sixteen trait audits'
assert not re.search(r'locket|daguerreotype|Curtis Weber',research,re.I),'Comparison research leaked into focused study'
assert '<img' not in research,'Do not repeat existing art in this section'
assert hashlib.sha256((ROOT/'assets/identities/joseph-smith-owner-approved-20260914.png').read_bytes()).hexdigest()=='518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827'
pdf=ROOT/'assets/research/focuschrist-joseph-evidence.pdf'
assert pdf.read_bytes().startswith(b'%PDF-'),'Download is not a PDF'
print(json.dumps({'result':'PASS','research_text_items':checked,'trait_audits':16,'sections':len(data['sections']),'document_navigation_adaptation':omitted,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'limits':'Content/links/bytes only; browser and independent mandate reviews remain separate.'},indent=2))
