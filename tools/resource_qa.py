from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_URLS = (
    "https://www.churchofjesuschrist.org/study/scriptures?lang=eng",
    "https://www.churchofjesuschrist.org/study/manual/gospel-topics?lang=eng",
    "https://www.churchofjesuschrist.org/study/general-conference?lang=eng",
    "https://www.churchofjesuschrist.org/comeuntochrist/believe/jesus/videos",
    "https://www.churchofjesuschrist.org/comeuntochrist/believe/bible/videos",
    "https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng",
)


def main() -> int:
    errors: list[str] = []

    common = (ROOT / "site-common.js").read_text(encoding="utf-8")
    for marker in (
        "window.toggleMenu",
        "OFFICIAL_RESOURCE_LINKS",
        "initOfficialResourceMenu",
        "Official Church Resources",
        "Watch & Study",
    ):
        if marker not in common:
            errors.append(f"site-common.js missing resource/navigation marker: {marker}")

    for url in OFFICIAL_URLS:
        if url not in common:
            errors.append(f"site-common.js missing verified official resource: {url}")

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

    if errors:
        print("focusChrist RESOURCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist RESOURCE QA PASSED")
    print("Shared hamburger routing, Watch official-media paths, and non-embed policy verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
