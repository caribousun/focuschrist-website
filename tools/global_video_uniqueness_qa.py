#!/usr/bin/env python3
"""Reject repeated concrete video identities across public focusChrist pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]
VIDEO = re.compile(r"(?:churchofjesuschrist\.org/(?:media|study)/video/|youtube\.com/(?:watch|shorts)|youtu\.be/)", re.I)

def identity(url):
    clean = url.replace("&amp;", "&")
    parsed = urlsplit(clean)
    path = parsed.path.replace("/study/video/", "/media/video/").rstrip("/")
    if parsed.netloc.lower().removeprefix("www.") == "youtube.com" and path == "/watch":
        video_id = dict(part.split("=", 1) for part in parsed.query.split("&") if "=" in part).get("v")
        if video_id:
            path = f"/watch/{video_id}"
    return (parsed.netloc.lower().removeprefix("www."), path)

class PageVideos(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.current = None
        self.loose = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and ("data-resource-key" in attrs or "data-watch-video" in attrs):
            self.current = {"key": attrs.get("data-resource-key") or attrs.get("data-watch-video"), "videos": set()}
            self.cards.append(self.current)
        if tag == "a" and VIDEO.search(attrs.get("href", "")):
            target = self.current["videos"] if self.current else self.loose
            value = identity(attrs["href"])
            target.add(value) if isinstance(target, set) else target.append(value)
    def handle_endtag(self, tag):
        if tag == "article": self.current = None

pages = {}
loose = []
for file in sorted(ROOT.glob("*.html")) + sorted((ROOT / "answers").glob("*.html")) + sorted((ROOT / "art-study").glob("*.html")):
    parser = PageVideos(); parser.feed(file.read_text())
    for card in parser.cards:
        for video in card["videos"]:
            pages.setdefault(video, []).append((file.relative_to(ROOT).as_posix(), card["key"]))
    for item in parser.loose:
        pages.setdefault(item, []).append((file.relative_to(ROOT).as_posix(), "standalone-link"))

errors = []
for video, placements in pages.items():
    distinct = sorted(set(placements))
    if len(distinct) > 1:
        errors.append(f"duplicate {video[0]}{video[1]}: {distinct}")
if errors:
    raise SystemExit("\n".join(errors))
print(f"GLOBAL VIDEO UNIQUENESS PASS: {len(pages)} reviewed videos, one themed placement each")
