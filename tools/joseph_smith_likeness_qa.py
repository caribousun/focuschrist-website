"""Verify the likeness study's integration; human source/pixel review stays separate."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'joseph-smith-likeness.html'
MASTER = 'assets/identities/joseph-smith-owner-approved-20260914.png'
MASTER_SHA = '518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827'
HYRUM_DRAFT = 'assets/page-art/joseph-smith-likeness/hyrum-reconstruction-blue-eyes-20261003.png'
HYRUM_DRAFT_SHA = '47b35f55b805ee0cc7c914cc1adb59273b2405402d4a50e284d0bb456bd9cb32'
SLOTS = {'portrait-sitting', 'writing', 'warmth', 'conversation', 'brothers'}
SECTIONS = {'living-portrait', 'death-masks', 'portraits-from-life',
            'our-portrait', 'face-in-motion', 'continue-study'}
SOURCES = {
    ('churchhistorylibrary.churchofjesuschrist.org', '/joseph-and-hyrum-death-masks'),
    ('churchhistorylibrary.churchofjesuschrist.org', '/blog/imaging-joseph-and-hyrum-smiths-death-masks'),
    ('www.josephsmithpapers.org', '/paper-summary/journal-december-1841-december-1842/30'),
}


def document(path):
    doc = Document()
    doc.feed(path.read_text(encoding='utf-8'))
    return list(doc.root.walk())


def mask_collection_valid(mask_section):
    links=[n for n in mask_section.walk() if n.tag=='a' and urlsplit(n.attrs.get('href','')).path=='/joseph-and-hyrum-death-masks']
    return (len(links)==2 and
            sum(any(c.tag=='img' for c in n.walk()) for n in links)==1 and
            sum(n.attrs.get('id')=='mask-collection-source' for n in links)==1)


def mask_collection_negative_test():
    url='https://churchhistorylibrary.churchofjesuschrist.org/joseph-and-hyrum-death-masks?lang=eng'
    good=f'<section><a href="{url}"><img src="masks.jpg"></a><a id="mask-collection-source" href="{url}">Explore the collection</a></section>'
    for markup, expected in [(good,True),(good.replace('</section>',f'<p><a href="{url}">Explore the collection again</a></p></section>'),False)]:
        doc=Document();doc.feed(markup)
        assert mask_collection_valid(next(n for n in doc.root.walk() if n.tag=='section'))==expected


def check():
    """Verify the approved bridge and exact relocation of the former likeness corpus."""
    from bs4 import BeautifulSoup
    import re,posixpath
    errors=[]
    def require(value,message):
        if not value:errors.append(PAGE+': '+message)
    routes=[PAGE,'joseph-smith-portrait-research.html','answers/who-was-joseph-smith.html']
    docs={r:BeautifulSoup((ROOT/r).read_text(encoding='utf-8'),'html.parser') for r in routes}
    bridge=docs[PAGE];research=docs[routes[1]];family=docs[routes[2]]
    from joseph_hero_contract import check_hero,check_grouping
    for route in routes[:2]:
        try:check_hero(route,docs[route])
        except AssertionError as error:require(False,str(error))
    try:check_grouping(research)
    except AssertionError as error:require(False,str(error))
    require(not bridge.select('main img, main figure'),'Bridge must not duplicate artwork ownership')
    require(len(bridge.select_one('main').get_text(' ',strip=True).split())<=500,'Bridge must remain concise')
    expected={'living-portrait':routes[1]+'#portrait-section-1','death-masks':routes[1]+'#portrait-section-4','joseph-mask-comparison':routes[1]+'#portrait-section-4','hyrum-mask-comparison':routes[1]+'#portrait-section-11','portraits-from-life':routes[1]+'#portrait-section-4','our-portrait':routes[1]+'#portrait-section-11','face-in-motion':routes[1]+'#research-feature-14','joseph-family-life':routes[2]+'#joseph-family-life','life-remembrance':routes[2]+'#life-remembrance','continue-study':routes[2]+'#continue-study','portrait-research':routes[1]}
    life=json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8-sig'))
    for scene in life['scenes']:expected['life-'+scene['id']]=routes[2]+'#life-'+scene['id']
    script=(ROOT/'joseph-study-bridge.js').read_text(encoding='utf-8');actual=json.loads(re.search(r'const routes=(\{.*?\});',script).group(1))
    require(actual==expected,'Exact legacy anchor routing differs from reviewed destinations')
    for old,destination in expected.items():
        node=bridge.find(id=old);require(node and node.select_one('a[href="'+destination+'"]'),'No-JS legacy destination missing: '+old)
        uri=urlsplit(destination);require(uri.path in docs and (not uri.fragment or docs[uri.path].find(id=uri.fragment)),'Legacy destination does not exist: '+old)
    for route,doc in docs.items():
        ids=[n['id'] for n in doc.select('[id]')];require(len(ids)==len(set(ids)),'Duplicate IDs in '+route)
    require(len(research.select('figure'))==81 and len(family.select('img'))>=20,'Complete illustrated journeys missing')
    require(len(research.select('.research-study-onward dl dd'))>=3 and len(family.select('.joseph-life-reflection'))>=10,'Guided reflections must survive relocation')
    for asset,sha in [(MASTER,MASTER_SHA),(HYRUM_DRAFT,HYRUM_DRAFT_SHA)]:
        require(hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()==sha,'Approved identity bytes changed: '+asset)
        require(research.select_one('a[href="'+asset+'"]') is not None,'Full identity source missing in portrait journey: '+asset)
    for entry in json.loads((ROOT/'docs/likeness-mask-comparison-review.json').read_text(encoding='utf-8'))['references']:
        require(hashlib.sha256((ROOT/entry['asset']).read_bytes()).hexdigest()==entry['sha256'],'Comparison provenance bytes changed')
    entries=json.loads((ROOT/'docs/art-study-image-review.json').read_text(encoding='utf-8'))['pages'][PAGE]
    require(len(entries)==5 and {e['slot'] for e in entries}==SLOTS,'Five prior reviewed scenes required')
    for entry in entries:
        asset=entry['asset'];owner=routes[2] if entry['slot']=='brothers' else routes[1];doc=docs[owner]
        require(entry['reviewed'] and entry.get('tone'),'Prior pixel/expression review missing')
        require(hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()==entry['sha256'],'Reviewed original bytes changed: '+asset)
        with Image.open(ROOT/asset) as image:require(image.format=='WEBP' and image.size==(entry['width'],entry['height']),'Reviewed dimensions changed')
        links=[a for a in doc.select('figure > a') if posixpath.normpath(posixpath.join(posixpath.dirname(owner),urlsplit(a.get('href','')).path))==asset]
        require(len(links)==1,'Original must have exactly one owning image action: '+asset)
        if links:
            a=links[0];require(a.get('aria-haspopup')=='dialog' and a.get('data-topic-study'),'Native detail and reading return missing')
            require(not any(a.has_attr(k) for k in ('data-full-image-viewer','data-hero-viewer','data-artwork-detail')),'Original bypasses study panel')
            figure=a.find_parent('figure');require(figure.select_one('figcaption a[href]') and a.select_one('img[alt]'),'Caption source or alternative text missing')
        thumb=ROOT/asset.replace('.webp','-960.webp')
        with Image.open(thumb) as image:require(image.format=='WEBP' and image.width==960,'Responsive original missing')
    for retired in ('museum-dibble-masks.jpg','joseph-death-mask.jpg','hyrum-death-mask.jpg'):
        require(not (ROOT/'assets/page-art/joseph-smith-likeness'/retired).exists(),'Withdrawn photo restored')
        require(all(retired not in str(doc) for doc in docs.values()),'Withdrawn photo display restored')
    # Exact reference placement/crops and all75+6 source-image signatures are checked independently.
    from joseph_research_narrative_qa import check_art_migration
    try:check_art_migration(research.select_one('#portrait-research'),ROOT)
    except AssertionError as error:require(False,str(error))
    require(research.select_one('a[href*="ask.html?topic=Joseph"]') is not None,'Contextual Ask path missing')
    require(family.select_one('a[href*="joseph-smith-portrait-research.html"]') is not None,'Family-to-portrait journey link missing')
    return errors


if __name__=='__main__':
    errors=check()
    if errors:raise SystemExit('\n'.join(errors))
    print('Joseph journeys PASS: exact legacy bridge destinations, unchanged five reviewed originals and identities, migrated sources, guidance and native image controls')
