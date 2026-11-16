"""Exact three-row Watch index inverse, never current review/release approval.

Call only after checking actual current generator output. Current Watch source
continuity is also checked; other index records and fields cannot be normalized.
The immutable original records are preserved in the projection manifest.
"""
import hashlib
import json
from pathlib import Path
from timeline_search_index_successor import source
ROOT=Path(__file__).resolve().parents[1]
BEFORE='cb138be2294b89e4f22bcb98fa074b85d9d3abe2dc93a8114a66e56590b14c60'
AFTER='b9b8a71893d3389ab9f12ed70c260e410d8fce3a74cbd85c6ddc180a9be7fc3a'
MANIFEST='docs/qa-watch-search-projection.json'
MANIFEST_SHA='564d1a5ef1a502061ec9f7e31c9c601192ef3382dff9b9cb28a2313ae9cec3f3'
CHANGED={'/watch.html','/watch.html#latest-shorts','/watch.html#latest-shorts-title'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def restore(raw,root=ROOT):
    """Return exact historical bytes; reject any unrecognized index or source."""
    from watch_current_source_qa import check_sources
    check_sources(root)
    assert sha(raw)==AFTER,'Unknown current Watch search index'
    manifest=source(root,MANIFEST)
    assert sha(manifest)==MANIFEST_SHA,'Changed Watch projection manifest'
    m=json.loads(manifest)
    assert m['schema']==1 and m['kind']=='watch_search_historical_projection_not_release'
    assert m['previous_sha256']==BEFORE and m['current_sha256']==AFTER
    assert set(m['previous_records'])==CHANGED,'Wrong Watch projection scope'
    data=json.loads(raw);urls=[r['url'] for r in data['records']]
    assert len(urls)==len(set(urls)) and CHANGED<=set(urls),'Missing or duplicate Watch index rows'
    for row in data['records']:
        if row['url'] not in CHANGED:continue
        previous=m['previous_records'][row['url']]
        assert set(previous)==set(row),'Watch field set changed'
        assert {k:v for k,v in row.items() if k!='text'}=={k:v for k,v in previous.items() if k!='text'},'Non-text Watch record drift'
        row['text']=previous['text']
    out=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    assert sha(out)==BEFORE,'Exact Watch predecessor not reconstructed'
    return out
