"""Exact generic-context bank bypass successor and registration binding.

Registers one exact change set in study-intelligence-v3.js (the Ask
bank-original-wording fix): inside askV3, when resolveQuestionContext
classifies the visitor's question as a generic-context follow-up
(genericContext=true), the reviewed answer bank is first matched
against the visitor's ORIGINAL wording, and an actual bank serve (not
a suggestion set) is returned before the generic-context guard can
suppress the bank. The guard itself is unchanged: it still keeps the
augmented generic-context query out of every local lane, so a
genuinely elliptical follow-up whose own wording the bank does not
serve keeps the existing contextual flow exactly. The death-as-
background and support-request guards still suppress the new match
as they suppress the existing lanes.

Why: resolveFollowup treats any question containing a referential
token (it, that, this, he, they, ...) as a follow-up candidate. A
complete, self-contained bank canonical such as "What does it mean
to endure to the end?" was reclassified whenever any earlier question
existed in the session, genericContext became true, askV3 set
allowContextualLocalMatch=false, and the bank was never consulted:
the question fell to the live research leg, which rendered either a
generated answer or the fail-closed "unable to check our approved
study sources" message. That is the only path by which a visitor
reaches that question as a follow-up chip under the faith-during-
trials answer, so the chip never served its reviewed record
(diagnosis fcfix2/endure-pill-diagnosis: 36 history-path attempts, 0
bank serves; 13 bank canonicals flip to genericContext=true with
history present). Fresh single-question sessions were unaffected,
which is why every census missed it.

study-intelligence-v3.js was not a pinned file before this layer
(the bank-serve decoupling successor's README records that status);
this layer pins it for the first time, with BEFORE the exact bytes
at the base of this change. No other file's registration composes
over it, so restoration removes only this layer and reproduces those
bytes directly. No predecessor map, MAP_SHA, motion
APPROVED_REVIEWS, or other successor manifest or module is
re-pinned here, and predecessor recovery never grants approval for
changed behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent
review of this registration is Jeff's exact-head review of the PR
carrying it, delivered on the channel; it gates merge, and no
finished in-tree review record is claimed here. check() verifies
the registration's exact bytes, spans, and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/bank-context-bypass-successor/manifest.json"
SOURCE_SHA = "c95e068a0d87f2e753f698bad4c8eecd04837ce631155c483707b3a3f42397f5"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "study-intelligence-v3.js": "a851a94a471a0637f5a95fcc25f3d31d87a28bac7bc55e0b7cdaaf789c8c42f1",
}
AFTER = {
    "study-intelligence-v3.js": "ff50c52144911c3c4f3244c2c9825778891109645d7bf6863756d8920ed2d9cb",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside bank context bypass successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed bank context bypass successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "bank_context_bypass_successor", "Wrong bank context bypass successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong bank context bypass successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong bank context bypass predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong bank context bypass candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing bank context bypass spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate bank context bypass spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid bank context bypass span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Bank context bypass successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Bank context bypass inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Bank context bypass predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Bank context bypass forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Bank context bypass forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed bank context bypass successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Bank context bypass successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Bank context bypass successor forward mismatch: " + name)
    return {"status": "BANK_CONTEXT_BYPASS_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Bank context bypass successor gate BLOCKED: " + str(error))
