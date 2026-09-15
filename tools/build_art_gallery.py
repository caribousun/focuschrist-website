#!/usr/bin/env python3
"""Build the gallery index from original public artwork triggers, not copied panels.

Run after adding artwork. No descriptions or pills are duplicated: the original
page remains their authority. --check detects an out-of-date committed inventory.
"""
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlsplit, unquote
from xml.etree import ElementTree as ET
sys.dont_write_bytecode = True
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://focuschrist.com'


def text(node):
    return re.sub(r'\s+', ' ', node.text()).strip() if node else ''


def ancestors(node):
    while node.parent:
        node = node.parent
        yield node


def first(node, predicate):
    return next((n for n in node.walk() if predicate(n)), None) if node else None


def asset(page, value):
    if not value:
        return ''
    url = urlsplit(urljoin(ORIGIN + page, value))
    if url.netloc not in {'focuschrist.com', 'www.focuschrist.com'}:
        raise ValueError('Unexpected external artwork: ' + value)
    path = unquote(url.path)
    if Path(path).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp', '.avif'}:
        raise ValueError('Artwork does not identify an image: ' + value)
    if not (ROOT / path.lstrip('/')).is_file():
        raise ValueError('Missing artwork: ' + path)
    return path


def attr(name, value):
    return '[' + name + '=' + json.dumps(value, ensure_ascii=False) + ']'


def stable(prefix, value):
    return prefix + hashlib.sha256(value.encode()).hexdigest()[:12]


def category(page):
    if page.startswith('/answers/'):
        return 'Gospel Studies'
    if page.startswith('/art-study/') or page == '/art.html':
        return 'Art & Study'
    return {'/index.html': 'Home', '/missionary.html': 'Missionary Work',
            '/church-history.html': 'Church History', '/joseph-smith-likeness.html': 'Church History', '/pioneers.html': 'Pioneers',
            '/come-follow-me.html': 'Come, Follow Me', '/watch.html': 'Watch',
            '/about.html': 'About', '/ask.html': 'Ask', '/answers.html': 'Gospel Studies',
            '/general-conference.html': 'General Conference'}.get(page, 'Gospel Studies')


