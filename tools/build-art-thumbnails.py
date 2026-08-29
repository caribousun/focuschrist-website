from pathlib import Path
from html.parser import HTMLParser
from PIL import Image, ImageOps
import re

ROOT = Path(__file__).resolve().parents[1]
ART_HTML = ROOT / "art.html"
THUMB_DIR = ROOT / "art" / "thumbs"
MAX_SIZE = (640, 640)
QUALITY = 82


class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.gallery_depth = 0
        self.local_sources = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "div" and "gallery-item" in data.get("class", "").split():
            self.gallery_depth += 1
        elif tag == "img" and self.gallery_depth:
            src = data.get("src", "")
            if src.startswith("art/") and not src.startswith("art/thumbs/"):
                self.local_sources.append(src)

    def handle_endtag(self, tag):
        if tag == "div" and self.gallery_depth:
            self.gallery_depth -= 1


def thumbnail_name(src: str) -> str:
    return Path(src).stem + ".webp"


def build_thumbnail(source: Path, target: Path):
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {"format": "WEBP", "quality": QUALITY, "method": 6}
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.save(target, **save_kwargs)


def main():
    html = ART_HTML.read_text(encoding="utf-8")
    parser = GalleryParser()
    parser.feed(html)
    sources = list(dict.fromkeys(parser.local_sources))
    if not sources:
        raise RuntimeError("No local gallery images found")

    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    replacements = 0
    original_total = 0
    thumb_total = 0

    for src in sources:
        source = ROOT / src
        if not source.exists() or source.stat().st_size == 0:
            raise RuntimeError(f"Missing or empty source artwork: {src}")
        target_rel = f"art/thumbs/{thumbnail_name(src)}"
        target = ROOT / target_rel
        build_thumbnail(source, target)
        original_total += source.stat().st_size
        thumb_total += target.stat().st_size

        pattern = re.compile(
            rf'<img\s+([^>]*?)src="{re.escape(src)}"([^>]*)>',
            re.I,
        )

        def replace_tag(match):
            nonlocal replacements
            attrs_before = match.group(1)
            attrs_after = match.group(2)
            combined = attrs_before + attrs_after
            if "data-full-src=" in combined:
                raise RuntimeError(f"data-full-src already exists for {src}")
            replacements += 1
            return f'<img {attrs_before}src="{target_rel}" data-full-src="{src}"{attrs_after}>'

        html, count = pattern.subn(replace_tag, html, count=1)
        if count != 1:
            raise RuntimeError(f"Expected one gallery reference for {src}, found {count}")

    old_open = """            galleryImages = Array.from(document.querySelectorAll('.gallery-item img')).map(img => img.src);\n            currentIndex = galleryImages.indexOf(element.querySelector('img').src);"""
    new_open = """            const galleryElements = Array.from(document.querySelectorAll('.gallery-item img'));\n            galleryImages = galleryElements.map(img => img.dataset.fullSrc || img.src);\n            currentIndex = galleryElements.indexOf(element.querySelector('img'));"""
    if old_open in html:
        html = html.replace(old_open, new_open, 1)
    elif new_open not in html:
        raise RuntimeError("Unable to update modal full-resolution source logic")

    ART_HTML.write_text(html, encoding="utf-8")

    if replacements != len(sources):
        raise RuntimeError(f"Expected {len(sources)} replacements, made {replacements}")

    reduction = 100 * (1 - thumb_total / original_total) if original_total else 0
    print(f"Built {len(sources)} local Art thumbnails")
    print(f"Original local gallery bytes: {original_total}")
    print(f"Thumbnail bytes: {thumb_total}")
    print(f"Gallery-transfer reduction for local artwork: {reduction:.1f}%")


if __name__ == "__main__":
    main()
