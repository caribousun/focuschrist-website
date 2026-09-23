"""Book of Mormon story/art integration gate; visual and browser review are separate.

Counts DOM placements, not manifest promises. Responsive variants count once.
Source lineage catches crops/resizes of one original; decoded hashes catch a
renamed/re-encoded copy. Neither mechanism certifies a person's likeness.
"""
from copy import deepcopy
import hashlib
from html import escape
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit, unquote

from PIL import Image, ImageOps
from life_after_death_qa import Parser

ROOT = Path(__file__).resolve().parents[1]
PAGE = "answers/what-is-the-book-of-mormon.html"
MANIFEST = "docs/book-of-mormon-art-review.json"
PRESERVED = {
    "assets/heroes/topics/book-of-mormon-full.webp": "hero",
    "assets/page-art/topics/christ-bountiful-1536.webp": "body",
    **{f"assets/page-art/exclusive/{key}-1536.webp": "body" for key in (
        "mormon-nephi-purpose", "mormon-ponder", "mormon-settle", "mormon-covenant-care"
    )},
}
# Approved pre-enrichment markup and bytes captured from the PR329 baseline.
# This immutable comparison is separate from the mutable integration review manifest.
PRESERVED_BASELINES = {
    "assets/heroes/topics/book-of-mormon-full.webp": {
        "sha256": "586b17d10795615303b998fe5eef3970b1c276a90468f9b0a78b723003488b93",
        "role": "hero",
        "hero": {
            "href": "../assets/heroes/topics/book-of-mormon-full.webp",
            "style": "--topic-hero-desktop:url('../assets/heroes/topics/book-of-mormon-desktop.webp');--topic-hero-mobile:url('../assets/heroes/topics/book-of-mormon-mobile.webp')",
            "data-full-image-alt": "A young adult man reads the Book of Mormon on a commuter train.",
            "aria-label": "Explore artwork: Begin with the record"
        },
        "assets": {
            "assets/heroes/topics/book-of-mormon-desktop.webp": "83991d9944e4453b04fb456b3758d5b05367de66f568829701093a39c924e0a7",
            "assets/heroes/topics/book-of-mormon-full.webp": "586b17d10795615303b998fe5eef3970b1c276a90468f9b0a78b723003488b93",
            "assets/heroes/topics/book-of-mormon-mobile.webp": "9a25c7a20e12b4c0758210be1b9eaffff24f3e1dd3095331aa634a67d63b353a"
        }
    },
    "assets/page-art/topics/christ-bountiful-1536.webp": {
        "sha256": "1fd4063b0789e0a7d2a71bc5939d9bbf8e025556797f92705b3f87108a492927",
        "role": "body",
        "image": {
            "src": "../assets/page-art/topics/christ-bountiful-800.webp",
            "srcset": "../assets/page-art/topics/christ-bountiful-800.webp 800w, ../assets/page-art/topics/christ-bountiful-1536.webp 1536w",
            "sizes": "(max-width: 700px) 100vw, 600px",
            "width": "1536",
            "height": "1024",
            "alt": "The risen Jesus Christ extending an invitation to a group of people",
            "loading": "lazy",
            "decoding": "async",
            "style": "--study-image-ratio: 800 / 533"
        },
        "assets": {
            "assets/page-art/topics/christ-bountiful-1536.webp": "1fd4063b0789e0a7d2a71bc5939d9bbf8e025556797f92705b3f87108a492927",
            "assets/page-art/topics/christ-bountiful-800.webp": "7f7c26b6aaab078cc05c7ae509d3350f9290cf03d2e97ebb22dddfffa93158ef"
        }
    },
    "assets/page-art/exclusive/mormon-nephi-purpose-1536.webp": {
        "sha256": "0a3aa09303563f88cc668483f262c6958d062402822969b303617753a3b4d054",
        "role": "body",
        "image": {
            "src": "../assets/page-art/exclusive/mormon-nephi-purpose-800.webp",
            "srcset": "../assets/page-art/exclusive/mormon-nephi-purpose-800.webp 800w, ../assets/page-art/exclusive/mormon-nephi-purpose-1536.webp 1536w",
            "sizes": "(max-width: 700px) calc(100vw - 36px), 600px",
            "width": "1536",
            "height": "1024",
            "alt": "A contemporary reader in a burgundy shirt studying a book on a stone terrace above a green valley",
            "loading": "lazy",
            "decoding": "async",
            "style": "--study-image-ratio:1536/1024;aspect-ratio:auto 1536/1024"
        },
        "assets": {
            "assets/page-art/exclusive/mormon-nephi-purpose-1536.webp": "0a3aa09303563f88cc668483f262c6958d062402822969b303617753a3b4d054",
            "assets/page-art/exclusive/mormon-nephi-purpose-800.webp": "fda06b52d526636fc3a885cad8700a6329e61c221bac71bdcee59a4f988612f0"
        }
    },
    "assets/page-art/exclusive/mormon-ponder-1536.webp": {
        "sha256": "77e4c3974e8dcf7c10be7f82ca348171025e34faba48e3719375e10028f6771e",
        "role": "body",
        "image": {
            "src": "../assets/page-art/exclusive/mormon-ponder-800.webp",
            "srcset": "../assets/page-art/exclusive/mormon-ponder-800.webp 800w, ../assets/page-art/exclusive/mormon-ponder-1536.webp 1536w",
            "sizes": "(max-width: 700px) 100vw, 600px",
            "width": "1536",
            "height": "1024",
            "alt": "A woman with an open book on her lap pausing to look across a quiet lake",
            "loading": "lazy",
            "decoding": "async",
            "style": "--study-image-ratio:1536/1024;aspect-ratio:auto 1536/1024"
        },
        "assets": {
            "assets/page-art/exclusive/mormon-ponder-1536.webp": "77e4c3974e8dcf7c10be7f82ca348171025e34faba48e3719375e10028f6771e",
            "assets/page-art/exclusive/mormon-ponder-800.webp": "2b9ea55253423cdb78326a7299e05e2e87aad773a7f7721e949ea08a62e518a9"
        }
    },
    "assets/page-art/exclusive/mormon-settle-1536.webp": {
        "sha256": "f522686e761d898c94d089487dc29def612d18ec71d3c89a5511cfe5a4e4b123",
        "role": "body",
        "image": {
            "src": "../assets/page-art/exclusive/mormon-settle-800.webp",
            "srcset": "../assets/page-art/exclusive/mormon-settle-800.webp 800w, ../assets/page-art/exclusive/mormon-settle-1536.webp 1536w",
            "sizes": "(max-width: 700px) calc(100vw - 36px), 600px",
            "width": "1536",
            "height": "1024",
            "alt": "A grandmother listening to a teenage boy as they study together on a living-room sofa",
            "loading": "lazy",
            "decoding": "async",
            "style": "--study-image-ratio:1536/1024;aspect-ratio:auto 1536/1024"
        },
        "assets": {
            "assets/page-art/exclusive/mormon-settle-1536.webp": "f522686e761d898c94d089487dc29def612d18ec71d3c89a5511cfe5a4e4b123",
            "assets/page-art/exclusive/mormon-settle-800.webp": "9fa4015e09f49f0cbba5f460312896c03f6ade4f4f1ec8384e3c2c1784b4c5c0"
        }
    },
    "assets/page-art/exclusive/mormon-covenant-care-1536.webp": {
        "sha256": "be6f3728c9a431570c17a0c6c59428be35700bb651646e072a27299cbc6a00c3",
        "role": "body",
        "image": {
            "src": "../assets/page-art/exclusive/mormon-covenant-care-800.webp",
            "srcset": "../assets/page-art/exclusive/mormon-covenant-care-800.webp 800w, ../assets/page-art/exclusive/mormon-covenant-care-1536.webp 1536w",
            "sizes": "(max-width: 700px) calc(100vw - 36px), 600px",
            "width": "1536",
            "height": "1024",
            "alt": "Adults helping load folded blankets and food into a neighbor’s car",
            "loading": "lazy",
            "decoding": "async",
            "style": "--study-image-ratio:1536/1024;aspect-ratio:auto 1536/1024"
        },
        "assets": {
            "assets/page-art/exclusive/mormon-covenant-care-1536.webp": "be6f3728c9a431570c17a0c6c59428be35700bb651646e072a27299cbc6a00c3",
            "assets/page-art/exclusive/mormon-covenant-care-800.webp": "f94a6e6e60fe6e6b270791fce183a51099fa0958ca7a004c7a7db34a600a75c6"
        }
    }
}

