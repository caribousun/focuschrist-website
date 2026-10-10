from __future__ import annotations

from pathlib import Path
import re
import json
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
VISIBLE_TOPIC_ROUTES = frozenset({
    'answers/abrahamic-covenant.html', 'answers/what-is-eternal-marriage.html',
    'general-conference.html', 'history/eleazer-miller.html',
    'history/john-rowe-moyle.html', 'history/john-tanner.html',
})
VISIBLE_HERO_ROUTES = frozenset({
    'about.html',
    'answers.html',
    'answers/aaronic-priesthood-restoration.html',
    'answers/are-latter-day-saints-christian.html',
    'answers/bible-and-book-of-mormon-together.html',
    'answers/death-of-a-child.html',
    'answers/divorce-and-faith.html',
    'answers/faith-in-jesus-christ-during-trials.html',
    'answers/god-our-heavenly-father.html',
    'answers/grief-and-faith.html',
    'answers/holy-ghost.html',
    'answers/jesus-christ-latter-day-saint-beliefs.html',
    'answers/look-unto-me-doctrine-and-covenants-6-36.html',
    'answers/plan-of-salvation.html',
    'answers/prayer-and-personal-revelation.html',
    'answers/restored-church-of-jesus-christ.html',
    'answers/stand-forever.html',
    'answers/what-happens-after-death.html',
    'answers/what-is-eternal-marriage.html',
    'answers/what-is-the-book-of-mormon.html',
    'answers/who-was-joseph-smith.html',
    'answers/why-families-are-important.html',
    'answers/why-latter-day-saints-build-temples.html',
    'art-study/be-still.html',
    'art-study/suffer-the-little-children.html',
    'art-study/the-good-shepherd.html',
    'art.html',
    'ask.html',
    'atonement.html',
    'birth-of-christ.html',
    'book-of-mormon-evidences.html',
    'missionary.html',
    'timeline.html',
    'watch.html',
})
TOPIC_HERO_PAGES = {p["page"] for p in json.loads((ROOT / "docs/sitewide-hero-production-plan.json").read_text(encoding="utf-8"))["plans"]}
PAGES = {
    "index.html": 3,
    "ask.html": 5,
    "answers.html": 9,
    "answers/death-of-a-child.html": 2,
    "answers/divorce-and-faith.html": 1,
    "church-history.html": 8,
    "art.html": 4,
    "pioneers.html": 31,
}
ROOT_VIEWER_PAGES = (*PAGES, "missionary.html", "general-conference.html")
ART_STUDY_PAGES = (
    "art-study/the-living-christ.html",
    "art-study/the-good-shepherd.html",
    "art-study/suffer-the-little-children.html",
    "art-study/be-still.html",
)
ART_STUDY_HEROES = {
    "art-study/the-living-christ.html": ("../assets/heroes/topics/living-christ-full.webp", "topic-living-christ"),
    "art-study/the-good-shepherd.html": ("../art/The-Good-Shephard.jpg", "good-shepherd-art"),
    "art-study/suffer-the-little-children.html": ("../art/Suffer-the-Little-Children-approved-20260929.webp", "little-children-art"),
    "art-study/be-still.html": ("../art/Be-Still.png", "be-still-art"),
}


def local_target(page: Path, value: str) -> Path:
    # A leading slash is a site-root URL, not an operating-system root.
    asset_path = urlsplit(value).path
    return (ROOT / asset_path.lstrip("/") if asset_path.startswith("/") else page.parent / asset_path).resolve()


TIMELINE_STUDY_HEROES = {
    "timelines/life-of-christ-journey-map.html": ("../answers/jesus-christ-latter-day-saint-beliefs.html#nested-page-title", "../assets/heroes/topics/jesus-desktop.webp", "../assets/heroes/topics/jesus-mobile.webp"),
    "timelines/latter-day-saint-church-history-timeline.html": ("../church-history.html#history-first-vision-title", "../assets/timelines/church-history-grove.webp", None),
    "timelines/willie-and-martin-handcart-map.html": ("../pioneers.html#pioneer-page-title", "../assets/heroes/pioneers.webp", None),
}


TIMELINE_PANEL_RECORDS = {
    'timelines/life-of-christ-journey-map.html': ('timeline-life', '../assets/heroes/topics/jesus-full.webp'),
    'timelines/latter-day-saint-church-history-timeline.html': ('timeline-history', '../assets/timelines/church-history-grove.webp'),
    'timelines/willie-and-martin-handcart-map.html': ('timeline-handcart', '../assets/heroes/pioneers.webp'),
}


def timeline_panel_record(script: str, key: str) -> dict:
    # The three additive records are JSON. Reject absent/duplicate/opaque records.
    matches = list(re.finditer(r'"' + re.escape(key) + r'"\s*:\s*', script))
    if len(matches) != 1:
        return {}
    try:
        record, _ = json.JSONDecoder().raw_decode(script[matches[0].end():])
        return record if isinstance(record, dict) else {}
    except ValueError:
        return {}


