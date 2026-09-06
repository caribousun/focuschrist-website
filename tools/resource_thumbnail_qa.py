#!/usr/bin/env python3
"""Gate canonical-page visual coverage and exact source/thumbnail relationships."""
import hashlib,json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Cards(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.current=None;self.ids=set();self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a: self.ids.add(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='article' and 'data-resource-key' in a:self.current={'key':a['data-resource-key'],'links':[],'images':[]};self.cards.append(self.current)
  if self.current:
   if tag=='a':self.current['links'].append(a)
   if tag=='img':self.current['images'].append(a)
 def handle_endtag(self,tag):
  if tag=='article':self.current=None
sources={r['key']:r for r in json.loads((ROOT/'docs/watch-source-ledger.json').read_text())['videos']}
sources.update({r['key']:r for r in json.loads((ROOT/'docs/resource-thumbnail-ledger.json').read_text())['resources']})
coverage=json.loads((ROOT/'docs/resource-page-coverage.json').read_text()); errors=[];count=0
canonical={urlsplit(x.text).path.lstrip('/') or 'index.html' for x in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')}
assert set(coverage)==canonical,'Every canonical page needs explicit coverage'
for file,keys in coverage.items():
 p=ROOT/file;parser=Cards();parser.feed(p.read_text());actual=[x['key'] for x in parser.cards]
 if actual!=keys:errors.append(f'{file}: coverage differs: {actual}')
 for c in parser.cards:
  count+=1;r=sources[c['key']]
  if len(c['images'])!=1 or len(c['links'])!=2:errors.append(f'{file}: malformed resource card {c["key"]}');continue
  if any(a.get('href')!=r['url'] for a in c['links']):errors.append(f'{file}: mismatched source {c["key"]}')
  if any(any(k in a for k in ['data-hero-viewer','data-full-image-viewer']) for a in c['links']):errors.append(f'{file}: preview hijacked by artwork viewer')
  i=c['images'][0];img=(p.parent/i['src']).resolve()
  if img!=ROOT/r['local_thumbnail'] or hashlib.sha256(img.read_bytes()).hexdigest()!=r['sha256']:errors.append(f'{file}: image mismatch')
  if any(str(r[k])!=i.get(k) for k in ['width','height']) or i.get('loading')!='lazy':errors.append(f'{file}: missing intrinsic sizing/lazy load')
 for link in parser.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(f'{file}: missing {link}');continue
  if u.fragment and target.suffix=='.html':
   q=Cards();q.feed(target.read_text())
   if unquote(u.fragment) not in q.ids and u.fragment not in ['ask-question']:errors.append(f'{file}: missing anchor {link}')
if errors:raise SystemExit('\n'.join(errors))
print(f'RESOURCE THUMBNAIL QA PASS: {len(coverage)} pages, {count} source-matched cards')
