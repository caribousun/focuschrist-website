"""Exactly three reviewed local composites; no new owner acceptance or generic waiver."""
from pathlib import Path
import hashlib,json,re,datetime as dt
from PIL import Image
SOURCES={'seek':'9b482deb6a3f8a80bf97f4481a4bcbc239b35a353ff0c9de78c34b398d0e70b1','joy':'db1577750a6efc66573cb4658b10136394a2414db1ba62ac2883b623be0cfb6d','shepherd':'4ae5bed79922f91dd6e136a24da712f046759f450ea03e658a5fd0fd5901c279'}
FAMILIES={'seek':('index.html','home-seek-study','assets/page-art/home-seek-study-four-marks-20261011',(1774,887),{'full':1774}),'joy':('answers/faith-in-jesus-christ-during-trials.html','christ-homecoming-celebration','assets/page-art/christ-world/christ-homecoming-celebration-dorsal-20261011',(1585,992),{'full':1585,'960':960,'480':480}),'shepherd':('birth-of-christ.html','13-shepherds-message','assets/page-art/birth-of-christ/13-shepherds-message-mixed-host-20261011',(1536,1024),{'full':1536,'800':800})}
LINEAGE='0be071a9e513376a722935fbca3e1a19445acfa353814aa7d5d6188f0b34fe69'
def require(ok,message):
 if not ok:raise ValueError('Three reviewed delivery: '+message)
