"""Exact legacy answer repairs successor and registration binding.

Registers one exact change set in ask.html and pioneers.html (PR #516):
the legacy answer repairs, the reviewed replacements for the answers
Hannah's full coverage pass flagged (76 repaired answer strings in
ask.html's qaDatabase, including the pioneer-hospitality source-slug
correction inside the pioneer hotels entry's sources, and 13 repaired
answer strings in pioneers.html's qaDatabase). 47 spans in ask.html
covering exactly the 76 changed lines and 11 spans in pioneers.html
covering exactly the 13 changed lines, all inside the two qaDatabase
stores, in AFTER-byte coordinates. Restoration removes only this layer
and reproduces the exact bytes the citation rendering successor layer
pins as its AFTER state for ask.html (4881b5a2...) and the exact bytes
the answer-bank successor layer pins as its AFTER state for
pioneers.html (b2b988d2...); the citation layer then strips ask.html
back to the answer-bank AFTER state (735ccd0d...), the answer-bank
layer strips both pages back to the states the continue-motion
predecessor map pins as current (ask.html 4a5f73ee..., pioneers.html
57fe21dc...), and the motion chain reconstructs the historical
predecessors. No answer-bank or citation manifest, module, or reviews,
no display-gate layer, no predecessor map, MAP_SHA, or motion
APPROVED_REVIEWS is re-pinned here, and predecessor recovery never
grants approval for changed behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent review
of this registration is Jeff's re-review of the PR head carrying it,
required by J-2026-10-25-081 conditions C1-C2 (registry figures as
corrected by J-2026-10-25-082) and delivered on the channel; it gates
merge, and no finished in-tree review record is claimed here. check()
verifies the registration's exact bytes, spans, and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/legacy-answer-repairs-successor/manifest.json"
SOURCE_SHA = "fffe86443107b0ca67bcb96536b804ca741ca88bcc464c85e1ff962e47b453dc"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "ask.html": "4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9",
    "pioneers.html": "b2b988d240a7d54b60b2d2701fde26f54fa6ca1b63261b3d7f7f9e89377a3bf5",
}
AFTER = {
    "ask.html": "0d9a5f1ba3a6bf815084ef3df330b25b771332dfa837dd2f21e74b133a9cfc90",
    "pioneers.html": "0674855075616de71f8b89b8b6e3b0145a48e80cc7e7f1b8b7a64874b77fa05d",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def require(value, message):
    if not value:
        raise ValueError(message)


def local(root, name):
    root = Path(root).resolve()
    path = (root / name).resolve()
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside legacy answer repairs successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed legacy answer repairs successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "legacy_answer_repairs_successor", "Wrong legacy answer repairs successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong legacy answer repairs successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong legacy answer repairs predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong legacy answer repairs candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing legacy answer repairs spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate legacy answer repairs spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid legacy answer repairs span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Legacy answer repairs successor candidate PENDING")
    return _manifest_bytes(local(root, MANIFEST).read_bytes())


def restore(name, raw, root=ROOT):
    if name not in BEFORE or SOURCE_SHA is None:
        return raw
    row = mapping(root)["files"][name]
    if sha(raw) != AFTER[name]:
        return raw
    result = raw
    for span in reversed(row["spans"]):
        start, stop = span["start"], span["end"]
        new = base64.b64decode(span["current_b64"])
        old = base64.b64decode(span["previous_b64"])
        require(stop <= len(raw) and raw[start:stop] == new, "Legacy answer repairs inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Legacy answer repairs predecessor mismatch: " + name)
    return result


def advance(name, raw, root=ROOT):
    """Generate only the exact registered successor from its exact predecessor."""
    if name not in BEFORE or SOURCE_SHA is None:
        return raw
    row = mapping(root)["files"][name]
    if sha(raw) != BEFORE[name]:
        return raw
    replacements = []
    delta = 0
    for span in row["spans"]:
        old = base64.b64decode(span["previous_b64"])
        new = base64.b64decode(span["current_b64"])
        start = span["start"] + delta
        require(raw[start:start + len(old)] == old, "Legacy answer repairs forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Legacy answer repairs forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed legacy answer repairs successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Legacy answer repairs successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Legacy answer repairs successor forward mismatch: " + name)
    return {"status": "LEGACY_ANSWER_REPAIRS_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Legacy answer repairs successor gate BLOCKED: " + str(error))
