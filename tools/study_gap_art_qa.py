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

# These additions are a separate reviewed release, not a relaxation of the four
# original study-gap placements above. Each manifest has a closed key inventory.
SITEWIDE = {
    'sitewide-supporting-review.json': {'living-breakfast-shore-20260919', 'shepherd-seeks-one-20260919', 'children-listen-at-home-20260919', 'still-phone-down-scripture-20260919'},
    'sitewide-gap-supporting-review.json': {'bom-archaeology-context', 'bom-alma-helaman', 'bom-mormon-moroni', 'bom-language-comparison'},
    'sitewide-community-supporting-review.json': {'history-relief-practical-care-20260919', 'cfm-gate-repair-service-20260919', 'marriage-community-welcome-20260919'},
    'sitewide-narrative-supporting-review.json': {'look-peter-rescue', 'trials-almas-people', 'birth-john-witness', 'two-witnesses-emmaus-20260919'},
    'sitewide-talk-thumbnail-review.json': {'holland-qualified-care', 'renlund-guided-flight', 'uchtdorf-youth-choice', 'holland-lord-believe'},
}


def sitewide_entries():
    """Normalize declared review records without inferring reviews from markup."""
    result = []
    for filename, expected in SITEWIDE.items():
        data = json.loads((ROOT/'docs'/filename).read_text(encoding='utf-8'))
        entries = data.get('records', data.get('artworks', []))
        assert len(entries) == len(expected) and {e.get('key', e.get('slug')) for e in entries} == expected, filename+': exact reviewed inventory changed'
        rejected = {e['sha256'] for e in data.get('rejected', []) if isinstance(e, dict) and 'sha256' in e} | set(data.get('rejected_sha256', []))
        for original in entries:
            entry = dict(original)
            entry['key'] = entry.get('key', entry.get('slug'))
            if not entry['page'].endswith('.html'):
                entry['page'] = 'art-study/'+entry['page']+'.html'
            entry['sha256'] = entry.get('sha256', entry.get('full_sha256'))
            entry['source_sha256'] = entry.get('source_sha256', entry.get('original_sha256'))
            entry['manifest'] = filename
            entry['rejected_sha256'] = rejected
            entry['talk'] = filename == 'sitewide-talk-thumbnail-review.json'
            sources = [s['url'] for s in entry.get('sources', [])]
            if not sources:
                sources = [entry.get('source_url', entry.get('source'))]
            # Mormon 8 documents the historical age interpretation; the displayed
            # source action intentionally opens Mormon 6's transfer of the record.
            entry['markup_sources'] = sources[:1] if entry['key'] == 'bom-mormon-moroni' else sources
            result.append(entry)
    return result


def inventory_errors(entries):
    errors = []
    for field in ('key', 'asset', 'thumbnail', 'source_sha256', 'sha256', 'thumbnail_sha256'):
        values = [e.get(field) for e in entries]
        if not all(values) or len(values) != len(set(values)):
            errors.append('Sitewide missing/duplicate '+field)
    for entry in entries:
        if entry.get('technical_review_passed') is not True:
            errors.append(entry['key']+': technical review missing')
        for field in ('source_sha256', 'sha256', 'thumbnail_sha256'):
            if not re.fullmatch(r'[0-9a-f]{64}', entry.get(field) or ''):
                errors.append(entry['key']+': invalid '+field)
            if entry.get(field) in entry.get('rejected_sha256', set()):
                errors.append(entry['key']+': rejected image selected')
        if not entry.get('markup_sources') or any(not s or urlsplit(s).scheme != 'https' for s in entry['markup_sources']):
            errors.append(entry['key']+': source missing')
    return errors


def dialog_dependency_errors(nodes, key):
    errors = []
    for dependency, tag, attribute in [('artwork-details.css', 'link', 'href'), ('topic-artwork-details.css', 'link', 'href'), ('topic-artwork-details.js', 'script', 'src'), ('full-image-viewer.css', 'link', 'href'), ('full-image-viewer.js', 'script', 'src')]:
        if sum(n.tag == tag and urlsplit(n.attrs.get(attribute, '')).path.split('/')[-1] == dependency for n in nodes) != 1:
            errors.append(key+': missing or duplicate shared dialog dependency '+dependency)
    return errors


