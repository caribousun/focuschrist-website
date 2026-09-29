"""Protect approved original pixels inside the owner-authorized wide renditions."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'docs/desktop-hero-pixel-proof-20260929.json').read_text())
assert {r['key'] for r in records} == {'plan', 'bom', 'conference', 'abrahamic'}
for record in records:
    with Image.open(ROOT / record['source']) as image:
        original = image.convert('RGB')
    with Image.open(ROOT / record['asset']) as image:
        wide = image.convert('RGB')
    assert wide.width == wide.height * 3, record['key'] + ': desktop ratio'
    assert hashlib.sha256(original.tobytes()).hexdigest() == record['source_decoded_sha256']
    assert wide.crop(tuple(record['center_box'])).tobytes() == original.tobytes(), record['key'] + ': original pixels changed'
print('PASS: four full original rectangles remain pixel-identical in lossless 3:1 desktop renditions.')
