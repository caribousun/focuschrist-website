#!/usr/bin/env python3
"""Release-blocking checks for final-runtime scripture/source grounding."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
texts = {
    name: (ROOT / name).read_text(encoding="utf-8")
    for name in (
        "ask.html", "site-common.js", "study-intelligence-v3.js",
        "pioneer-experience.js", "groq-proxy/src/index.js",
    )
}
required_by_file = {
    "ask.html": (
        "the Holy Bible, Book of Mormon, Doctrine and Covenants, and Pearl of Great Price",
        "SCRIPTURE ACCURACY IS A HARD REQUIREMENT",
        "Doctrine and Covenants 18:15 is about the joy of bringing a soul to Christ",
        "if(dbResult.verified)", "site-common.js?v=20260901-8", "Legacy fallback path",
    ),
    "site-common.js": (
        "window.focusChristSourceIntegrity", "isScriptureDependent",
        "unreviewed-source-dependent-generation", "ungrounded-scripture-citation",
        "ungrounded-scripture-attribution", "study-intelligence-v3.js?v=20260901-8",
    ),
    "study-intelligence-v3.js": (
        "if (localReference.found && localReference.verified)", "groundedLocalReference",
        "Unreviewed legacy Q&A entries are quarantined", "verifiedIntentMatches",
        "isScriptureDependent(query)", "retrieval-researched-and-verified",
        "serverVerified: researched.serverVerified",
    ),
    "pioneer-experience.js": (
        "serverVerified: serverVerified",
        "retrieval-researched-and-verified",
        "renderPioneerChoices",
    ),
    "groq-proxy/src/index.js": (
        "SERVER RESEARCH AND SOURCE-INTEGRITY POLICY", "ALLOWED_ORIGINS", "guardVerifiedAnswer",
        "SOURCE_POLICY_VERSION = '2026-09-01.8'",
        "retrieval-researched-and-verified", "execute web search", "compound-mini",
        "churchofjesuschrist.org",
    ),
}
errors = []
for filename, markers in required_by_file.items():
    for marker in markers:
        if marker not in texts[filename]:
            errors.append(f"{filename} missing {marker}")

common = texts["site-common.js"]
if "appendScript('study-intelligence.js" in common or "appendScript('study-intelligence-v2.js" in common:
    errors.append("site-common.js still loads unsafe intermediate Study Intelligence owners")

for false_claim in (
    'red light that "shines upon the righteous"',
    "Black represents the lowest degree of glory", "Red represents the highest degree",
):
    if false_claim in texts["ask.html"]:
        errors.append(f"known false claim present: {false_claim}")

if errors:
    raise SystemExit("Scripture grounding QA failed:\n - " + "\n - ".join(errors))
print("Scripture grounding QA PASS")