def timeline_study_hero_errors(relative: str, page: str, script: str | None = None) -> list[str]:
    from bs4 import BeautifulSoup
    href, src, mobile = TIMELINE_STUDY_HEROES[relative]
    key, full = TIMELINE_PANEL_RECORDS[relative]
    dom = BeautifulSoup(page, "html.parser")
    heroes = dom.select(".fc-visual-hero")
    if len(heroes) != 1:
        return [f"{relative}: expected one exact timeline study-reference hero"]
    hero = heroes[0]
    errors = []
    if hero.name != "a" or hero.get("href") != full or not hero.get("aria-label"):
        errors.append(f"{relative}: timeline hero must retain its accessible image fallback")
    if not hero.has_attr('data-hero-viewer') or hero.get('data-hero-record') != key or hero.get('data-hero-study') != href or hero.get('aria-haspopup') != 'dialog' or not hero.get('data-full-image-alt'):
        errors.append(f"{relative}: timeline panel must retain its exact record and owning study")
    record = timeline_panel_record(script if script is not None else (ROOT / 'hero-details.js').read_text(encoding='utf-8'), key)
    if record.get('study') != href.removeprefix('../') or not record.get('studyLabel') or not record.get('source') or not record.get('paragraphs'):
        errors.append(f"{relative}: actual panel record must retain the owning-study pill and reflection")
    images = hero.select("img")
    if len(images) != 1 or images[0].get("src") != src or not images[0].get("alt"):
        errors.append(f"{relative}: timeline hero image or alternative text differs")
    sources = [n.get("srcset") for n in hero.select("source")]
    if sources != ([mobile] if mobile else []):
        errors.append(f"{relative}: timeline hero responsive source differs")
    if any(hero.has_attr(a) for a in ('data-full-image-viewer', 'data-artwork-detail', 'onclick')):
        errors.append(f"{relative}: normal artwork details must precede full-size viewing")
    for name, version in [('hero-details.js', '20261007-timeline-panels-1'), ('full-image-viewer.js', '20261009-titled-downloads-1'), ('full-image-viewer.css', '20261007-viewer-controls-1'), ('hero-details.css', '20260909-warm'), ('artwork-details.css', '20260909-warm'), ('artwork-actions.css', '20261004-explicit-grid-1')]:
        nodes = [n for n in dom.select('script[src],link[href]') if urlsplit(n.get('src', n.get('href', ''))).path == '../' + name]
        if len(nodes) != 1 or nodes[0].get('src', nodes[0].get('href')) != '../' + name + '?v=' + version:
            errors.append(f'{relative}: exact panel dependency missing, duplicated or stale: {name}')
    path = ROOT / relative
    for asset in [src, full] + ([mobile] if mobile else []):
        if not local_target(path, asset).is_file():
            errors.append(f"{relative}: timeline hero asset missing: {asset}")
    target = local_target(path, href)
    if not target.is_file() or not BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser").find(id=urlsplit(href).fragment):
        errors.append(f"{relative}: exact study destination missing")
    return errors


HISTORY_HERO_UNITS = {
    'history/john-tanner.html': 'tanner-healing-witness',
    'history/eleazer-miller.html': 'miller-teaching-brigham',
    'history/john-rowe-moyle.html': 'moyle-handcart-journey',
}


def history_topic_hero_errors(relative, page, story, ready):
    from bs4 import BeautifulSoup
    errors = []
    unit = HISTORY_HERO_UNITS[relative]
    selected = story.get('hero', story['units'][0])
    if selected['id'] != unit or story.get('hero_unit_id') != unit:
        errors.append(f'{relative}: configured hero differs from exact reviewed scene')
    dom = BeautifulSoup(page, 'html.parser')
    figures = dom.select('figure.fc-life-hero')
    if len(figures) != 1 or figures[0].get('data-topic-art') != unit:
        errors.append(f'{relative}: missing exact reviewed topic hero')
    else:
        figure = figures[0]
        anchors = figure.select('a.fc-visual-hero')
        if len(anchors) != 1 or anchors[0].get('href') != '../' + ready[unit]['full'] or not figure.select_one('figcaption[data-picture-panel-copy][hidden]'):
            errors.append(f'{relative}: hero source or study metadata differs')
    topic_version = '20261009-settled-continue-2'
    if page.count('../topic-artwork-details.js?v=' + topic_version) != 1 or 'hero-details.js' in page or 'data-hero-viewer' in page:
        errors.append(f'{relative}: hero must have exactly one topic controller')
    return errors


