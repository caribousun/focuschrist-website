"""Birth study's static release contract; direct visual/runtime review is separate."""
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlsplit

from PIL import Image
from life_after_death_qa import Parser

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "birth-of-christ.html"


def local_asset(page, value):
    url = urlsplit(value or "")
    if not url.path or (url.netloc and url.netloc not in ("focuschrist.com", "www.focuschrist.com")):
        return None
    if url.scheme and url.scheme not in ("http", "https"):
        return None
    return ((ROOT / url.path.lstrip("/")) if url.path.startswith("/") else (page.parent / url.path)).resolve()


def references(page, nodes):
    result = set()
    for node in nodes:
        values = [node.attrs.get("href"), node.attrs.get("src")]
        values += [part.strip().split()[0] for part in (node.attrs.get("srcset") or "").split(",") if part.strip()]
        for value in values:
            target = local_asset(page, value)
            if target:
                result.add(target)
    return result


def check():
    errors = []
    def require(condition, message):
        if not condition:
            errors.append("Birth of Christ: " + message)

    text = PAGE.read_text(encoding="utf-8")
    nodes = list(Parser(text).root.walk())
    figures = [n for n in nodes if n.tag == "figure" and "data-birth-art" in n.attrs]
    heroes = [n for n in nodes if n.tag == "a" and n.attrs.get("data-hero-record") == "birth-of-christ"]
    require(len(figures) >= 22 and len(heroes) == 1, "requires at least22 body pictures and exactly one unique hero")
    require(not re.search(r"BIRTH_(?:ART|RESOURCE)_|\b(?:TODO|PLACEHOLDER)\b", text), "unresolved integration placeholder")
    for asset in ("topic-artwork-details.js", "topic-artwork-details.css", "hero-details.js"):
        require(any(asset in (n.attrs.get("src") or n.attrs.get("href") or "") for n in nodes), "missing shared interaction asset " + asset)
    require(any(n.tag == "header" and n.has("fc-topic-opening") for n in nodes), "standard opening frame missing")
    ids = [n.attrs["id"] for n in nodes if n.attrs.get("id")]
    require(len(ids) == len(set(ids)), "duplicate HTML IDs")
    for node in nodes:
        href = node.attrs.get("href") or ""
        if href.startswith("#"):
            require(href[1:] in ids, "missing anchor destination " + href)
    navs = [n for n in nodes if n.tag == "nav" and n.has("fc-study-nav")]
    require(len(navs) == 1 and len([n for n in navs[0].walk() if n.tag == "a"]) >= 12, "requires12 reading stops")
    require(len([n for n in nodes if n.tag == "details"]) >= 8, "requires8 guided reflections")
    onward = next((n for n in nodes if n.attrs.get("id") == "continue-study"), None)
    require(onward is not None and len([n for n in onward.walk() if n.tag == "article"]) >= 4, "requires4 onward study cards")
    ask = [n for n in nodes if n.tag == "a" and urlsplit(n.attrs.get("href") or "").path.endswith("ask.html") and parse_qs(urlsplit(n.attrs.get("href") or "").query).get("topic")]
    require(bool(ask), "contextual Ask handoff missing")
    cards = [n for n in nodes if n.tag == "article" and n.has("fc-resource-card")]
    require(len(cards) >= 8, "requires8 official resource cards")
    keys = [n.attrs.get("data-resource-key") for n in cards]
    require(all(keys) and len(set(keys)) == len(keys), "resource keys must be unique")
    for card in cards:
        wrappers = [n for n in card.walk() if n.has("fc-resource-card__image")]
        require(len(wrappers) == 1, "resource requires shared thumbnail containment")
        if wrappers:
            require(urlsplit(wrappers[0].attrs.get("href") or "").netloc == "www.churchofjesuschrist.org", "resource must open its official Church source")

    def scripture(url):
        parsed = urlsplit(url or "")
        params = parse_qs(parsed.query)
        selection = params.get("id", [""])[0]
        valid = parsed.netloc == "www.churchofjesuschrist.org" and parsed.path.startswith("/study/scriptures/") and re.fullmatch(r"p\d+(?:-p\d+)?", selection)
        require(bool(valid), "scripture action must select exact official verses: " + str(url))
        if not valid:
            return
        require(params.get("lang") == ["eng"] and parsed.fragment == selection.split("-")[0], "scripture language/fragment mismatch: " + url)
        chapter = ROOT / "scripture-data" / (parsed.path.removeprefix("/study/scriptures/") + ".json")
        require(chapter.is_file(), "scripture chapter unavailable: " + url)
        if chapter.is_file():
            values = [int(x) for x in re.findall(r"\d+", selection)]
            verses = json.loads(chapter.read_text(encoding="utf-8"))["verses"]
            require(1 <= values[0] <= values[-1] <= len(verses), "scripture selection out of range: " + url)

    for node in nodes:
        if node.tag == "a" and node.has("fc-inline-scripture"):
            scripture(node.attrs.get("href"))
    manifest = ROOT / "docs/birth-of-christ-art-review.json"
    if not manifest.is_file():
        return errors + ["Birth of Christ: artwork review manifest missing"]
    entries = json.loads(manifest.read_text(encoding="utf-8"))["artworks"]
    require(len(entries) >= 23, "requires at least23 reviewed unique artworks")
    for field in ("key", "asset", "thumbnail", "source_sha256", "sha256", "thumbnail_sha256"):
        values = [entry.get(field) for entry in entries]
        require(all(values) and len(set(values)) == len(values), "missing/duplicate review field " + field)
    by_asset = {(ROOT / entry.get("asset", "")).resolve(): entry for entry in entries}
    page_assets = []
    for figure in figures:
        children = list(figure.walk())
        triggers = [n for n in figure.children if n.tag == "a"]
        images = [n for n in children if n.tag == "img"]
        require(len(triggers) == 1 and len(images) == 1, "body figure requires one artwork trigger and image")
        if len(triggers) != 1 or len(images) != 1:
            continue
        trigger, image = triggers[0], images[0]
        full = local_asset(PAGE, trigger.attrs.get("href"))
        thumb = local_asset(PAGE, image.attrs.get("src"))
        page_assets.append(full)
        require("data-full-image-viewer" not in trigger.attrs and trigger.attrs.get("aria-haspopup") == "dialog", "body artwork must open study dialog first")
        require(bool(image.attrs.get("alt")) and image.attrs.get("loading") == "lazy", "body artwork needs alt text and lazy loading")
        srcset = image.attrs.get("srcset") or ""
        require(bool(image.attrs.get("sizes")) and (trigger.attrs.get("href") or "MISSING") in srcset and (image.attrs.get("src") or "MISSING") in srcset, "responsive body variants missing")
        entry = by_asset.get(full)
        require(entry is not None, "body artwork absent from manifest: " + str(full))
        if entry:
            require(thumb == (ROOT / entry["thumbnail"]).resolve(), "body thumbnail differs from reviewed manifest")
            expected = entry.get("scripture", [])
            expected = [expected] if isinstance(expected, str) else expected
            actual = [n.attrs.get("href") for n in children if n.tag == "a" and n.has("fc-inline-scripture")]
            require(bool(expected) and set(expected).issubset(actual), "picture scripture differs from review: " + str(full))
        if full and thumb and full.is_file() and thumb.is_file():
            with Image.open(full) as a, Image.open(thumb) as b:
                try:
                    dimensions = (int(image.attrs.get("width", 0)), int(image.attrs.get("height", 0)))
                except ValueError:
                    dimensions = (0, 0)
                require(dimensions in (a.size, b.size), "body image intrinsic dimensions mismatch")
                require(b.width < a.width and abs(a.width / a.height - b.width / b.height) < .01, "responsive artwork geometry mismatch")
    if heroes:
        hero = local_asset(PAGE, heroes[0].attrs.get("href"))
        require(hero not in page_assets, "hero is repeated as body artwork")
        page_assets.append(hero)
    require(len(page_assets) == len(set(page_assets)) and set(page_assets) == set(by_asset), "page artwork inventory must exactly match review manifest")
    decoded = []
    exclusive = set()
    for entry in entries:
        require(entry.get("reviewed") is True and bool(entry.get("review")), "artwork visual review incomplete: " + str(entry.get("key")))
        owner_approval = entry.get("owner_approval")
        require(isinstance(owner_approval, bool), "owner approval must be recorded explicitly as a boolean")
        if owner_approval is True:
            require(isinstance(entry.get("owner_approval_evidence"), str) and bool(entry["owner_approval_evidence"].strip()), "owner approval requires explicit evidence separate from technical review")
        require(re.fullmatch(r"[0-9a-f]{64}", entry.get("source_sha256") or "") is not None, "source lineage hash missing")
        urls = entry.get("scripture", [])
        urls = [urls] if isinstance(urls, str) else urls
        require(bool(urls), "review scripture evidence missing")
        for url in urls:
            scripture(url)
        for field, hash_field in (("asset", "sha256"), ("thumbnail", "thumbnail_sha256")):
            path = (ROOT / entry.get(field, "")).resolve()
            require(path.is_relative_to(ROOT) and path.is_file(), "missing local reviewed asset: " + str(path))
            if not path.is_relative_to(ROOT) or not path.is_file():
                continue
            exclusive.add(path)
            require(hashlib.sha256(path.read_bytes()).hexdigest() == entry.get(hash_field), "asset changed after review: " + str(path))
            with Image.open(path) as image:
                require(image.format == "WEBP", "published artwork must be WebP")
                if field == "asset":
                    decoded.append(hashlib.sha256(image.convert("RGB").tobytes()).hexdigest())
    require(len(decoded) == len(set(decoded)), "new artwork repeats decoded pixels")
    for other in ROOT.rglob("*.html"):
        if other == PAGE or ".git" in other.parts:
            continue
        reused = references(other, Parser(other.read_text(encoding="utf-8", errors="replace")).root.walk()) & exclusive
        require(not reused, "exclusive artwork reused by " + other.relative_to(ROOT).as_posix() + ": " + str(sorted(reused)))
    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        print("Birth of Christ QA failed:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print("Birth of Christ QA passed: reviewed exclusive hero/body inventory, at least23 artworks, responsive assets, exact scripture actions,12 reading stops,8 reflections,8 official resources and4 onward paths.")
