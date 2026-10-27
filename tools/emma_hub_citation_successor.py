"""Exact outer hub-anchor registration; historical pins and release gates remain intact."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'history/emma-hale-smith.html'
MANIFEST = 'docs/emma-hub-citation-successor/manifest.json'
BEFORE = 'e26dff780368d88ea1cdd2e5f0ed0636b9f048f2af4b88f9be1fdef03036fe0f'
AFTER = '0d825d6c9d0648006ca4ba12f496b49540a6aa065f8ec82063df643da8a0fe9d'
SOURCE_SHA = '814218588e48e887e2e65ec6322b2a795ee0e51a95eccadb793f2ad728ea8abb'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def mapping(root=ROOT):
    root = Path(root).resolve()
    file = (root / MANIFEST).resolve()
    require(file.is_relative_to(root) and file.is_file(), 'Missing/outside hub citation manifest')
    value = json.loads(file.read_text(encoding='utf-8'))
    canonical = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    require(sha(canonical) == SOURCE_SHA, 'Changed hub citation manifest')
    require(value['schema'] == 1 and value['layer'] == 'emma_hub_citation_successor' and value['path'] == NAME, 'Wrong hub citation schema/owner')
    require(value['before_sha256'] == BEFORE and value['after_sha256'] == AFTER, 'Changed hub citation endpoints')
    require(len(value['pairs']) == 2, 'Exactly two citation wrappers required')
    return value

def restore(name, raw, root=ROOT):
    if name != NAME or sha(raw) != AFTER:
        return raw
    value = mapping(root)
    out = raw
    for pair in reversed(value['pairs']):
        new, old = pair['after'].encode(), pair['before'].encode()
        require(out.count(new) == 1, 'Hub citation inverse span mismatch')
        out = out.replace(new, old, 1)
    require(sha(out) == BEFORE, 'Hub citation inverse digest mismatch')
    return out

def advance(name, raw, root=ROOT):
    if name != NAME or sha(raw) != BEFORE:
        return raw
    value = mapping(root)
    out = raw
    for pair in value['pairs']:
        old, new = pair['before'].encode(), pair['after'].encode()
        require(out.count(old) == 1, 'Hub citation forward span mismatch')
        out = out.replace(old, new, 1)
    require(sha(out) == AFTER, 'Hub citation forward digest mismatch')
    return out

def check(root=ROOT):
    root = Path(root).resolve()
    file = (root / NAME).resolve()
    require(file.is_relative_to(root) and file.is_file(), 'Missing/outside hub citation page')
    from owner_integration_successor import restore as restore_owner
    raw = restore_owner(NAME, file.read_bytes(), root)
    require(sha(raw) == AFTER, 'Changed hub citation current page')
    mapping(root)
    prior = restore(NAME, raw, root)
    require(sha(prior) == BEFORE and advance(NAME, prior, root) == raw, 'Hub citation round trip mismatch')
    return {'status': 'EXACT_HUB_CITATION_BINDING', 'files': 1, 'limits': 'Exact historical hub citation registration only; current owner source validation is separate from rendered/release approval.'}

@contextmanager
def predecessor_view(root=ROOT):
    """Validate current bytes, then expose only the exact prior hub and old manifest."""
    root = Path(root).resolve()
    check(root)
    with tempfile.TemporaryDirectory() as temp:
        view = Path(temp)
        (view / NAME).parent.mkdir(parents=True)
        from owner_integration_successor import restore as restore_owner
        (view / NAME).write_bytes(restore(NAME, restore_owner(NAME, (root / NAME).read_bytes(), root), root))
        source = (root / 'docs/emma-story-successor').resolve()
        require(source.is_relative_to(root), 'Outside historical manifest')
        shutil.copytree(source, view / 'docs/emma-story-successor')
        yield view
