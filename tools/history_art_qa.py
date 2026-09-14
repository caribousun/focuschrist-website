"""Check new historical study art contracts; actual pixel review remains separate."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'church-history.html'
SLOTS = ('richmond-rebuke', 'liberty-prayer', 'liberty-letter', 'porter-reunion',
         'relief-society', 'kirtland-bank', 'kirtland-temple', 'nauvoo-temple',
         'aaronic-priesthood', 'melchizedek-priesthood', 'nauvoo-legion',
         'joseph-baptizes-oliver', 'oliver-baptizes-joseph',
         'apostles-ordain-joseph', 'apostles-ordain-oliver')
SECTIONS = {'richmond-rebuke', 'liberty-jail-study', 'porter-rockwell',
            'relief-society-organization', 'kirtland-safety-society', 'kirtland-temple',
            'nauvoo-temple', 'aaronic-priesthood-restoration',
            'melchizedek-priesthood-restoration', 'nauvoo-legion'}
MASTER = 'assets/identities/joseph-smith-owner-approved-20260914.png'
MASTER_SHA = '518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827'


def check():
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(PAGE + ': ' + message)
    text = (ROOT / PAGE).read_text(encoding='utf-8')
    doc = Document(); doc.feed(text)
    nodes = list(doc.root.walk())
    ids = [n.attrs['id'] for n in nodes if n.attrs.get('id')]
    require(len(ids) == len(set(ids)), 'duplicate IDs')
    require(SECTIONS.issubset(ids), 'historical study anchors missing: ' + ', '.join(sorted(SECTIONS - set(ids))))
    figures = [n for n in nodes if n.tag == 'figure' and n.attrs.get('data-enriched-study-art', '').startswith('history-')]
    require(len(figures) == len(SLOTS), f'requires exactly {len(SLOTS)} new historical figures')
    require({n.attrs.get('data-enriched-study-art') for n in figures} == {'history-' + s for s in SLOTS}, 'figure inventory differs from the requested scenes')
    assets = set()
    for figure in figures:
        slot = figure.attrs.get('data-enriched-study-art', '').removeprefix('history-')
        expected = f'assets/page-art/church-history/{slot}.webp'
        require(figure.attrs.get('data-exclusive-artwork') == 'history-' + slot, slot + ': exclusive artwork marker missing')
        triggers = [n for n in figure.children if n.tag == 'a' and any(c.tag == 'img' for c in n.walk())]
        require(len(triggers) == 1, slot + ': requires one direct native image trigger')
        if triggers:
            trigger = triggers[0]
            require(urlsplit(trigger.attrs.get('href', '')).path == expected, slot + ': full asset path differs')
            require(trigger.attrs.get('aria-haspopup') == 'dialog', slot + ': dialog semantics missing')
            require(not any(k in trigger.attrs for k in ('data-artwork-detail', 'data-hero-viewer', 'data-full-image-viewer')), slot + ': bypasses native topic study panel')
            require(bool(trigger.attrs.get('data-topic-study')), slot + ': onward study missing')
            assets.add(expected)
        caption = next((n for n in figure.children if n.tag == 'figcaption'), None)
        require(caption is not None and len(caption.text().split()) >= 25, slot + ': substantive caption missing')
        require(caption is not None and any(n.tag == 'a' and urlsplit(n.attrs.get('href', '')).hostname in ('www.churchofjesuschrist.org', 'www.josephsmithpapers.org', 'churchhistorylibrary.churchofjesuschrist.org') for n in caption.walk()), slot + ': historical or scripture source missing')
        images = [n for n in figure.walk() if n.tag == 'img']
        require(len(images) == 1 and bool(images[0].attrs.get('alt')), slot + ': image alternative missing')
        thumb = ROOT / f'assets/page-art/church-history/{slot}-960.webp'
        require(thumb.is_file(), slot + ': responsive thumbnail missing')
        if thumb.is_file():
            with Image.open(thumb) as im:
                require(im.format == 'WEBP' and im.width == 960, slot + ': invalid thumbnail format or width')
    # Keep new pairs in their historical context and preserve the original scenes.
    section_nodes = {n.attrs.get('id'): n for n in nodes if n.tag == 'section'}
    pairs = {
        'aaronic-priesthood-restoration': ('aaronic-priesthood', 'joseph-baptizes-oliver', 'oliver-baptizes-joseph'),
        'melchizedek-priesthood-restoration': ('melchizedek-priesthood', 'apostles-ordain-joseph', 'apostles-ordain-oliver'),
    }
    for section_id, slots in pairs.items():
        section = section_nodes.get(section_id)
        if section is None:
            continue
        contained = list(section.walk())
        require([n.attrs.get('data-enriched-study-art') for n in contained if n.tag == 'figure'] == ['history-' + s for s in slots], section_id + ': original scene and two new scenes must remain together in order')
        pair = [n for n in contained if n.has('fc-priesthood-pair')]
        require(len(pair) == 1 and len([n for n in pair[0].children if n.tag == 'figure']) == 2, section_id + ': requires one two-scene pair')
        require(any(n.tag == 'details' and n.has('fc-priesthood-evidence') and any(c.tag == 'summary' for c in n.children) for n in contained), section_id + ': expandable source context missing')
    by_slot = {n.attrs.get('data-enriched-study-art'): n for n in figures}
    for slot, verses in [('joseph-baptizes-oliver', 'p70-p73'), ('oliver-baptizes-joseph', 'p71-p73')]:
        figure = by_slot.get('history-' + slot)
        if figure is None:
            continue
        source_links = [urlsplit(n.attrs.get('href', '')) for n in figure.walk() if n.tag == 'a']
        require(any(u.scheme == 'https' and u.hostname == 'www.churchofjesuschrist.org' and u.path == '/study/scriptures/pgp/js-h/1' and parse_qs(u.query).get('id') == [verses] and u.fragment == verses.split('-')[0] for u in source_links), slot + ': exact baptism source passage missing')
        expected = 'Joseph baptized Oliver first' if slot == 'joseph-baptizes-oliver' else 'Oliver then baptized Joseph'
        require(expected in figure.text(), slot + ': documented baptism sequence missing or reversed')
    melchizedek = section_nodes.get('melchizedek-priesthood-restoration')
    if melchizedek is not None:
        prose = melchizedek.text()
        require('do not establish the exact date' in prose and 'do not establish who came first' in prose, 'Melchizedek date and recipient-order uncertainty missing')
        require(not re.search(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+1829(?!\d)', prose), 'precise Melchizedek restoration date asserted')
        require(any(n.tag == 'a' and n.attrs.get('href') == 'https://www.churchofjesuschrist.org/study/history/topics/restoration-of-the-melchizedek-priesthood?lang=eng' for n in melchizedek.walk()), 'Melchizedek documentary dating source missing')
    entries = json.loads((ROOT / 'docs/art-study-image-review.json').read_text(encoding='utf-8'))['pages'].get(PAGE, [])
    require(len(entries) == len(SLOTS) and {e.get('slot') for e in entries} == set(SLOTS), f'{len(SLOTS)} scene review records required')
    require({e.get('asset') for e in entries} == assets, 'review ledger and native figure assets disagree')
    for entry in entries:
        asset = entry.get('asset', ''); path = (ROOT / asset).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'missing reviewed asset ' + asset)
        require(entry.get('reviewed') is True and bool(entry.get('tone')), 'pixel/expression review missing: ' + asset)
        if path.is_file() and path.is_relative_to(ROOT):
            require(hashlib.sha256(path.read_bytes()).hexdigest() == entry.get('sha256'), 'reviewed bytes changed: ' + asset)
            with Image.open(path) as im:
                require(im.format == 'WEBP' and im.size == (entry.get('width'), entry.get('height')), 'reviewed image dimensions/format differ: ' + asset)
    master = ROOT / MASTER
    require(master.is_file() and hashlib.sha256(master.read_bytes()).hexdigest() == MASTER_SHA, 'owner-locked Joseph master changed')
    links = [urlsplit(n.attrs.get('href', '')) for n in nodes if n.tag == 'a']
    for chapter, verses in [('121', 'p1-p9'), ('121', 'p41-p46'), ('122', 'p7-p9'), ('123', 'p17')]:
        require(any(u.hostname == 'www.churchofjesuschrist.org' and u.path == '/study/scriptures/dc-testament/dc/' + chapter and parse_qs(u.query).get('id') == [verses] and u.fragment == verses.split('-')[0] for u in links), 'contextual scripture passage missing: D&C ' + chapter + ' ' + verses)
    require('ART SLOT' not in text, 'pending historical artwork placeholder')
    return errors


if __name__ == '__main__':
    errors = check()
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'History art QA PASS: {len(SLOTS)} native scenes, reviewed asset hashes, locked Joseph identity, {len(SECTIONS)} study anchors and contextual D&C passages')
