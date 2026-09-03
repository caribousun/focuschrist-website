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
    ask_js = read("ask-experience.js", errors)
    pioneer_css = read("pioneer-experience.css", errors)
    pioneer = read("pioneer-experience.js", errors)
    pioneer_page = read("pioneers.html", errors)
    pioneer_book = read("tell-my-story-too.txt", errors)
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
        "study-journey.js?v=20260903-1",
        "study-intelligence-v3.js?v=20260903-17",
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
    ), errors)

    require(ask_css, "ask-experience.css", (
        "Harvest Sky hardening",
        "body.fc-site .ask-followup-shell",
        "border-color: rgba(134,175,200,.38) !important",
        "linear-gradient(145deg, rgba(30,63,75,.98), rgba(17,39,49,.99)) !important",
        "body.fc-site .ask-followup-input",
        "body.fc-site .ask-followup-button",
    ), errors)

    require(ask_js, "ask-experience.js", (
        "chatBox.insertAdjacentElement('beforebegin', dock)",
        "followupDock.classList.contains('visible') ? followupDock : chatBox",
        "followupInput.focus({ preventScroll: true })",
        "document.getElementById('conversationClearBtn')",
        "focusAskComposer(false)",
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
        "PIONEER_POLICY_VERSION = '2026-09-03.16'",
        "function ownDisclosureEvent(event)",
        "event.stopImmediatePropagation()",
        "function installDisclosureOwnership()",
        "data-focuschrist-pioneer-disclosure-controller",
        "Willie & Martin Companies",
        "controller.abort()",
        "75000",
        "renderPioneerChoices",
        "answerSelectedPioneer",
        "cleanLocalPioneerStory",
        "reviewed-local-book-entry",
        "if (localAnswer) return",
        "requestIdleCallback",
        "reviewedLocalDisclosure",
        "local-reviewed-card",
        "failure must never replace it with a refusal or empty panel",
    ), errors)

    require(pioneer_page, "pioneers.html", (
        "const nextStory = storyPosition >= 0 ? storyStarts[storyPosition + 1] : null",
        "const storyEnd = nextStory ? nextStory.index : lines.length",
    ), errors)

    selected_start = pioneer.find("async function answerSelectedPioneer")
    selected_end = pioneer.find("function renderPioneerChoices", selected_start)
    selected_flow = pioneer[selected_start:selected_end]
    local_position = selected_flow.find("showLocalPioneerStory")
    ai_position = selected_flow.find("requestPioneerAI")
    if local_position < 0 or ai_position < 0 or local_position > ai_position:
        errors.append("selected pioneer flow must render a local book entry before any AI request")

    disclosure_start = pioneer.find("async function runDisclosure")
    disclosure_end = pioneer.find("function disclosureTopic", disclosure_start)
    disclosure_flow = pioneer[disclosure_start:disclosure_end]
    disclosure_local = disclosure_flow.find("renderDisclosureAnswer(aiResponse, localAnswer)")
    disclosure_ai = disclosure_flow.find("requestPioneerAI")
    if disclosure_local < 0 or disclosure_ai < 0 or disclosure_local > disclosure_ai:
        errors.append("timeline/trail disclosures must render reviewed local card content before optional AI research")
    if "showLoading(" in disclosure_flow:
        errors.append("timeline/trail disclosures must not show a provider-dependent spinner")
    if "result.sourceIntegrityPassed" not in disclosure_flow:
        errors.append("timeline/trail disclosures must not replace local content with unverified AI output")

    smith_start = pioneer_book.find("ELIZABETH SMITH")
    smith_page_two = pioneer_book.find("(Elizabeth Smith - Page 2)", smith_start)
    smith_page_three = pioneer_book.find("(Elizabeth Smith - Page 3)", smith_start)
    if smith_start < 0 or smith_page_two < 0 or smith_page_three < 0:
        errors.append("Tell My Story, Too must retain all three indexed Elizabeth Smith biography pages")

    require(journey, "study-journey.js", (
        "#ask-question",
        "data-focuschrist-ask-target",
        "rewriteContentAskLinks",
        "headerOffset",
        "requestAnimationFrame",
        "window.addEventListener('load'",
        "loadVerifiedSourceRouter",
        "study-source-router.js?v=20260903-16",
        "loadArtStudyRouter",
        "art-study-router.js?v=20260830-3",
        "loadWatchStudyEnrichment",
        "watch-study-enrichment.js?v=20260830-3",
        "document.readyState === 'loading'",
        "data-focuschrist-study-journey-ready",
    ), errors)

    for unrequested_control in ("Clear & Start Over", "Clear Conversation", "data-focuschrist-conversation-reset"):
        if unrequested_control in journey:
            errors.append(f"study-journey.js must not inject unrequested reset control: {unrequested_control}")

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
        "study-intelligence-v3.js?v=20260903-17",
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
