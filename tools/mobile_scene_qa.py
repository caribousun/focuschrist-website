"""Protect reviewed mobile renditions and their unchanged full-size originals."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
record = json.loads((ROOT / 'docs/mobile-scene-review-20260920.json').read_text(encoding='utf-8'))
css = (ROOT / 'site-system.css').read_text(encoding='utf-8')
assert {v['page'] for v in record['variants']} == {'ask', 'watch', 'answers', 'missionary', 'bom', 'about', 'art'}
for variant in record['variants']:
    page = 'book-of-mormon-evidences.html' if variant['page'] == 'bom' else variant['page'] + '.html'
    html = (ROOT / page).read_text(encoding='utf-8')
    for field in ('original', 'mobile'):
        asset = ROOT / variant[field]
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == variant[field + '_sha256'], asset
    width, height = Image.open(ROOT / variant['mobile']).size
    assert width >= 1000 and 0.79 < width / height < 0.81, variant['mobile']
    assert variant['mobile'] in css + html, 'Mobile source disconnected: ' + page
    assert 'href="' + variant['original'] in html, 'Original full-size path lost: ' + page
    if variant['page'] in ('missionary', 'bom'):
        assert '<source media="(max-width:700px)" srcset="' + variant['mobile'] in html
        assert '<img src="' + variant['original'] in html, 'Desktop fallback lost: ' + page
assert '--fc-mobile-hero-height: clamp(320px, 115vw, 800px)' in css
print('Mobile scene QA PASS: seven reviewed portraits, original bytes/full-size links and desktop fallbacks retained.')