def emma_portrait_errors(text):
    records = re.findall(r'<article\b[^>]*data-artwork-detail-content="history-emma-portrait"[^>]*>', text)
    markers = (
        'data-detail-image="assets/portraits/emma-smith-natural-20261008.png"',
        'data-detail-full="assets/portraits/emma-smith-natural-20261008.png"',
        'data-detail-source="https://www.churchofjesuschrist.org/study/history/topics/emma-hale-smith?lang=eng"',
        'data-detail-study="history/emma-hale-smith.html"',
    )
    return [] if len(records) == 1 and all(x in records[0] for x in markers) else [
        "Church History Emma portrait must retain the reviewed natural portrait, official biography and whole-life journey"]


def emma_reference_errors(page, history):
    errors = []
    figures = re.findall(r'<figure\b[^>]*class="fc-life-hero"[^>]*>[\s\S]*?</figure>', page)
    heroes = re.findall(r'<a\b[^>]*class="[^"\n]*\bfc-visual-hero\b[^"\n]*"[^>]*>', page)
    markers = (
        'data-artwork-reference="history-harmony"',
        'data-linked-picture-reference="history-harmony"',
        'href="../church-history.html#history-harmony-title"',
        'src="../assets/history/joseph-emma-harmony-1400.webp"',
        'width="1400" height="467"',
    )
    if len(figures) != 1 or len(heroes) != 1 or any(x not in figures[0] for x in markers):
        errors.append("Emma opening must retain one exact linked Harmony reference hero")
    elif any(x in figures[0] for x in ('data-hero-viewer', 'data-topic-art=', 'data-full-image-viewer')):
        errors.append("Emma Harmony opening is a study link, not a local image modal")
    if history.count('id="history-harmony-title"') != 1:
        errors.append("Emma Harmony destination heading must exist exactly once")
    for marker in (
        'src="../full-image-viewer.js?v=20261009-titled-downloads-1"',
        'src="../topic-artwork-details.js?v=20261009-settled-continue-2"',
    ):
        if page.count(marker) != 1:
            errors.append("Emma study dependency missing or duplicated: " + marker)
    if re.search(r'<script\b[^>]*src="[^"\n]*(?:hero-image-source|hero-details)\.js', page):
        errors.append("Emma must not load an unmapped hero helper or legacy modal controller")
    return errors


