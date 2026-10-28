"""Exact outer source reconstruction for historical assertions only.

Current UI/artwork acceptance is separate and stays pending until its real
rendered evidence and reviews pass. Unknown bytes are never normalized.
"""
import base64
from pathlib import Path
from owner_integration_contract import CHART, LANDING, HUB, STORIES, manifest, sha, validate_file, historical_bytes

ROOT=Path(__file__).resolve().parents[1]
NAMES=frozenset((CHART,LANDING,HUB,*STORIES))
CURRENT={'timeline.html': 'c910ae58c2f8feccf1d59f44b154d31f224436b79538e86bf73774c65b0b8c4c', 'timelines/adams-1881-chart.html': 'b90c19dd9f77c3966843b41d514319816a194deee86b87235909f6b2c742130c', 'history/emma-elect-lady.html': 'f32c79609f15d51e9c85b2f4bc941de38d2626c944e33f1876fc574f46f7986c', 'history/emma-hale-smith.html': '50c334379066722ef6e80e97d70f0f2ca431777b5857eb15b998da65cc1783cf', 'history/emma-hymns.html': '719bc7f899ebc188f33322c4c7c6bea9e326b209e28e2d49855543185e12aedb', 'history/emma-last-testimony.html': 'ff608df4a3bb994d29834e253daac97b1721ecf2b3209a621e284f16ca91eb70', 'history/emma-relief-society.html': 'e90e7b25239973e2488f32e57482fd5cfbdabb6a7f3f1746599aded9cd546ebb', 'history/emma-winter-crossing.html': 'a2c6003789eaaf4458bb3f431943c2d4602908b19324054ef8ca9f0aab30a417'}
BEFORE={'timeline.html': 'fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578', 'timelines/adams-1881-chart.html': '95802a989d818d0ff7297660274c62f18140950b0bf58fc96a90277ef1e1cb90', 'history/emma-elect-lady.html': 'e5b234afe494b825f90a94b58ff8b6363e349aa94a4d51562c9d037c58906820', 'history/emma-hale-smith.html': '0d825d6c9d0648006ca4ba12f496b49540a6aa065f8ec82063df643da8a0fe9d', 'history/emma-hymns.html': 'ab1373de9ed550b1a7192f30f67f0222538d50c9422c4fca7168d8efe9fc754c', 'history/emma-last-testimony.html': '983a41ea229c286018be4c355f28a39b4c9f6294221b001d2985356f0fafb559', 'history/emma-relief-society.html': 'f13772d3e7aa457aef1cb02804e3c2ab86adcab870b64e2f7aa25a8cc3a70310', 'history/emma-winter-crossing.html': '4245bdf43ad6dd24dfa47b31c6f3ff411c407d0e9a6d7ef352cec0f815008186'}

def restore(name, raw, root=ROOT):
    if name == LANDING:
        validate_file(name, raw, root)
        return historical_bytes(name, raw, root)
    if name not in NAMES or sha(raw)!=CURRENT[name]:
        return raw
    row=manifest(root)['files'][name]
    assert row['sha256']==CURRENT[name]
    return historical_bytes(name,raw,root)

def advance(name, raw, root=ROOT):
    if name == LANDING and sha(raw) == BEFORE[name]:
        # Historical checks compare against the actual current page's semantics,
        # not a fabricated current page reconstructed from the old receipt.
        path = Path(root) / name
        assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(Path(root).resolve())
        current = path.read_bytes()
        validate_file(name, current, root)
        assert historical_bytes(name, current, root) == raw, 'Historical Timeline endpoint mismatch'
        return current
    if name not in NAMES or sha(raw)!=BEFORE[name]:
        return raw
    row=manifest(root)['files'][name];history=row['historical']
    assert history['sha256']==BEFORE[name]
    replacements=[];delta=0
    for span in history['inverse_spans']:
        old=base64.b64decode(span['before'],validate=True)
        new=base64.b64decode(span['after'],validate=True)
        offset=span['current_offset']+delta
        assert raw[offset:offset+len(old)]==old, 'Exact integration forward context'
        replacements.append((offset,offset+len(old),new));delta+=len(old)-len(new)
    result=raw
    for start,end,new in reversed(replacements):
        result=result[:start]+new+result[end:]
    validate_file(name,result,root)
    return result

def check(root=ROOT):
    for name,row in manifest(root)['files'].items():
        raw=(root/name).read_bytes();validate_file(name,raw,root)
        if name in NAMES and name != LANDING:
            assert advance(name,restore(name,raw,root),root)==raw, 'Current exact source round trip'
    return {'status':'EXACT_OWNER_SOURCE_REGISTRATION','files':11,'limits':'Source reconstruction only; no current artwork/rendered/release approval.'}
