"""Exact Ask entry scroll-follow successor and registration binding.

Registers one exact change set (branch
feature/ask-entry-scroll-follow-2026-10-25): the Ask conversation
scroll follow fix in ask.html and ask-experience.js. In ask.html,
addMessage now calls a new bringEntryIntoView helper on the appended
entry instead of forcing the transcript to its bottom. In
ask-experience.js, the MutationObserver captures the actual added
answer node and passes it to the follow functions, the answer-ready
handler passes its event target, and focusLatestAnswer,
focusLatestAnswerSettled, and addRelatedStudyToLatestAnswer anchor
the answer's own exchange (its preceding user message) instead of
the first exchange in the box, which is where a follow-up chip click
left the view. Spans are in AFTER-byte coordinates. Restoration
removes only this layer and reproduces the exact bytes the
bank-serve decoupling successor pins as its AFTER state for
ask.html (42329b80...), which itself composes over the
legacy-answer-repairs successor's AFTER state, and the exact
bytes the continue-motion predecessor map pins as current for
ask-experience.js (its after hash, 62f17066...); the older
layers then strip back through the decoupling, legacy,
citation, and answer-bank states and the motion chain to the
historical predecessors. No predecessor map, MAP_SHA, motion
APPROVED_REVIEWS, or other successor manifest or module is
re-pinned here, and predecessor recovery never grants approval
for changed behavior.

Re-pin note (2026-10-25): the bank-serve decoupling successor's
ask.html AFTER state was amended in place (its inline serve now
also renders the follow-up chips adjunct), so this layer's
ask.html BEFORE and AFTER pins moved with it; this layer's span
byte contents are unchanged.

Re-pin note (2026-10-25, second): the bank-serve decoupling
successor's ask.html AFTER state was amended in place again
(its inline controller now waits, bounded, for the bank lane
before producing any outcome when the lane has not arrived
yet), so this layer's ask.html BEFORE and AFTER pins moved
with it again; this layer's span byte contents are unchanged.

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
MANIFEST = "docs/entry-scroll-successor/manifest.json"
SOURCE_SHA = "9ed42a5cc9aeb838a4c02ed132d15f292b5900b7382a25fadddf2e25309ced41"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "ask.html": "42329b80eaeb28c89d7c1bcab62215e914f2e10e1e9c01eb35d1c9268d32d41d",
    "ask-experience.js": "62f17066d8d50d8e8ec417190f026111b628f11e8221f2babd7b40d257ea2fab",
}
AFTER = {
    "ask.html": "3595a295f5df683c2cc842f3ae51705eed08963face03b90bd85a8fe9246ad1f",
    "ask-experience.js": "9aba64e444ddc89f1b0c3a5dfc5fdae3b77e6933a28cc83901059b8041e34b8d",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside entry scroll successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed entry scroll successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "entry_scroll_successor", "Wrong entry scroll successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong entry scroll successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong entry scroll predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong entry scroll candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing entry scroll spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate entry scroll spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid entry scroll span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Entry scroll successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Entry scroll inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Entry scroll predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Entry scroll forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Entry scroll forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed entry scroll successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Entry scroll successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Entry scroll successor forward mismatch: " + name)
    return {"status": "ENTRY_SCROLL_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Entry scroll successor gate BLOCKED: " + str(error))
