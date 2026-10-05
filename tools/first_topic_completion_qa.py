#!/usr/bin/env python3
"""Strict additive FIRST topic family; does not change any historical count.

Manifest contract: {"artworks": [records], "review_receipts":
{"Fermi": [{"path": ..., "sha256": ...}], "Newton": [...]}}.
Keys are bare scene keys. Frozen heterogeneous reviewer receipts remain intact.
Evidence files must be preserved authentic reviewer receipts, not synthesized
approvals. This checker binds evidence bytes; it cannot perform human review.
"""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'docs/first-topic-completion/art-review.json'
PREFIX = 'assets/page-art/first-topic-completion/'
PRAYER = 'answers/prayer-and-personal-revelation.html'
FAMILIES = 'answers/why-families-are-important.html'
EXPECTED = {**{f'prayer-{n:02}': PRAYER for n in range(1, 5)},
            **{k: FAMILIES for k in ('families-01-v2', 'families-02-alt',
               'families-03-alt', 'families-04', 'families-05-alt', 'families-06')}}
STUDIES = {
    'prayer-01': ('jesus-christ-latter-day-saint-beliefs.html', 'Study Jesus Christ'),
    'prayer-02': ('why-families-are-important.html', 'Study caring for families'),
    'prayer-03': ('grief-and-faith.html', 'Study grief and faith'),
    'prayer-04': ('holy-ghost.html', 'Study the Holy Ghost'),
    'families-01-v2': ('jesus-christ-latter-day-saint-beliefs.html', 'Study Jesus Christ'),
    'families-02-alt': ('faith-in-jesus-christ-during-trials.html', 'Study faith during trials'),
    'families-03-alt': ('jesus-christ-latter-day-saint-beliefs.html', 'Study Jesus Christ'),
    'families-04': ('faith-in-jesus-christ-during-trials.html', 'Study faith during trials'),
    'families-05-alt': ('grief-and-faith.html', 'Study grief and faith'),
    'families-06': ('jesus-christ-latter-day-saint-beliefs.html', 'Study Jesus Christ'),
}

def require(condition, message):
    if not condition:
        raise AssertionError('FIRST topic completion: ' + message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def norm(value):
    return ' '.join(value.split())

def local(root, path):
    require(isinstance(path, str) and path and '\\' not in path, 'invalid local manifest path')
    u = urlsplit(path)
    require(not u.scheme and not u.netloc and not u.query and not u.fragment,
            'manifest path must be plain local path')
    require(not path.startswith('/') and '..' not in Path(path).parts, 'manifest path escapes root')
    p = (root / path).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(), 'missing or escaping file: ' + path)
    return p

def html_asset(root, page, value):
    u = urlsplit(value)
    require(not u.scheme and not u.netloc and not u.query and not u.fragment,
            'artwork fallback must be plain local URL')
    target = (root / u.path.lstrip('/') if u.path.startswith('/') else page.parent / u.path).resolve()
    require(target.is_relative_to(root.resolve()), 'HTML artwork escapes root')
    return target.relative_to(root.resolve()).as_posix()

def ancestors(node):
    while node.parent:
        node = node.parent
        yield node

def first_marker(node):
    return any(node.attrs.get(a, '').startswith('first-') for a in
               ('data-exclusive-artwork', 'data-enriched-study-art', 'data-topic-art'))

def family_asset(value):
    return isinstance(value, str) and 'first-topic-completion/' in value

