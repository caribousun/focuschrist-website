#!/usr/bin/env python3
"""Verify every body-artwork entry can reach the shared contextual detail adapter."""
from pathlib import Path
import json
from urllib.parse import urlsplit
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
def parents(n):
 while n.parent:
  n=n.parent;yield n
errors=[];count=0;preserved=0;panels=0;life_assets=[];gap_assets=[]
for page in [*sorted((ROOT/'answers').glob('*.html')),ROOT/'general-conference.html']:
 d=Document();d.feed(page.read_text(encoding='utf-8'));ns=list(d.root.walk())
 for asset,tag,attr in [('topic-artwork-details.js','script','src'),('topic-artwork-details.css','link','href')]:
  if sum(n.tag==tag and asset in n.attrs.get(attr,'') for n in ns)!=1:errors.append(f'{page.name}: missing or duplicate {asset}')
 for panel in [n for n in ns if n.has('fc-study-feature') and any(c.has('fc-study-visual') for c in n.walk())]:
  panels+=1
  if not panel.has('fc-study-feature--illustrated'):errors.append(page.name+': body artwork still nested in split study panel')
  for f in [n for n in panel.walk() if n.has('fc-study-visual')]:
   if f.parent is not panel:errors.append(page.name+': artwork not lifted out of narrow study/media column')
 for a in [n for n in ns if n.tag=='a' and 'href' in n.attrs and (n.parent.tag=='figure' or n.has('fc-marriage-era__art') or n.has('fc-foundation-card__image'))]:
  if not any(n.tag=='img' for n in a.walk()) or not any(n.tag=='main' for n in parents(a)):continue
  if any(n.has('fc-resource-card') or n.tag=='dialog' for n in parents(a)):continue
  if 'data-artwork-detail' in a.attrs:
   preserved+=1;continue
  count+=1;container=a.parent
  cap=next((n for n in container.walk() if n.tag=='figcaption' or n.has('fc-marriage-era__copy') or n.has('fc-foundation-card-copy')),None)
  if cap is None or not cap.text().strip():errors.append(page.name+': missing approved body caption')
  sources=[n for n in cap.walk() if n.tag=='a' and urlsplit(n.attrs.get('href','')).hostname=='www.churchofjesuschrist.org'] if cap else []
  if not sources and 'data-topic-study' not in a.attrs and page.name not in ('grief-and-faith.html','general-conference.html'):errors.append(page.name+': body source unavailable without unrelated page fallback')
  if 'data-life-after-death-art' in container.attrs or 'data-study-gap-art' in container.attrs:
   # The anchor href is the native fallback. New figures intentionally let the
   # study adapter install the first action rather than the bare-image viewer.
   if 'data-full-image-viewer' in a.attrs:errors.append(page.name+': new picture must open study options first')
   if a.attrs.get('aria-haspopup')!='dialog':errors.append(page.name+': new picture dialog semantics missing')
   (life_assets if 'data-life-after-death-art' in container.attrs else gap_assets).append((page.parent/urlsplit(a.attrs['href']).path).resolve().relative_to(ROOT).as_posix())
  elif 'data-full-image-viewer' not in a.attrs:errors.append(page.name+': native image fallback missing')
  if not (page.parent/urlsplit(a.attrs['href']).path).resolve().is_file():errors.append(page.name+': full image missing')
life_review=json.loads((ROOT/'docs/life-after-death-art-review.json').read_text(encoding='utf-8'))['artworks']
reviewed_life_assets={entry['asset'] for entry in life_review}
assert len(life_assets)==18 and len(set(life_assets))==18 and set(life_assets)==reviewed_life_assets,'Life After Death adapter inventory differs from reviewed art'
gap_review=json.loads((ROOT/'docs/study-gap-art-review.json').read_text(encoding='utf-8'))['artworks']
assert len(gap_assets)==4 and len(set(gap_assets))==4 and set(gap_assets)=={entry['asset'] for entry in gap_review},'Study-gap adapter inventory differs from reviewed art'
assert (count-len(life_assets)-len(gap_assets),preserved)==(99,3),(count,preserved)
# Life After Death lifted its old illustrated feature panel into full reading
# sections. All twelve remaining panels still undergo the structural checks.
assert panels==12,panels
stand=Document();stand.feed((ROOT/'answers/stand-forever.html').read_text(encoding='utf-8'));stand_nodes=list(stand.root.walk())
foundation_images=[n for n in stand_nodes if n.tag=='a' and n.has('fc-foundation-card__image')]
assert len(foundation_images)==4,len(foundation_images)
for image in foundation_images:
 study=image.attrs.get('data-topic-study','');assert study and (ROOT/'answers'/study).is_file(),study
 card=next(n for n in parents(image) if n.has('fc-foundation-card'))
 direct=next((n for n in card.walk() if n.tag=='a' and n.has('fc-foundation-card-action')),None)
 assert direct is not None and direct.attrs.get('href')==study,(study,direct.attrs.get('href') if direct else None)
 assert 'data-full-image-viewer' in image.attrs and 'data-full-image-alt' in image.attrs
adapter=(ROOT/'topic-artwork-details.js').read_text(encoding='utf-8')
assert "if (!record.study) {" in adapter,'Foundation cards must not inherit unrelated section sources'
assert "if (record.study) pill(record.studyLabel, record.study, true);" in adapter,'Foundation topic action missing from detail panel'
if errors:raise SystemExit('\n'.join(errors))
print(f'TOPIC ARTWORK DETAILS QA PASS: {count} adapter pictures, {preserved} existing detail pictures, {panels} expanded illustration panels, 19 page dependencies')
