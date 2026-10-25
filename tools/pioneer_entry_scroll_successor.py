"""Exact Pioneer entry scroll-follow successor and registration binding.

Registers one exact change set (branch
feature/pioneer-entry-scroll-follow-2026-10-25, amended by
branch feature/pioneer-composer-scroll-followup-2026-10-25):
the Pioneer conversation scroll follow fix in pioneers.html and
pioneer-experience.js, the Pioneers counterpart of the Ask entry
scroll fix in PR #520. In pioneers.html, the page's own addMessage
ended by forcing the transcript to its absolute top
(c.scrollTop=0) on every append; it now calls a new
bringEntryIntoView helper on the appended entry instead. In
pioneer-experience.js, whose window.addMessage override is the
live append path on the page, the appended message is now passed
to a new bringPioneerEntryIntoView helper immediately after the
append, so every append anchors its own entry (composer answers
already receive the exchange-level positionAnswer refinement;
the choice-list, story, and error appends that never call it now
anchor too). Amendment: the helper now defers to the scripture
display gate. site-common wraps window.addMessage so a bot answer
is first rendered as a [data-scripture-pending] placeholder,
which the caller positions with positionAnswer, and the real
answer is appended afterwards and transplanted into the
placeholder. The append-time scrollIntoView also fired on that
late real append, after positioning, and dragged the panel to
the appended position; when an earlier exchange followed the
promoted one, the answer-ready re-positioning is suppressed and
the wrong scroll stood (the composer-path regression the #522
finisher's live watch caught). The helper therefore returns
without scrolling when the entry's parent box still holds a
[data-scripture-pending] placeholder: that append's content is
bound for the already-positioned placeholder. Appends with no
gate placeholder pending keep the original anchor unchanged.
Spans are in AFTER-byte coordinates. Restoration
removes only this layer and reproduces the exact bytes the
legacy-answer-repairs successor pins as its AFTER state for
pioneers.html (06748550...), which itself composes over the
answer-bank successor's AFTER state for pioneers.html
(b2b988d2...), and the exact bytes the answer-bank successor
pins as its AFTER state for pioneer-experience.js
(b1f6f026...); the older layers then strip back through the
answer-bank states and the motion chain to the historical
predecessors. No predecessor map, MAP_SHA, motion
APPROVED_REVIEWS, or other successor manifest or module is
re-pinned here, and predecessor recovery never grants approval
for changed behavior.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. The independent
review of this registration is Jeff's exact-head review of the
PR carrying it, delivered on the channel; it gates merge, and
no finished in-tree review record is claimed here. check()
verifies the registration's exact bytes, spans, and round trip
only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/pioneer-entry-scroll-successor/manifest.json"
SOURCE_SHA = "b4b19d29bb489612f35a2acc6cca18d9dceb980c22576006629c4fa5a704445f"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "pioneers.html": "0674855075616de71f8b89b8b6e3b0145a48e80cc7e7f1b8b7a64874b77fa05d",
    "pioneer-experience.js": "b1f6f02625377c9f28850e88d707c4e9837c0d6c183510463b65448294cfb9cb",
}
AFTER = {
    "pioneers.html": "b9275099d3a124a940e3c402d905c7994be2fbaf6fe69caebf28481e84078e4f",
    "pioneer-experience.js": "2baf4d3cef128337fb687f99299d21ebdcf4831cd781d5fa8b72fee6955f00cd",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside pioneer entry scroll successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed pioneer entry scroll successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "pioneer_entry_scroll_successor", "Wrong pioneer entry scroll successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong pioneer entry scroll successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong pioneer entry scroll predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong pioneer entry scroll candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing pioneer entry scroll spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate pioneer entry scroll spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid pioneer entry scroll span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Pioneer entry scroll successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Pioneer entry scroll inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Pioneer entry scroll predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Pioneer entry scroll forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Pioneer entry scroll forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed pioneer entry scroll successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Pioneer entry scroll successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Pioneer entry scroll successor forward mismatch: " + name)
    return {"status": "PIONEER_ENTRY_SCROLL_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Pioneer entry scroll successor gate BLOCKED: " + str(error))
