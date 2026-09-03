#!/usr/bin/env python3
"""Audit current robots and sitemap revision against the approved index."""

from __future__ import annotations

import re

from build_church_source_index import (
    OUTPUT,
    build_entries,
    validate_review_manifest,
)


def committed_value(name: str, content: str) -> str:
    match = re.search(rf"const {re.escape(name)} = \"([^\"]+)\";", content)
    if not match:
        raise RuntimeError(f"Committed index is missing {name}")
    return match.group(1)


def main() -> None:
    content = OUTPUT.read_text(encoding="utf-8")
    approved_robots = committed_value("CHURCH_SOURCE_ROBOTS_SHA256", content)
    approved_revision = committed_value("CHURCH_SOURCE_SITEMAP_REVISION", content)
    approved_sitemaps = committed_value("CHURCH_SOURCE_SITEMAPS_SHA256", content)
    current_revision, current_robots, current_sitemaps, _entries = build_entries()
    if current_robots != approved_robots:
        raise RuntimeError("Official robots.txt changed; review and rebuild the Church source index")
    if current_revision != approved_revision:
        raise RuntimeError(
            f"Official sitemap revision changed from {approved_revision} to {current_revision}; rebuild the index"
        )
    if current_sitemaps != approved_sitemaps:
        raise RuntimeError("Official combined sitemap content changed; review and rebuild the Church source index")
    validate_review_manifest(approved_revision, approved_robots, approved_sitemaps)
    print(f"Church source freshness AUDIT PASS: revision {current_revision}, robots {current_robots[:12]}, sitemaps {current_sitemaps[:12]}")


if __name__ == "__main__":
    main()
