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
MANIFEST_SHA='07dfcae66ff826d553c306f75e9a12a93c04fc1ecb6334a8cde8f2434962ca5a'
FILES={'church-history.html','pioneers.html','jesus-christ/mortal-ministry.html','jesus-christ/restoration-and-today.html','timeline-images.js'}

def sha(data): return hashlib.sha256(data).hexdigest()

def mapping(root=ROOT):
    raw=(root/MANIFEST).read_bytes()
    if sha(raw)!=MANIFEST_SHA: raise ValueError('Unreviewed timeline destination successor manifest')
    data=json.loads(raw)
    if data.get('schema')!=1 or set(data.get('files',{}))!=FILES: raise ValueError('Invalid timeline destination successor scope')
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
