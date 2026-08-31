from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(name: str, errors: list[str]) -> str:
    path = ROOT / name
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"{name} missing or empty")
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, name: str, markers: tuple[str, ...], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{name} missing hardened marker: {marker}")


def main() -> int:
    errors: list[str] = []

    index = read("index.html", errors)
    common = read("site-common.js", errors)
    header = read("site-header.css", errors)
    system = read("site-system.css", errors)
    ask_css = read("ask-experience.css", errors)
    pioneer_css = read("pioneer-experience.css", errors)
    pioneer = read("pioneer-experience.js", errors)
    journey = read("study-journey.js", errors)
    sources = read("study-source-router.js", errors)
    grounded = read("study-intelligence-v3.js", errors)
    art_router = read("art-study-router.js", errors)
    watch_enrichment = read("watch-study-enrichment.js", errors)

    require(index, "index.html", (
        'href="ask.html#ask-question"',
        'Ask a Question',
        'Ask. Seek. Study.',
    ), errors)

    require(common, "site-common.js", (
        "BYU_RESOURCE_LINKS",
        "BYU Study Resources",
        "Religious Studies Center",
        "Scripture Citation Index",
        "Gospel Topics Essays",
        "Book of Mormon Videos",
        "loadStudyJourney",
        "study-journey.js?v=20260830-3",
        "study-intelligence-v3.js?v=20260831-5",
        "window.focusChristSourceIntegrity",
        "unreviewed-source-dependent-generation",
        "data-focuschrist-study-intelligence-v3",
        "ensureMainLandmark",
        "Skip to main content",
        "normalizeFooterIdentity",
    ), errors)

    require(header, "site-header.css", (
        "Shared conversation alignment hardening",
        "body.fc-site .ask-chat-box .user-message",
        "body.fc-site .qa-container .user-message",
        "body.fc-site .fc-history-message--user",
        "margin-left: clamp(8px, 2.4vw, 28px) !important",
        "@media (max-width: 720px)",
    ), errors)

    require(system, "site-system.css", (
        "--fc-ember:",
        "--fc-sky:",
        "Harvest Sky",
        "radial-gradient(circle at 84% 4%",
        "#ask-question",
        ".ask-conversation-reset",
        ".ask-followup-actions",
    ), errors)

    require(ask_css, "ask-experience.css", (
        "Harvest Sky hardening",
        "body.fc-site .ask-followup-shell",
        "border-color: rgba(134,175,200,.38) !important",
        "linear-gradient(145deg, rgba(30,63,75,.98), rgba(17,39,49,.99)) !important",
        "body.fc-site .ask-followup-input",
        "body.fc-site .ask-followup-button",
    ), errors)

    require(pioneer_css, "pioneer-experience.css", (
        "Pioneer date/title collision hardening",
        "body.fc-site .timeline-item > .map-date",
        "flex: 0 0 165px !important",
        "white-space: normal !important",
        "body.fc-site .timeline-item > .map-content",
        "flex-direction: column",
    ), errors)

    require(pioneer, "pioneer-experience.js", (
        "PIONEER_POLICY_VERSION = '2026-08-31.5'",
        "function ownDisclosureEvent(event)",
        "event.stopImmediatePropagation()",
        "function installDisclosureOwnership()",
        "data-focuschrist-pioneer-disclosure-controller",
        "Willie & Martin Companies",
        "controller.abort()",
        "25000",
    ), errors)

    require(journey, "study-journey.js", (
        "#ask-question",
        "data-focuschrist-ask-target",
        "Clear & Start Over",
        "Clear Conversation",
        "data-focuschrist-conversation-reset",
        "rewriteContentAskLinks",
        "headerOffset",
        "requestAnimationFrame",
        "window.addEventListener('load'",
        "loadVerifiedSourceRouter",
        "study-source-router.js?v=20260830-2",
        "loadArtStudyRouter",
        "art-study-router.js?v=20260830-3",
        "loadWatchStudyEnrichment",
        "watch-study-enrichment.js?v=20260830-3",
        "document.readyState === 'loading'",
        "data-focuschrist-study-journey-ready",
    ), errors)

    require(sources, "study-source-router.js", (
        "https://www.churchofjesuschrist.org/search?lang=eng&query=",
        "Topics & Questions",
        "Gospel Topics Essays",
        "General Conference",
        "Bible Videos",
        "Book of Mormon Videos",
        "BYU Religious Studies Center",
        "BYU Scripture Citation Index",
        "Search official Church sources for this question",
        "data-focuschrist-source-paths",
        "Official Church search",
        "BYU educational",
        "study-intelligence-v3.js?v=20260831-5",
        "document.readyState === 'loading'",
        "data-focuschrist-source-router-ready",
        "oliver cowdery",
        "premortality",
        "melchizedek",
    ), errors)

    require(grounded, "study-intelligence-v3.js", (
        "focusChrist Study Intelligence v3",
        "VERIFIED CORE RESTORATION FACTS:",
        "John the Baptist conferred the Aaronic Priesthood",
        "Peter, James, and John later conferred the Melchizedek Priesthood",
        "Do not use Markdown tables or pipe-table syntax",
        "non-breaking spaces",
        "normalizeDisplayText",
        "convertMarkdownTables",
        "focusChristStudyAskV3",
        "temperature: 0.25",
        "data-focuschrist-study-intelligence-version",
    ), errors)

    require(art_router, "art-study-router.js", (
        "Study this artwork",
        "Ask about this artwork",
        "Study this topic on ChurchofJesusChrist.org",
        "returnUrlForCaption",
        "data-focuschrist-art-return-restored",
        "data-focuschrist-art-study-button",
        "data-focuschrist-art-study-drawer",
        "document.readyState === 'loading'",
        "data-focuschrist-art-study-router",
    ), errors)

    require(watch_enrichment, "watch-study-enrichment.js", (
        "watch-mini-media",
        "data-watch-thumbnail-ready",
        "Watch ",
        "ChurchofJesusChrist.org",
        "MutationObserver",
        "document.readyState === 'loading'",
        "data-focuschrist-watch-enrichment-ready",
    ), errors)

    forbidden = {
        "ask-experience.css": ("rgba(183,104,72,0.09)",),
        "study-source-router.js": ("innerHTML", "javascript:"),
        "art-study-router.js": ("youtube.com", "youtu.be/", "@theRisen636"),
        "watch-study-enrichment.js": ("youtube.com/watch?v=", "youtu.be/"),
        "study-journey.js": ("location.reload",),
        "study-intelligence-v3.js": ("May the love of Jesus Christ bring you peace and clarity", "temperature: 0.7"),
    }
    texts = {
        "ask-experience.css": ask_css,
        "study-source-router.js": sources,
        "art-study-router.js": art_router,
        "watch-study-enrichment.js": watch_enrichment,
        "study-journey.js": journey,
        "study-intelligence-v3.js": grounded,
    }
    for name, markers in forbidden.items():
        for marker in markers:
            if marker in texts[name]:
                errors.append(f"{name} contains forbidden hardened marker: {marker}")

    if index.count('href="ask.html#ask-question"') < 2:
        errors.append("index.html must deep-link both Home Ask pathways to #ask-question")

    if errors:
        print("focusChrist HARDENED EXPERIENCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist HARDENED EXPERIENCE QA PASSED")
    print("Verified direct Home-to-Ask arrival, complete Harvest Sky Ask follow-up styling, Pioneer date/title collision protection, hardened Pioneer disclosure ownership and timeout recovery, accessibility shell, Church/BYU source routing, grounded response hygiene, Art-to-official-study/contextual-Ask routing with exact return continuity, and thumbnail-backed Watch enrichment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
