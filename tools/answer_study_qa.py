#!/usr/bin/env python3
"""Prevent partial Answer enrichment and footer-only media regressions.
Editorial relevance and source review are separate acceptance requirements.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Node:
    def __init__(self, tag='', attrs=(), parent=None, order=0):
        self.tag, self.attrs, self.parent, self.order = tag, dict(attrs), parent, order
        self.children, self.words = [], []
    def has(self, cls): return cls in self.attrs.get('class','').split()
    def walk(self):
        yield self
        for child in self.children: yield from child.walk()
    def text(self, without_cards=False):
        if without_cards and self.has('fc-resource-card'): return ''
        return ' '.join(self.words + [c.text(without_cards) for c in self.children])
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.root=Node(); self.stack=[self.root]; self.order=0
    def handle_starttag(self, tag, attrs):
        self.order+=1; n=Node(tag,attrs,self.stack[-1],self.order); self.stack[-1].children.append(n)
        if tag not in VOID: self.stack.append(n)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag: self.stack=self.stack[:i]; break
    def handle_data(self, text): self.stack[-1].words.append(text)

def check():
    errors=[]
    canonical={urlsplit(x.text).path.lstrip('/') for x in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')}
    pages=sorted(p for p in canonical if p.startswith('answers/') and p.endswith('.html'))
    actual={str(p.relative_to(ROOT)) for p in (ROOT/'answers').glob('*.html')}
    if set(pages)!=actual: errors.append('Every permanent Answer must be inventoried in the sitemap; no batch subset.')
    for path in pages:
        d=Document(); d.feed((ROOT/path).read_text()); nodes=list(d.root.walk())
        main=next((n for n in nodes if n.tag=='main'),None)
        if main is None: errors.append(f'{path}: no main study'); continue
        content=list(main.walk()); ids={n.attrs['id']:n for n in nodes if 'id' in n.attrs}
        cards=[n for n in content if n.has('fc-resource-card')]
        nav=next((n for n in content if n.has('fc-study-nav')),None)
        if not nav: errors.append(f'{path}: missing visible study navigation')
        if any('A companion for your study' in n.text() for n in content if n.tag=='h2'):
            errors.append(f'{path}: generic footer-only media is not Answer enrichment')
        if not cards: errors.append(f'{path}: no visible source media')
        contexts=set()
        for card in cards:
            parent=card.parent
            while parent and parent is not main and not (parent.has('fc-study-feature') or parent.tag=='section'):
                parent=parent.parent
            if parent is None or parent is main or not parent.text(without_cards=True).strip():
                errors.append(f'{path}: media {card.attrs.get("data-resource-key")} lacks topical study context')
            else: contexts.add(parent.order)
        if cards and len(contexts)<2: errors.append(f'{path}: media remains one undifferentiated collection')
        sources=[n for n in content if n.tag=='h2' and 'official sources' in n.text().lower()]
        if cards and sources and min(c.order for c in cards)>min(n.order for n in sources):
            errors.append(f'{path}: media is discoverable only after source appendix')
        if nav:
            targets=[ids.get(n.attrs.get('href','')[1:]) for n in nav.walk() if n.tag=='a' and n.attrs.get('href','').startswith('#')]
            if not any(t and any(n.has('fc-resource-card') for n in t.walk()) for t in targets):
                errors.append(f'{path}: study navigation never reaches contextual media')
        if not any(n.tag=='details' for n in content): errors.append(f'{path}: missing optional reflection control')
        if 'continue-study' not in ids: errors.append(f'{path}: no purposeful continuation')
        if not any(n.tag=='a' and 'ask.html' in n.attrs.get('href','') for n in content): errors.append(f'{path}: no Ask pathway')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'ANSWER STUDY QA PASS: all {len(pages)} permanent Answers have contextual media, navigation, reflection and continuation')
if __name__=='__main__': check()
