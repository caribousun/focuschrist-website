"""Exact World controls source successor; this is not release approval."""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'timelines/world-and-scripture-timeline.html'
MANIFEST = 'docs/timeline-controls-successor/world-source-delta.json'
MANIFEST_SHA = '90563b2ba333d764a73cca4d497179f6c00e9725005b2fc3c3a86bd72c95a6f3'
BEFORE = 'a6f0a9fb82e16405a0cf32e25cbd7889ad0a56b5af4e9003fca40bd985ad93fd'
AFTER = '016e9896db70ff0a8a142503f289f2e0cbd2f4d96b73d667247dbb2a2370ceef'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def restore(raw, root=ROOT):
    root = Path(root).resolve()
    path = root / MANIFEST
    assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root)
    content = path.read_bytes()
    assert sha(content) == MANIFEST_SHA, 'World controls successor manifest changed'
    record = json.loads(content)
    assert record['schema'] == 1 and record['path'] == PAGE
    assert record['before_sha256'] == BEFORE and record['after_sha256'] == AFTER
    assert sha(raw) == AFTER, 'Unreviewed World controls source'
    assert len(record['changes']) == 7
    for item in reversed(record['changes']):
        before = base64.b64decode(item['before_b64'], validate=True)
        after = base64.b64decode(item['after_b64'], validate=True)
        assert before != after and after and raw.count(after) == 1, 'World controls successor context changed'
        raw = raw.replace(after, before, 1)
    assert sha(raw) == BEFORE, 'World controls predecessor mismatch'
    return raw
