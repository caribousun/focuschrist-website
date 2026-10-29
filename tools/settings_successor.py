"""Exact two-page settings/filter successor and finished-review binding."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/settings-successor/manifest.json'
REVIEWS='docs/settings-successor/reviews.json'
SOURCE_SHA='b786e625d7efb888512d0f492e2d1ffbb9916a28b724057cd0dedb40d5fa2793'
BEFORE={'timelines/world-and-scripture-timeline.html': '2aee89b976da080c2c363da3a32967061f93ac6abd0e2f140362b0338d3fe65d', 'timelines/life-of-christ-journey-map.html': 'eea836a5698693a84f76d2e79e153055b8c7d7a198b11141b1df75c1e98d4a62'}
AFTER={'timelines/world-and-scripture-timeline.html': 'a6f0a9fb82e16405a0cf32e25cbd7889ad0a56b5af4e9003fca40bd985ad93fd', 'timelines/life-of-christ-journey-map.html': 'e8e6124f50a19d7cac839ec8b405e33b036284c57b8182d2e7776dc8af90c418'}
APPROVED_REVIEWS='e1274b84484e2108b70b093aeef204230182e4a587ae2a3fc0a912cc19f97308'

def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def require(ok,message):
 if not ok:raise ValueError(message)
def local(root,name):
 root=Path(root).resolve();p=(root/name).resolve()
 require(p.is_relative_to(root) and p.is_file(),'Missing/outside settings evidence: '+name)
 return p
def mapping(root=ROOT):
 data=json.loads(local(root,MANIFEST).read_bytes())
 require(SOURCE_SHA is not None and canonical(data)==SOURCE_SHA,'Changed/unbound settings manifest')
 require(data.get('schema')==1 and set(data.get('files',{}))==set(BEFORE),'Wrong settings route set')
 for name,row in data['files'].items():
  require(row.get('before_sha256')==BEFORE[name],'Wrong settings predecessor')
  require(row.get('after_sha256')==AFTER[name] and AFTER[name]!=BEFORE[name],'Wrong settings candidate digest')
  require(bool(row.get('spans')),'Missing settings spans');end=-1
  for span in row['spans']:
   a,b=span['start'],span['end'];require(type(a) is int and type(b) is int and 0<=a<=b and a>end,'Overlapping/duplicate settings span')
   old=base64.b64decode(span['previous_b64'],validate=True);new=base64.b64decode(span['current_b64'],validate=True)
   require(len(new)==b-a and old!=new,'Wrong settings span bytes');end=b
 return data

def restore(name,raw,root=ROOT):
 if name not in BEFORE or sha(raw)!=AFTER[name]:return raw
 row=mapping(root)['files'][name]
 result=raw
 for s in reversed(row['spans']):
  a,b=s['start'],s['end'];require(raw[a:b]==base64.b64decode(s['current_b64']),'Settings inverse byte mismatch')
  result=result[:a]+base64.b64decode(s['previous_b64'])+result[b:]
 require(sha(result)==BEFORE[name],'Settings predecessor mismatch')
 return result

def advance(name,raw,root=ROOT):
 if name not in BEFORE or sha(raw)!=BEFORE[name]:return raw
 row=mapping(root)['files'][name]
 replacements=[];delta=0
 for s in row['spans']:
  old=base64.b64decode(s['previous_b64']);new=base64.b64decode(s['current_b64']);a=s['start']+delta
  require(raw[a:a+len(old)]==old,'Settings forward byte mismatch');replacements.append((a,a+len(old),new));delta+=len(old)-len(new)
 result=raw
 for a,b,new in reversed(replacements):result=result[:a]+new+result[b:]
 require(sha(result)==row['after_sha256'],'Settings forward digest mismatch')
 return result

def check(root=ROOT):
 data=mapping(root);hashes={}
 for name,row in data['files'].items():
  raw=local(root,name).read_bytes()
  if name=='timelines/world-and-scripture-timeline.html':
   from timeline_world_controls_successor import restore as restore_world_controls, AFTER as WORLD_AFTER
   if sha(raw)==WORLD_AFTER: raw=restore_world_controls(raw,root)
  require(sha(raw)==row['after_sha256'],'Changed settings page: '+name)
  require(sha(restore(name,raw,root))==BEFORE[name],'Settings predecessor mismatch');hashes[name]=sha(raw)
 require(APPROVED_REVIEWS is not None,'Settings finished reviews PENDING')
 record=json.loads(local(root,REVIEWS).read_bytes())
 require(canonical(record)==APPROVED_REVIEWS,'Changed settings reviews')
 require(record.get('source_sha256')==SOURCE_SHA and record.get('page_hashes')==hashes,'Wrong settings review binding')
 reviews=record.get('reviews',[])
 require(len(reviews)==3 and {r.get('reviewer') for r in reviews}=={'Albert','Fermi','Newton'},'Missing/duplicate settings reviewers')
 for review in reviews:
  require(review.get('decision')=='CONCUR' and review.get('finished_pixels') is True and review.get('finished_behavior') is True and review.get('page_hashes')==hashes,'Unfinished/wrong-bound settings review')
  item=review['evidence'];require(sha(local(root,item['path']).read_bytes())==item['sha256'],'Changed settings review evidence')
 return {'status':'SETTINGS_SUCCESSOR_EVIDENCE_PASS','page_hashes':hashes}
