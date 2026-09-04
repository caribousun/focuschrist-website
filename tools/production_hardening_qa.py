from __future__ import annotations

from pathlib import Path
import hashlib
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str, errors: list[str]) -> str:
    path = ROOT / rel
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"{rel} missing or empty")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, rel: str, markers: tuple[str, ...], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{rel} missing production marker: {marker}")


def assert_order(text: str, rel: str, markers: list[str], errors: list[str]) -> None:
    positions = []
    for marker in markers:
        pos = text.find(marker)
        if pos < 0:
            errors.append(f"{rel} missing chronology marker: {marker}")
            return
        positions.append(pos)
    if positions != sorted(positions):
        errors.append(f"{rel} chronology is out of order: {' -> '.join(markers)}")


def webp_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a RIFF WebP")
    offset = 12
    while offset + 8 <= len(data):
        kind = data[offset:offset+4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if kind == b"VP8X" and size >= 10:
            width = 1 + int.from_bytes(data[payload+4:payload+7], "little")
            height = 1 + int.from_bytes(data[payload+7:payload+10], "little")
            return width, height
        if kind == b"VP8 " and size >= 10:
            frame = data.find(b"\x9d\x01\x2a", payload, min(payload + size, len(data)))
            if frame >= 0 and frame + 7 <= len(data):
                width = int.from_bytes(data[frame+3:frame+5], "little") & 0x3FFF
                height = int.from_bytes(data[frame+5:frame+7], "little") & 0x3FFF
                return width, height
        if kind == b"VP8L" and size >= 5 and data[payload] == 0x2F:
            bits = int.from_bytes(data[payload+1:payload+5], "little")
            width = (bits & 0x3FFF) + 1
            height = ((bits >> 14) & 0x3FFF) + 1
            return width, height
        offset = payload + size + (size & 1)
    raise ValueError("WebP dimensions unavailable")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with an IHDR header")
    return struct.unpack(">II", data[16:24])


def image_dimensions(path: Path) -> tuple[int, int]:
    if path.suffix.lower() == ".png":
        return png_dimensions(path)
    return webp_dimensions(path)


def check_hero_assets(errors: list[str]) -> None:
    floors = {
        "assets/heroes/home.webp": (1400, 700),
        "assets/heroes/ask.webp": (2100, 700),
        "assets/heroes/answers.webp": (2100, 700),
        "assets/heroes/art.webp": (2100, 700),
        "assets/heroes/church-history.webp": (1900, 700),
        "assets/heroes/pioneers.webp": (2100, 700),
        "assets/heroes/watch.webp": (2100, 700),
        "assets/heroes/about.webp": (2100, 700),
        "assets/heroes/missionary.webp": (2100, 700),
    }
    for rel, (min_w, min_h) in floors.items():
        path = ROOT / rel
        if not path.exists() or path.stat().st_size < 40_000:
            errors.append(f"{rel} missing, empty, or implausibly small")
            continue
        try:
            w, h = image_dimensions(path)
        except Exception as exc:
            errors.append(f"{rel} dimension check failed: {exc}")
            continue
        if w < min_w or h < min_h:
            errors.append(f"{rel} below production resolution floor: {w}x{h}, expected at least {min_w}x{min_h}")


def check_supporting_art_assets(errors: list[str]) -> None:
    floors = {
        "assets/page-art/ask-seek-study-800.webp": (800, 400),
        "assets/page-art/ask-seek-study-1400.webp": (1400, 700),
        "assets/page-art/ask-nicodemus-640.webp": (640, 800),
        "assets/page-art/ask-nicodemus-1122.webp": (1122, 1402),
        "assets/history/first-vision-800.webp": (800, 267),
        "assets/history/first-vision-1400.webp": (1400, 468),
        "assets/history/joseph-emma-harmony-800.webp": (800, 267),
        "assets/history/joseph-emma-harmony-1400.webp": (1400, 467),
        "assets/history/three-witnesses-800.webp": (800, 267),
        "assets/history/three-witnesses-1400.webp": (1400, 467),
        "assets/history/restoration-print-shop-800.webp": (800, 267),
        "assets/history/restoration-print-shop-1400.webp": (1400, 467),
        "assets/history/preserving-the-record-800.webp": (800, 267),
        "assets/history/preserving-the-record-1400.webp": (1400, 467),
        "assets/history/christ-museum-record-800.webp": (800, 400),
        "assets/history/christ-museum-record-1400.webp": (1400, 700),
        "assets/history/christ-through-eras-800.webp": (800, 267),
        "assets/history/christ-through-eras-1400.webp": (1400, 467),
    }
    for rel, expected in floors.items():
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"{rel} missing or empty")
            continue
        try:
            actual = webp_dimensions(path)
        except Exception as exc:
            errors.append(f"{rel} dimension check failed: {exc}")
            continue
        if actual != expected:
            errors.append(f"{rel} has unexpected dimensions: {actual[0]}x{actual[1]}, expected {expected[0]}x{expected[1]}")


