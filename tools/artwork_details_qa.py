from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "index.html": 3,
    "ask.html": 5,
    "answers.html": 9,
    "answers/death-of-a-child.html": 2,
    "answers/divorce-and-faith.html": 1,
    "church-history.html": 7,
    "art.html": 4,
    "pioneers.html": 10,
}
ROOT_VIEWER_PAGES = (*PAGES, "missionary.html")
ART_STUDY_PAGES = (
    "art-study/the-living-christ.html",
    "art-study/the-good-shepherd.html",
    "art-study/suffer-the-little-children.html",
    "art-study/be-still.html",
)


def main() -> int:
    errors: list[str] = []
    all_trigger_keys: list[str] = []
    all_record_keys: list[str] = []

    for relative, expected_count in PAGES.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        trigger_keys = re.findall(r'data-artwork-detail="([^"]+)"', text)
        record_keys = re.findall(r'data-artwork-detail-content="([^"]+)"', text)
        all_trigger_keys.extend(relative + ":" + key for key in trigger_keys)
        all_record_keys.extend(relative + ":" + key for key in record_keys)

        if len(trigger_keys) != expected_count:
            errors.append(f"{relative}: expected {expected_count} artwork detail triggers, found {len(trigger_keys)}")
        if len(record_keys) != expected_count:
            errors.append(f"{relative}: expected {expected_count} artwork detail records, found {len(record_keys)}")
        if sorted(trigger_keys) != sorted(record_keys):
            errors.append(f"{relative}: trigger and record keys do not match")
        if text.count('id="artworkDetailDialog"') != 1:
            errors.append(f"{relative}: shared artwork detail dialog missing or duplicated")
        if text.count('id="artworkDetailStudy" hidden') != 1:
            errors.append(f"{relative}: optional study action must start hidden exactly once")
        if re.search(r'id="artworkDetailStudy"[^>]*href=', text):
            errors.append(f"{relative}: hidden study action must not have a default destination")
        prefix = "../" if "/" in relative else ""
        for marker in (
            'href="artwork-details.css?v=20260905-viewport"',
            'src="artwork-details.js?v=20260905-home-study"',
            'id="artworkDetailSource"',
            'id="artworkDetailStudy" hidden',
            'id="artworkDetailFullImage"',
            'data-artwork-detail-close',
            'aria-haspopup="dialog"',
        ):
            if marker.startswith(('href="', 'src="')):
                marker = marker.replace('="', '="' + prefix, 1)
            if marker not in text:
                errors.append(f"{relative}: missing artwork detail marker: {marker}")

        for attr in ("data-detail-image", "data-detail-full"):
            for asset in re.findall(fr'{attr}="([^"]+)"', text):
                if asset.startswith(("http://", "https://", "#")):
                    continue
                target = (path.parent / urlsplit(asset).path).resolve()
                if not target.is_relative_to(ROOT.resolve()) or not target.exists() or target.stat().st_size == 0:
                    errors.append(f"{relative}: missing local artwork asset: {asset}")

        sources = re.findall(r'data-detail-source="([^"]+)"', text)
        if len(sources) != expected_count or any(not source.startswith("https://") for source in sources):
            errors.append(f"{relative}: every record must have one HTTPS official source")

    if len(all_trigger_keys) != 41 or len(all_record_keys) != 41:
        errors.append("site-wide non-Mission artwork detail total must be exactly 41")
    if len(set(all_trigger_keys)) != 41 or len(set(all_record_keys)) != 41:
        errors.append("site-wide artwork detail keys must be unique")

    missionary = (ROOT / "missionary.html").read_text(encoding="utf-8")
    mission_image_triggers = re.findall(
        r'<a[^>]+data-missionary-detail="[^"]+"[^>]*>\s*(?:<picture>)?\s*<img|'
        r'<a[^>]+data-missionary-detail="[^"]+"[^>]*>\s*<picture>',
        missionary,
        re.S,
    )
    if len(mission_image_triggers) != 7:
        errors.append(f"missionary.html: expected 7 image detail triggers, found {len(mission_image_triggers)}")
    if "missionary.css?v=20260906-mission-intro-fit" not in missionary:
        errors.append("missionary.html: centered close-control stylesheet version missing")
    mission_records = re.findall(r'data-missionary-detail-content="([^"]+)"', missionary)
    if len(mission_records) != 9 or len(set(mission_records)) != 9:
        errors.append(f"missionary.html: expected 9 unique detail records, found {len(mission_records)}")

    art = (ROOT / "art.html").read_text(encoding="utf-8")
    study_links = {
        relative: len(re.findall(r'data-detail-study="[^"]+"', (ROOT / relative).read_text(encoding="utf-8")))
        for relative in PAGES
    }
    expected_studies = {"art.html": 4, "index.html": 3, "ask.html": 5, "answers.html": 9, "answers/death-of-a-child.html": 2, "answers/divorce-and-faith.html": 1}
    for relative, count in study_links.items():
        if count != expected_studies.get(relative, 0):
            errors.append(f"{relative}: unexpected related study count {count}")
        for study_path in re.findall(r'data-detail-study="([^"]+)"', (ROOT / relative).read_text(encoding="utf-8")):
            target = (ROOT / relative).parent / study_path
            if not target.resolve().is_relative_to(ROOT.resolve()) or not target.is_file():
                errors.append(f"{relative}: related study missing: {study_path}")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if len(re.findall(r'data-detail-topic="[^"]+"', home)) != 3:
        errors.append("all three Home artworks need contextual Ask topics")
    for study_path in re.findall(r'data-detail-study="([^"]+)"', home):
        target = (ROOT / study_path).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            errors.append(f"index.html: related study missing: {study_path}")
    for study_path in re.findall(r'data-detail-study="([^"]+)"', art):
        target = (ROOT / study_path).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.exists():
            errors.append(f"art.html: complete study page does not exist: {study_path}")

    gallery_section = art.split('<div class="gallery">', 1)[1].split('data-focuschrist-featured-art-study', 1)[0]
    if "data-artwork-detail=" in gallery_section:
        errors.append("art.html: main gallery must retain its existing dedicated viewer")

    for relative in ART_STUDY_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "data-artwork-detail=" in text:
            errors.append(f"{relative}: dedicated study page artwork should retain direct full-size behavior")

    pioneer = (ROOT / "pioneers.html").read_text(encoding="utf-8", errors="replace")
    pioneer_hero = re.search(r'<a class="fc-visual-hero fc-visual-hero--history"[^>]*>', pioneer)
    if not pioneer_hero or "data-artwork-detail=" in pioneer_hero.group(0):
        errors.append("pioneers.html: Pioneer hero behavior changed or was incorrectly enrolled")

    for relative in ROOT_VIEWER_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        for marker in (
            'href="full-image-viewer.css?v=20260905-viewport"',
            'src="full-image-viewer.js?v=20260905-viewport"',
        ):
            if "/" in relative and '="../' not in marker:
                marker = marker.replace('="', '="../', 1)
            if text.count(marker) != 1:
                errors.append(f"{relative}: full-image viewer asset must load exactly once: {marker}")

    for relative in ART_STUDY_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for marker in (
            'href="../full-image-viewer.css?v=20260905-viewport"',
            'src="../full-image-viewer.js?v=20260905-viewport"',
        ):
            if "/" in relative and '="../' not in marker:
                marker = marker.replace('="', '="../', 1)
            if text.count(marker) != 1:
                errors.append(f"{relative}: full-image viewer asset must load exactly once: {marker}")

    viewer_documents = [
        (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        for relative in (*ROOT_VIEWER_PAGES, *ART_STUDY_PAGES)
    ]
    viewer_triggers = sum(text.count("data-full-image-viewer") for text in viewer_documents)
    if viewer_triggers != 24:
        errors.append(f"same-page full-image viewer must have exactly 24 scoped triggers, found {viewer_triggers}")
    if 'id="artworkDetailFullImage" href="#" target="_blank" rel="noopener noreferrer" data-full-image-viewer aria-haspopup="dialog"' not in art:
        errors.append("shared artwork full-size action is not enrolled in the same-page viewer")
    if 'id="missionaryDetailFullImage" href="#" target="_blank" rel="noopener noreferrer" data-full-image-viewer aria-haspopup="dialog"' not in missionary:
        errors.append("Mission full-size action is not enrolled in the same-page viewer")
    if 'fc-visual-hero--history' not in pioneer or 'data-full-image-viewer' not in pioneer:
        errors.append("Pioneer hero must retain its approved full-image action through the same-page viewer")
    if pioneer.count("data-full-image-viewer") != 12:
        errors.append("Pioneer page must retain its hero viewer, ten artwork fallbacks, and the detail-dialog full-size action")

    full_assets: list[str] = []
    for relative in (*PAGES, "missionary.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for asset in re.findall(r'data-detail-full="([^"]+)"', text):
            full_assets.append(asset)
            target = ((ROOT / relative).parent / urlsplit(asset).path).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.exists() or target.stat().st_size == 0:
                errors.append(f"{relative}: missing full-image source: {asset}")
    if len(full_assets) != 50:
        errors.append(f"expected 50 artwork detail full-image sources, found {len(full_assets)}")

    detail_paragraphs: list[str] = []
    for relative in (*PAGES, "missionary.html"):
        detail_paragraphs.extend(
            re.findall(
                r'<p data-detail-paragraph>(.*?)</p>',
                (ROOT / relative).read_text(encoding="utf-8"),
                re.S,
            )
        )
    flattened_copy = " ".join(detail_paragraphs).lower()
    for phrase in (
        "documentary",
        "does not assert",
        "provenance",
        "without claiming",
        "historical portrayal",
        "contemporary portrayal",
        "not one documented",
        "not a documented",
    ):
        if phrase in flattened_copy:
            errors.append(f"artwork detail copy contains generic disclaimer wording: {phrase}")

    js = (ROOT / "artwork-details.js").read_text(encoding="utf-8")
    for marker in (
        "dialog.showModal()",
        "event.metaKey",
        "event.ctrlKey",
        "event.shiftKey",
        "event.altKey",
        "event.target === dialog",
        "returnFocus.focus({ preventScroll: true })",
        "document.body.classList.add('fc-dialog-open')",
        "dialog.addEventListener('cancel'",
        "study.hidden = false",
        "study.hidden = true",
        "study.removeAttribute('href')",
    ):
        if marker not in js:
            errors.append(f"artwork-details.js: missing interaction marker: {marker}")

    full_viewer_js = (ROOT / "full-image-viewer.js").read_text(encoding="utf-8")
    for marker in (
        "dialog.showModal()",
        "event.metaKey",
        "event.ctrlKey",
        "event.shiftKey",
        "event.altKey",
        "event.target === stage",
        "returnFocus.focus({ preventScroll: true })",
        "dialog.addEventListener('cancel'",
        "document.body.classList.add('fc-full-image-open')",
        "image.removeAttribute('src')",
    ):
        if marker not in full_viewer_js:
            errors.append(f"full-image-viewer.js: missing interaction marker: {marker}")

    css = (ROOT / "artwork-details.css").read_text(encoding="utf-8")
    for marker in (
        ".fc-artwork-detail-dialog::backdrop",
        "margin: auto;",
        "@media (max-width: 820px)",
        ".fc-artwork-detail-close::before",
        ".fc-artwork-detail-close::after",
        "translate(-50%, -50%) rotate(45deg)",
        "translate(-50%, -50%) rotate(-45deg)",
        ".fc-artwork-detail-actions [hidden]",
        "display: none !important;",
    ):
        if marker not in css:
            errors.append(f"artwork-details.css: missing presentation marker: {marker}")

    mission_css = (ROOT / "missionary.css").read_text(encoding="utf-8")
    mission_dialog_rule = re.search(r'\.fc-missionary-detail-dialog\s*\{([^}]+)\}', mission_css, re.S)
    if not mission_dialog_rule or "margin: auto;" not in mission_dialog_rule.group(1):
        errors.append("missionary.css: artwork detail dialog must remain viewport-centered")

    for marker in (
        ".fc-missionary-detail-close::before",
        ".fc-missionary-detail-close::after",
        "translate(-50%, -50%) rotate(45deg)",
        "translate(-50%, -50%) rotate(-45deg)",
    ):
        if marker not in mission_css:
            errors.append(f"missionary.css: missing centered close-control marker: {marker}")

    full_viewer_css = (ROOT / "full-image-viewer.css").read_text(encoding="utf-8")
    for marker in (
        ".fc-full-image-viewer::backdrop",
        "object-fit: contain",
        ".fc-full-image-close::before",
        ".fc-full-image-close::after",
        "translate(-50%, -50%) rotate(45deg)",
        "translate(-50%, -50%) rotate(-45deg)",
        "@media (max-width: 640px)",
    ):
        if marker not in full_viewer_css:
            errors.append(f"full-image-viewer.css: missing presentation marker: {marker}")

    if errors:
        print("Artwork detail QA: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Artwork detail QA: PASS")
    print("41 non-Mission artwork triggers and 7 Mission artwork triggers verified")
    print("Same-page full-image viewing, sacred detail copy, and intentional interaction scope verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
