"""Exact World companion/order successor; reconstruction is not approval."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGE='timelines/world-and-scripture-timeline.html'
BEFORE='f2cf7bb2cd4c007ead8d883b55a912749637d13a40cddbc24448a0910f208be0'
ASSET='assets/timeline/book-of-mormon-internal-map.png'
ASSET_SHA='e6a0339eb745127166d468bb5f24b771aec8f4d4221ebceb80b04e380dd11ce7'
MANIFEST='docs/world-companion-successor/manifest.json'
REVIEWS='docs/world-companion-successor/reviews.json'
SOURCE_SHA='bb45d06812b0798951b5a54f5552752e6d43760501a7d64e0ec7fc7899d73626'  # Integrator pins exact candidate spans; this is not review approval.
APPROVED_REVIEWS='d97ed42b4f332ee3dcf472db76db9cbcbd42bfa5a35477785d2a80497c8bb94a'  # Only after actual finished review.
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def require(ok,message):
    if not ok:raise ValueError(message)
def local(root,name):
    root=Path(root).resolve();p=(root/name).resolve()
    require(p.is_relative_to(root) and p.is_file(),'Missing/outside successor evidence: '+name)
    return p
def mapping(root=ROOT):
    require(SOURCE_SHA is not None,'World successor candidate PENDING')
    row=json.loads(local(root,MANIFEST).read_bytes())
    require(canonical(row)==SOURCE_SHA,'Changed successor manifest')
    require(row.get('schema')==1 and row.get('page')==PAGE and row.get('before_sha256')==BEFORE,'Wrong successor predecessor/route')
    require(row.get('asset')==ASSET and row.get('asset_sha256')==ASSET_SHA,'Wrong successor map asset')
    require(isinstance(row.get('after_sha256'),str) and len(row['after_sha256'])==64 and row['after_sha256']!=BEFORE,'Invalid successor digest')
    spans=row.get('spans');require(isinstance(spans,list) and bool(spans),'Missing successor spans')
    end=-1
    for span in spans:
        a,b=span['start'],span['end']
        require(type(a) is int and type(b) is int and 0<=a<=b and a>end,'Overlapping/duplicate successor spans')
        old=base64.b64decode(span['previous_b64'],validate=True);new=base64.b64decode(span['current_b64'],validate=True)
        require(len(new)==b-a and old!=new,'Invalid successor span bytes');end=b
    return row
def restore(name,raw,root=ROOT):
    if name!=PAGE or SOURCE_SHA is None:return raw
    row=mapping(root)
    if sha(raw)!=row['after_sha256']:return raw
    result=raw
    for span in reversed(row['spans']):
        a,b=span['start'],span['end'];new=base64.b64decode(span['current_b64']);old=base64.b64decode(span['previous_b64'])
        require(b<=len(raw) and raw[a:b]==new,'Successor inverse byte mismatch')
        result=result[:a]+old+result[b:]
    require(sha(result)==BEFORE,'Successor inverse predecessor mismatch')
    return result
def advance(name,raw,root=ROOT):
    if name!=PAGE or SOURCE_SHA is None:return raw
    row=mapping(root)
    if sha(raw)!=BEFORE:return raw
    replacements=[];delta=0
    for span in row['spans']:
        old=base64.b64decode(span['previous_b64']);new=base64.b64decode(span['current_b64']);a=span['start']+delta
        require(raw[a:a+len(old)]==old,'Successor forward byte mismatch')
        replacements.append((a,a+len(old),new));delta+=len(old)-len(new)
    result=raw
    for a,b,new in reversed(replacements):result=result[:a]+new+result[b:]
    require(sha(result)==row['after_sha256'],'Successor forward digest mismatch')
    return result
def check(root=ROOT):
    from settings_successor import restore as restore_settings
    from timeline_world_controls_successor import restore as restore_world_controls, AFTER as WORLD_AFTER
    from timeline_world_mobile_successor import AFTER as MOBILE_AFTER
    row=mapping(root);raw=local(root,PAGE).read_bytes()
    if sha(raw) in (WORLD_AFTER, MOBILE_AFTER):raw=restore_world_controls(raw,root)
    raw=restore_settings(PAGE,raw,root)
    require(sha(raw)==row['after_sha256'],'Changed successor page')
    require(sha(restore(PAGE,raw,root))==BEFORE,'Successor predecessor mismatch')
    require(sha(local(root,ASSET).read_bytes())==ASSET_SHA,'Changed successor map asset')
    require(APPROVED_REVIEWS is not None,'World successor finished review PENDING')
    record=json.loads(local(root,REVIEWS).read_bytes())
    require(canonical(record)==APPROVED_REVIEWS,'Changed successor reviews')
    require(record.get('source_sha256')==SOURCE_SHA and record.get('page_sha256')==row['after_sha256'],'Wrong successor review binding')
    reviews=record.get('reviews',[])
    require(len(reviews)==3 and {r.get('reviewer') for r in reviews}=={'Albert','Fermi','Newton'},'Missing/duplicate successor reviewers')
    for review in reviews:
        require(review.get('decision')=='CONCUR' and review.get('finished_pixels') is True and review.get('finished_behavior') is True,'Unfinished successor review')
        require(review.get('page_sha256')==row['after_sha256'],'Wrong reviewer page')
        item=review['evidence'];require(sha(local(root,item['path']).read_bytes())==item['sha256'],'Changed successor review evidence')
    return {'status':'WORLD_SUCCESSOR_EVIDENCE_PASS','page_sha256':row['after_sha256']}
