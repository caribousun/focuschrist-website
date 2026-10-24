"""Exact reviewed answer bank (step 1) successor and finished-review binding.

Registers one exact change set: four deferred answer-bank script tags
inserted immediately after the reviewed-ask-knowledge.js tag in ask.html
and pioneers.html, and one guarded bank branch inserted at the top of
researchDisclosure in pioneer-experience.js. Restoration removes only
this layer and reproduces the exact bytes the continue-motion
predecessor map pins as current for those files. No predecessor map,
MAP_SHA, or motion APPROVED_REVIEWS is re-pinned here, and predecessor
recovery never grants approval for changed behavior.
"""
import base64
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/answer-bank-successor/manifest.json"
REVIEWS = "docs/answer-bank-successor/reviews.json"
RENDERED_DIR = "docs/answer-bank-successor/rendered"
SOURCE_SHA = "2a2b55fcb06404702fe01df1e55f974f68e138bd04835e13313c9903fe25cebe"  # Integrator pins exact candidate spans; this is not review approval.
BEFORE = {
    "ask.html": "4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3",
    "pioneers.html": "57fe21dc3a92dde1b5c51cddcf872cabe62d1e88a7ec259fc135afaa80cb8b81",
    "pioneer-experience.js": "229d4698dd9316af84047e295134636f77ed9965291c5444c03183fa54487593",
}
AFTER = {
    "ask.html": "735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612",
    "pioneers.html": "b2b988d240a7d54b60b2d2701fde26f54fa6ca1b63261b3d7f7f9e89377a3bf5",
    "pioneer-experience.js": "b1f6f02625377c9f28850e88d707c4e9837c0d6c183510463b65448294cfb9cb",
}
APPROVED_REVIEWS = "ed646f1ccb999eb71433619bfa6d1d4ce4dbf3483eede4dfe4d487fd02c8c9a0"  # Finished Jeff reviews of this registration: J-2026-10-23-048 (registration-source) and J-2026-10-23-049 (rendered).


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
    require(path.is_relative_to(root) and path.is_file(), "Missing/outside answer bank successor evidence: " + name)
    return path


from functools import lru_cache


@lru_cache(maxsize=4)
def _manifest_bytes(raw):
    data = json.loads(raw.decode("utf-8"))
    require(SOURCE_SHA is not None and canonical(data) == SOURCE_SHA, "Changed answer bank successor manifest")
    require(data.get("schema") == 1 and data.get("layer") == "answer_bank_successor", "Wrong answer bank successor schema")
    files = data.get("files")
    require(isinstance(files, dict) and set(files) == set(BEFORE), "Wrong answer bank successor file set")
    for name, row in files.items():
        require(row.get("before_sha256") == BEFORE[name], "Wrong answer bank predecessor: " + name)
        require(row.get("after_sha256") == AFTER[name] and AFTER[name] != BEFORE[name], "Wrong answer bank candidate digest: " + name)
        spans = row.get("spans")
        require(isinstance(spans, list) and bool(spans), "Missing answer bank spans: " + name)
        end = -1
        for span in spans:
            start, stop = span["start"], span["end"]
            require(type(start) is int and type(stop) is int and 0 <= start <= stop and start > end, "Overlapping/duplicate answer bank spans: " + name)
            old = base64.b64decode(span["previous_b64"], validate=True)
            new = base64.b64decode(span["current_b64"], validate=True)
            require(len(new) == stop - start and old == b"" and new != old, "Invalid answer bank span bytes: " + name)
            end = stop
    return data


def mapping(root=ROOT):
    require(SOURCE_SHA is not None, "Answer bank successor candidate PENDING")
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
        require(stop <= len(raw) and raw[start:stop] == new, "Answer bank inverse byte mismatch: " + name)
        result = result[:start] + old + result[stop:]
    require(sha(result) == BEFORE[name], "Answer bank predecessor mismatch: " + name)
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
        require(raw[start:start + len(old)] == old, "Answer bank forward byte mismatch: " + name)
        replacements.append((start, start + len(old), new))
        delta += len(old) - len(new)
    result = raw
    for start, stop, new in reversed(replacements):
        result = result[:start] + new + result[stop:]
    require(sha(result) == AFTER[name], "Answer bank forward digest mismatch: " + name)
    return result


RENDERED_MISSING = "Answer bank successor rendered review MISSING"


