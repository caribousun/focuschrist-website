#!/usr/bin/env python3
"""Inventory and gate verified/unverified source-dependent answer paths."""

from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ask = (ROOT / "ask.html").read_text(encoding="utf-8")
common = (ROOT / "site-common.js").read_text(encoding="utf-8")
v3 = (ROOT / "study-intelligence-v3.js").read_text(encoding="utf-8")
pioneer = (ROOT / "pioneer-experience.js").read_text(encoding="utf-8")
history = (ROOT / "church-history-experience.js").read_text(encoding="utf-8")
router = (ROOT / "study-source-router.js").read_text(encoding="utf-8")
journey = (ROOT / "study-journey.js").read_text(encoding="utf-8")
pioneers_html = (ROOT / "pioneers.html").read_text(encoding="utf-8")
history_html = (ROOT / "church-history.html").read_text(encoding="utf-8")
answer_audit = json.loads((ROOT / "answer-audit.json").read_text(encoding="utf-8"))

database = ask.split("const qaDatabase = {", 1)[1].split("\n    };", 1)[0]
entry_pattern = re.compile(r"^\s*'(?P<key>[^']+)'\s*:\s*(?P<body>\{.*\})\s*,?\s*$", re.M)
parsed_entries = {match.group("key"): match.group("body") for match in entry_pattern.finditer(database)}
entries = len(re.findall(r"^\s*'[^']+'\s*:\s*\{", database, re.M))
verified_keys = {
    key for key, body in parsed_entries.items()
    if re.search(r"\bverified\s*:\s*true\b", body)
}
verified = len(re.findall(r"\bverified\s*:\s*true\b", database))
unverified = entries - verified
errors = []
if entries < 1 or verified < 1 or unverified < 1:
    errors.append(f"unexpected Q&A inventory: entries={entries}, verified={verified}, unverified={unverified}")
if verified != len(verified_keys):
    errors.append("one or more verified Ask entries could not be pinned to a reviewed key and hash")

reviewed_records = answer_audit.get("reviewed_answers", [])
reviewed_key_list = [record.get("key") for record in reviewed_records if record.get("path") == "ask.html"]
reviewed_keys = set(reviewed_key_list)
if len(reviewed_key_list) != len(reviewed_keys):
    errors.append("duplicate keys in reviewed-answer manifest")
if verified_keys != reviewed_keys:
    errors.append(
        "Ask verified keys differ from the reviewed allowlist: "
        f"runtime={sorted(verified_keys)} reviewed={sorted(reviewed_keys)}"
    )
for record in reviewed_records:
    if record.get("path") != "ask.html":
        errors.append(f"unsupported reviewed-answer path: {record.get('path')!r}")
        continue
    key = record.get("key")
    body = parsed_entries.get(key)
    if body is None:
        errors.append(f"reviewed Ask answer is missing: {key!r}")
        continue
    normalized = re.sub(r"\s+", " ", body).strip()
    actual_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if record.get("entry_sha256") != actual_hash:
        errors.append(f"reviewed Ask answer changed after approval: {key!r}")
    sources = record.get("authoritative_sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"reviewed Ask answer lacks authoritative sources: {key!r}")

pioneer_database = pioneers_html.split("const qaDatabase = {", 1)[1].split("\n    function collapseAIResponse", 1)[0]
pioneer_verified = len(re.findall(r"\bverified\s*:\s*true\b", pioneer_database))
reviewed_pioneer = answer_audit.get("pioneer_verified_answers")
if reviewed_pioneer != [] or pioneer_verified != 0:
    errors.append(
        "Pioneer legacy answers must remain fully quarantined until individually reviewed: "
        f"runtime_verified={pioneer_verified} reviewed={reviewed_pioneer!r}"
    )
if "verifiedIntentMatchesBase(q,bestMatch)" not in ask:
    errors.append("Ask legacy accessor can still serve unverified or intent-mismatched entries")
if "groundedLocalReference" not in v3 or "Unreviewed legacy Q&A entries are quarantined" not in v3:
    errors.append("v3 does not quarantine unverified legacy entries")
if "verifiedIntentMatches" not in v3:
    errors.append("verified entries lack explicit intent matching")
if "Source-dependent pioneer answers remain blocked" not in pioneer:
    errors.append("Pioneer final owner is not fail-closed")
if "LINKS ONLY; NOT CLAIM VERIFICATION" not in history or "LINKS ONLY; NOT CLAIM VERIFICATION" not in router:
    errors.append("Church History routes can still be mislabeled as claim verification")
if router.count("focusChristSourceIntegrity.isScriptureDependent") < 2:
    errors.append("source router does not reuse the shared scripture detector for faith classification and Scriptures-hub routing")
if "Verified study paths" in router or "Verified study sources" in router:
    errors.append("source routes are still mislabeled as claim verification")
if "unreviewed-source-dependent-generation" not in common:
    errors.append("shared source-integrity contract is not fail-closed")

runtime_files = [ROOT / "site-common.js", ROOT / "study-source-router.js", ROOT / "ask.html", ROOT / "pioneers.html", ROOT / "church-history.html"]
versions = set()
for path in runtime_files:
    versions.update(re.findall(r"study-intelligence-v3\.js\?v=(\d+-\d+)", path.read_text(encoding="utf-8")))
if versions != {"20260831-5"}:
    errors.append(f"mixed Study Intelligence v3 cache versions: {sorted(versions)}")

cache_markers = {
    "site-common.js": (common, "study-journey.js?v=20260831-5"),
    "study-journey.js": (journey, "study-source-router.js?v=20260831-5"),
    "pioneers.html": (pioneers_html, "pioneer-experience.js?v=20260831-5"),
    "church-history.html common": (history_html, "site-common.js?v=20260831-5"),
    "church-history.html router": (history_html, "study-source-router.js?v=20260831-5"),
    "church-history.html experience": (history_html, "church-history-experience.js?v=20260831-5"),
}
for label, (text, marker) in cache_markers.items():
    if marker not in text:
        errors.append(f"stale source-integrity cache path: {label} missing {marker}")

if errors:
    raise SystemExit("Source integrity inventory failed:\n - " + "\n - ".join(errors))
print(f"Source integrity inventory PASS: {entries} entries; {verified} verified; {unverified} quarantined")
