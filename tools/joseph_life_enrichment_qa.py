"""Exact added family originals and delivery checks, not rendered approval."""
import hashlib,json
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from artwork_reviewed_corrections import canonical as correction_canonical, evidence as correction_evidence
from joseph_research_acceptance import check_exact_review,check_original_page_exclusivity
from joseph_research_acceptance import check_artwork_badges_and_footer
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'marriage-partnership-1827','household-gift-harmony-1828','emma-early-scribe-1828','hyrum-reading-before-carthage-1844','emma-relief-service-1842','care-after-loss-1828','emma-family-letter-1838','joseph-household-labor-1828','journey-to-harmony-1827','emma-prayer-during-arrest-1830'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
CORRECTION_SCENES={'household-gift-harmony-1828': 'SITE10', 'journey-to-harmony-1827': 'SITE07_EXPRESSION', 'care-after-loss-1828': 'SITE09', 'emma-family-letter-1838': 'SITE12', 'emma-early-scribe-1828': 'SITE08','emma-prayer-during-arrest-1830': 'SITE11'}
CORRECTION_RECORDS={'SITE07', 'SITE08', 'SITE11', 'SITE01_IDENTITY', 'SITE10', 'SITE05_IDENTITY', 'SITE01', 'SITE12', 'SITE09', 'SITE07_EXPRESSION', 'SITE02_IDENTITY'}
CURRENT_SCENES={'SITE01': 'SITE01_IDENTITY', 'SITE07': 'SITE07_EXPRESSION', 'SITE08': 'SITE08', 'SITE09': 'SITE09', 'SITE10': 'SITE10', 'SITE12': 'SITE12', 'SITE11': 'SITE11', 'SITE02': 'SITE02_IDENTITY', 'SITE05': 'SITE05_IDENTITY'}
CURRENT_BINDING='42ba0b7b149470f37c30c7677946b43695cf8f991f6158f7e97fe6b09b4f2691'
SITE10_BINDING='6f9510c88845fbef288289a33beab1a841f414ea65ab1212577c02e284d27a75'
def current_corrections():
 record=json.loads((ROOT/'docs/artwork-correction-reviews.json').read_text(encoding='utf-8'))
 assert record['schema']==1 and record['status']=='REVIEWED_EXACT_EVIDENCE'
 assert record['approved_binding']==CURRENT_BINDING
 assert correction_canonical(record['spec'])==CURRENT_BINDING,'Unreviewed correction specification'
 families=record['spec']['families'];assert len(families)==11 and {f['id'] for f in families}==CORRECTION_RECORDS
 assert record['spec']['current_scene_records']==CURRENT_SCENES
 resolved={}
 for family in families:
  if family['id'] in {'SITE01_IDENTITY','SITE02_IDENTITY','SITE05_IDENTITY'}:
   assert not family.get('immutable_originals'), 'Identity must preserve prior lineage, not invent originals'
   sources=family['preserved_assets']+[family['prior_source']]+family['identity_references']
  else:sources=family['immutable_originals']
  for item in sources+family['evidence']+family['assets']:
   correction_evidence(ROOT,item,set())
  assets=family['assets'];assert len(assets)==(3 if family['id'] in {'SITE02_IDENTITY','SITE05_IDENTITY'} else 4)
  for item in assets:
   path=ROOT/item['path'];assert path.stat().st_size==item['bytes']
   with Image.open(path) as image:assert image.size==tuple(item['dimensions']) and image.format==item['format']
  source=assets[0];variants=[{'asset':a['path'],'width':a['dimensions'][0],'height':a['dimensions'][1],'sha256':a['sha256'],'bytes':a['bytes']} for a in assets[1:]]
  resolved[family['id']]=source,{'source_sha256':source['sha256'],'width':source['dimensions'][0],'height':source['dimensions'][1],'variants':variants,'default':variants[-1]['asset']}
 # Preserve historical family IDs while selecting each explicitly pinned current scene.
 for scene,record_id in CURRENT_SCENES.items():resolved[scene]=resolved[record_id]
 return resolved