def check_sitewide(page_filter=None):
    entries = sitewide_entries()
    errors = inventory_errors(entries)
    def need(ok, message):
        if not ok:
            errors.append(message)
    pixels = []
    for entry in entries:
        if page_filter is not None and entry['page'] != page_filter:
            continue
        key, page = entry['key'], ROOT/entry['page']
        nodes = list(Parser(page.read_text(encoding='utf-8')).root.walk())
        if not entry['talk']:
            errors.extend(dialog_dependency_errors(nodes, key))
        dimensions = {}
        for field, hash_field in [('asset', 'sha256'), ('thumbnail', 'thumbnail_sha256')]:
            asset = (ROOT/entry[field]).resolve()
            need(asset.is_relative_to(ROOT) and asset.is_file(), key+': missing '+field)
            if not asset.is_file():
                continue
            need(hashlib.sha256(asset.read_bytes()).hexdigest() == entry[hash_field], key+': changed '+field)
            with Image.open(asset) as image:
                dimensions[field] = image.size
                need(image.format == 'WEBP', key+': WebP required')
                pixels.append((image.size, hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()))
        if entry['talk']:
            containers = [n for n in nodes if n.tag == 'article' and n.attrs.get('data-resource-key') == entry['resource_key']]
        else:
            containers = [n for n in nodes if n.tag == 'figure' and any(local_asset(page, a.attrs.get('href')) == (ROOT/entry['asset']).resolve() for a in n.children if a.tag == 'a')]
        need(len(containers) == 1, key+': exact owning figure/card missing or repeated')
        if len(containers) != 1:
            continue
        container = containers[0]
        images = [n for n in container.walk() if n.tag == 'img']
        need(len(images) == 1, key+': exactly one thumbnail required')
        if len(images) == 1:
            image = images[0]
            need(local_asset(page, image.attrs.get('src')) == (ROOT/entry['thumbnail']).resolve(), key+': thumbnail mismatch')
            need(image.attrs.get('alt') == entry['alt'] and image.attrs.get('loading') == 'lazy' and image.attrs.get('decoding') == 'async', key+': reviewed alt/loading mismatch')
            intrinsic = tuple(int(image.attrs.get(k, 0)) for k in ('width', 'height'))
            need(intrinsic in dimensions.values(), key+': intrinsic dimensions do not describe an actual variant')
        actual_sources = [n.attrs.get('href') for n in container.walk() if n.tag == 'a' and urlsplit(n.attrs.get('href', '')).scheme == 'https']
        if entry['talk']:
            ledger = json.loads((ROOT/'docs/resource-thumbnail-ledger.json').read_text(encoding='utf-8'))['resources']
            record = next((r for r in ledger if r['key'] == entry['resource_key']), {})
            need(actual_sources == [record.get('url')]*2 + entry.get('inline_scripture_urls', []), key+': exact official resource actions differ')
            need(record.get('local_thumbnail') == entry['thumbnail'] and record.get('sha256') == entry['thumbnail_sha256'], key+': resource ledger bytes differ')
        else:
            need(actual_sources == entry['markup_sources'], key+': displayed primary sources differ from review')
            trigger = next((n for n in container.children if n.tag == 'a'), None)
            need(trigger is not None and trigger.attrs.get('aria-haspopup') == 'dialog' and 'data-full-image-viewer' not in trigger.attrs, key+': must enter study details first')
            need(any(n.tag in ('h3', 'strong') and ''.join(n.words).strip() == entry['title'] for n in container.walk()), key+': reviewed title missing')
    need(len(pixels) == len(set(pixels)), 'Sitewide artwork repeats decoded pixels')
    return errors


def sitewide_negative_fixtures():
    from copy import deepcopy
    entries = sitewide_entries()
    assert not inventory_errors(entries), 'Positive fixture must pass before corruption'
    duplicate = deepcopy(entries); duplicate[1]['source_sha256'] = duplicate[0]['source_sha256']
    assert any('duplicate source_sha256' in e for e in inventory_errors(duplicate)), 'Duplicate source regression escaped'
    rejected = deepcopy(entries); rejected[0]['rejected_sha256'].add(rejected[0]['sha256'])
    assert any('rejected image' in e for e in inventory_errors(rejected)), 'Rejected hash regression escaped'
    missing = deepcopy(entries); missing[0]['markup_sources'] = []
    assert any('source missing' in e for e in inventory_errors(missing)), 'Missing source regression escaped'
    nodes = list(Parser((ROOT/'come-follow-me.html').read_text(encoding='utf-8')).root.walk())
    assert not dialog_dependency_errors(nodes, 'cfm'), 'Positive shared-dialog fixture must pass'
    missing_style = [n for n in nodes if urlsplit(n.attrs.get('href', '')).path != 'artwork-details.css']
    assert any('artwork-details.css' in e for e in dialog_dependency_errors(missing_style, 'cfm')), 'Unstyled white-dialog regression escaped'


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
    sitewide_negative_fixtures()
    errors = check() + check_sitewide()
    if errors:
        print('Study gap artwork QA failed:\n- '+'\n- '.join(errors))
        sys.exit(1)
    print('Study gap artwork QA passed: four original placements plus 14 sitewide body additions and four talk thumbnails; exact inventories, reviewed hashes, decoded uniqueness, sources, styled-dialog dependencies and four negative fixtures.')
