"""Exact historical reconstruction plus a separate fail-closed motion gate.

Predecessor recovery never grants approval for changed behavior. The CLI requires
actual separately authored finished review evidence pinned by the integrator.
"""
import base64
import hashlib
import json
from pathlib import Path
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[1]
MAP='docs/continue-motion/predecessors.json'
REVIEWS='docs/continue-motion/reviews.json'
MAP_SHA='010f24f44c70beaab3dbfe2b92832cdc28adbb79343dcb34c144191154f4312a'
APPROVED_REVIEWS='4dddbcc19a585f93627a3d3bace52419ed588952aaaef2adf6c22f2353cea615'  # Actual finite finished reviews; publication is separate.

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def require(value,message):
    if not value:raise ValueError(message)

@lru_cache(maxsize=2)
def _mapping(raw,expected):
    data=json.loads(raw)
    require(expected is not None and canonical(data)==expected,'Unknown motion predecessor map')
    require(data.get('schema')==1 and data.get('version')=='20261021-continue-motion-1','Wrong motion predecessor schema')
    return data

def mapping(root=ROOT):
    return _mapping((root/MAP).read_bytes(),MAP_SHA)

def reviewed_bytes(path):
    """Preserve exact historical context for enumerated repository consumers."""
    raw=path.read_bytes()
    try:name=path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:return raw
    return restore(name,raw)

def restore(name,data,root=ROOT):
    from missionary_close_successor import restore as restore_close
    from commission_hand_successor import restore as restore_hand
    from world_companion_successor import restore as restore_world
    from settings_successor import restore as restore_settings
    from answer_bank_successor import restore as restore_bank
    from display_gate_successor import restore as restore_gate
    from citation_rendering_successor import restore as restore_citation
    data=restore_world(name,restore_settings(name,restore_close(name,restore_hand(name,restore_bank(name,restore_gate(name,restore_citation(name,data,root),root),root),root),root),root),root)
    record=mapping(root)['files'].get(name)
    if not record or sha(data)!=record['after_sha256']:return data
    restored=data
    last=len(data)
    for span in reversed(record['spans']):
        start,end=span['start'],span['end']
        require(isinstance(start,int) and isinstance(end,int) and 0<=start<=end<=last,'Overlapping motion inverse spans')
        require(data[start:end]==base64.b64decode(span['current_b64'],validate=True),'Motion inverse byte mismatch')
        restored=restored[:start]+base64.b64decode(span['previous_b64'],validate=True)+restored[end:]
        last=start
    require(sha(restored)==record['before_sha256'],'Motion predecessor reconstruction drift')
    return restored

def advance(name,data,root=ROOT):
    """Generate only the exact enumerated successor from an exact predecessor."""
    record=mapping(root)['files'].get(name)
    from missionary_close_successor import advance as advance_close
    from commission_hand_successor import advance as advance_hand
    from world_companion_successor import advance as advance_world
    from settings_successor import advance as advance_settings
    from answer_bank_successor import advance as advance_bank
    from display_gate_successor import advance as advance_gate
    from citation_rendering_successor import advance as advance_citation
    if not record or sha(data)!=record['before_sha256']:return advance_citation(name,advance_gate(name,advance_bank(name,advance_hand(name,advance_close(name,advance_settings(name,advance_world(name,data,root),root),root),root),root),root),root)
    replacements=[];delta=0
    for span in record['spans']:
        previous=base64.b64decode(span['previous_b64'],validate=True)
        current=base64.b64decode(span['current_b64'],validate=True)
        start=span['start']+delta
        require(data[start:start+len(previous)]==previous,'Motion successor byte mismatch')
        replacements.append((start,start+len(previous),current))
        delta+=len(previous)-len(current)
    result=data
    for start,end,current in reversed(replacements):result=result[:start]+current+result[end:]
    require(sha(result)==record['after_sha256'],'Motion successor reconstruction drift')
    return advance_citation(name,advance_gate(name,advance_bank(name,advance_hand(name,advance_close(name,advance_settings(name,advance_world(name,result,root),root),root),root),root),root),root)

def check(root=ROOT):
    from missionary_close_successor import check as check_close,restore as restore_close
    from commission_hand_successor import check as check_hand,restore as restore_hand
    from world_companion_successor import check as check_world,restore as restore_world
    from settings_successor import restore as restore_settings,check as check_settings
    from answer_bank_successor import check as check_bank,restore as restore_bank
    from display_gate_successor import check as check_gate,restore as restore_gate
    from citation_rendering_successor import check as check_citation,restore as restore_citation
    data=mapping(root)
    for name,row in data['files'].items():
        path=(root/name).resolve()
        require(path.is_relative_to(root.resolve()) and path.is_file(),'Missing/outside motion consumer')
        current=restore_world(name,restore_settings(name,restore_close(name,restore_hand(name,restore_bank(name,restore_gate(name,restore_citation(name,path.read_bytes(),root),root),root),root),root),root),root)
        require(sha(current)==row['after_sha256'],'Motion candidate changed: '+name)
        require(sha(restore(name,current,root))==row['before_sha256'],'Motion inverse failed: '+name)
    require(APPROVED_REVIEWS is not None,'Motion finished review PENDING')
    reviews=json.loads((root/REVIEWS).read_text(encoding='utf-8'))
    require(canonical(reviews)==APPROVED_REVIEWS,'Motion review record changed')
    require(reviews.get('map_sha256')==MAP_SHA,'Motion review source mismatch')
    rows=reviews.get('reviews',[])
    require(len(rows)==3 and {r.get('reviewer') for r in rows}=={'Albert','Fermi','Newton'},'Missing actual motion reviewers')
    for row in rows:
        require(row.get('decision')=='CONCUR' and row.get('finished_behavior') is True and row.get('map_sha256')==MAP_SHA,'Motion review incomplete')
        item=row['evidence'];path=(root/item['path']).resolve()
        require(path.is_relative_to(root.resolve()) and path.is_file(),'Missing/outside motion review evidence')
        require(sha(path.read_bytes())==item['sha256'],'Motion review evidence changed')
    check_world(root)
    check_settings(root)
    import shutil,tempfile
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        (view/'missionary.html').write_bytes(restore_hand('missionary.html',(root/'missionary.html').read_bytes(),root))
        shutil.copy2(root/'missionary-details.js',view/'missionary-details.js')
        shutil.copytree(root/'docs/missionary-close-successor',view/'docs/missionary-close-successor')
        check_close(view)
    check_hand(root)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        for bank_name in ('ask.html','pioneers.html','pioneer-experience.js'):
            (view/bank_name).write_bytes(restore_citation(bank_name,(root/bank_name).read_bytes(),root))
        shutil.copytree(root/'docs/answer-bank-successor',view/'docs/answer-bank-successor')
        check_bank(view)
    check_gate(root)
    check_citation(root)
    return {'status':'EXACT_MOTION_EVIDENCE_PASS','files':len(data['files']),'limits':'Technical evidence binding only; does not authenticate reviewers or grant publication approval.'}

if __name__=='__main__':
    try:print(json.dumps(check(),sort_keys=True))
    except (ValueError,KeyError,TypeError,OSError) as error:raise SystemExit('Continue motion gate BLOCKED: '+str(error))
