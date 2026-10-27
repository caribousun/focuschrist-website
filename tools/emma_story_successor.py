"""Exact Emma story successor and registration binding.

Registers one exact change set in history/emma-hale-smith.html, the
Emma Hale Smith hub page: the doorways from the hub into five new
Emma story pages built under action
A-2026-10-26-EMMA-STORY-ENRICHMENT-01, plus the reading-flow
transition remedies judged by Hannah, the team's voice lead, in the
assembled candidate under
A-2026-10-26-EMMA-VISUAL-REFERENCE-COORDINATION-01.

The change set, in page order:

- a small page-local style block for the doorway card grid (the
  fifth card spans two columns at desktop widths so the row
  completes, under the complete-card-rows mandate);
- in section 1, the reflection paragraph after the night-prayer
  picture (picture-emma-c1) is reworded to begin from Emma's own
  documented prayer life, with the family tradition labeled as
  family tradition, before turning to Luke 6 and the reader;
- in section 2, a short pause paragraph is inserted between the
  paragraph recording the children's deaths and the well picture
  (picture-emma-c2), so the grief is given room in the reading
  sequence, and the visible reflection paragraph after the picture
  is reworded to name Emma herself as someone who also needed
  food, rest, and care;
- "Continue with ..." doorway links at the ends of hub sections 2,
  3 (two links, in story order), 4, and 6, pointing to the five new
  story pages;
- in section 6, the boat picture (picture-emma-c5) and its
  reflection paragraph are moved, wording unchanged, to after the
  paragraph about David's illness, so the reflection's gentleness
  lands where the grief is freshest in the sequence;
- a new "More of Emma's stories" section before "Pause and
  reflect", with five story cards in the shared panel design.

The hub was already pinned in the continue-motion predecessors map
(its two script-tag spans); no other successor layer covers it, so
this layer composes as the new outermost layer in
tools/continue_motion_binding.py: restoration removes this layer
first and reproduces the mapped AFTER bytes, and the map spans
then apply as before. The figure at #picture-emma-h4, its artwork,
caption, and id are byte-identical before and after; every existing
hub picture, caption, and source link outside the spans above is
unchanged. This layer adds no image files: the five new story
pages' scene pictures are held under the character-image gates
(Fermi and Newton pre-creation concurrence and finished-pixel
inspection, with creation reserved to Albert's cloud image tool),
so the pages are registered as scaffolding without images.

The five story texts themselves are the concurred stage-1 drafts
(Jeff J-2026-10-25-119 on the exact draft bytes); the new furniture
copy and the transition remedies carry Hannah's build pass
(exact replacements applied as written), and the finished
candidate carries Jeff's independent exact-bytes review on the
channel.

Review model: this module pins the exact candidate spans only
(SOURCE_SHA); that pin is not review approval. Publication
requires Albert's concurrence on the finished package; no
finished in-tree review record is claimed here. check() verifies
the registration's exact bytes, spans, and round trip only.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/emma-story-successor/manifest.json"
SOURCE_SHA = "f4e713e6c4930e4a494ac44c333b21aaff790d6ba3985be72304fde243c379cd"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "history/emma-hale-smith.html": "a238cee0edaea3d0f5c6e3c8f453fa7988bc5e995bf01649ea369388e9262cc1",
}
AFTER = {
    "history/emma-hale-smith.html": "e26dff780368d88ea1cdd2e5f0ed0636b9f048f2af4b88f9be1fdef03036fe0f",
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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside Emma story successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed Emma story successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "emma_story_successor", "Wrong Emma story successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong Emma story successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong Emma story successor predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong Emma story successor candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing Emma story successor spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate Emma story successor spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old != new, "Invalid Emma story successor span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Emma story successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Emma story successor inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Emma story successor predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Emma story successor forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Emma story successor forward digest mismatch: " + name)
    return result


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed Emma story successor page: " + name)
        restored = restore(name, raw, root)
        require(sha(restored) == BEFORE[name], "Emma story successor predecessor mismatch: " + name)
        require(advance(name, restored, root) == raw, "Emma story successor forward mismatch: " + name)
    return {"status": "EMMA_STORY_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Emma story successor gate BLOCKED: " + str(error))