def canonical(v):return hashlib.sha256((json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def digest(p):
    from test_opening_composition_binding import reviewed_opening_bytes
    from artwork_display_delivery import reviewed_bytes
    return hashlib.sha256(reviewed_opening_bytes(p) if p.name == 'unified-opening.js' else reviewed_bytes(p)).hexdigest()
def local(root,name):
 require(isinstance(name,str) and not Path(name).is_absolute() and '\\'not in name and ':'not in name,'unsafe path')
 p=(root/name).resolve();require(p.is_relative_to(root.resolve()) and p.is_file(),'missing local file '+name);return p
def bound(root,row):
 p=local(root,row['path']);require(digest(p)==row['sha256'],'changed evidence '+row['path']);return p
def stamp(x):
 d=dt.datetime.fromisoformat(x.replace('Z','+00:00'));require(d.tzinfo is not None,'undated review');return d
def validate(root,record,approved_binding,added,covered,rejected,pixel_hash,page_dependencies):
 require(record.get('schema')==1 and canonical(record)==approved_binding,'unreviewed record')
 spec=record['spec'];binding=canonical(spec)
 require(spec['registration_class']=='EXACT_THREE_REVIEWED_LOCAL_COMPOSITES' and spec['owner_final_image_acceptance']=='not-claimed' and spec['historical_generation_preflight']=='not-claimed-by-this-registration','invented owner or historical approval')
 require(len(spec['scenes'])==3 and {s['key']for s in spec['scenes']}==set(SOURCES),'family expansion/duplicate')
 require(spec['lineage']=={'path':'docs/three-reviewed-20261011/local-lineage.json','sha256':LINEAGE},'wrong lineage projection')
 lineage=json.loads(bound(root,spec['lineage']).read_bytes());require(lineage['projection_author']=='Newton' and lineage['limits'],'missing bounded independent lineage')
 assets=set();hashes=set();pixels=set();routes=set()
 from bs4 import BeautifulSoup
 for scene in spec['scenes']:
  key=scene['key'];route,section,stem,size,widths=FAMILIES[key];routes.add(route)
  require((scene['route'],scene['section'])==(route,section) and scene['source_sha256']==SOURCES[key] and SOURCES[key]not in rejected,'wrong source/owner')
  masterpath=str(Path(stem).parent/'masters'/(Path(stem).name+'.png')).replace('\\','/');expected={masterpath,*[stem+'-'+label+'.webp'for label in widths]}
  aa=scene['assets'];require(len(aa)==len(expected) and {a['path']for a in aa}==expected,'asset expansion/omission')
  masters=[a for a in aa if a['kind']=='original'];require(len(masters)==1 and masters[0]['path']==masterpath and masters[0]['sha256']==SOURCES[key],'wrong master')
  with Image.open(bound(root,masters[0]))as master:
   master.load();require(master.mode=='RGB' and master.size==size and master.format=='PNG','invalid master')
   for a in aa:
    p=bound(root,a);require(a['sha256']not in rejected and a['source_sha256']==SOURCES[key],'wrong/rejected ancestry')
    width=size[0]if a['kind']=='original'else widths[a['kind']];target=master if width==size[0]else master.resize((width,round(size[1]*width/size[0])),Image.Resampling.LANCZOS)
    with Image.open(p)as im:
     im.load();require(im.mode=='RGB' and getattr(im,'n_frames',1)==1 and im.format==('PNG'if a['kind']=='original'else'WEBP'),'invalid format/mode')
     require(im.size==target.size and im.tobytes()==target.tobytes(),'source or derivative pixel drift');require(im.size==(a['width'],a['height']),'dimensions drift')
    require(pixel_hash(p)==a['pixel_sha256'],'pixel digest drift');assets.add(a['path']);hashes.add(a['sha256']);pixels.add(a['pixel_sha256'])
  require(scene['preserved_originals'],'missing original preservation')
  for row in scene['preserved_originals']:bound(root,row)
  require(lineage['scenes'][key]['final_source_sha256']==SOURCES[key],'lineage source drift')
  from artwork_display_delivery import inverse
  soup=BeautifulSoup(inverse(route,local(root,route).read_bytes()).decode('utf8'),'html.parser')
  selector='a[data-artwork-detail="home-seek-study"]'if key=='seek'else'figure[data-exclusive-artwork="christ-homecoming-celebration"] > a'if key=='joy'else'figure[data-birth-art="13-shepherds-message"] > a'
  matches=soup.select(selector);require(len(matches)==1,'owner figure absent/duplicated');a=matches[0];require(stem+'-full.webp'in a['href'],'wrong active full')
  im=a.find('img');label='full'if key=='seek'else'960'if key=='joy'else'800';require(im and stem+'-'+label+'.webp'in im.get('src',''),'wrong thumbnail')
  if key=='seek':
   details=soup.select('[data-artwork-detail-content="home-seek-study"]');require(len(details)==1 and details[0]['data-detail-full']==stem+'-full.webp' and details[0]['data-detail-image']==stem+'-full.webp','detail/full source mismatch')
  else:require(a.get('data-topic-study')==('#continue-study'if key=='joy'else'art-study/the-living-christ.html'),'onward study changed')
  owners=[]
  for page in root.rglob('*.html'):
   if any(p in {'.git','node_modules','.qa-artifacts'}for p in page.relative_to(root).parts):continue
   doc=BeautifulSoup(page.read_text(encoding='utf8'),'html.parser');n=sum(stem in str(i.get('src',''))or stem in str(i.get('srcset',''))for i in doc.find_all('img'))
   if n:owners.append((page.relative_to(root).as_posix(),n))
  require(owners==[(route,1)],'duplicate/unrelated owner')
 require(len(assets)==9 and assets<=added and not assets&covered,'coverage overlap/omission')
 ctx=spec['context'];require(len(ctx)==len({r['path']for r in ctx}),'duplicate context')
 require(set().union(*(page_dependencies(root,r)for r in routes))<={r['path']for r in ctx},'missing page context')
 from historical_generated_index_context import ALLOWED, validate_context as validate_historical_index_context
 for row in ctx:
  if row['path'] in ALLOWED:validate_historical_index_context(root,row)
  else:bound(root,row)
 reviews=set();require(len(record['reviews'])==3,'three current reviews required')
 for row in record['reviews']:
  review=json.loads(bound(root,row).read_bytes());who=review['reviewer'];require(who in {'Fermi','Newton','Albert'} and who not in reviews,'duplicate/unknown reviewer');reviews.add(who)
  require(review['decision']=='CONCUR' and review['spec_sha256']==binding and stamp(review['reviewed_at'])>=stamp(record['prepared_at']),'stale/negative current review')
  require(review['no_individual_owner_acceptance_claim']is True and review['evidence'] and review['limits'],'missing scope')
  if who=='Albert':require(review['desktop_phone_direct_browser_review']is True,'root assembled review missing')
  else:require(review['source_pixel_review']is True and review['derivative_pixel_review']is True and review['assembled_context_review']is True,'finished scene/context review missing')
 require(not re.search(r'(?i)(\b[a-z]:[\\/]|file://|/Users/|docs.google.com/document/d/)',json.dumps(record)),'private data in public record')
 return assets,hashes,pixels