def scalar_hashes(value):
    if isinstance(value, dict):
        return set().union(*(scalar_hashes(v) for v in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(scalar_hashes(v) for v in value)) if value else set()
    if isinstance(value, str) and re.fullmatch('[0-9a-fA-F]{64}', value):
        return {value.lower()}
    return set()

def review_hashes(root, data):
    receipts = data.get('review_receipts', {})
    require(set(receipts) == {'Fermi', 'Newton'}, 'exact independent review sets required')
    found = {}
    paths = {}
    for reviewer, entries in receipts.items():
        require(isinstance(entries, list) and entries, reviewer + ': missing preserved receipts')
        paths[reviewer] = [e.get('path') for e in entries]
        require(len(paths[reviewer]) == len(set(paths[reviewer])), reviewer + ': duplicate receipt path')
        found[reviewer] = set()
        for entry in entries:
            p = local(root, entry.get('path'))
            require(digest(p) == entry.get('sha256'), reviewer + ': receipt content changed')
            found[reviewer] |= scalar_hashes(json.loads(p.read_text(encoding='utf-8')))
    require(set(paths['Fermi']).isdisjoint(paths['Newton']), 'same receipt cannot stand for both reviewers')
    return found

def validate_record(root, record, evidence):
    key = record.get('key')
    require(key in EXPECTED, 'unregistered key ' + str(key))
    require(record.get('route') == EXPECTED[key], key + ': wrong owning route')
    require((record.get('study'), record.get('study_label')) == STUDIES[key],
            key + ': onward study or label differs')
    local(root, 'answers/' + record['study'])
    require(record.get('asset') == PREFIX + key + '-full.webp', key + ': full asset differs')
    require(record.get('responsive') == PREFIX + key + '-960.webp', key + ': responsive asset differs')
    require(record.get('reviewed') is True, key + ': unreviewed')
    require(type(record.get('christ')) is bool and record['christ'] == (key != 'prayer-04'),
            key + ': Christ classification differs')
    require((record.get('width'), record.get('height')) == (1536, 1024), key + ': dimensions differ')
    for field in ('title', 'caption', 'alt', 'source_label'):
        require(isinstance(record.get(field), str) and norm(record[field]), key + ': empty ' + field)
    for field in ('sha256', 'responsive_sha256', 'source_sha256'):
        require(re.fullmatch('[0-9a-f]{64}', record.get(field, '')) is not None, key + ': invalid ' + field)
    for field, hashfield in (('asset', 'sha256'), ('responsive', 'responsive_sha256')):
        require(digest(local(root, record[field])) == record[hashfield], key + ': changed ' + field)
    urls = record.get('source_urls')
    require(isinstance(urls, list) and urls and len(urls) == len(set(urls)), key + ': invalid sources')
    require(all(urlsplit(u).scheme == 'https' and urlsplit(u).hostname == 'www.churchofjesuschrist.org'
                and '/study/scriptures/' in urlsplit(u).path for u in urls), key + ': nonofficial scripture source')
    for reviewer, hashes in evidence.items():
        require({record[f] for f in ('sha256', 'responsive_sha256', 'source_sha256')} <= hashes,
                key + ': raw/full/responsive hashes absent from ' + reviewer + ' receipts')

def validate_figure(root, page, figure, record):
    key = record['key']
    require(page.relative_to(root).as_posix() == record['route'], key + ': picture on wrong page')
    require(figure.tag == 'figure' and figure.has('fc-study-visual'), key + ': must be study figure')
    require(any(n.tag == 'main' for n in ancestors(figure)), key + ': figure outside main')
    require(not any(n.tag in ('dialog', 'template') or 'hidden' in n.attrs
                    or n.attrs.get('aria-hidden') == 'true' for n in [figure, *ancestors(figure)]),
            key + ': owning figure hidden or in dialog/template')
    require(figure.attrs.get('data-exclusive-artwork') == 'first-' + key
            and figure.attrs.get('data-enriched-study-art') == 'first-' + key,
            key + ': figure binding differs')
    anchors = [n for n in figure.children if n.tag == 'a']
    require(len(anchors) == 1, key + ': exactly one native image fallback required')
    anchor = anchors[0]
    require(html_asset(root, page, anchor.attrs.get('href', '')) == record['asset'], key + ': wrong full fallback')
    require(anchor.attrs.get('aria-haspopup') == 'dialog' and 'data-artwork-detail' not in anchor.attrs,
            key + ': bypasses shared topic adapter')
    # The established adapter upgrades this native image fallback to study first.
    require('data-full-image-viewer' in anchor.attrs, key + ': native fallback marker absent')
    require(anchor.attrs.get('data-full-image-alt') == record['alt'], key + ': full-image alt differs')
    require(anchor.attrs.get('aria-label') == 'Explore artwork: ' + record['title'], key + ': trigger label differs')
    require(anchor.attrs.get('data-topic-study') == record['study']
            and anchor.attrs.get('data-topic-study-label') == record['study_label'],
            key + ': onward study binding differs')
    require(html_asset(root, page, anchor.attrs['data-topic-study']) == 'answers/' + STUDIES[key][0],
            key + ': onward destination differs')
    images = [n for n in anchor.walk() if n.tag == 'img']
    require(len(images) == 1, key + ': requires exactly one responsive image')
    img = images[0]
    require(html_asset(root, page, img.attrs.get('src', '')) == record['responsive'], key + ': wrong responsive src')
    require(img.attrs.get('alt') == record['alt'], key + ': alt differs')
    require((img.attrs.get('width'), img.attrs.get('height')) == ('1536', '1024'), key + ': intrinsic dimensions differ')
    parts = [v.strip().split() for v in img.attrs.get('srcset', '').split(',')]
    require(len(parts) == 2 and all(len(p) == 2 for p in parts), key + ': srcset malformed')
    require({(html_asset(root, page, p[0]), p[1]) for p in parts} ==
            {(record['responsive'], '960w'), (record['asset'], '1536w')}, key + ': srcset differs')
    captions = [n for n in figure.children if n.tag == 'figcaption']
    require(len(captions) == 1, key + ': exactly one caption required')
    cap = captions[0]
    headings = [n for n in cap.walk() if n.tag == 'h3']
    prose = [n for n in cap.children if n.tag == 'p' and not n.has('fc-study-visual-label')
             and not any(c.tag == 'a' for c in n.walk())]
    require(len(headings) == 1 and norm(headings[0].text()) == norm(record['title']), key + ': title differs')
    require(len(prose) == 1 and norm(prose[0].text()) == norm(record['caption']), key + ': caption differs')
    links = [n for n in cap.walk() if n.tag == 'a']
    require(len(links) == len(record['source_urls']) and {n.attrs.get('href') for n in links} == set(record['source_urls']),
            key + ': exact source links differ')
    require(all(n.has('fc-inline-scripture') for n in links), key + ': scripture-reader binding missing')
    require(norm(' '.join(n.text() for n in links)) == norm(record['source_label']), key + ': source label differs')

def check(root=ROOT):
    root = Path(root).resolve()
    data = json.loads(local(root, MANIFEST).read_text(encoding='utf-8'))
    records = data.get('artworks', [])
    require(isinstance(records, list) and len(records) == len(EXPECTED), 'exact ten records required')
    require({r.get('key') for r in records} == set(EXPECTED), 'exact ten unique keys required')
    evidence = review_hashes(root, data)
    for record in records:
        validate_record(root, record, evidence)
    require(len({r['asset'] for r in records}) == len(records), 'duplicate original assets')
    require(len({r['sha256'] for r in records}) == len(records), 'duplicate original bytes')
    require(len({r['source_sha256'] for r in records}) == len(records), 'duplicate source originals')
    by_key = {r['key']: r for r in records}
    by_asset = {r['asset']: r for r in records}
    registered = {r[f] for r in records for f in ('asset', 'responsive')}
    require({p.relative_to(root).as_posix() for p in (root / PREFIX).rglob('*') if p.is_file()} == registered,
            'unregistered or missing deployed family file')
    pages = {urlsplit(e.text).path.lstrip('/') for e in ET.parse(local(root, 'sitemap.xml')).getroot().findall('{*}url/{*}loc')}
    pages |= {p.relative_to(root).as_posix() for p in (root / 'answers').glob('*.html')}
    pages |= {'general-conference.html'}
    seen = []
    for rel in sorted(p for p in pages if p.endswith('.html')):
        page = local(root, rel)
        doc = Document(); doc.feed(page.read_text(encoding='utf-8'))
        nodes = list(doc.root.walk())
        figures = []
        for node in nodes:
            if first_marker(node):
                require(node.tag == 'figure', rel + ': first marker outside figure')
                key = node.attrs.get('data-exclusive-artwork', '')[len('first-'):]
                require(key in by_key, rel + ': unregistered first figure')
                figures.append(node)
                validate_figure(root, page, node, by_key[key]); seen.append(key)
        for node in nodes:
            if any(family_asset(v) for v in node.attrs.values()):
                figure = next((n for n in [node, *ancestors(node)] if n.tag == 'figure'), None)
                require(figure in figures, rel + ': unregistered family asset outside owning figure')
        if figures:
            for name, tag, attr in [('topic-artwork-details.js', 'script', 'src'),
                                    ('topic-artwork-details.css', 'link', 'href')]:
                require(sum(n.tag == tag and name in n.attrs.get(attr, '') for n in nodes) == 1,
                        rel + ': missing/duplicate shared adapter dependency ' + name)
    require(len(seen) == len(EXPECTED) and set(seen) == set(EXPECTED), 'each artwork must occur exactly once')
    registry = json.loads(local(root, 'docs/art-study-image-review.json').read_text(encoding='utf-8'))['pages']
    registered_rows = []
    for route, rows in registry.items():
        for entry in rows:
            if family_asset(entry.get('asset', '')):
                require(entry.get('asset') in by_asset, 'unregistered shared-registry family asset')
                record = by_asset[entry['asset']]
                require(route == record['route'] and entry.get('sha256') == record['sha256']
                        and entry.get('reviewed') is True, 'shared registry owner/hash/review mismatch')
                registered_rows.append(entry['asset'])
    require(len(registered_rows) == len(EXPECTED) and set(registered_rows) == set(by_asset),
            'exact shared registry family required')
    return by_asset

if __name__ == '__main__':
    result = check()
    print(f'FIRST TOPIC COMPLETION QA PASS: {len(result)} exact additive originals; historical baseline untouched')
