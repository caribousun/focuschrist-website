from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ROOT_PAGES = [
    "index.html", "ask.html", "answers.html", "art.html", "pioneers.html",
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


def main() -> int:
    errors: list[str] = []

    design = ROOT / "site-system.css"
    if not design.exists() or design.stat().st_size == 0:
        fail(errors, "site-system.css missing or empty")
    else:
        css = design.read_text(encoding="utf-8")
        for marker in (
            "--fc-bg", "--fc-standard", ".fc-visual-hero", ".fc-page-intro",
            ".fc-card", ".fc-button", ".fc-footer", "prefers-reduced-motion",
        ):
            if marker not in css:
                fail(errors, f"site-system.css missing design-system marker: {marker}")

    for relative in PUBLIC_PAGES:
        path = ROOT / relative
        if not path.exists() or path.stat().st_size == 0:
            fail(errors, f"{relative}: missing or empty")
            continue
        text = path.read_text(encoding="utf-8")
        system_href = expected_system_href(relative)
        if f'href="{system_href}"' not in text:
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

    pioneer_js = ROOT / "pioneer-experience.js"
    if not pioneer_js.exists() or pioneer_js.stat().st_size == 0:
        fail(errors, "pioneer-experience.js missing or empty")
    else:
        js = pioneer_js.read_text(encoding="utf-8")
        for marker in (
            "window.sendMessage", "window.clearChat", "Continue the conversation",
            "Ask a follow-up question", "textContent", "positionAnswer",
            "conversationHistory", "pioneerComposerLabel",
        ):
            if marker not in js:
                fail(errors, f"pioneer-experience.js missing conversation-parity marker: {marker}")
        if "message.innerHTML" in js:
            fail(errors, "pioneer-experience.js unsafe message.innerHTML renderer detected")

    art = (ROOT / "art.html").read_text(encoding="utf-8")
    if "art-experience.css" not in art:
        fail(errors, "art.html: unified Art presentation stylesheet missing")

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
    print("Brand casing, shared design system, image-first heroes, unified footers, Art wiring, and Pioneer conversation parity verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
