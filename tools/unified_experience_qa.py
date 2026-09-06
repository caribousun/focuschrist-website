from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ROOT_PAGES = [
    "index.html", "ask.html", "answers.html", "art.html", "church-history.html", "pioneers.html",
    "about.html", "watch.html", "404.html",
]
NESTED_PAGES = sorted(
    [p.relative_to(ROOT).as_posix() for p in (ROOT / "answers").glob("*.html")]
    + [p.relative_to(ROOT).as_posix() for p in (ROOT / "art-study").glob("*.html")]
)
PUBLIC_PAGES = ROOT_PAGES + NESTED_PAGES
IMAGE_FIRST_PAGES = [p for p in PUBLIC_PAGES if p != "404.html"]


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden_depth = 0
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            self.text.append(data)


def fail(errors: list[str], message: str):
    errors.append(message)


def visible_text(html: str) -> str:
    parser = VisibleTextParser()
    parser.feed(html)
    return " ".join(parser.text)


def expected_system_href(path: str) -> str:
    return "../site-system.css" if "/" in path else "site-system.css"


def css_block(css: str, header: str) -> str | None:
    start = css.find(header)
    if start < 0:
        return None
    opening = css.find("{", start + len(header))
    if opening < 0:
        return None
    depth = 0
    for index in range(opening, len(css)):
        if css[index] == "{":
            depth += 1
        elif css[index] == "}":
            depth -= 1
            if depth == 0:
                return css[opening + 1:index]
    return None


