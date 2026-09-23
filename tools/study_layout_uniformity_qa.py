"""Guard shared study rails and Joseph navigation; browser geometry is separate."""
import re
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, urljoin, parse_qs
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


JOURNEY_VERSION = '20260923-standard-formatting-1'


def journey_errors(css, consumers, expected):
    """Inspect actual stylesheet rules and saved consumers, independently of builders."""
    errors = []
    clean = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    blocks = re.findall(r'([^{}]+)\{([^{}]*)\}', clean)
    for selector in ('.jj-reading', '.jj-opening .lede'):
        rules = []
        for selectors, body in blocks:
            if any(selector in s.strip() for s in selectors.split(',')):
                rules.append(dict((k.strip(), compact(v)) for k, v in
                                  re.findall(r'([\w-]+)\s*:\s*([^;]+)', body)))
        for prop, value in {'width': '100%', 'max-width': 'none', 'min-width': '0'}.items():
            values = [rule[prop] for rule in rules if prop in rule]
            if not values or any(v != value for v in values):
                errors.append(selector + ' must retain ' + prop + ': ' + value)
    heading_wraps = [compact(value) for selectors, body in blocks
                     if '.jj-opening h1' in [s.strip() for s in selectors.split(',')]
                     for value in re.findall(r'overflow-wrap\s*:\s*([^;]+)', body)]
    if not heading_wraps or any(value != 'anywhere' for value in heading_wraps):
        errors.append('.jj-opening h1 must retain overflow-wrap: anywhere for enlarged text')
    legacy_wraps = [compact(value) for selectors, body in blocks
                    if '.content-wrap.article>h2' in [compact(s) for s in selectors.split(',')]
                    for value in re.findall(r'overflow-wrap\s*:\s*([^;]+)', body)]
    if not legacy_wraps or any(value != 'anywhere' for value in legacy_wraps):
        errors.append('.content-wrap.article>h2 must retain overflow-wrap: anywhere for enlarged text')
    if set(consumers) != set(expected):
        errors.append('Journey CSS consumers must exactly match the canonical journey and Birth inventory')
    for page, hrefs in consumers.items():
        if len(hrefs) != 1 or any(parse_qs(urlsplit(href).query).get('v') != [JOURNEY_VERSION] for href in hrefs):
            errors.append(page + ': journey stylesheet must load once with current version ' + JOURNEY_VERSION)
    return errors


def journey_fixture_tests():
    css = '.jj-reading,.jj-opening .lede{width:100%;max-width:none;min-width:0}.jj-opening h1{overflow-wrap:anywhere}.content-wrap.article>h2{overflow-wrap:anywhere}'
    consumers = {'example.html': ['jesus-journey.css?v=' + JOURNEY_VERSION]}
    assert not journey_errors(css, consumers, {'example.html'})
    for bad in ('780px', '760px'):
        assert journey_errors(css.replace('max-width:none', 'max-width:' + bad), consumers, {'example.html'})
    assert journey_errors(css + '@media(min-width:900px){body .jj-reading{max-width:780px}}', consumers, {'example.html'})
    assert journey_errors(css, {'example.html': ['jesus-journey.css?v=old']}, {'example.html'})
    assert journey_errors(css, {}, {'example.html'})
    assert journey_errors(css, dict(consumers, **{'unexpected.html': consumers['example.html']}), {'example.html'})
    assert journey_errors(css, {'example.html': consumers['example.html'] * 2}, {'example.html'})
    assert journey_errors(css.replace('.jj-opening h1{overflow-wrap:anywhere}', ''), consumers, {'example.html'})
    assert journey_errors(css.replace('.content-wrap.article>h2{overflow-wrap:anywhere}', ''), consumers, {'example.html'})


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

contract('jesus-journey.css', 'body.fc-jesus-journey .jj-wrap', {
    'width': 'min(var(--fc-standard,1040px),calc(100% - 2 * var(--fc-body-gutter,18px)))',
    'margin-inline': 'auto',
})
journey_expected = {'birth-of-christ.html', 'answers/jesus-christ-latter-day-saint-beliefs.html'}
for filename in ('branch-content-reviewed.json', 'parable-content-reviewed.json', 'parable-collections-reviewed.json'):
    journey_expected.update(page['url'].lstrip('/') for page in json.loads(
        (ROOT / 'docs/jesus-journey' / filename).read_text(encoding='utf-8')))
require(len(journey_expected) == 78, 'Expected all 78 journey stylesheet consumers')
journey_consumers = {}
for path in ROOT.rglob('*.html'):
    if any(part in {'.git', 'node_modules'} for part in path.relative_to(ROOT).parts):
        continue
    page = path.relative_to(ROOT).as_posix()
    doc = Document()
    doc.feed(path.read_text(encoding='utf-8'))
    hrefs = [n.attrs.get('href', '') for n in doc.root.walk() if n.tag == 'link'
             and urlsplit(urljoin('/' + page, n.attrs.get('href', ''))).path == '/jesus-journey.css']
    if hrefs:
        journey_consumers[page] = hrefs
        rail = 'jj-wrap' if page.startswith('jesus-christ/') else 'content-wrap'
        require(any(n.tag == 'main' and n.has(rail) for n in doc.root.walk()), page + ': standard journey content rail missing')
ERRORS.extend(journey_errors((ROOT / 'jesus-journey.css').read_text(encoding='utf-8'), journey_consumers, journey_expected))
if '--self-test' in sys.argv:
    journey_fixture_tests()
    print('Journey formatting fixtures passed: full-width valid, caps/override/stale/missing/extra/duplicate/missing-h1-wrap/missing-h2-wrap rejected')

if ERRORS:
    raise SystemExit("\n".join(ERRORS))
print("STUDY LAYOUT QA PASS: five shared rails, Joseph spacing and six centered study pills; all 78 journey consumers use full-width reading and current CSS; rendered geometry requires browser review")
