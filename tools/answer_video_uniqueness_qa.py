#!/usr/bin/env python3
"""Enforce the owner's distinct Answer-video policy against actual placements.

The reviewed identity registry joins alternate URLs for the same production.
Editorial/source review remains necessary; a unique identifier cannot prove fit.
"""
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]

def canonical(url):
    u = urlsplit(url)
    host = u.netloc.lower().removeprefix('www.')
    if host == 'youtube.com' and u.path == '/watch':
        video_id = parse_qs(u.query).get('v', [''])[0]
        if video_id: return host + '/watch/' + video_id
    return host + unquote(u.path).rstrip('/').lower()

def title_key(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())

def page(path):
    d = Document()
    d.feed(path.read_text())
    return list(d.root.walk())

def check():
    assert canonical('https://www.youtube.com/watch?v=AbC&list=one') == canonical('https://www.youtube.com/watch?v=AbC&list=two')
    assert canonical('https://www.youtube.com/watch?v=AbC') != canonical('https://www.youtube.com/watch?v=abc'), 'YouTube IDs are case-sensitive and identify distinct videos'
    registry = json.loads((ROOT / 'docs/answer-video-identities.json').read_text())['resources']
    errors, aliases, titles = [], {}, {}
    for key, record in registry.items():
        if record['kind'] != 'video':
            continue
        identity = record['video_identity']
        for url in [record['url']] + record.get('aliases', []):
            value = canonical(url)
            if value in aliases and aliases[value] != identity:
                errors.append('Conflicting video aliases: ' + key)
            aliases[value] = identity
        name = title_key(record['title'])
        if name in titles and titles[name] != identity:
            errors.append('Same video title assigned different identities: ' + key)
        titles[name] = identity

    watch = set()
    for node in page(ROOT / 'watch.html'):
        key = node.attrs.get('data-watch-video') or node.attrs.get('data-resource-key')
        if key:
            record = registry.get(key)
            if not record:
                errors.append('Watch resource missing identity review: ' + key)
            elif record['kind'] == 'video':
                watch.add(record['video_identity'])
        href = node.attrs.get('href', '')
        if '/media/video/' in href or '/study/video/' in href:
            watch.add(aliases.get(canonical(href), canonical(href)))

    owners = defaultdict(set)
    count = 0
    for path in sorted((ROOT / 'answers').glob('*.html')):
        nodes = page(path)
        for node in nodes:
            if not node.has('fc-resource-card'):
                continue
            key = node.attrs.get('data-resource-key')
            record = registry.get(key)
            if not record:
                errors.append(f'{path.name}: resource missing identity review: {key}')
                continue
            if record['kind'] == 'study-reference':
                # A thumbnail can lead to the existing owning study, never duplicate its video.
                destination=record.get('url','');target=urlsplit(destination)
                owner=registry.get(record.get('owning_resource_key'),{})
                target_path=(path.parent/target.path).resolve()
                if target.scheme or target.netloc or not target.fragment or target_path.parent != (ROOT/'answers').resolve() or not target_path.is_file() or target_path==path.resolve():
                    errors.append(f'{path.name}: invalid owning study reference: {key}')
                    continue
                owner_nodes=page(target_path)
                owner_cards=[n for n in owner_nodes if n.attrs.get('data-resource-key')==record.get('owning_resource_key')]
                bound=False
                if len(owner_cards)==1:
                    ancestor=owner_cards[0]
                    while ancestor:
                        if ancestor.attrs.get('id')==target.fragment:bound=True
                        ancestor=ancestor.parent
                if not bound or owner.get('kind')!='video' or owner.get('video_identity')!=record.get('referenced_video_identity'):
                    errors.append(f'{path.name}: study reference not bound to existing owning video: {key}')
                if any(n.has('fc-resource-card__play') for n in node.walk()) or any(n.attrs.get('href')!=destination for n in node.walk() if n.tag=='a'):
                    errors.append(f'{path.name}: study reference must link only to owning study without video play presentation: {key}')
                continue
            visual_video = any(n.has('fc-resource-card__play') for n in node.walk())
            kind_text = ' '.join(n.text() for n in node.walk() if n.has('fc-resource-card__kind'))
            if (visual_video or 'video' in kind_text.lower()) and record['kind'] != 'video':
                errors.append(f'{path.name}: video presented with non-video identity: {key}')
            if record['kind'] != 'video':
                continue
            count += 1
            identity = record['video_identity']
            owners[identity].add(path.name)
            if identity in watch:
                errors.append(f'{path.name}: video already appears in Watch: {key}')
            for link in (n for n in node.walk() if n.tag == 'a'):
                if link.has('fc-inline-scripture') and link.attrs.get('href','').startswith('https://www.churchofjesuschrist.org/study/scriptures/'):
                    continue  # Exact inline chapter URLs are gated by resource_thumbnail_qa.py.
                if aliases.get(canonical(link.attrs.get('href', ''))) != identity:
                    errors.append(f'{path.name}: source URL does not match reviewed video identity: {key}')
        # Direct video links outside thumbnail cards must not reintroduce Watch.
        for node in nodes:
            href = node.attrs.get('href', '')
            if '/media/video/' in href or '/study/video/' in href:
                identity = aliases.get(canonical(href), canonical(href))
                owners[identity].add(path.name)
                if identity in watch:
                    errors.append(f'{path.name}: direct video link repeats Watch: {href}')
    for identity, paths in owners.items():
        if len(paths) > 1:
            errors.append('Video repeated across Answers: ' + ', '.join(sorted(paths)))
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'ANSWER VIDEO UNIQUENESS PASS: {count} video cards, no Watch or cross-Answer repetition')

if __name__ == '__main__':
    check()
