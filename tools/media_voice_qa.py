from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = [
    path
    for path in sorted(ROOT.rglob("*.html"))
    if not any(part in {".git", "node_modules", "tools"} for part in path.parts)
]

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

        kind = ""
        if tag == "figcaption":
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
    for path in PUBLIC_PAGES:
        parser = MediaVoiceParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        parser.close()
        totals["pages"] += 1
        relative = path.relative_to(ROOT).as_posix()
        for capture in parser.captures:
            kind = capture["kind"]
            totals[kind] += 1
            value = capture["text"]
            for pattern in DISTANT_MEDIA_PATTERNS:
                if re.search(pattern, value, flags=re.IGNORECASE):
                    errors.append(
                        f"{relative}: {kind} uses distant placeholder-style phrasing {pattern!r}: {value}"
                    )

    minimums = {
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
        f"{totals['media intro']} media introductions and {totals['alt']} alt texts audited."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
