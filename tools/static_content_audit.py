#!/usr/bin/env python3
"""Validate the semantic-audit ledger against published static HTML content.

The ledger is a human-reviewed approval record. This script does not pretend
that hashing proves a religious or historical claim. It makes the human review
durable by invalidating approval whenever buyer/visitor-visible wording changes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from joseph_research_acceptance import check_no_repeated_artwork_disclosure, check_caption_evidence_metacommentary


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "content-audit.json"
SKIP_TAGS = {"script", "style", "svg", "noscript", "template"}
PUBLISHED_ATTRIBUTES = ("alt", "aria-label", "placeholder", "title")
VALID_STATUSES = {"verified", "non-source-dependent"}

# These reviewed map narratives live inside inline JavaScript. Keep their binding
# separate from static text and require it even when a ledger field is removed.
INLINE_SCRIPT_ROUTES = frozenset({
    "timelines/life-of-christ-journey-map.html",
    "timelines/latter-day-saint-church-history-timeline.html",
    "timelines/willie-and-martin-handcart-map.html",
})



class PublishedTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.stack.append(tag)
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        values = {key.lower(): value or "" for key, value in attrs}
        for name in PUBLISHED_ATTRIBUTES:
            if values.get(name):
                self.parts.append(values[name])
        if tag == "input" and values.get("type", "").lower() in {"button", "submit", "reset"}:
            self.parts.append(values.get("value", ""))
        if tag == "meta":
            identity = (values.get("name") or values.get("property") or "").lower()
            if identity in {"description", "og:title", "og:description", "twitter:title", "twitter:description"}:
                self.parts.append(values.get("content", ""))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth:
            self.parts.append("\n")
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def published_text(path: Path) -> str:
    parser = PublishedTextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    text = html.unescape(" ".join(parser.parts))
    return re.sub(r"\s+", " ", text).strip()


def content_hash(path: Path) -> str:
    return hashlib.sha256(published_text(path).encode("utf-8")).hexdigest()



class InlineScriptParser(HTMLParser):
    """Locate whole inline script elements without normalizing their raw bytes."""

    def __init__(self, raw: bytes) -> None:
        super().__init__(convert_charrefs=False)
        # Latin-1 is a one-to-one byte mapping; offsets also preserve CRLF.
        self.raw = raw
        self.line_offsets = [0]
        self.line_offsets.extend(match.end() for match in re.finditer(b"\n", raw))
        self.start: int | None = None
        self.blocks: list[bytes] = []

    def byte_offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script" and not any(key.lower() == "src" for key, _ in attrs):
            self.start = self.byte_offset()

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.start is not None:
            end = self.raw.find(b">", self.byte_offset())
            if end < 0:
                raise ValueError("unterminated inline script closing tag")
            self.blocks.append(self.raw[self.start:end + 1])
            self.start = None


def inline_script_hash(path: Path) -> str:
    raw = path.read_bytes()
    parser = InlineScriptParser(raw)
    parser.feed(raw.decode("latin-1"))
    parser.close()
    if parser.start is not None:
        raise ValueError("unterminated inline script")
    digest = hashlib.sha256(b"focus-inline-scripts-v1\0")
    digest.update(len(parser.blocks).to_bytes(8, "big"))
    for block in parser.blocks:
        digest.update(len(block).to_bytes(8, "big"))
        digest.update(block)
    return digest.hexdigest()


def html_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_ledger() -> dict:
    if not LEDGER.exists():
        return {"version": 1, "documents": []}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def print_inventory() -> int:
    for path in html_files():
        text = published_text(path)
        print(json.dumps({
            "path": relative(path),
            "sha256": content_hash(path),
            "characters": len(text),
            "lines": text.count("\n") + (1 if text else 0),
        }, ensure_ascii=False))
    return 0


def validate() -> int:
    ledger = load_ledger()
    records = ledger.get("documents")
    if not isinstance(records, list):
        print("STATIC CONTENT AUDIT FAIL: ledger documents must be a list", file=sys.stderr)
        return 1

    record_paths = [record.get("path") for record in records if isinstance(record, dict)]
    duplicate_paths = sorted(path for path, count in Counter(record_paths).items() if path and count > 1)
    by_path = {record.get("path"): record for record in records if isinstance(record, dict)}
    actual = {relative(path): path for path in html_files()}
    errors: list[str] = []

    if duplicate_paths:
        errors.append("duplicate ledger paths: " + ", ".join(duplicate_paths))

    missing = sorted(set(actual) - set(by_path))
    extra = sorted(set(by_path) - set(actual))
    if missing:
        errors.append("unreviewed HTML files: " + ", ".join(missing))
    if extra:
        errors.append("ledger paths no longer present: " + ", ".join(extra))

    for name, path in actual.items():
        try:
            # Published extraction includes visible copy and accessible text.
            # Exact rejected phrases only: shared footer and substantive source
            # or geographic uncertainty are not blanket-banned vocabulary.
            check_no_repeated_artwork_disclosure(published_text(path))
            for caption in re.findall(r'<figcaption\b[^>]*>(.*?)</figcaption>', path.read_text(encoding='utf-8'), flags=re.S|re.I):
                check_caption_evidence_metacommentary(html.unescape(re.sub(r'<[^>]+>', ' ', caption)))
        except AssertionError as exc:
            errors.append(f"{name}: {exc}")
        record = by_path.get(name)
        if not record:
            continue
        status = record.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{name}: invalid or incomplete audit status {status!r}")
        if status == "verified":
            sources = record.get("authoritative_sources")
            if not isinstance(sources, list) or not sources:
                errors.append(f"{name}: verified content requires authoritative_sources")
            elif any(not isinstance(source, str) or not source.strip() for source in sources):
                errors.append(f"{name}: authoritative_sources must contain non-empty strings")
        if not record.get("reviewed_on") or not record.get("review_standard"):
            errors.append(f"{name}: missing review date or standard")
        if name in INLINE_SCRIPT_ROUTES:
            try:
                script_hash = inline_script_hash(path)
                if record.get("reviewed_inline_script_sha256") != script_hash:
                    errors.append(f"{name}: inline script review missing or changed after review "
                                  f"(expected {record.get('reviewed_inline_script_sha256')}, actual {script_hash})")
            except ValueError as exc:
                errors.append(f"{name}: {exc}")
        actual_hash = content_hash(path)
        if record.get("published_text_sha256") != actual_hash:
            errors.append(f"{name}: published wording changed after review (expected {record.get('published_text_sha256')}, actual {actual_hash})")

    if errors:
        print("STATIC CONTENT AUDIT FAIL")
        for error in errors:
            print("- " + error)
        return 1

    verified = sum(1 for record in records if record.get("status") == "verified")
    nonsource = sum(1 for record in records if record.get("status") == "non-source-dependent")
    print(f"STATIC CONTENT AUDIT PASS: {len(records)} documents ({verified} verified, {nonsource} non-source-dependent)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", action="store_true", help="print normalized published-content hashes")
    args = parser.parse_args()
    if args.inventory:
        return print_inventory()
    return validate()


if __name__ == "__main__":
    raise SystemExit(main())
