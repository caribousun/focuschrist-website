"""Exact Timeline search successor for historical Emma index comparisons.

This checks bytes and fresh producers; it does not create a current review,
owner acceptance, or a release decision. Historical Emma receipts remain bound
only to the reconstructed previous index. Current review is a separate gate.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/timeline-controls-successor/search-index-delta.json'
MANIFEST_SHA256='92017fcda04ec298e06cff1c6b259c89b02ae43946737d0da87eea97aba2235c'
BEFORE='ba1ea0787568ce5dc6f51b7661a31ead0088c7e39f2d988286fd98697398ac67'
AFTER='abcd13069b734ca5f25ecc003abef56717093b73c31e336ae84bd3d647ffabf1'
CHANGED=frozenset({'/answers/jesus-christ-latter-day-saint-beliefs.html',
                   '/answers/jesus-christ-latter-day-saint-beliefs.html#nazareth-childhood',
                   '/timelines/adams-1881-chart.html'})
SOURCES={'answers/jesus-christ-latter-day-saint-beliefs.html':'dd071c356cb85d33bea1b717447446a2ab9f7f49d2fcb8e4eb4e458b3a7d6078',
         'timelines/adams-1881-chart.html':'43f19fc23f4fd17e1c9fdb54003feab2885565c97b1a98abc6aefb092ec06944'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def record_hash(record):return sha(json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def source(root,name):
    root=Path(root).resolve();p=root/name
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert all(not root.joinpath(*Path(name).parts[:i]).is_symlink() for i in range(1,len(Path(name).parts)+1))
    assert p.resolve().is_relative_to(root) and p.is_file(), 'Missing or unsafe source '+name
    return p.read_bytes()
def manifest(root=ROOT):
    raw=source(root,MANIFEST);assert sha(raw)==MANIFEST_SHA256,'Changed index delta manifest'
    m=json.loads(raw)
    assert set(m)=={'schema','kind','previous_sha256','current_sha256','source_sha256','changes'}
    assert m['schema']==1 and m['kind']=='timeline_search_delta_for_historical_emma_review'
    assert m['previous_sha256']==BEFORE and m['current_sha256']==AFTER and m['source_sha256']==SOURCES
    assert set(m['changes'])==CHANGED
    return m

def restore(raw,root=ROOT):
    """Project the exact current bytes to the exact previously reviewed bytes."""
    m=manifest(root);assert sha(raw)==AFTER,'Unknown or modified current search index'
    for name,expected in SOURCES.items():assert sha(source(root,name))==expected,'Changed current source '+name
    current=json.loads(raw);assert set(current)=={'version','pages','records'} and current['version']==1
    records=current['records'];assert isinstance(records,list)
    urls=[r['url'] for r in records];assert len(urls)==len(set(urls)),'Duplicate search destination'
    assert CHANGED <= set(urls),'Missing expected current destination'
    output=[]
    for r in records:
        url=r['url']
        if url not in CHANGED:output.append(r);continue
        change=m['changes'][url];assert set(change)=={'previous','current_record_sha256'}
        assert record_hash(r)==change['current_record_sha256'],'Changed current record '+url
        previous=change['previous']
        if previous is not None:
            assert isinstance(previous,dict) and previous.get('url')==url
            assert set(previous)==set(r),'Prior record field set changed'
            output.append({key:previous[key] for key in r})
        else:assert url.endswith('#nazareth-childhood'),'Unexpected added record'
    previous=dict(current,records=output)
    restored=(json.dumps(previous,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    assert sha(restored)==BEFORE,'Prior exact search bytes not reconstructed'
    return restored

def validate_current(root=ROOT):
    """Check real output and producer before the historic byte projection."""
    import build_site_search
    root=Path(root).resolve();assert build_site_search.ROOT.resolve()==root,'Search producer root mismatch'
    raw=source(root,'site-search-index.json');previous=restore(raw,root)
    assert build_site_search.build()==json.loads(raw),'Search output differs from full-tree producer'
    return {'current_sha256':sha(raw),'previous_sha256':sha(previous),'changed_urls':sorted(CHANGED),
            'scope':'mechanical exact-output comparison only; independent review and release remain separate'}
