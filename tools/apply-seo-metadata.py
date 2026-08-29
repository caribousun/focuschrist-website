from pathlib import Path
from html import escape
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
    text = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"

    # Remove a prior managed block if this script is ever rerun.
    text = re.sub(
        r"\r?\n\s*<!-- FocusChrist SEO START -->.*?<!-- FocusChrist SEO END -->\s*\r?\n",
        newline,
        text,
        count=1,
        flags=re.S,
    )

    title_tag = f"<title>{escape(meta['title'])}</title>"
    text, count = re.subn(r"<title>.*?</title>", title_tag, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Expected one <title> in {filename}")

    title_attr = escape(meta["title"], quote=True)
    desc_attr = escape(meta["description"], quote=True)
    url_attr = escape(meta["url"], quote=True)
    image_attr = escape(IMAGE, quote=True)

    lines = [
        START,
        f'    <meta name="description" content="{desc_attr}">',
        '    <meta name="robots" content="index, follow, max-image-preview:large">',
        f'    <link rel="canonical" href="{url_attr}">',
        '    <meta property="og:type" content="website">',
        '    <meta property="og:site_name" content="focusChrist">',
        f'    <meta property="og:title" content="{title_attr}">',
        f'    <meta property="og:description" content="{desc_attr}">',
        f'    <meta property="og:url" content="{url_attr}">',
        f'    <meta property="og:image" content="{image_attr}">',
        '    <meta name="twitter:card" content="summary_large_image">',
        f'    <meta name="twitter:title" content="{title_attr}">',
        f'    <meta name="twitter:description" content="{desc_attr}">',
        f'    <meta name="twitter:image" content="{image_attr}">',
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
    block = newline.join(lines)
    text = text.replace(title_tag, title_tag + newline + block, 1)
    path.write_bytes(text.encode("utf-8"))

print("Applied FocusChrist SEO metadata to:", ", ".join(SITE))
