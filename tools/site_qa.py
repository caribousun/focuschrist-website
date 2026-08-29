from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CORE = {
    "index.html": "https://focuschrist.com/",
    "ask.html": "https://focuschrist.com/ask.html",
    "art.html": "https://focuschrist.com/art.html",
    "pioneers.html": "https://focuschrist.com/pioneers.html",
    "about.html": "https://focuschrist.com/about.html",
}
OLD_MODEL = "llama-3.1-8b-instant"
NEW_MODEL = "openai/gpt-oss-20b"
VERIFICATION_FILE = "google3fa84a4b37862f36.html"


class RefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[tuple[str, str, dict[str, str]]] = []
        self.images: list[dict[str, str]] = []
        self.blank_links: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        data = {k: (v or "") for k, v in attrs}
        if tag == "img":
            self.images.append(data)
            if data.get("src"):
                self.refs.append((tag, data["src"], data))
        elif tag == "script" and data.get("src"):
            self.refs.append((tag, data["src"], data))
        elif tag == "link" and data.get("href"):
            self.refs.append((tag, data["href"], data))
        elif tag == "a" and data.get("href"):
            self.refs.append((tag, data["href"], data))
            if data.get("target") == "_blank":
                self.blank_links.append(data)


def fail(errors: list[str], message: str):
    errors.append(message)


def local_path_for(ref: str) -> Path | None:
    ref = ref.strip()
    if not ref or ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(ref)
    if parsed.scheme or parsed.netloc:
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None
    if clean.startswith("/"):
        clean = clean[1:]
    return ROOT / clean


