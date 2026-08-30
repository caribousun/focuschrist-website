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
        ('church-history-experience.js?v=20260830-2', "versioned history experience loader"),
        ('church-history.css?v=20260830-2', "versioned history stylesheet"),
        ('https://lh3.googleusercontent.com/d/1B1dzLdcOSCEf5ahk-wFAsd7IAJVaVjMk', "working Sacred Grove hero delivery pattern"),
        ('referrerpolicy="no-referrer"', "hero no-referrer delivery"),
        ('1815–1846', "Saints Volume 1 era"),
        ('1846–1893', "Saints Volume 2 era"),
        ('1893–1955', "Saints Volume 3 era"),
        ('1955–2020', "Saints Volume 4 era"),
        ('https://www.churchofjesuschrist.org/study/church-history?lang=eng', "official Church History hub"),
        ('https://www.churchofjesuschrist.org/study/church-history/saints?lang=eng', "official Saints hub"),
        ('https://www.churchofjesuschrist.org/study/history/topics?lang=eng', "Church History Topics"),
        ('https://www.churchofjesuschrist.org/study/history/global-histories?lang=eng', "Global Histories"),
        ('focusChrist is an independent faith-based website', "independence disclosure"),
    ]:
        if needle not in history:
            errors.append(f"church-history.html: missing {label}")
    if 'https://drive.google.com/uc?export=view&id=1B1dzLdcOSCEf5ahk-wFAsd7IAJVaVjMk' in history:
        errors.append("church-history.html: broken Drive uc hero delivery pattern remains")

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
        ('https://lh3.googleusercontent.com/d/1B1dzLdcOSCEf5ahk-wFAsd7IAJVaVjMk', "working hero source in runtime"),
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
