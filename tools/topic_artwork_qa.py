#!/usr/bin/env python3
"""Enforce reviewed contextual artwork, responsive originals and exact scripture sources."""
import json,hashlib
from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document
from production_hardening_qa import webp_dimensions

def nodes(path):
 doc=Document();doc.feed(path.read_text(encoding="utf-8"));return list(doc.root.walk())

def child(node,tag):
 return next((n for n in node.children if n.tag==tag),None)
ROOT=Path(__file__).resolve().parents[1]
placements=json.loads((ROOT/'docs/topic-artwork-placement.json').read_text(encoding='utf-8'))
assert len(placements)==21
review=json.loads((ROOT/'docs/topic-artwork-review.json').read_text(encoding='utf-8'))
approved={r['name']:r for r in review['assets'] if r['status']=='approved'}
approved['christ-disciples-gaze-v2']=approved['christ-disciples-replacement']
for record in review['assets']:
 for asset in record['published_assets']:
  assert hashlib.sha256((ROOT/asset['path']).read_bytes()).hexdigest()==asset['sha256'],asset['path']+' changed after independent visual review'
seen=set()
for item in placements:
 page=ROOT/item['page'];doc=nodes(page)
 sections=[n for n in doc if n.attrs.get('id')==item['section']];assert len(sections)==1
 fs=[n for n in sections[0].walk() if n.tag=='figure' and n.attrs.get('data-enriched-study-art')==item['asset']]
 assert len(fs)==1,(item['page'],item['section'])
 f=fs[0];links=[n for n in f.children if n.tag=='a' and 'data-full-image-viewer' in n.attrs];assert len(links)==1
 a=links[0];im=child(a,'img');assert im is not None and im.attrs.get('alt')
 assert item['asset'] in approved
 for attr in ['href']:
  full=(page.parent/a.attrs.get(attr)).resolve();assert full.is_file()
 src=(page.parent/im.attrs.get('src')).resolve();assert src.is_file()
 assert webp_dimensions(full)==(1536,1024) and webp_dimensions(src)==(800,533)
 assert im.attrs.get('width')=='1536' and im.attrs.get('height')=='1024'
 assert full.name==item['asset']+'-1536.webp' and src.name==item['asset']+'-800.webp'
 assert im.attrs.get('loading')=='lazy' and im.attrs.get('decoding')=='async'
 assert '800w' in im.attrs.get('srcset','') and '1536w' in im.attrs.get('srcset','')
 caption=child(f,'figcaption');assert caption is not None
 assert child(caption,'h3').text().strip()==item['title']
 assert item['description'] in caption.text()
 actual=[n for n in caption.walk() if n.tag=='a' and n.has('fc-inline-scripture')]
 assert [(a.text().strip(),a.attrs.get('href')) for a in actual]==[(s['label'],s['url']) for s in item['sources']]
 for s in item['sources']:
  u=urlsplit(s['url']);assert u.netloc=='www.churchofjesuschrist.org'
  key=u.path.split('/study/scriptures/')[1];assert (ROOT/'scripture-data'/(key+'.json')).is_file()
 assert len([n for n in doc if n.tag=='script' and 'full-image-viewer.js' in n.attrs.get('src','')])==1
 seen.add(item['asset'])
assert len(seen)==12
allfigures=sum(sum(n.tag=='figure' and 'data-enriched-study-art' in n.attrs for n in nodes(p)) for p in (ROOT/'answers').glob('*.html'))
assert allfigures==21
css=(ROOT/'topic-art.css').read_text();assert 'object-fit:contain' in css and 'height:auto' in css
print('TOPIC ARTWORK QA PASS: 21 contextual placements, 12 approved assets, exact sources, responsive full-image viewing')