def main() -> int:
    errors: list[str] = []

    # No zero-byte production media is allowed.
    for media_path in ROOT.rglob("*"):
        if media_path.is_file() and media_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            if media_path.stat().st_size == 0:
                fail(errors, f"Zero-byte media file detected: {media_path.relative_to(ROOT).as_posix()}")

    for filename, canonical in CORE.items():
        path = ROOT / filename
        if not path.exists() or path.stat().st_size == 0:
            fail(errors, f"{filename}: missing or empty")
            continue
        text = path.read_text(encoding="utf-8")

        if text.count("<title>") != 1:
            fail(errors, f"{filename}: expected exactly one <title>")
        if f'<link rel="canonical" href="{canonical}">' not in text:
            fail(errors, f"{filename}: canonical URL missing or incorrect")
        if text.count('data-focuschrist-independence="footer"') != 1:
            fail(errors, f"{filename}: independence footer disclosure missing/duplicated")
        if text.count('<script src="site-common.js" defer></script>') != 1:
            fail(errors, f"{filename}: shared interaction controller missing/duplicated")
        if 'aria-controls="hamburgerMenu"' not in text:
            fail(errors, f"{filename}: hamburger ARIA controls missing")

        parser = RefParser()
        try:
            parser.feed(text)
        except Exception as exc:
            fail(errors, f"{filename}: HTML parser error: {exc}")
            continue

        for tag, ref, _attrs in parser.refs:
            local = local_path_for(ref)
            if local is None:
                continue
            # Directory/root links resolve to index.html.
            if ref in ("/", "./"):
                local = ROOT / "index.html"
            if not local.exists():
                fail(errors, f"{filename}: broken local {tag} reference: {ref}")
            elif local.is_file() and local.stat().st_size == 0:
                fail(errors, f"{filename}: referenced zero-byte file: {ref}")

        for attrs in parser.blank_links:
            rel = set(attrs.get("rel", "").lower().split())
            if "noopener" not in rel:
                fail(errors, f"{filename}: target=_blank link missing rel=noopener: {attrs.get('href')}")

    common = ROOT / "site-common.js"
    if not common.exists() or common.stat().st_size == 0:
        fail(errors, "site-common.js missing or empty")
        common_text = ""
    else:
        common_text = common.read_text(encoding="utf-8")
        for marker in ("initNavigation", "initPioneerDisclosures", "aria-expanded", "aria-live"):
            if marker not in common_text:
                fail(errors, f"site-common.js missing required behavior marker: {marker}")

    ask = (ROOT / "ask.html").read_text(encoding="utf-8")
    pioneers = (ROOT / "pioneers.html").read_text(encoding="utf-8")
    about = (ROOT / "about.html").read_text(encoding="utf-8")
    art = (ROOT / "art.html").read_text(encoding="utf-8")

    if 'onclick="expandTimelineItem' in pioneers or 'onclick="expandTrailPoint' in pioneers:
        fail(errors, "Pioneers legacy inline expansion handlers detected")
    if pioneers.count('data-focus-expand="timeline"') < 8:
        fail(errors, "Pioneers timeline disclosure metadata unexpectedly missing")
    if pioneers.count('data-focus-expand="trail"') < 8:
        fail(errors, "Pioneers trail disclosure metadata unexpectedly missing")
    if pioneers.count('role="button" tabindex="0" aria-expanded="false"') < 16:
        fail(errors, "Pioneers disclosure keyboard/ARIA attributes unexpectedly missing")

    if OLD_MODEL in ask or OLD_MODEL in pioneers:
        fail(errors, "Retired Groq model reintroduced into Ask/Pioneers")
    if NEW_MODEL not in ask or NEW_MODEL not in pioneers:
        fail(errors, "Current Groq model missing from Ask/Pioneers")
    if ask.count('data-focuschrist-ai-notice="true"') != 1:
        fail(errors, "Ask AI/privacy transparency notice missing/duplicated")
    if "d.innerHTML" in ask or "message.innerHTML" in ask:
        fail(errors, "Ask unsafe legacy message renderer detected")
    if "document.createTextNode" not in ask:
        fail(errors, "Ask safe text renderer not detected")
    if "AI-assisted responses are study aids and may contain errors" not in about:
        fail(errors, "About AI/source transparency language missing")
    if about.count('data-focuschrist-independence="about"') != 1:
        fail(errors, "About independence section missing/duplicated")

    art_parser = RefParser()
    art_parser.feed(art)
    gallery_imgs = [img for img in art_parser.images if img.get("src") and img.get("id") != "modalImage"]
    if len(gallery_imgs) < 38:
        fail(errors, f"Art gallery unexpectedly contains only {len(gallery_imgs)} images")
    for img in gallery_imgs:
        if not img.get("alt", "").strip():
            fail(errors, f"Art image missing alt text: {img.get('src')}")
        if img.get("loading") != "lazy":
            fail(errors, f"Art image missing loading=lazy: {img.get('src')}")
        if img.get("decoding") != "async":
            fail(errors, f"Art image missing decoding=async: {img.get('src')}")
    if art.count('data-focuschrist-art-accessibility="true"') != 1:
        fail(errors, "Art accessibility helper missing/duplicated")

    local_full_pairs = [img for img in gallery_imgs if img.get("data-full-src", "").startswith("art/")]
    if len(local_full_pairs) < 27:
        fail(errors, f"Expected at least 27 local thumbnail/full-resolution Art pairs, found {len(local_full_pairs)}")
    for img in local_full_pairs:
        thumb_src = img.get("src", "")
        full_src = img.get("data-full-src", "")
        if not thumb_src.startswith("art/thumbs/") or not thumb_src.endswith(".webp"):
            fail(errors, f"Local Art preview is not a WebP thumbnail: {thumb_src}")
        thumb_path = ROOT / thumb_src
        full_path = ROOT / full_src
        if not thumb_path.exists() or thumb_path.stat().st_size == 0:
            fail(errors, f"Missing/empty Art thumbnail: {thumb_src}")
        if not full_path.exists() or full_path.stat().st_size == 0:
            fail(errors, f"Missing/empty full-resolution Art source: {full_src}")

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists() or sitemap.stat().st_size == 0:
        fail(errors, "sitemap.xml missing or empty")
    else:
        try:
            tree = ET.parse(sitemap)
            locs = {node.text.strip() for node in tree.findall('.//{*}loc') if node.text}
            for canonical in CORE.values():
                if canonical not in locs:
                    fail(errors, f"sitemap.xml missing {canonical}")
        except Exception as exc:
            fail(errors, f"sitemap.xml parse failure: {exc}")

    robots = ROOT / "robots.txt"
    if not robots.exists() or "sitemap.xml" not in robots.read_text(encoding="utf-8").lower():
        fail(errors, "robots.txt missing sitemap declaration")

    verification = ROOT / VERIFICATION_FILE
    if not verification.exists() or not verification.read_text(encoding="utf-8").strip().startswith("google-site-verification:"):
        fail(errors, "Google Search Console verification file missing or malformed")

    page404 = ROOT / "404.html"
    if not page404.exists() or page404.stat().st_size == 0:
        fail(errors, "404.html missing or empty")
    else:
        text404 = page404.read_text(encoding="utf-8")
        for target in ("index.html", "ask.html", "art.html", "pioneers.html", "about.html"):
            if f'href="{target}"' not in text404:
                fail(errors, f"404.html missing recovery link to {target}")

    if errors:
        print("FocusChrist SITE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("FocusChrist SITE QA PASSED")
    print(f"Core pages checked: {len(CORE)}")
    print(f"Art gallery images checked: {len(gallery_imgs)}")
    print("Search Console verification, sitemap, local references, model migration, disclosures, accessibility markers, and Ask rendering verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