def check_answers_art_assets(errors: list[str]) -> None:
    approved = {
        "assets/heroes/answers-christ-companion.png": ((2048, 682), "d6fd78e892da505de24e0c84f6a68c70e823f20c052eb8320d0ceac538282f91"),
        "assets/answers-christ-portrait.png": ((941, 1672), "b64d4d125fe03f7b8f2bb3f1e919b0e8107d4b9cc24b8a38fdf854176cf62c45"),
        "assets/answers-christ-walking.png": ((2048, 682), "60dedc0b4fde604470975b0bfe08def25c6bf5448e1310b93175d86a3837fa97"),
    }
    for rel, (expected_dimensions, expected_sha256) in approved.items():
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"{rel} missing or empty")
            continue
        try:
            actual_dimensions = image_dimensions(path)
        except Exception as exc:
            errors.append(f"{rel} dimension check failed: {exc}")
            continue
        if actual_dimensions != expected_dimensions:
            errors.append(
                f"{rel} has unexpected dimensions: {actual_dimensions[0]}x{actual_dimensions[1]}, "
                f"expected {expected_dimensions[0]}x{expected_dimensions[1]}"
            )
        actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            errors.append(f"{rel} no longer matches the owner-approved source image")


def check_no_editable_drive_runtime(errors: list[str]) -> None:
    forbidden = ("lh3.googleusercontent.com/d/", "drive.google.com/file/d/", "caribousun.github.io/focuschrist-website/Jesus.png")
    runtime = []
    for pattern in ("*.html", "*.css", "*.js"):
        runtime.extend(ROOT.rglob(pattern))
    for path in runtime:
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in forbidden:
            if marker in text:
                errors.append(f"{path.relative_to(ROOT)} retains editable/external project asset dependency: {marker}")


