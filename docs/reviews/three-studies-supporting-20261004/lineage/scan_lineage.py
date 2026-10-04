from pathlib import Path
import json,hashlib,re,xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps
import cv2,numpy as np
from bs4 import BeautifulSoup
ROOT=Path(r'C:/Users/wyatt/Documents/Codex/2026-10-03/joseph-research-site'); OUT=Path(__file__).parent
OLD=Path(r'C:/Users/wyatt/Documents/Codex/2026-10-04/three-art-studies-enriched-continuation'); PRIOR=OLD.parent/'full-site-enriched-review-continuation'
h=lambda b:hashlib.sha256(b).hexdigest()
ret=json.loads((OLD/'work/fermi/retained15-review.json').read_text()); ledger=json.loads((ROOT/'docs/artwork-uniqueness-audit-20260929/pixel-families.json').read_text()); cache={r['path']:r for r in ledger['assets']}
routes=sorted({urlsplit(e.text).path.lstrip('/') or 'index.html' for e in ET.parse(ROOT/'sitemap.xml').getroot().iter() if e.tag.endswith('loc')})
occ=defaultdict(list); routehash={}
for route in routes:
 raw=(ROOT/route).read_bytes();routehash[route]=h(raw);soup=BeautifulSoup(raw.decode(),'html.parser')
 for tag in soup.find_all(True):
  for attr in ['src','href','poster','data-src','data-full','data-image','srcset']:
   for value in re.split(r'[,\s]+',tag.get(attr,'')):
    p=urlsplit(value)
    if not p.path or p.scheme or p.netloc:continue
    asset=(ROOT/(unquote(p.path).lstrip('/') if p.path.startswith('/') else str(Path(route).parent/unquote(p.path)))).resolve()
    if not asset.is_relative_to(ROOT) or asset.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.avif'}:continue
    context=tag.find_parent(['figure','section'])
    occ[asset.relative_to(ROOT).as_posix()].append({'route':route,'tag':tag.name,'attribute':attr,'section':context.get('id') if context else None,'class':tag.get('class',[])})
targets=[]
for r in ret['rows']:targets.append({'key':r['asset'],'path':str(ROOT/r['asset']),'owner':r['owner_route'],'retained':True,'expected_sha256':r['sha256']})
versions={'GS2':2,'GS3':1,'GS4':2,'GS5':1,'CH1':1,'CH2':2,'CH3':1,'CH4':1,'BS2':1,'BS3':1,'BS4':1,'BS5':1}
for root in [PRIOR,OLD]:
 j=json.loads((root/'work/gary/generated/generation-manifest.json').read_text(encoding='utf-8-sig'))
 for r in j.get('outputs',j.get('entries',[])):
  if versions.get(r['key'])==r.get('version',1):
   p=Path(r['candidate_path']);p=p if p.is_absolute() else root/p
   if not any(t['key']==r['key'] for t in targets):targets.append({'key':r['key'],'path':str(p),'owner':{'GS':'art-study/the-good-shepherd.html','CH':'art-study/suffer-the-little-children.html','BS':'art-study/be-still.html'}[r['key'][:2]],'retained':False,'expected_sha256':r['output_sha256']})
