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
APPROVED_REVIEWS='359a2e86c71c6b3ef8d5c3cdfbc619d87ba7963169c668af9eac4bb578073efe'  # Canonical hash of the completed reviews.json: J007 registration (pixels false), Merlin rendered evidence, Jeff J009 rendered CONCUR; gate change reviewed in J008.
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
RENDERED_MISSING='Missionary close successor rendered review MISSING'
def _rendered(root,record,after):
    """A002 split: rendered evidence collection and the independent rendered
    review are separate scopes from Jeff's registration/source review.
    Returns False only when a slot is absent or still unfilled; anything
    present but wrong-scope, wrong-actor, unfinished, or tampered raises."""
    ev=record.get('rendered_evidence')
    if not isinstance(ev,dict) or ev.get('status')!='COLLECTED' or not ev.get('captures'):return False
    require(ev.get('collected_by')=='Merlin','Wrong successor rendered evidence collector')
    require(ev.get('page_sha256')==after,'Wrong successor rendered evidence page')
    head=ev.get('served_git_head');require(isinstance(head,str) and len(head)==40,'Missing successor rendered evidence served head')
    require(ev.get('details_js_sha256')==sha(local(root,'missionary-details.js').read_bytes()),'Successor rendered evidence script mismatch')
    caps=ev['captures'];viewports={c.get('viewport') for c in caps}
    require('desktop' in viewports and 'phone' in viewports,'Successor rendered evidence must cover desktop and phone viewports')
    hashes=[]
    for cap in caps:
        raw=local(root,cap['path']).read_bytes()
        if cap['path'].endswith('.b64'):
            try:raw=base64.b64decode(raw,validate=False)
            except Exception:raise ValueError('Invalid successor rendered evidence encoding')
        require(sha(raw)==cap['sha256'],'Changed successor rendered evidence')
        hashes.append(cap['sha256'])
    rv=record.get('rendered_review')
    if not isinstance(rv,dict) or rv.get('status')!='FINISHED':return False
    require(rv.get('reviewer') in ('Jeff','Albert'),'Wrong successor rendered reviewer')
    require(rv.get('scope')=='rendered','Wrong successor rendered review scope')
    require(rv.get('decision')=='CONCUR','Unfinished successor rendered review')
    require(rv.get('finished_pixels') is True and rv.get('finished_behavior') is True,'Unfinished successor rendered review')
    require(rv.get('page_sha256')==after,'Wrong successor rendered reviewer page')
    require(rv.get('capture_sha256')==hashes,'Successor rendered review not bound to rendered evidence captures')
    item=rv['evidence'];require(sha(local(root,item['path']).read_bytes())==item['sha256'],'Changed successor rendered review evidence')
    return True
def check(root=ROOT):
    row=mapping(root);raw=local(root,PAGE).read_bytes()
    require(sha(raw)==row['after_sha256'],'Changed successor page')
    require(sha(restore(PAGE,raw,root))==BEFORE,'Successor predecessor mismatch')
    record=json.loads(local(root,REVIEWS).read_bytes())
    if APPROVED_REVIEWS is not None:require(canonical(record)==APPROVED_REVIEWS,'Changed successor reviews')
    require(record.get('source_sha256')==SOURCE_SHA and record.get('page_sha256')==row['after_sha256'],'Wrong successor review binding')
    require(record.get('required_reviewers')==['Jeff'],'Wrong successor required reviewers')
    reg=record.get('registration_review')
    require(isinstance(reg,dict),'Missing successor registration review')
    require(reg.get('reviewer')=='Jeff','Wrong successor registration reviewer')
    require(reg.get('scope')=='registration-source','Wrong successor registration review scope')
    require(reg.get('decision')=='CONCUR','Unfinished successor registration review')
    require(reg.get('finished_pixels') is False,'Successor registration review must record finished_pixels=false (A002)')
    require(reg.get('finished_behavior') is True,'Unfinished successor registration behavior review')
    require(reg.get('page_sha256')==row['after_sha256'],'Wrong successor registration reviewer page')
    item=reg['evidence'];require(sha(local(root,item['path']).read_bytes())==item['sha256'],'Changed successor registration review evidence')
    require(_rendered(root,record,row['after_sha256']),RENDERED_MISSING)
    require(APPROVED_REVIEWS is not None,'Missionary close successor finished review PENDING')
    return {'status':'MISSIONARY_CLOSE_SUCCESSOR_EVIDENCE_PASS','page_sha256':row['after_sha256']}
