"""Reconstruct the prior search index from the exact new event-section output.

This is a mechanical comparison, not an independent current review or release.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/reviews/timeline-51-search-delta.json'
MANIFEST_SHA='1d6101c7a3ed5df4ca8aad4a252c1cd4ed3795f0995ec7f4a5fadc82277d25ab'
BEFORE='abcd13069b734ca5f25ecc003abef56717093b73c31e336ae84bd3d647ffabf1'
AFTER='cb138be2294b89e4f22bcb98fa074b85d9d3abe2dc93a8114a66e56590b14c60'

def sha(b):return hashlib.sha256(b).hexdigest()
def record_sha(r):return sha(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def manifest(root=ROOT):
    raw=(Path(root)/MANIFEST).read_bytes()
    if sha(raw)!=MANIFEST_SHA:raise ValueError('Changed event search delta manifest')
    m=json.loads(raw)
    if m['schema']!=1 or m['previous_sha256']!=BEFORE or m['current_sha256']!=AFTER or len(m['changes'])!=56:raise ValueError('Invalid event search delta scope')
    return m

def restore(raw,root=ROOT):
    root=Path(root);m=manifest(root)
    if sha(raw)!=AFTER:raise ValueError('Unreviewed event search index')
    for name,expected in m['source_sha256'].items():
        if sha((root/name).read_bytes())!=expected:raise ValueError('Changed event source: '+name)
    data=json.loads(raw);records=data['records'];urls=[r['url'] for r in records]
    if len(urls)!=len(set(urls)) or not set(m['changes'])<=set(urls):raise ValueError('Invalid event search destinations')
    out=[]
    for r in records:
        change=m['changes'].get(r['url'])
        if change is None:out.append(r);continue
        if record_sha(r)!=change['current_record_sha256']:raise ValueError('Changed event search record')
        previous=change['previous']
        if previous is not None:
            if previous['url']!=r['url'] or set(previous)!=set(r):raise ValueError('Invalid predecessor record')
            out.append({key:previous[key] for key in r})
    previous=dict(data,records=out)
    result=(json.dumps(previous,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    if sha(result)!=BEFORE:raise ValueError('Event search predecessor mismatch')
    return result

def validate_current(root=ROOT):
    import build_site_search
    root=Path(root).resolve()
    if build_site_search.ROOT.resolve()!=root:raise ValueError('Search producer root mismatch')
    raw=(root/'site-search-index.json').read_bytes();previous=restore(raw,root)
    if build_site_search.build()!=json.loads(raw):raise ValueError('Actual search producer mismatch')
    return {'current_sha256':sha(raw),'previous_sha256':sha(previous),'changed_records':56,'scope':'mechanical only; independent current review remains required'}
