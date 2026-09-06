#!/usr/bin/env python3
"""Verify crawlable canonical study URLs and usable search/share metadata."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from datetime import date, datetime, timezone
import xml.etree.ElementTree as ET
import json
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://focuschrist.com'
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.meta={};self.canonical=[];self.title='';self.in_title=False;self.scripts=[];self.in_json=False;self.json='';self.feed(text)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if t=='title':self.in_title=True
  if t=='script' and a.get('type')=='application/ld+json':self.in_json=True;self.json=''
 def handle_data(self,d):
  if self.in_title:self.title+=d
  if self.in_json:self.json+=d
 def handle_endtag(self,t):
  if t=='title':self.in_title=False
  if t=='script' and self.in_json:self.scripts.append(self.json);self.in_json=False
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
entries=ET.parse(ROOT/'sitemap.xml').findall('s:url',ns)
urls=[e.findtext('s:loc',namespaces=ns) for e in entries]
errors=[];seen=set()
if len(urls)!=len(set(urls)):errors.append('Duplicate sitemap URLs')
for e,u in zip(entries,urls):
 parts=urlsplit(u)
 if parts.scheme!='https' or parts.netloc!='focuschrist.com' or parts.query or parts.fragment:errors.append(f'Noncanonical sitemap URL: {u}')
 p=ROOT/(parts.path.lstrip('/') or 'index.html')
 if not p.is_file():errors.append(f'Missing sitemap destination: {u}');continue
 page=Page(p.read_text());seen.add(p.resolve())
 if page.canonical!=[u]:errors.append(f'{p.name}: canonical and sitemap disagree')
 if not page.title.strip() or not page.meta.get('description','').strip():errors.append(f'{p.name}: missing search title/description')
 if 'noindex' in page.meta.get('robots','').lower():errors.append(f'{p.name}: sitemap page marked noindex')
 if page.meta.get('og:url')!=u:errors.append(f'{p.name}: social URL differs from canonical')
 for key in ['og:title','og:description','og:image','twitter:card']:
  if not page.meta.get(key):errors.append(f'{p.name}: missing {key}')
 img=urlsplit(page.meta.get('og:image',''))
 if img.netloc=='focuschrist.com' and not (ROOT/img.path.lstrip('/')).is_file():errors.append(f'{p.name}: missing share image')
 for script in page.scripts:
  try:json.loads(script)
  except ValueError:errors.append(f'{p.name}: invalid structured data JSON')
 modified=e.findtext('s:lastmod',namespaces=ns)
 if modified and date.fromisoformat(modified)>datetime.now(timezone.utc).date():errors.append(f'{p.name}: future modification date')
expected={p.resolve() for p in [*ROOT.glob('*.html'),*ROOT.glob('answers/*.html'),*ROOT.glob('art-study/*.html')] if p.name not in ['404.html','google3fa84a4b37862f36.html']}
if expected!=seen:errors.append('Published content and sitemap coverage differ')
robots=(ROOT/'robots.txt').read_text()
if 'Sitemap: '+ORIGIN+'/sitemap.xml' not in robots:errors.append('Robots lacks canonical sitemap')
if errors:raise SystemExit('\n'.join(errors))
print(f'Discovery QA PASSED: {len(urls)} canonical pages, complete sitemap coverage, search/share metadata and valid structured data. Indexing and traffic require external evidence.')
