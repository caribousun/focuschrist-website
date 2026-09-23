"""Verify durable artwork files without implying full project completion."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from build_jesus_journey import validate_artwork_review

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/jesus-journey'
registry = json.loads((DATA / 'artworks.json').read_text(encoding='utf-8'))
ready = {k:v for k,v in registry.items() if v.get('reviewed') and v.get('asset')}
errors = []
for key, item in ready.items():
    try:
        validate_artwork_review(key, item)
    except ValueError as error:
        errors.append(str(error))
    for name, path, field in [
        ('original', ROOT.parent / 'originals' / item['original'], 'original_sha256'),
        ('full', ROOT / item['asset'], 'asset_sha256'),
        ('thumbnail', ROOT / item['thumbnail'], 'thumbnail_sha256')]:
        if not path.is_file():
            errors.append(f'{key}: missing {name}')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item[field]:
            errors.append(f'{key}: changed {name}')
report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
          'planned': len(registry), 'reviewed_prepared': len(ready),
          'checked_files': len(ready)*3, 'errors': errors,
          'nested_pages': len(list((ROOT/'jesus-christ').rglob('*.html'))),
          'remaining_keys': sorted(set(registry)-set(ready)),
          'published': False,
          'scope': 'Local recovery and accepted-file integrity only, not release approval.'}
(DATA/'recovery-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(f'Recovery: {len(ready)} reviewed originals; {len(ready)*3} files; {len(errors)} errors.')
if errors: raise SystemExit('\n'.join(errors))
