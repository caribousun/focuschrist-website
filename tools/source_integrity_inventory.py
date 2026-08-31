#!/usr/bin/env python3
"""Inventory and gate verified/unverified source-dependent answer paths."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ask = (ROOT / "ask.html").read_text(encoding="utf-8")
common = (ROOT / "site-common.js").read_text(encoding="utf-8")
v3 = (ROOT / "study-intelligence-v3.js").read_text(encoding="utf-8")
pioneer = (ROOT / "pioneer-experience.js").read_text(encoding="utf-8")
history = (ROOT / "church-history-experience.js").read_text(encoding="utf-8")
router = (ROOT / "study-source-router.js").read_text(encoding="utf-8")

database = ask.split("const qaDatabase = {", 1)[1].split("\n    };", 1)[0]
entries = len(re.findall(r"^\s*'[^']+'\s*:\s*\{", database, re.M))
verified = len(re.findall(r"\bverified\s*:\s*true\b", database))
unverified = entries - verified
errors = []
if entries < 1 or verified < 1 or unverified < 1:
    errors.append(f"unexpected Q&A inventory: entries={entries}, verified={verified}, unverified={unverified}")
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
if "unreviewed-source-dependent-generation" not in common:
    errors.append("shared source-integrity contract is not fail-closed")

runtime_files = [ROOT / "site-common.js", ROOT / "study-source-router.js", ROOT / "ask.html", ROOT / "pioneers.html", ROOT / "church-history.html"]
versions = set()
for path in runtime_files:
    versions.update(re.findall(r"study-intelligence-v3\.js\?v=(\d+-\d+)", path.read_text(encoding="utf-8")))
if versions != {"20260831-5"}:
    errors.append(f"mixed Study Intelligence v3 cache versions: {sorted(versions)}")

if errors:
    raise SystemExit("Source integrity inventory failed:\n - " + "\n - ".join(errors))
print(f"Source integrity inventory PASS: {entries} entries; {verified} verified; {unverified} quarantined")
