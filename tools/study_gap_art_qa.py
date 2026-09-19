"""Hash-bound integration contract for the four editorial study-gap additions."""
import hashlib
import json
import re
import sys
from urllib.parse import parse_qs, urlsplit
from PIL import Image
from birth_of_christ_qa import ROOT, local_asset, references
from life_after_death_qa import Parser

EXPECTED = {
    'child-keepsake': 'answers/death-of-a-child.html',
    'divorce-child': 'answers/divorce-and-faith.html',
    'paul-athens': 'answers/god-our-heavenly-father.html',
    'jesus-weeps-bethany': 'answers/grief-and-faith.html',
}


def check():
    errors = []
    def need(ok, message):
        if not ok:
            errors.append(message)
    entries = json.loads((ROOT/'docs/study-gap-art-review.json').read_text(encoding='utf-8'))['artworks']
    need(len(entries) == 4 and {e.get('key'): e.get('page') for e in entries} == EXPECTED,
         'Gap manifest must inventory the four exact approved placements')
    shared = json.loads((ROOT/'docs/art-study-image-review.json').read_text(encoding='utf-8'))['pages']
    owners, pixels = {}, []
    for field in ['asset', 'thumbnail', 'source_sha256']:
        values = [e.get(field) for e in entries]
        need(all(values) and len(values) == len(set(values)), 'Missing/duplicate '+field)
    for entry in entries:
        key, page = entry['key'], ROOT/entry['page']
        need(entry.get('reviewed') is True and bool(entry.get('review')), key+': visual review missing')
        need(isinstance(entry.get('owner_approval'), bool), key+': explicit owner approval boolean missing')
        if entry.get('owner_approval'):
            need(bool(entry.get('owner_approval_evidence')), key+': owner approval evidence missing')
        need(bool(re.fullmatch(r'[0-9a-f]{64}', entry.get('source_sha256', ''))), key+': source lineage hash invalid')
        records = [e for e in shared.get(entry['page'], []) if e.get('asset') == entry['asset']]
        need(len(records) == 1 and records[0].get('sha256') == entry['sha256'] and records[0].get('reviewed') is True,
             key+': shared review ledger does not match')
        dimensions = {}
        for field, hash_field in [('asset', 'sha256'), ('thumbnail', 'thumbnail_sha256')]:
            path = (ROOT/entry[field]).resolve()
            need(path.is_relative_to(ROOT) and path.is_file(), key+': missing local '+field)
            if not path.is_file():
                continue
            owners[path] = page.resolve()
            need(hashlib.sha256(path.read_bytes()).hexdigest() == entry.get(hash_field), key+': changed '+field)
            with Image.open(path) as image:
                image.load()
                need(image.format == 'WEBP', key+': publish WebP assets')
                dimensions[field] = image.size
                pixels.append((image.size, hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()))
        need(dimensions.get('asset') == (entry.get('width'), entry.get('height')) == (1536, 1024), key+': full dimensions differ')
        need(dimensions.get('thumbnail') == (800, 533), key+': thumbnail dimensions differ')
        nodes = list(Parser(page.read_text(encoding='utf-8')).root.walk())
        need(any('topic-artwork-details.js' in (n.attrs.get('src') or '') for n in nodes), key+': shared study script missing')
        figures = [n for n in nodes if n.tag == 'figure' and n.attrs.get('data-study-gap-art') == key]
        need(len(figures) == 1, key+': requires one owning figure')
        if len(figures) != 1:
            continue
        figure = figures[0]
        need(figure.has('fc-study-visual'), key+': shared study figure class missing')
        triggers = [n for n in figure.children if n.tag == 'a']
        images = [n for n in figure.walk() if n.tag == 'img']
        need(len(triggers) == len(images) == 1, key+': one image and trigger required')
        if len(triggers) != 1 or len(images) != 1:
            continue
        trigger, image = triggers[0], images[0]
        need(local_asset(page, trigger.attrs.get('href')) == (ROOT/entry['asset']).resolve(), key+': full reference differs')
        need(local_asset(page, image.attrs.get('src')) == (ROOT/entry['thumbnail']).resolve(), key+': thumbnail reference differs')
        need(trigger.attrs.get('aria-haspopup') == 'dialog' and 'data-full-image-viewer' not in trigger.attrs,
             key+': must open study dialog before full image')
        need(bool(image.attrs.get('alt')) and image.attrs.get('loading') == 'lazy' and image.attrs.get('decoding') == 'async', key+': image accessibility/loading missing')
        need((image.attrs.get('width'), image.attrs.get('height')) == ('1536', '1024'), key+': intrinsic dimensions missing')
        need(bool(image.attrs.get('sizes')) and trigger.attrs.get('href', 'MISSING') in image.attrs.get('srcset', '') and image.attrs.get('src', 'MISSING') in image.attrs.get('srcset', ''), key+': responsive variants missing')
        captions = [n for n in figure.children if n.tag == 'figcaption']
        need(len(captions) == 1, key+': caption missing')
        if captions:
            cn = list(captions[0].walk())
            need(any(n.tag == 'h3' and ''.join(n.words).strip() for n in cn) and any(n.tag == 'p' and len(''.join(n.words).split()) >= 12 for n in cn), key+': substantive title/caption missing')
            sources = [n for n in cn if n.has('fc-study-visual-sources')]
            links = [n for s in sources for n in s.walk() if n.tag == 'a']
            need(bool(links), key+': source pills missing')
            for link in links:
                url = urlsplit(link.attrs.get('href', ''))
                need(url.netloc == 'www.churchofjesuschrist.org', key+': source must be official Church resource')
                if '/scriptures/' in url.path:
                    selection = parse_qs(url.query).get('id', [''])[0]
                    need(link.has('fc-inline-scripture') and bool(re.fullmatch(r'p\d+(?:-p\d+)?', selection)) and url.fragment == selection.split('-')[0], key+': exact shared-reader verse action required')
    need(len(pixels) == len(set(pixels)), 'Gap assets repeat decoded pixels')
    for page in ROOT.rglob('*.html'):
        if '.git' in page.parts:
            continue
        nodes = list(Parser(page.read_text(encoding='utf-8', errors='replace')).root.walk())
        for path in references(page, nodes) & owners.keys():
            need(owners[path] == page.resolve(), 'Exclusive gap artwork reused on '+page.relative_to(ROOT).as_posix())
        for node in nodes:
            if 'data-study-gap-art' in node.attrs:
                need(EXPECTED.get(node.attrs['data-study-gap-art']) == page.relative_to(ROOT).as_posix(), 'Unknown/misplaced gap figure')
    return errors


if __name__ == '__main__':
    errors = check()
    if errors:
        print('Study gap artwork QA failed:\n- '+'\n- '.join(errors))
        sys.exit(1)
    print('Study gap artwork QA passed: four reviewed exclusive placements, hashes, decoded uniqueness, responsive assets, captions, sources and study triggers.')
