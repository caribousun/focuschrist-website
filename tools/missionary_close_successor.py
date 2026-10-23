"""Exact Mission Close pill successor; reconstruction is not approval."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGE='missionary.html'
BEFORE='028f7bc23aa9c7a21e8cc2def40c429ba5ea628880347653292974e8fe7caa31'
AFTER='e5696e60b60faef5f456647ff2a153b939871acb895a6671d3d95a718d2ad55a'
MANIFEST='docs/missionary-close-successor/manifest.json'
REVIEWS='docs/missionary-close-successor/reviews.json'
SOURCE_SHA='5def8841bee12decbe14be551c896794493dd944d8b15cf1fbb9d7f585400b41'  # Integrator pins exact candidate spans; this is not review approval.
APPROVED_REVIEWS=None  # Only after actual finished Jeff review.
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def require(ok,message):
    if not ok:raise ValueError(message)
def local(root,name):
    root=Path(root).resolve();p=(root/name).resolve()
    require(p.is_relative_to(root) and p.is_file(),'Missing/outside successor evidence: '+name)
    return p
def mapping(root=ROOT):
    require(SOURCE_SHA is not None,'Missionary close successor candidate PENDING')
    row=json.loads(local(root,MANIFEST).read_bytes())
    require(canonical(row)==SOURCE_SHA,'Changed successor manifest')
    require(row.get('schema')==1 and row.get('page')==PAGE,'Wrong successor schema/route')
    require(row.get('before_sha256')==BEFORE,'Wrong successor predecessor')
    require(row.get('after_sha256')==AFTER,'Wrong successor candidate digest')
    spans=row.get('spans');require(isinstance(spans,list) and bool(spans),'Missing successor spans')
    end=-1
    for span in spans:
        a,b=span['start'],span['end']
        require(type(a) is int and type(b) is int and 0<=a<=b and a>end,'Overlapping/duplicate successor spans')
        old=base64.b64decode(span['previous_b64'],validate=True);new=base64.b64decode(span['current_b64'],validate=True)
        require(len(new)==b-a and old==b'' and new!=old,'Invalid successor span bytes');end=b
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
    row=mapping(root);raw=local(root,PAGE).read_bytes()
    require(sha(raw)==row['after_sha256'],'Changed successor page')
    require(sha(restore(PAGE,raw,root))==BEFORE,'Successor predecessor mismatch')
    require(APPROVED_REVIEWS is not None,'Missionary close successor finished review PENDING')
    record=json.loads(local(root,REVIEWS).read_bytes())
    require(canonical(record)==APPROVED_REVIEWS,'Changed successor reviews')
    require(record.get('source_sha256')==SOURCE_SHA and record.get('page_sha256')==row['after_sha256'],'Wrong successor review binding')
    require(record.get('required_reviewers')==['Jeff'],'Wrong successor required reviewers')
    reviews=record.get('reviews',[])
    require(len(reviews)==1 and {r.get('reviewer') for r in reviews}=={'Jeff'},'Missing/duplicate successor reviewers')
    for review in reviews:
        require(review.get('decision')=='CONCUR' and review.get('finished_pixels') is True and review.get('finished_behavior') is True,'Unfinished successor review')
        require(review.get('page_sha256')==row['after_sha256'],'Wrong reviewer page')
        item=review['evidence'];require(sha(local(root,item['path']).read_bytes())==item['sha256'],'Changed successor review evidence')
    return {'status':'MISSIONARY_CLOSE_SUCCESSOR_EVIDENCE_PASS','page_sha256':row['after_sha256']}
