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

    common = read("site-common.js", errors)
    system = read("site-system.css", errors)
    journey = read("study-journey.js", errors)
    sources = read("study-source-router.js", errors)
    art_router = read("art-study-router.js", errors)

    require(common, "site-common.js", (
        "BYU_RESOURCE_LINKS",
        "BYU Study Resources",
        "Religious Studies Center",
        "Scripture Citation Index",
        "Gospel Topics Essays",
        "Book of Mormon Videos",
        "loadStudyJourney",
        "study-journey.js?v=20260829-1",
        "ensureMainLandmark",
        "Skip to main content",
        "normalizeFooterIdentity",
    ), errors)

    require(system, "site-system.css", (
        "--fc-ember:",
        "warm umber / harvest gold / restrained firelight",
        "radial-gradient(circle at 50% 8%",
        "#ask-question",
        ".ask-conversation-reset",
        ".ask-followup-actions",
    ), errors)

    require(journey, "study-journey.js", (
        "#ask-question",
        "data-focuschrist-ask-target",
        "Clear & Start Over",
        "Clear Conversation",
        "data-focuschrist-conversation-reset",
        "rewriteContentAskLinks",
        "headerOffset",
        "loadVerifiedSourceRouter",
        "study-source-router.js?v=20260829-1",
        "loadArtStudyRouter",
        "art-study-router.js?v=20260829-1",
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
    ), errors)

    require(art_router, "art-study-router.js", (
        "Study this artwork",
        "The Living Christ",
        "The Good Shepherd",
        "Suffer the Little Children",
        "Be Still",
        "Official Bible Videos",
        "Related @theRisen636 videos",
        "/search?query=",
        "data-focuschrist-art-study-router",
    ), errors)

    forbidden = {
        "study-source-router.js": ("innerHTML", "javascript:"),
        "art-study-router.js": ("youtube.com/watch?v=", "youtu.be/"),
        "study-journey.js": ("location.reload",),
    }
    for name, markers in forbidden.items():
        text = {"study-source-router.js": sources, "art-study-router.js": art_router, "study-journey.js": journey}[name]
        for marker in markers:
            if marker in text:
                errors.append(f"{name} contains forbidden hardened marker: {marker}")

    if errors:
        print("focusChrist HARDENED EXPERIENCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist HARDENED EXPERIENCE QA PASSED")
    print("Verified Ask micro-friction controls, warm palette, accessibility shell, Church/BYU source routing, and Art-to-study/video routing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
