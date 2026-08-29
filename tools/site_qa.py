from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CORE = {
    "index.html": "https://focuschrist.com/",
    "ask.html": "https://focuschrist.com/ask.html",
    "answers.html": "https://focuschrist.com/answers.html",
    "watch.html": "https://focuschrist.com/watch.html",
    "art.html": "https://focuschrist.com/art.html",
    "pioneers.html": "https://focuschrist.com/pioneers.html",
    "about.html": "https://focuschrist.com/about.html",
}
ANSWER_PAGES = {
    "answers/jesus-christ-latter-day-saint-beliefs.html": "https://focuschrist.com/answers/jesus-christ-latter-day-saint-beliefs.html",
    "answers/are-latter-day-saints-christian.html": "https://focuschrist.com/answers/are-latter-day-saints-christian.html",
    "answers/what-is-the-book-of-mormon.html": "https://focuschrist.com/answers/what-is-the-book-of-mormon.html",
    "answers/why-latter-day-saints-build-temples.html": "https://focuschrist.com/answers/why-latter-day-saints-build-temples.html",
    "answers/what-happens-after-death.html": "https://focuschrist.com/answers/what-happens-after-death.html",
    "answers/who-was-joseph-smith.html": "https://focuschrist.com/answers/who-was-joseph-smith.html",
    "answers/prayer-and-personal-revelation.html": "https://focuschrist.com/answers/prayer-and-personal-revelation.html",
    "answers/why-families-are-important.html": "https://focuschrist.com/answers/why-families-are-important.html",
    "answers/bible-and-book-of-mormon-together.html": "https://focuschrist.com/answers/bible-and-book-of-mormon-together.html",
    "answers/faith-in-jesus-christ-during-trials.html": "https://focuschrist.com/answers/faith-in-jesus-christ-during-trials.html",
}
ART_STUDY_PAGES = {
    "art-study/the-living-christ.html": "https://focuschrist.com/art-study/the-living-christ.html",
    "art-study/the-good-shepherd.html": "https://focuschrist.com/art-study/the-good-shepherd.html",
    "art-study/suffer-the-little-children.html": "https://focuschrist.com/art-study/suffer-the-little-children.html",
    "art-study/be-still.html": "https://focuschrist.com/art-study/be-still.html",
}
OLD_MODEL = "llama-3.1-8b-instant"
NEW_MODEL = "openai/gpt-oss-20b"
VERIFICATION_FILE = "google3fa84a4b37862f36.html"
HEADER_PAGES = {
    **{name: "site-header.css" for name in CORE},
    **{name: "../site-header.css" for name in ANSWER_PAGES},
    **{name: "../site-header.css" for name in ART_STUDY_PAGES},
    "404.html": "site-header.css",
}
HEADER_LABELS = ("HOME", "ASK", "ANSWERS", "ART", "PIONEERS", "ABOUT")


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


def local_path_for(ref: str, source_path: Path) -> Path | None:
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
        candidate = ROOT / clean.lstrip("/")
    else:
        candidate = source_path.parent / clean
    try:
        return candidate.resolve()
    except OSError:
        return candidate


def inspect_html(path: Path, errors: list[str], require_noopener: bool = True) -> tuple[str, RefParser]:
    if not path.exists() or path.stat().st_size == 0:
        fail(errors, f"{path.relative_to(ROOT).as_posix()}: missing or empty")
        return "", RefParser()
    text = path.read_text(encoding="utf-8")
    parser = RefParser()
    try:
        parser.feed(text)
    except Exception as exc:
        fail(errors, f"{path.relative_to(ROOT).as_posix()}: HTML parser error: {exc}")
        return text, parser

    for tag, ref, _attrs in parser.refs:
        local = local_path_for(ref, path)
        if local is None:
            continue
        if ref in ("/", "./"):
            local = ROOT / "index.html"
        if not local.exists():
            fail(errors, f"{path.relative_to(ROOT).as_posix()}: broken local {tag} reference: {ref}")
        elif local.is_file() and local.stat().st_size == 0:
            fail(errors, f"{path.relative_to(ROOT).as_posix()}: referenced zero-byte file: {ref}")

    if require_noopener:
        for attrs in parser.blank_links:
            rel = set(attrs.get("rel", "").lower().split())
            if "noopener" not in rel:
                fail(errors, f"{path.relative_to(ROOT).as_posix()}: target=_blank link missing rel=noopener: {attrs.get('href')}")
    return text, parser


