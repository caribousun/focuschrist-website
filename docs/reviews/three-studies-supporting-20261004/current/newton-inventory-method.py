from pathlib import Path
import json,hashlib,io,re,sys,xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote
from itertools import combinations
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw
import cv2,numpy as np
S=Path(r'C:/Users/wyatt/Documents/Codex/2026-10-03/joseph-research-site')
P=Path(r'C:/Users/wyatt/Documents/Codex/2026-10-04/three-art-studies-integration-continuation/work')
W=Path(__file__).parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(S/'tools'));from art_study_current_mandate_qa import Inventory
new=json.loads((S/'docs/three-studies-supporting-review-20261004.json').read_text(encoding='utf-8'))['records']
ret=json.loads(Path(r'C:/Users/wyatt/Documents/Codex/2026-10-04/full-site-enriched-review-continuation/work/newton/retained15-review.json').read_text(encoding='utf-8'))['rows']
allrows={x['asset']:x for x in ret+new};assert len(allrows)==30
lineage=[];tiles=[]
for r in new:
 source=Path(r['original_file']);assert h(source)==r['source_sha256'];im=Image.open(source).convert('RGB');assert im.size==(1536,1024)
 for field,sz,q,hfield in [('asset',(1536,1024),92,'sha256'),('thumbnail',(800,533),88,'thumbnail_sha256')]:
  p=S/r[field];assert h(p)==r[hfield];buf=io.BytesIO();expected=im if field=='asset' else im.resize(sz,Image.Resampling.LANCZOS);expected.save(buf,'WEBP',quality=q,method=6);assert hashlib.sha256(buf.getvalue()).hexdigest()==h(p),(r['key'],field)
 lineage.append({'asset':r['asset'],'source_sha256':r['source_sha256'],'full_sha256':r['sha256'],'thumbnail_sha256':r['thumbnail_sha256'],'reproduced_full_and_thumb_encoding_exact':True,'full_dimensions':[1536,1024],'thumb_dimensions':[800,533],'uncropped':True})
lookup={}
for r in ret+new:
 lookup[r['asset']]=r['asset'];lookup[r['asset'].replace('/full/','/thumbs/')]=r['asset']
routes=sorted({urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(S/'sitemap.xml').getroot().iter() if n.tag.endswith('loc')});occur={};hashes={}
for route in routes:
 p=S/route;hashes[route]=h(p);dom=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 for tag in dom.find_all(True):
  for attr,val in tag.attrs.items():
   if not isinstance(val,str):continue
   for raw in re.split(r'[,\s]+',val):
    u=urlsplit(raw)
    if u.scheme or u.netloc or not u.path:continue
    p=(S/(unquote(u.path).lstrip('/') if u.path.startswith('/') else str(Path(route).parent/unquote(u.path)))).resolve()
    if p.is_relative_to(S) and p.relative_to(S).as_posix() in lookup:occur.setdefault(lookup[p.relative_to(S).as_posix()],set()).add(route)
for asset,r in allrows.items():assert occur[asset]=={r.get('owner_route',r.get('page'))},(asset,occur[asset])
gallery=BeautifulSoup((S/'art.html').read_text(encoding='utf-8'),'html.parser');byroute={}
for route in sorted({r['page'] for r in new}):
 p=S/route;raw=p.read_text(encoding='utf-8');dom=BeautifulSoup(raw,'html.parser');inv=Inventory();inv.feed(raw);images=[];resources=[];orig=[]
 for img in dom.find_all('img'):
  a=img.find_parent('a');context=img.find_parent(['figure','section','article']);entry={'src':img.get('src'),'srcset':img.get('srcset'),'alt':img.get('alt'),'anchor':a.get('href') if a else None,'context_id':context.get('id') if context else None,'context_class':context.get('class') if context else None}
  if a and 'data-art-study-supporting' in a.attrs:
   asset=((S/route).parent/a['href']).resolve().relative_to(S).as_posix();r=allrows[asset];owner=a.find_parent(lambda n:n.name in ['section','figure'] and n.get('id'));assert owner
   orig.append({'kind':'original','asset':asset,'sha256':h(S/asset),'owner_route':route,'owner_section':owner['id'],'original_id':str(Path(asset).with_suffix('')).replace('\\','/'),'depicts_christ':r.get('depicts_christ',r.get('christ'))});entry['classification']='owned-original-variant'
  elif a and 'fc-art-study-hero' in a.get('class',[]):entry['classification']='excluded-gallery-reference'
  else:
   assert img.find_parent(class_='fc-resource-card'),entry
   entry['classification']='official-resource-preview';resources.append(entry)
  images.append(entry)
 assert len(orig)==10 and len({x['asset'] for x in orig})==10
 hero=dom.select_one('a.fc-art-study-hero');target=dom.select_one('.fc-page-intro').find('a',href=re.compile(r'^\.\./art\.html#'))['href'];assert target in inv.placement_links[hero['href']][0]
 g=gallery.find(id=urlsplit(target).fragment);assert g
 ref=((S/route).parent/hero['href']).resolve().relative_to(S).as_posix();assert g.img['data-full-src']==ref,(ref,g.img)
 byroute[route]={'html_sha256':h(p),'originals':orig,'original_count':10,'christ_count':sum(r['depicts_christ'] for r in orig),'image_elements':images,'source_elements':[dict(x.attrs) for x in dom.find_all('source')],'inline_style_images':[dict(x.attrs) for x in dom.find_all(style=re.compile('url\\('))],'scripts':[x.get('src') for x in dom.find_all('script')],'resource_exclusions':resources,'reference_target':target,'reference_asset':ref,'gallery_owner':{'route':'art.html','html_sha256':h(S/'art.html'),'section':g['id'],'full_asset':g.img['data-full-src'],'full_sha256':h(S/ref),'thumbnail':g.img['src'],'thumbnail_sha256':h(S/g.img['src']),'caption':g.select_one('.caption').get_text(' ',strip=True),'alt':g.img['alt']}}
