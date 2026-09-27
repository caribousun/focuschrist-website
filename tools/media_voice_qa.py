from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import json
import subprocess
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
def public_pages(root=ROOT):
    """Rendered routes plus public fallback pages, never archived work/QA fixtures."""
    routes = {('index.html' if urlsplit(n.text).path in {'', '/'} else urlsplit(n.text).path.lstrip('/'))
              for n in ET.parse(root / 'sitemap.xml').getroot().findall('{*}url/{*}loc')}
    routes.update(p.relative_to(root).as_posix() for p in root.glob('*.html'))
    for directory in ('answers', 'art-study', 'jesus-christ'):
        routes.update(p.relative_to(root).as_posix() for p in (root / directory).rglob('*.html'))
    return [root / name for name in sorted(routes)]


# These phrases are not forbidden everywhere. They are blocked specifically in
# visitor-facing media copy because repeated abstract bridge language makes a
# concrete human moment sound like an asset note or generated placeholder.
DISTANT_MEDIA_PATTERNS = (
    r"\bthis (?:symbolic )?scene (?:shows|reflects|portrays)\b",
    r"\bthe (?:surrounding )?study makes room\b",
    r"\breflect(?:s|ing) the\b",
    r"\brepresent(?:s|ing)\b",
    r"\bembod(?:y|ies)\b",
    r"\binviting (?:the viewer|readers?|attention|reflection)\b",
    r"\b(?:makes|make|leaves) room for\b",
    r"\ballowing uncertainty\b",
    r"\bdirecting (?:the eye|attention)\b",
    r"\bholding space\b",
    r"\bwithout (?:placing|presuming)\b",
    r"\bgives? (?:living|everyday|visual) form\b",
    r"\bordinary household task\b",
    r"\bstudy illustration\b",
)

# Narrow caption-production constructions, not a ban on uncertainty or on words
# like "historical", "imagined" or "records" in ordinary teaching prose.
PRODUCTION_NOTE_PATTERNS = (
    r"\b(?:this|the|an?) (?:imagined|interpretive|devotional|symbolic)(?: (?:devotional|symbolic))? (?:scene|encounter|moment|portrayal|setting|composition|gathering|community)\b",
    r"\bthis devotional interpretation (?:looks to|invites|depicts|portrays)\b",
    r"\b(?:historical|scriptural|scripture|source) (?:accounts|records|sources) (?:guide|inform|ground) (?:this|the) (?:scene|image|composition|portrayal)\b",
    r"\b(?:do(?:es)? not|don't|doesn't) (?:preserve|record|document) (?:this|the) exact (?:session|conversation|moment|scene|arrangement)\b",
    r"\b(?:setting|faces|clothing|landscape|composition|scene)\b[^.!?]{0,100}\b(?:artistic interpretations?|artistic reconstructions?|artistic choices|creative choices)\b",
)

ALT_PRODUCTION_PATTERNS = (
    r"^\s*(?:an? )?(?:artistic|devotional) interpretation of\b",
)

