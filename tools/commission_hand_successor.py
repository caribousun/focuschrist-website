"""Fail-closed successor for the approved commission hand repair delivery.

The artwork creation gate preserves every baseline raster byte-exactly, so the
owner-approved hand repair ships as a registered corrected family at new paths
(docs/artwork-correction-reviews.json, family MISSION-HAND) and this layer
registers the exact page change that re-points the two affected pages from the
preserved original renditions to the corrected renditions. Restoration removes
only this layer and reproduces the exact bytes the missionary close successor
produced; no predecessor map is re-pinned here.
"""
import base64
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/commission-hand-successor/manifest.json"
REVIEWS = "docs/commission-hand-successor/reviews.json"
RENDERED_DIR = "docs/commission-hand-successor/rendered"
SOURCE_SHA = "d7fdbb0ec36ec5c318c58277eefe9301fd9e83076ec216e171fba64939527eb5"
APPROVED_REVIEWS = "4aecfe596e44f868416ce3ea7b2ce8f50cc80c8643f1154e74f8794fdbd48657"
DETAILS_JS = "missionary-details.js"
SCREENS = {
    "missionary-figure-desktop",
    "missionary-detail-desktop",
    "missionary-figure-phone",
    "missionary-detail-phone",
    "index-mission-card-desktop",
    "index-mission-card-phone",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def require(value, message):
    if not value:
        raise ValueError(message)


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    manifest = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(manifest) == SOURCE_SHA, "Commission hand successor source changed")
    require(manifest.get("schema") == 1 and manifest.get("layer") == "commission_hand_successor", "Wrong commission hand successor schema")
    files = manifest.get("files")
    require(isinstance(files, dict) and set(files) == {"index.html", "missionary.html"}, "Commission hand successor file set changed")
    return manifest


def _manifest(root):
    return _manifest_bytes((root / MANIFEST).read_bytes())


def _spans(record):
    spans = record.get("spans")
    require(isinstance(spans, list) and spans, "Missing commission hand successor spans")
    decoded = []
    for span in spans:
        require(set(span) == {"after_b64", "before_b64", "occurrences"}, "Wrong commission hand successor span")
        before = base64.b64decode(span["before_b64"], validate=True)
        after = base64.b64decode(span["after_b64"], validate=True)
        require(before and after and before != after, "Invalid commission hand successor span bytes")
        require(isinstance(span["occurrences"], int) and span["occurrences"] >= 1, "Invalid commission hand successor span count")
        decoded.append((before, after, span["occurrences"]))
    return decoded


FILES = {"index.html", "missionary.html"}


def restore(name, data, root=ROOT):
    if name not in FILES:
        return data
    record = _manifest(root)["files"][name]
    if sha(data) != record["after_sha256"]:
        return data
    restored = data
    for before, after, occurrences in _spans(record):
        require(restored.count(after) == occurrences and before not in restored, "Commission hand successor span mismatch: " + name)
        restored = restored.replace(after, before)
    require(sha(restored) == record["before_sha256"], "Commission hand successor restore drift: " + name)
    return restored


def advance(name, data, root=ROOT):
    """Generate only the exact registered successor from its exact predecessor."""
    if name not in FILES:
        return data
    record = _manifest(root)["files"][name]
    if sha(data) != record["before_sha256"]:
        return data
    advanced = data
    for before, after, occurrences in _spans(record):
        require(advanced.count(before) == occurrences and after not in advanced, "Commission hand successor span mismatch: " + name)
        advanced = advanced.replace(before, after)
    require(sha(advanced) == record["after_sha256"], "Commission hand successor advance drift: " + name)
    return advanced


def _record(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(), "Missing/outside commission hand successor evidence")
    return path