snap=json.loads((P/'fermi/lineage-assets-final3-snapshot.json').read_text());prior=json.loads((P/'fermi/lineage-assets-current.json').read_text());assert snap==prior
for a in snap:assert h(S/a['path'])==a['file_sha256'],a['path']
fd=json.loads((P/'fermi/lineage-final3-scan.json').read_text());assert h(P/'fermi/lineage-final3-scan.json')=='e3718925f9806a3c06a2c5fee44bd829c83ce2b93ecf0ad3566aff6bcb626007'
assert fd['asset_count']==len(snap)
for r in fd['targets']:
 assert h(Path(r['path']))==r['expected_sha256'];assert not r['exact_aliases'] and not r['phash_candidates'] and not r['sift_candidates']
# Explicit new-to-new/retained cross-target retrieval, independent of preintegration corpus.
sift=cv2.SIFT_create(nfeatures=500);features={};phashes={};decoded={}
for asset in allrows:
 im=Image.open(S/asset).convert('RGB');decoded[asset]=hashlib.sha256(im.tobytes()).hexdigest();dct=cv2.dct(np.asarray(im.resize((32,32)).convert('L'),dtype=np.float32))[:8,:8].flatten();phashes[asset]=sum(int(v)<<i for i,v in enumerate(dct>np.median(dct[1:])))
 a=np.asarray(im.convert('L'));a=cv2.resize(a,None,fx=min(1,640/max(a.shape)),fy=min(1,640/max(a.shape)));k,d=sift.detectAndCompute(a,None);features[asset]=(np.float32([x.pt for x in k]),d)
bf=cv2.BFMatcher();pairs=[]
for a,b in combinations(allrows,2):
 assert decoded[a]!=decoded[b]
 ka,da=features[a];kb,db=features[b];good=[m for m,n in bf.knnMatch(da,db,k=2) if m.distance<.7*n.distance];inliers=0
 if len(good)>=10:
  H,mask=cv2.findHomography(np.float32([ka[m.queryIdx] for m in good]),np.float32([kb[m.trainIdx] for m in good]),cv2.RANSAC,3);inliers=int(mask.sum()) if mask is not None else 0
 distance=(phashes[a]^phashes[b]).bit_count()
 if distance<=10 or inliers>=10 and inliers/len(good)>=.55:pairs.append({'a':a,'b':b,'phash_distance':distance,'sift_matches':len(good),'sift_inliers':inliers})
for group,rows in [('new',new),('retained',ret)]:
 for start in range(0,15,5):
  sheet=Image.new('RGB',(1500,650),'white')
  for i,r in enumerate(rows[start:start+5]):
   tile=ImageOps.contain(Image.open(S/r['asset']).convert('RGB'),(490,295));x=(i%3)*500;y=(i//3)*325;sheet.paste(tile,(x,y+25));ImageDraw.Draw(sheet).text((x+3,y+3),r.get('key',Path(r['asset']).stem),fill='black')
  sheet.save(W/f'{group}-{start//5+1}.jpg')
result={'reviewer':'Newton','status':'TECHNICAL_RECHECK_COMPLETE_VISUAL_ADJUDICATION_PENDING','pages':byroute,'lineage':lineage,'canonical_routes':routes,'canonical_route_hashes':hashes,'ownership_occurrences':{k:sorted(v) for k,v in occur.items()},'corpus':{'rehashed_assets':len(snap),'final3_snapshot_matches_prior27_exact':True,'final3_sha256':h(P/'fermi/lineage-final3-scan.json'),'snapshot_sha256':h(P/'fermi/lineage-assets-final3-snapshot.json')},'cross_target_pair_count':435,'cross_target_candidates':pairs}
(W/'inventory-recheck.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pages':{k:[v['original_count'],v['christ_count'],len(v['resource_exclusions'])] for k,v in byroute.items()},'corpus':result['corpus'],'pairs':pairs},indent=2))
