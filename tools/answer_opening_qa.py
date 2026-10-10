"""Exact Answer opening inventory and preserved-art contract; rendering is separate."""
from pathlib import Path
import hashlib,json,re,copy
from scripture_reference_preservation_qa import normalize_reviewed_reference
from bs4 import BeautifulSoup
from hero_introductions_qa import ROUTES as INTRODUCTION_ROUTES, assert_current_opening, restore_reviewed_opening
ROOT=Path(__file__).resolve().parents[1]
BASELINE=json.loads((ROOT/'docs/answer-opening-baseline.json').read_text(encoding='utf8'))
COVENANT='answers/abrahamic-covenant.html'
SOURCE='answers/race-priesthood-and-temple-blessings.html'
LOOK='answers/look-unto-me-doctrine-and-covenants-6-36.html'
def digest(text):return hashlib.sha256(text.encode()).hexdigest()

REVIEWED_READING_ADDITIONS = {'answers/stand-forever.html': [{'src': '../assets/page-art/stand-forever-journey/stand-john6-remain-960.webp', 'markup_sha256': '0541ea5722ab1bd9459d0f8c8a12e6488c0852c444da5f6cb3ec21ebedfc9051', 'asset_sha256': 'bcbfa7bb0face64659185fe097bf8ae213e100b14b3de8765a549b15dc113aab'}, {'src': '../assets/page-art/stand-forever-journey/stand-john7-do-his-will-960.webp', 'markup_sha256': '16ffff2374bbac3a89e9278c77bd842925400264d3b4cc061142045dc7433285', 'asset_sha256': '43be5dbb873b53460c987d8cfc06a6342a1c5f2c208da6e3fa3cb8d2828f31b8'}], 'answers/why-latter-day-saints-build-temples.html': [{'src': '../assets/page-art/visual-rhythm-journey/temple-tribute-960.webp', 'markup_sha256': 'a3eccad0b5981b33237447d3ab74e06278e941e6fa593b5feb9cc3da16e6a5d1', 'asset_sha256': 'fc1dff1127af137bdf0cf20d3da8833b6b6180940aa7dd019106bb022f5e050a'}]}

def remove_reviewed_reading_additions(name, images):
    rows = REVIEWED_READING_ADDITIONS.get(name, [])
    for row in rows:
        found = images.select('img[src="' + row['src'] + '"]')
        assert len(found) == 1 and digest(str(found[0])) == row['markup_sha256'], name + ': exact new body image markup required'
        assert hashlib.sha256(((ROOT/name).parent/row['src']).read_bytes()).hexdigest() == row['asset_sha256'], name + ': body image bytes changed'
        found[0].decompose()

def reading_additions_self_test():
    for route, rows in REVIEWED_READING_ADDITIONS.items():
        original = (ROOT/route).read_text(encoding='utf8')
        for row in rows:
            doc = BeautifulSoup(original, 'html.parser')
            img = doc.select_one('img[src="' + row['src'] + '"]')
            mutations = []
            duplicate = copy.deepcopy(doc); duplicate.append(copy.deepcopy(img)); mutations.append(duplicate)
            missing = copy.deepcopy(doc); missing.select_one('img[src="' + row['src'] + '"]').decompose(); mutations.append(missing)
            changed = copy.deepcopy(doc); changed.select_one('img[src="' + row['src'] + '"]')['alt'] = 'unreviewed'; mutations.append(changed)
            for mutation in mutations:
                try: remove_reviewed_reading_additions(route, mutation)
                except AssertionError: pass
                else: raise AssertionError('Changed/duplicate/missing body image escaped exact inverse')

def check():
    from first_topic_completion_qa import check as check_first_topic_completion
    first_topic_review = check_first_topic_completion(ROOT)
    reading_additions_self_test()
    records=BASELINE['pages']
    assert BASELINE['commit']=='9e95856dc14ce2e41830c2445ffff96a5f8fe39e'
    actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'answers').glob('*.html')}
    assert actual==set(records) and len(actual)==25, 'All 25 Answer openings must be inventoried'
    topics={p for p,r in records.items() if r['kind']=='fc-topic-opening'}
    assert len(topics)==23 and actual-topics=={COVENANT,SOURCE}
    for name,r in records.items():
        source=(ROOT/name).read_text(encoding='utf8')
        if name in INTRODUCTION_ROUTES:
            assert_current_opening(name,source)
            source=restore_reviewed_opening(name,source)
        doc=BeautifulSoup(source,'html.parser')
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
        remove_reviewed_reading_additions(name, images)
        expected_first = {r['responsive']: r for r in first_topic_review.values() if r['route'] == name}
        first_images = [i for i in images.select('img') if 'first-topic-completion/' in i.get('src', '')]
        assert len(first_images) == len(expected_first) and {i.get('src', '').removeprefix('../') for i in first_images} == set(expected_first), name+': exact validated FIRST additions required'
        for img in first_images:
            img.decompose() # Only strict hash/source/ownership-validated additions are excluded from the unchanged historical digest.
        if images.select('[data-linked-study-reference="modern-scripture"]'):
            normalize_reviewed_reference(images) # Exact retired preview only; retain original whole-image digest.
        expected_images = r['images_sha256']
        if name == 'answers/who-was-joseph-smith.html':
            # Preserve the historical baseline while binding the separately reviewed
            # eight corrected family artwork references and the approved warm-gaze alt.
            assert expected_images == '0496e9a59b12f44514a70b236853e705b8cb17c2f0f5132c600a3307cdf1ae4f'
            assert len(images.select('img')) == 36, 'Exact reviewed Joseph image inventory required'
            expected_images = '73bc4c791ee95bd0d275bc36d5efc77c4fdea2aaf6f4e6848f0fc293d7190fd5'
        assert digest(''.join(str(i) for i in images.select('img')))==expected_images,name+': approved image references/attributes changed'
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
