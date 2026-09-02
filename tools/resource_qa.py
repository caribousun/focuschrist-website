from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_URLS = (
    "https://www.churchofjesuschrist.org/study/scriptures?lang=eng",
    "https://www.churchofjesuschrist.org/study/manual/gospel-topics?lang=eng",
    "https://www.churchofjesuschrist.org/study/manual/gospel-topics/essays?lang=eng",
    "https://www.churchofjesuschrist.org/study/general-conference?lang=eng",
    "https://www.churchofjesuschrist.org/comeuntochrist/believe/jesus/videos",
    "https://www.churchofjesuschrist.org/study/videos-and-images/bible-videos?lang=eng",
    "https://www.churchofjesuschrist.org/study/videos-and-images/book-of-mormon-videos?lang=eng",
    "https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng",
)

BYU_MENU_URLS = (
    "https://rsc.byu.edu/",
    "https://scriptures.byu.edu/",
)


def main() -> int:
    errors: list[str] = []

    common = (ROOT / "site-common.js").read_text(encoding="utf-8")
    for marker in (
        "window.toggleMenu",
        "OFFICIAL_RESOURCE_LINKS",
        "BYU_RESOURCE_LINKS",
        "initOfficialResourceMenu",
        "Official Church Resources",
        "BYU Study Resources",
        "Watch & Study",
        "ensurePrimaryStudyNavigation",
        "data-focuschrist-primary-missionary",
        "createMissionaryLink('MISSION')",
        "createMissionaryLink('MISSIONARY WORK')",
        "menu.querySelector('[data-focuschrist-primary-history]')",
        "data-focuschrist-primary-watch",
        "createWatchLink('WATCH')",
        "createWatchLink('WATCH & STUDY')",
    ):
        if marker not in common:
            errors.append(f"site-common.js missing resource/navigation marker: {marker}")

    for url in OFFICIAL_URLS:
        if url not in common:
            errors.append(f"site-common.js missing verified official resource: {url}")

    for url in BYU_MENU_URLS:
        if url not in common:
            errors.append(f"site-common.js missing verified BYU educational menu resource: {url}")

    if "https://rsc.byu.edu/search" in common or "RSC Search" in common:
        errors.append("site-common.js reintroduces redundant RSC Search hamburger item")

    if "textContent.trim().toUpperCase() === 'CHURCH HISTORY'" in common:
        errors.append(
            "site-common.js may mistake the official Church History resource below the divider "
            "for the primary mobile History destination and remove Missionary Work during menu cleanup"
        )

    watch = (ROOT / "watch.html").read_text(encoding="utf-8")
    for marker in (
        "Official Church Video &amp; Study",
        "The media remains on ChurchofJesusChrist.org",
        "@theRisen636",
    ):
        if marker not in watch:
            errors.append(f"watch.html missing official-media marker: {marker}")

    for url in (
        "https://www.churchofjesuschrist.org/comeuntochrist/believe/jesus/videos",
        "https://www.churchofjesuschrist.org/comeuntochrist/believe/bible/videos",
        "https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng",
        "https://www.churchofjesuschrist.org/study/general-conference?lang=eng",
    ):
        if url not in watch:
            errors.append(f"watch.html missing verified official video/study path: {url}")

    if "<iframe" in watch.lower():
        errors.append("watch.html unexpectedly embeds third-party video; use verified outbound paths instead")

    missionary = (ROOT / "missionary.html").read_text(encoding="utf-8")
    for marker in (
        'data-focuschrist-primary-missionary="true"',
        'data-focuschrist-primary-history="true"',
    ):
        if missionary.count(marker) != 2:
            errors.append(
                f"missionary.html must mark exactly one desktop and one hamburger destination for {marker}"
            )

    header = (ROOT / "site-header.css").read_text(encoding="utf-8")
    for marker in (
        "@media (min-width: 1021px) and (max-width: 1450px)",
        "@media (max-width: 1020px)",
        "gap: clamp(14px, 1.6vw, 24px) !important",
    ):
        if marker not in header:
            errors.append(f"site-header.css missing expanded-navigation responsive marker: {marker}")

    if errors:
        print("focusChrist RESOURCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist RESOURCE QA PASSED")
    print("Shared hamburger routing, primary Watch path, official Church/BYU resource grouping, redundant-RSC prevention, responsive header, Watch media paths, and non-embed policy verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
