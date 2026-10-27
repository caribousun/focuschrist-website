"""Canonical coverage and asset-version contract; visual approval remains separate."""
import json
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from hero_introductions_qa import ROUTES as INTRODUCTION_ROUTES
from section_panel_surface_qa import STANDALONE_ROUTE, assert_standalone

from emma_story_consumers import EMMA_STORY_ROUTES, COMMON_REF, historical_routes, assert_story_opening
from owner_integration_contract import CHART as ADAMS_ROUTE, without_integrated_adams_routes as without_adams_route
ROOT = Path(__file__).resolve().parents[1]
HERO_ROUTES = frozenset(p['path'] for p in json.loads((ROOT / 'docs/unified-opening-inventory.json').read_text())['pages'] if p['hero'])


def assert_common_version(route, doc):
    from continue_motion_binding import mapping
    common = [s['src'] for s in doc.select('script[src]') if 'site-common.js' in s['src']]
    version = {
        'church-history.html': '20261010-emma-identity-links-1',
        'answers/who-was-joseph-smith.html': '20261010-final-art-links-1',
        'art-gallery.html': '20261010-emma-identity-links-1',
        'book-of-mormon-evidences.html': '20261010-emma-identity-links-1',
    }.get(route, '20261008-section-top-2')
    prefix = '/' if route.startswith('jesus-christ/') else '../' * route.count('/')
    if route in mapping()['files']:version='20261021-continue-motion-1'
    expected = COMMON_REF if route in EMMA_STORY_ROUTES else prefix + 'site-common.js?v=' + version
    assert common == [expected], route + ': exact shared-script binding required'


inventory = json.loads((ROOT / 'docs/unified-opening-inventory.json').read_text(encoding='utf8'))
pages = [urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(ROOT / 'sitemap.xml').findall('{*}url/{*}loc')]
historical_pages = historical_routes(without_adams_route(pages, (ROOT / ADAMS_ROUTE).read_bytes()))
assert len(historical_pages) == 132
assert len(inventory['pages']) == len({p['path'] for p in inventory['pages']}) == 130
assert historical_pages == {p['path'] for p in inventory['pages']} | {'history/emma-hale-smith.html', STANDALONE_ROUTE}
assert sum(bool(p['hero']) for p in inventory['pages']) == inventory['hero_count']
assert sum(not p['hero'] for p in inventory['pages']) == inventory['excluded_count']
assert inventory['hero_count'] == 51 and inventory['excluded_count'] == 79
assert next(p for p in inventory['pages'] if p['path'] == 'joseph-smith-portrait-research.html')['hero'] is True, 'Research requires its distinct reviewed hero'
assert next(p for p in inventory['pages'] if p['path'] == 'joseph-smith-likeness.html')['hero'] is True, 'Joseph gateway requires its distinct reviewed hero'
# Preserve the original130-record inventory; Emma is the separately accepted addition.
for record in [*inventory['pages'], {'path': 'history/emma-hale-smith.html', 'hero': True}]:
    doc = BeautifulSoup((ROOT / record['path']).read_text(encoding='utf8'), 'html.parser')
    actual = bool(doc.select_one('.fc-visual-hero,[data-covenant-hero-slot],.cfm-desktop-picture,.gc-intro-visual'))
    assert actual == record['hero'], record['path'] + ': opening hero inventory drift'
    assert_common_version(record['path'], doc)
# Five reading-first additions do not alter the historical 51/79 inventory.
for route in sorted(EMMA_STORY_ROUTES):
    text = (ROOT / route).read_text(encoding='utf8')
    doc = BeautifulSoup(text, 'html.parser')
    assert_story_opening(route, text, doc)
    assert_common_version(route, doc)
# The separately reviewed standalone opening embeds its own header controller.
assert_standalone(STANDALONE_ROUTE, (ROOT / STANDALONE_ROUTE).read_bytes())
standalone_doc = BeautifulSoup((ROOT / STANDALONE_ROUTE).read_text(encoding='utf8'), 'html.parser')
assert standalone_doc.select_one('section.topsec#top img[alt]'), 'Standalone illustrated opening missing'
assert [x.get('src') for x in standalone_doc.select('script[src]')] == ['/site-search.js?v=20260919-focused-answers-1','/header-scroll.js?v=20261021-continue-motion-1']
common = (ROOT / 'site-common.js').read_text(encoding='utf8')
assert common.count("relativeAssetHref('unified-opening.css?v=20261006-balanced-opening-1')") == 1
assert common.count("relativeAssetHref('unified-opening.js?v=20261006-introductions-1')") == 1
script = (ROOT / 'unified-opening.js').read_text(encoding='utf8')
assert '\\u2193' in script and 'Ãƒ' not in script, 'Continue arrow encoding'
assert "opening.matches('.jj-opening') ? []" in script, 'Covenant invitation must remain in opening'
assert 'getBoundingClientRect().bottom + scrollY' in script, 'Fit must use document coordinates'
print('UNIFIED OPENING STATIC PASS: 132 historical routes, 53 historical illustrated openings, 79 historical exclusions; 5 additional reading-first Emma stories and 2 source-validated integrated Adams pages, current shared versions and protected Covenant invitation')