def main() -> int:
    assert local_target(ROOT / "404.html", "/assets/heroes/home.webp") == (ROOT / "assets/heroes/home.webp").resolve()
    assert local_target(ROOT / "answers/example.html", "../assets/heroes/home.webp?x=1") == (ROOT / "assets/heroes/home.webp").resolve()
    assert not local_target(ROOT / "404.html", "/assets/heroes/qa-missing-image.webp").is_file()
    errors: list[str] = []
    from visual_rhythm_art_qa import check as check_rhythm_art, self_test as rhythm_art_self_test, without_reviewed_figure
    rhythm_art_self_test()
    rhythm_records = check_rhythm_art()
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
        detail_version = "20260908-continue-lesson" if relative in {"answers/death-of-a-child.html", "answers/divorce-and-faith.html"} else "20260905-home-study"
        for marker in (
            'href="artwork-details.css?v=20260909-warm"',
            f'src="artwork-details.js?v={detail_version}"',
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
                target = local_target(path, asset)
                if not target.is_relative_to(ROOT.resolve()) or not target.exists() or target.stat().st_size == 0:
                    errors.append(f"{relative}: missing local artwork asset: {asset}")

        sources = re.findall(r'data-detail-source="([^"]+)"', text)
        if len(sources) != expected_count or any(not source.startswith("https://") for source in sources):
            errors.append(f"{relative}: every record must have one HTTPS official source")

    if len(all_trigger_keys) != 63 or len(all_record_keys) != 63:
        errors.append("site-wide non-Mission artwork detail total must be exactly 63")
    if len(set(all_trigger_keys)) != 63 or len(set(all_record_keys)) != 63:
        errors.append("site-wide artwork detail keys must be unique")

    history_text = (ROOT / "church-history.html").read_text(encoding="utf-8")
    errors.extend(emma_portrait_errors(history_text))
    emma_page = (ROOT / "history/emma-hale-smith.html").read_text(encoding="utf-8")
    errors.extend(emma_reference_errors(emma_page, history_text))

    missionary = (ROOT / "missionary.html").read_text(encoding="utf-8")
    mission_image_triggers = re.findall(
        r'<a[^>]+data-missionary-detail="[^"]+"[^>]*>\s*(?:<picture>)?\s*<img|'
        r'<a[^>]+data-missionary-detail="[^"]+"[^>]*>\s*<picture>',
        missionary,
        re.S,
    )
    if len(mission_image_triggers) != 11:
        errors.append(f"missionary.html: expected 11 image detail triggers, found {len(mission_image_triggers)}")
    if "missionary.css?v=20260923-enrichment-finish-1" not in missionary:
        errors.append("missionary.html: centered close-control stylesheet version missing")
    mission_records = re.findall(r'data-missionary-detail-content="([^"]+)"', missionary)
    if len(mission_records) != 13 or len(set(mission_records)) != 13:
        errors.append(f"missionary.html: expected 13 unique detail records, found {len(mission_records)}")

    art = (ROOT / "art.html").read_text(encoding="utf-8")
    study_links = {
        relative: len(re.findall(r'data-detail-study="[^"]+"', (ROOT / relative).read_text(encoding="utf-8")))
        for relative in PAGES
    }
    expected_studies = {"church-history.html": 1, "art.html": 4, "index.html": 3, "ask.html": 5, "answers.html": 9, "answers/death-of-a-child.html": 2, "answers/divorce-and-faith.html": 1, "pioneers.html": 21}
    for relative, count in study_links.items():
        if count != expected_studies.get(relative, 0):
            errors.append(f"{relative}: unexpected related study count {count}")
        for study_path in re.findall(r'data-detail-study="([^"]+)"', (ROOT / relative).read_text(encoding="utf-8")):
            destination = urlsplit(study_path)
            target = local_target(ROOT / relative, study_path)
            if not target.resolve().is_relative_to(ROOT.resolve()) or not target.is_file():
                errors.append(f"{relative}: related study missing: {study_path}")
            elif destination.fragment and f'id="{destination.fragment}"' not in target.read_text(encoding="utf-8"):
                errors.append(f"{relative}: related study anchor missing: {study_path}")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if len(re.findall(r'data-detail-topic="[^"]+"', home)) != 3:
        errors.append("all three Home artworks need contextual Ask topics")
    for study_path in re.findall(r'data-detail-study="([^"]+)"', home):
        target = local_target(ROOT / "index.html", study_path)
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            errors.append(f"index.html: related study missing: {study_path}")
    for study_path in re.findall(r'data-detail-study="([^"]+)"', art):
        target = local_target(ROOT / "index.html", study_path)
        if not target.is_relative_to(ROOT.resolve()) or not target.exists():
            errors.append(f"art.html: complete study page does not exist: {study_path}")

    gallery_section = art.split('<div class="gallery" id="art-gallery">', 1)[1].split('data-focuschrist-featured-art-study', 1)[0]
    if "data-artwork-detail=" in gallery_section:
        errors.append("art.html: main gallery must retain its existing dedicated viewer")

    for relative in ART_STUDY_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "data-artwork-detail=" in text:
            errors.append(f"{relative}: dedicated study page artwork should retain direct full-size behavior")
        asset, record = ART_STUDY_HEROES[relative]
        intrinsic = relative != 'art-study/the-living-christ.html'
        hero = re.search(r'<a[^>]*data-hero-viewer[^>]*>' + (r'\s*(?:<picture(?: class="fc-exact-hero-picture")?>\s*(?:<source[^>]*>\s*)+)?<img[^>]*>\s*(?:</picture>\s*)?</a>' if intrinsic else ''), text, re.S)
        if not hero:
            errors.append(f"{relative}: featured artwork hero with intrinsic image is missing")
        else:
            hero_text = hero.group(0)
            markers = [f'href="{asset}"', f'data-hero-record="{record}"']
            markers += [f'<img src="{asset}"'] if intrinsic else ['fc-topic-unique-hero', '--topic-hero-desktop:', '--topic-hero-mobile:']
            for marker in markers:
                if marker not in hero_text:
                    errors.append(f"{relative}: artwork hero mismatch: {marker}")
            if "assets/heroes/home.webp" in hero_text:
                errors.append(f"{relative}: generic Home hero fallback returned")
        for marker in (
            'href="../art-study-page.css?v=20260908-image-heroes"',
            ('src="../hero-details.js?v=20261006-visible-art-1"' if intrinsic else 'src="../hero-details.js?v=20260927-plan-study-1"'),
            'class="fc-page-intro-copy"',
            '>Begin Scripture Study</a>',
            'href="#study-resources">Explore Resources</a>',
            'id="study-resources"',
        ):
            if text.count(marker) != 1:
                errors.append(f"{relative}: enriched opening marker missing or duplicated: {marker}")
        if re.search(r'<figure[^>]*>.*?' + re.escape(asset) + r'.*?</figure>', text, re.S):
            errors.append(f"{relative}: featured artwork repeats below its hero")

    pioneer = (ROOT / "pioneers.html").read_text(encoding="utf-8", errors="replace")
    pioneer_hero = re.search(r'<a class="fc-visual-hero fc-visual-hero--history"[^>]*>', pioneer)
    if not pioneer_hero or "data-artwork-detail=" in pioneer_hero.group(0):
        errors.append("pioneers.html: Pioneer hero behavior changed or was incorrectly enrolled")

    for relative in ROOT_VIEWER_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        for marker in (
            'href="full-image-viewer.css?v=20261007-viewer-controls-1"',
            'src="full-image-viewer.js?v=20261009-titled-downloads-1"',
        ):
            if relative in VISIBLE_HERO_ROUTES | VISIBLE_TOPIC_ROUTES:
                marker = marker.replace('20260905-viewport', '20261006-versions-1').replace('20260914-reopen-1', '20261006-versions-1')
            if "/" in relative and '="../' not in marker:
                marker = marker.replace('="', '="../', 1)
            if text.count(marker) != 1:
                errors.append(f"{relative}: full-image viewer asset must load exactly once: {marker}")

    for relative in ART_STUDY_PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for marker in (
            'href="../full-image-viewer.css?v=20261007-viewer-controls-1"',
            'src="../full-image-viewer.js?v=20261009-titled-downloads-1"',
        ):
            if relative in VISIBLE_HERO_ROUTES | VISIBLE_TOPIC_ROUTES:
                marker = marker.replace('20260905-viewport', '20261006-versions-1').replace('20260914-reopen-1', '20261006-versions-1')
            if "/" in relative and '="../' not in marker:
                marker = marker.replace('="', '="../', 1)
            if text.count(marker) != 1:
                errors.append(f"{relative}: full-image viewer asset must load exactly once: {marker}")

    viewer_documents = [
        (without_reviewed_figure(relative, (ROOT / relative).read_text(encoding="utf-8"), rhythm_records[relative]) if relative in rhythm_records else (ROOT / relative).read_text(encoding="utf-8", errors="replace"))
        for relative in (*ROOT_VIEWER_PAGES, *ART_STUDY_PAGES)
    ]
    # Preserve the existing enriched-figure scope; supporting Art & Study
    # pictures are counted separately because they no longer carry viewer attrs.
    # Only subtract enriched figures that actually contain a bare viewer trigger.
    # Native topic panels (including History) have no such trigger to subtract.
    viewer_triggers = sum(
        text.count("data-full-image-viewer")
        - sum("data-full-image-viewer" in figure for figure in re.findall(
            r'<figure\b[^>]*data-enriched-study-art=[\s\S]*?</figure>', text))
        - sum("data-full-image-viewer" in anchor for anchor in re.findall(
            r'<a\b[^>]*data-enriched-study-art=[^>]*>', text))
        - text.count("data-five-picture-mandate")
        for text in viewer_documents
    )
    # Conference's opening now uses its own source-linked study panel first;
    # general_conference_qa.py verifies that migrated trigger explicitly.
    if viewer_triggers != 19:
        errors.append(f"same-page full-image viewer must have exactly 19 scoped triggers, found {viewer_triggers}")
    from study_gap_art_qa import sitewide_entries
    reviewed_supporting = sitewide_entries()
    for relative in ART_STUDY_PAGES:
        expected_supporting = 4 + sum(e['page'] == relative and not e['talk'] for e in reviewed_supporting)
        text = (ROOT / relative).read_text(encoding="utf-8")
        supporting = [anchor for anchor in re.findall(r'<a\b[^>]*>', text) if 'data-art-study-supporting' in anchor]
        if len(supporting) != expected_supporting or any('data-full-image-viewer' in anchor for anchor in supporting):
            errors.append(f"{relative}: requires {expected_supporting} manifest-bound supporting picture study triggers without direct full-size activation")
    if 'id="artworkDetailFullImage" href="#" target="_blank" rel="noopener noreferrer" data-full-image-viewer aria-haspopup="dialog"' not in art:
        errors.append("shared artwork full-size action is not enrolled in the same-page viewer")
    if 'id="missionaryDetailFullImage" href="#" target="_blank" rel="noopener noreferrer" data-full-image-viewer aria-haspopup="dialog"' not in missionary:
        errors.append("Mission full-size action is not enrolled in the same-page viewer")
    if 'fc-visual-hero--history' not in pioneer or 'data-full-image-viewer' not in pioneer:
        errors.append("Pioneer hero must retain its approved full-image action through the same-page viewer")
    if without_reviewed_figure("pioneers.html", pioneer, rhythm_records["pioneers.html"]).count("data-full-image-viewer") != 11:
        errors.append("Pioneer page must retain ten artwork fallbacks, and the detail-dialog full-size action")

    hero_pages = 0
    timeline_references = set()
    for path in ROOT.rglob("*.html"):
        page = path.read_text(encoding="utf-8")
        if not re.search(r'class="[^\"]*\bfc-visual-hero\b', page):
            continue
        hero_pages += 1
        relative = path.relative_to(ROOT).as_posix()
        if relative == "history/emma-hale-smith.html":
            # Validated unconditionally above, including missing/duplicate hero.
            hero_pages -= 1  # Linked Harmony reference is outside the 43 local modals.
            continue
        if relative in TIMELINE_STUDY_HEROES:
            timeline_references.add(relative)
            errors.extend(timeline_study_hero_errors(relative, page))
            hero_pages -= 1  # Three explicitly scoped panels, separate from the legacy baseline.
            continue
        prefix = "../" * (len(path.relative_to(ROOT).parts) - 1)
        if 'fc-hero-fullscreen' in page:
            errors.append(f"{relative}: hero must not display an overlay pill")
        history_pages = HISTORY_HERO_UNITS
        if relative in history_pages:
            # Eleazer has its own reviewed hero; the other two retain their first scene.
            stories = json.loads((ROOT / "docs/history-stories/stories.json").read_text(encoding="utf-8"))["stories"]
            story = next(x for x in stories if relative == f"history/{x['id']}.html")
            ready = json.loads((ROOT / "docs/history-stories/art-ready.json").read_text(encoding="utf-8"))
            if "artworks" in ready: ready = ready["artworks"]
            errors.extend(history_topic_hero_errors(relative, page, story, ready))
            unit = HISTORY_HERO_UNITS[relative]
            for original, replacement in (
                (f'data-topic-art="{unit}"', 'data-topic-art="wrong-scene"'),
                ('class="fc-life-hero"', 'class="wrong-hero"'),
                (f'href="../{ready[unit]["full"]}"', 'href="../assets/heroes/home.webp"'),
                ('data-picture-panel-copy hidden', 'data-picture-panel-copy'),
                ('../topic-artwork-details.js?v=20261009-settled-continue-2', '../topic-artwork-details.js?v=unknown'),
            ):
                mutated = page.replace(original, replacement, 1)
                assert mutated != page
                assert history_topic_hero_errors(relative, mutated, story, ready), 'History hero mutation escaped'
            assert history_topic_hero_errors(relative, page + '<figure class="fc-life-hero"></figure>', story, ready)
            assert history_topic_hero_errors(relative, page + '<script src="../topic-artwork-details.js?v=20261009-settled-continue-2"></script>', story, ready)
            assert history_topic_hero_errors(relative, page, dict(story, hero=dict(story['units'][0], id='wrong-scene')), ready)
            hero_pages -= 1  # Preserve the separate 41-page legacy controller baseline.
            continue
        hero_script = ("hero-details.js?v=20260927-plan-study-1" if relative in TOPIC_HERO_PAGES else "hero-details.js?v=20260927-plan-study-1" if relative == "birth-of-christ.html" else "hero-details.js?v=20260927-plan-study-1" if relative == "atonement.html" else "hero-details.js?v=20260927-plan-study-1" if relative == "joseph-smith-likeness.html" else "hero-details.js?v=20260927-plan-study-1" if relative == "book-of-mormon-evidences.html" else "hero-details.js?v=20260927-plan-study-1" if relative in ART_STUDY_PAGES else "hero-details.js?v=20260927-plan-study-1")
        if relative == "answers/settle-this-in-your-hearts.html":
            hero_script = "hero-details.js?v=20260927-plan-study-1"
        if relative == "answers/holy-ghost.html":
            hero_script = "hero-details.js?v=20260927-plan-study-1"
        if relative in {"joseph-smith-likeness.html","joseph-smith-portrait-research.html"}:
            hero_script = "hero-details.js?v=20261004-joseph-heroes-1"
        if relative in VISIBLE_HERO_ROUTES:
            hero_script = "hero-details.js?v=20261006-visible-art-1"
        if relative == "timeline.html" and relative not in VISIBLE_HERO_ROUTES:
            hero_script = "hero-details.js?v=20261002-timeline-1"
        viewer_css = "full-image-viewer.css?v=" + '20261007-viewer-controls-1'
        viewer_js = "full-image-viewer.js?v=" + '20261009-titled-downloads-1'
        for asset in (viewer_css, viewer_js, hero_script, "hero-details.css?v=20260909-warm", "artwork-details.css?v=20260909-warm"):
            if page.count(prefix + asset) != 1:
                errors.append(f"{relative}: hero study dependency missing or duplicated: {asset}")
        hero_links = re.findall(r'<a[^>]*data-hero-viewer[^>]*>', page)
        if len(hero_links) != 1:
            errors.append(f"{relative}: expected one clickable hero")
            continue
        hero_link = hero_links[0]
        asset = re.search(r'href="([^\"]+)"', hero_link)
        if not asset or not local_target(path, asset.group(1)).is_file():
            errors.append(f"{relative}: hero study action lacks a real local image")
        for marker in ('aria-haspopup="dialog"', 'data-full-image-alt=', 'data-hero-ask='):
            if marker not in hero_link:
                errors.append(f"{relative}: missing hero study metadata: {marker}")
        if 'data-full-image-viewer' in hero_link:
            errors.append(f"{relative}: hero must open study before full-size viewer")
    if timeline_references != set(TIMELINE_STUDY_HEROES):
        errors.append("expected all three exact timeline study-reference heroes")
    for relative, (href, src, mobile) in TIMELINE_STUDY_HEROES.items():
        page = (ROOT / relative).read_text(encoding="utf-8")
        assert timeline_study_hero_errors(relative, page.replace(href, "../index.html", 1)), "Wrong study link must fail"
        assert timeline_study_hero_errors(relative, page.replace(href, href.split("#")[0], 1)), "Missing study fragment must fail"
        assert timeline_study_hero_errors(relative, page.replace(src, "../assets/heroes/home.webp", 1)), "Wrong artwork must fail"
        for original, replacement in [('data-hero-viewer', 'data-full-image-viewer'), ('data-hero-record="' + TIMELINE_PANEL_RECORDS[relative][0] + '"', 'data-hero-record="home"'), ('hero-details.js?v=20261007-timeline-panels-1', 'hero-details.js?v=unknown')]:
            mutated = page.replace(original, replacement, 1)
            assert mutated != page and timeline_study_hero_errors(relative, mutated), 'Timeline panel mutation escaped'
        script = (ROOT / 'hero-details.js').read_text(encoding='utf-8')
        assert timeline_study_hero_errors(relative, page, script.replace('"study": "' + href.removeprefix('../') + '"', '"study": "index.html"')), 'Spoofed metadata with wrong actual panel destination must fail'
        assert timeline_study_hero_errors(relative, page + '<script src="../hero-details.js?v=20261007-timeline-panels-1"></script>'), 'Duplicate controller must fail'
    # Preserve the exact gateway destinations alongside the two reviewed new heroes.
    # Retain positive gateway/legacy-destination checks rather than skipping the route.
    from joseph_smith_likeness_qa import check as check_joseph_gateway
    errors.extend(check_joseph_gateway())
    if hero_pages != 43:
        errors.append(f"expected43 local-modal hero pages including both Joseph openings, found{hero_pages}")

    full_assets: list[str] = []
    for relative in (*PAGES, "missionary.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for asset in re.findall(r'data-detail-full="([^"]+)"', text):
            full_assets.append(asset)
            target = local_target(ROOT / relative, asset)
            if not target.is_relative_to(ROOT.resolve()) or not target.exists() or target.stat().st_size == 0:
                errors.append(f"{relative}: missing full-image source: {asset}")
    if len(full_assets) != 76:
        errors.append(f"expected 76 artwork detail full-image sources, found {len(full_assets)}")

    detail_paragraphs: list[str] = []
    for relative in (*PAGES, "missionary.html"):
        detail_paragraphs.extend(re.findall(r'<p data-detail-paragraph>(.*?)</p>', (ROOT / relative).read_text(encoding="utf-8"), re.S))
    flattened_copy = " ".join(detail_paragraphs).lower()
    for phrase in ("documentary", "does not assert", "provenance", "without claiming", "historical portrayal", "contemporary portrayal", "not one documented", "not a documented"):
        if phrase in flattened_copy:
            errors.append(f"artwork detail copy contains generic disclaimer wording: {phrase}")

    js = (ROOT / "artwork-details.js").read_text(encoding="utf-8")
    for marker in ("dialog.showModal()", "event.metaKey", "event.ctrlKey", "event.shiftKey", "event.altKey", "event.target === dialog", "returnFocus.focus({ preventScroll: true })", "document.body.classList.add('fc-dialog-open')", "dialog.addEventListener('cancel'", "study.hidden = false", "study.hidden = true", "study.removeAttribute('href')"):
        if marker not in js:
            errors.append(f"artwork-details.js: missing interaction marker: {marker}")

    full_viewer_js = (ROOT / "full-image-viewer.js").read_text(encoding="utf-8")
    for marker in ("dialog.showModal()", "event.metaKey", "event.ctrlKey", "event.shiftKey", "event.altKey", "event.target === stage", "returnFocus.focus({ preventScroll: true })", "dialog.addEventListener('cancel'", "document.body.classList.add('fc-full-image-open')", "image.removeAttribute('src')"):
        if marker not in full_viewer_js:
            errors.append(f"full-image-viewer.js: missing interaction marker: {marker}")

    css = (ROOT / "artwork-details.css").read_text(encoding="utf-8")
    for marker in (".fc-artwork-detail-dialog::backdrop", "margin: auto;", "@media (max-width: 820px)", ".fc-artwork-detail-close::before", ".fc-artwork-detail-close::after", "translate(-50%, -50%) rotate(45deg)", "translate(-50%, -50%) rotate(-45deg)", ".fc-artwork-detail-actions [hidden]", "display: none !important;"):
        if marker not in css:
            errors.append(f"artwork-details.css: missing presentation marker: {marker}")

    action_css = (ROOT / "artwork-actions.css").read_text(encoding="utf-8")
    close_rule = re.search(
        r"\.fc-site\s+:is\(\.fc-artwork-detail-actions,\s*\.fc-missionary-detail-actions\)\s*>\s*:is\(\[data-artwork-detail-close\],\s*\[data-missionary-detail-close\]\)\s*\{([^}]+)\}",
        action_css,
        re.S,
    )
    if not close_rule:
        errors.append("artwork-actions.css: shared detail-dialog close action rule missing")
    else:
        declarations = close_rule.group(1)
        for marker in ("grid-column: auto;", "justify-self: stretch;", "width: 100%;", "min-width: 0;", "margin-top: 0;"):
            if marker not in declarations:
                errors.append(f"artwork-actions.css: desktop detail actions can separate again; missing {marker}")
        if re.search(r"grid-column:\s*1\s*/\s*-1", declarations):
            errors.append("artwork-actions.css: desktop close action must not span a separate full row")
    if ".fc-site .fc-topic-artwork-detail .fc-artwork-detail-actions > [data-artwork-detail-close]" not in action_css:
        errors.append("artwork-actions.css: topic art-study Close action needs a specificity-safe gold border rule")
    # Select the last explicit track: forcing column 2 creates a tiny implicit
    # track when enlarged text makes the auto-fit action grid one column.
    desktop_close = re.search(
        r"@media\s*\(min-width:\s*821px\)\s*\{\s*\.fc-site\s+\.fc-topic-artwork-detail\s+\.fc-artwork-detail-actions\s*>\s*\[data-artwork-detail-close\]\s*\{([^}]+)\}",
        action_css, re.S,
    )
    if not desktop_close or not re.search(r"grid-column:\s*-2\s*/\s*-1\s*;", desktop_close.group(1)):
        errors.append("artwork-actions.css: desktop Close must use the last explicit action-grid column without creating an implicit track")
    if re.search(r"grid-column:\s*2\s*;", action_css):
        errors.append("artwork-actions.css: fixed second-column placement recreates the enlarged-text implicit-track defect")

    hero_css = (ROOT / "hero-details.css").read_text(encoding="utf-8")
    hero_close_rule = re.search(r"\.fc-site \.fc-hero-detail-dialog \.fc-artwork-detail-actions > \[data-hero-close\]\s*\{([^}]+)\}", hero_css, re.S)
    if not hero_close_rule:
        errors.append("hero-details.css: desktop hero close action rule missing")
    else:
        declarations = hero_close_rule.group(1)
        for marker in ("grid-column: auto;", "justify-self: stretch;", "width: 100%;", "min-width: 0;", "margin-top: 0;"):
            if marker not in declarations:
                errors.append(f"hero-details.css: desktop hero actions can separate again; missing {marker}")
        if re.search(r"grid-column:\s*1\s*/\s*-1", declarations):
            errors.append("hero-details.css: desktop hero close action must not span a separate full row")

    art_study_css = (ROOT / "art-study-page.css").read_text(encoding="utf-8")
    for marker in (".fc-art-study-hero::before", "var(--fc-art-study-image)", "object-fit: contain", 'href$="The-Good-Shephard.jpg"', "transform: scale(1.145)", "transform-origin: center bottom", "@media (max-width: 1020px)", "height: auto", "aspect-ratio: 16 / 10", ":focus-visible"):
        if marker not in art_study_css:
            errors.append(f"art-study-page.css: missing resilient hero marker: {marker}")

    hero_js = (ROOT / "hero-details.js").read_text(encoding="utf-8")
    for record in ART_STUDY_HEROES.values():
        if not re.search(r"[\"']" + re.escape(record[1]) + r"[\"']\s*:", hero_js):
            errors.append(f"hero-details.js: missing art-study detail record: {record[1]}")

    mission_css = (ROOT / "missionary.css").read_text(encoding="utf-8")
    if ".fc-missionary-commission-artwork figcaption { position: static;" not in mission_css:
        errors.append("Mission phone caption must not intercept the picture tap target")
    mission_dialog_rule = re.search(r'\.fc-missionary-detail-dialog\s*\{([^}]+)\}', mission_css, re.S)
    if not mission_dialog_rule or "margin: auto;" not in mission_dialog_rule.group(1):
        errors.append("missionary.css: artwork detail dialog must remain viewport-centered")

    for marker in (".fc-missionary-detail-close::before", ".fc-missionary-detail-close::after", "translate(-50%, -50%) rotate(45deg)", "translate(-50%, -50%) rotate(-45deg)"):
        if marker not in mission_css:
            errors.append(f"missionary.css: missing centered close-control marker: {marker}")

    full_viewer_css = (ROOT / "full-image-viewer.css").read_text(encoding="utf-8")
    for marker in (".fc-full-image-viewer::backdrop", "object-fit: contain", ".fc-full-image-close::before", ".fc-full-image-close::after", "translate(-50%, -50%) rotate(45deg)", "translate(-50%, -50%) rotate(-45deg)", "@media (max-width: 640px)"):
        if marker not in full_viewer_css:
            errors.append(f"full-image-viewer.css: missing presentation marker: {marker}")

    if errors:
        print("Artwork detail QA: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Artwork detail QA: PASS")
    print("63 non-Mission artwork triggers and 11 Mission artwork triggers verified")
    print("Same-page full-image viewing, sacred detail copy, and intentional interaction scope verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
