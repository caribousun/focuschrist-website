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
assert '--fc-mobile-hero-height: clamp(180px, 42svh, 360px)' in css
assert '--fc-mobile-hero-height: clamp(320px, 115vw, 800px)' in css
assert 'fc-mobile-hero-surround' not in css
assert 'fc-mobile-hero-surround' not in (ROOT / 'site-common.js').read_text(encoding='utf-8')
# The first-screen correction must never reintroduce containment/side treatments.
mobile_opening_css = css[css.index('/* A single mobile image budget'):]
original_css = css[:css.index('/* A single mobile image budget')].rstrip()
assert hashlib.sha256(original_css.encode()).hexdigest() == '84bb60d6413028bb5517b9dcd5c3cb7f897c990043eb91c53ce77003af3e3d17', 'Original study-page CSS must remain unchanged'
assert 'body.fc-site.fc-main-opening { --fc-mobile-hero-height:' in mobile_opening_css
main_pages = {'index.html','ask.html','answers.html','art.html','missionary.html','church-history.html','pioneers.html','about.html','watch.html','atonement.html'}
marked_pages = {str(p.relative_to(ROOT)).replace('\\', '/') for p in ROOT.rglob('*.html') if '<body class="fc-main-opening ' in p.read_text(encoding='utf-8')}
assert marked_pages == main_pages, 'Compact redesign is limited to the ten top-navigation pages'
assert 'background-size: contain' not in mobile_opening_css
assert 'object-fit: contain' not in mobile_opening_css
print('Mobile scene QA PASS: seven reviewed portraits, original bytes/full-size links and desktop fallbacks retained.')
