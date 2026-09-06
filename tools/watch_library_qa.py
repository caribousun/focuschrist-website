#!/usr/bin/env python3
"""Protect verified video/thumbnail pairs, crawlable study links and locked hero."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,parse_qs
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,path):
  super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.images=[];self.cards=[];self.feed(path.read_text())
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if t=='a':self.links.append(a)
  if t=='img':self.images.append(a)
  if 'data-watch-video' in a:self.cards.append(a['data-watch-video'])
p=Page(ROOT/'watch.html');ledger=json.loads((ROOT/'docs/watch-source-ledger.json').read_text())
assert len(p.ids)==len(set(p.ids)), 'Duplicate Watch anchors'
assert len(p.cards)>=18 and len(set(p.cards))==len(p.cards),'Distinct video coverage missing'
for v in ledger['videos']:
 assert v['key'] in p.cards, v['key']+' missing card'
 assert v['status']==v['image_status']==200, v['key']+' source unverified'
 assert urlsplit(v['url']).hostname=='www.churchofjesuschrist.org'
 asset=ROOT/v['local_thumbnail'];assert hashlib.sha256(asset.read_bytes()).hexdigest()==v['sha256'],v['key']+' thumbnail changed'
 imgs=[i for i in p.images if i.get('src')==v['local_thumbnail']];assert imgs,v['key']+' missing image'
 for i in imgs:assert i.get('width')==str(v['width']) and i.get('height')==str(v['height']) and i.get('loading')=='lazy'
 assert any(a.get('href')==v['url'] and 'Watch '+v['title'] in a.get('aria-label','') for a in p.links),v['key']+' mismatched source image action'
for a in p.links:
 u=urlsplit(a.get('href',''))
 if a.get('target')=='_blank':assert {'noopener','noreferrer'}<=set(a.get('rel','').split())
 if not u.scheme and not u.netloc:
  if not u.path and u.fragment:assert u.fragment in p.ids,'Missing Watch anchor '+u.fragment
  if u.path.endswith('.html'):
   target=ROOT/u.path.lstrip('/');assert target.exists(),'Missing '+u.path
   if u.fragment and u.fragment!='ask-question':assert u.fragment in Page(target).ids,'Missing '+a['href']
  q=parse_qs(u.query)
  if 'watch' in q:
   ret=urlsplit(q['return'][0]);assert ret.path=='/watch.html' and ret.fragment in p.ids
assert 'fc-visual-hero' not in (ROOT/'watch-library.css').read_text(),'Body styles must not target hero'
print(f'Watch library QA PASSED: {len(p.cards)} verified video pairs, image hashes/dimensions, anchors, sources and study routes.')
