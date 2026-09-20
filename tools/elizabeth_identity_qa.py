"""Elizabeth replacement provenance/routing gate; pixel likeness needs human review."""
from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = '1861d3e4aa908dc56e0840328bbacbc62c5944b3'
IDS = {'07-elizabeth-family', '09-elizabeth-fuel', '10-cave-gift', '11-sharing-meat'}
REFERENCE = 'assets/identities/elizabeth-crook-panting-owner-approved-20260920.png'
REFERENCE_SHA = 'b791eff6c39b3a8007eb04a4498f9021878f251514ee93f1d142aaaac65c5c7e'

def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

assert sha(REFERENCE) == REFERENCE_SHA, 'Approved identity bytes changed'
review = json.loads((ROOT / 'docs/elizabeth-likeness-review-20260920.json').read_text(encoding='utf-8'))
replacements = review['replacements']
assert len(replacements) == 4 and {r['id'] for r in replacements} == IDS
story = json.loads((ROOT / 'docs/pioneer-story-review.json').read_text(encoding='utf-8'))
records = {r['id']: r for r in story['images']}
public_files = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts
                and p.suffix in {'.html', '.js', '.css', '.json'}
                and not any(x in p.relative_to(ROOT).parts for x in ('docs', 'tools', 'node_modules'))]
public = '\n'.join(p.read_text(encoding='utf-8') for p in public_files)
for r in replacements:
    key = r['id']
    old = f'assets/pioneers/story/{key}-full.webp'
    full = f'assets/pioneers/story/{key}-approved-20260920-full.webp'
    preview = f'assets/pioneers/story/{key}-approved-20260920-800.webp'
    assert (r['old_asset'], r['asset'], r['preview']) == (old, full, preview), key
    assert r['identity_reference'] == REFERENCE and r['reference_sha256'] == REFERENCE_SHA, key
    assert r['technical_review'], key
    old_bytes = subprocess.check_output(['git', 'show', BASE + ':' + old], cwd=ROOT)
    assert hashlib.sha256(old_bytes).hexdigest() == r['old_sha256'], key
    assert sha(full) == r['newsha'] and sha(full) != r['old_sha256'], key
    assert sha(preview) == r['preview_sha256'], key
    assert Image.open(ROOT / full).size == (1536, 1024), key
    assert Image.open(ROOT / preview).size == (800, 533), key
    record = records[key]
    assert record['asset'] == full and record['preview'] == preview, key
    assert sha(full) == record['sha256'] and sha(preview) == record['preview_sha256'], key
    assert record['owner_identity_locked'] and record['identity_reference'] == REFERENCE, key
    assert old not in public and old.replace('-full.webp', '-800.webp') not in public, key
    for consumer in ('pioneers.html', 'art-gallery.json', 'site-search-index.json'):
        text = (ROOT / consumer).read_text(encoding='utf-8')
        assert full in text or preview in text, (key, consumer)

# A dated replacement does not authorize editing any preexisting Pioneer bytes.
assets = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
                                 'assets/pioneers', 'assets/heroes/pioneers.webp'], cwd=ROOT).decode().splitlines()
for asset in assets:
    before = subprocess.check_output(['git', 'show', BASE + ':' + asset], cwd=ROOT)
    assert (ROOT / asset).read_bytes() == before, 'Unscoped image mutation: ' + asset
print(f'Elizabeth QA PASS: four replacements, exact approved reference, current public paths, {len(assets)} preserved assets. Visual likeness remains a separate review.')
