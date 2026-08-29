from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"{path.name}: integration marker not found for {label}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main():
    index = ROOT / "index.html"
    old_index = '''        <div class="cta-section">\n            <a href="ask.html" class="cta-button">Ask a Question</a>\n        </div>'''
    new_index = '''        <div class="section">\n            <h2>Watch &amp; Continue Study</h2>\n            <p>Continue from the focusChrist YouTube channel into the exact scripture, Answer, Art &amp; Study, or Ask path that matches the topic.</p>\n            <p><a href="watch.html" style="color:#c9a961;">Open Watch &amp; Continue Study</a></p>\n        </div>\n\n        <div class="cta-section">\n            <a href="ask.html" class="cta-button">Ask a Question</a>\n        </div>'''
    replace_once(index, old_index, new_index, "homepage Watch entry")
    text = index.read_text(encoding="utf-8")
    text = text.replace("Ac 2026 focusChrist. All are welcome here.", "© 2026 focusChrist. All are welcome here.")
    index.write_text(text, encoding="utf-8")

    answers = ROOT / "answers.html"
    old_answers = '''<div class="cta-row"><a class="cta primary" href="ask.html">Ask a Question</a><a class="cta" href="https://www.churchofjesuschrist.org/study/manual/gospel-topics?lang=eng" target="_blank" rel="noopener noreferrer">Official Church Topics</a><a class="cta" href="https://www.youtube.com/@theRisen636" target="_blank" rel="noopener noreferrer">focusChrist on YouTube</a></div>'''
    new_answers = '''<div class="cta-row"><a class="cta primary" href="ask.html">Ask a Question</a><a class="cta" href="watch.html">Watch &amp; Continue Study</a><a class="cta" href="https://www.churchofjesuschrist.org/study/manual/gospel-topics?lang=eng" target="_blank" rel="noopener noreferrer">Official Church Topics</a><a class="cta" href="https://www.youtube.com/@theRisen636" target="_blank" rel="noopener noreferrer">focusChrist on YouTube</a></div>'''
    replace_once(answers, old_answers, new_answers, "Answers Watch continuation")

    page404 = ROOT / "404.html"
    old_404 = '''<a href="answers.html">Answer Library</a><a href="art.html">Inspirational Art</a>'''
    new_404 = '''<a href="answers.html">Answer Library</a><a href="watch.html">Watch &amp; Study</a><a href="art.html">Inspirational Art</a>'''
    replace_once(page404, old_404, new_404, "404 Watch recovery")

    sitemap = ROOT / "sitemap.xml"
    old_sitemap = '''  <url><loc>https://focuschrist.com/answers.html</loc><lastmod>2026-08-29</lastmod></url>\n  <url><loc>https://focuschrist.com/art.html</loc><lastmod>2026-08-29</lastmod></url>'''
    new_sitemap = '''  <url><loc>https://focuschrist.com/answers.html</loc><lastmod>2026-08-29</lastmod></url>\n  <url><loc>https://focuschrist.com/watch.html</loc><lastmod>2026-08-29</lastmod></url>\n  <url><loc>https://focuschrist.com/art.html</loc><lastmod>2026-08-29</lastmod></url>'''
    replace_once(sitemap, old_sitemap, new_sitemap, "sitemap Watch URL")

    qa = ROOT / "tools/site_qa.py"
    text = qa.read_text(encoding="utf-8")
    if '"watch.html": "https://focuschrist.com/watch.html",' not in text:
        old = '    "answers.html": "https://focuschrist.com/answers.html",\n    "art.html": "https://focuschrist.com/art.html",'
        new = '    "answers.html": "https://focuschrist.com/answers.html",\n    "watch.html": "https://focuschrist.com/watch.html",\n    "art.html": "https://focuschrist.com/art.html",'
        if old not in text:
            raise SystemExit("site_qa.py: CORE Watch insertion marker not found")
        text = text.replace(old, new, 1)

    text = text.replace('if len(locs) < 20:', 'if len(locs) < 21:')
    text = text.replace('(\"index.html\", \"ask.html\", \"answers.html\", \"art.html\", \"pioneers.html\", \"about.html\")', '(\"index.html\", \"ask.html\", \"answers.html\", \"watch.html\", \"art.html\", \"pioneers.html\", \"about.html\")')

    watch_checks_anchor = '    answers_index = core_texts.get("answers.html", "")\n'
    watch_checks = '''    watch = core_texts.get("watch.html", "")\n    if watch:\n        if "https://www.youtube.com/@theRisen636" not in watch:\n            fail(errors, "watch.html missing verified YouTube channel path")\n        if watch.count('href="ask.html"') < 2:\n            fail(errors, "watch.html missing Ask continuation paths")\n        for required_path in (\n            "answers/jesus-christ-latter-day-saint-beliefs.html",\n            "answers/what-is-the-book-of-mormon.html",\n            "answers/prayer-and-personal-revelation.html",\n            "answers/faith-in-jesus-christ-during-trials.html",\n            "art-study/the-living-christ.html",\n            "art-study/the-good-shepherd.html",\n            "art-study/suffer-the-little-children.html",\n            "art-study/be-still.html",\n        ):\n            if required_path not in watch:\n                fail(errors, f"watch.html missing topic continuation path: {required_path}")\n\n'''
    if 'watch = core_texts.get("watch.html", "")' not in text:
        if watch_checks_anchor not in text:
            raise SystemExit("site_qa.py: Watch checks anchor not found")
        text = text.replace(watch_checks_anchor, watch_checks + watch_checks_anchor, 1)

    qa.write_text(text, encoding="utf-8")
    print("Integrated Watch & Continue Study into Home, Answers, 404, sitemap, and permanent QA.")


if __name__ == "__main__":
    main()