def main() -> int:
    errors: list[str] = []

    design = ROOT / "site-system.css"
    if not design.exists() or design.stat().st_size == 0:
        fail(errors, "site-system.css missing or empty")
    else:
        css = design.read_text(encoding="utf-8")
        for marker in (
            "--fc-bg", "--fc-standard", "--fc-opening-hero-height", "--fc-ultrawide-hero-width",
            ".fc-visual-hero", ".fc-page-intro",
            ".fc-visual-hero + .fc-page-intro", "100dvh",
            "@media (min-width: 2560px)", "Each original hero supplies the nearby",
            "width: var(--fc-ultrawide-hero-width)",
            "--fc-hero-edge-left-top", "--fc-hero-edge-right-bottom",
            "rgba(0,0,0,.50) 9%", "rgba(0,0,0,.50) 91%",
            ".fc-card", ".fc-button", ".fc-content-artwork", ".fc-art-link", ".fc-footer", "prefers-reduced-motion",
        ):
            if marker not in css:
                fail(errors, f"site-system.css missing design-system marker: {marker}")

        ultrawide = css_block(css, "@media (min-width: 2560px)")
        if ultrawide is None:
            fail(errors, "site-system.css missing complete ultrawide block")
        else:
            edge_keys = (
                "--fc-hero-edge-left-top",
                "--fc-hero-edge-left-bottom",
                "--fc-hero-edge-right-top",
                "--fc-hero-edge-right-bottom",
            )
            hero_mappings = (
                ".fc-visual-hero--christ",
                ".fc-visual-hero--ask",
                ".fc-visual-hero--answers",
                ".fc-visual-hero--art",
                ".fc-visual-hero--about",
                ".fc-visual-hero--watch",
                ".fc-visual-hero--history",
                ".fc-history-hero",
            )
            for selector in hero_mappings:
                mapping = css_block(ultrawide, selector)
                if mapping is None:
                    fail(errors, f"site-system.css missing ultrawide edge mapping: {selector}")
                    continue
                for key in edge_keys:
                    if key not in mapping:
                        fail(errors, f"site-system.css {selector} missing ultrawide edge color: {key}")

            radial_fields = (
                "radial-gradient(ellipse 34% 88% at 22% 0%, var(--fc-hero-edge-left-top) 0%, transparent 100%)",
                "radial-gradient(ellipse 34% 88% at 22% 100%, var(--fc-hero-edge-left-bottom) 0%, transparent 100%)",
                "radial-gradient(ellipse 34% 88% at 78% 0%, var(--fc-hero-edge-right-top) 0%, transparent 100%)",
                "radial-gradient(ellipse 34% 88% at 78% 100%, var(--fc-hero-edge-right-bottom) 0%, transparent 100%)",
            )
            for field in radial_fields:
                if field not in ultrawide:
                    fail(errors, f"site-system.css missing hero-matched ultrawide field: {field}")

            curved_mask = (
                "linear-gradient(90deg, transparent 0%, rgba(0,0,0,.13) 4%, rgba(0,0,0,.50) 9%, "
                "rgba(0,0,0,.87) 14%, #000 18%, #000 82%, rgba(0,0,0,.87) 86%, "
                "rgba(0,0,0,.50) 91%, rgba(0,0,0,.13) 96%, transparent 100%)"
            )
            if ultrawide.count(curved_mask) != 2:
                fail(errors, "site-system.css must keep matching standard and WebKit curved ultrawide masks")
            if "url(" in ultrawide or "image-set(" in ultrawide or "--fc-hero-image" in ultrawide:
                fail(errors, "site-system.css ultrawide atmosphere must not contain a duplicate image layer")

    for relative in PUBLIC_PAGES:
        path = ROOT / relative
        if not path.exists() or path.stat().st_size == 0:
            fail(errors, f"{relative}: missing or empty")
            continue
        text = path.read_text(encoding="utf-8")
        system_href = expected_system_href(relative)
        if f'href="{system_href}' not in text:
            fail(errors, f"{relative}: unified site-system stylesheet missing")
        body_tag = re.search(r"<body[^>]*>", text, re.I)
        if not body_tag or "fc-site" not in body_tag.group(0):
            fail(errors, f"{relative}: fc-site body marker missing")
        if relative != "404.html" and text.count('data-focuschrist-independence="footer"') != 1:
            fail(errors, f"{relative}: independence footer disclosure missing/duplicated")
        if text.count('data-focuschrist-footer="standard"') != 1:
            fail(errors, f"{relative}: unified footer marker missing/duplicated")

        rendered = visible_text(text)
        if re.search(r"\bFocusChrist\b|\bFocuschrist\b|\bFOCUSCHRIST\b", rendered):
            fail(errors, f"{relative}: public brand casing drift detected; use focusChrist")

    for relative in IMAGE_FIRST_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if 'class="fc-visual-hero' not in text:
            fail(errors, f"{relative}: image-first hero marker missing")
        if 'class="fc-page-intro' not in text:
            fail(errors, f"{relative}: below-image page introduction missing")
        hero = re.search(r'<(?:div|a) class="fc-visual-hero[^>]*>.*?</(?:div|a)>', text, re.S | re.I)
        if hero and re.search(r"<h[1-6]\b|<p\b", hero.group(0), re.I):
            fail(errors, f"{relative}: text content detected inside image-first hero")

    for relative in ("index.html", "ask.html", "answers.html", "art.html", "about.html", "watch.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if 'fc-visual-hero--christ' not in text:
            fail(errors, f"{relative}: Christ image hero variant missing")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    home_art = "assets/page-art/home-seek-study-remember.webp"
    if not re.search(r'src="' + re.escape(home_art) + r'(?:\?[^"\s]*)?"', home) or 'class="fc-content-artwork fc-home-purpose-art"' not in home:
        fail(errors, "index.html: approved supporting artwork missing or not wired")
    for marker in ('href="home.css?v=20260906-sky"', 'class="fc-home-purpose-split"', 'class="fc-home-purpose-copy"'):
        if marker not in home:
            fail(errors, f"index.html: Missionary-style Home composition marker missing: {marker}")
    home_art_path = ROOT / home_art
    if not home_art_path.exists() or home_art_path.stat().st_size == 0:
        fail(errors, f"index.html: supporting artwork asset missing or empty: {home_art}")
    if not re.search(r'class="fc-art-link" href="' + re.escape(home_art) + r'(?:\?[^"\s]*)?"', home):
        fail(errors, "index.html: Home supporting artwork must open its full-resolution source")
    home_new_art = (
        "assets/page-art/home-come-and-see-900.webp",
        "assets/page-art/home-come-and-see-1672.webp",
        "assets/page-art/home-light-through-study-900.webp",
        "assets/page-art/home-light-through-study-1672.webp",
    )
    for asset in home_new_art:
        path = ROOT / asset
        if asset not in home:
            fail(errors, f"index.html: approved supporting artwork not wired: {asset}")
        if not path.exists() or path.stat().st_size == 0:
            fail(errors, f"index.html: supporting artwork asset missing or empty: {asset}")
        elif asset.endswith("-900.webp") and path.stat().st_size > 120_000:
            fail(errors, f"index.html: responsive supporting artwork exceeds 120 KB performance budget: {asset}")
    for full_art in (
        "assets/page-art/home-come-and-see-1672.webp",
        "assets/page-art/home-light-through-study-1672.webp",
    ):
        if not re.search(r'class="fc-art-link" href="' + re.escape(full_art) + r'(?:\?[^"\s]*)?"', home):
            fail(errors, f"index.html: full-resolution supporting artwork link missing: {full_art}")

    ask = (ROOT / "ask.html").read_text(encoding="utf-8")
    ask_art_assets = (
        "assets/page-art/ask-seek-study-800.webp",
        "assets/page-art/ask-seek-study-1400.webp",
        "assets/page-art/ask-nicodemus-640.webp",
        "assets/page-art/ask-nicodemus-1122.webp",
        "assets/page-art/ask-road-to-emmaus-eye-corrected-900.webp",
    )
    for ask_art in ask_art_assets:
        ask_art_path = ROOT / ask_art
        if ask_art not in ask:
            fail(errors, f"ask.html: approved supporting artwork not wired: {ask_art}")
        if not ask_art_path.exists() or ask_art_path.stat().st_size == 0:
            fail(errors, f"ask.html: supporting artwork asset missing or empty: {ask_art}")
        elif ask_art_path.stat().st_size > 120_000:
            fail(errors, f"ask.html: supporting artwork exceeds 120 KB performance budget: {ask_art}")
    for marker in (
        'class="ask-conversation-feature"',
        'id="conversationClearBtn"',
        '>Clear Conversation</button>',
        'class="ask-continue-layout"',
        'loading="lazy"',
        'decoding="async"',
        'srcset="assets/page-art/ask-seek-study-800.webp 800w',
        'srcset="assets/page-art/ask-nicodemus-640.webp 640w',
        'srcset="assets/page-art/ask-road-to-emmaus-eye-corrected-900.webp 900w',
    ):
        if marker not in ask:
            fail(errors, f"ask.html: supporting artwork responsive marker missing: {marker}")
    for full_art in (
        "assets/page-art/ask-seek-study-1400.webp",
        "assets/page-art/ask-nicodemus-1122.webp",
        "assets/page-art/ask-road-to-emmaus-eye-corrected-1672.webp",
    ):
        if f'class="fc-art-link" href="{full_art}"' not in ask:
            fail(errors, f"ask.html: full-resolution supporting artwork link missing: {full_art}")

    history = (ROOT / "church-history.html").read_text(encoding="utf-8")
    history_art_assets = (
        "assets/history/first-vision-800.webp",
        "assets/history/first-vision-1400.webp",
        "assets/history/joseph-emma-harmony-800.webp",
        "assets/history/joseph-emma-harmony-1400.webp",
        "assets/history/three-witnesses-800.webp",
        "assets/history/three-witnesses-1400.webp",
        "assets/history/restoration-print-shop-800.webp",
        "assets/history/restoration-print-shop-1400.webp",
        "assets/history/preserving-the-record-800.webp",
        "assets/history/preserving-the-record-1400.webp",
        "assets/history/christ-museum-record-800.webp",
        "assets/history/christ-museum-record-1400.webp",
        "assets/history/christ-through-eras-800.webp",
        "assets/history/christ-through-eras-1400.webp",
    )
    for history_art in history_art_assets:
        history_art_path = ROOT / history_art
        if history_art not in history:
            fail(errors, f"church-history.html: approved supporting artwork not wired: {history_art}")
        if not history_art_path.exists() or history_art_path.stat().st_size == 0:
            fail(errors, f"church-history.html: supporting artwork asset missing or empty: {history_art}")
        elif history_art_path.stat().st_size > 120_000:
            fail(errors, f"church-history.html: supporting artwork exceeds 120 KB performance budget: {history_art}")
    for marker in (
        'church-history.css?v=20260904-2',
        'class="fc-history-art-panel fc-history-art-panel--wide"',
        'class="fc-history-art-panel fc-history-art-panel--inline fc-history-art-panel--offset-left"',
        'class="fc-history-art-panel fc-history-art-panel--inline fc-history-art-panel--offset-right"',
        'loading="lazy"',
        'srcset="assets/history/first-vision-800.webp 800w',
        'srcset="assets/history/christ-through-eras-800.webp 800w',
    ):
        if marker not in history:
            fail(errors, f"church-history.html: artwork-flow marker missing: {marker}")
    for full_art in history_art_assets[1::2]:
        if f'class="fc-art-link" href="{full_art}"' not in history:
            fail(errors, f"church-history.html: full-resolution supporting artwork link missing: {full_art}")
    history_opening = history.split('<section class="fc-page-intro"', 1)[0]
    for history_art in history_art_assets:
        if history_art in history_opening:
            fail(errors, f"church-history.html: supporting artwork replaced the approved hero: {history_art}")
    ask_css = (ROOT / "ask-experience.css").read_text(encoding="utf-8")
    for marker in (
        'grid-template-columns: minmax(0, 1.45fr) minmax(310px, .75fr)',
        '.ask-conversation-copy .ask-section-heading',
        '.ask-clear-conversation',
        'grid-template-areas: "links art"',
        '@media (max-width: 1050px)',
        '.ask-continue-card span',
    ):
        if marker not in ask_css:
            fail(errors, f"ask-experience.css: polished artwork-flow marker missing: {marker}")

    ask_js = (ROOT / "ask-experience.js").read_text(encoding="utf-8")
    for marker in ("chatBox.insertAdjacentElement('beforebegin', dock)", "followupDock.classList.contains('visible') ? followupDock : chatBox", "document.getElementById('conversationClearBtn')"):
        if marker not in ask_js:
            fail(errors, f"ask-experience.js: follow-up visibility marker missing: {marker}")
    for unrequested_control in ("Clear & Start Over", "Clear Conversation", "data-focuschrist-conversation-reset"):
        if unrequested_control in (ROOT / "study-journey.js").read_text(encoding="utf-8"):
            fail(errors, f"study-journey.js: unrequested reset control remains: {unrequested_control}")

    pioneers = (ROOT / "pioneers.html").read_text(encoding="utf-8")
    if 'fc-visual-hero--history' not in pioneers:
        fail(errors, "pioneers.html: historical hero variant missing")
    for asset in ("pioneer-experience.css", "pioneer-experience.js"):
        if asset not in pioneers:
            fail(errors, f"pioneers.html: {asset} not wired")
    for malformed in ("</script></script>", "<!-- Hero removed -->"):
        if malformed in pioneers:
            fail(errors, f"pioneers.html: malformed legacy marker remains: {malformed}")
    if '>New Question</button>' not in pioneers:
        fail(errors, "pioneers.html: New Question reset language missing")

    pioneer_art_names = (
        "leaving-nauvoo", "winter-quarters", "life-along-trail", "platte-river",
        "river-crossing", "handcart-journey", "rescue-wagons", "first-view-valley",
        "building-community", "salt-lake-temple",
    )
    for name in pioneer_art_names:
        for width in (800, 1400, 1672):
            pioneer_art = f"assets/pioneers/{name}-{width}.webp"
            pioneer_art_path = ROOT / pioneer_art
            if pioneer_art not in pioneers:
                fail(errors, f"pioneers.html: approved supporting artwork not wired: {pioneer_art}")
            if not pioneer_art_path.exists() or pioneer_art_path.stat().st_size == 0:
                fail(errors, f"pioneers.html: supporting artwork asset missing or empty: {pioneer_art}")
            elif width != 1672 and pioneer_art_path.stat().st_size > 120_000:
                fail(errors, f"pioneers.html: delivered supporting artwork exceeds 120 KB: {pioneer_art}")
        full_art = f"assets/pioneers/{name}-1672.webp"
        if f'class="fc-art-link" href="{full_art}"' not in pioneers:
            fail(errors, f"pioneers.html: full-resolution supporting artwork link missing: {full_art}")
    for marker in (
        'class="pioneer-art-grid pioneer-art-grid--two"',
        'class="pioneer-art-grid pioneer-art-grid--three"',
        'data-full-image-viewer',
        'loading="lazy"',
        'decoding="async"',
    ):
        if marker not in pioneers:
            fail(errors, f"pioneers.html: supporting artwork flow marker missing: {marker}")
    if pioneers.count("data-full-image-viewer") < 11:
        fail(errors, "pioneers.html: hero and all ten supporting artworks must retain full-image viewer behavior")

    pioneer_js = ROOT / "pioneer-experience.js"
    if not pioneer_js.exists() or pioneer_js.stat().st_size == 0:
        fail(errors, "pioneer-experience.js missing or empty")
    else:
        js = pioneer_js.read_text(encoding="utf-8")
        for marker in (
            "window.sendMessage", "window.clearChat", "Continue the conversation",
            "Ask a follow-up question", "textContent", "positionAnswer",
            "conversationHistory", "pioneerComposerLabel",
            "PIONEER_PAGE_CONTEXT", "Exodus from Nauvoo", "EXPLICIT_NON_PIONEER_RE",
            "window.focusChristPioneerAskAI", "window.expandTimelineItem",
            "window.expandTrailPoint", "window.askTopic", "temperature: 0.2",
        ):
            if marker not in js:
                fail(errors, f"pioneer-experience.js missing conversation/context hardening marker: {marker}")
        if "message.innerHTML" in js:
            fail(errors, "pioneer-experience.js unsafe message.innerHTML renderer detected")
        if "findAnswer(question)" in js:
            fail(errors, "pioneer-experience.js must not give the legacy general Q&A database first priority")
        if "It does NOT mean the biblical Book of Exodus" not in js:
            fail(errors, "pioneer-experience.js missing explicit Nauvoo Exodus disambiguation")

    pioneer_css = ROOT / "pioneer-experience.css"
    if not pioneer_css.exists() or pioneer_css.stat().st_size == 0:
        fail(errors, "pioneer-experience.css missing or empty")
    else:
        css = pioneer_css.read_text(encoding="utf-8")
        for marker in (
            "[data-focus-expand] .ai-response", "pioneer-collapse-action",
            "border-left: 3px solid var(--fc-sky) !important",
            "linear-gradient(145deg, rgba(28,61,76,.98), rgba(18,43,56,.99)) !important",
        ):
            if marker not in css:
                fail(errors, f"pioneer-experience.css missing Pioneer response palette marker: {marker}")
        if "linear-gradient(145deg, rgba(49,74,69,.94), rgba(28,54,61,.96))" in css:
            fail(errors, "pioneer-experience.css contains the superseded olive/brown expanded-response surface")

    art = (ROOT / "art.html").read_text(encoding="utf-8")
    if "art-experience.css" not in art:
        fail(errors, "art.html: unified Art presentation stylesheet missing")
    if 'data-full-src=' not in art or 'id="imageModal"' not in art:
        fail(errors, "art.html: gallery artwork must retain its full-resolution viewer")

    supporting_art_links = {
        "answers.html": (
            "assets/heroes/answers-christ-companion.png",
            "assets/answers-christ-portrait.png",
            "assets/answers-christ-walking.png",
            "assets/page-art/answers-savior-welcomes-child-1672.webp?v=20260905-approved-face",
            "assets/page-art/answers-quiet-prayer-1536.webp",
            "assets/page-art/answers-child-loss-father-1726.webp",
            "assets/page-art/answers-child-loss-parents-1726.webp",
            "assets/page-art/answers-divorced-father-1724.webp",

            "assets/page-art/answers-comfort-in-grief-1536.webp",
        ),
        "missionary.html": (
            "assets/missionary/christ-centered-world.webp",
            "assets/missionary/light-across-world.webp",
            "assets/missionary/samuel-smith-first-mission-1400.webp",
            "assets/missionary/early-missionaries-liverpool-1400.webp",
            "assets/missionary/sister-missionaries-teaching-1400.webp",
            "assets/missionary/service-missionaries-food-pantry-1400.webp",
            "assets/missionary/christ-commissions-twelve-approved-full.webp",
        ),
    }
    for relative, assets in supporting_art_links.items():
        page = (ROOT / relative).read_text(encoding="utf-8")
        for asset in assets:
            if f'href="{asset}"' not in page:
                fail(errors, f"{relative}: full-resolution supporting artwork link missing: {asset}")

    missionary = (ROOT / "missionary.html").read_text(encoding="utf-8")
    missionary_art_variants = (
        "assets/missionary/samuel-smith-first-mission-800.webp",
        "assets/missionary/samuel-smith-first-mission-1400.webp",
        "assets/missionary/early-missionaries-liverpool-800.webp",
        "assets/missionary/early-missionaries-liverpool-1400.webp",
        "assets/missionary/sister-missionaries-teaching-800.webp",
        "assets/missionary/sister-missionaries-teaching-1400.webp",
        "assets/missionary/service-missionaries-food-pantry-800.webp",
        "assets/missionary/service-missionaries-food-pantry-1400.webp",
        "assets/missionary/christ-commissions-twelve-approved-900.webp",
        "assets/missionary/christ-commissions-twelve-approved-1100.webp",
    )
    for asset in missionary_art_variants:
        path = ROOT / asset
        if not path.exists() or path.stat().st_size == 0:
            fail(errors, f"missionary.html: supporting artwork asset missing or empty: {asset}")
        elif path.stat().st_size > 120_000:
            fail(errors, f"missionary.html: supporting artwork exceeds 120 KB performance budget: {asset}")
        if f'"{asset}"' not in missionary:
            fail(errors, f"missionary.html: responsive supporting artwork marker missing: {asset}")

    missionary_detail_keys = (
        "commission",
        "samuel-smith",
        "crossing-oceans",
        "early-missionaries",
        "growth-of-work",
        "missionary-purpose",
        "worldwide-work",
        "teaching-families",
        "service-missionaries",
    )
    commission_link = re.search(r'<a[^>]+href="https://www.churchofjesuschrist.org/study/scriptures/nt/matt/28\?lang=eng"[^>]*>Read the Savior\'s commission</a>', missionary)
    if not commission_link or 'data-missionary-detail' in commission_link.group(0):
        fail(errors, 'missionary.html: scripture commission link must reach shared scripture reader directly')
    if missionary.count('data-missionary-detail=') != 9:
        fail(errors, "missionary.html: expected seven artwork and two non-scripture study-link detail triggers")
    for key in missionary_detail_keys:
        if f'data-missionary-detail-content="{key}"' not in missionary:
            fail(errors, f"missionary.html: detail content missing for {key}")
    for marker in (
        'missionary-details.js?v=20260905-viewport',
        'id="missionaryDetailDialog"',
        'id="missionaryDetailFullImage"',
        'id="missionaryDetailSource"',
        'aria-haspopup="dialog"',
        'View Full-Size Image',
    ):
        if marker not in missionary:
            fail(errors, f"missionary.html: artwork detail marker missing: {marker}")

    missionary_detail_js_path = ROOT / "missionary-details.js"
    if not missionary_detail_js_path.exists() or missionary_detail_js_path.stat().st_size == 0:
        fail(errors, "missionary-details.js missing or empty")
    else:
        missionary_detail_js = missionary_detail_js_path.read_text(encoding="utf-8")
        for marker in (
            "dialog.showModal()",
            "dialog.close()",
            "dialog.addEventListener('cancel'",
            "event.metaKey",
            "returnFocus.focus({ preventScroll: true })",
            "document.body.classList.add('fc-dialog-open')",
        ):
            if marker not in missionary_detail_js:
                fail(errors, f"missionary-details.js: accessibility or interaction marker missing: {marker}")

    missionary_css = (ROOT / "missionary.css").read_text(encoding="utf-8")
    for marker in (
        ".fc-missionary-detail-dialog",
        ".fc-missionary-detail-dialog::backdrop",
        ".fc-missionary-detail-shell",
        ".fc-missionary-detail-actions",
    ):
        if marker not in missionary_css:
            fail(errors, f"missionary.css: artwork detail presentation marker missing: {marker}")

    for study_page in (ROOT / "art-study").glob("*.html"):
        page = study_page.read_text(encoding="utf-8")
        if not re.search(r'<figure[^>]*>\s*<a href="\.\./art/[^\"]+"', page, re.S):
            fail(errors, f"{study_page.relative_to(ROOT)}: featured artwork must open its full-resolution source")

    ask = (ROOT / "ask.html").read_text(encoding="utf-8")
    if '<header class="ask-hero"' in ask:
        fail(errors, "ask.html: legacy text-over-image hero remains")
    answers = (ROOT / "answers.html").read_text(encoding="utf-8")
    if '<header class="answer-hero"' in answers:
        fail(errors, "answers.html: legacy text-over-image hero remains")

    if errors:
        print("focusChrist UNIFIED EXPERIENCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist UNIFIED EXPERIENCE QA PASSED")
    print(f"Public pages checked: {len(PUBLIC_PAGES)}")
    print("Brand casing, shared design system, image-first heroes, unified footers, Art wiring, and hardened Pioneer conversation context/palette verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