STORIES = (
    "jaredite-faith", "lehis-family", "nephis-witness", "keepers-of-the-record",
    "kings-and-covenants", "deliverance-and-covenant", "a-changed-heart",
    "lamanite-conversions", "faith-among-the-poor", "captain-moroni", "covenants-and-courage",
    "moroni-and-pahoran", "voices-before-the-dawn", "the-promised-sign",
    "the-saviors-ministry", "the-saviors-sermon", "the-saviors-compassion",
    "the-saviors-lasting-witness", "a-people-made-one", "mormons-final-hope", "the-final-witnesses", "moroni-and-joseph",
)
NAV = ("watch-and-study", "scripture-study", "guided-practice", "study-resources",
       "continue-study", "personal-reflections")
HASH = re.compile(r"[0-9a-f]{64}\Z")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words(node):
    return " ".join(" ".join(part for n in node.walk() for part in n.words).split())


def local_asset(root, value):
    url = urlsplit(value or "")
    if not url.path or url.scheme or url.netloc:
        return None
    path = (root / url.path.lstrip("/") if url.path.startswith("/")
            else root / Path(PAGE).parent / url.path).resolve()
    return path if path.is_relative_to(root.resolve()) else None


def verified_cross_study_reference(root, image, nodes):
    """An explicit non-owning article must link its exact thumbnail to its owning figure."""
    containers = [n for n in nodes if n.tag == 'article' and n.attrs.get('data-linked-picture-reference')
                  and any(child is image for child in n.walk())]
    if len(containers) != 1:
        return False
    card = containers[0]
    if any(n.tag == 'figure' for n in card.walk()):
        return False
    if sum(n.tag == 'img' for n in card.walk()) != 1:
        return False
    trigger = next((n for n in card.walk() if n.tag == 'a' and any(c is image for c in n.walk())), None)
    if trigger is None:
        return False
    url = urlsplit(trigger.attrs.get('href', ''))
    owner = local_asset(root, unquote(url.path))
    if url.scheme or url.netloc or not url.fragment or not owner or owner == (root/PAGE).resolve() or owner.suffix != '.html' or not owner.is_file():
        return False
    owner_nodes = list(Parser(owner.read_text(encoding='utf8')).root.walk())
    targets = [n for n in owner_nodes if n.attrs.get('id') == unquote(url.fragment)]
    if len(targets) != 1:
        return False
    figures = [n for n in targets[0].walk() if n.tag == 'figure']
    source = local_asset(root, image.attrs.get('src'))
    if not source or not source.is_file():
        return False
    for figure in figures:
        for candidate in figure.walk():
            if candidate.tag != 'img':
                continue
            src = urlsplit(candidate.attrs.get('src', ''))
            if src.scheme or src.netloc:
                continue
            path = (root/unquote(src.path).lstrip('/') if src.path.startswith('/') else owner.parent/unquote(src.path)).resolve()
            if path.is_relative_to(root) and path == source:
                return True
    return False


