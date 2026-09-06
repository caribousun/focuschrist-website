#!/usr/bin/env python3
"""Focused QA for the focusChrist Church History study hub."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(path, needle, label=None):
    text = (ROOT / path).read_text(encoding="utf-8")
    if needle not in text:
        errors.append(f"{path}: missing {label or needle}")
    return text


def forbid(path, needle, label=None):
    text = (ROOT / path).read_text(encoding="utf-8")
    if needle in text:
        errors.append(f"{path}: contains forbidden {label or needle}")


required_files = [
    "church-history.html",
    "church-history.css",
    "church-history-experience.js",
    "study-source-router.js",
]
for name in required_files:
    if not (ROOT / name).is_file():
        errors.append(f"missing required file: {name}")

if not errors:
    history = (ROOT / "church-history.html").read_text(encoding="utf-8")
    for needle, label in [
        ('<title>Church History Study | focusChrist</title>', "unique page title"),
        ('rel="canonical" href="https://focuschrist.com/church-history.html"', "canonical URL"),
        ('data-focuschrist-primary-history="true"', "active History navigation"),
        ('id="ask-history"', "history question section"),
        ('id="historyAskForm"', "history question form"),
        ('id="historyConversation"', "history conversation anchor"),
        ('id="historyResetButton"', "New Question control"),
        ('study-source-router.js', "source router loader"),
        ('church-history-experience.js?v=20260903-16', "versioned history experience loader"),
        ('church-history.css?v=20260904-2', "versioned history stylesheet"),
        ('site-system.css?v=20260906-fit', "versioned shared artwork interaction stylesheet"),
        ('assets/heroes/church-history.webp', "repository-local Sacred Grove hero delivery pattern"),
        ('referrerpolicy="no-referrer"', "hero no-referrer delivery"),
        ('1815–1846', "Saints Volume 1 era"),
        ('1846–1893', "Saints Volume 2 era"),
        ('1893–1955', "Saints Volume 3 era"),
        ('1955–2020', "Saints Volume 4 era"),
        ('https://www.churchofjesuschrist.org/study/church-history?lang=eng', "official Church History hub"),
        ('https://www.churchofjesuschrist.org/study/church-history/saints?lang=eng', "official Saints hub"),
        ('https://www.churchofjesuschrist.org/study/history/topics?lang=eng', "Church History Topics"),
        ('https://www.churchofjesuschrist.org/study/history/global-histories?lang=eng', "Global Histories"),
        ('assets/history/first-vision-1400.webp', "approved First Vision artwork"),
        ('assets/history/joseph-emma-harmony-1400.webp', "approved Joseph and Emma artwork"),
        ('assets/history/three-witnesses-1400.webp', "approved Three Witnesses artwork"),
        ('assets/history/restoration-print-shop-1400.webp', "approved Restoration print shop artwork"),
        ('assets/history/preserving-the-record-1400.webp', "approved record preservation artwork"),
        ('assets/history/christ-museum-record-1400.webp', "approved museum record artwork"),
        ('assets/history/christ-through-eras-1400.webp', "approved Christ across generations artwork"),
        ('focusChrist is an independent faith-based website', "independence disclosure"),
    ]:
        if needle not in history:
            errors.append(f"church-history.html: missing {label}")
    if 'https://drive.google.com/uc?export=view&id=1B1dzLdcOSCEf5ahk-wFAsd7IAJVaVjMk' in history:
        errors.append("church-history.html: broken Drive uc hero delivery pattern remains")

    source_lock_pos = history.find('fc-history-source-lock')
    first_vision_pos = history.find('assets/history/first-vision-1400.webp')
    ask_pos = history.find('id="ask-history"')
    harmony_pos = history.find('assets/history/joseph-emma-harmony-1400.webp')
    saints_pos = history.find('Read <em>Saints</em> Across Four Eras')
    official_index_pos = history.find('id="official-history-index"')
    christ_eras_pos = history.find('assets/history/christ-through-eras-1400.webp')
    if min(source_lock_pos, first_vision_pos, ask_pos, harmony_pos, saints_pos, official_index_pos, christ_eras_pos) < 0 or not (
        source_lock_pos < first_vision_pos < ask_pos < harmony_pos < saints_pos < official_index_pos < christ_eras_pos
    ):
        errors.append(
            "church-history.html: page order must preserve source standard -> First Vision -> Ask -> Harmony -> Saints -> official index -> Christ across generations"
        )

    approved_art_order = [
        "assets/history/first-vision-1400.webp",
        "assets/history/joseph-emma-harmony-1400.webp",
        "assets/history/three-witnesses-1400.webp",
        "assets/history/restoration-print-shop-1400.webp",
        "assets/history/preserving-the-record-1400.webp",
        "assets/history/christ-museum-record-1400.webp",
        "assets/history/christ-through-eras-1400.webp",
    ]
    art_positions = [history.find(asset) for asset in approved_art_order]
    if art_positions != sorted(art_positions):
        errors.append("church-history.html: approved artwork narrative order drifted")
    if history.count('loading="lazy"') < 7 or history.count('decoding="async"') < 8:
        errors.append("church-history.html: approved supporting artwork must remain lazy-loaded and asynchronously decoded")
    if history.count('class="fc-art-link"') != 7:
        errors.append("church-history.html: every approved supporting artwork must open its full-resolution source")
    for asset in approved_art_order:
        if f'href="{asset}"' not in history:
            errors.append(f"church-history.html: full-resolution artwork link missing: {asset}")
    opening = history.split('<section class="fc-page-intro"', 1)[0]
    for asset in approved_art_order:
        if asset in opening:
            errors.append(f"church-history.html: supporting artwork cannot replace the approved History hero: {asset}")
    for forbidden in (
        "A Worldwide Living History",
        "Moroni Appears to Joseph - proportion revision",
    ):
        if forbidden in history:
            errors.append(f"church-history.html: rejected artwork reference present: {forbidden}")

    router = (ROOT / "study-source-router.js").read_text(encoding="utf-8")
    for needle, label in [
        ('sourcesForHistoryQuestion', "history-specific source function"),
        ('historyPromptContext', "history prompt contract"),
        ('CHURCH HISTORY PAGE SOURCE CONTRACT', "history source authority prompt"),
        ('Saints, Volume 1: The Standard of Truth, 1815-1846', "Saints Volume 1 index"),
        ('Saints, Volume 2: No Unhallowed Hand, 1846-1893', "Saints Volume 2 index"),
        ('Saints, Volume 3: Boldly, Nobly, and Independent, 1893-1955', "Saints Volume 3 index"),
        ('Saints, Volume 4: Sounded in Every Ear, 1955-2020', "Saints Volume 4 index"),
        ('joseph-smiths-first-vision-accounts?lang=eng', "First Vision topic route"),
        ('book-of-mormon-translation?lang=eng', "Book of Mormon translation route"),
        ('kirtland-safety-society?lang=eng', "Kirtland Safety Society route"),
        ('mountain-meadows-massacre?lang=eng', "Mountain Meadows route"),
        ('restoration-of-the-aaronic-priesthood?lang=eng', "Aaronic Priesthood route"),
        ('restoration-of-the-melchizedek-priesthood?lang=eng', "Melchizedek Priesthood route"),
        ('seer-stones?lang=eng', "seer stones route"),
        ('joseph-smith-and-plural-marriage?lang=eng', "plural marriage route"),
        ('handcart-companies?lang=eng', "handcart route"),
        ('word-of-wisdom-dc-89?lang=eng', "Word of Wisdom history route"),
    ]:
        if needle not in router:
            errors.append(f"study-source-router.js: missing {label}")

    experience = (ROOT / "church-history-experience.js").read_text(encoding="utf-8")
    for needle, label in [
        ('focusChristStudyAskV3', "v3 grounded intelligence integration"),
        ('sourcesForHistoryQuestion', "history source rendering"),
        ('historyPromptContext', "history prompt context"),
        ("textContent", "safe text renderer"),
        ('Latter-day Saint Church history question:', "history intent forcing"),
        ('HISTORY_HERO_URL', "approved History hero binding"),
        ('assets/heroes/church-history.webp', "repository-local hero source in runtime"),
        ('fallback-no-broken-bitmap', "broken-image fallback"),
        ("event.key === 'Enter' && !event.shiftKey", "Enter submits while Shift+Enter keeps multiline input"),
        ('form.requestSubmit()', "form-native Enter submission"),
        ('recentConversationContext', "follow-up conversation context"),
        ('setConversationMode(true)', "follow-up composer mode"),
        ('resetConversation', "New Question reset"),
        ('focusConversation', "submit auto-follow"),
        ('focusLatestAnswer', "answer auto-follow"),
        ('fixedHeaderOffset', "header-safe scroll offset"),
        ('initHero();', "History hero initialization"),
    ]:
        if needle not in experience:
            errors.append(f"church-history-experience.js: missing {label}")
    if '.innerHTML' in experience:
        errors.append("church-history-experience.js: unsafe innerHTML renderer introduced")
    if "(event.ctrlKey || event.metaKey) && event.key === 'Enter'" in experience:
        errors.append("church-history-experience.js: legacy Ctrl/Cmd+Enter-only submission remains")
    if 'https://drive.google.com/uc?export=view&id=1B1dzLdcOSCEf5ahk-wFAsd7IAJVaVjMk' in experience:
        errors.append("church-history-experience.js: broken Drive uc hero delivery pattern remains")

    require("index.html", 'href="church-history.html"', "Home -> Church History path")
    require("site-common.js", "data-focuschrist-primary-history", "shared History navigation")
    require("site-common.js", "study/church-history?lang=eng", "official Church History menu resource")
    require("site-common.js", "study/church-history/saints?lang=eng", "official Saints menu resource")
    require("sitemap.xml", "https://focuschrist.com/church-history.html", "Church History sitemap entry")

    css = (ROOT / "church-history.css").read_text(encoding="utf-8")
    for token in ["var(--fc-gold-light)", "var(--fc-sage-light)", "var(--fc-sky)", "var(--fc-bg-warm)"]:
        if token not in css:
            errors.append(f"church-history.css: Harvest Sky token not used: {token}")
    for needle, label in [
        ('.fc-history-page .fc-history-hero { min-height: clamp(350px, 27vw, 440px); }', "History hero uses unified site hero height"),
        ('.fc-history-page #ask-history', "History Ask section Harvest Sky surface"),
        ('.fc-history-form-buttons', "Ask-style form actions"),
        ('.fc-history-hero--image-error', "hero failure fallback styling"),
        ('html[data-focuschrist-history-conversation-active]', "active conversation visual state"),
        ('.fc-history-page .fc-history-art-section--quiet + .fc-section.fc-section--flush-top', "current Saints narrative section buffer selector"),
        ('padding-top: clamp(56px, 7vw, 92px);', "Saints narrative section top buffer"),
        ('.fc-history-helper', "History disclosure inset styling"),
        ('padding: 22px clamp(24px, 3vw, 34px) 24px;', "History disclosure edge spacing"),
        ('.fc-history-art-panel', "approved artwork presentation surface"),
        ('.fc-history-art-panel--offset-left', "alternating artwork alignment"),
        ('aspect-ratio: 12 / 5;', "mobile panoramic artwork crop"),
    ]:
        if needle not in css:
            errors.append(f"church-history.css: missing {label}")
    if 'clamp(360px, 31vw, 500px)' in css:
        errors.append("church-history.css: oversized legacy History hero height remains")

if errors:
    print("Church History QA FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Church History QA PASS")
