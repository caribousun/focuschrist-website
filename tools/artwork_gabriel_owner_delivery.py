"""Exactly two owner-approved Gabriel replacements; no historical or generic exemption."""
from pathlib import Path
import datetime as dt
import hashlib,json,re
from PIL import Image

SOURCES={'07-zacharias':'5315c94322adca83c8d3c75dad74f647f2fe395c9e0c751541aeec11461c73b4','08-annunciation':'d0b7ccfc5fc16b6697e0c54e488d3869eab003e8f10fe326511a0fbe7394fa4a'}
ORIGINALS={'07-zacharias':'fca9e54e4431a56cb052a1e9198b97f314c5ac30af8eab6396dd8c71b0986f33','08-annunciation':'a643f31dbb22808a66b266c90604403274847aab70acaa741d090bb56c22773e'}
PREFIX='assets/page-art/birth-of-christ/'
ROUTE='birth-of-christ.html'
def require(ok,message):
 if not ok:raise ValueError('Gabriel owner delivery: '+message)
def canonical(v):return hashlib.sha256((json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def digest(p):
    from test_opening_composition_binding import reviewed_opening_bytes
    from artwork_display_delivery import reviewed_bytes
    return hashlib.sha256(reviewed_opening_bytes(p) if p.name == 'unified-opening.js' else reviewed_bytes(p)).hexdigest()
def local(root,name):
 require(isinstance(name,str)and not Path(name).is_absolute()and '\\'not in name and ':'not in name,'unsafe path')
 p=(root/name).resolve();require(p.is_relative_to(root.resolve())and p.is_file(),'missing local evidence '+name);return p
def stamp(s):
 d=dt.datetime.fromisoformat(s.replace('Z','+00:00'));require(d.tzinfo is not None,'undated review');return d
def bound_file(root,row):
 p=local(root,row['path']);require(digest(p)==row['sha256'],'changed evidence '+row['path']);return p
def validate(root,record,approved_binding,added,covered,rejected,pixel_hash,page_dependencies):
 require(record.get('schema')==1 and canonical(record)==approved_binding,'unreviewed exact record')
 spec=record['spec'];binding=canonical(spec)
 require(spec['classification']=='owner-approved-scripture-illustrations'and spec['route']==ROUTE,'wrong scope')
 require(spec['registration_class']=='EXACT_OWNER_APPROVED_REPLACEMENTS'and spec['historical_preparation_claim'] is False,'invented historical approval')
 scenes=spec['scenes'];require(len(scenes)==2 and {s['key']for s in scenes}==set(SOURCES),'family expansion/duplicate')
 expected_all=set();hashes=set();pixels=set()
 for scene in scenes:
  key=scene['key'];sourcepin=SOURCES[key];require(scene['source_sha256']==sourcepin and sourcepin not in rejected,'wrong/rejected source')
  family=key+'-owner-20261011';expected={PREFIX+'masters/'+family+'.png',PREFIX+family+'-full.webp',PREFIX+family+'-800.webp'}
  assets=scene['assets'];require(len(assets)==3 and {a['path']for a in assets}==expected,'asset omission/expansion/duplicate')
  masters=[a for a in assets if a['kind']=='original'];require(len(masters)==1 and masters[0]['sha256']==sourcepin,'wrong master')
  master=Image.open(bound_file(root,masters[0]));master.load();require(master.mode=='RGB'and master.size==(1536,1024),'wrong source dimensions/mode')
  for a in assets:
   p=bound_file(root,a);require(a['sha256']not in rejected,'rejected delivery')
   with Image.open(p)as im:
    require(getattr(im,'n_frames',1)==1 and im.mode=='RGB','invalid decoded image')
    target=master.resize((800,533),Image.Resampling.LANCZOS)if a['path'].endswith('-800.webp')else master
    require(im.size==target.size and im.tobytes()==target.tobytes(),'lossless source/derivative equivalence failed')
    require([im.width,im.height]==[a['width'],a['height']],'dimension record drift')
    require(im.format==('PNG'if a['kind']=='original'else'WEBP'),'format drift')
   require(pixel_hash(p)==a['pixel_sha256'],'decoded digest drift');hashes.add(a['sha256']);pixels.add(a['pixel_sha256'])
  require(digest(local(root,PREFIX+key+'-full.webp'))==ORIGINALS[key],'frozen original changed')
  owner=json.loads(bound_file(root,scene['owner_approval']).read_text(encoding='utf8'))
  require(owner['owner']=='Wyatt'and owner['exact_response']=='approve'and owner['image_sha256']==sourcepin,'missing exact owner approval')
  require(stamp(owner['recorded_at'])<=stamp(record['prepared_at']),'backdated preparation')
  expected_all|=expected
 require(expected_all<=added and not expected_all&covered,'overlapping/unregistered coverage')
 audit=json.loads(bound_file(root,spec['lineage']).read_text(encoding='utf8'))
 require(audit['reviewer']=='Newton'and audit['status']=='VERIFIED_BOUNDED_NATIVE_AND_LOCAL_LINEAGE','unreviewed lineage')
 require(audit['approved_outputs']==SOURCES and audit['original_references']==ORIGINALS,'lineage outputs/references differ')
 require(audit['mary']['base_sha256']=='de731190eaa5849ac3f8eab5fc46b44ba0a78b5af426b2e1f6adb1d603566b5c'and audit['mary']['donor_sha256']=='66d303e00e559d46b4f5e756282808e2f012deb50c1fa8d18f9f928ab5f0750e','wrong Mary ancestry')
 require(audit['mary']['mask_sha256']=='811522abf50ec343d9022e4c8ce992c4b9af818c17cb22fa44e7fde3222c2965'and audit['mary']['changed_pixels']==164 and audit['mary']['editable_pixels']==166 and audit['mary']['outside_mask_exact'] is True,'wrong local preservation')
 events=audit['generation_events'];require(len(events)==3 and {e['output_sha256']for e in events}=={SOURCES['07-zacharias'],audit['mary']['base_sha256'],audit['mary']['donor_sha256']},'missing/duplicate generation node')
 for event in events:
  require(stamp(event['loaded_at'])<=stamp(event['dispatched_at'])<stamp(event['completed_at']),'reversed generation chronology')
  for k in ['load_event_sha256','dispatch_event_sha256','completion_event_sha256','prompt_sha256']:require(re.fullmatch('[0-9a-f]{64}',event[k])is not None,'malformed native digest')
 require(audit['limits'],'missing audit limits')
 context=spec['context'];require(len(context)==len({r['path']for r in context}),'duplicate context')
 require(page_dependencies(root,ROUTE)<={r['path']for r in context},'incomplete actual context')
 for row in context:bound_file(root,row)
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(local(root,ROUTE).read_text(encoding='utf8'),'html.parser')
 for key in SOURCES:
  figs=soup.select('figure[data-birth-art="'+key+'"]');require(len(figs)==1,'wrong/duplicate owning figure')
  fig=figs[0];family=key+'-owner-20261011';require(fig.find('a')['href']==PREFIX+family+'-full.webp'and fig.find('img')['src']==PREFIX+family+'-800.webp','wrong active source')
  require(fig.find('a').get('data-topic-study')=='art-study/the-living-christ.html','study destination drift')
  owners=[]
  for page in root.rglob('*.html'):
   if any(part in {'.git','node_modules','.qa-artifacts'}for part in page.relative_to(root).parts):continue
   doc=BeautifulSoup(page.read_text(encoding='utf8'),'html.parser')
   count=sum(family in str(img.get('src',''))or family in str(img.get('srcset',''))for img in doc.find_all('img'))
   if count:owners.append((page.relative_to(root).as_posix(),count))
  require(owners==[(ROUTE,1)],'duplicate or wrong owner')
 reviews=record['reviews'];require(len(reviews)==3,'three actual current reviews required');roles=set()
 for row in reviews:
  review=json.loads(bound_file(root,row).read_text(encoding='utf8'));role=review['reviewer'];require(role in {'Albert','Fermi','Newton'}and role not in roles,'duplicate/missing reviewer');roles.add(role)
  require(review['spec_sha256']==binding and review['decision']=='CONCUR'and stamp(review['reviewed_at'])>=stamp(record['prepared_at']),'stale/current negative review')
  require(review['source_and_derivative_pixels_reviewed']is True and review['current_context_reviewed']is True and review['evidence']and review['limits'],'missing actual review coverage')
  if role=='Albert':require(review['desktop_phone_browser_review']is True,'missing root browser review')
 require(not re.search(r'(?i)(\b[a-z]:[\\/]|file://|/Users/|docs.google.com/document/d/)',json.dumps(record)),'private path/authority in public record')
 return expected_all,hashes,pixels
