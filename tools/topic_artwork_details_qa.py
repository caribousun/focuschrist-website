#!/usr/bin/env python3
"""Verify every body-artwork entry can reach the shared contextual detail adapter."""
from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
def parents(n):
 while n.parent:
  n=n.parent;yield n
errors=[];count=0;preserved=0;panels=0
for page in [*sorted((ROOT/'answers').glob('*.html')),ROOT/'general-conference.html']:
 d=Document();d.feed(page.read_text(encoding='utf-8'));ns=list(d.root.walk())
 for asset,tag,attr in [('topic-artwork-details.js','script','src'),('topic-artwork-details.css','link','href')]:
  if sum(n.tag==tag and asset in n.attrs.get(attr,'') for n in ns)!=1:errors.append(f'{page.name}: missing or duplicate {asset}')
 for panel in [n for n in ns if n.has('fc-study-feature') and any(c.has('fc-study-visual') for c in n.walk())]:
  panels+=1
  if not panel.has('fc-study-feature--illustrated'):errors.append(page.name+': body artwork still nested in split study panel')
  for f in [n for n in panel.walk() if n.has('fc-study-visual')]:
   if f.parent is not panel:errors.append(page.name+': artwork not lifted out of narrow study/media column')
 for a in [n for n in ns if n.tag=='a' and 'href' in n.attrs and (n.parent.tag=='figure' or n.has('fc-marriage-era__art'))]:
  if not any(n.tag=='img' for n in a.walk()) or not any(n.tag=='main' for n in parents(a)):continue
  if any(n.has('fc-resource-card') or n.tag=='dialog' for n in parents(a)):continue
  if 'data-artwork-detail' in a.attrs:
   preserved+=1;continue
  count+=1;container=a.parent
  cap=next((n for n in container.walk() if n.tag=='figcaption' or n.has('fc-marriage-era__copy')),None)
  if cap is None or not cap.text().strip():errors.append(page.name+': missing approved body caption')
  sources=[n for n in cap.walk() if n.tag=='a' and urlsplit(n.attrs.get('href','')).hostname=='www.churchofjesuschrist.org'] if cap else []
  if not sources and page.name not in ('grief-and-faith.html','general-conference.html'):errors.append(page.name+': body source unavailable without unrelated page fallback')
  if 'data-full-image-viewer' not in a.attrs:errors.append(page.name+': native image fallback missing')
  if not (page.parent/urlsplit(a.attrs['href']).path).resolve().is_file():errors.append(page.name+': full image missing')
assert (count,preserved)==(95,3),(count,preserved)
assert panels==13,panels
if errors:raise SystemExit('\n'.join(errors))
print(f'TOPIC ARTWORK DETAILS QA PASS: {count} adapter pictures, {preserved} existing detail pictures, {panels} expanded illustration panels, 19 page dependencies')