def scripture_error(root, url):
    parsed = urlsplit(url or "")
    query = parse_qs(parsed.query)
    selector = query.get("id", [""])[0]
    if not (parsed.scheme == "https" and parsed.netloc == "www.churchofjesuschrist.org"
            and (parsed.path.startswith("/study/scriptures/bofm/") or parsed.path == "/study/scriptures/pgp/js-h/1")
            and re.fullmatch(r"p\d+(?:-p\d+)?(?:,p\d+(?:-p\d+)?)*", selector)
            and query.get("lang") == ["eng"]
            and parsed.fragment == re.split(r"[-,]", selector)[0]):
        return "requires an exact official Book of Mormon or Joseph Smith-History verse selector: " + str(url)
    chapter = root / "scripture-data" / (parsed.path.removeprefix("/study/scriptures/") + ".json")
    if not chapter.is_file():
        return "scripture chapter is unavailable: " + str(url)
    try:
        count = len(json.loads(chapter.read_text(encoding="utf-8"))["verses"])
        for group in selector.split(","):
            values = [int(v) for v in re.findall(r"\d+", group)]
            if not 1 <= values[0] <= values[-1] <= count:
                return "scripture selector is out of range: " + str(url)
    except (OSError, ValueError, KeyError, TypeError):
        return "invalid scripture chapter data: " + str(chapter)
    return None


