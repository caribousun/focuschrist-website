from __future__ import annotations

from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/art-study-image-review.json"
PAGES = (
    "art-study/the-living-christ.html",
    "art-study/the-good-shepherd.html",
    "art-study/suffer-the-little-children.html",
    "art-study/be-still.html",
)


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.nav_hrefs: list[str] = []
        self.in_study_nav = 0
        self.in_art_story = 0
        self.in_figcaption = 0
        self.figures = 0
        self.details = 0
        self.resource_cards = 0
        self.continuation_cards = 0
        self.in_continuation = 0
        self.full_assets: list[str] = []
        self.thumb_assets: list[str] = []
        self.links: list[str] = []
        self.captions: list[list[str]] = []
        self.caption_links: list[list[str]] = []
        self.direct_viewers = 0
        self.featured_destinations: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        data = {key: value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "nav" and "fc-study-nav" in classes:
            self.in_study_nav += 1
        if tag == "section" and data.get("id") == "continue-study":
            self.in_continuation += 1
        if tag == "figure" and "fc-art-story" in classes:
            self.figures += 1
            self.in_art_story += 1
        if tag == "details":
            self.details += 1
        if tag == "article" and "fc-resource-card" in classes:
            self.resource_cards += 1
        if tag == "article" and self.in_continuation:
            self.continuation_cards += 1
        if tag == "a" and data.get("href"):
            href = data["href"]
            self.links.append(href)
            if self.in_study_nav:
                self.nav_hrefs.append(href)
            if "data-artwork-detail" in data and href.startswith("art-study/"):
                self.featured_destinations.append(href)
            if self.in_art_story and "data-full-image-viewer" in data:
                self.direct_viewers += 1
            if self.in_art_story and "data-art-study-supporting" in data:
                self.full_assets.append(href)
            if self.in_figcaption and self.captions:
                self.caption_links[-1].append(href)
        if tag == "img" and self.in_art_story and data.get("src"):
            self.thumb_assets.append(data["src"])
        if tag == "figcaption" and self.in_art_story:
            self.in_figcaption += 1
            self.captions.append([])
            self.caption_links.append([])

    def handle_data(self, data: str) -> None:
        if self.captions and self.in_art_story:
            value = " ".join(data.split())
            if value:
                self.captions[-1].append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_study_nav:
            self.in_study_nav -= 1
        if tag == "figure" and self.in_art_story:
            self.in_art_story -= 1
        if tag == "figcaption" and self.in_figcaption:
            self.in_figcaption -= 1
        if tag == "section" and self.in_continuation:
            self.in_continuation -= 1


def local_target(page: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or href.startswith(('#', 'mailto:', 'tel:')):
        return None
    return (page.parent / parsed.path).resolve()


def main() -> int:
    errors: list[str] = []
    gallery = AuditParser()
    gallery.feed((ROOT / "art.html").read_text(encoding="utf-8"))
    if set(gallery.featured_destinations) != set(PAGES) or len(gallery.featured_destinations) != len(PAGES):
        errors.append("Featured Art & Study destinations differ from the complete audited page inventory")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reviewed_pages = manifest.get("pages", {})
    required = manifest.get("standard", {}).get("supporting_visuals_per_page")
    if required != 4:
        errors.append("review manifest must require four supporting visuals per page")
    reference = ROOT / manifest.get("standard", {}).get("identity_reference", "")
    if not reference.is_file():
        errors.append("approved Home identity reference is missing")

    all_full_assets: list[str] = []
    html_pages = [
        path.read_text(encoding="utf-8", errors="replace")
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts
    ]

    for relative in PAGES:
        page = ROOT / relative
        text = page.read_text(encoding="utf-8")
        parser = AuditParser()
        parser.feed(text)
        parser.close()
        if parser.direct_viewers:
            errors.append(f"{relative}: supporting pictures must open study options before the full-image viewer")
        for asset in ("topic-artwork-details.js", "topic-artwork-details.css"):
            if not re.search(r'(?:src|href)="\.\./' + re.escape(asset) + r'(?:\?[^\"]*)?"', text):
                errors.append(f"{relative}: missing required picture study asset {asset}")

        for marker in (
            'data-art-study-enriched="true"',
            'href="../art-study-enrichment.css?v=20260908-complete"',
            'class="fc-study-opening"',
            'class="fc-art-meditation"',
            'class="fc-reflection-prompts"',
            'class="fc-source-panel"',
            'class="fc-continuation-grid"',
        ):
            if marker not in text:
                errors.append(f"{relative}: missing enrichment marker {marker}")

        if len(parser.nav_hrefs) != 6:
            errors.append(f"{relative}: expected 6 study navigation stops, found {len(parser.nav_hrefs)}")
        for href in parser.nav_hrefs:
            if not href.startswith("#") or href[1:] not in parser.ids:
                errors.append(f"{relative}: navigation target does not exist: {href}")
        if parser.figures != 4 or len(parser.full_assets) != 4 or len(parser.thumb_assets) != 4:
            errors.append(f"{relative}: requires exactly four interactive supporting artworks")
        if parser.details < 3:
            errors.append(f"{relative}: requires at least three guided reflection prompts")
        if parser.resource_cards < 2:
            errors.append(f"{relative}: requires at least two visual official resources")
        if parser.continuation_cards != 3:
            errors.append(f"{relative}: requires exactly three onward study cards")
        church_links = [href for href in parser.links if href.startswith("https://www.churchofjesuschrist.org/")]
        if len(church_links) < 8:
            errors.append(f"{relative}: expected at least 8 official scripture or Church links, found {len(church_links)}")
        if len(parser.captions) != 4 or any(len(" ".join(parts).split()) < 18 for parts in parser.captions):
            errors.append(f"{relative}: every supporting artwork needs a substantive image-specific caption")
        if len(parser.caption_links) != 4 or any(
            not any(href.startswith("https://www.churchofjesuschrist.org/") for href in links)
            for links in parser.caption_links
        ):
            errors.append(f"{relative}: every supporting artwork caption needs an official scripture or Church link")

        entries = reviewed_pages.get(relative, [])
        reviewed_assets = ["../" + entry.get("asset", "") for entry in entries]
        if len(entries) != 4 or any(
            not entry.get("reviewed") or not entry.get("tone") or not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", ""))
            for entry in entries
        ):
            errors.append(f"{relative}: four hash-bound expression-and-style review records are required")
        if reviewed_assets != parser.full_assets:
            errors.append(f"{relative}: page artwork does not match the reviewed exclusive-art manifest")

        expected_dimensions = tuple(manifest.get("standard", {}).get("full_image_dimensions", []))
        for entry, full_href, thumb_href in zip(entries, parser.full_assets, parser.thumb_assets):
            full = local_target(page, full_href)
            thumb = local_target(page, thumb_href)
            if not full or not full.is_file() or full.stat().st_size < 90_000:
                errors.append(f"{relative}: missing or undersized full artwork {full_href}")
            elif full:
                full_bytes = full.read_bytes()
                if hashlib.sha256(full_bytes).hexdigest() != entry.get("sha256"):
                    errors.append(f"{relative}: artwork changed after visual review {full_href}")
                else:
                    with Image.open(full) as image:
                        if image.format != manifest.get("standard", {}).get("full_image_format") or image.size != expected_dimensions:
                            errors.append(f"{relative}: full artwork must use the reviewed format and dimensions {full_href}")
            if not thumb or not thumb.is_file() or thumb.stat().st_size < 20_000:
                errors.append(f"{relative}: missing or undersized thumbnail {thumb_href}")
            if full and thumb and full.stem != thumb.stem:
                errors.append(f"{relative}: full artwork and thumbnail names do not match")
            if full_href.startswith("../art/"):
                errors.append(f"{relative}: gallery artwork was reused instead of exclusive page art")
            all_full_assets.append(full_href)

        for href in parser.links:
            target = local_target(page, href)
            if target is None:
                continue
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                errors.append(f"{relative}: broken local destination {href}")

    duplicates = [asset for asset, count in Counter(all_full_assets).items() if count > 1]
    if duplicates:
        errors.append(f"supporting artwork is reused across study pages: {duplicates}")
    for asset in all_full_assets:
        # A responsive image may reference its full source in both href and
        # srcset. Exclusivity concerns owning pages, not references on that page.
        if sum(asset in text for text in html_pages) != 1:
            errors.append(f"exclusive supporting artwork must appear on exactly one page: {asset}")
    if set(reviewed_pages) != set(PAGES):
        errors.append("image review manifest page inventory does not match the featured studies")

    if errors:
        print("Art study enrichment QA failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Art study enrichment QA passed: 4 pages, 20 total visuals, 16 exclusive supporting photographs, 12 reflection prompts, 8 visual resources, and 12 onward study paths verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
