"""Exact bank-serve decoupling successor and registration binding.

Registers one exact change set across two files, the reviewed-bank
decoupling fix:

- ask.html: the page's inline legacy sendMessage controller consults
  the reviewed answer bank lane (window.FocusChristAnswerBankLane)
  before its legacy lookup, and a lane serve renders through
  addMessage with the reviewed-bank provenance marker, so a bank-bound
  question is answered by the bank whichever controller owns the ask.
- site-common.js: the scripture display gate's reviewed-bank
  exemption (isPinnedReviewedBankServe) is bound through the
  bank-owning code. The marker fields remain a claim filter, but the
  exemption now requires the lane's verifyPinnedServe to confirm,
  against the loaded pin-checked bank, the claimed record ID, the
  whole-entry pin, the exact served answer, and its sources. A forged
  marker, a wrong pin, an edited answer, or a stale, unreviewed, or
  missing record earns no exemption.

This layer is the outermost successor over both files. For ask.html
its BEFORE state is the citation rendering successor's AFTER state;
for site-common.js its BEFORE state is the evaluator corrections
successor's AFTER state. Restoration removes only this layer and
reproduces those exact bytes; the composed binding chain then
reconstructs the earlier states. No predecessor map, MAP_SHA, or
motion APPROVED_REVIEWS is re-pinned here, and predecessor recovery
never grants approval for changed behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent review
of this registration is the exact-head review of the PR carrying it
(Jeff, with Newton's parallel review per
A-2026-10-24-ASK-DECOUPLING-CONCURRENCE-01); it gates merge, and no
finished in-tree review record is claimed here. check() verifies the
registration's exact bytes, spans, and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/bank-serve-decoupling-successor/manifest.json"
SOURCE_SHA = "517a1d5bd339441661f4d5f62796cdd9b542c955ec294fdc4b253439719eaa90"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "ask.html": "4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9",
    "site-common.js": "54cfb9fc5de9c5ab76133cb32843053ee6c5700ff0fe11d8bedd470de3412a77",
}
AFTER = {
    "ask.html": "7e316e8901de722fc06a5972a786a45c36ddfa07dcc26578d496239c76bc404f",
    "site-common.js": "62e8d576062521da340ad6b0a82f58b151829c21b6868b684e6491b04c723f73",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside bank serve decoupling successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed bank serve decoupling successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "bank_serve_decoupling_successor", "Wrong bank serve decoupling successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong bank serve decoupling successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong bank serve decoupling predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong bank serve decoupling candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing bank serve decoupling spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate bank serve decoupling spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid bank serve decoupling span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Bank serve decoupling successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Bank serve decoupling inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Bank serve decoupling predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Bank serve decoupling forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Bank serve decoupling forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed bank serve decoupling successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Bank serve decoupling successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Bank serve decoupling successor forward mismatch: " + name)
    return {"status": "BANK_SERVE_DECOUPLING_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Bank serve decoupling successor gate BLOCKED: " + str(error))
