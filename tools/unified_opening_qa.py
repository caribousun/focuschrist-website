"""Canonical coverage and asset-version contract; visual approval remains separate."""
import json
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'docs/unified-opening-inventory.json').read_text(encoding='utf8'))
pages = [urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(ROOT / 'sitemap.xml').findall('{*}url/{*}loc')]
assert len(pages) == len(set(pages)) == 129
assert set(pages) == {p['path'] for p in inventory['pages']}
assert inventory['hero_count'] == 47 and inventory['excluded_count'] == 82
for record in inventory['pages']:
    doc = BeautifulSoup((ROOT / record['path']).read_text(encoding='utf8'), 'html.parser')
    actual = bool(doc.select_one('.fc-visual-hero,[data-covenant-hero-slot],.cfm-desktop-picture,.gc-intro-visual'))
    assert actual == record['hero'], record['path'] + ': opening hero inventory drift'
    common = [s['src'] for s in doc.select('script[src]') if 'site-common.js' in s['src']]
    assert len(common) == 1 and common[0].endswith('site-common.js?v=20261002-timeline-1'), record['path']
common = (ROOT / 'site-common.js').read_text(encoding='utf8')
assert common.count("relativeAssetHref('unified-opening.css?v=20260930-alignment-2')") == 1
assert common.count("relativeAssetHref('unified-opening.js?v=20260930-1')") == 1
script = (ROOT / 'unified-opening.js').read_text(encoding='utf8')
assert '\\u2193' in script and 'Ãƒ' not in script, 'Continue arrow encoding'
assert "opening.matches('.jj-opening') ? []" in script, 'Covenant invitation must remain in opening'
assert 'getBoundingClientRect().bottom + scrollY' in script, 'Fit must use document coordinates'
print('UNIFIED OPENING STATIC PASS: 129 canonical routes, 47 illustrated openings, 82 explicit exclusions, current shared versions and protected Covenant invitation')
