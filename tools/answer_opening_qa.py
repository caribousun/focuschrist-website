"""Exact Answer opening inventory and preserved-art contract; rendering is separate."""
from pathlib import Path
import hashlib,json,re,copy
from scripture_reference_preservation_qa import normalize_reviewed_reference
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASELINE=json.loads((ROOT/'docs/answer-opening-baseline.json').read_text(encoding='utf8'))
COVENANT='answers/abrahamic-covenant.html'
SOURCE='answers/race-priesthood-and-temple-blessings.html'
LOOK='answers/look-unto-me-doctrine-and-covenants-6-36.html'
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def check():
    records=BASELINE['pages']
    assert BASELINE['commit']=='9e95856dc14ce2e41830c2445ffff96a5f8fe39e'
    actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'answers').glob('*.html')}
    assert actual==set(records) and len(actual)==25, 'All 25 Answer openings must be inventoried'
    topics={p for p,r in records.items() if r['kind']=='fc-topic-opening'}
    assert len(topics)==23 and actual-topics=={COVENANT,SOURCE}
    for name,r in records.items():
        doc=BeautifulSoup((ROOT/name).read_text(encoding='utf8'),'html.parser')
        openings=doc.select('.fc-topic-opening,.jj-opening,.fc-source-opening')
        assert len(openings)==1 and r['kind'] in openings[0].get('class',[]),name
        header=openings[0]
        if name==LOOK:
            main=doc.select_one('main#main-content')
            continuation=main.find(recursive=False)
            assert continuation and 'fc-opening-continuation' in continuation.get('class',[])
            action=continuation.select_one(':scope > .fc-actions')
            assert action and action.get('class')==['fc-actions','fc-actions--center','fc-actions--content'], 'Retained actions require the established content gap'
            action['class']=['fc-actions','fc-actions--center'] # Only the reviewed spacing class is normalized for the original content hash.
            blocks=continuation.find_all(recursive=False)
            assert len(blocks)==3 and digest(''.join(str(b) for b in blocks))==r['continuation_blocks_sha256'], 'Preserve both introduction paragraphs and all secondary actions in order'
            assert not header.select('.fc-page-intro-copy,.fc-actions'), 'Retained introduction must follow Continue in main'
        if name in topics:
            cue=header.select_one('a.fc-scroll-cue[href="#main-content"]')
            assert cue and doc.select_one('#main-content'),name+': valid Continue'
        elif name==COVENANT:
            assert not header.select('a[href="/answers.html"]'), 'Owner removed Covenant opening breadcrumb'
            cues=header.select('a.fc-covenant-continue')
            assert len(cues)==1 and cues[0].get('href')=='#a-promise-to-live-by'
            assert doc.select_one('#a-promise-to-live-by') and 'fc-button' not in cues[0].get('class',[])
            cues[0].decompose() # Only this reviewed action replaces the previously hidden Begin.
        else:assert header.select_one('a[href="#begin-study"]') and doc.select_one('#begin-study')
        if name==SOURCE:
            green=header.select('a[href="#green-flake"]')
            assert len(green)==1 and green[0].get_text(strip=True)=='Green Flake' and doc.select_one('section#green-flake'), 'Only reviewed Green Flake directory addition allowed'
            green[0].decompose()
            pictures=json.loads((ROOT/'docs/priesthood-history/body-pictures.json').read_text(encoding='utf8'))
            expected={('/'+p['asset']):p for p in pictures}
            assert len(expected)==len(pictures), 'Generated study assets must be unique'
            added=[i for i in doc.select('img') if i.get('src','').startswith('/assets/page-art/priesthood-history/')]
            assert len(added)==len(expected) and {i['src'] for i in added}==set(expected), 'Study images must exactly match reviewed manifest'
            for img in added:
                picture=expected[img['src']]
                assert img.get('alt')==picture['alt'] and img.get('width')==str(picture['width']) and img.get('height')==str(picture['height']), 'Preserve manifest image description and dimensions'
                assert img.get('loading')=='lazy' and img.get('decoding')=='async'
                assert hashlib.sha256((ROOT/picture['asset']).read_bytes()).hexdigest()==picture['sha256'], 'Preserve exact reviewed image bytes'
                img.decompose()
            assert len(doc.select('img'))==6, 'Preserve six original official media previews'
        assert digest(str(header))==r['opening_sha256'],name+': opening copy/hero markup changed'
        images=copy.deepcopy(doc)
        if images.select('[data-linked-study-reference="modern-scripture"]'):
            normalize_reviewed_reference(images) # Exact retired preview only; retain original whole-image digest.
        assert digest(''.join(str(i) for i in images.select('img')))==r['images_sha256'],name+': approved image references/attributes changed'
        for css,owned in [('answer-opening.css',name in topics),('covenant-opening.css',name==COVENANT)]:
            links=[l for l in doc.select('link[rel="stylesheet"]') if css in l.get('href','')]
            assert len(links)==int(owned),name+': wrong opening stylesheet ownership'
            if links:assert links[0]['href']=='../'+css+'?v='+('20260930-boundary-4' if name==COVENANT else '20260930-2')
    css=(ROOT/'answer-opening.css').read_text(encoding='utf8')
    clean=re.sub(r'/\*.*?\*/','',css,flags=re.S).strip()
    assert clean.startswith('@media (min-width: 701px) {') and clean.count('@media')==1
    inner=clean[clean.index('{')+1:-1]
    rules=re.findall(r'([^{}]+)\{([^{}]*)\}',inner)
    assert rules and not re.sub(r'[^{}]+\{[^{}]*\}','',inner).strip()
    for selector,body in rules:
        assert selector.strip().startswith('body.fc-site.fc-topic-page .fc-topic-opening .fc-page-intro')
        assert '.fc-visual-hero' not in selector, 'Do not resize, crop or hide the hero/content'
        allowed={'padding','gap','margin','font-size','line-height'}
        if selector.strip().endswith('.fc-father-opening-guide'):allowed.add('max-width')
        assert set(re.findall(r'([\w-]+)\s*:',body)) <= allowed
    for p in ROOT.rglob('*.html'):
        if any(x in p.parts for x in ('.git','node_modules','focuschrist-repo')):continue
        if p.relative_to(ROOT).as_posix() in actual:continue
        assert not re.search(r'href=["\'][^"\']*(?:answer-opening|covenant-opening)\.css',p.read_text(encoding='utf8')),p
    print('ANSWER OPENING QA PASS: exact23 image openings + Covenant + source study; preserved opening/art markup, scoped desktop spacing and valid Continue targets; rendered fit is separate')
if __name__=='__main__':check()