def audit(root, text, manifest, preserved_baselines=None):
    preserved_baselines = PRESERVED_BASELINES if preserved_baselines is None else preserved_baselines
    root = root.resolve()
    errors = []

    def need(condition, message):
        if not condition:
            errors.append(message)

    nodes = list(Parser(text).root.walk())
    ids = [n.attrs["id"] for n in nodes if n.attrs.get("id")]
    need(len(ids) == len(set(ids)), "duplicate HTML IDs")
    need(not re.search(r"BOM ART:|BOM_(?:ART|RESOURCE)_|\b(?:TODO|PLACEHOLDER)\b", text),
         "unresolved story/art integration placeholder")
    for n in nodes:
        href = n.attrs.get("href") or ""
        if href.startswith("#"):
            need(href[1:] in ids, "broken local anchor: " + href)
    nav = [n for n in nodes if n.tag == "nav" and n.has("fc-study-nav")]
    actual_nav = [n.attrs.get("href") for n in nav[0].walk() if n.tag == "a"] if len(nav) == 1 else []
    need(set(actual_nav) == {"#" + item for item in NAV} and len(actual_nav) == 6,
         "six original study navigation destinations must remain")
    stories = [n for n in nodes if n.tag == "section" and n.has("bom-story")]
    need(set(STORIES).issubset({n.attrs.get("id") for n in stories}), "one or more of the 22 story stops are missing")
    directories = [n for n in nodes if n.tag == "nav" and n.has("bom-story-directory")]
    directory_links = [n.attrs.get("href") for d in directories for n in d.walk() if n.tag == "a"]
    need(len(directories) == 1 and all(directory_links.count("#" + item) == 1 for item in STORIES),
         "story directory must link to each story exactly once")
    for story in stories:
        paragraphs = [n for n in story.children if n.tag == "p" and not n.has("fc-eyebrow")]
        need(sum(len(words(p).split()) for p in paragraphs) >= 100,
             "story needs substantive study prose: " + str(story.attrs.get("id")))
        links = [n.attrs.get("href") for p in paragraphs for n in p.walk()
                 if n.tag == "a" and n.has("fc-inline-scripture")]
        need(bool(links), "story requires inline scripture: " + str(story.attrs.get("id")))
        for url in links:
            problem = scripture_error(root, url)
            if problem:
                errors.append(problem)
    need(sum(n.tag == "details" for s in stories for n in s.walk()) >= 3,
         "at least three story reflections must remain")
    for asset in ("topic-artwork-details.js", "topic-artwork-details.css", "hero-details.js", "bom-story-journey.css"):
        need(any(asset in (n.attrs.get("src") or n.attrs.get("href") or "") for n in nodes),
             "missing shared story/interaction dependency: " + asset)

    need(manifest.get("page") == PAGE, "review manifest must bind this exact page")
    minimum = manifest.get("minimum_unique")
    need(isinstance(minimum, int) and not isinstance(minimum, bool) and minimum >= 20,
         "owner minimum of 20 unique pictures may not be weakened")
    additions = manifest.get("artworks", [])
    preserved = manifest.get("preserved", [])
    if not isinstance(additions, list) or not isinstance(preserved, list):
        return errors + ["manifest artwork collections must be lists"], {}
    if not all(isinstance(e, dict) for e in additions + preserved):
        return errors + ["manifest artwork records must be objects"], {}
    need(bool(additions), "reviewed new story artworks are missing")
    need({e.get("asset"): e.get("role") for e in preserved} == PRESERVED,
         "all six preserved hero/body originals must remain in the manifest")
    for field in ("key", "asset", "thumbnail", "source_sha256"):
        values = [entry.get(field) for entry in additions]
        need(all(values) and len(values) == len(set(values)), "missing/duplicate new artwork " + field)
    for entry in preserved:
        baseline = preserved_baselines.get(entry.get("asset"), {})
        label = str(entry.get("asset"))
        need(bool(baseline) and entry.get("sha256") == baseline.get("sha256"),
             label + ": preserved original manifest hash differs from approved baseline")
        for relative, expected in baseline.get("assets", {}).items():
            asset = root / relative
            need(asset.is_file() and digest(asset) == expected,
                 label + ": preserved responsive/original bytes differ from approved baseline: " + relative)
    entries = additions + preserved
    paths = [entry.get("asset") for entry in entries]
    need(all(paths) and len(paths) == len(set(paths)), "duplicate original asset in complete inventory")
    by_asset = {(root / e["asset"]).resolve(): e for e in entries if isinstance(e.get("asset"), str)}
    pixels = []
    sizes = {}
    for entry in entries:
        label = entry.get("key") or entry.get("asset") or "unnamed artwork"
        need(isinstance(entry.get("christ"), bool), str(label) + ": Christ count requires explicit boolean")
        fields = [("asset", "sha256")]
        if entry in additions:
            fields.append(("thumbnail", "thumbnail_sha256"))
            need(entry.get("reviewed") is True and bool(entry.get("review")), str(label) + ": visual review incomplete")
            need(isinstance(entry.get("owner_approved"), bool), str(label) + ": owner approval must be separately explicit")
            if entry.get("owner_approved") is True:
                need(bool(entry.get("owner_approval_evidence")), str(label) + ": owner approval requires evidence")
            need(bool(HASH.fullmatch(entry.get("source_sha256") or "")), str(label) + ": missing source lineage hash")
            need(bool(entry.get("source_file")), str(label) + ": missing source provenance")
            source = Path(entry.get("source_file") or "__missing__")
            source = source if source.is_absolute() else root / source
            if source.is_file():
                need(digest(source) == entry.get("source_sha256"), str(label) + ": retained original source bytes changed")
            problem = scripture_error(root, entry.get("source_url"))
            if problem:
                errors.append(str(label) + ": " + problem)
        for field, hash_field in fields:
            value = entry.get(field)
            path = (root / value).resolve() if isinstance(value, str) else root
            need(path.is_relative_to(root) and path.is_file(), str(label) + ": missing local " + field)
            need(bool(HASH.fullmatch(entry.get(hash_field) or "")), str(label) + ": invalid " + hash_field)
            if not path.is_relative_to(root) or not path.is_file():
                continue
            need(digest(path) == entry.get(hash_field), str(label) + ": changed reviewed " + field)
            try:
                with Image.open(path) as image:
                    rgb = ImageOps.exif_transpose(image).convert("RGB")
                    sizes[path] = rgb.size
                    if field == "asset":
                        pixels.append((rgb.size, hashlib.sha256(rgb.tobytes()).hexdigest()))
            except (OSError, ValueError) as exc:
                errors.append(str(label) + ": undecodable image: " + str(exc))
    need(len(pixels) == len(set(pixels)), "originals repeat decoded pixels under different filenames/encodings")

    mains = [n for n in nodes if n.tag == "main"]
    main_nodes = list(mains[0].walk()) if len(mains) == 1 else []
    figures = [n for n in main_nodes if n.tag == "figure"
               and any(c.tag == "img" for c in n.walk())]
    placements = []
    figure_images = set()
    for figure in figures:
        children = list(figure.walk())
        images = [n for n in children if n.tag == "img"]
        figure_images.update(id(n) for n in images)
        triggers = [n for n in children if n.tag == "a" and local_asset(root, n.attrs.get("href")) in by_asset]
        need(len(images) == 1 and len(triggers) == 1, "each body figure requires one bound original and one responsive image")
        if len(images) != 1 or len(triggers) != 1:
            continue
        trigger, image = triggers[0], images[0]
        full = local_asset(root, trigger.attrs.get("href"))
        placements.append(full)
        entry = by_asset[full]
        need(entry.get("role", "body") == "body", "hero must not repeat in body")
        if entry not in additions:
            baseline = preserved_baselines.get(entry.get("asset"), {}).get("image", {})
            need(bool(baseline), "preserved body image baseline missing: " + str(entry.get("asset")))
            for field, expected in baseline.items():
                need(image.attrs.get(field) == expected,
                     str(entry.get("asset")) + ": preserved image " + field + " differs from approved baseline")
            continue
        label = entry.get("key", "unnamed")
        need(any(name.startswith("data-") and value == label for name, value in figure.attrs.items()),
             str(label) + ": figure data key differs from review")
        need(trigger.attrs.get("aria-haspopup") == "dialog", str(label) + ": study dialog trigger missing")
        thumb = local_asset(root, image.attrs.get("src"))
        need(thumb == (root / entry["thumbnail"]).resolve(), str(label) + ": thumbnail differs from review")
        need(image.attrs.get("alt") == entry.get("alt") and bool(entry.get("alt")), str(label) + ": alternative text differs from review")
        need(image.attrs.get("loading") == "lazy", str(label) + ": body artwork must load lazily")
        srcset = {local_asset(root, part.strip().split()[0]) for part in (image.attrs.get("srcset") or "").split(",") if part.strip()}
        need({full, thumb}.issubset(srcset) and bool(image.attrs.get("sizes")), str(label) + ": responsive variants missing")
        if full in sizes and thumb in sizes:
            w, h = sizes[full]
            tw, th = sizes[thumb]
            need(tw < w and abs(w / h - tw / th) < .01, str(label) + ": responsive geometry mismatch")
            try:
                declared = int(image.attrs.get("width", 0)), int(image.attrs.get("height", 0))
            except (ValueError, TypeError):
                declared = 0, 0
            need(declared in (sizes[full], sizes[thumb]), str(label) + ": incorrect intrinsic image dimensions")
        captions = [n for n in children if n.tag == "figcaption"]
        titles = [n for n in children if n.tag in ("h3", "h4")]
        need(len(captions) == 1 and any(words(n) == entry.get("title") for n in titles), str(label) + ": picture title missing/different")
        if captions:
            need(bool(entry.get("caption")) and entry.get("caption") in words(captions[0]), str(label) + ": picture caption missing/different")
        sources = [n for n in children if n.tag == "a" and n.attrs.get("href") == entry.get("source_url")]
        need(any(entry.get("label") and entry["label"] in words(n) for n in sources), str(label) + ": picture source label/verses differ from review")
    owned_paths = {local_asset(root, '../'+e[field]) for e in manifest.get('artworks', []) + manifest.get('preserved', []) for field in ('asset', 'thumbnail') if e.get(field)}
    owned_paths.update((root/value).resolve() for baseline in preserved_baselines.values() for value in baseline.get('assets', {}))
    for image in (n for n in main_nodes if n.tag == "img" and id(n) not in figure_images):
        path = local_asset(root, image.attrs.get("src"))
        need(not (path and "/assets/page-art/" in path.as_posix()) or (path not in owned_paths and verified_cross_study_reference(root, image, nodes)), "artwork repeated/outside its owning study figure")
    heroes = [n for n in nodes if n.tag == "a" and n.attrs.get("data-hero-record") == "topic-book-of-mormon"]
    need(len(heroes) == 1, "exactly one preserved Book of Mormon hero required")
    if len(heroes) == 1:
        placements.append(local_asset(root, heroes[0].attrs.get("href")))
        hero_baseline = preserved_baselines.get("assets/heroes/topics/book-of-mormon-full.webp", {}).get("hero", {})
        for field, expected in hero_baseline.items():
            need(heroes[0].attrs.get(field) == expected, "preserved hero " + field + " differs from approved baseline")
    need(len(placements) == len(set(placements)), "same-page artwork original repeated")
    need(set(placements) == set(by_asset), "DOM original inventory differs from complete reviewed inventory (missing or extra artwork)")
    total = len(set(placements) & set(by_asset))
    christ = sum(by_asset[p].get("christ") is True for p in set(placements) if p in by_asset)
    need(total >= max(20, minimum if isinstance(minimum, int) else 20), "fewer than required unique original pictures")
    need(christ >= (total + 1) // 2, f"Christ picture ratio fails: {christ}/{total}; requires {(total + 1) // 2}")
    return list(dict.fromkeys(errors)), {"unique": total, "christ": christ, "stories": len(stories), "new": len(additions)}


def self_test():
    """Real files and DOM mutations prove the gate rejects relevant regressions."""
    with tempfile.TemporaryDirectory(prefix="focus-bom-qa-") as directory:
        root = Path(directory)
        chapter = root / "scripture-data/bofm/alma/32.json"
        chapter.parent.mkdir(parents=True)
        chapter.write_text(json.dumps({"verses": ["verse"] * 43}), encoding="utf-8")
        source = "https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/32?id=p21-p28&lang=eng#p21"
        manifest = {"page": PAGE, "minimum_unique": 20, "artworks": [], "preserved": []}
        figures = []
        fixture_baselines = {}
        for index, (asset, role) in enumerate(list(PRESERVED.items()) + [(f"assets/page-art/test-{i}.webp", "body") for i in range(14)]):
            path = root / asset
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (60, 40), (index * 11, index * 7, index * 5)).save(path, lossless=True)
            entry = {"asset": asset, "sha256": digest(path), "christ": index < 10}
            if index < 6:
                entry["role"] = role
                manifest["preserved"].append(entry)
                baseline = {"sha256": digest(path), "role": role, "assets": {asset: digest(path)}}
                if role == "body":
                    thumbnail = asset.replace(".webp", "-thumb.webp")
                    with Image.open(path) as image:
                        image.resize((30, 20)).save(root / thumbnail, lossless=True)
                    baseline["assets"][thumbnail] = digest(root / thumbnail)
                    baseline["image"] = {
                        "src": "../" + thumbnail,
                        "srcset": f"../{thumbnail} 30w, ../{asset} 60w",
                        "sizes": "100vw", "width": "60", "height": "40",
                        "alt": f"Preserved scene {index}", "loading": "lazy", "decoding": "async",
                    }
                    attrs = " ".join(f'{key}="{escape(value, quote=True)}"' for key, value in baseline["image"].items())
                    figures.append(f'<figure><a href="../{asset}"><img {attrs}></a></figure>')
                else:
                    baseline["hero"] = {"href": "../" + asset}
                fixture_baselines[asset] = baseline
                continue
            thumbnail = asset.replace(".webp", "-thumb.webp")
            with Image.open(path) as image:
                image.resize((30, 20)).save(root / thumbnail, lossless=True)
            entry.update(key=f"test-{index}", thumbnail=thumbnail, thumbnail_sha256=digest(root / thumbnail),
                         source_sha256=hashlib.sha256(str(index).encode()).hexdigest(), source_file=f"unretained-original-{index}.png",
                         reviewed=True, owner_approved=False, review={"visual": "fixture"}, source_url=source,
                         label="Alma 32:21-28", title=f"A distinct story {index}", caption=f"A meaningful caption for original picture {index}.", alt=f"Scene {index}")
            manifest["artworks"].append(entry)
            figures.append(f'<figure data-bom-art="{entry["key"]}"><a href="../{asset}" aria-haspopup="dialog"><img src="../{thumbnail}" srcset="../{thumbnail} 30w, ../{asset} 60w" sizes="100vw" width="60" height="40" alt="{entry["alt"]}" loading="lazy"></a><figcaption><h3>{entry["title"]}</h3><p>{entry["caption"]}</p><a href="{escape(source, quote=True)}">{entry["label"]}</a></figcaption></figure>')
        stories = ''.join(f'<section class="bom-story" id="{key}"><p>{"Substantive study prose. " * 40}<a class="fc-inline-scripture" href="{escape(source, quote=True)}">Alma 32:21-28</a></p><details><summary>Reflect</summary></details></section>' for key in STORIES)
        text = '<link href="topic-artwork-details.css"><link href="bom-story-journey.css"><script src="topic-artwork-details.js"></script><script src="hero-details.js"></script>'
        text += '<a data-hero-record="topic-book-of-mormon" href="../assets/heroes/topics/book-of-mormon-full.webp"></a><main>'
        text += '<nav class="fc-study-nav">' + ''.join(f'<a href="#{key}">{key}</a>' for key in NAV) + '</nav>'
        text += ''.join(f'<section id="{key}"></section>' for key in NAV)
        text += '<nav class="bom-story-directory">' + ''.join(f'<a href="#{key}">{key}</a>' for key in STORIES) + '</nav>'
        text += stories + ''.join(figures) + '</main>'
        errors, counts = audit(root, text, manifest, fixture_baselines)
        assert not errors, errors
        assert counts["unique"] == 20 and counts["christ"] == 10
        def rejected(label, html, review, fragment):
            failures, _ = audit(root, html, review, fixture_baselines)
            assert any(fragment in failure for failure in failures), (label, failures)
        reference_asset = root/'assets/page-art/reference.webp'
        Image.new('RGB', (30,20), (11,22,33)).save(reference_asset, lossless=True)
        owner = root/'other.html'
        owner.write_text('<figure id="scene"><img src="assets/page-art/reference.webp"></figure>', encoding='utf8')
        reference = '<article data-linked-picture-reference="test"><a href="/other.html#scene"><img src="/assets/page-art/reference.webp"></a></article>'
        good_reference = text.replace('</main>', reference+'</main>')
        assert not audit(root, good_reference, manifest, fixture_baselines)[0]
        for label, replacement in [('missing anchor', '/other.html#missing'), ('missing owner', '/missing.html#scene'), ('same owner', '/'+PAGE+'#scene')]:
            rejected(label, good_reference.replace('/other.html#scene', replacement), manifest, 'artwork repeated/outside')
        rejected('unlinked fake reference', good_reference.replace('<a href="/other.html#scene">', '<a>'), manifest, 'artwork repeated/outside')
        owner.write_text('<figure id="scene"><img src="assets/page-art/wrong.webp"></figure>', encoding='utf8')
        rejected('misowned thumbnail', good_reference, manifest, 'artwork repeated/outside')
        owner.write_text('<figure id="scene"><img src="assets/page-art/reference.webp"></figure>', encoding='utf8')
        rejected('own original disguised as reference', good_reference.replace('/assets/page-art/reference.webp', '../'+manifest['artworks'][0]['thumbnail']), manifest, 'artwork repeated/outside')
        rejected("missing placed original", text.replace(figures[-1], ""), manifest, "DOM original inventory")
        rejected("same-page repetition", text.replace('</main>', figures[-1] + '</main>'), manifest, "same-page artwork")
        preserved_body = next(value for value in fixture_baselines.values() if value["role"] == "body")
        preserved_src = preserved_body["image"]["src"]
        preserved_srcset = preserved_body["image"]["srcset"]
        swapped = text.replace(f'src="{preserved_src}"', f'src="../{manifest["artworks"][0]["thumbnail"]}"', 1)
        rejected("preserved image swap with original link retained", swapped, manifest, "preserved image src differs")
        duplicated = text.replace(f'srcset="{preserved_srcset}"', f'srcset="{preserved_srcset}, {preserved_src} 30w"', 1)
        rejected("preserved responsive duplicate with original link retained", duplicated, manifest, "preserved image srcset differs")

        changed = deepcopy(manifest)
        changed["artworks"][0]["christ"] = False
        rejected("Christ ratio", text, changed, "Christ picture ratio")
        changed = deepcopy(manifest)
        changed["artworks"][1]["source_sha256"] = changed["artworks"][0]["source_sha256"]
        # The second file may be a visually different crop, but its original lineage is still the same.
        rejected("crop masquerading as original", text, changed, "duplicate new artwork source_sha256")
        changed = deepcopy(manifest)
        other = root / changed["artworks"][1]["asset"]
        with Image.open(root / changed["artworks"][0]["asset"]) as image:
            image.save(other, format="PNG")
        changed["artworks"][1]["sha256"] = digest(other)
        rejected("renamed different encoding", text, changed, "repeat decoded pixels")
        # Restore the original fixture before testing independent hash and citation failures.
        Image.new("RGB", (60, 40), (77, 49, 35)).save(other, lossless=True)
        changed = deepcopy(manifest)
        changed["preserved"][0]["sha256"] = "0" * 64
        rejected("preserved hero hash", text, changed, "changed reviewed asset")
        changed = deepcopy(manifest)
        changed["artworks"][0]["source_url"] = source.replace("p21-p28", "p21-p99")
        rejected("verse range", text, changed, "out of range")
        rejected("integration placeholder", text + '<!-- BOM ART: pending -->', manifest, "placeholder")
    print("Book of Mormon story QA self-test passed: positive original/reference inventories and sixteen relevant rejection fixtures.")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return 0
    path = ROOT / MANIFEST
    if not path.is_file():
        print("Book of Mormon story QA failed: missing " + MANIFEST)
        return 1
    try:
        errors, counts = audit(ROOT, (ROOT / PAGE).read_text(encoding="utf-8"), json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("Book of Mormon story QA failed: " + str(exc))
        return 1
    if errors:
        print("Book of Mormon story QA failed:\n- " + "\n- ".join(errors))
        return 1
    print(f'Book of Mormon story QA passed: {counts["unique"]} unique originals, {counts["christ"]} depicting Christ, '
          f'{counts["new"]} new reviewed pictures, {counts["stories"]} story stops; preserved hashes, decoded/source uniqueness, '
          'exact scripture selections, responsive placements, and original navigation.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
