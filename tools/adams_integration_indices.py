"""Exact Adams landing-page and two-index delivery; not publication approval.

Pending: new actual generated indices have not been received. The layer binds
their complete predecessor/current pairs. Semantic acceptance requires
separate independent review.
Only the complete named byte pairs apply. Unknown input is never normalized;
older validators still see it unchanged and keep every historical expected pin.
No artwork-creation, source, rights, layout, or finished-review gate is waived.
Future generated combinations need their own separately reviewed exact layer.
"""
import base64
import hashlib
import json
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/adams-integrated-context/generated-indices.json"
# Exact candidate data binding, NOT a reviewer or publication authorization.
INDEX_FILES = ("art-gallery.json", "site-search-index.json")
SOURCE_SHA = '9183f7c6d5eaf3f7918f23f2fc98a2323a7a82f36ae9b42724d2c79f3a141efc'  # Actual data binding; independent review remains separate.
BEFORE = {'timeline.html': 'fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578', 'art-gallery.json': '21e3ca0c843117371bae82010c3faea37ea9e4394df44975019220a7f4c8cea3', 'site-search-index.json': 'edbd12a7385703fa632e69af0366ce3fb7e61a23dce7a73680b225a6c3a83f76'}
AFTER = {'timeline.html': 'c910ae58c2f8feccf1d59f44b154d31f224436b79538e86bf73774c65b0b8c4c', 'art-gallery.json': '1bf5d0adbb1a6699313cf24a599a316e800b9e62ef8aeeb7acfde8f32e867402', 'site-search-index.json': 'a9933a9ec749aec4163a1b146f0946c54244a4f78f781e7f508cea4e51b8260a'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def require(value, message):
    if not value:
        raise ValueError("Adams delivery: " + message)


def local(root, name):
    root = Path(root).resolve()
    require(isinstance(name, str) and name in {MANIFEST, *BEFORE}, "unknown evidence path")
    path = root / name
    require(not path.is_symlink() and path.is_file() and path.resolve().is_relative_to(root),
            "missing/outside evidence: " + name)
    return path


def _mapping(raw, expected):
    data = json.loads(raw)
    require(expected is not None and canonical(data) == expected, "changed manifest")
    require(set(data) == {"schema", "layer", "files"} and type(data["schema"]) is int
            and data["schema"] == 1 and data["layer"] == "adams_integration_indices", "wrong schema")
    files = data["files"]
    require(isinstance(files, dict) and set(files) == set(BEFORE) == set(AFTER), "wrong file set")
    for name, row in files.items():
        require(set(row) == {"before_sha256", "after_sha256", "before_bytes", "after_bytes", "spans"},
                "wrong binding fields: " + name)
        require(row["before_sha256"] == BEFORE[name], "wrong predecessor: " + name)
        require(row["after_sha256"] == AFTER[name] , "wrong candidate: " + name)
        require(all(type(row[k]) is int and row[k] > 0 for k in ("before_bytes", "after_bytes")),
                "wrong sizes: " + name)
        spans = row["spans"]
        require(isinstance(spans, list) and (bool(spans) or AFTER[name] == BEFORE[name]), "missing spans: " + name)
        end, delta = -1, 0
        for span in spans:
            require(set(span) == {"start", "end", "previous_b64", "current_b64"}, "wrong span fields: " + name)
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop <= row["after_bytes"]
                    and start > end, "overlapping/outside spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "invalid span bytes: " + name)
            end = stop
            delta += len(old) - len(new)
        require(row["after_bytes"] + delta == row["before_bytes"], "inconsistent sizes: " + name)
    return data


def mapping(root=ROOT):
    return _mapping(local(root, MANIFEST).read_bytes(), SOURCE_SHA)


def restore(name, raw, root=ROOT):
    if name not in AFTER or sha(raw) != AFTER[name]:
        return raw
    row = mapping(root)["files"][name]
    require(len(raw) == row["after_bytes"], "candidate size mismatch: " + name)
    result = raw
    for span in reversed(row["spans"]):
        start, stop = span["start"], span["end"]
        new = base64.b64decode(span["current_b64"], validate=True)
        old = base64.b64decode(span["previous_b64"], validate=True)
        require(raw[start:stop] == new, "inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(len(result) == row["before_bytes"] and sha(result) == BEFORE[name], "predecessor mismatch: " + name)
    return result


def advance(name, raw, root=ROOT):
    if name not in BEFORE or sha(raw) != BEFORE[name]:
        return raw
    row = mapping(root)["files"][name]
    require(len(raw) == row["before_bytes"], "predecessor size mismatch: " + name)
    replacements, delta = [], 0
    for span in row["spans"]:
        old = base64.b64decode(span["previous_b64"], validate=True)
        new = base64.b64decode(span["current_b64"], validate=True)
        start = span["start"] + delta
        require(0 <= start <= start + len(old) <= len(raw) and raw[start:start + len(old)] == old,
                "forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(len(result) == row["after_bytes"] and sha(result) == AFTER[name], "forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    for name in mapping(root)["files"]:
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "changed current delivery: " + name)
        prior = restore(name, raw, root)
        require(sha(prior) == BEFORE[name], "predecessor mismatch: " + name)
        require(advance(name, prior, root) == raw, "round trip mismatch: " + name)
    return {"status": "EXACT_ADAMS_INTEGRATION_INDEX_EVIDENCE_PASS", "files": sorted(AFTER),
            "limits": "Exact byte reconstruction only; no review or publication authorization."}

PRODUCER_MANIFEST = 'docs/adams-integrated-context/index-producer.json'
PRODUCER_SHA = '9b6f21a948aa8d8fd0f5fc5e97b85b57501836dd6016b4c819275e0c84ab76e8'  # Actual successful generator job evidence; review remains separate.
FRONTEND_INPUTS = {'timeline.html','timelines/adams-1881-chart.html',
 'timelines/adams-1881-introduction.html','adams-integration.css','adams-integration.js',
 'history/emma-hale-smith.html','history/emma-elect-lady.html','history/emma-hymns.html',
 'history/emma-winter-crossing.html','history/emma-relief-society.html','history/emma-last-testimony.html'}
GENERATORS = {'tools/build_art_gallery.py','tools/build_site_search.py'}

def validate_historical_producer(root=ROOT):
    import re
    path = Path(root) / PRODUCER_MANIFEST
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(Path(root).resolve()), 'unsafe producer evidence')
    record = json.loads(path.read_bytes())
    require(PRODUCER_SHA is not None and canonical(record) == PRODUCER_SHA, 'actual producer evidence pending or changed')
    require(type(record.get('schema')) is int and record.get('schema') == 1 and record.get('repository') == 'caribousun/focuschrist-website', 'producer schema/repository')
    require(record.get('job_conclusion') == 'success', 'generator job not successful')
    for key in ('producer_commit','producer_tree'):
        require(re.fullmatch(r'[0-9a-f]{40}',record.get(key,'')) is not None, 'missing producer '+key)
    require(all(type(record.get(k)) is int and record[k] > 0 for k in ('run_id','job_id','artifact_id')), 'missing actual provider identities')
    rows = record['inputs']
    require(len(rows) == 14 and {r['path'] for r in rows} == FRONTEND_INPUTS | GENERATORS | {'sitemap.xml'}, 'exact eleven frontend, two generators and current canonical inventory')
    for row in rows:
        p = Path(root) / row['path']
        require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(Path(root).resolve()), 'unsafe producer input')
        require(not any(q.is_symlink() for q in [p,*p.parents] if q == Path(root) or Path(root) in q.parents), 'symlink producer input')
        raw = p.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'producer input changed: '+row['path'])
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob_sha1'], 'producer Git binding changed')
    from xml.etree import ElementTree
    routes = [node.text for node in ElementTree.fromstring((Path(root) / 'sitemap.xml').read_bytes()).iter() if node.tag.rsplit('}',1)[-1] == 'loc']
    require(len(routes) == len(set(routes)) == 139, 'coherent current139 canonical routes required')
    require('https://focuschrist.com/timelines/adams-1881-introduction.html' in routes, 'current introduction absent from producer inventory')
    outputs = record['outputs']
    require(len(outputs) == 2 and {r['path'] for r in outputs} == set(INDEX_FILES), 'exact generated output pair')
    for row in outputs:
        raw = local(root, row['path']).read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'] == AFTER[row['path']], 'actual output differs from producer')
    return record

def validate_producer(root=ROOT):
    # Current evidence must never silently fall back to a historical producer.
    # The old verifier remains separately named for explicitly historical use.
    from adams_index_producer_successor import validate_successor
    return validate_successor(root)


def check_current(root=ROOT):
    # Current content/index validity is separate from old producer receipts.
    # The configured generator --check steps independently establish complete
    # source-to-output equivalence on the actual checkout.
    from timeline_current_indices import validate_current
    return validate_current(root)

if __name__ == '__main__':
    try:
        print(json.dumps(check_current(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit('Adams integrated indices BLOCKED: ' + str(error))
