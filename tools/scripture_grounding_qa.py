#!/usr/bin/env python3
"""Release-blocking checks for Ask-page scripture grounding controls."""

from pathlib import Path

ask_text = (Path(__file__).resolve().parents[1] / "ask.html").read_text(encoding="utf-8")
v3_text = (Path(__file__).resolve().parents[1] / "study-intelligence-v3.js").read_text(encoding="utf-8")
common_text = (Path(__file__).resolve().parents[1] / "site-common.js").read_text(encoding="utf-8")

required = {
    "official LDS canon boundary": "the Holy Bible, Book of Mormon, Doctrine and Covenants, and Pearl of Great Price",
    "hard accuracy rule": "SCRIPTURE ACCURACY IS A HARD REQUIREMENT",
    "reference-content citation boundary": "ONLY when that passage and its official ChurchofJesusChrist.org source were supplied in REFERENCE CONTENT",
    "citation-to-source comparison": "const hasUngroundedCitation = generatedCitations.some",
    "fail-closed runtime check": "if (generatedCitations.length && hasUngroundedCitation)",
    "official Gospel Library fallback": "Please confirm this question in the official Gospel Library at ChurchofJesusChrist.org",
    "low-variance generation": "temperature: 0.1",
    "verified color answer": "Doctrine and Covenants 18:15 is about the joy of bringing a soul to Christ",
    "verified-answer bypass": "if(dbResult.verified)",
    "Ask shell cache version": "site-common.js?v=20260831-4",
}

missing = [label for label, marker in required.items() if marker not in ask_text]
if missing:
    raise SystemExit("Scripture grounding QA failed: " + ", ".join(missing))

runtime_required = {
    "final runtime verified-answer bypass": "if (localReference.found && localReference.verified)",
    "final runtime verified flag": "verified: item.verified === true",
    "known false-claim blocker": "Blocked known false Doctrine and Covenants color claim",
}
runtime_missing = [label for label, marker in runtime_required.items() if marker not in v3_text]
if runtime_missing:
    raise SystemExit("Scripture grounding runtime QA failed: " + ", ".join(runtime_missing))

if "study-intelligence-v3.js?v=20260831-4" not in common_text:
    raise SystemExit("Scripture grounding runtime QA failed: final runtime cache version is stale")

for false_claim in (
    'red light that "shines upon the righteous"',
    "Black represents the lowest degree of glory",
    "Red represents the highest degree",
):
    if false_claim in ask_text:
        raise SystemExit(f"Scripture grounding QA failed: known false claim present: {false_claim}")

print("Scripture grounding QA PASS")
