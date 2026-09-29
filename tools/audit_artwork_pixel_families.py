"""Read-only visual lineage candidates; similarity is not an ownership verdict."""
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,re,cv2,numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/artwork-uniqueness-audit-20260929'
EXT={'.png','.jpg','.jpeg','.webp','.avif'}
files=sorted(p for p in ROOT.rglob('*') if p.suffix.lower() in EXT and not set(p.relative_to(ROOT).parts)&{'.git','work','node_modules','outputs','tools','tests','.venv'})
def read(p):
 try:
  with Image.open(p) as im: a=ImageOps.exif_transpose(im).convert('RGB')
  if min(a.size)<120:return None
  small=np.asarray(a.resize((32,32)).convert('L'),dtype=np.float32);d=cv2.dct(small)[:8,:8].flatten();bits=d>np.median(d[1:]);h=sum(int(v)<<i for i,v in enumerate(bits))
  return dict(path=p.relative_to(ROOT).as_posix(),width=a.width,height=a.height,file_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),decoded_sha256=hashlib.sha256(a.tobytes()).hexdigest(),phash=f'{h:016x}')
 except Exception as e:return {'path':str(p),'error':str(e)}
with ThreadPoolExecutor(max_workers=8) as ex: records=[r for r in ex.map(read,files) if r]
assets=[r for r in records if 'error' not in r];print('decoded',len(assets),flush=True)
parent=list(range(len(assets)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def join(i,j):parent[find(j)]=find(i)
pairs=[];exact=defaultdict(list)
for i,a in enumerate(assets):exact[a['decoded_sha256']].append(i)
for group in exact.values():
 for i in group[1:]:join(group[0],i)
for i,a in enumerate(assets):
 for j in range(i):
  b=assets[j];dist=(int(a['phash'],16)^int(b['phash'],16)).bit_count()
  if dist<=10:
   pairs.append(dict(a=b['path'],b=a['path'],method='phash64',distance=dist,confidence='candidate'))
   if dist<=3 and abs(a['width']/a['height']-b['width']/b['height'])<.025:join(i,j)
groups=defaultdict(list)
for i in range(len(assets)):groups[find(i)].append(i)
reps=[max(g,key=lambda i:assets[i]['width']*assets[i]['height']) for g in groups.values()]
print('representatives',len(reps),'phash pairs',len(pairs),flush=True)
sift=cv2.SIFT_create(nfeatures=240);features=[];kp=[];valid=[]
for i in reps:
 image=cv2.imread(str(ROOT/assets[i]['path']),cv2.IMREAD_GRAYSCALE)
 if image is None:continue
 scale=min(1,640/max(image.shape));image=cv2.resize(image,None,fx=scale,fy=scale)
 k,d=sift.detectAndCompute(image,None)
 if d is not None and len(d)>=12:valid.append(i);features.append(d);kp.append(np.float32([x.pt for x in k]))
lengths=[len(d) for d in features];labels=np.repeat(np.arange(len(features)),lengths);matrix=np.vstack(features).astype(np.float32)
index=cv2.FlannBasedMatcher(dict(algorithm=1,trees=4),dict(checks=32));index.add([matrix]);index.train();candidates=set()
for idx,d in enumerate(features):
 votes=Counter()
 for matches in index.knnMatch(d,k=8):
  foreign=[m for m in matches if labels[m.trainIdx]!=idx]
  if len(foreign)>1 and foreign[0].distance<.7*foreign[1].distance:votes[int(labels[foreign[0].trainIdx])]+=1
 for other,count in votes.items():
  if count>=10:candidates.add(tuple(sorted((idx,other))))
print('feature candidates',len(candidates),flush=True)
matcher=cv2.BFMatcher()
for i,j in sorted(candidates):
 matches=matcher.knnMatch(features[i],features[j],k=2);good=[m for m,n in matches if m.distance<.7*n.distance]
 if len(good)<10:continue
 src=np.float32([kp[i][m.queryIdx] for m in good]);dst=np.float32([kp[j][m.trainIdx] for m in good]);H,mask=cv2.findHomography(src,dst,cv2.RANSAC,3)
 if mask is None:continue
 count=int(mask.sum());ratio=count/len(good)
 if count>=10 and ratio>=.55:pairs.append(dict(a=assets[valid[i]]['path'],b=assets[valid[j]]['path'],method='SIFT_homography',inliers=count,matches=len(good),inlier_ratio=round(ratio,3),confidence='strong_visual_lineage_candidate'))
report=dict(status='CANDIDATES_REQUIRE_OCCURRENCE_AND_VISUAL_REVIEW',method='SHA/decoded RGB,64-bit DCT pHash; SIFT descriptor retrieval and RANSAC homography crop detection',assets=assets,pairs=pairs,exact_groups=[[assets[i]['path'] for i in g] for g in exact.values() if len(g)>1],source_family_groups=[[assets[i]['path'] for i in g] for g in groups.values() if len(g)>1],errors=[r for r in records if 'error'in r])
(OUT/'pixel-families.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('saved',len(pairs),'pairs',flush=True)
