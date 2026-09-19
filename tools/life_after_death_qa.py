"""Static release contract for the enriched Life After Death study.

This validates integration and hash-bound review records. It does not substitute
for direct artwork review or desktop/phone interaction checks.
"""
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGE = "answers/what-happens-after-death.html"
GROUPS = {"new-testament": 5, "third-nephi": 8, "modern": 5}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Node:
    def __init__(self, tag="root", attrs=()):
        self.tag, self.attrs, self.children, self.words = tag, dict(attrs), [], []

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def has(self, name):
        return name in (self.attrs.get("class") or "").split()


class Parser(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].words.append(data)


def check():
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(f"Life After Death: {message}")

    page = ROOT / PAGE
    text = page.read_text(encoding="utf-8")
    nodes = list(Parser(text).root.walk())
    figures = [n for n in nodes if n.tag == "figure" and "data-life-after-death-art" in n.attrs]
    require(len(figures) == 18, "requires 18 new reviewed Christ figures")
    require(Counter(n.attrs.get("data-life-art-group") for n in figures) == Counter(GROUPS), "requires 5 New Testament, 8 Third Nephi and 5 modern figures")
    require(not re.search(r"LIFE_(?:ART|RESOURCE)_|\b(?:TODO|PLACEHOLDER)\b", text), "unresolved artwork/resource placeholder")
    require(any(n.tag == 'a' and n.attrs.get('data-hero-record') == 'topic-life-after-death' and n.attrs.get('href') == '../assets/heroes/topics/life-after-death-full.webp' for n in nodes), "unique Life After Death hero reference missing")
    require(any(n.tag == "header" and n.has("fc-topic-opening") for n in nodes), "original opening structure missing")
    require(any(n.attrs.get("data-focuschrist-header") == "standard" for n in nodes), "standard header missing")
    for asset in ("topic-artwork-details.js", "topic-artwork-details.css"):
        require(any(asset in (n.attrs.get("src") or n.attrs.get("href") or "") for n in nodes), f"required study asset missing: {asset}")
    ids = [n.attrs["id"] for n in nodes if n.attrs.get("id")]
    require(len(ids) == len(set(ids)), "duplicate HTML IDs")
    for n in nodes:
        href = n.attrs.get("href") or ""
        if href.startswith("#"):
            require(href[1:] in ids, f"unresolved section link {href}")
    navs = [n for n in nodes if n.tag == "nav" and n.has("fc-study-nav")]
    require(len(navs) == 1 and len([n for n in navs[0].walk() if n.tag == "a"]) >= 10, "requires ten reading-navigation stops")
    require(len([n for n in nodes if n.tag == "details"]) >= 6, "requires substantive guided reflections")
    cards = [n for n in nodes if n.tag == "article" and n.has("fc-resource-card")]
    require(len(cards) == 9, "requires nine official resource thumbnail cards")
    resource_keys = [n.attrs.get("data-resource-key") for n in cards]
    require(all(resource_keys) and len(set(resource_keys)) == len(resource_keys), "resource cards need distinct keys")
    for card in cards:
        wrappers = [n for n in card.walk() if n.has("fc-resource-card__image")]
        require(len(wrappers) == 1, "resource thumbnail requires shared containment wrapper")
        if wrappers:
            require(urlsplit(wrappers[0].attrs.get("href") or "").netloc == "www.churchofjesuschrist.org", "resource thumbnail must open its official Church source")

    manifest_path = ROOT / "docs/life-after-death-art-review.json"
    if not manifest_path.is_file():
        errors.append("Life After Death: artwork review manifest missing")
        return errors
    entries = json.loads(manifest_path.read_text(encoding="utf-8")).get("artworks", [])
    require(len(entries) == 18, "requires 18 artwork review records")
    require(Counter(e.get("group") for e in entries) == Counter(GROUPS), "review groups differ from required groups")
    for field in ("key", "asset", "thumbnail", "source_sha256", "sha256"):
        values = [e.get(field) for e in entries]
        require(all(values) and len(set(values)) == len(values), f"review {field} values must be present and unique")
    by_asset = {e.get("asset"): e for e in entries}
    page_assets, pixel_hashes = [], []
    for figure in figures:
        descendants = list(figure.walk())
        anchors = [n for n in descendants if n.tag == "a" and (n.attrs.get("href") or "").endswith(".webp")]
        images = [n for n in descendants if n.tag == "img"]
        require(len(anchors) == 1 and len(images) == 1, "each new figure needs one local artwork trigger and image")
        if len(anchors) != 1 or len(images) != 1:
            continue
        trigger, image = anchors[0], images[0]
        require("data-full-image-viewer" not in trigger.attrs, "new artwork must open the study panel first")
        full = (page.parent / urlsplit(trigger.attrs["href"]).path).resolve()
        thumb = (page.parent / urlsplit(image.attrs.get("src") or "").path).resolve()
        if not full.is_relative_to(ROOT) or not thumb.is_relative_to(ROOT):
            require(False, "artwork path escapes repository")
            continue
        asset = full.relative_to(ROOT).as_posix()
        page_assets.append(asset)
        entry = by_asset.get(asset)
        require(bool(entry), f"unreviewed artwork {asset}")
        if not entry:
            continue
        require(entry.get("group") == figure.attrs.get("data-life-art-group"), f"review/page group mismatch {asset}")
        require(entry.get("reviewed") is True and bool(entry.get("review")), f"direct visual review not recorded {asset}")
        require(re.fullmatch(r"[0-9a-f]{64}", entry.get("source_sha256") or "") is not None, f"source lineage hash missing {asset}")
        require(entry.get("thumbnail") == thumb.relative_to(ROOT).as_posix(), f"thumbnail differs from review {asset}")
        require(full.is_file() and thumb.is_file(), f"artwork files missing {asset}")
        if not full.is_file() or not thumb.is_file():
            continue
        require(hashlib.sha256(full.read_bytes()).hexdigest() == entry.get("sha256"), f"art changed after review {asset}")
        with Image.open(full) as full_image, Image.open(thumb) as thumb_image:
            require(full_image.format == "WEBP" and thumb_image.format == "WEBP", f"responsive art must use WebP {asset}")
            try:
                width, height = int(image.attrs.get("width", 0)), int(image.attrs.get("height", 0))
            except ValueError:
                width, height = 0, 0
            require((width, height) in (full_image.size, thumb_image.size), f"intrinsic dimensions mismatch {asset}")
            require(abs(full_image.width / full_image.height - thumb_image.width / thumb_image.height) < .01, f"responsive aspect ratios differ {asset}")
            require(thumb_image.width < full_image.width, f"thumbnail must be a smaller variant {asset}")
            pixel_hashes.append(hashlib.sha256(full_image.convert("RGB").tobytes()).hexdigest())
        srcset = image.attrs.get("srcset") or ""
        require(trigger.attrs["href"] in srcset and image.attrs["src"] in srcset and bool(image.attrs.get("sizes")), f"responsive image choices missing {asset}")
        require(image.attrs.get("loading") == "lazy" and bool(image.attrs.get("alt")), f"alt text or lazy loading missing {asset}")
        scriptures = [n for n in descendants if n.tag == "a" and "/study/scriptures/" in (n.attrs.get("href") or "")]
        require(bool(scriptures), f"picture lacks scripture study action {asset}")
        for link in scriptures:
            u = urlsplit(link.attrs["href"])
            selection = parse_qs(u.query).get("id", [""])[0]
            require(u.netloc == "www.churchofjesuschrist.org" and re.fullmatch(r"p\d+(?:-p\d+)?", selection) is not None, f"picture scripture must select exact verses {asset}")
            if selection:
                require(u.fragment == selection.split("-")[0], f"scripture fragment/range mismatch {asset}")
                chapter = ROOT / "scripture-data" / (u.path.removeprefix("/study/scriptures/") + ".json")
                require(chapter.is_file(), f"canonical scripture chapter unavailable {asset}")
                if chapter.is_file():
                    verses = json.loads(chapter.read_text(encoding="utf-8")).get("verses", [])
                    numbers = [int(number) for number in re.findall(r"\d+", selection)]
                    require(bool(numbers) and 1 <= numbers[0] <= numbers[-1] <= len(verses), f"scripture range is outside chapter {asset}")
    require(len(set(page_assets)) == len(page_assets) and set(page_assets) == set(by_asset), "page/review artwork inventories differ or repeat")
    require(len(set(pixel_hashes)) == len(pixel_hashes), "duplicate decoded image pixels among new artworks")
    for other in ROOT.rglob("*.html"):
        if other == page or ".git" in other.parts:
            continue
        other_text = other.read_text(encoding="utf-8", errors="replace")
        references = set()
        for node in Parser(other_text).root.walk():
            values = [node.attrs.get("href") or "", node.attrs.get("src") or ""]
            values.extend(part.strip().split()[0] for part in (node.attrs.get("srcset") or "").split(",") if part.strip())
            for value in values:
                url = urlsplit(value)
                if not url.path or value.startswith(("#", "data:")):
                    continue
                if url.scheme or url.netloc:
                    if url.netloc not in ("focuschrist.com", "www.focuschrist.com"):
                        continue
                    target = (ROOT / url.path.lstrip("/")).resolve()
                else:
                    target = ((ROOT / url.path.lstrip("/")) if url.path.startswith("/") else (other.parent / url.path)).resolve()
                references.add(target)
        for asset in page_assets:
            require((ROOT / asset).resolve() not in references, f"exclusive artwork also referenced in {other.relative_to(ROOT)}: {asset}")
    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        print("Life After Death QA failed:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print("Life After Death QA passed: 18 reviewed exclusive artworks (5 New Testament, 8 Third Nephi, 5 modern), 9 official resources, responsive assets, scripture actions and reading journey.")
