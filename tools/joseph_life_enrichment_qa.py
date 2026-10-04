"""Exact added family originals and delivery checks, not rendered approval."""
import hashlib,json
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from joseph_research_acceptance import check_exact_review,check_original_page_exclusivity
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'marriage-partnership-1827','household-gift-harmony-1828','emma-early-scribe-1828','hyrum-reading-before-carthage-1844','emma-relief-service-1842','care-after-loss-1828','emma-family-letter-1838','joseph-household-labor-1828','journey-to-harmony-1827','emma-prayer-during-arrest-1830'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 data=json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8-sig'))['scenes']
 records=json.loads((ROOT/'docs/joseph-life-art-review.json').read_text())['originals']
 assert {r['id'] for r in data}=={r['id'] for r in records}==EXPECTED and len(data)==len(records)==10,'Ten deliberate family scenes required'
 assert len({r['sha256'] for r in records})==10,'Repeated bytes cannot count as originals'
 doc=BeautifulSoup((ROOT/'joseph-smith-likeness.html').read_text(encoding='utf-8'),'html.parser')
 assert len(doc.select('img'))>=20,'Main study needs at least20 meaningful picture placements; count is necessary only'
 assert len(doc.select('.joseph-life-scene'))==10,'Ten enriched scene articles required'
 for row in data:
  r=next(x for x in records if x['id']==row['id']);im=row['image'];section=doc.select_one('#life-'+row['id']);assert section
  assert row['image_status']=='accepted' and r['sha256']==im['sha256']==digest(ROOT/im['src'])
  assert r['asset']==im['src'] and r['owning_page']=='joseph-smith-likeness.html' and r['owning_section']==section['id']
  figure=section.select_one('figure');assert figure and figure.get('data-exclusive-artwork')==section['id']
  title=section.select_one('h3');duplicate=figure.select_one('h4.joseph-life-caption-title')
  assert title and not title.has_attr('hidden') and title.get_text(strip=True)==row['heading'],'Visible scene title required'
  assert duplicate and duplicate.has_attr('hidden') and duplicate.get_text(strip=True)==row['heading'],'Redundant modal-title data must be explicitly hidden, not a clipped caption'
  assert figure.select_one('a[href="'+im['src']+'"][aria-haspopup="dialog"]')
  img=figure.select_one('img');assert img and img.get('data-source-original',img.get('src'))==im['src'] and img.get('alt')==im['alt']
  actual=' '.join(section.stripped_strings)
  for value in [row['heading'],row['date_label'],*row['paragraphs'],row['interpretation_limit'],row['reflection']]:assert value in actual,'Missing local scene content: '+row['id']
  assert all(section.select_one('a[href="'+s['url']+'"]') for s in row['sources'])
  assert doc.select_one('nav.joseph-life-nav a[href="#life-'+row['id']+'"]')
  for key in ['fermi_preflight','newton_preflight','fermi_finished_pixels','newton_finished_pixels']:
   receipt=json.loads((ROOT/r[key]).read_text());check_exact_review(r,receipt,finished=key.endswith('finished_pixels'))
   if key.endswith('finished_pixels'):assert receipt.get('whole_image_review') is True,'Whole exact final-image review missing'
 delivery=json.loads((ROOT/'docs/joseph-art-delivery.json').read_text()); owners={}
 for manifest in ['joseph-life-art-review.json','joseph-portrait-research-art-review.json']:
  for r in json.loads((ROOT/'docs'/manifest).read_text())['originals']:owners[r['asset']]=r['owning_page']
 assert set(delivery)==set(owners),'Delivery inventory differs from20new originals'
 hashes=[]
 for source,d in delivery.items():
  assert digest(ROOT/source)==d['source_sha256']
  hashes.append({'sha256':d['source_sha256'],'owning_page':owners[source]})
  for v in d['variants']:
   p=ROOT/v['asset'];assert digest(p)==v['sha256'] and p.stat().st_size==v['bytes']
   with Image.open(p) as image:assert image.format=='WEBP' and image.size==(v['width'],v['height'])
   assert abs(v['width']/v['height']-d['width']/d['height'])<0.005,'Delivery must preserve source proportions'
   hashes.append({'sha256':v['sha256'],'owning_page':owners[source]})
  page=BeautifulSoup((ROOT/owners[source]).read_text(encoding='utf-8'),'html.parser');images=page.select('img[data-source-original="'+source+'"]');assert len(images)==1
  img=images[0];assert img['src']==d['default'] and img.get('loading')=='lazy' and img.get('decoding')=='async'
  assert img.get('srcset')==', '.join(v['asset']+' '+str(v['width'])+'w' for v in d['variants']) and img.get('sizes')
 sizes={ (ROOT/s).stat().st_size for s in delivery }|{v['bytes'] for d in delivery.values() for v in d['variants']};pages={};cache={}
 for p in ROOT.rglob('*.html'):
  if any(t in {'work','outputs','node_modules','.git'} for t in p.relative_to(ROOT).parts):continue
  ds=[]
  for im in BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser').select('img[src]'):
   paths=[im['src']]+[x.strip().split()[0] for x in im.get('srcset','').split(',') if x.strip()]
   for src in paths:
    target=(p.parent/src.split('?')[0]).resolve()
    if not target.is_file() or target.stat().st_size not in sizes:continue
    if target not in cache:cache[target]=digest(target)
    ds.append(cache[target])
  pages[p.relative_to(ROOT).as_posix()]=ds
 check_original_page_exclusivity(hashes,pages)
 return {'result':'STRUCTURAL_PASS_NOT_RENDERED_CONCURRENCE','new_main_originals':10,'main_picture_placements':len(doc.select('img')),'new_delivery_sources':20,'responsive_variants':sum(len(d['variants']) for d in delivery.values())}
if __name__=='__main__':print(json.dumps(check(),indent=2))
