"""Guard shared study rails and Joseph navigation; browser geometry is separate."""
import re
from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []


def require(ok, message):
    if not ok:
        ERRORS.append(message)


def compact(value):
    return re.sub(r"\s+", "", value)


def declarations(filename, selector):
    # Inspect every exact-selector rule, including later media-query overrides.
    css = re.sub(r"/\*.*?\*/", "", (ROOT / filename).read_text(encoding="utf-8"), flags=re.S)
    blocks = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
    return [dict((k.strip(), compact(v)) for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", body))
            for selectors, body in blocks if selector in [s.strip() for s in selectors.split(",")]]


def contract(filename, selector, expected):
    rules = declarations(filename, selector)
    require(bool(rules), filename + ": missing " + selector)
    for prop, value in expected.items():
        values = [r[prop] for r in rules if prop in r]
        require(bool(values) and all(v == compact(value) for v in values),
                filename + ": " + selector + " must retain " + prop + ": " + value)


PADDED = "calc(var(--fc-standard) + 2 * var(--fc-body-gutter))"
contract("site-system.css", ".fc-actions", {"justify-content": "center"})
contract("joseph-smith-likeness.css", ".likeness-main", {"max-width": PADDED, "padding": "0 var(--fc-body-gutter)"})
contract("atonement.css", ".atonement-main", {"max-width": PADDED, "padding-inline": "var(--fc-body-gutter)"})
contract("site-search.css", ".fc-search-main", {"max-width": PADDED, "padding": "var(--fc-body-section-gap) var(--fc-body-gutter)"})
contract("bom-evidences.css", ".fc-bom-evidences .bom-reading", {"max-width": "var(--fc-standard)", "width": "calc(100% - 2 * var(--fc-body-gutter))"})
contract("come-follow-me.css", ".cfm-wrap", {"width": "min(var(--fc-standard),100%)"})
contract("come-follow-me.css", ".cfm-jump", {"justify-content": "center"})
contract("joseph-smith-likeness.css", ".likeness-chapter", {"padding": "0", "margin-block": "var(--fc-body-section-gap)", "border": "0"})
contract("joseph-smith-likeness.css", ".likeness-path", {"justify-content": "center", "margin-block": "var(--fc-body-section-gap)"})
for selector in (".likeness-chapter > p", ".likeness-art figcaption", ".likeness-evidence", ".likeness-reflection"):
    contract("joseph-smith-likeness.css", selector, {"max-width": "none"})
for selector in (".likeness-main .fc-actions", ".likeness-main .fc-study-visual-sources"):
    contract("joseph-smith-likeness.css", selector, {"justify-content": "center"})

PAGES = {
    "joseph-smith-likeness.html": ("joseph-smith-likeness.css", "likeness-main"),
    "atonement.html": ("atonement.css", "atonement-main"),
    "book-of-mormon-evidences.html": ("bom-evidences.css", "bom-reading"),
    "come-follow-me.html": ("come-follow-me.css", "cfm-wrap"),
    "search.html": ("site-search.css", "fc-search-main"),
}
for page, (stylesheet, rail) in PAGES.items():
    doc = Document()
    doc.feed((ROOT / page).read_text(encoding="utf-8"))
    nodes = list(doc.root.walk())
    require(any(n.has(rail) for n in nodes), page + ": intended content rail missing")
    require(sum(n.tag == "link" and urlsplit(n.attrs.get("href", "")).path == stylesheet for n in nodes) == 1,
            page + ": intended stylesheet must load once")
    if page == "joseph-smith-likeness.html":
        navs = [n for n in nodes if n.tag == "nav" and n.has("likeness-path")]
        links = [n for nav in navs for n in nav.walk() if n.tag == "a"]
        require(len(navs) == 1 and len(links) == 6, "Joseph: six directory pills required")
        ids = {n.attrs.get("id") for n in nodes}
        require(all(n.has("fc-button") and n.attrs.get("href", "").startswith("#") and n.attrs["href"][1:] in ids for n in links),
                "Joseph: directory pills must use shared buttons and existing section targets")
        require(len({n.attrs.get("href") for n in links}) == 6, "Joseph: directory destinations must be unique")

if ERRORS:
    raise SystemExit("\n".join(ERRORS))
print("STUDY LAYOUT QA PASS: five shared rails, Joseph spacing and six centered study pills; rendered geometry requires browser review")
