#!/usr/bin/env python3
"""Check study destinations, section links, and reachability without JavaScript."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.duplicates = set(), [], []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids: self.duplicates.append(a['id'])
            self.ids.add(a['id'])
        if tag == 'a' and a.get('href'): self.links.append(a['href'])

pages = {p.resolve(): Page(p) for p in ROOT.rglob('*.html') if '.git' not in p.parts and 'node_modules' not in p.parts}
hubs = [ROOT / (n + '.html') for n in ['index','ask','answers','art','missionary','church-history','pioneers','watch','about']]
studies = [*ROOT.glob('answers/*.html'), *ROOT.glob('art-study/*.html')]
errors = []
graph = {}
for path in hubs + studies:
    path = path.resolve(); page = pages[path]; graph[path] = set()
    if page.duplicates: errors.append(f'{path.name}: duplicate IDs {page.duplicates}')
    for href in page.links:
        u = urlsplit(href)
        if u.scheme or u.netloc: continue
        target = (ROOT / unquote(u.path).lstrip('/') if u.path.startswith('/') else path.parent / unquote(u.path)).resolve() if u.path else path
        if target.suffix != '.html': continue
        if target not in pages:
            errors.append(f'{path.name}: missing page {href}'); continue
        graph[path].add(target)
        # Runtime-owned anchors exist elsewhere; all new connected study anchors must be static.
        if u.fragment in {'connected-study','scripture-study','study-resources','continue-study'} and u.fragment not in pages[target].ids:
            errors.append(f'{path.name}: missing study anchor {href}')
for hub in hubs:
    if 'connected-study' not in pages[hub.resolve()].ids: errors.append(f'{hub.name}: missing guided study entry')
for study in studies:
    if 'continue-study' not in pages[study.resolve()].ids: errors.append(f'{study.name}: missing next study destination')
    destinations = graph[study.resolve()] & {p.resolve() for p in studies}
    if len(destinations) < 2: errors.append(f'{study.name}: fewer than two distinct related studies')
visited, pending = set(), [(ROOT/'index.html').resolve()]
while pending:
    p = pending.pop()
    if p in visited: continue
    visited.add(p); pending.extend(graph.get(p,set()) - visited)
for study in studies:
    if study.resolve() not in visited: errors.append(f'{study.name}: unreachable from Home without JavaScript')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Connected study QA PASSED: {len(hubs)} section guides, {len(studies)} studies, static destinations and learning paths reachable from Home.')
