"""Focused Answers routing, contextual study and preserved-image regression gate.

Counts validate structure, not editorial richness, photographic quality or owner approval.
The closed baseline permits CI shallow checkouts without requiring Git history.
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
NEW = {f'answers/{kind}-priesthood-restoration.html' for kind in ('aaronic', 'melchizedek')}

def document(path):
    doc = Document()
    doc.feed(path.read_text(encoding='utf-8'))
    return list(doc.root.walk())

def local(page, url):
    part = urlsplit(url).path
    target = (ROOT / part.lstrip('/') if part.startswith('/') else page.parent / part).resolve()
    assert target.is_relative_to(ROOT), f'Nonlocal asset {url}'
    assert target.is_file(), f'Missing asset {target.relative_to(ROOT)}'
    return target

def opening(page, nodes):
    heroes = [n for n in nodes if n.tag == 'a' and 'data-hero-viewer' in n.attrs]
    if heroes:
        assert len(heroes) == 1, f'{page.name}: duplicate hero'
        return local(page, heroes[0].attrs['href'])
    if page.name == 'come-follow-me.html':
        assert any(n.has('cfm-hero') for n in nodes), 'CFM opening missing'
        css = (ROOT/'come-follow-me.css').read_text(encoding='utf-8')
        match = re.search(r'\.cfm-hero\s*\{[^}]*url\([\"\x27]?([^\"\x27)]+)', css)
        assert match, 'CFM actual CSS hero missing'
        return local(ROOT/'come-follow-me.css', match[1])
    if page.name == 'general-conference.html':
        header = next(n for n in nodes if n.has('gc-page-opening'))
        images = [n for n in header.walk() if n.tag == 'img']
        assert len(images) == 1, 'Conference must preserve one bounded opening picture'
        trigger = images[0].parent
        while trigger and trigger.tag != 'a': trigger = trigger.parent
        assert trigger and trigger.attrs.get('aria-haspopup') == 'dialog', 'Conference opening study trigger missing'
        assert 'data-full-image-viewer' not in trigger.attrs, 'Conference opening must show study before full size'
        return local(page, trigger.attrs['href'])
    raise AssertionError(f'{page.name}: no supported topic opening')

def check():
    errors = []
    reviewed = json.loads((ROOT/'tools/focused_answers_baseline.json').read_text(encoding='utf-8'))['reviewed_stylesheets']
    assert set(reviewed) == {'focused-answers.css'}, 'Unexpected reviewed stylesheet'
    for name, digest in reviewed.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name + ': differs from reviewed CSS'
    nodes = document(ROOT/'answers.html')
    directory = next(n for n in nodes if n.has('fc-answers-jump-links'))
    routes = [n.attrs['href'] for n in directory.walk() if n.tag == 'a']
    assert len(routes) == len(set(routes)) == 28, 'Exact 28 unique topic destinations required'
    assert NEW <= set(routes), 'Both priesthood topics must own their destination'
    assert all(not urlsplit(r).fragment and not urlsplit(r).scheme and r.endswith('.html') for r in routes), 'Topic pills must open own pages'
    pixels = {}; pages = {}
    for route in routes:
        page = local(ROOT/'answers.html', route); ns = document(page); pages[route] = ns
        try:
            hero = opening(page, ns)
            with Image.open(hero) as image:
                image = image.convert('RGB')
                digest = hashlib.sha256(str(image.size).encode()+image.tobytes()).hexdigest()
            assert digest not in pixels, f'{route}: same opening pixels as {pixels.get(digest)}'
            pixels[digest] = route
            if route == 'general-conference.html':
                assert 'come-follow-me' not in hero.as_posix(), 'Conference opening still borrows Come, Follow Me artwork'
        except (AssertionError, StopIteration) as error: errors.append(str(error) or route+': opening absent')
    for route in NEW:
        page = ROOT/route; ns = pages[route]; ids = {n.attrs['id']: n for n in ns if 'id' in n.attrs}
        nav = next(n for n in ns if n.has('fc-study-nav'))
        stops = [n.attrs.get('href','') for n in nav.walk() if n.tag == 'a']
        assert len(stops) >= 7 and len(stops) == len(set(stops)), route+': seven distinct study stops required'
        assert all(s.startswith('#') and s[1:] in ids for s in stops), route+': invalid study stop'
        figures = [n for n in ns if n.tag == 'figure' and n.has('fc-study-visual')]
        assert len(figures) == 5, route+': five focused supporting pictures required'
        assets = set()
        for figure in figures:
            anchor = next(n for n in figure.children if n.tag == 'a')
            asset = local(page, anchor.attrs['href']); assert asset not in assets; assets.add(asset)
            assert anchor.attrs.get('aria-haspopup') == 'dialog' and 'data-full-image-viewer' not in anchor.attrs, route+': detail-first picture required'
            caption = next(n for n in figure.children if n.tag == 'figcaption')
            assert any(n.tag == 'a' and urlsplit(n.attrs.get('href','')).hostname == 'www.churchofjesuschrist.org' for n in caption.walk()), route+': picture needs official source'
        assert sum(n.tag == 'details' for n in ids['guided-practice'].walk()) >= 3, route+': three guided reflections required'
        cards = [n for n in ns if n.has('fc-resource-card')]
        assert len(cards) >= 2, route+': two contextual video cards required'
        for card in cards:
            assert any(n.tag == 'a' and '/media/video/' in n.attrs.get('href','') for n in card.walk()), route+': official video route missing'
            assert any(n.has('fc-resource-card__image') and any(c.tag == 'img' for c in n.walk()) for n in card.walk()), route+': contained preview missing'
        onward = {n.attrs.get('href') for n in ids['continue-study'].walk() if n.tag == 'a' and '.html' in n.attrs.get('href','') and 'ask.html' not in n.attrs['href'] and 'answers.html' not in n.attrs['href']}
        assert len(onward) >= 3, route+': three onward studies required'
        asks = [n for n in ns if n.tag == 'a' and 'ask.html?' in n.attrs.get('href','')]
        assert any(parse_qs(urlsplit(n.attrs['href']).query).get('return',[''])[0].startswith('/'+route) for n in asks), route+': contextual Ask return missing'
    baseline = json.loads((ROOT/'tools/focused_answers_baseline.json').read_text())
    assert baseline['commit'] == '1302ed7f8aaaab004ad4da97a09c5c605942608f' and len(baseline['images']) == 853
    for entry in baseline['images']:
        data = (ROOT/entry['path']).read_bytes()
        digest = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert digest == entry['git_blob_sha1'], entry['path']+': approved baseline image changed'
    review = (ROOT/'docs/focused-answers-art-review.json').read_text(encoding='utf-8')
    assert not re.search(r'[A-Za-z]:\\|/Users/|/home/', review), 'Focused art manifest must not publish private machine paths'
    if errors: raise AssertionError('\n'.join(errors))
    print('FOCUSED ANSWERS QA PASS: 28 own destinations/openings, two complete priesthood studies, 853 unchanged baseline images; editorial and rendered review remain separate')

if __name__ == '__main__': check()
