"""Exact Adams landing-page and two-index delivery; not publication approval.

The landing page and actual indices from CI run 40482829846 are bound to
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
MANIFEST = "docs/adams-delivery-successor/manifest.json"
# Exact candidate data binding, NOT a reviewer or publication authorization.
INDEX_FILES = ("art-gallery.json", "site-search-index.json")
SOURCE_SHA = "62f8b61493b018695e9de9fb130d40bf26de6e98302b99263e9da964b7c8146f"
BEFORE = {
    "timeline.html": "dc00d3d589a6e50c7359c98f8228d2491926b8a5a9ed764628b0ac9c31264e8f",
    "art-gallery.json": "87d40761a71174a62c1686af62967f9904d1fee762333859f91bea11e0754a96",
    "site-search-index.json": "eb85bd29a11eee569749064667a00c5640687c08ea6d7ff413ca7a606d8831a0",
}
AFTER = {
    "timeline.html": "fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578",
    "art-gallery.json": "21e3ca0c843117371bae82010c3faea37ea9e4394df44975019220a7f4c8cea3",
    "site-search-index.json": "edbd12a7385703fa632e69af0366ce3fb7e61a23dce7a73680b225a6c3a83f76",
}


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
            and data["schema"] == 1 and data["layer"] == "adams_delivery_successor", "wrong schema")
    files = data["files"]
    require(isinstance(files, dict) and set(files) == set(BEFORE) == set(AFTER), "wrong file set")
    for name, row in files.items():
        require(set(row) == {"before_sha256", "after_sha256", "before_bytes", "after_bytes", "spans"},
                "wrong binding fields: " + name)
        require(row["before_sha256"] == BEFORE[name], "wrong predecessor: " + name)
        require(row["after_sha256"] == AFTER[name] and AFTER[name] != BEFORE[name], "wrong candidate: " + name)
        require(all(type(row[k]) is int and row[k] > 0 for k in ("before_bytes", "after_bytes")),
                "wrong sizes: " + name)
        spans = row["spans"]
        require(isinstance(spans, list) and bool(spans), "missing spans: " + name)
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
    return {"status": "EXACT_ADAMS_DELIVERY_EVIDENCE_PASS", "files": sorted(AFTER),
            "limits": "Exact byte reconstruction only; no review or publication authorization."}


@contextmanager
def predecessor_view(root=ROOT):
    """Verify actual Adams first; yield only an exact historical Emma fixture.

    This does NOT establish that current checkout files have Emma hashes.
    All three actual current Adams files must pass their own complete hashes and
    round trips before the unchanged historical layer is checked separately.
    The real checkout is read only; the temporary view contains exactly the
    two reconstructed indices and unchanged Emma manifest, then is removed.
    """
    import tempfile
    import emma_generated_indices_successor as emma
    check(root)
    prior_bytes = {}
    for name in INDEX_FILES:
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "current changed before predecessor view: " + name)
        prior = restore(name, raw, root)
        require(sha(prior) == BEFORE[name] == emma.AFTER[name], "wrong historical Emma pair: " + name)
        prior_bytes[name] = prior
    emma.mapping(root)
    manifest = emma.local(root, emma.MANIFEST).read_bytes()
    with tempfile.TemporaryDirectory(prefix="adams-historical-emma-") as td:
        view = Path(td)
        for name, raw in prior_bytes.items():
            (view / name).write_bytes(raw)
        dest = view / emma.MANIFEST
        dest.parent.mkdir(parents=True)
        dest.write_bytes(manifest)
        yield view


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Adams delivery gate BLOCKED: " + str(error))