def main() -> int:
    errors: list[str] = []

    for media_path in ROOT.rglob("*"):
        if media_path.is_file() and media_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            if media_path.stat().st_size == 0:
                fail(errors, f"Zero-byte media file detected: {media_path.relative_to(ROOT).as_posix()}")

    core_texts: dict[str, str] = {}
    for filename, canonical in CORE.items():
        path = ROOT / filename
        text, _parser = inspect_html(path, errors)
        core_texts[filename] = text
        if not text:
            continue
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
        if text.count('href="answers.html"') < 2:
            fail(errors, f"{filename}: Answer Library missing from primary/hamburger navigation")

    watch = core_texts.get("watch.html", "")
    if watch:
        if "https://www.youtube.com/@theRisen636" not in watch:
            fail(errors, "watch.html missing verified YouTube channel path")
        if watch.count('href="ask.html"') < 2:
            fail(errors, "watch.html missing Ask continuation paths")
        for required_path in (
            "answers/jesus-christ-latter-day-saint-beliefs.html",
            "answers/what-is-the-book-of-mormon.html",
            "answers/prayer-and-personal-revelation.html",
            "answers/faith-in-jesus-christ-during-trials.html",
            "art-study/the-living-christ.html",
            "art-study/the-good-shepherd.html",
            "art-study/suffer-the-little-children.html",
            "art-study/be-still.html",
        ):
            if required_path not in watch:
                fail(errors, f"watch.html missing topic continuation path: {required_path}")

    answers_index = core_texts.get("answers.html", "")
    for answer_path, canonical in ANSWER_PAGES.items():
        path = ROOT / answer_path
        text, _parser = inspect_html(path, errors)
        if not text:
            continue
        if text.count("<title>") != 1 or text.count("<h1") != 1:
            fail(errors, f"{answer_path}: expected one title and one h1")
        if f'<link rel="canonical" href="{canonical}">' not in text:
            fail(errors, f"{answer_path}: canonical URL missing or incorrect")
        if '<meta name="description"' not in text:
            fail(errors, f"{answer_path}: meta description missing")
        if text.count('data-focuschrist-independence="footer"') != 1:
            fail(errors, f"{answer_path}: independence footer disclosure missing/duplicated")
        if text.count('<script src="../site-common.js" defer></script>') != 1:
            fail(errors, f"{answer_path}: shared interaction controller missing/duplicated")
        if 'href="../ask.html"' not in text:
            fail(errors, f"{answer_path}: Ask continuation path missing")
        if 'href="../answers.html"' not in text:
            fail(errors, f"{answer_path}: Answer Library return path missing")
        official_count = text.count("churchofjesuschrist.org") + text.count("faq.churchofjesuschrist.org")
        if official_count < 2:
            fail(errors, f"{answer_path}: insufficient official Church source pathways")
        index_href = answer_path
        if f'href="{index_href}"' not in answers_index:
            fail(errors, f"answers.html missing card for {answer_path}")

    header_css = ROOT / "site-header.css"
    if not header_css.exists() or header_css.stat().st_size == 0:
        fail(errors, "site-header.css missing or empty")
    else:
        header_css_text = header_css.read_text(encoding="utf-8")
        for required in ('data-focuschrist-header="standard"', 'linear-gradient', '.hamburger-menu', '@media (max-width: 900px)'):
            if required not in header_css_text:
                fail(errors, f"site-header.css missing canonical marker: {required}")

    for header_page, stylesheet in HEADER_PAGES.items():
        page = ROOT / header_page
        if not page.exists() or page.stat().st_size == 0:
            fail(errors, f"{header_page}: header page missing or empty")
            continue
        header_text = page.read_text(encoding="utf-8")
        if header_text.count('data-focuschrist-header="standard"') != 1:
            fail(errors, f"{header_page}: canonical header missing/duplicated")
        if f'href="{stylesheet}"' not in header_text:
            fail(errors, f"{header_page}: shared header stylesheet missing")
        if header_text.count('id="hamburgerMenu"') != 1:
            fail(errors, f"{header_page}: hamburger menu id missing/duplicated")
        for label in HEADER_LABELS:
            if header_text.count(f'>{label}</a>') < 2:
                fail(errors, f"{header_page}: synchronized header link missing: {label}")
        for resource in ('Church Website', 'Gospel Library', 'Come Follow Me', 'Temples', 'Church History', 'Citation Index', 'All Resources', '@theRisen636'):
            if resource not in header_text:
                fail(errors, f"{header_page}: synchronized hamburger resource missing: {resource}")

    common = ROOT / "site-common.js"
    if not common.exists() or common.stat().st_size == 0:
        fail(errors, "site-common.js missing or empty")
    else:
        common_text = common.read_text(encoding="utf-8")
        for marker in ("initNavigation", "initPioneerDisclosures", "aria-expanded", "aria-live"):
            if marker not in common_text:
                fail(errors, f"site-common.js missing required behavior marker: {marker}")

    ask = core_texts.get("ask.html", "")
    pioneers = core_texts.get("pioneers.html", "")
    about = core_texts.get("about.html", "")
    art = core_texts.get("art.html", "")

    for study_path, canonical in ART_STUDY_PAGES.items():
        path = ROOT / study_path
        text, parser = inspect_html(path, errors)
        if not text:
            continue
        if text.count("<title>") != 1 or text.count("<h1") != 1:
            fail(errors, f"{study_path}: expected one title and one h1")
        if f'<link rel="canonical" href="{canonical}">' not in text:
            fail(errors, f"{study_path}: canonical URL missing or incorrect")
        if '<meta name="description"' not in text:
            fail(errors, f"{study_path}: meta description missing")
        if text.count('data-focuschrist-independence="footer"') != 1:
            fail(errors, f"{study_path}: independence footer disclosure missing/duplicated")
        if '<script src="../site-common.js" defer></script>' not in text:
            fail(errors, f"{study_path}: shared interaction controller missing")
        if 'href="../art.html"' not in text or 'href="../ask.html"' not in text:
            fail(errors, f"{study_path}: Art/Ask continuation path missing")
        if text.count("churchofjesuschrist.org") < 2:
            fail(errors, f"{study_path}: official scripture/Church study pathway missing")
        if study_path not in art:
            fail(errors, f"art.html missing featured study link for {study_path}")
        local_images = [img for img in parser.images if img.get("src", "").startswith("../art/")]
        if not local_images:
            fail(errors, f"{study_path}: local gallery artwork image missing")


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
    if art.count('data-focuschrist-featured-art-study="true"') != 1:
        fail(errors, "Featured Art study section missing/duplicated")
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
            for canonical in list(CORE.values()) + list(ANSWER_PAGES.values()) + list(ART_STUDY_PAGES.values()):
                if canonical not in locs:
                    fail(errors, f"sitemap.xml missing {canonical}")
            if len(locs) < 21:
                fail(errors, f"sitemap.xml unexpectedly contains only {len(locs)} URLs")
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
        for target in ("index.html", "ask.html", "answers.html", "watch.html", "art.html", "pioneers.html", "about.html"):
            if f'href="{target}"' not in text404:
                fail(errors, f"404.html missing recovery link to {target}")

    if errors:
        print("FocusChrist SITE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("FocusChrist SITE QA PASSED")
    print(f"Core pages checked: {len(CORE)}")
    print(f"Permanent answer pages checked: {len(ANSWER_PAGES)}")
    print(f"Featured Art study pages checked: {len(ART_STUDY_PAGES)}")
    print(f"Art gallery images checked: {len(gallery_imgs)}")
    print("Search Console verification, sitemap, local references, Answer Library sources, model migration, disclosures, accessibility markers, and Ask rendering verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
