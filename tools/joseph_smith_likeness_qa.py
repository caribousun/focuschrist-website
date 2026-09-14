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
SLOTS = {'portrait-sitting', 'writing', 'warmth', 'conversation'}
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


def check():
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(PAGE + ': ' + message)

    path = ROOT / PAGE
    if not path.is_file():
        return [PAGE + ': missing dedicated study page']
    nodes = document(path)
    ids = [n.attrs['id'] for n in nodes if n.attrs.get('id')]
    require(len(ids) == len(set(ids)), 'duplicate IDs')
    require(SECTIONS.issubset(ids), 'missing study sections: ' + ', '.join(sorted(SECTIONS - set(ids))))
    navlinks = {n.attrs.get('href') for nav in nodes if nav.tag == 'nav'
                for n in nav.walk() if n.tag == 'a'}
    require({'#' + s for s in SECTIONS}.issubset(navlinks), 'six study navigation destinations required')
    reflections = [n for n in nodes if n.tag == 'details' and n.has('likeness-reflection')]
    require(len(reflections) >= 3, 'at least three guided reflections required')
    for reflection in reflections:
        summary = next((n for n in reflection.children if n.tag == 'summary'), None)
        require(summary is not None and bool(summary.text().strip()), 'reflection summary missing')
        require(any(n.tag == 'p' and n.text().strip() for n in reflection.walk()), 'reflection prompt missing')

    heroes = [n for n in nodes if n.tag == 'a' and 'data-hero-viewer' in n.attrs]
    require(len(heroes) == 1 and urlsplit(heroes[0].attrs.get('href', '')).path == MASTER,
            'hero must open the exact approved Joseph master')
    require(len(heroes) == 1 and heroes[0].attrs.get('data-hero-record') == 'joseph-likeness',
            'approved hero must bind its historical study record')
    master = ROOT / MASTER
    require(master.is_file() and hashlib.sha256(master.read_bytes()).hexdigest() == MASTER_SHA,
            'owner-approved Joseph master bytes changed')
    scripts = [n.attrs.get('src', '') for n in nodes if n.tag == 'script']
    styles = [n.attrs.get('href', '') for n in nodes if n.tag == 'link']
    require(any(urlsplit(s).path == 'topic-artwork-details.js' for s in scripts), 'native artwork panel script missing')
    require(any(urlsplit(s).path == 'topic-artwork-details.css' for s in styles), 'native artwork panel stylesheet missing')
    figures = [n for n in nodes if n.tag == 'figure' and n.attrs.get('data-enriched-study-art', '').startswith('likeness-')]
    require(len(figures) == 4 and {n.attrs['data-enriched-study-art'] for n in figures} == {'likeness-' + s for s in SLOTS},
            'four creative scene inventory differs')
    expected_assets = {f'assets/page-art/joseph-smith-likeness/{s}.webp' for s in SLOTS}
    for figure in figures:
        slot = figure.attrs['data-enriched-study-art'].removeprefix('likeness-')
        asset = f'assets/page-art/joseph-smith-likeness/{slot}.webp'
        require(figure.attrs.get('data-exclusive-artwork') == 'likeness-' + slot, slot + ': exclusive marker missing')
        triggers = [n for n in figure.children if n.tag == 'a' and any(c.tag == 'img' for c in n.walk())]
        require(len(triggers) == 1, slot + ': one direct native image trigger required')
        if triggers:
            trigger = triggers[0]
            require(urlsplit(trigger.attrs.get('href', '')).path == asset, slot + ': wrong full-size asset')
            require(trigger.attrs.get('aria-haspopup') == 'dialog', slot + ': dialog semantics missing')
            require(not any(k in trigger.attrs for k in ('data-full-image-viewer', 'data-hero-viewer', 'data-artwork-detail')),
                    slot + ': bypasses normal study panel')
            require(bool(trigger.attrs.get('data-topic-study')), slot + ': onward study missing')
        caption = next((n for n in figure.children if n.tag == 'figcaption'), None)
        require(caption is not None and bool(caption.text().strip()), slot + ': caption missing')
        if caption is not None:
            require(any(n.tag == 'a' and urlsplit(n.attrs.get('href', '')).hostname in
                        {'www.churchofjesuschrist.org', 'www.josephsmithpapers.org', 'churchhistorylibrary.churchofjesuschrist.org'}
                        for n in caption.walk()), slot + ': source link missing')
        images = [n for n in figure.walk() if n.tag == 'img']
        require(len(images) == 1 and bool(images[0].attrs.get('alt')), slot + ': image alternative missing')
        thumb = ROOT / f'assets/page-art/joseph-smith-likeness/{slot}-960.webp'
        require(thumb.is_file(), slot + ': responsive image missing')
        if thumb.is_file():
            with Image.open(thumb) as im:
                require(im.format == 'WEBP' and im.width == 960, slot + ': invalid responsive image')

    entries = json.loads((ROOT / 'docs/art-study-image-review.json').read_text(encoding='utf-8'))['pages'].get(PAGE, [])
    require(len(entries) == 4 and {e.get('slot') for e in entries} == SLOTS, 'four scene review records required')
    require({e.get('asset') for e in entries} == expected_assets, 'reviewed assets differ from scene contract')
    for entry in entries:
        asset = entry.get('asset', '')
        image_path = (ROOT / asset).resolve()
        require(image_path.is_relative_to(ROOT) and image_path.is_file(), 'reviewed asset missing: ' + asset)
        require(entry.get('reviewed') is True and bool(entry.get('tone')), 'pixel/expression review missing: ' + asset)
        if image_path.is_relative_to(ROOT) and image_path.is_file():
            require(hashlib.sha256(image_path.read_bytes()).hexdigest() == entry.get('sha256'), 'reviewed bytes changed: ' + asset)
            with Image.open(image_path) as im:
                require(im.format == 'WEBP' and im.size == (entry.get('width'), entry.get('height')), 'reviewed dimensions differ: ' + asset)
    for other in ROOT.rglob('*.html'):
        if other == path or '.git' in other.parts:
            continue
        text = other.read_text(encoding='utf-8')
        require(not any(asset in text for asset in expected_assets), 'creative artwork reused in ' + other.relative_to(ROOT).as_posix())

    links = [urlsplit(n.attrs.get('href', '')) for n in nodes if n.tag == 'a']
    require(SOURCES.issubset({(u.hostname, u.path) for u in links}), 'required primary/institutional sources missing')
    require(any(u.path.lstrip('/') == 'ask.html' and (u.query or u.fragment) for u in links), 'contextual Ask route missing')
    for linked in ('church-history.html', 'answers/who-was-joseph-smith.html'):
        require(any(u.path.lstrip('/') == linked for u in links), 'return link missing: ' + linked)
        require(any(n.tag == 'a' and urlsplit(n.attrs.get('href', '')).path.rstrip('/').endswith(PAGE)
                    for n in document(ROOT / linked)), 'reciprocal link missing from ' + linked)
    require(any(n.has('fc-resource-card') and any(c.tag == 'img' for c in n.walk()) and
                any(c.tag == 'a' and urlsplit(c.attrs.get('href', '')).hostname == 'churchhistorylibrary.churchofjesuschrist.org'
                    for c in n.walk()) for n in nodes), 'separate museum source thumbnail/card missing')
    return errors


if __name__ == '__main__':
    errors = check()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Joseph Smith likeness QA PASS: approved hero, four reviewed native artwork panels, six study stops, reflections, primary sources and reciprocal routes')
