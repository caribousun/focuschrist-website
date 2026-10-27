"""Explicit isolated a36 historical fixtures for unchanged old regression assertions.

Current frontend bytes are checked before projection. This does not replace any
current QA input or claim that standalone behavior remains current. The normal
CLI and current integration tests always read the actual repository tree.
"""
import atexit
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
from owner_integration_contract import historical_bytes, manifest, validate_file

ARCHIVE = 'docs/owner-integration-contract/history/a36'
FIXTURE_SHA = 'b2b7985c1bdead0e828e28a55517d3ca902a9b9e4c159730f193e25766f52c02'
SHARED = {
    'docs/unified-opening-inventory.json': '1b8a8fcd180c95591caff7a8cc26f90d8817942b',
    'site-system.css': 'bf2b326352f5a4b57cdf8195d9331264844b9c41',
    'missionary.css': '3c3c72d2219418525b4478a77cf96fe6de7b4055',
    'timeline-mobile-study.css': '67e3121a94784e6047f3b8a302ed8c91f4872e52',
    'tools/test_section_panel_standalone.py': 'a716de861394d3f1b6a173172f56c63da7409880',
}
_roots = {}
_temps = []

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def historical_root(current):
    current = Path(current).resolve()
    if current in _roots:
        return _roots[current]
    source = current/ARCHIVE
    raw = (source/'fixtures.json').read_bytes()
    assert sha(raw) == FIXTURE_SHA, 'Historical fixture manifest drift'
    files = json.loads(raw)['files']
    values = {}
    for rel, item in files.items():
        assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
        assert '/' not in item['file'] and '\\' not in item['file']
        raw = (source/item['file']).read_bytes()
        assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'Historical fixture bytes drift'
        values[rel] = raw
    # No projection of unchecked current source or new-page invented predecessor.
    for rel, row in manifest(current)['files'].items():
        raw = (current/rel).read_bytes()
        validate_file(rel, raw, current)
        if 'historical' in row:
            values[rel] = historical_bytes(rel, raw, current)
    for rel, expected in SHARED.items():
        raw = (current/rel).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == expected, 'Shared historical fixture source drift: '+rel
        values[rel] = raw
    # The new actual index must inverse to the exact unchanged predecessor. A
    # pending/unrecognized index cannot make the historical test silently pass.
    from adams_integration_indices import restore
    raw = restore('site-search-index.json', (current/'site-search-index.json').read_bytes(), current)
    assert sha(raw) == 'edbd12a7385703fa632e69af0366ce3fb7e61a23dce7a73680b225a6c3a83f76', 'Exact historical search fixture drift'
    values['site-search-index.json'] = raw
    temp = tempfile.TemporaryDirectory(prefix='focus-owner-historical-tests-')
    _temps.append(temp); root = Path(temp.name)
    for rel, raw in values.items():
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    _roots[current] = root
    return root

def historical_panel_module(root):
    path = Path(root)/'tools/section_panel_surface_qa.py'
    loader=importlib.machinery.SourceFileLoader('owner_historical_section_panels',str(path))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    module=importlib.util.module_from_spec(spec);loader.exec_module(module)
    assert module.ROOT == Path(root)
    return module

def _cleanup():
    for temp in _temps:
        temp.cleanup()

atexit.register(_cleanup)
