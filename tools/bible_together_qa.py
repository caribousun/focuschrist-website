#!/usr/bin/env python3
"""Protect the scoped Bible/Book of Mormon enrichment and its reviewed inventory.

Visual age, likeness, semantic scene review and rendered layout remain separate gates.
This checks the selected review evidence, not owner approval.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit, urljoin
from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'answers/bible-and-book-of-mormon-together.html'
BASE = 'https://focuschrist.com/' + PAGE
EXPECTED = {
    'moses-brass-serpent': ('ot/num/21', 'bofm/alma/33'),
    'ezekiel-two-sticks': ('ot/ezek/37', 'bofm/2-ne/3'),
    'lehi-joseph-counsel': ('bofm/2-ne/3', 'ot/gen/50'),
    'alma-preserves-abinadi': ('bofm/mosiah/17', 'bofm/mosiah/14', 'ot/isa/53'),
    'nephi-reads-isaiah': ('bofm/1-ne/19', 'bofm/1-ne/20', 'ot/isa/48'),
    'isaiah-call': ('ot/isa/6', 'bofm/2-ne/16'),
    'moroni-quotes-malachi': ('pgp/js-h/1', 'ot/mal/3', 'ot/mal/4'),
    'mosiah-engraved-stone': ('bofm/omni/1', 'ot/gen/11'),
    'christ-isaiah-nazareth': ('nt/luke/4', 'bofm/3-ne/23'),
    'christ-wilderness-temptation': ('nt/matt/4', 'bofm/mosiah/15'),
    'christ-roof-paralytic': ('nt/mark/2', 'bofm/mosiah/3'),
    'christ-sabbath-grainfield': ('nt/mark/2', 'bofm/3-ne/15'),
    'christ-heals-servant-ear': ('nt/luke/22', 'nt/john/18', 'bofm/3-ne/12'),
}
PRESERVED = {
    'assets/page-art/exclusive/bible-bountiful-witness-1536.webp': '1d70739ea2056688d9f924adc028ef7ff9d648837ddbf7bb90e92954ac7a8126',
    'assets/page-art/topics/paired-scripture-study-1536.webp': 'b591ce2407b479d825b5721ad35e36d80d4567ad42f58473cfe1f5dc599fbd57',
    'assets/page-art/exclusive/two-witnesses-observation-1536.webp': '76cd0387261a7ed5254c000dfda64956e958b3f9089075f262719fd85357bf1c',
    'assets/page-art/exclusive/two-witnesses-readers-1536.webp': 'b667c0fb89dbf9d4ad850f4d56a88cd7cfa1e2190ad766dd67f0222f14810ba6',
    'assets/page-art/exclusive/two-witnesses-charity-1536.webp': 'e58ea4a69155688a2529c3574a6fcc8b2169ff9c2434d9d044b067ba9afec7d2',
    'assets/page-art/sitewide-narratives/two-witnesses-emmaus-20260919-full.webp': '4689447ec8cda332762eea5f62d89666a730174642f7cc290e9ed6e74603cce8',
}
HERO = {
    'assets/heroes/topics/bible-bom-desktop.webp': '7d09e685da7441da02daa1c1c622ef38de04bcdf22b0976509dff276290379e7',
    'assets/heroes/topics/bible-bom-full.webp': 'f0631b714acabdd729e90ee95858c1d107ff90efe509fe7c89adc4788f4e144a',
    'assets/heroes/topics/bible-bom-mobile.webp': '200bcf82ca5f3f2ff01b88a3ffc3294cb08560a1c6b42655287fc5fed549e479',
}
OLD_HEADINGS = {
    "The Bible Records God's Dealings with His People",
    'The Book of Mormon Adds Another Historical Witness',
    'They Reinforce Shared Doctrines',
    'They Also Preserve Different Voices and Settings',
    'A Practical Way to Study Them Together',
    'Read Two Short Passages Side by Side',
    'Compare Without Losing the Context',
}


def ancestors(node):
    while node.parent:
        node = node.parent
        yield node


def scripture_url(path, verses):
    url = 'https://www.churchofjesuschrist.org/study/scriptures/' + path + '?lang=eng'
    if verses:
        first, *last = verses.split('-')
        url += '&id=p' + first + ('-p' + last[0] if last else '') + '#p' + first
    return url


def check(html, manifest, files=True):
    def require(ok, reason):
        if not ok:
            raise AssertionError(reason)
    doc = Document(); doc.feed(html)
    nodes = list(doc.root.walk())
    main = next(n for n in nodes if n.tag == 'main')
    ids = [n.attrs['id'] for n in nodes if 'id' in n.attrs]
    require(len(ids) == len(set(ids)), 'Duplicate page IDs')
    id_nodes = {n.attrs['id']: n for n in nodes if 'id' in n.attrs}
    entries = manifest['artworks']
    review = {e['key']: e for e in entries}
    require(manifest['page'] == PAGE and len(entries) == 13 and set(review) == set(EXPECTED), 'Exact thirteen reviewed scene inventory required')
    require(len({e['asset'] for e in entries}) == 13 and len({e['sha256'] for e in entries}) == 13, 'New originals must be distinct')
    figures = [n for n in main.walk() if n.tag == 'figure' and 'data-bible-original' in n.attrs]
    require(Counter(n.attrs['data-bible-original'] for n in figures) == Counter(EXPECTED.keys()), 'Every new scene must occur exactly once')
    links = [n for n in nodes if n.tag == 'a' and n.attrs.get('href')]
    body_assets = [urlsplit(urljoin(BASE, n.attrs['href'])).path.lstrip('/') for n in links if n.parent.tag == 'figure' and any(c.tag == 'img' for c in n.walk())]
    require(all(body_assets.count(asset) == 1 for asset in PRESERVED), 'Six existing body originals must remain once each')
    require(len(body_assets) == 19, 'Exactly six preserved plus thirteen new body originals required')
    hero = next(n for n in links if n.attrs.get('data-hero-record') == 'topic-bible-bom')
    require(hero.attrs.get('href') == '../assets/heroes/topics/bible-bom-full.webp', 'Preserve full hero destination')
    for variant in ('desktop', 'mobile'):
        require(f"--topic-hero-{variant}:url('../assets/heroes/topics/bible-bom-{variant}.webp')" in hero.attrs.get('style', ''), 'Preserve responsive hero CSS assets')
    groups = Counter()
    for figure in figures:
        key = figure.attrs['data-bible-original']; record = review[key]
        require(record.get('reviewed') is True and record.get('technical_review_passed') is True, key + ': review required')
        require(all(record.get(k) for k in ('scene', 'relationship', 'interpretation', 'independent_review')), key + ': semantic/source review evidence required')
        sections = [n for n in ancestors(figure) if n.tag == 'section']
        require(len(sections) >= 2 and sections[0].has('fc-bible-scene'), key + ': needs its own closest scene section')
        scene = sections[0]
        groups[sections[-1].attrs.get('id')] += 1
        heading = next((n for n in scene.walk() if n.tag in ('h2', 'h3') and not any(a.tag == 'figure' for a in ancestors(n))), None)
        require(heading is not None and heading.attrs.get('id') and scene.attrs.get('aria-labelledby') == heading.attrs['id'], key + ': unique accessible lesson target required')
        trigger = next(n for n in figure.children if n.tag == 'a')
        require(trigger.attrs.get('href') == '../' + record['asset'], key + ': selected full image mismatch')
        require(trigger.attrs.get('aria-haspopup') == 'dialog' and 'data-full-image-viewer' not in trigger.attrs, key + ': study must open first')
        require(not trigger.attrs.get('data-topic-study') or ('#' not in trigger.attrs['data-topic-study'] and trigger.attrs['data-topic-study'].split('/')[-1] != PAGE.split('/')[-1]), key + ': onward study must not trap the viewer on a same-page fragment')
        caption = next(n for n in figure.children if n.tag == 'figcaption')
        source_links = {n.attrs['href'] for n in caption.walk() if n.tag == 'a'}
        expected_links = {scripture_url(path, verses) for path, label, verses in record['source_references']}
        require(expected_links <= source_links and record['source_url'] in source_links, key + ': exact reviewed source links missing')
        require(set(EXPECTED[key]) <= {r[0] for r in record['source_references']}, key + ': source-specific event lost')
        img = next(n for n in trigger.walk() if n.tag == 'img')
        require(img.attrs.get('src') == '../' + record['thumbnail'] and img.attrs.get('alt', '').strip(), key + ': thumbnail/alternative text missing')
    require(groups == Counter({'bible-history': 2, 'book-of-mormon-history': 3, 'prophets-and-records': 3, 'christ-in-both-records': 5}), 'Pictures must retain the reviewed 2/3/3/5 distribution')
    run = 0
    for n in main.children:
        if n.tag == 'h2':
            run += 1
            require(n.text().strip() not in OLD_HEADINGS, 'Redundant text-wall heading returned')
            require(run < 7, 'Seven consecutive text-only heading blocks returned')
        elif n.tag not in ('p', 'h3', 'ul', 'ol'):
            run = 0
    cross = id_nodes['cross-reference-guide']
    require(sum(n.tag == 'details' and n.has('fc-bible-reference') for n in cross.walk()) == 12, 'Twelve compact paired reading disclosures required')
    for n in links:
        dest = urlsplit(urljoin(BASE, n.attrs['href']))
        if dest.netloc == 'focuschrist.com' and dest.path == '/' + PAGE and dest.fragment:
            require(dest.fragment in id_nodes, 'Broken same-page link: ' + n.attrs['href'])
    joseph = review['moroni-quotes-malachi']
    require(joseph.get('event_age', {}).get('Joseph Smith') == 17, 'Joseph event age must be seventeen')
    require(joseph['original_generation'] == 'exec-85cc0924-c01e-4884-b6ae-b021ae02a066.png', 'Rejected mature Joseph version must not return')
    require('assets/identities/joseph-smith-owner-approved-20260914.png' in joseph['identity_references'], 'Joseph exact identity reference required')
    require(joseph.get('corrections', [])[-1]['selected'] == joseph['original_generation'], 'Age correction must be the selected image')
    if files:
        hashes = {**PRESERVED, **HERO}
        for record in entries:
            hashes[record['asset']] = record['sha256']
            hashes[record['thumbnail']] = record['thumbnail_sha256']
        for asset, expected in hashes.items():
            require(hashlib.sha256((ROOT / asset).read_bytes()).hexdigest() == expected, 'Reviewed pixels changed: ' + asset)
        pixel_hashes = []
        for asset in body_assets + ['assets/heroes/topics/bible-bom-full.webp']:
            with Image.open(ROOT / asset) as im:
                pixel_hashes.append(hashlib.sha256(str(im.size).encode() + im.convert('RGB').tobytes()).hexdigest())
        require(len(set(pixel_hashes)) == 20, 'Decoded duplicate original artwork')
        # Check ownership by actual image placement. A linked reference to the owner is allowed.
        asset_names = {e['asset'] for e in entries} | {e['thumbnail'] for e in entries}
        for other in ROOT.rglob('*.html'):
            if other == ROOT / PAGE or any(p in other.relative_to(ROOT).parts for p in ('node_modules', '.git', 'work')):
                continue
            text = other.read_text(encoding='utf-8')
            if not any(Path(a).name in text for a in asset_names):
                continue
            other_doc = Document(); other_doc.feed(text)
            other_base = 'https://focuschrist.com/' + other.relative_to(ROOT).as_posix()
            for img in (n for n in other_doc.root.walk() if n.tag == 'img'):
                path = urlsplit(urljoin(other_base, img.attrs.get('src', ''))).path.lstrip('/')
                if path in asset_names:
                    enclosing = next((n for n in ancestors(img) if n.tag == 'a'), None)
                    require(enclosing is not None and urlsplit(urljoin(other_base, enclosing.attrs.get('href', ''))).path == '/' + PAGE, 'New artwork reused as another page owner: ' + str(other))


if __name__ == '__main__':
    html = (ROOT / PAGE).read_text(encoding='utf-8')
    manifest = json.loads((ROOT / 'docs/bible-together-art-review.json').read_text(encoding='utf-8'))
    check(html, manifest)
    if '--self-test' in sys.argv:
        fixtures = [
            html.replace('data-bible-original="moses-brass-serpent"', 'data-bible-original="wrong-scene"', 1),
            html.replace('--topic-hero-mobile:', '--removed-hero-mobile:', 1),
            html.replace('id="bible-history"', 'id="main-content"', 1),
            html.replace('../assets/page-art/exclusive/two-witnesses-charity-1536.webp', '../missing-preserved.webp'),
            html.replace('</main>', '<h2>The Bible Records God\'s Dealings with His People</h2></main>'),
            html.replace('class="fc-bible-scene" id="study-isaiah-call"', 'class="lost-scene" id="study-isaiah-call"', 1),
            html.replace('aria-haspopup="dialog"', 'aria-haspopup="dialog" data-topic-study="bible-and-book-of-mormon-together.html#bible-history"'),
        ]
        for fixture in fixtures:
            try:
                check(fixture, manifest, files=False)
            except AssertionError:
                continue
            raise AssertionError('Regression fixture was not rejected')
        wrong_age = json.loads(json.dumps(manifest))
        next(e for e in wrong_age['artworks'] if e['key'] == 'moroni-quotes-malachi')['event_age']['Joseph Smith'] = 24
        try:
            check(html, wrong_age, files=False)
        except AssertionError:
            pass
        else:
            raise AssertionError('Incorrect Joseph event age was not rejected')
    print('BIBLE TOGETHER QA PASS: 7 preserved originals, 13 reviewed additions, 2/3/3/5 scene distribution, local lesson returns and 12 paired readings')
