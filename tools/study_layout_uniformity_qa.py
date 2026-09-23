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
PAGE_BOUNDARY_VERSIONS = {'church-history.css': '20260923-page-borders-1',
                          'missionary.css': '20260923-purpose-flow-1'}


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


def media_body(css, query):
    """Collect exact breakpoint blocks while retaining their nested rules."""
    results = []
    for match in re.finditer(r'@media\s*([^{}]+)\{', css):
        if compact(match.group(1)) != compact(query):
            continue
        start, depth, end = match.end(), 1, match.end()
        while end < len(css) and depth:
            depth += (css[end] == '{') - (css[end] == '}')
            end += 1
        results.append(css[start:end - 1])
    return '\n'.join(results)


def boundary_errors(mission, history, pioneer, css):
    errors = []
    def nodes(text):
        doc = Document()
        doc.feed(text)
        return list(doc.root.walk())
    mission_nodes = nodes(mission)
    for section_class in ('fc-missionary-purpose', 'fc-missionary-world'):
        sections = [n for n in mission_nodes if n.has(section_class)]
        if len(sections) != 1 or not any(n.has('fc-container--standard') for n in sections[0].children):
            errors.append('Mission body section must retain standard rail: ' + section_class)
        if any(n.has('fc-container--wide') for section in sections for n in section.walk()):
            errors.append('Mission body must not return to 1240px wide rail: ' + section_class)
    figures = [n for n in nodes(history) if n.tag == 'figure' and n.has('fc-history-art-panel')]
    if len(figures) != 7 or any(n.has('fc-history-art-panel--offset-left') or n.has('fc-history-art-panel--offset-right') for n in figures):
        errors.append('History must retain seven artwork panels, including the four corrected figures, without offset modifiers')
    links = [n.attrs.get('href', '') for n in nodes(pioneer) if n.tag == 'link'
             and urlsplit(n.attrs.get('href', '')).path == 'pioneer-story.css']
    if len(links) != 1 or parse_qs(urlsplit(links[0]).query).get('v') != ['20260923-page-borders-1']:
        errors.append('Pioneer boundary stylesheet version must be current and unique')
    clean = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    def rule(query, selector, expected):
        rules = re.findall(r'([^{}]+)\{([^{}]*)\}', media_body(clean, query))
        actual = {}
        for selectors, body in rules:
            if compact(selector) in [compact(s) for s in selectors.split(',')]:
                actual.update((k, compact(v)) for k, v in re.findall(r'([\w-]+)\s*:\s*([^;]+)', body))
        for prop, value in expected.items():
            if actual.get(prop) != compact(value):
                errors.append('Pioneer ' + query + ' ' + selector + ' must retain ' + prop + ': ' + value)
    phone = '(max-width:700px)'
    rule(phone, 'body.fc-site main>.qa-section', {'padding-inline': '0'})
    rail = {'width': 'min(var(--fc-standard,1040px),calc(100% - 2 * var(--fc-body-gutter,24px)))',
            'max-width': 'var(--fc-standard,1040px)', 'margin-inline': 'auto'}
    for selector in ('body.fc-site main>.qa-section>.qa-container', 'body.fc-site main>.section'):
        rule(phone, selector, rail)
    tablet = '(min-width:701px) and (max-width:1040px)'
    card = 'body.fc-site .pioneer-art-grid--three>.pioneer-art-card:last-child'
    rule(tablet, card, {'width': '100%', 'display': 'grid', 'grid-template-columns': 'repeat(2,minmax(0,1fr))', 'align-items': 'center'})
    rule(tablet, card + '>a', {'min-width': '0'})
    return errors


def boundary_fixture_tests(mission, history, pioneer, css):
    assert not boundary_errors(mission, history, pioneer, css)
    assert boundary_errors(mission.replace('fc-container--standard fc-missionary-split', 'fc-container--wide fc-missionary-split'), history, pioneer, css)
    assert boundary_errors(mission, history.replace('<figure class="fc-history-art-panel', '<figure class="fc-history-art-panel fc-history-art-panel--offset-left', 1), pioneer, css)
    assert boundary_errors(mission, history, pioneer, css.replace('var(--fc-body-gutter, 24px)', 'var(--fc-body-gutter, 14px)'))
    assert boundary_errors(mission, history, pioneer, css.replace('width: 100%;\n        display: grid;', 'width: 560px;\n        display: grid;'))
    assert boundary_errors(mission, history, pioneer.replace('20260923-page-borders-1', 'stale'), css)


def page_wrap_errors(html, css, stylesheet, selector):
    errors = []
    doc = Document()
    doc.feed(html)
    links = [n.attrs.get('href', '') for n in doc.root.walk() if n.tag == 'link'
             and urlsplit(n.attrs.get('href', '')).path == stylesheet]
    if len(links) != 1 or parse_qs(urlsplit(links[0]).query).get('v') != [PAGE_BOUNDARY_VERSIONS[stylesheet]]:
        errors.append(stylesheet + ': page boundary version must be current and unique')
    clean = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    wraps = [compact(value) for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', clean)
             if compact(selector) in [compact(s) for s in selectors.split(',')]
             for value in re.findall(r'overflow-wrap\s*:\s*([^;]+)', body)]
    if not wraps or any(value != 'anywhere' for value in wraps):
        errors.append(stylesheet + ': ' + selector + ' must retain overflow-wrap: anywhere')
    return errors


