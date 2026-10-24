"""Exact display-gate bank exemption successor and registration binding.

Registers one exact change set in site-common.js (PR #509): the
scripture display gate exemption for pinned reviewed-bank serves. Three
spans in AFTER-byte coordinates: the verifier signature line replaced
and its early-return line added, the isPinnedReviewedBankServe
predicate inserted, and the gate wrapper call line replaced to pass
its fourth argument through. Restoration removes only this layer and
reproduces the exact bytes the continue-motion predecessor map pins
as current for site-common.js (its after hash); the motion chain then
reconstructs the historical predecessor. No predecessor map, MAP_SHA,
or motion APPROVED_REVIEWS is re-pinned here, and predecessor recovery
never grants approval for changed behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent review
of this registration is Jeff's review of the PR head carrying it,
required by J-2026-10-24-068 conditions C1-C3 and delivered on the
channel; it gates merge, and no finished in-tree review record is
claimed here. check() verifies the registration's exact bytes, spans,
and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/display-gate-successor/manifest.json"
SOURCE_SHA = "b9517e15318253debbac73d1d020f290260f5ad3e419d429598ebdef139b9adc"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "site-common.js": "4a7e22262e1a62e9b9e119cc83b70f02f6fc2902a935d03ffec77f67333911a9",
}
AFTER = {
    "site-common.js": "9090c0bf19a4093f881bf0d1f9f95236ec1db8d61a7072251d807f5c9ce3a041",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside display gate successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed display gate successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "display_gate_successor", "Wrong display gate successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong display gate successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong display gate predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong display gate candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing display gate spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate display gate spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid display gate span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Display gate successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Display gate inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Display gate predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Display gate forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Display gate forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed display gate successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Display gate successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Display gate successor forward mismatch: " + name)
    return {"status": "DISPLAY_GATE_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Display gate successor gate BLOCKED: " + str(error))
