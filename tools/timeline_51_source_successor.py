"""Exact inverse of the proposed 51-event source changes for historical checks.

This reconstruction is not a current prose, artwork, or release review. The
current source still needs its own content, index, and browser acceptance.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/reviews/timeline-51-source-successor.json'
MANIFEST_SHA='cd56a72331d00f7cc91ff6fe79e920a4d4b380a5e8a174d5ada0d15ff351e3ab'
FILES={'pioneers.html', 'timeline-images.js', 'timelines/life-of-christ-journey-map.html', 'jesus-christ/mortal-ministry.html', 'timelines/latter-day-saint-church-history-timeline.html', 'church-history.html', 'jesus-christ/restoration-and-today.html', 'timelines/willie-and-martin-handcart-map.html'}
AFTER={'church-history.html': '3b82d70f453983aa9bbd17dfe604a34f8dade8d1559f128a31de146c171eb6a3', 'jesus-christ/mortal-ministry.html': '119fc0150bb5cfd90a3be1b68350ad515efed702144e409d05120a075f8ef892', 'jesus-christ/restoration-and-today.html': '8e61672ff83cfefe04652e7f71456d1f5b58a35e85b04e1d1e933d9a534942cf', 'pioneers.html': 'ebd9444e89b0acff74bf0b761460a42c30f04a149ff8d9de9ce49f127188b3aa', 'timeline-images.js': '09b1a9b957fbe3a920dc9629c8ae1f9569c8e8b9fcfceee27d2564663e6ec9bb', 'timelines/life-of-christ-journey-map.html': 'a7e572937527036e3ff4f4b446acac70e838f7b6dbc7ecee8c200e52cefbf988', 'timelines/willie-and-martin-handcart-map.html': 'b4f4e14bcf0a28655620f24015ca063bfcacc1ac7fe788bb10c21e0226a9adbc', 'timelines/latter-day-saint-church-history-timeline.html': '31d69df1046ec884b109a215d9dd5627921979947874f825b17714f02a000932'}

def sha(data): return hashlib.sha256(data).hexdigest()

def mapping(root=ROOT):
    raw=(root/MANIFEST).read_bytes()
    if sha(raw)!=MANIFEST_SHA: raise ValueError('Unreviewed timeline destination successor manifest')
    data=json.loads(raw)
    if data.get('schema')!=1 or set(data.get('files',{}))!=FILES: raise ValueError('Invalid timeline destination successor scope')
    if any(data['files'][name].get('after_sha256')!=AFTER[name] for name in FILES): raise ValueError('Changed timeline destination subject')
    return data['files']

def restore(name,data,root=ROOT):
    if name not in FILES: return data
    item=mapping(root)[name]
    if sha(data)!=item['after_sha256']: raise ValueError('Unreviewed timeline destination source: '+name)
    start=item['offset']; current=base64.b64decode(item['current_b64'],validate=True); previous=base64.b64decode(item['previous_b64'],validate=True)
    if data[start:start+len(current)]!=current: raise ValueError('Timeline destination inverse mismatch: '+name)
    result=data[:start]+previous+data[start+len(current):]
    if sha(result)!=item['before_sha256']: raise ValueError('Timeline destination predecessor mismatch: '+name)
    return result

def project_exact(name,data,root=ROOT):
    """Only reconstruct an exact later source; older sources stay untouched."""
    if name in AFTER and sha(data)==AFTER[name]:return restore(name,data,root)
    return data

def advance_exact(name,data,root=ROOT):
    """Advance an exact predecessor to the exact current source only."""
    if name not in FILES:return data
    item=mapping(root)[name]
    if sha(data)!=item['before_sha256']:return data
    start=item['offset'];previous=base64.b64decode(item['previous_b64'],validate=True);current=base64.b64decode(item['current_b64'],validate=True)
    if data[start:start+len(previous)]!=previous:raise ValueError('Timeline destination forward mismatch: '+name)
    result=data[:start]+current+data[start+len(previous):]
    if sha(result)!=item['after_sha256']:raise ValueError('Timeline destination successor mismatch: '+name)
    return result
