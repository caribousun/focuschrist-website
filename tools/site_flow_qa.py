#!/usr/bin/env python3
"""Verify complete public-route continuity, internal links and fragment targets."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
DYNAMIC_EMPTY_LINK_IDS = {
    "artworkDetailSource",
    "artworkDetailFullImage",
    "missionaryDetailSource",
    "missionaryDetailFullImage",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
        if tag.lower() == "a" and "href" in values:
            self.links.append((values["href"].strip(), values.get("id", ""), tag.lower()))


def sitemap_pages() -> list[Path]:
    tree = ET.parse(SITEMAP)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    pages: list[Path] = []
    for location in tree.findall("sm:url/sm:loc", namespace):
        url = urlsplit((location.text or "").strip())
        relative = url.path.lstrip("/") or "index.html"
        pages.append((ROOT / relative).resolve())
    return pages


def main() -> int:
    pages = sitemap_pages()
    errors: list[str] = []
    parsed: dict[Path, PageParser] = {}

    for page in pages:
        if not page.exists():
            errors.append(f"sitemap route has no file: {page.relative_to(ROOT)}")
            continue
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page] = parser

    for page, parser in parsed.items():
        relative = page.relative_to(ROOT).as_posix()
        local_destinations: set[Path] = set()
        for href, element_id, _tag in parser.links:
            if not href or href == "#":
                if element_id not in DYNAMIC_EMPTY_LINK_IDS:
                    errors.append(f"{relative}: non-navigating link {href!r} ({element_id or 'no id'})")
                continue

            split = urlsplit(href)
            if split.scheme or href.startswith("//") or href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue

            raw_path = unquote(split.path)
            target = (ROOT / raw_path.lstrip("/")).resolve() if raw_path.startswith("/") else (page.parent / raw_path).resolve()
            if not raw_path:
                target = page
            if target.is_dir():
                target = target / "index.html"
            if not target.suffix:
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{relative}: missing internal target {href}")
                continue

            if target.suffix.lower() == ".html":
                local_destinations.add(target)
                if split.fragment:
                    target_parser = parsed.get(target)
                    if target_parser is None:
                        target_parser = PageParser()
                        target_parser.feed(target.read_text(encoding="utf-8"))
                    fragment = unquote(split.fragment)
                    if fragment not in target_parser.ids:
                        errors.append(f"{relative}: missing fragment target {href}")

        outward = {target for target in local_destinations if target != page}
        if len(outward) < 2:
            errors.append(f"{relative}: fewer than two local continuation destinations")

    if errors:
        print("SITE FLOW QA FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"SITE FLOW QA PASS: {len(pages)} sitemap routes, complete internal targets and fragments, "
        "no inert public links, and multiple continuation paths per page"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
