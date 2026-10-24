"""Exact A047 evaluator corrections successor and registration binding.

Registers one exact change set in site-common.js (PR #512): the A047
Step S evaluator corrections, token-boundary profanity matching
(compactProfanityHit) and the D4 past-hurt forgiveness release
(pastHurtForgivenessRelease), the release's blocker alternation
carrying the four stated-intent forms Jeff's adversarial probing
required (threatens to, plans to, intends to, promised to). Four spans
in AFTER-byte coordinates: the two helpers inserted, the old
whole-string compact line removed from the profanity alternation, the
urgent alternation line replaced so bare past-tense "hurt me" is gated
by the release, and the profanity match line replaced to call the new
helper. Restoration removes only this layer and reproduces the exact
bytes the display-gate successor layer pins as its after-state for
site-common.js; the chain then strips the display-gate layer and the
motion chain reconstructs the historical predecessor. No predecessor
map, MAP_SHA, or motion APPROVED_REVIEWS is re-pinned here, and
predecessor recovery never grants approval for changed behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent review
of this registration is Jeff's re-review of the PR head carrying it,
required by J-2026-10-24-074 conditions C1-C3 and delivered on the
channel; it gates merge, and no finished in-tree review record is
claimed here. check() verifies the registration's exact bytes, spans,
and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/evaluator-corrections-successor/manifest.json"
SOURCE_SHA = "f865e1520576471cbeac12d12fdfaad23dcd9969bb32afbd19cb195a88e1a353"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "site-common.js": "9090c0bf19a4093f881bf0d1f9f95236ec1db8d61a7072251d807f5c9ce3a041",
}
AFTER = {
    "site-common.js": "54cfb9fc5de9c5ab76133cb32843053ee6c5700ff0fe11d8bedd470de3412a77",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside evaluator corrections successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed evaluator corrections successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "evaluator_corrections_successor", "Wrong evaluator corrections successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong evaluator corrections successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong evaluator corrections predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong evaluator corrections candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing evaluator corrections spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate evaluator corrections spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"])
            require(len(new) == stop - start and old != new, "Invalid evaluator corrections span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Evaluator corrections successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Evaluator corrections inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Evaluator corrections predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Evaluator corrections forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Evaluator corrections forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed evaluator corrections successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Evaluator corrections successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Evaluator corrections successor forward mismatch: " + name)
    return {"status": "EVALUATOR_CORRECTIONS_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Evaluator corrections successor gate BLOCKED: " + str(error))
