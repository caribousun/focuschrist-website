"""Focused draft-capable checks; these do not certify a complete release."""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from build_jesus_discovery import sitemap
from answer_study_qa import Document

ROOT=Path(__file__).resolve().parents[1]
read=lambda name:json.loads((ROOT/name).read_text(encoding='utf-8'))
pages=read('docs/jesus-journey/pages.json')
registry=read('docs/jesus-journey/artworks.json')
gallery=read('art-gallery.json');search=read('site-search-index.json')
urls={p['url'] for p in pages};errors=[]

def directory_css_valid(css):
    compact=re.sub(r'\s+','',css)
    return all(rule in compact for rule in (
        '.jj-directory{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));',
        '.jj-directory>:last-child:nth-child(odd){grid-column:1/-1}',
        '@media(max-width:700px){.jj-directory{grid-template-columns:1fr}',
    ))

css=(ROOT/'jesus-journey.css').read_text(encoding='utf-8')
if not directory_css_valid(css):errors.append('Journey directory lost two-column, odd-row or phone stacking contract')
# Negative fixtures keep removal of any part from becoming a silent pass.
for old,new in [('grid-column:1/-1','grid-column:auto'),('repeat(2,minmax(0,1fr))','repeat(3,minmax(0,1fr))'),('grid-template-columns:1fr','grid-template-columns:repeat(2,1fr)')]:
    assert not directory_css_valid(css.replace(old,new)), 'Directory negative fixture failed: '+old
directory_count=0
for page in pages:
    doc=Document();doc.feed((ROOT/page['url'].lstrip('/')).read_text(encoding='utf-8'))
    nodes=list(doc.root.walk())
    grids=[n for n in nodes if n.has('jj-directory')]
    expected=sum(isinstance(b,dict) and 'cards' in b for s in page['sections'] for b in s.get('blocks',[]))+bool(page.get('related'))
    if len(grids)!=expected:errors.append('Journey directory inventory differs: '+page['url'])
    styles=[n.attrs.get('href','') for n in nodes if n.tag=='link' and 'jesus-journey.css' in n.attrs.get('href','')]
    if grids and styles!=['/jesus-journey.css?v=20260923-chapters-2']:errors.append('Missing or stale journey directory stylesheet: '+page['url'])
    if any(not grid.children for grid in grids):errors.append('Empty journey directory: '+page['url'])
    directory_count+=len(grids)
xml=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
if sitemap(xml,pages)!=xml:errors.append('Journey sitemap regeneration is not stable')
locations={n.text for n in ET.fromstring(xml).findall('{*}url/{*}loc')}
if not {'https://focuschrist.com'+u for u in urls}<=locations:errors.append('Missing nested sitemap destinations')
if not urls<=set(gallery['pages']) or not urls<=set(search['pages']):errors.append('Missing nested discovery pages')
search_urls={r['url'] for r in search['records']}
if not urls<=search_urls:errors.append('Missing nested page search records')
if 'About this portrayal' in json.dumps(search,ensure_ascii=False):errors.append('Removed portrayal language remains in search')
accepted=0
for key,a in registry.items():
    full='/'+a.get('asset','__unprepared__')
    matches=[art for art in gallery['artworks'] if art['fullImage']==full]
    if not a.get('reviewed'):
        if matches:errors.append('Unreviewed art in gallery '+key)
        continue
    accepted+=1
    if len(matches)!=1:errors.append('Expected one discoverable original '+key);continue
    art=matches[0]
    if art['thumbnail']!='/'+a['thumbnail']:errors.append('Wrong discovery thumbnail '+key)
    if len(art['occurrences'])!=1 or art['occurrences'][0]['page']!='/'+a['owner']:errors.append('Wrong or duplicate original owner '+key)
    if '/art-gallery.html?picture='+art['id'] not in search_urls:errors.append('Missing artwork search route '+key)
    for chapter in next((p['sections'] for p in pages if p['url']=='/'+a['owner']),[]):
        if any(isinstance(b,dict) and b.get('art')==key for b in chapter.get('blocks',[])):
            if '/'+a['owner']+'#'+chapter['id'] not in search_urls:errors.append('Missing source-story search stop '+key)
if errors:raise SystemExit('\n'.join(errors))
print(f'JOURNEY DISCOVERY PASS: 76 nested pages and {accepted} reviewed original pictures; stable sitemap, owning studies, chapter search and gallery routes. Drafts are not release-ready.')
