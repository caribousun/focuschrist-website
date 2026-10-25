"""Exact A047 citation rendering successor and registration binding.

Registers one exact change set in ask.html (PR #515): addMessage's
sources block classifies each source by its actual URL host at render
time, so only official Church hosts render under "Official Church
sources", focusChrist sources render once in the related group
carrying the study-source router's dedupe marker, and any other host
renders under a neutral "Referenced sources" group. Five spans in
AFTER-byte coordinates, together exactly the PR #515 edit (+53/-11
lines) inside addMessage's sources block. Restoration removes only
this layer and reproduces the exact bytes the answer-bank successor
layer pins as its AFTER state for ask.html (735ccd0d...); the
answer-bank layer then strips back to the state the continue-motion
predecessor map pins as current for ask.html (4a5f73ee...), and the
motion chain reconstructs the historical predecessor (bbeeb8c6...).
No answer-bank manifest, module, or reviews, no display-gate layer,
no predecessor map, MAP_SHA, or motion APPROVED_REVIEWS is re-pinned
here, and predecessor recovery never grants approval for changed
behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent review
of this registration is Jeff's re-review of the PR head carrying it,
required by J-2026-10-24-075 conditions C1-C2 and delivered on the
channel; it gates merge, and no finished in-tree review record is
claimed here. check() verifies the registration's exact bytes, spans,
and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/citation-rendering-successor/manifest.json"
SOURCE_SHA = "aec0fb747f31c69d328cad446cac1222a8cd42cedaf2d0e03f57482ec6f0e462"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "ask.html": "735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612",
}
AFTER = {
    "ask.html": "4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside citation rendering successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed citation rendering successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "citation_rendering_successor", "Wrong citation rendering successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong citation rendering successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong citation rendering predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong citation rendering candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing citation rendering spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate citation rendering spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid citation rendering span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Citation rendering successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Citation rendering inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Citation rendering predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Citation rendering forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Citation rendering forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed citation rendering successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Citation rendering successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Citation rendering successor forward mismatch: " + name)
    return {"status": "CITATION_RENDERING_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Citation rendering successor gate BLOCKED: " + str(error))