def page_wrap_fixture_tests():
    for stylesheet, selector in (('church-history.css', '.fc-history-page main'),
                                 ('missionary.css', '.fc-missionary-page main')):
        version = PAGE_BOUNDARY_VERSIONS[stylesheet]
        html = '<link rel="stylesheet" href="' + stylesheet + '?v=' + version + '">'
        css = selector + '{overflow-wrap:anywhere}'
        assert not page_wrap_errors(html, css, stylesheet, selector)
        assert page_wrap_errors(html, '', stylesheet, selector)
        assert page_wrap_errors(html.replace(version, 'stale'), css, stylesheet, selector)


def mission_purpose_errors(html, css):
    """Keep the panorama above its teaching and retain the full mobile scene."""
    errors = []
    doc = Document()
    doc.feed(html)
    splits = [n for n in doc.root.walk() if n.has('fc-missionary-split')]
    if len(splits) != 1 or [n.tag for n in splits[0].children] != ['figure', 'div']:
        errors.append('Mission purpose must retain picture followed by teaching')
    elif not splits[0].children[0].has('fc-missionary-visual--purpose') or not splits[0].children[1].has('fc-missionary-copy'):
        errors.append('Mission purpose picture and teaching order changed')
    clean = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    rules = [(selectors, dict((k, compact(v)) for k, v in re.findall(r'([\w-]+)\s*:\s*([^;]+)', body)))
             for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', clean)]
    split_rules = [r for s, r in rules if '.fc-missionary-split' in [x.strip() for x in s.split(',')]]
    columns = [r['grid-template-columns'] for r in split_rules if 'grid-template-columns' in r]
    if not columns or any(v not in ('minmax(0,1fr)', '1fr') for v in columns):
        errors.append('Mission purpose must remain a single full-width column at every breakpoint')
    captions = [r for s, r in rules if compact('.fc-missionary-purpose .fc-missionary-visual figcaption') in [compact(x) for x in s.split(',')]]
    if not captions or any(r.get('position') != 'static' for r in captions):
        errors.append('Mission purpose caption must remain outside the artwork')
    for selectors, rule in rules:
        if '.fc-missionary-visual--purpose img' in selectors and (
                rule.get('object-fit') == 'cover' or rule.get('min-height', '0') != '0' or rule.get('height', 'auto') != 'auto'):
            errors.append('Mission purpose panorama must not be cropped or stretched on phones')
    return errors


def mission_purpose_fixture_tests(html, css):
    assert not mission_purpose_errors(html, css)
    assert mission_purpose_errors(html, css.replace('grid-template-columns: minmax(0, 1fr);', 'grid-template-columns: 2fr 1fr;', 1))
    assert mission_purpose_errors(html, css + '@media(min-width:900px){.fc-missionary-split{grid-template-columns:2fr 1fr}}')
    assert mission_purpose_errors(html, css.replace('.fc-missionary-purpose .fc-missionary-visual figcaption', '.removed-caption'))
    assert mission_purpose_errors(html, css + '@media(max-width:700px){.fc-missionary-visual--purpose img{min-height:270px;object-fit:cover}}')
    assert mission_purpose_errors(html.replace('fc-missionary-visual--purpose', 'missing-purpose-figure'), css)


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
boundary_inputs = [(ROOT / name).read_text(encoding='utf-8') for name in
                   ('missionary.html', 'church-history.html', 'pioneers.html', 'pioneer-story.css')]
ERRORS.extend(boundary_errors(*boundary_inputs))
mission_purpose_inputs = (boundary_inputs[0], (ROOT / 'missionary.css').read_text(encoding='utf-8'))
ERRORS.extend(mission_purpose_errors(*mission_purpose_inputs))
for page, stylesheet, selector in (
        ('church-history.html', 'church-history.css', '.fc-history-page main'),
        ('missionary.html', 'missionary.css', '.fc-missionary-page main')):
    ERRORS.extend(page_wrap_errors((ROOT / page).read_text(encoding='utf-8'),
                                  (ROOT / stylesheet).read_text(encoding='utf-8'), stylesheet, selector))
if '--self-test' in sys.argv:
    journey_fixture_tests()
    print('Journey formatting fixtures passed: full-width valid, caps/override/stale/missing/extra/duplicate/missing-h1-wrap/missing-h2-wrap rejected')
    boundary_fixture_tests(*boundary_inputs)
    print('Boundary fixtures passed: valid, Mission wide rail, History offsets, Pioneer narrow gutter, 560px last card and stale CSS')
    page_wrap_fixture_tests()
    print('Page wrap fixtures passed: History and Mission valid, missing wrap and stale version rejected')
    mission_purpose_fixture_tests(*mission_purpose_inputs)
    print('Mission purpose fixtures passed: full-width picture then teaching; narrow columns, later overrides, missing caption flow, phone crop and missing picture rejected')

if ERRORS:
    raise SystemExit("\n".join(ERRORS))
print("STUDY LAYOUT QA PASS: five shared rails, Joseph spacing and six centered study pills; all 78 journey consumers use full-width reading and current CSS; rendered geometry requires browser review")
