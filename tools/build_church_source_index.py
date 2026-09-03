#!/usr/bin/env python3
"""Build the bounded focusChrist Church-source discovery index.

The generated artifact stores URL discovery metadata only. Article text is
retrieved in small bounded excerpts by the Worker at question time.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "groq-proxy" / "src" / "church-source-index.js"
REVIEW_MANIFEST = ROOT / "groq-proxy" / "src" / "church-source-index-review.json"
SITEMAP_INDEX = "https://sitemaps.churchofjesuschrist.org/sitemap-service/www.churchofjesuschrist.org/en/index.xml"
ROBOTS_URL = "https://www.churchofjesuschrist.org/robots.txt"
USER_AGENT = "focusChrist-source-index/1.0 (+https://focuschrist.com/about.html)"
ALLOWED_HOST = "www.churchofjesuschrist.org"
SITEMAP_HOST = "sitemaps.churchofjesuschrist.org"
MAX_ENTRIES = 900
MAX_XML_ELEMENTS = 1_000_000
MAX_XML_DEPTH = 8
MAX_REVIEW_AGE_DAYS = 8
REQUIRED_KINDS = (
    "gospel-topic",
    "history-topic",
    "church-history-overview",
    "church-history",
    "church-history-manual",
    "scripture-guide",
    "official-explainer",
)
KIND_RESERVES = {
    "gospel-topic": 260,
    "history-topic": 180,
    "church-history-overview": 120,
    "church-history": 120,
    "church-history-manual": 90,
    "scripture-guide": 80,
    "official-explainer": 50,
}

SOURCE_FAMILIES = (
    ("/study/manual/gospel-topics/", "gospel-topic", 100),
    ("/study/history/topics/", "history-topic", 95),
    ("/study/church-history/womens-history", "church-history", 92),
    ("/study/church-history/saints", "church-history", 88),
    ("/study/manual/church-history-in-the-fulness-of-times/", "church-history-manual", 76),
    ("/study/scriptures/gs", "scripture-guide", 78),
    ("/learn/history/", "church-history-overview", 90),
    ("/temples/why-latter-day-saints-build-temples", "official-explainer", 92),
    ("/comeuntochrist/believe/", "official-explainer", 82),
)

BLOCKED_PATH_PARTS = (
    "/search",
    "/scriptures/search",
    "/internal-use-only/",
    "/handbook-1-stake-presidents-and-bishops",
)

CURATED_DISCOVERY = (
    {
        "url": "https://www.churchofjesuschrist.org/learn/history/a-brief-history?lang=eng",
        "title": "A Brief History of The Church of Jesus Christ of Latter-day Saints",
        "kind": "church-history-overview",
        "priority": 110,
        "keywords": "pioneer pioneers settlement settlements irrigation cooperative agriculture community communities Utah Salt Lake Valley migration restoration",
    },
    {
        "url": "https://www.churchofjesuschrist.org/study/scriptures/gs?lang=eng",
        "title": "Guide to the Scriptures",
        "kind": "scripture-guide",
        "priority": 70,
        "keywords": "scripture doctrine gospel bible book of mormon doctrine covenants pearl great price topics",
    },
    {
        "url": "https://www.churchofjesuschrist.org/study/church-history/womens-history?lang=eng",
        "title": "Women in Church History",
        "kind": "church-history",
        "priority": 96,
        "keywords": "women church history relief society nauvoo faith service organization",
    },
    {
        "url": "https://www.churchofjesuschrist.org/study/church-history/saints?lang=eng",
        "title": "Saints: The Story of the Church of Jesus Christ in the Latter Days",
        "kind": "church-history",
        "priority": 96,
        "keywords": "saints church history restoration pioneers joseph smith nauvoo kirtland",
    },
    {
        "url": "https://www.churchofjesuschrist.org/temples/why-latter-day-saints-build-temples?lang=eng",
        "title": "Why Latter-day Saints Build Temples",
        "kind": "official-explainer",
        "priority": 96,
        "keywords": "temple temples worship covenants ordinances Jesus Christ God families",
    },
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201
        raise RuntimeError(f"Redirect rejected while refreshing source index: {newurl}")


def fetch_bytes(url: str, expected_host: str, accepted_types: tuple[str, ...], max_bytes: int) -> bytes:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != expected_host:
        raise RuntimeError(f"Unapproved refresh URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": ",".join(accepted_types)})
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=45) as response:
        if urllib.parse.urlsplit(response.geturl()).hostname != expected_host:
            raise RuntimeError(f"Refresh response changed host: {response.geturl()}")
        content_type = response.headers.get_content_type().lower()
        if content_type not in accepted_types:
            raise RuntimeError(f"Unexpected content type {content_type} from {url}")
        payload = response.read(max_bytes + 1)
        if len(payload) > max_bytes:
            raise RuntimeError(f"Refresh response exceeded {max_bytes} bytes: {url}")
        return payload


def robots_rules(payload: bytes) -> list[re.Pattern[str]]:
    text = payload.decode("utf-8", errors="strict")
    active = False
    rules: list[re.Pattern[str]] = []
    saw_star = False
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        if field.lower() == "user-agent":
            active = value == "*"
            saw_star = saw_star or active
            continue
        if active and field.lower() == "disallow" and value:
            escaped = re.escape(value).replace(r"\*", ".*")
            if escaped.endswith(r"\$"):
                escaped = escaped[:-2] + "$"
            rules.append(re.compile("^" + escaped, re.I))
    if not saw_star or not rules:
        raise RuntimeError("Current robots.txt did not contain usable User-agent: * rules")
    return rules


def parse_bounded_xml(payload: bytes) -> ET.Element:
    upper = payload.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise RuntimeError("DTD and entity declarations are not permitted in sitemap XML")
    root = ET.fromstring(payload)
    count = 0
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > MAX_XML_ELEMENTS:
            raise RuntimeError(f"Sitemap XML exceeded {MAX_XML_ELEMENTS} elements")
        if depth > MAX_XML_DEPTH:
            raise RuntimeError(f"Sitemap XML exceeded depth {MAX_XML_DEPTH}")
        stack.extend((child, depth + 1) for child in node)
    return root


def xml_locations(payload: bytes, element_name: str) -> list[str]:
    root = parse_bounded_xml(payload)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [node.text.strip() for node in root.findall(f"sm:{element_name}/sm:loc", namespace) if node.text]


def xml_lastmods(payload: bytes) -> list[str]:
    root = parse_bounded_xml(payload)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [node.text.strip() for node in root.findall("sm:sitemap/sm:lastmod", namespace) if node.text]


def canonicalize(raw_url: str, disallow: list[re.Pattern[str]]) -> str | None:
    parsed = urllib.parse.urlsplit(html.unescape(raw_url))
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        return None
    path = re.sub(r"/{2,}", "/", parsed.path).rstrip("/") or "/"
    lower_path = path.lower()
    if any(part in lower_path for part in BLOCKED_PATH_PARTS):
        return None
    path_and_query = path + (f"?{parsed.query}" if parsed.query else "")
    if any(rule.search(path_and_query) for rule in disallow):
        return None
    family = next((item for item in SOURCE_FAMILIES if lower_path.startswith(item[0])), None)
    if not family:
        return None
    if lower_path.endswith(("/contents", "/title-page", "/front-cover", "/inside-front-cover")):
        return None
    return urllib.parse.urlunsplit(("https", ALLOWED_HOST, path, "lang=eng", ""))


def title_from_path(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    slug = path.rstrip("/").split("/")[-1]
    title = re.sub(r"^(?:chapter|lesson)-(?=\d+)", "", slug, flags=re.I)
    title = re.sub(r"[-_]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title.title() if title else "Official Church Source"


def family_for(url: str) -> tuple[str, int]:
    path = urllib.parse.urlsplit(url).path.lower()
    for prefix, kind, priority in SOURCE_FAMILIES:
        if path.startswith(prefix):
            return kind, priority
    raise AssertionError(f"Unclassified generated URL: {url}")


def token_text(title: str, url: str, extra: str = "") -> str:
    path = urllib.parse.urlsplit(url).path
    value = f"{title} {path.replace('/', ' ')} {extra}".lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    tokens = []
    for token in value.split():
        if token not in tokens:
            tokens.append(token)
    return " ".join(tokens)[:420]


def build_entries() -> tuple[str, str, str, list[dict[str, object]]]:
    robots_payload = fetch_bytes(ROBOTS_URL, ALLOWED_HOST, ("text/plain",), 150_000)
    robots_hash = hashlib.sha256(robots_payload).hexdigest()
    disallow = robots_rules(robots_payload)
    index_payload = fetch_bytes(SITEMAP_INDEX, SITEMAP_HOST, ("application/xml", "text/xml"), 150_000)
    sitemap_hasher = hashlib.sha256(index_payload)
    sitemap_urls = xml_locations(index_payload, "sitemap")
    revisions = xml_lastmods(index_payload)
    if not sitemap_urls or len(sitemap_urls) > 10:
        raise RuntimeError(f"Official English sitemap index returned an invalid child count: {len(sitemap_urls)}")

    discovered: dict[str, dict[str, object]] = {}
    for position, sitemap_url in enumerate(sitemap_urls):
        child = urllib.parse.urlsplit(sitemap_url)
        if child.scheme != "https" or child.hostname != SITEMAP_HOST:
            raise RuntimeError(f"External child sitemap rejected: {sitemap_url}")
        if position:
            time.sleep(0.25)
        payload = fetch_bytes(sitemap_url, SITEMAP_HOST, ("application/xml", "text/xml"), 60_000_000)
        sitemap_hasher.update(b"\0")
        sitemap_hasher.update(sitemap_url.encode("utf-8"))
        sitemap_hasher.update(b"\0")
        sitemap_hasher.update(payload)
        for raw_url in xml_locations(payload, "url"):
            url = canonicalize(raw_url, disallow)
            if not url or url in discovered:
                continue
            kind, priority = family_for(url)
            title = title_from_path(url)
            discovered[url] = {
                "url": url,
                "title": title,
                "kind": kind,
                "priority": priority,
                "tokens": token_text(title, url),
            }

    for seed in CURATED_DISCOVERY:
        entry = dict(seed)
        keywords = str(entry.pop("keywords", ""))
        entry["tokens"] = token_text(str(entry["title"]), str(entry["url"]), keywords)
        if canonicalize(str(entry["url"]), disallow) != entry["url"]:
            raise RuntimeError(f"Curated URL violates current robots or route policy: {entry['url']}")
        discovered[str(entry["url"])] = entry

    ranked = sorted(discovered.values(), key=lambda item: (-int(item["priority"]), str(item["url"])))
    entries: list[dict[str, object]] = []
    selected_urls: set[str] = set()
    for kind in REQUIRED_KINDS:
        family_entries = [item for item in ranked if item["kind"] == kind][:KIND_RESERVES[kind]]
        for item in family_entries:
            url = str(item["url"])
            if url not in selected_urls:
                entries.append(item)
                selected_urls.add(url)
    for item in ranked:
        if len(entries) >= MAX_ENTRIES:
            break
        url = str(item["url"])
        if url not in selected_urls:
            entries.append(item)
            selected_urls.add(url)
    entries.sort(key=lambda item: (-int(item["priority"]), str(item["url"])))
    revision = max(revisions) if revisions else "unknown"
    return revision, robots_hash, sitemap_hasher.hexdigest(), entries


def render(revision: str, robots_hash: str, sitemap_hash: str, entries: list[dict[str, object]]) -> str:
    serialized = json.dumps(entries, ensure_ascii=True, separators=(",", ":"))
    return (
        "// Generated by tools/build_church_source_index.py. Do not edit by hand.\n"
        f"const CHURCH_SOURCE_SITEMAP_REVISION = {json.dumps(revision)};\n"
        f"const CHURCH_SOURCE_ROBOTS_SHA256 = {json.dumps(robots_hash)};\n"
        f"const CHURCH_SOURCE_SITEMAPS_SHA256 = {json.dumps(sitemap_hash)};\n"
        f"const CHURCH_SOURCE_INDEX = Object.freeze({serialized});\n\n"
        "export { CHURCH_SOURCE_INDEX, CHURCH_SOURCE_ROBOTS_SHA256, CHURCH_SOURCE_SITEMAP_REVISION, CHURCH_SOURCE_SITEMAPS_SHA256 };\n"
    )


def validate(revision: str, entries: list[dict[str, object]], rendered: str) -> None:
    if revision == "unknown":
        raise RuntimeError("Sitemap revision is missing")
    if len(entries) < 100 or len(entries) > MAX_ENTRIES:
        raise RuntimeError(f"Index coverage is unexpectedly small: {len(entries)} entries")
    if len(rendered.encode("utf-8")) > 300_000:
        raise RuntimeError("Generated index exceeds the 300 KB bundle budget")
    urls = [str(entry["url"]) for entry in entries]
    if len(urls) != len(set(urls)):
        raise RuntimeError("Generated index contains duplicate URLs")
    kind_counts = {kind: 0 for kind in REQUIRED_KINDS}
    for entry in entries:
        if set(entry) != {"url", "title", "kind", "priority", "tokens"}:
            raise RuntimeError(f"Generated entry has an invalid schema: {entry.get('url', '(missing URL)')}")
        url = str(entry["url"])
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
            raise RuntimeError(f"Generated URL violates the host allowlist: {url}")
        if parsed.query != "lang=eng" or parsed.fragment:
            raise RuntimeError(f"Generated URL violates the canonical query policy: {url}")
        if any(part in parsed.path.lower() for part in BLOCKED_PATH_PARTS):
            raise RuntimeError(f"Generated URL violates the route allowlist: {url}")
        if not isinstance(entry["title"], str) or not entry["title"].strip():
            raise RuntimeError(f"Generated title is missing: {url}")
        if not isinstance(entry["tokens"], str) or not 1 <= len(entry["tokens"]) <= 420:
            raise RuntimeError(f"Generated tokens violate the 420-character bound: {url}")
        if not isinstance(entry["priority"], int) or not 1 <= entry["priority"] <= 250:
            raise RuntimeError(f"Generated priority is invalid: {url}")
        if entry["kind"] in kind_counts:
            kind_counts[str(entry["kind"])] += 1
    missing_kinds = [kind for kind, count in kind_counts.items() if count == 0]
    if missing_kinds:
        raise RuntimeError(f"Generated index is missing source families: {', '.join(missing_kinds)}")
    required_terms = ("jesus-christ", "temple", "prayer", "hyrum-smith", "relief-society", "handcart")
    corpus = "\n".join(urls).lower()
    missing = [term for term in required_terms if term not in corpus]
    if missing:
        raise RuntimeError(f"Generated index is missing representative coverage: {', '.join(missing)}")


def write_review_manifest(revision: str, robots_hash: str, sitemap_hash: str) -> None:
    manifest = {
        "schema_version": 1,
        "reviewed_on": dt.datetime.now(dt.timezone.utc).date().isoformat(),
        "robots_sha256": robots_hash,
        "sitemap_revision": revision,
        "sitemaps_sha256": sitemap_hash,
    }
    REVIEW_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_review_manifest(revision: str, robots_hash: str, sitemap_hash: str) -> None:
    if not REVIEW_MANIFEST.exists():
        raise RuntimeError("Church source review manifest is missing")
    manifest = json.loads(REVIEW_MANIFEST.read_text(encoding="utf-8"))
    expected = {
        "robots_sha256": robots_hash,
        "sitemap_revision": revision,
        "sitemaps_sha256": sitemap_hash,
    }
    if manifest.get("schema_version") != 1:
        raise RuntimeError("Church source review manifest schema is invalid")
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeError(f"Church source review manifest does not approve {key}")
    reviewed = dt.date.fromisoformat(str(manifest.get("reviewed_on", "")))
    age = (dt.datetime.now(dt.timezone.utc).date() - reviewed).days
    if age < 0 or age > MAX_REVIEW_AGE_DAYS:
        raise RuntimeError(f"Church source review is {age} days old; refresh and approve within {MAX_REVIEW_AGE_DAYS} days")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate the committed generated file without network access")
    parser.add_argument("--approve", action="store_true", help="Record review approval for the exact rebuilt source hashes")
    args = parser.parse_args()

    if args.check:
        if not OUTPUT.exists():
            raise RuntimeError(f"Generated index is missing: {OUTPUT}")
        content = OUTPUT.read_text(encoding="utf-8")
        if "Generated by tools/build_church_source_index.py" not in content:
            raise RuntimeError("Generated index header is missing")
        values: dict[str, str] = {}
        for name in ("CHURCH_SOURCE_SITEMAP_REVISION", "CHURCH_SOURCE_ROBOTS_SHA256", "CHURCH_SOURCE_SITEMAPS_SHA256"):
            match = re.search(rf'const {name} = "([0-9a-f]{{64}})";', content)
            if name == "CHURCH_SOURCE_SITEMAP_REVISION":
                match = re.search(rf'const {name} = "([^"]+)";', content)
            if not match:
                raise RuntimeError(f"Generated index is missing a valid {name}")
            values[name] = match.group(1)
        if any(part in content for part in ('/search?', '/scriptures/search', '/internal-use-only/')):
            raise RuntimeError("Generated index includes a blocked route")
        entries_match = re.search(r"const CHURCH_SOURCE_INDEX = Object\.freeze\((\[.*\])\);", content)
        if not entries_match:
            raise RuntimeError("Committed index entries are not valid generated JSON")
        entries = json.loads(entries_match.group(1))
        validate(values["CHURCH_SOURCE_SITEMAP_REVISION"], entries, content)
        validate_review_manifest(
            values["CHURCH_SOURCE_SITEMAP_REVISION"],
            values["CHURCH_SOURCE_ROBOTS_SHA256"],
            values["CHURCH_SOURCE_SITEMAPS_SHA256"],
        )
        print(f"Church source index CHECK PASS: {len(entries)} URLs, {OUTPUT.stat().st_size} bytes")
        return 0

    revision, robots_hash, sitemap_hash, entries = build_entries()
    rendered = render(revision, robots_hash, sitemap_hash, entries)
    validate(revision, entries, rendered)
    OUTPUT.write_text(rendered, encoding="utf-8")
    if args.approve:
        write_review_manifest(revision, robots_hash, sitemap_hash)
    print(f"Church source index BUILD PASS: {len(entries)} URLs, {len(rendered.encode('utf-8'))} bytes, revision {revision}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Church source index BUILD FAIL: {error}", file=sys.stderr)
        raise
