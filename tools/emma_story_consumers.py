"""Five explicit reading-first Emma additions; historical contracts stay separate."""
import hashlib
import re

EMMA_STORY_ROUTES = frozenset({
    'history/emma-elect-lady.html', 'history/emma-hymns.html',
    'history/emma-winter-crossing.html', 'history/emma-relief-society.html',
    'history/emma-last-testimony.html',
})
SYSTEM_REF = '../site-system.css?v=20261005-mobile-study-rows-1'
STORY_REF = '../history-stories.css?v=20261009-directory-alignment-1'
COMMON_REF = '../site-common.js?v=20261021-continue-motion-1'
VIEWER_REFS = [
    ['link', {'rel': 'stylesheet', 'href': '../full-image-viewer.css?v=20260922-viewer-3'}],
    ['script', {'src': '../full-image-viewer.js?v=20260919-viewer-1', 'defer': None}],
]
SCRIPT_REFS = [COMMON_REF, '../full-image-viewer.js?v=20260919-viewer-1',
               '../topic-artwork-details.js?v=20261021-continue-motion-1',
               '../site-search.js?v=20260919-focused-answers-1']
# Canonical header bytes, with read_text universal-newline normalization only.
HEADER_SHA256 = '0863a44ae3f830782f22a9c60419538da91ac4421bc30f34b2cb149b1653b501'


def historical_consumers(consumers, expected_new):
    """Require every exact new entry, return all other entries for old validation.

    Unknown owners are deliberately NOT removed; the old set/digest rejects them.
    """
    if not isinstance(consumers, dict):
        return None
    if any(consumers.get(route) != expected_new for route in EMMA_STORY_ROUTES):
        return None
    return {k: v for k, v in consumers.items() if k not in EMMA_STORY_ROUTES}


def reviewed_wrap_additions(consumers, expected, version, historical_check):
    if version != SYSTEM_REF.split('?v=')[1]:
        return False
    historical = historical_consumers(consumers, [SYSTEM_REF])
    return historical is not None and historical_check(historical, expected, version)


def reviewed_viewer_additions(bindings, historical_check):
    historical = historical_consumers(bindings, VIEWER_REFS)
    return historical is not None and historical_check(historical)


def historical_routes(pages):
    assert len(pages) == len(set(pages)), 'Duplicate canonical route'
    assert EMMA_STORY_ROUTES <= set(pages), 'Missing exact Emma story owner'
    return set(pages) - EMMA_STORY_ROUTES


def assert_story_opening(route, text, doc):
    assert route in EMMA_STORY_ROUTES, 'Unknown Emma story owner'
    headers = re.findall(r'<nav\b[^>]*data-focuschrist-header="standard"[^>]*>.*?</nav>', text, re.S)
    assert len(headers) == 1 and hashlib.sha256(headers[0].encode()).hexdigest() == HEADER_SHA256, route + ': canonical header drift'
    assert doc.body and set(doc.body.get('class', [])) == {'fc-site', 'fc-life-story', 'fc-emma-study'}, route + ': story body drift'
    assert not doc.select('.fc-visual-hero,[data-covenant-hero-slot],.cfm-desktop-picture,.gc-intro-visual'), route + ': reading-first opening must not invent hero'
    assert len(doc.select('main .fc-life-opening')) == 1 and doc.select_one('main .fc-life-opening h1') and doc.select_one('main .fc-life-opening .fc-page-intro-copy'), route + ': reading-first introduction missing'
    assert len(doc.select('main figure.fc-study-visual.fc-life-picture[data-exclusive-artwork][data-topic-art]')) == 1, route + ': body artwork missing'
    assert doc.select_one('main #reflect') and doc.select_one('main #sources') and doc.select_one('main #more-stories'), route + ': story structure missing'
    assert [s.get('src') for s in doc.select('script[src]')] == SCRIPT_REFS, route + ': exact script order/binding drift'