def check():
 corrections=current_corrections()
 data=json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8-sig'))['scenes']
 records=json.loads((ROOT/'docs/joseph-life-art-review.json').read_text())['originals']
 assert {r['id'] for r in data}==EXPECTED|{'joseph-hyrum-bond'} and {r['id'] for r in records}==EXPECTED and len(data)==11 and len(records)==10,'Ten deliberate family scenes required'
 assert len({r['sha256'] for r in records})==10,'Repeated bytes cannot count as originals'
 doc=BeautifulSoup((ROOT/'answers/who-was-joseph-smith.html').read_text(encoding='utf-8'),'html.parser')
 # Normalize nested-route local assets for existing exact source-delivery assertions.
 for node in doc.select('[src], [href], [data-source-original]'):
  for key in ('src','href','data-source-original'):
   if node.get(key,'').startswith('../'):node[key]=node[key][3:]
 check_artwork_badges_and_footer(doc)
 closing=json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8-sig'))['closing']
 assert 'The original letter to Phelps is not extant; a contemporary letterbook copy survives.' in closing.get('interpretation_limit',''), 'Closing internal provenance must remain preserved'
 assert doc.select_one('#life-remembrance a[href="https://www.josephsmithpapers.org/paper-summary/letter-to-william-w-phelps-22-july-1840/1/"]'), 'Preserve the actual letterbook source'
 retired_commentary = (
  'The birth dates above follow the family list in the linked Susquehanna history.',
  'The meeting record’s historical notes preserve this recent loss alongside her public work.',
  'The surviving letterbook copy preserves that act of forgiveness.',
  'Love and gratitude can inspire careful study: honoring a person also means being truthful about what the record preserves.',
  'The original letter to Phelps is not extant; a contemporary letterbook copy survives.',
 )
 assert not any(text in doc.get_text(' ',strip=True) for text in retired_commentary), 'Owner-rejected routine source-checking commentary returned to biography prose'
 assert len(doc.select('img'))>=20,'Main study needs at least20 meaningful picture placements; count is necessary only'
 assert len([n for n in doc.select('.joseph-life-scene') if not n.find_parent(id='lucy-family-stories')])==11,'Original ten family scenes plus reviewed brothers scene remain; Lucy ten have their separate strict gate'
 for row in data:
  if row['id']=='joseph-hyrum-bond':
   prior=next(r for r in json.loads((ROOT/'docs/art-study-image-review.json').read_text())['pages']['joseph-smith-likeness.html'] if r['slot']=='brothers')
   assert prior['reviewed'] and prior['owner_approved'] and prior['sha256']==row['image']['sha256']==digest(ROOT/prior['asset'])
   assert doc.select_one('#life-joseph-hyrum-bond a[href="'+prior['asset']+'"]'),'Moved brothers full-size action missing'
   continue
  r=next(x for x in records if x['id']==row['id']);im=row['image'];section=doc.select_one('#life-'+row['id']);assert section
  assert row['image_status']=='accepted' and r['sha256']==digest(ROOT/r['asset'])
  if row['id'] in CORRECTION_SCENES:
   corrected,corrected_delivery=corrections[CORRECTION_SCENES[row['id']]]
   assert im['src']==corrected['path'] and im['sha256']==corrected['sha256']==digest(ROOT/im['src'])
   assert im['correction_binding']==SITE10_BINDING and im['correction_record']=='docs/artwork-correction-reviews.json'
   if row['id']=='household-gift-harmony-1828':assert row['date_label']=='Harmony · December 4, 1828'
   assert any(old.get('src')==r['asset'] and old['sha256']==r['sha256'] for old in row['retained_previous_images'])
  else:assert r['asset']==im['src'] and r['sha256']==im['sha256']==digest(ROOT/im['src'])
  assert r['owning_page']=='answers/who-was-joseph-smith.html' and r['owning_section']==section['id']
  figure=section.select_one('figure');assert figure and figure.get('data-exclusive-artwork')==section['id']
  title=section.select_one('h3');duplicate=figure.select_one('h4.joseph-life-caption-title')
  assert title and not title.has_attr('hidden') and title.get_text(strip=True)==row['heading'],'Visible scene title required'
  assert duplicate and duplicate.has_attr('hidden') and duplicate.get_text(strip=True)==row['heading'],'Redundant modal-title data must be explicitly hidden, not a clipped caption'
  assert figure.select_one('a[href="'+im['src']+'"][aria-haspopup="dialog"]')
  img=figure.select_one('img');assert img and img.get('data-source-original',img.get('src'))==im['src'] and img.get('alt')==im['alt']
  actual=' '.join(section.stripped_strings)
  assert row.get('interpretation_limit'), 'Internal scene provenance must remain preserved'
  assert row.get('visitor_caption'), 'Owner-reviewed visitor caption required'
  for value in [row['heading'],row['date_label'],*row['paragraphs'],row['visitor_caption'],row['reflection']]:assert value in actual,'Missing local scene content: '+row['id']
  assert all(section.select_one('a[href="'+s['url']+'"]') for s in row['sources'])
  assert doc.select_one('nav.joseph-life-nav a[href="#life-'+row['id']+'"]')
  for key in ['fermi_preflight','newton_preflight','fermi_finished_pixels','newton_finished_pixels']:
   receipt=json.loads((ROOT/r[key]).read_text());check_exact_review(r,receipt,finished=key.endswith('finished_pixels'))
   if key.endswith('finished_pixels'):assert receipt.get('whole_image_review') is True,'Whole exact final-image review missing'
 archives=json.loads((ROOT/'docs/joseph-family-archival-art.json').read_text(encoding='utf-8'))['items']
 assert len(archives)==5 and len({a['asset'] for a in archives})==5,'Five distinct historical family references required'
 for archive in archives:
  assert archive['kind']=='historical_reference' and archive['owning_page']=='answers/who-was-joseph-smith.html'
  asset=ROOT/archive['asset'];assert digest(asset)==archive['sha256'],'Archival source bytes changed'
  with Image.open(asset) as image:assert image.size==(archive['width'],archive['height'])
  section=doc.find(id=archive['owning_section']);assert section is not None
  image=section.select_one('img[src="'+archive['asset']+'"]');assert image and image['alt']==archive['alt']
  figure=image.find_parent('figure');assert archive['caption'] in figure.get_text(' ',strip=True),'Dated source caption missing'
  assert figure.select_one('a[href="'+archive['asset']+'"]') and figure.select_one('a[href="'+archive['source_url']+'"]'),'Archive full image and actual catalogue required'
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
  display_source=source;display_delivery=d
  source_corrections={'assets/page-art/joseph-smith-likeness/family/household-gift-harmony-1828-wardrobe-v2.png': 'SITE10', 'assets/page-art/joseph-smith-likeness/family/journey-to-harmony-1827-corrected-v2.png': 'SITE07_EXPRESSION', 'assets/page-art/joseph-smith-likeness/family/care-after-loss-1828-wardrobe-v2.png': 'SITE09', 'assets/page-art/joseph-smith-likeness/family/emma-family-letter-1838-wardrobe-v2.png': 'SITE12', 'assets/page-art/joseph-smith-likeness/family/emma-early-scribe-1828-wardrobe-v2.png': 'SITE08', 'assets/page-art/joseph-smith-likeness/family/emma-prayer-during-arrest-1830.png': 'SITE11'}
  if source in source_corrections:
   corrected,corrected_delivery=corrections[source_corrections[source]]
   display_source=corrected['path'];display_delivery=corrected_delivery
   hashes.extend([{'sha256':a['sha256'],'owning_page':owners[source]} for a in [corrected,*display_delivery['variants']]])
  page=BeautifulSoup((ROOT/owners[source]).read_text(encoding='utf-8'),'html.parser');images=page.select('img[data-source-original="'+display_source+'"], img[data-source-original="../'+display_source+'"]');assert len(images)==1
  img=images[0];assert img['src'].removeprefix('../')==display_delivery['default'] and img.get('loading')=='lazy' and img.get('decoding')=='async'
  assert img.get('srcset','').replace('../','')==', '.join(v['asset']+' '+str(v['width'])+'w' for v in display_delivery['variants']) and img.get('sizes')
 sizes={ (ROOT/s).stat().st_size for s in delivery }|{v['bytes'] for d in delivery.values() for v in d['variants']}|{a['bytes'] for corrected,delivered in corrections.values() for a in [corrected,*delivered['variants']]};pages={};cache={}
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
 # Owner-rejected unrelated references are absent here, preserved at their owners.
 for key,owner in [('bb-philip-isaiah','jesus-christ/before-bethlehem.html'),('modern-prayer','answers/jesus-christ-latter-day-saint-beliefs.html')]:
  assert not doc.select('[data-linked-picture-reference="'+key+'"]'), 'Unrelated reference returned to Joseph biography: '+key
  assert not any(key in img.get('src','') for img in doc.select('img')), 'Unrelated image returned to Joseph biography: '+key
  owning=BeautifulSoup((ROOT/owner).read_text(encoding='utf-8'),'html.parser')
  picture=owning.find(id='picture-'+key)
  assert picture and picture.select_one('img'), 'Owner artwork must remain available: '+key
 for key in ['rt-vision-1832','rt-persuasion']:
  assert doc.select_one('[data-linked-picture-reference="'+key+'"]'), 'Direct Joseph Restoration reference lost: '+key
 counsel=doc.select_one('[data-linked-picture-reference="rt-persuasion"]').get_text(' ',strip=True)
 assert 'Joseph' in counsel and 'Liberty Jail' in counsel, 'Retained persuasion card must identify Joseph historical context'
 return {'result':'STRUCTURAL_PASS_NOT_RENDERED_CONCURRENCE','new_main_originals':10,'main_picture_placements':len(doc.select('img')),'new_delivery_sources':20,'responsive_variants':sum(len(d['variants']) for d in delivery.values())}
if __name__=='__main__':print(json.dumps(check(),indent=2))