def voice_matches(value, kind=''):
    normalized = ' '.join(value.split()).replace('’', "'")
    patterns = (*DISTANT_MEDIA_PATTERNS, *PRODUCTION_NOTE_PATTERNS, *(ALT_PRODUCTION_PATTERNS if kind == "alt" else ()))
    return [pattern for pattern in patterns
            if re.search(pattern, normalized, flags=re.IGNORECASE)]

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class MediaVoiceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[dict[str, object]] = []
        self.captures: list[dict[str, str]] = []

    def _inside_resource_card(self) -> bool:
        return any(
            frame["tag"] == "article" and "fc-resource-card" in frame["classes"]
            for frame in self.stack
        )

    def handle_starttag(self, tag: str, attrs) -> None:
        data = {key: (value or "") for key, value in attrs}
        classes = set(data.get("class", "").split())

        if tag == "img" and data.get("alt", "").strip():
            self.captures.append({"kind": "alt", "text": data["alt"].strip()})

        for attr in ('data-detail-image-alt', 'data-full-image-alt'):
            if data.get(attr, '').strip():
                self.captures.append({'kind': 'alt', 'text': data[attr].strip()})

        kind = ""
        if tag == "figcaption" or classes.intersection({'caption', 'fc-marriage-era__copy', 'fc-foundation-card-copy'}):
            kind = "caption"
        elif "data-detail-paragraph" in data:
            kind = "detail"
        elif tag == "p" and "fc-resource-intro" in classes:
            kind = "media intro"
        elif (
            tag == "p"
            and self._inside_resource_card()
            and not classes.intersection({"fc-resource-card__kind", "fc-resource-card__source"})
        ):
            kind = "resource description"

        if tag not in VOID_ELEMENTS:
            capture = {"kind": kind, "parts": []} if kind else None
            self.stack.append({"tag": tag, "classes": classes, "capture": capture})

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if not value:
            return
        for frame in self.stack:
            capture = frame["capture"]
            if capture:
                capture["parts"].append(value)

    def handle_endtag(self, tag: str) -> None:
        matching_index = next(
            (index for index in range(len(self.stack) - 1, -1, -1) if self.stack[index]["tag"] == tag),
            None,
        )
        if matching_index is None:
            return
        closing = self.stack[matching_index:]
        del self.stack[matching_index:]
        for frame in reversed(closing):
            capture = frame["capture"]
            if capture:
                self.captures.append(
                    {"kind": str(capture["kind"]), "text": " ".join(capture["parts"])}
                )


def main() -> int:
    errors: list[str] = []
    totals = {"pages": 0, "caption": 0, "detail": 0, "resource description": 0, "media intro": 0, "alt": 0}
    for path in public_pages():
        parser = MediaVoiceParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        parser.close()
        totals["pages"] += 1
        relative = path.relative_to(ROOT).as_posix()
        for capture in parser.captures:
            kind = capture["kind"]
            totals[kind] += 1
            value = capture["text"]
            for pattern in voice_matches(value, kind):
                if pattern:
                    errors.append(
                        f"{relative}: {kind} uses distant placeholder-style phrasing {pattern!r}: {value}"
                    )

    # These paragraphs are inserted only when a hero dialog opens, so an HTML
    # scan cannot see them. Read the actual record object, including Object.assign.
    result = subprocess.run(['node', str(ROOT / 'tools/media_voice_records.js')],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True)
    records = json.loads(result.stdout)
    if len(records) < 20:
        errors.append('Hero record audit unexpectedly lost public dialog records')
    totals['hero records'] = len(records)
    for key, record in records.items():
        for value in [record['title'], *record['paragraphs']]:
            for pattern in voice_matches(value):
                errors.append(f'hero-details.js:{key}: dialog production phrasing {pattern!r}: {value}')
    gallery = json.loads((ROOT / 'art-gallery.json').read_text(encoding='utf-8'))['artworks']
    totals['gallery records'] = len(gallery)
    if len(gallery) < 100:
        errors.append('Gallery audit unexpectedly lost public artwork records')
    for item in gallery:
        for field in ('title', 'alt'):
            for pattern in voice_matches(item[field], field):
                errors.append(f'art-gallery.json:{item["id"]}:{field}: {pattern!r}: {item[field]}')

    minimums = {
        "pages": 121,
        "caption": 100,
        "detail": 40,
        "resource description": 50,
        "media intro": 10,
        "alt": 150,
    }
    for kind, minimum in minimums.items():
        if totals[kind] < minimum:
            errors.append(f"Media audit unexpectedly found only {totals[kind]} {kind} entries")

    if errors:
        print("Media voice QA failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Media voice QA passed: "
        f"{totals['pages']} pages; {totals['caption']} captions, "
        f"{totals['detail']} expanded details, {totals['resource description']} resource descriptions, "
        f"{totals['media intro']} media introductions, {totals['alt']} alt texts, "
        f"{totals['hero records']} hero dialogs and {totals['gallery records']} gallery records audited."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