def build():
    pages = sorted({('/index.html' if urlsplit(x.text).path in {'', '/'} else urlsplit(x.text).path)
                    for x in ET.parse(ROOT / 'sitemap.xml').getroot().findall('{*}url/{*}loc')})
    pages = [p for p in pages if p != '/art-gallery.html' and (ROOT / p.lstrip('/')).is_file()]
    hero_text = (ROOT / 'hero-details.js').read_text(encoding='utf-8')
    hero_titles = {}
    for match in re.finditer(r"(?:^|\n)\s*(?:'([^']+)'|([\w-]+)):\s*\{\s*title:\s*'([^']+)'", hero_text):
        hero_titles[match[1] or match[2]] = match[3]
    entries = []
    for page in pages:
        doc = Document()
        doc.feed((ROOT / page.lstrip('/')).read_text(encoding='utf-8'))
        nodes = list(doc.root.walk())
        page_title = text(first(doc.root, lambda n: n.tag == 'h1')) or text(first(doc.root, lambda n: n.tag == 'title')).split('|')[0].strip()
        records = {(key, n.attrs[key]): n for n in nodes for key in
                   ['data-artwork-detail-content', 'data-missionary-detail-content'] if key in n.attrs}
        for node in nodes:
            parents = list(ancestors(node))
            if any(p.tag == 'dialog' or p.has('fc-resource-card') or p.tag == 'nav' for p in parents):
                continue
            image = first(node, lambda n: n.tag == 'img')
            attrs = node.attrs
            kind = ''
            record = None
            selector = ''
            title = ''
            full = ''
            thumb = image.attrs.get('src', '') if image else ''
            alt = attrs.get('data-full-image-alt') or (image.attrs.get('alt', '') if image else '')
            if node.tag == 'a' and 'data-hero-viewer' in attrs:
                kind = 'hero'
                full = attrs['href']
                selector = 'a[data-hero-viewer]' + attr('href', full)
                key = attrs.get('data-hero-record')
                if not key:
                    key = 'home' if node.has('fc-home-hero') or node.has('fc-answer-detail-hero') else Path(full).stem
                    key = {'missionary': 'mission', 'church-history': 'history'}.get(key, key)
                title = hero_titles.get(key, alt or page_title)
            elif node.tag == 'a' and ('data-artwork-detail' in attrs or 'data-missionary-detail' in attrs):
                kind = 'artwork' if 'data-artwork-detail' in attrs else 'missionary'
                key = 'data-artwork-detail' if kind == 'artwork' else 'data-missionary-detail'
                record = records.get((key + '-content', attrs[key]))
                if record is None:
                    raise ValueError(page + ': missing original panel record ' + attrs[key])
                selector = 'a' + attr(key, attrs[key])
                full = record.attrs.get('data-detail-full') or record.attrs.get('data-detail-image') or attrs.get('href')
                thumb = thumb or record.attrs.get('data-detail-image', '')
                title = text(first(record, lambda n: 'data-detail-title' in n.attrs))
                alt = record.attrs.get('data-detail-image-alt') or alt
            elif node.has('gallery-item') and image:
                kind = 'legacy'
                full = image.attrs.get('data-full-src') or thumb
                title = text(first(node, lambda n: n.has('caption'))) or alt
                selector = '.gallery-item:has(img' + attr('src', image.attrs['src']) + ')'
            elif node.tag == 'a' and image and 'href' in attrs and any(p.tag == 'main' for p in parents) and (
                    node.parent.tag == 'figure' or node.has('fc-marriage-era__art') or node.has('fc-foundation-card__image')):
                kind = 'topic' if any(n.tag == 'script' and 'topic-artwork-details.js' in n.attrs.get('src', '') for n in nodes) else 'full'
                if kind == 'full' and 'data-full-image-viewer' not in attrs:
                    raise ValueError(page + ': artwork has no recognized native viewer: ' + attrs['href'])
                full = attrs['href']
                selector = 'a' + attr('href', full) + ':has(img' + attr('src', image.attrs['src']) + ')'
                if attrs.get('id'):
                    selector = 'a' + attr('id', attrs['id'])
                container = next((p for p in parents if p.tag == 'figure' or p.has('fc-marriage-era') or p.has('fc-foundation-card')), None)
                caption = first(container, lambda n: n.tag == 'figcaption' or n.has('fc-marriage-era__copy') or n.has('fc-foundation-card-copy'))
                heading = first(caption, lambda n: n.tag in {'h2', 'h3', 'h4', 'strong'})
                title = text(heading) or alt or page_title
            if not kind:
                continue
            full = asset(page, full)
            sensitive_gate = attrs.get('data-sensitive-scene')
            if sensitive_gate:
                thumb = attrs['data-sensitive-preview']
            thumb = asset(page, thumb) if thumb else full
            title = title or alt or page_title
            entries.append({'fullImage': full, 'thumbnail': thumb, 'title': title, 'alt': alt or title,
                            'category': category(page), 'occurrence': {
                                'id': stable('source-', page + '|' + kind + '|' + selector),
                                'page': page, 'pageTitle': page_title, 'category': category(page), 'kind': kind, 'selector': selector, 'title': title,
                                **({'sensitiveGate': sensitive_gate} if sensitive_gate else {})}})
    # The full-size URL is authoritative; exact duplicate files share an identity too.
    # Numeric responsive suffixes are removed only for grouping matching image families.
    groups = {}
    identities = {}
    for entry in entries:
        path = entry['fullImage']
        family = re.sub(r'-\d{3,4}w?(?=\.[^.]+$)', '', path)
        # Artwork identities are URLs: keep slash semantics identical on every OS.
        family = str(PurePosixPath(family).with_suffix('')).lower()
        digest = hashlib.sha256((ROOT / path.lstrip('/')).read_bytes()).hexdigest()
        identity = identities.get(digest, family)
        identities[digest] = identity
        groups.setdefault(identity, []).append(entry)
    artworks = []
    for identity, group in groups.items():
        # Prefer substantive study panels to the older Art drawer for duplicates.
        group.sort(key=lambda e: ({'artwork': 0, 'topic': 1, 'missionary': 2, 'hero': 3, 'legacy': 4, 'full': 5}[e['occurrence']['kind']], e['occurrence']['page']))
        chosen = group[0]
        item = {key: chosen[key] for key in ['title', 'category', 'thumbnail', 'fullImage', 'alt']}
        item['id'] = stable('art-', identity)
        item['occurrences'] = list({e['occurrence']['id']: e['occurrence'] for e in group}.values())
        item['categories'] = sorted({e['category'] for e in group})
        artworks.append(item)
    artworks.sort(key=lambda item: (item['title'].casefold(), item['id']))
    occurrence_ids = [o['id'] for a in artworks for o in a['occurrences']]
    if len(occurrence_ids) != len(set(occurrence_ids)):
        raise ValueError('A source occurrence was assigned to multiple artworks')
    return {'version': 1, 'pages': pages, 'artworks': artworks,
            'stats': {'artworks': len(artworks), 'occurrences': len(occurrence_ids),
                      'byKind': {k: sum(e['occurrence']['kind'] == k for e in entries) for k in sorted({e['occurrence']['kind'] for e in entries})}}}


if __name__ == '__main__':
    output = json.dumps(build(), ensure_ascii=False, indent=2) + '\n'
    destination = ROOT / 'art-gallery.json'
    if '--check' in sys.argv:
        if not destination.is_file() or destination.read_text(encoding='utf-8') != output:
            raise SystemExit('Art gallery inventory is stale. Run python tools/build_art_gallery.py')
        print('Art gallery inventory is current.')
    else:
        destination.write_text(output, encoding='utf-8', newline='\n')
        print(json.loads(output)['stats'])
