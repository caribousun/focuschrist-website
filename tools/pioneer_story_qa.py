"""Preservation, source, and unique-picture contracts for the Pioneer enrichment."""
from pathlib import Path
import hashlib,json,re,subprocess
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
page=(ROOT/'pioneers.html').read_text(encoding='utf-8')
baseline=subprocess.check_output(['git','show','78f4a6cf61f223a1a1b330abab4edf992fa1cdfb:pioneers.html'],cwd=ROOT).decode()
topics=lambda s:re.findall(r'data-topic="([^"]+)"',s)
assert topics(page)==topics(baseline),'Existing29 topic identifiers/order changed'
assert len(re.findall(r'data-focus-expand="(?:timeline|trail)"',page))==29
assert page.count('class="pioneer-timeline-group"')==3
assert page.count('class="pioneer-story-card"')==18
triggers=re.findall(r'data-artwork-detail="([^"]+)"',page)
records=re.findall(r'data-artwork-detail-content="([^"]+)"',page)
assert len(triggers)==31 and len(set(triggers))==31 and sorted(triggers)==sorted(records)
manifest=json.loads((ROOT/'docs/pioneer-story-review.json').read_text())
assert len(manifest['images'])==18
hashes=[]
for r in manifest['images']:
 for field,digest in [('asset','sha256'),('preview','preview_sha256')]:
  assert hashlib.sha256((ROOT/r[field]).read_bytes()).hexdigest()==r[digest],r[field]
 hashes.append(r['sha256'])
 assert r['technical_visual_review']
 # Owner approved the exact family candidate, not every generated derivative.
 assert r['owner_approved'] == (r['id'] in {'07-elizabeth-family','12-jane-witness'}),r['id']
 if r['owner_approved']:
  assert r.get('approval_evidence'), 'Exact owner approval must remain recorded'
  if r['id']=='07-elizabeth-family':
   assert r.get('owner_reference_sha256')=='b791eff6c39b3a8007eb04a4498f9021878f251514ee93f1d142aaaac65c5c7e'
  else:
   assert r.get('owner_reference_sha256')==r['sha256']
assert len(set(hashes))==18,'A duplicated original cannot count as another picture'
# Preserve every preexisting Pioneer image and the owner-approved hero byte for byte.
assets=sorted(set(re.findall(r'assets/(?:pioneers/[^"\s<>]+\.webp|heroes/pioneers\.webp)',baseline)))
for asset in assets:
 old=subprocess.check_output(['git','show','78f4a6cf61f223a1a1b330abab4edf992fa1cdfb:'+asset],cwd=ROOT)
 assert (ROOT/asset).read_bytes()==old,asset
for phrase in ['Jane had been a baby','June Cranney Monson','unidentified','November 9','November 30','October 5','Ephraim Hanks','Mother’s Day']:
 assert phrase in page,phrase
assert 'my grandmother' not in page.lower()
assert 'site-common.js' in page and 'tell-my-story-too' in page
for key in triggers:
 if not key.startswith('pioneer-story-'):continue
 record=re.search(r'<article data-artwork-detail-content="'+key+r'".*?</article>',page,re.S)[0]
 paragraphs=re.findall(r'<p data-detail-paragraph>(.*?)</p>',record,re.S)
 assert len(paragraphs)>=2 and all(p.strip() for p in paragraphs),key
 assert 'data-detail-source="https://' in record,key
assert 'elizabeth-crook-panting_1900_486.pdf' not in page, 'Owner removed Elizabeth PDF actions'
print('Pioneer story QA: PASS (31unique studies,18new originals,29preserved topics,31preserved image variants/hero)')