def _rendered(root, reviews, manifest):
    evidence = reviews["rendered_evidence"]
    require(evidence.get("collected_by") == "Merlin worker", "Wrong rendered evidence collector")
    require(re.fullmatch(r"[0-9a-f]{40}", str(evidence.get("served_git_head", ""))) is not None, "Wrong served head")
    require(evidence.get("details_js_sha256") == sha((root / DETAILS_JS).read_bytes()), "Rendered evidence details script changed")
    pages = evidence.get("pages_sha256")
    require(isinstance(pages, dict) and set(pages) == {"index.html", "missionary.html"}, "Rendered evidence page set changed")
    for name, digest in pages.items():
        require(digest == manifest["files"][name]["after_sha256"], "Rendered evidence page changed: " + name)
    captures = evidence.get("captures")
    require(isinstance(captures, list) and {item.get("screen") for item in captures} == SCREENS, "Rendered evidence screens changed")
    hashes = {}
    for item in captures:
        require(set(item) == {"height", "media", "path", "screen", "sha256", "width"}, "Wrong rendered capture record")
        require(item["path"].startswith(RENDERED_DIR + "/") and item["path"].endswith(".png.b64"), "Wrong rendered capture path")
        encoded = _record(root, item["path"]).read_bytes()
        require(re.fullmatch(rb"[A-Za-z0-9+/=\r\n]+", encoded) is not None, "Rendered capture is not base64 text")
        decoded = base64.b64decode(encoded, validate=False)
        require(sha(decoded) == item["sha256"], "Rendered capture changed")
        from PIL import Image
        with Image.open(io.BytesIO(decoded)) as image:
            require(image.format == "PNG" and list(image.size) == [item["width"], item["height"]], "Rendered capture dimensions changed")
        hashes[item["screen"]] = item["sha256"]
    observations = _record(root, RENDERED_DIR + "/observations.json")
    require(sha(observations.read_bytes()) == evidence.get("observations_sha256"), "Rendered observations changed")
    return hashes


def _reviews(root, manifest):
    require(APPROVED_REVIEWS is not None, "Commission hand finished review PENDING")
    reviews = json.loads((root / REVIEWS).read_text(encoding="utf-8"))
    require(canonical(reviews) == APPROVED_REVIEWS, "Commission hand review record changed")
    require(set(reviews) == {"layer", "registration_review", "rendered_evidence", "rendered_review", "schema"}, "Wrong commission hand review schema")
    require(reviews.get("schema") == 1 and reviews.get("layer") == "commission_hand_successor", "Wrong commission hand review layer")
    hashes = _rendered(root, reviews, manifest)
    registration = reviews["registration_review"]
    require(registration.get("reviewer") == "Jeff" and registration.get("scope") == "registration-source", "Wrong registration reviewer")
    require(registration.get("decision") == "CONCUR" and registration.get("finished_pixels") is False and registration.get("finished_behavior") is True, "Registration review incomplete")
    rendered = reviews["rendered_review"]
    require(rendered.get("reviewer") == "Jeff" and rendered.get("scope") == "rendered-review", "Wrong rendered reviewer")
    require(rendered.get("decision") == "CONCUR" and rendered.get("finished_pixels") is True and rendered.get("finished_behavior") is True, "Rendered review incomplete")
    require(rendered.get("capture_hashes") == hashes, "Rendered review is not bound to the collected captures")
    return reviews


def check(root=ROOT):
    manifest = _manifest(root)
    for name, record in manifest["files"].items():
        current = _record(root, name).read_bytes()
        require(sha(current) == record["after_sha256"], "Commission hand successor page changed: " + name)
        _spans(record)
        require(sha(restore(name, current, root)) == record["before_sha256"], "Commission hand successor inverse failed: " + name)
    _reviews(root, manifest)
    return {
        "status": "COMMISSION_HAND_SUCCESSOR_EVIDENCE_PASS",
        "files": sorted(manifest["files"]),
        "limits": "Technical evidence binding only; does not authenticate reviewers or grant publication approval.",
    }


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Commission hand successor gate BLOCKED: " + str(error))
