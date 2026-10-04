"""Exact scoped geometry contract; rendered equality is a separate Chromium gate."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT/'docs/hero-home-height-audit-20260929.json').read_text(encoding='utf-8'))
assert len(audit['pages']) == len({r['page'] for r in audit['pages']}) == 125
assert sum(r['desktop_repair'] for r in audit['pages']) == 23
data = (ROOT/'topic-study-pages.css').read_bytes()
prefix = audit['topic_preserved_prefix']
assert hashlib.sha256(data[:prefix['bytes']]).hexdigest() == prefix['sha256'], 'Approved mobile/base rules changed'
appendix = data[prefix['bytes']:].decode()
assert appendix.count('@media') == 1 and '@media(min-width:701px)' in appendix
assert 'aspect-ratio:2048/684' in appendix and 'min-height:0;grid-template-rows:auto auto' in appendix
cfm = (ROOT/'come-follow-me.css').read_bytes()
cfm_prefix = audit['cfm_preserved_prefix']
assert hashlib.sha256(cfm[:cfm_prefix['bytes']]).hexdigest() == cfm_prefix['sha256'], 'Existing CFM phone/base rules changed'
for r in audit['pages']:
    text = (ROOT/r['page']).read_text(encoding='utf-8')
    for asset in ['topic-study-pages.css', 'desktop-hero-repairs.css', 'desktop-hero-repairs.js']:
        if asset+'?' in text:
            assert asset+'?v=20260929-home-height-1' in text, (r['page'], asset, 'stale cache key')
    if r['page'].startswith('answers/jesus-christ/'):
        assert r['selector'] is None, 'Body pictures are not newly invented heroes'
print('PASS:125 route classifications,23 desktop corrections, preserved mobile/base bytes and current cache keys')

# Each new canvas is a rendition of its owning original, never a replacement study image.
from PIL import Image
proof = json.loads((ROOT/'docs/hero-extension-pixel-proof-20260929.json').read_text(encoding='utf-8'))
assert {'shepherd','joseph-portrait'} <= {r['key'] for r in proof}
assert len({r['key'] for r in proof}) == len(proof)
for r in proof:
    original = Image.open(ROOT/r['source']).convert('RGB')
    crop_top = r.get('source_crop_top', 0)
    if crop_top:
        assert r['key'] == 'shepherd' and crop_top == 110, 'Unreviewed source cropping'
        original = original.crop((0, crop_top, original.width, original.height))
    rendition = Image.open(ROOT/r['asset']).convert('RGB')
    assert list(rendition.size) == r['size']
    assert hashlib.sha256(original.tobytes()).hexdigest() == r['source_decoded_sha256']
    assert rendition.crop(tuple(r['center_box'])).tobytes() == original.tobytes(), r['key']+': original pixels changed'
    assert hashlib.sha256((ROOT/r['asset']).read_bytes()).hexdigest() == r['asset_sha256']
print(f'PASS:{len(proof)} reviewed extension centers remain decoded-pixel identical')

variants=json.loads((ROOT/'docs/hero-responsive-variant-review-20260929.json').read_text(encoding='utf-8'))
assert {'birth','covenant-phone','be-still','tanner','children-phone'} <= {r['key'] for r in variants}
for r in variants:
    assert r['classification'] == 'visually reviewed responsive variant; not decoded-pixel identical'
    assert hashlib.sha256((ROOT/r['asset']).read_bytes()).hexdigest() == r['asset_sha256'], r['key']+': unreviewed variant bytes'
    assert list(Image.open(ROOT/r['asset']).size) == r['size']
print(f'PASS:{len(variants)} visual-continuity variants match reviewed hashes; no pixel-identity claim')

replacement=json.loads((ROOT/'docs/children-artwork-replacement-20260929.json').read_text(encoding='utf-8'))
assert replacement['original_count_delta'] == 0
assert (ROOT/replacement['replaced_original']).is_file(), 'Archival original removed'
assert hashlib.sha256((ROOT/replacement['current_original']).read_bytes()).hexdigest() == replacement['current_sha256']
for page in ['art.html','art-study/suffer-the-little-children.html']:
    markup=(ROOT/page).read_text(encoding='utf-8')
    assert replacement['current_original'] in markup
    assert replacement['replaced_original'] not in markup, page+': superseded original still active'
print('PASS:Children original replacement retains one owner/gallery slot and archival source')
