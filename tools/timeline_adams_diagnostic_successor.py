"""Exact Adams diagnostic-only successor; reconstruction does not approve release."""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = 'timelines/adams-1881-chart.html'
MANIFEST = 'docs/timeline-controls-successor/adams-source-delta.json'
MANIFEST_SHA = '25cb8c9ca50d607f1bcef7dfb84ed560732397810dbea889a4d62c6fd9c2e4cb'
BEFORE = 'b90c19dd9f77c3966843b41d514319816a194deee86b87235909f6b2c742130c'
AFTER = '43f19fc23f4fd17e1c9fdb54003feab2885565c97b1a98abc6aefb092ec06944'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def restore(raw, root=ROOT):
    """Validate exact changed bytes, then return the exact prior source."""
    root = Path(root).resolve()
    path = root / MANIFEST
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    manifest_raw = path.read_bytes()
    assert sha(manifest_raw) == MANIFEST_SHA, 'Adams successor manifest changed'
    record = json.loads(manifest_raw)
    assert record['schema'] == 1 and record['path'] == PATH
    assert record['before_sha256'] == BEFORE and record['after_sha256'] == AFTER
    assert sha(raw) == AFTER, 'Unreviewed Adams successor source'
    changes = record['changes']
    assert len(changes) == 4
    for row in reversed(changes):
        old = base64.b64decode(row['before_b64'], validate=True)
        new = base64.b64decode(row['after_b64'], validate=True)
        assert old != new and raw.count(new) == 1, 'Adams successor context changed'
        raw = raw.replace(new, old, 1)
    assert sha(raw) == BEFORE, 'Adams predecessor mismatch'
    return raw
