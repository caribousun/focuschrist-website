"""Exact Adams header CSS producer successor, not release approval.

The previous producer record is immutable and historical. The exact current
record below binds a real independently verified provider run and artifact.
"""
import hashlib
import json
import re
from pathlib import Path

from adams_integration_indices import (AFTER, FRONTEND_INPUTS, GENERATORS,
                                       PRODUCER_MANIFEST, PRODUCER_SHA, canonical, require)

ROOT = Path(__file__).resolve().parents[1]
CSS = 'adams-integration.css'
OLD_CSS_BYTES = 4965
OLD_CSS_SHA = 'd936516926aa47c12c634b11b15278e1590502d0491d9b1f17cd90a0210fdeb1'
NEW_CSS_BYTES = 5292
NEW_CSS_SHA = '3c8a2390e93e94f5d67d3b7a4356f018d78df7ea5c654a3841366549df76d131'
SUCCESSOR_MANIFEST = 'docs/adams-integrated-context/header-fit-index-producer.json'
# Actual generator run 40588766214 / artifact 12773960035, independently reviewed.
# This is source/output evidence, not visual, artwork, or release approval.
APPROVED_RECORD_SHA256 = 'ddba5124f94156f686af422ca9e385bd5ec8d95f05a45192aa1c2455beb2d693'
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')


def read_file(root, name):
    root = Path(root).resolve()
    require(isinstance(name, str) and name and not Path(name).is_absolute()
            and '..' not in Path(name).parts and '\\' not in name, 'unsafe successor path')
    p = root / name
    require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root), 'missing/outside successor file: '+name)
    require(not any(x.is_symlink() for x in [p, *p.parents] if x == root or root in x.parents), 'symlink successor path')
    return p.read_bytes()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def positive_int(value):
    return type(value) is int and value > 0


def check_rows(rows, names, keys):
    require(isinstance(rows,list) and len(rows)==len(names), 'incorrect successor row count')
    require(all(isinstance(row,dict) and set(row)==keys for row in rows), 'incorrect successor row fields')
    require(all(isinstance(row['path'],str) for row in rows), 'invalid successor path')
    require({row['path'] for row in rows} == names, 'missing or duplicate successor paths')
    require(all(positive_int(row['bytes']) and isinstance(row['sha256'],str) and HEX64.fullmatch(row['sha256']) for row in rows), 'invalid successor row data')
    return {row['path']:row for row in rows}


def validate_successor(root=ROOT):
    # No missing/placeholder record can accidentally pass through an old pin.
    require(APPROVED_RECORD_SHA256 is not None, 'actual current index producer evidence PENDING')
    require(HEX64.fullmatch(APPROVED_RECORD_SHA256) is not None, 'invalid successor approval digest')
    root=Path(root).resolve()
    prior=json.loads(read_file(root, PRODUCER_MANIFEST))
    require(canonical(prior)==PRODUCER_SHA, 'historical producer record changed')
    record=json.loads(read_file(root, SUCCESSOR_MANIFEST))
    require(canonical(record)==APPROVED_RECORD_SHA256, 'current producer evidence is not the independently reviewed exact record')
    fields={'schema','repository','event','producer_ref','head_sha','producer_commit','producer_tree','producer_parents','run_id','job_id','artifact_id','job_conclusion','artifact_bytes','artifact_sha256','inputs','outputs','scope','release_claim'}
    require(set(record)==fields and type(record['schema']) is int and record['schema']==1, 'successor schema/fields')
    require(record['repository']=='caribousun/focuschrist-website' and record['event']=='pull_request' and record['producer_ref']=='refs/pull/531/merge', 'unexpected producer repository/event/ref')
    require(record['job_conclusion']=='success' and record['release_claim'] is False and isinstance(record['scope'],str) and record['scope'], 'producer status or scope')
    require(all(isinstance(record[k],str) and HEX40.fullmatch(record[k]) for k in ('head_sha','producer_commit','producer_tree')), 'invalid producer git identity')
    parents=record['producer_parents']
    require(isinstance(parents,list) and len(parents)==2 and len(set(parents))==2 and all(isinstance(p,str) and HEX40.fullmatch(p) for p in parents), 'invalid merge parents')
    require(parents[1]==record['head_sha'], 'producer merge is not tied to reported PR head')
    require(all(positive_int(record[k]) for k in ('run_id','job_id','artifact_id','artifact_bytes')), 'invalid provider identity/size')
    require(isinstance(record['artifact_sha256'],str) and HEX64.fullmatch(record['artifact_sha256']), 'invalid artifact hash')
    require(all(record[k]!=prior[k] for k in ('run_id','job_id','artifact_id','producer_commit','producer_tree')), 'old producer cannot be relabeled current')
    names=set(FRONTEND_INPUTS)|set(GENERATORS)|{'sitemap.xml'}
    keys={'path','bytes','sha256','git_blob_sha1'}
    old=check_rows(prior['inputs'],names,keys)
    current=check_rows(record['inputs'],names,keys)
    require(all(current[name]==old[name] for name in names-{CSS}), 'non-CSS producer input changed; separate successor required')
    css=read_file(root,CSS)
    require(len(css)==NEW_CSS_BYTES and digest(css)==NEW_CSS_SHA, 'unknown current CSS')
    require(len(css)>OLD_CSS_BYTES and digest(css[:OLD_CSS_BYTES])==OLD_CSS_SHA, 'historical CSS prefix changed')
    require(old[CSS]['bytes']==OLD_CSS_BYTES and old[CSS]['sha256']==OLD_CSS_SHA, 'historical CSS producer pin changed')
    for name,row in current.items():
        raw=read_file(root,name)
        require(len(raw)==row['bytes'] and digest(raw)==row['sha256'] and git_blob(raw)==row['git_blob_sha1'], 'current producer input drift: '+name)
    outputs=check_rows(record['outputs'],set(AFTER)-{'timeline.html'},{'path','bytes','sha256'})
    prior_outputs=check_rows(prior['outputs'],set(outputs),{'path','bytes','sha256'})
    for name,row in outputs.items():
        raw=read_file(root,name)
        require(row==prior_outputs[name] and len(raw)==row['bytes'] and digest(raw)==row['sha256']==AFTER[name], 'produced index differs; separately reviewed successor required: '+name)
    return record
