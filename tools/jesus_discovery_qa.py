"""Focused draft-capable checks; these do not certify a complete release."""
import json
import re
from collections import Counter
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
journey=read('docs/jesus-journey/main-content.json')
route=next(b['cards'] for b in journey['sections'][0]['blocks'] if isinstance(b,dict) and 'cards' in b)

def expected_directories(page):
    """Inventory exact destination rows, including explicitly linked owner previews."""
    rows=[]
    for section in page['sections']:
        for block in section.get('blocks',[]):
            if not isinstance(block,dict):continue
            if 'cards' in block:rows.append(tuple(card[0] for card in block['cards']))
            elif 'reference_art' in block:
                key=block['reference_art'];art=registry[key]
                rows.append(('/'+art['owner']+'#picture-'+key,))
            elif 'reference_picture' in block:rows.append((block['reference_picture']['href'],))
    index=next((i for i,card in enumerate(route) if card[0]==page['url']),None)
    if index is not None and index+1<len(route):rows.append((route[index+1][0],))
    if page.get('related'):rows.append(tuple(card[0] for card in page['related']))
    return Counter(rows)

def card_destination(node):
    if node.tag=='a':return node.attrs.get('href','')
    if node.tag=='div' and node.has('jj-card'):
        links=[n for n in node.children if n.tag=='a']
        if len(links)==2 and links[1].has('jj-card-action') and any(n.tag=='h3' for n in links[0].walk()):
            destination=links[0].attrs.get('href','')
            if destination and links[1].attrs.get('href')==destination:return destination
    return ''

def directory_rows(grids):
    return Counter(tuple(card_destination(n) for n in grid.children) for grid in grids)

# Source-bearing cards must retain both matching local-study actions. A source
# link inside the description must never substitute for the onward destination.
fixture='<div class="jj-directory"><div class="jj-card"><a href="/study.html"><h3>Study</h3></a><p><a href="https://example.org/source">Source</a></p><a class="jj-card-action" href="/study.html">Open study</a></div></div>'
def fixture_rows(text):
    doc=Document();doc.feed(text)
    return directory_rows([n for n in doc.root.walk() if n.has('jj-directory')])
assert fixture_rows(fixture)==Counter({('/study.html',):1})
for mutant in (
    fixture.replace('<a class="jj-card-action" href="/study.html">Open study</a>',''),
    fixture.replace('class="jj-card-action" href="/study.html"','class="jj-card-action" href="/wrong.html"'),
    fixture.replace('</p>','</p><a href="/study.html">Duplicate</a>'),
    fixture.replace('class="jj-card"','class="unrecognized"'),
):
    assert fixture_rows(mutant)!=Counter({('/study.html',):1}), 'Source-bearing directory negative fixture failed'

directory_count=0
for page in pages:
    doc=Document();doc.feed((ROOT/page['url'].lstrip('/')).read_text(encoding='utf-8'))
    nodes=list(doc.root.walk())
    grids=[n for n in nodes if n.has('jj-directory')]
    expected=expected_directories(page)
    actual=directory_rows(grids)
    if actual!=expected:errors.append('Journey directory destinations or row inventory differ: '+page['url'])
    # Equal row counts must not hide a missing, duplicated, or misdirected reference.
    if expected:
        key=next(iter(expected));missing=expected.copy();missing.subtract([key]);missing=+missing
        wrong=expected.copy();wrong.subtract([key]);wrong[('/incorrect-owner.html',)]+=1;wrong=+wrong
        assert missing!=expected and wrong!=expected, 'Directory inventory negative fixture failed'
    styles=[n.attrs.get('href','') for n in nodes if n.tag=='link' and 'jesus-journey.css' in n.attrs.get('href','')]
    if grids and styles!=['/jesus-journey.css?v=20261007-chapter-pair-1']:errors.append('Missing or stale journey directory stylesheet: '+page['url'])
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