def main() -> int:
    errors: list[str] = []

    check_hero_assets(errors)
    check_supporting_art_assets(errors)
    check_answers_art_assets(errors)
    check_no_editable_drive_runtime(errors)

    hero_refs = {
        "site-system.css": "assets/heroes/home.webp",
        "ask-hero.css": "assets/heroes/ask.webp",
        "answers-hero.css": "assets/heroes/answers.webp",
        "art-hero.css": "assets/heroes/art.webp",
        "church-history-experience.js": "assets/heroes/church-history.webp",
        "pioneers.html": "assets/heroes/pioneers.webp",
        "watch-experience.css": "assets/heroes/watch.webp",
        "about-hero.css": "assets/heroes/about.webp",
        "missionary.html": "assets/heroes/missionary.webp",
    }
    for rel, marker in hero_refs.items():
        require(read(rel, errors), rel, (marker,), errors)

    answers_page = read("answers.html", errors)
    original_answers_hero = (
        '<div class="fc-visual-hero fc-visual-hero--christ fc-visual-hero--answers" '
        'aria-label="Open scriptures and study materials overlooking a peaceful sunset landscape"></div>'
    )
    if original_answers_hero not in answers_page:
        errors.append("answers.html must preserve the owner-approved original Answers hero unless the owner explicitly approves a hero change")
    answers_art_order = [
        "assets/heroes/answers-christ-companion.png",
        "assets/answers-christ-portrait.png",
        "assets/answers-christ-walking.png",
    ]
    assert_order(answers_page, "answers.html supporting artwork", answers_art_order, errors)
    opening = answers_page.split('<section class="fc-page-intro"', 1)[0]
    for art_path in answers_art_order:
        if art_path in opening:
            errors.append(f"answers.html uses supporting artwork as the hero without explicit owner approval: {art_path}")

    social = {
        "index.html": "home.webp",
        "ask.html": "ask.webp",
        "answers.html": "answers.webp",
        "art.html": "art.webp",
        "church-history.html": "church-history.webp",
        "pioneers.html": "pioneers.webp",
        "watch.html": "watch.webp",
        "about.html": "about.webp",
        "missionary.html": "missionary.webp",
    }
    for rel, image in social.items():
        text = read(rel, errors)
        url = f"https://focuschrist.com/assets/heroes/{image}"
        if text.count(url) < 2:
            errors.append(f"{rel} must use page-specific production hero for both Open Graph and Twitter image metadata")
        require(text, rel, ('rel="canonical"', 'name="robots" content="index, follow, max-image-preview:large"'), errors)

    missionary = read("missionary.html", errors)
    require(missionary, "missionary.html", (
        "assets/heroes/missionary.webp",
        "assets/missionary/christ-centered-world.webp",
        "assets/missionary/light-across-world.webp",
        "data-focuschrist-primary-missionary",
        "Meet with Missionaries",
        "Explore Ways to Serve",
        "data-focuschrist-independence=\"missionary\"",
    ), errors)

    pioneers = read("pioneers.html", errors)
    assert_order(pioneers, "pioneers.html THE JOURNEY", [
        'data-topic="exodus"', 'data-topic="winterquarters"', 'data-topic="valley"', 'data-topic="pioneerday"',
        'data-topic="templesquare"', 'data-topic="templestart"', 'data-topic="handcart"',
        'data-topic="railroad"', 'data-topic="statehood"'
    ], errors)
    assert_order(pioneers, "pioneers.html THE TRAIL", [
        'data-topic="nauvoo"', 'data-topic="garden-grove"', 'data-topic="council-bluffs"', 'data-topic="chimney-rock"',
        'data-topic="fort-laramie"', 'data-topic="independence-rock"', 'data-topic="sweetwater"', 'data-topic="south-pass"',
        'data-topic="fort-bridger"', 'data-topic="echo-canyon"', 'data-topic="canyon"', 'data-topic="salt-lake-valley"',
        'data-topic="mountain-meadow"'
    ], errors)
    assert_order(pioneers, "pioneers.html Willie & Martin", [
        'data-topic="willie-july"', 'data-topic="willie-august"', 'data-topic="willie-september"', 'data-topic="willie-october"',
        'data-topic="martin-september"', 'data-topic="willie-november"', 'data-topic="martin-november"'
    ], errors)
    require(pioneers, "pioneers.html verified primary-source research", (
        "PRIMARY-SOURCE JOURNALS",
        "pioneer-diaries-and-journals",
        "study/history/topics/pioneer-trek",
        "nps.gov/articles/000/mormon-pioneer-trail-junior-ranger",
    ), errors)
    for unsupported in (
        "William A. Anderson, Pioneer Journal",
        "British convert journal entry",
        "Willie Handcart Company survivor",
        "Martin Handcart Company survivor",
        'data-topic="goldrush"',
    ):
        if unsupported in pioneers:
            errors.append(f"pioneers.html retains removed unsupported material: {unsupported}")

    art = read("art.html", errors)
    art_router = read("art-study-router.js", errors)
    art_ask = read("art-ask-context.js", errors)
    require(art_router, "art-study-router.js", (
        "Study this artwork", "Study this topic on ChurchofJesusChrist.org", "Ask about this artwork",
        "returnUrlForCaption", "art.html?art=", "data-focuschrist-art-return-restored"
    ), errors)
    require(art_ask, "art-ask-context.js", (
        "Studying artwork", "Return to this artwork", "data-focuschrist-art-return-float",
        "data-focuschrist-art-prefill", "data-focuschrist-art-ask-context"
    ), errors)
    if re.search(r"youtube\.com|@theRisen636|CHANNEL\s*=", art_router, re.I):
        errors.append("art-study-router.js must not use YouTube/@theRisen636 as an artwork study destination")
    if "art-ask-context.js?v=20260830-1" not in read("ask.html", errors):
        errors.append("ask.html must load contextual artwork Ask bridge")
    if art.count("art/thumbs/new/") < 11 or art.count("data-full-src=\"art/new/") < 11:
        errors.append("art.html must use localized thumbnails + full-resolution targets for all newly added artworks")
    new_full = sorted((ROOT / "art" / "new").glob("*.webp"))
    new_thumbs = sorted((ROOT / "art" / "thumbs" / "new").glob("*.webp"))
    if len(new_full) < 11 or len(new_thumbs) != len(new_full):
        errors.append(f"new Art localization incomplete: {len(new_full)} full images, {len(new_thumbs)} thumbnails")

    watch = read("watch.html", errors)
    watch_js = read("watch-experience.js", errors)
    watch_css = read("watch-experience.css", errors)
    watch_enrichment = read("watch-study-enrichment.js", errors)
    require(watch_js, "watch-experience.js", (
        "3a960a019d9f6bb9a0abc1d6dba875c8d0aa13bf",
        "46BE164CBF18B911A146DA4838DC630D7FEBDD47",
        "18da2703093511ed8ad5eeeeac1ea1e004d5c967",
        "fbeeffd36f5d11eea80aeeeeac1e2a5eec857672",
        "Jesus Christ Appears in the Ancient Americas",
        "Welcome to the House of the Lord",
        "--watch-path-thumb",
        "data-watch-thumbnail-ready",
    ), errors)
    require(watch_css, "watch-experience.css", (
        "--watch-thumb", "nth-child(1)", "nth-child(2)", "nth-child(3)",
        "Production hardening: every concrete theme Watch route carries a corresponding video thumbnail.",
        "var(--watch-path-thumb)"
    ), errors)
    require(watch_enrichment, "watch-study-enrichment.js", (
        "watch-mini-media", "data-watch-thumbnail-ready", "MutationObserver", "data-focuschrist-watch-enrichment-ready"
    ), errors)
    if watch.count("watch-mini-media") < 3:
        errors.append("watch.html must retain all three verified official mini-video cards")

    sitemap = read("sitemap.xml", errors)
    robots = read("robots.txt", errors)
    require(robots, "robots.txt", ("User-agent: *", "Allow: /", "Sitemap: https://focuschrist.com/sitemap.xml"), errors)
    for url in ("ask.html", "answers.html", "watch.html", "art.html", "missionary.html", "church-history.html", "pioneers.html", "about.html"):
        if f"https://focuschrist.com/{url}" not in sitemap:
            errors.append(f"sitemap.xml missing core page {url}")
    if sitemap.count("<lastmod>2026-08-30</lastmod>") < 8:
        errors.append("sitemap.xml core-page lastmod values were not refreshed for hardened production release")

    checklist = read("WEBSITE_CHECKLIST.md", errors)
    memory = read("MEMORY.md", errors)
    receipt = read("PRODUCTION-RECEIPT-2026-08-30.md", errors)
    require(checklist, "WEBSITE_CHECKLIST.md", ("Hardened presentation gates", "Art -> Ask -> Art", "production_hardening_qa.py"), errors)
    require(memory, "MEMORY.md", ("FocusChrist Production Hardening Standard", "Pioneer historical lists must remain chronological", "Artwork Ask continuity is mandatory"), errors)
    require(receipt, "PRODUCTION-RECEIPT-2026-08-30.md", ("Locked outcomes", "Learning rule"), errors)

    for workflow in (".github/workflows/site-qa.yml", ".github/workflows/deploy-pages.yml"):
        wf = read(workflow, errors)
        require(wf, workflow, (
            "python tools/production_hardening_qa.py",
            "node --check watch-experience.js",
            "node --check art-ask-context.js"
        ), errors)

    if errors:
        print("focusChrist PRODUCTION HARDENING QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist PRODUCTION HARDENING QA PASSED")
    print("Verified local high-resolution heroes, page-specific social previews, Pioneer chronology, artwork topic study + contextual Ask + exact return continuity, thumbnail-backed Watch video paths, localized Art assets, discovery controls, workflow gates, and durable local-brain learning.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
