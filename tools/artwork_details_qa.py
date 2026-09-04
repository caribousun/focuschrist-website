from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "index.html": 1,
    "ask.html": 2,
    "answers.html": 3,
    "church-history.html": 7,
    "art.html": 4,
}


def main() -> int:
    errors: list[str] = []
    all_trigger_keys: list[str] = []
    all_record_keys: list[str] = []

    for relative, expected_count in PAGES.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        trigger_keys = re.findall(r'data-artwork-detail="([^"]+)"', text)
        record_keys = re.findall(r'data-artwork-detail-content="([^"]+)"', text)
        all_trigger_keys.extend(trigger_keys)
        all_record_keys.extend(record_keys)

        if len(trigger_keys) != expected_count:
            errors.append(f"{relative}: expected {expected_count} artwork detail triggers, found {len(trigger_keys)}")
        if len(record_keys) != expected_count:
            errors.append(f"{relative}: expected {expected_count} artwork detail records, found {len(record_keys)}")
        if sorted(trigger_keys) != sorted(record_keys):
            errors.append(f"{relative}: trigger and record keys do not match")
        if text.count('id="artworkDetailDialog"') != 1:
            errors.append(f"{relative}: shared artwork detail dialog missing or duplicated")
        for marker in (
            'href="artwork-details.css?v=20260904-1"',
            'src="artwork-details.js?v=20260904-1"',
            'id="artworkDetailSource"',
            'id="artworkDetailStudy"',
            'id="artworkDetailFullImage"',
            'data-artwork-detail-close',
            'aria-haspopup="dialog"',
        ):
            if marker not in text:
                errors.append(f"{relative}: missing artwork detail marker: {marker}")

        for attr in ("data-detail-image", "data-detail-full"):
            for asset in re.findall(fr'{attr}="([^"]+)"', text):
                if asset.startswith(("http://", "https://", "#")):
                    continue
                target = (path.parent / asset).resolve()
                if not target.is_relative_to(ROOT.resolve()) or not target.exists() or target.stat().st_size == 0:
                    errors.append(f"{relative}: missing local artwork asset: {asset}")

        sources = re.findall(r'data-detail-source="([^"]+)"', text)
        if len(sources) != expected_count or any(not source.startswith("https://") for source in sources):
            errors.append(f"{relative}: every record must have one HTTPS official source")

    if len(all_trigger_keys) != 17 or len(all_record_keys) != 17:
        errors.append("site-wide non-Mission artwork detail total must be exactly 17")
    if len(set(all_trigger_keys)) != 17 or len(set(all_record_keys)) != 17:
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
    if "missionary.css?v=20260904-5" not in missionary:
        errors.append("missionary.html: centered close-control stylesheet version missing")

    art = (ROOT / "art.html").read_text(encoding="utf-8")
    gallery_section = art.split('<div class="gallery">', 1)[1].split('data-focuschrist-featured-art-study', 1)[0]
    if "data-artwork-detail=" in gallery_section:
        errors.append("art.html: main gallery must retain its existing dedicated viewer")

    for relative in (
        "art-study/the-living-christ.html",
        "art-study/the-good-shepherd.html",
        "art-study/suffer-the-little-children.html",
        "art-study/be-still.html",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "data-artwork-detail=" in text:
            errors.append(f"{relative}: dedicated study page artwork should retain direct full-size behavior")

    pioneer = (ROOT / "pioneers.html").read_text(encoding="utf-8", errors="replace")
    if 'class="fc-visual-hero fc-visual-hero--history"' not in pioneer or "data-artwork-detail=" in pioneer:
        errors.append("pioneers.html: Pioneer hero behavior changed or was incorrectly enrolled")

    js = (ROOT / "artwork-details.js").read_text(encoding="utf-8")
    for marker in (
        "dialog.showModal()",
        "event.metaKey",
        "event.ctrlKey",
        "event.shiftKey",
        "event.altKey",
        "event.target === dialog",
        "returnFocus.focus()",
        "document.body.classList.add('fc-dialog-open')",
        "dialog.addEventListener('cancel'",
    ):
        if marker not in js:
            errors.append(f"artwork-details.js: missing interaction marker: {marker}")

    css = (ROOT / "artwork-details.css").read_text(encoding="utf-8")
    for marker in (
        ".fc-artwork-detail-dialog::backdrop",
        "@media (max-width: 820px)",
        ".fc-artwork-detail-close::before",
        ".fc-artwork-detail-close::after",
        "translate(-50%, -50%) rotate(45deg)",
        "translate(-50%, -50%) rotate(-45deg)",
    ):
        if marker not in css:
            errors.append(f"artwork-details.css: missing presentation marker: {marker}")

    mission_css = (ROOT / "missionary.css").read_text(encoding="utf-8")
    for marker in (
        ".fc-missionary-detail-close::before",
        ".fc-missionary-detail-close::after",
        "translate(-50%, -50%) rotate(45deg)",
        "translate(-50%, -50%) rotate(-45deg)",
    ):
        if marker not in mission_css:
            errors.append(f"missionary.css: missing centered close-control marker: {marker}")

    if errors:
        print("Artwork detail QA: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Artwork detail QA: PASS")
    print("17 new artwork triggers and 7 existing Mission artwork triggers verified")
    print("Heroes, main Art gallery, Art and Study page images, and video thumbnails remain excluded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
