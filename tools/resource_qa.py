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

BYU_URLS = (
    "https://rsc.byu.edu/",
    "https://rsc.byu.edu/search",
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
        "data-focuschrist-primary-watch",
        "createWatchLink('WATCH')",
        "createWatchLink('WATCH & STUDY')",
    ):
        if marker not in common:
            errors.append(f"site-common.js missing resource/navigation marker: {marker}")

    for url in OFFICIAL_URLS:
        if url not in common:
            errors.append(f"site-common.js missing verified official resource: {url}")

    for url in BYU_URLS:
        if url not in common:
            errors.append(f"site-common.js missing verified BYU educational resource: {url}")

    watch = (ROOT / "watch.html").read_text(encoding="utf-8")
    for marker in (
        "Official Church Video &amp; Study",
        "The media remains on ChurchofJesusChrist.org",
        "@theRisen636",
    ):
        if marker not in watch:
            errors.append(f"watch.html missing official-media marker: {marker}")

    # Watch currently retains these verified outbound paths. They may be
    # modernized independently, but must remain official Church destinations.
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

    header = (ROOT / "site-header.css").read_text(encoding="utf-8")
    for marker in (
        "@media (min-width: 1021px) and (max-width: 1260px)",
        "@media (max-width: 1020px)",
        "gap: 22px !important",
    ):
        if marker not in header:
            errors.append(f"site-header.css missing expanded-navigation responsive marker: {marker}")

    if errors:
        print("focusChrist RESOURCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist RESOURCE QA PASSED")
    print("Shared hamburger routing, primary Watch path, official Church/BYU resource grouping, responsive header, Watch media paths, and non-embed policy verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
