"""Import only individually reviewed original pixels; no implicit approval by filename."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from build_jesus_journey import validate_artwork_review

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/jesus-journey'
WORK = ROOT.parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reviews', nargs='+', type=Path)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    registry = read(DATA / 'artworks.json')
    records = [read(p) for p in sorted((WORK / 'generated-records').glob('*.json'))]
    output = {}
    for source in args.reviews:
        review = read(source)
        shutil.copy2(source, DATA / source.name)
        for entry in review.get('entries', review.get('candidates', [])):
            if entry.get('status', entry.get('verdict')) not in ('pass', 'pass_with_caption_conditions'):
                continue
            key = entry['key']
            if key not in registry:
                raise ValueError('Unplanned artwork: ' + key)
            candidates = [r for r in records if r['key'] == key and
                          hashlib.sha256(Path(r['generated_path']).read_bytes()).hexdigest() == entry['sha256']]
            if len(candidates) != 1:
                raise ValueError(f'{key}: expected exactly one matching reviewed original, found {len(candidates)}')
            record = candidates[0]
            if not entry.get('alt') or not entry.get('caption'):
                raise ValueError('Missing actual-pixel editorial copy: ' + key)
            refs = entry.get('refs')
            if not isinstance(refs, list) or not refs or any(not isinstance(ref, list) or len(ref) != 3 for ref in refs):
                refs = registry[key]['refs']
            if not isinstance(refs, list) or not refs or any(not isinstance(ref, list) or len(ref) != 3 for ref in refs):
                raise ValueError('Missing structured source references: ' + key)
            output[key] = {
                **registry[key],
                'title': entry.get('recommendedTitle', registry[key]['title']),
                'alt': entry['alt'], 'caption': entry['caption'],
                'refs': refs,
                'generated_path': record['generated_path'], 'original': key + '.png',
                'original_sha256': entry['sha256'], 'prompt': record['prompt'],
                'referenced_image_paths': record.get('referenced_image_paths', []),
                'reviewed': True, 'review_record': source.name, 'owner_approved': False,
            }
            previous=registry[key].get('original_sha256')
            if previous and previous!=entry['sha256']:
                output[key]['supersedes_sha256']=previous
                stem=key+'--'+entry['sha256'][:12]
                output[key]['original']=stem+'.png'
                for field,suffix in [('asset','-full.webp'),('thumbnail','-thumb.webp')]:
                    output[key][field]=str(Path(registry[key][field]).parent/stem).replace('\\','/')+suffix
                    output[key].pop(field+'_sha256',None)
            elif previous==entry['sha256']:
                output[key]['original']=registry[key]['original']
            validate_artwork_review(key,output[key],DATA)
    target = DATA / ('art-batch-' + args.batch + '.json')
    if target.exists() and read(target) != output:
        raise ValueError('Refusing to replace a different imported batch: ' + str(target))
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Imported {len(output)} hash-matched reviewed originals into {target.name}')


if __name__ == '__main__':
    main()
