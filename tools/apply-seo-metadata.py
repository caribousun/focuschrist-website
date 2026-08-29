from pathlib import Path
import json
import re

SITE = {
    "index.html": {
        "title": "focusChrist | Jesus Christ & Latter-day Saint Faith",
        "description": "Explore Christ-centered answers about Jesus Christ, scripture, and Latter-day Saint faith. Ask questions, view inspirational art, and study pioneer faith.",
        "url": "https://focuschrist.com/",
    },
    "ask.html": {
        "title": "Ask About Jesus Christ & Latter-day Saint Beliefs | focusChrist",
        "description": "Ask sincere questions about Jesus Christ, scripture, and the beliefs of The Church of Jesus Christ of Latter-day Saints, with Christ-centered answers and sources.",
        "url": "https://focuschrist.com/ask.html",
    },
    "art.html": {
        "title": "Jesus Christ & Scripture Art | focusChrist",
        "description": "View inspirational Christian artwork centered on Jesus Christ, scripture, faith, hope, and teachings from the Latter-day Saint tradition.",
        "url": "https://focuschrist.com/art.html",
    },
    "pioneers.html": {
        "title": "Latter-day Saint Pioneer Stories | focusChrist",
        "description": "Explore Latter-day Saint pioneer stories, trail history, handcart journeys, sacrifice, faith, and devotion to Jesus Christ.",
        "url": "https://focuschrist.com/pioneers.html",
    },
    "about.html": {
        "title": "About focusChrist | Christ-Centered Faith Resource",
        "description": "Learn about focusChrist, an independent Christ-centered resource for exploring Jesus Christ, scripture, and Latter-day Saint faith.",
        "url": "https://focuschrist.com/about.html",
    },
}

IMAGE = "https://focuschrist.com/Jesus.png"
START = "    <!-- FocusChrist SEO START -->"
END = "    <!-- FocusChrist SEO END -->"

for filename, meta in SITE.items():
    path = Path(filename)
    text = path.read_text(encoding="utf-8")

    # Remove a prior managed block if this script is ever rerun.
    text = re.sub(
        r"\n\s*<!-- FocusChrist SEO START -->.*?<!-- FocusChrist SEO END -->\s*\n",
        "\n",
        text,
        count=1,
        flags=re.S,
    )

    title_tag = f"<title>{meta['title']}</title>"
    text, count = re.subn(r"<title>.*?</title>", title_tag, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Expected one <title> in {filename}")

    lines = [
        START,
        f'    <meta name="description" content="{meta["description"]}">',
        '    <meta name="robots" content="index, follow, max-image-preview:large">',
        f'    <link rel="canonical" href="{meta["url"]}">',
        '    <meta property="og:type" content="website">',
        '    <meta property="og:site_name" content="focusChrist">',
        f'    <meta property="og:title" content="{meta["title"]}">',
        f'    <meta property="og:description" content="{meta["description"]}">',
        f'    <meta property="og:url" content="{meta["url"]}">',
        f'    <meta property="og:image" content="{IMAGE}">',
        '    <meta name="twitter:card" content="summary_large_image">',
        f'    <meta name="twitter:title" content="{meta["title"]}">',
        f'    <meta name="twitter:description" content="{meta["description"]}">',
        f'    <meta name="twitter:image" content="{IMAGE}">',
    ]

    if filename == "index.html":
        website_schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "focusChrist",
            "url": "https://focuschrist.com/",
            "description": meta["description"],
            "sameAs": ["https://www.youtube.com/@theRisen636"],
        }
        lines.extend([
            '    <script type="application/ld+json">',
            '    ' + json.dumps(website_schema, ensure_ascii=False, separators=(",", ":")),
            '    </script>',
        ])

    lines.append(END)
    block = "\n".join(lines)
    text = text.replace(title_tag, title_tag + "\n" + block, 1)
    path.write_text(text, encoding="utf-8")

print("Applied FocusChrist SEO metadata to:", ", ".join(SITE))