def _rendered(root, record):
    """Rendered evidence collection and the independent rendered review are
    separate scopes from the registration/source review (A002 split).
    Returns False only when a slot is absent or still unfilled; anything
    present but wrong-scope, wrong-actor, unfinished, or tampered raises."""
    evidence = record.get("rendered_evidence")
    if not isinstance(evidence, dict) or evidence.get("status") != "COLLECTED" or not evidence.get("captures"):
        return False
    require(evidence.get("collected_by") in ("Merlin", "Merlin worker"), "Wrong answer bank rendered evidence collector")
    require(evidence.get("pages_sha256") == AFTER, "Wrong answer bank rendered evidence pages")
    hashes = []
    for cap in evidence["captures"]:
        require(set(cap) == {"height", "media", "path", "screen", "sha256", "width"}, "Wrong answer bank rendered capture record")
        require(cap["path"].startswith(RENDERED_DIR + "/") and cap["path"].endswith(".png.b64"), "Wrong answer bank rendered capture path")
        encoded = local(root, cap["path"]).read_bytes()
        require(re.fullmatch(rb"[A-Za-z0-9+/=\r\n]+", encoded) is not None, "Rendered capture is not base64 text")
        decoded = base64.b64decode(encoded, validate=False)
        require(sha(decoded) == cap["sha256"], "Changed answer bank rendered evidence")
        from PIL import Image
        with Image.open(io.BytesIO(decoded)) as image:
            require(image.format == "PNG" and list(image.size) == [cap["width"], cap["height"]], "Rendered capture dimensions changed")
        hashes.append(cap["sha256"])
    observations = evidence.get("observations")
    require(isinstance(observations, dict), "Missing answer bank rendered observations")
    require(sha(local(root, observations["path"]).read_bytes()) == observations["sha256"], "Changed answer bank rendered observations")
    review = record.get("rendered_review")
    if not isinstance(review, dict) or review.get("status") != "FINISHED":
        return False
    require(review.get("reviewer") in ("Jeff", "Albert"), "Wrong answer bank rendered reviewer")
    require(review.get("scope") in ("rendered", "rendered-review"), "Wrong answer bank rendered review scope")
    require(review.get("decision") == "CONCUR", "Unfinished answer bank rendered review")
    require(review.get("finished_pixels") is True and review.get("finished_behavior") is True, "Unfinished answer bank rendered review")
    require(review.get("files") == AFTER, "Wrong answer bank rendered reviewer pages")
    require(review.get("capture_sha256") == hashes, "Answer bank rendered review not bound to rendered evidence captures")
    item = review["evidence"]
    require(sha(local(root, item["path"]).read_bytes()) == item["sha256"], "Changed answer bank rendered review evidence")
    return True


def check(root=ROOT):
    data = mapping(root)
    for name, row in data["files"].items():
        raw = local(root, name).read_bytes()
        require(sha(raw) == AFTER[name], "Changed answer bank successor page: " + name)
        require(sha(restore(name, raw, root)) == BEFORE[name], "Answer bank successor predecessor mismatch: " + name)
    require(APPROVED_REVIEWS is not None, "Answer bank successor finished review PENDING")
    record = json.loads(local(root, REVIEWS).read_text(encoding="utf-8"))
    require(canonical(record) == APPROVED_REVIEWS, "Changed answer bank successor reviews")
    require(record.get("source_sha256") == SOURCE_SHA and record.get("files") == AFTER, "Wrong answer bank successor review binding")
    require(record.get("required_reviewers") == ["Jeff"], "Wrong answer bank required reviewers")
    registration = record.get("registration_review")
    require(isinstance(registration, dict), "Missing answer bank registration review")
    require(registration.get("reviewer") == "Jeff", "Wrong answer bank registration reviewer")
    require(registration.get("scope") == "registration-source", "Wrong answer bank registration review scope")
    require(registration.get("decision") == "CONCUR", "Unfinished answer bank registration review")
    require(registration.get("finished_pixels") is False, "Answer bank registration review must record finished_pixels=false (A002)")
    require(registration.get("finished_behavior") is True, "Unfinished answer bank registration behavior review")
    require(registration.get("files") == AFTER, "Wrong answer bank registration reviewer pages")
    item = registration["evidence"]
    require(sha(local(root, item["path"]).read_bytes()) == item["sha256"], "Changed answer bank registration review evidence")
    require(_rendered(root, record), RENDERED_MISSING)
    return {"status": "ANSWER_BANK_SUCCESSOR_EVIDENCE_PASS", "files": sorted(AFTER)}


if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("Answer bank successor gate BLOCKED: " + str(error))