assert len(targets)==27,len(targets)
files=sorted(p for p in ROOT.rglob('*') if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.avif'} and not set(p.relative_to(ROOT).parts)&{'.git','work','node_modules','outputs','tools','tests','.venv'})
def read(p):
 rel=p.relative_to(ROOT).as_posix();sha=h(p.read_bytes());old=cache.get(rel)
 if old and old['file_sha256']==sha:return dict(old,cache_revalidated=True)
 try:
  with Image.open(p) as im:a=ImageOps.exif_transpose(im).convert('RGB')
  d=cv2.dct(np.asarray(a.resize((32,32)).convert('L'),dtype=np.float32))[:8,:8].flatten();bits=d>np.median(d[1:]);ph=sum(int(v)<<i for i,v in enumerate(bits))
  return dict(path=rel,width=a.width,height=a.height,file_sha256=sha,decoded_sha256=h(a.tobytes()),phash=f'{ph:016x}',cache_revalidated=False)
 except Exception as e:return dict(path=rel,error=str(e))
with ThreadPoolExecutor(max_workers=8) as ex:records=list(ex.map(read,files))
assets=[r for r in records if 'error' not in r]; print('assets',len(assets),'cached',sum(r['cache_revalidated'] for r in assets),flush=True)
# Representatives retain aliases; pHash grouping does not adjudicate ownership.
groups=defaultdict(list)
for a in assets:groups[a['decoded_sha256']].append(a)
reps=[max(g,key=lambda a:a['width']*a['height']) for g in groups.values() if max(min(a['width'],a['height']) for a in g)>=120]
sift=cv2.SIFT_create(nfeatures=300)
def feature(p):
 im=cv2.imread(str(p),0)
 if im is None:return None,None
 scale=min(1,640/max(im.shape));im=cv2.resize(im,None,fx=scale,fy=scale);k,d=sift.detectAndCompute(im,None)
 return np.float32([x.pt for x in k]),d
features=[];points=[];valid=[]
for a in reps:
 k,d=feature(ROOT/a['path'])
 if d is not None and len(d)>=12:valid.append(a);features.append(d);points.append(k)
print('features',len(valid),flush=True)
labels=np.repeat(np.arange(len(features)),[len(d) for d in features]);matrix=np.vstack(features).astype(np.float32)
index=cv2.FlannBasedMatcher(dict(algorithm=1,trees=4),dict(checks=64));index.add([matrix]);index.train();bf=cv2.BFMatcher();results=[]
for t in targets:
 p=Path(t['path']);assert h(p.read_bytes())==t['expected_sha256'];im=Image.open(p).convert('RGB');dct=cv2.dct(np.asarray(im.resize((32,32)).convert('L'),dtype=np.float32))[:8,:8].flatten();ph=sum(int(v)<<i for i,v in enumerate(dct>np.median(dct[1:])));decoded=h(im.tobytes());k,d=feature(p)
 votes=Counter()
 for matches in index.knnMatch(d,k=12):
  seen=set()
  for m in matches:
   lab=int(labels[m.trainIdx])
   if lab not in seen and m.distance<180:votes[lab]+=1;seen.add(lab)
 candidates={i for i,n in votes.items() if n>=10};near=[a for a in assets if (int(a['phash'],16)^ph).bit_count()<=10];hits=[]
 for i in candidates:
  good=[m for m,n in bf.knnMatch(d,features[i],k=2) if m.distance<.7*n.distance]
  if len(good)<10:continue
  H,mask=cv2.findHomography(np.float32([k[m.queryIdx] for m in good]),np.float32([points[i][m.trainIdx] for m in good]),cv2.RANSAC,3)
  if mask is not None and int(mask.sum())>=10 and float(mask.sum())/len(good)>=.55:hits.append({'asset':valid[i]['path'],'inliers':int(mask.sum()),'matches':len(good),'ratio':round(float(mask.sum())/len(good),3)})
 exact=[a['path'] for a in assets if a['file_sha256']==t['expected_sha256'] or a['decoded_sha256']==decoded]
 names=set(exact+[a['path'] for a in near]+[a['asset'] for a in hits]);result=dict(t,exact_aliases=exact,phash_candidates=[{'asset':a['path'],'distance':(int(a['phash'],16)^ph).bit_count()} for a in near],sift_candidates=hits,occurrences={n:occ.get(n,[]) for n in sorted(names)});results.append(result);print(t['key'],len(exact),len(near),len(hits),flush=True)
report={'reviewer':'Fermi','status':'CANDIDATES_NEED_VISUAL_ADJUDICATION_NOT_STRICT_PASS','canonical_routes':routes,'route_sha256':routehash,'asset_count':len(assets),'revalidated_cached_pixel_records':sum(r['cache_revalidated'] for r in assets),'fresh_decoded_records':sum(not r['cache_revalidated'] for r in assets),'feature_representatives':len(valid),'method':'Fresh all-file SHA; unchanged prior decoded/pHash metrics reused only on exact file SHA match. New/changed pixels decoded. All 27 target originals compared against all assets by exact/decoded equality and pHash, plus fresh SIFT/RANSAC query retrieval across all feature representatives. HTML src/href/srcset/data attributes normalized across130sitemap routes.','targets':results,'errors':[r for r in records if 'error' in r],'limits':['Heuristic crop/alias retrieval is not exhaustive mathematical proof; manual adjudication pending','Source reference resemblance is not automatic duplicate original','Current SITE snapshot only; staged future refs and candidate page freeze need renewed coverage','No strict approval booleans set']}
(OUT/'lineage-candidate-scan.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'lineage-assets-current.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
print('DONE',h((OUT/'lineage-candidate-scan.json').read_bytes()),flush=True)

