from __future__ import annotations

from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from PIL import Image
from study_gap_art_qa import sitewide_entries, check_sitewide


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/art-study-image-review.json"
PAGES = (
    "art-study/the-living-christ.html",
    "art-study/the-good-shepherd.html",
    "art-study/suffer-the-little-children.html",
    "art-study/be-still.html",
)


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.nav_hrefs: list[str] = []
        self.in_study_nav = 0
        self.in_art_story = 0
        self.in_figcaption = 0
        self.figures = 0
        self.details = 0
        self.resource_cards = 0
        self.continuation_cards = 0
        self.in_continuation = 0
        self.full_assets: list[str] = []
        self.thumb_assets: list[str] = []
        self.links: list[str] = []
        self.captions: list[list[str]] = []
        self.caption_links: list[list[str]] = []
        self.direct_viewers = 0
        self.featured_destinations: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        data = {key: value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "nav" and "fc-study-nav" in classes:
            self.in_study_nav += 1
        if tag == "section" and data.get("id") == "continue-study":
            self.in_continuation += 1
        if tag == "figure" and "fc-art-story" in classes:
            self.figures += 1
            self.in_art_story += 1
        if tag == "details":
            self.details += 1
        if tag == "article" and "fc-resource-card" in classes:
            self.resource_cards += 1
        if tag == "article" and self.in_continuation:
            self.continuation_cards += 1
        if tag == "a" and data.get("href"):
            href = data["href"]
            self.links.append(href)
            if self.in_study_nav:
                self.nav_hrefs.append(href)
            if "data-artwork-detail" in data and href.startswith("art-study/"):
                self.featured_destinations.append(href)
            if self.in_art_story and "data-full-image-viewer" in data:
                self.direct_viewers += 1
            if self.in_art_story and "data-art-study-supporting" in data:
                self.full_assets.append(href)
            if self.in_figcaption and self.captions:
                self.caption_links[-1].append(href)
        if tag == "img" and self.in_art_story and data.get("src"):
            self.thumb_assets.append(data["src"])
        if tag == "figcaption" and self.in_art_story:
            self.in_figcaption += 1
            self.captions.append([])
            self.caption_links.append([])

    def handle_data(self, data: str) -> None:
        if self.captions and self.in_art_story:
            value = " ".join(data.split())
            if value:
                self.captions[-1].append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_study_nav:
            self.in_study_nav -= 1
        if tag == "figure" and self.in_art_story:
            self.in_art_story -= 1
        if tag == "figcaption" and self.in_figcaption:
            self.in_figcaption -= 1
        if tag == "section" and self.in_continuation:
            self.in_continuation -= 1


def local_target(page: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or href.startswith(('#', 'mailto:', 'tel:')):
        return None
    return (page.parent / parsed.path).resolve()


BOM_PAGE = "answers/what-is-the-book-of-mormon.html"


def book_of_mormon_review_errors(reviewed_pages, root=ROOT):
    """Bind the newly allowed page to its exact, hash-reviewed art inventory."""
    errors = []
    review = json.loads((root / "docs/book-of-mormon-art-review.json").read_text(encoding="utf-8"))
    entries = review.get("artworks", [])
    if review.get("page") != BOM_PAGE or not entries:
        return ["Book of Mormon review must bind the exact owning page and a nonempty artwork inventory"]
    assets = [entry.get("asset") for entry in entries]
    if not all(assets) or len(assets) != len(set(assets)):
        errors.append("Book of Mormon review contains missing or duplicate original assets")
    global_entries = reviewed_pages.get(BOM_PAGE, [])
    if len(global_entries) != len(entries) or {entry.get("asset") for entry in global_entries} != set(assets):
        errors.append("Book of Mormon global review inventory differs from its complete dedicated review")
    expected = {entry.get("asset"): entry for entry in entries}
    for entry in global_entries:
        original = expected.get(entry.get("asset"), {})
        asset = (root / entry.get("asset", "")).resolve()
        if (not asset.is_relative_to(root.resolve()) or not asset.is_file()
                or entry.get("reviewed") is not True or entry.get("technical_review_passed") is not True
                or original.get("reviewed") is not True or not entry.get("tone")
                or entry.get("sha256") != original.get("sha256")
                or (asset.is_file() and hashlib.sha256(asset.read_bytes()).hexdigest() != entry.get("sha256"))):
            errors.append("Book of Mormon artwork differs from reviewed technical evidence: " + str(entry.get("asset")))
    return errors


SETTLE_PAGE = "answers/settle-this-in-your-hearts.html"

def settle_review_errors(reviewed_pages, root=ROOT):
    from answer_study_qa import Document
    errors=[]
    review=json.loads((root/'docs/settle-heart-art-review.json').read_text(encoding='utf-8'))
    entries=review.get('artworks',[])
    assets=[e.get('asset') for e in entries]
    if review.get('page')!=SETTLE_PAGE or len(entries)!=15 or len(set(assets))!=15 or sum(e.get('christ') is True for e in entries)!=8:
        return ['Settled faith requires exactly fifteen distinct reviewed originals, eight depicting Christ']
    if review.get('allocation')!={'new-testament':4,'old-testament':2,'book-of-mormon':3,'pearl-of-great-price':2,'church-history':2,'faith-today':2} or dict(Counter(e.get('category') for e in entries))!=review['allocation']:
        errors.append('Settled faith six-category artwork allocation differs from review')
    global_entries=reviewed_pages.get(SETTLE_PAGE,[])
    if [e.get('asset') for e in global_entries]!=assets:
        errors.append('Settled faith global and dedicated review inventories differ')
    for e in entries:
        a=root/e['asset']
        if not a.is_file() or hashlib.sha256(a.read_bytes()).hexdigest()!=e.get('sha256') or not e.get('reviewed') or not e.get('technical_review_passed') or not e.get('tone'):
            errors.append('Settled faith technical artwork review mismatch: '+e['asset'])
        elif Image.open(a).size!=(1536,1024):errors.append('Settled faith image dimensions changed: '+e['asset'])
        g=next((x for x in global_entries if x.get('asset')==e['asset']),{})
        if g.get('sha256')!=e.get('sha256') or g.get('christ')!=e.get('christ') or not g.get('technical_review_passed'):
            errors.append('Settled faith global review evidence mismatch: '+e['asset'])
    d=Document();d.feed((root/SETTLE_PAGE).read_text(encoding='utf-8'));ns=list(d.root.walk())
    shown=[n.attrs.get('href','').removeprefix('../') for n in ns if n.tag=='a' and ('data-hero-viewer' in n.attrs or n.parent.tag=='figure')]
    if shown!=assets:errors.append('Settled faith displayed original inventory differs from exact review order')
    ids={n.attrs['id'] for n in ns if 'id' in n.attrs}
    nav=[a.attrs.get('href','') for n in ns if n.has('fc-study-nav') for a in n.walk() if a.tag=='a']
    if len(nav)<6 or any(not h.startswith('#') or h[1:] not in ids for h in nav):errors.append('Settled faith needs six working study stops')
    if sum(n.tag=='details' for n in ns)<3:errors.append('Settled faith needs three guided reflections')
    return errors


def main() -> int:
    errors: list[str] = []
    gallery = AuditParser()
    gallery.feed((ROOT / "art.html").read_text(encoding="utf-8"))
    if set(gallery.featured_destinations) != set(PAGES) or len(gallery.featured_destinations) != len(PAGES):
        errors.append("Featured Art & Study destinations differ from the complete audited page inventory")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reviewed_pages = manifest.get("pages", {})
    additions = [entry for entry in sitewide_entries() if not entry['talk']]
    errors.extend(check_sitewide())
    required = manifest.get("standard", {}).get("supporting_visuals_per_page")
    if required != 5:
        errors.append("review manifest must require five supporting visuals per page")
    reference = ROOT / manifest.get("standard", {}).get("identity_reference", "")
    if not reference.is_file():
        errors.append("approved Home identity reference is missing")

    all_full_assets: list[str] = []
    html_pages = [
        path.read_text(encoding="utf-8", errors="replace")
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts
    ]

    for relative in PAGES:
        page_additions = [entry for entry in additions if entry['page'] == relative]
        expected_supporting = 4 + len(page_additions)
        page = ROOT / relative
        text = page.read_text(encoding="utf-8")
        parser = AuditParser()
        parser.feed(text)
        parser.close()
        if parser.direct_viewers:
            errors.append(f"{relative}: supporting pictures must open study options before the full-image viewer")
        for asset in ("topic-artwork-details.js", "topic-artwork-details.css"):
            if not re.search(r'(?:src|href)="\.\./' + re.escape(asset) + r'(?:\?[^\"]*)?"', text):
                errors.append(f"{relative}: missing required picture study asset {asset}")

        for marker in (
            'data-art-study-enriched="true"',
            'href="../art-study-enrichment.css?v=20260909-warm"',
            'class="fc-study-opening"',
            'class="fc-art-meditation"',
            'class="fc-reflection-prompts"',
            'class="fc-source-panel"',
            'class="fc-continuation-grid"',
        ):
            if marker not in text:
                errors.append(f"{relative}: missing enrichment marker {marker}")

        if len(parser.nav_hrefs) != 6:
            errors.append(f"{relative}: expected 6 study navigation stops, found {len(parser.nav_hrefs)}")
        for href in parser.nav_hrefs:
            if not href.startswith("#") or href[1:] not in parser.ids:
                errors.append(f"{relative}: navigation target does not exist: {href}")
        if parser.figures != expected_supporting or len(parser.full_assets) != expected_supporting or len(parser.thumb_assets) != expected_supporting:
            errors.append(f"{relative}: requires four preserved artworks plus {len(page_additions)} reviewed additions")
        if parser.details < 3:
            errors.append(f"{relative}: requires at least three guided reflection prompts")
        if parser.resource_cards < 2:
            errors.append(f"{relative}: requires at least two visual official resources")
        if parser.continuation_cards != 3:
            errors.append(f"{relative}: requires exactly three onward study cards")
        church_links = [href for href in parser.links if href.startswith("https://www.churchofjesuschrist.org/")]
        if len(church_links) < 8:
            errors.append(f"{relative}: expected at least 8 official scripture or Church links, found {len(church_links)}")
        if len(parser.captions) != expected_supporting or any(len(" ".join(parts).split()) < 18 for parts in parser.captions):
            errors.append(f"{relative}: every supporting artwork needs a substantive image-specific caption")
        if len(parser.caption_links) != expected_supporting or any(
            not any(href.startswith("https://www.churchofjesuschrist.org/") for href in links)
            for links in parser.caption_links
        ):
            errors.append(f"{relative}: every supporting artwork caption needs an official scripture or Church link")

        entries = reviewed_pages.get(relative, [])
        reviewed_assets = ["../" + entry.get("asset", "") for entry in entries]
        if len(entries) != expected_supporting or any(
            not entry.get("reviewed") or not entry.get("tone") or not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", ""))
            for entry in entries
        ):
            errors.append(f"{relative}: {expected_supporting} hash-bound expression-and-style review records are required")
        if reviewed_assets != parser.full_assets:
            errors.append(f"{relative}: page artwork does not match the reviewed exclusive-art manifest")

        expected_dimensions = tuple(manifest.get("standard", {}).get("full_image_dimensions", []))
        for entry, full_href, thumb_href in zip(entries, parser.full_assets, parser.thumb_assets):
            full = local_target(page, full_href)
            thumb = local_target(page, thumb_href)
            if not full or not full.is_file() or full.stat().st_size < 90_000:
                errors.append(f"{relative}: missing or undersized full artwork {full_href}")
            elif full:
                full_bytes = full.read_bytes()
                if hashlib.sha256(full_bytes).hexdigest() != entry.get("sha256"):
                    errors.append(f"{relative}: artwork changed after visual review {full_href}")
                else:
                    with Image.open(full) as image:
                        if image.format != manifest.get("standard", {}).get("full_image_format") or image.size != expected_dimensions:
                            errors.append(f"{relative}: full artwork must use the reviewed format and dimensions {full_href}")
            if not thumb or not thumb.is_file() or thumb.stat().st_size < 20_000:
                errors.append(f"{relative}: missing or undersized thumbnail {thumb_href}")
            if full and thumb and full.stem != thumb.stem:
                errors.append(f"{relative}: full artwork and thumbnail names do not match")
            if full_href.startswith("../art/"):
                errors.append(f"{relative}: gallery artwork was reused instead of exclusive page art")
            all_full_assets.append(full_href)

        for href in parser.links:
            target = local_target(page, href)
            if target is None:
                continue
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                errors.append(f"{relative}: broken local destination {href}")

    duplicates = [asset for asset, count in Counter(all_full_assets).items() if count > 1]
    if duplicates:
        errors.append(f"supporting artwork is reused across study pages: {duplicates}")
    for asset in all_full_assets:
        # A responsive image may reference its full source in both href and
        # srcset. Exclusivity concerns owning pages, not references on that page.
        if sum(asset in text for text in html_pages) != 1:
            errors.append(f"exclusive supporting artwork must appear on exactly one page: {asset}")
    if set(reviewed_pages) != set(PAGES) | {'answers/aaronic-priesthood-restoration.html', 'answers/melchizedek-priesthood-restoration.html'} | {"book-of-mormon-evidences.html", "church-history.html", "joseph-smith-likeness.html", "atonement.html", "missionary.html", "answers/what-happens-after-death.html", "birth-of-christ.html", "answers/death-of-a-child.html", "answers/divorce-and-faith.html", "answers/god-our-heavenly-father.html", "answers/grief-and-faith.html"} | {e['page'] for e in additions} | {BOM_PAGE, SETTLE_PAGE}:
        errors.append("image review manifest must contain the four featured studies, Evidences, Church History, Joseph Smith likeness, Atonement, Mission, Life After Death, Birth of Christ, Book of Mormon stories and the four reviewed study-gap pages")

    errors.extend(book_of_mormon_review_errors(reviewed_pages))
    errors.extend(settle_review_errors(reviewed_pages))

    life_entries = reviewed_pages.get("answers/what-happens-after-death.html", [])
    if len(life_entries) != 18:
        errors.append("Life After Death requires 18 technical artwork review records")
    life_review_path = ROOT / "docs/life-after-death-art-review.json"
    if life_review_path.is_file():
        life_review = json.loads(life_review_path.read_text(encoding="utf-8"))
        expected_life_assets = {entry.get("asset") for entry in life_review.get("artworks", [])}
        if len({entry.get("asset") for entry in life_entries}) != 18 or {entry.get("asset") for entry in life_entries} != expected_life_assets:
            errors.append("Life After Death technical review inventory must match its complete artwork review")
    for entry in life_entries:
        asset = ROOT / entry.get("asset", "")
        if (entry.get("reviewed") is not True or entry.get("technical_review_passed") is not True
                or not entry.get("tone") or not asset.is_file()
                or hashlib.sha256(asset.read_bytes()).hexdigest() != entry.get("sha256")):
            errors.append(f"Life After Death artwork must match reviewed bytes and pass technical review: {entry.get('asset')}")
    from life_after_death_qa import check as check_life_after_death
    errors.extend(check_life_after_death())

    for entry in reviewed_pages.get("missionary.html", []):
        if not entry.get("reviewed") or hashlib.sha256((ROOT/entry["asset"]).read_bytes()).hexdigest()!=entry.get("sha256"):
            errors.append("Mission replacement must match reviewed bytes")

    from bom_evidences_qa import check as check_evidences
    errors.extend(check_evidences())
    from history_art_qa import check as check_history
    errors.extend(check_history())
    from joseph_smith_likeness_qa import check as check_likeness
    errors.extend(check_likeness())

    if errors:
        print("Art study enrichment QA failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Art study enrichment QA passed: 4 featured pages with four preserved plus manifest-bound supporting additions each; exact sources, reviewed hashes, reflection/resource/onward paths, and Evidences/Church History contracts verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
