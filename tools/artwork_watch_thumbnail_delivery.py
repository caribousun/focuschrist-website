"""Exact historical Spannaus cover delivery; current Watch review is separate."""
import hashlib
import json
from pathlib import Path
from PIL import Image

PREVIOUS_ASSET = 'assets/shorts/god-is-at-your-side-approved-20261012.png'
PREVIOUS_SHA256 = '4c0e9bd8ab7d06d588c78c35e3862705313fd869d11baac501e6525d38a56154'
ASSET = 'assets/shorts/god-is-at-your-side-portrait-20261012.png'
SOURCE_SHA256 = '78f547b0f541f33e97cb8d8be33a7ea6dfdac8a10516c8712a8b08e19be1ab63'
VIDEO_ID = 'zIntX6aoq1g'
HISTORICAL_CONTEXT = {
    'watch.html': 'docs/watch-bednar/history/watch.html.txt',
    'docs/watch-shorts.json': 'docs/watch-bednar/history/watch-shorts.json',
}

def require(value, message):
    if not value:
        raise ValueError('Watch thumbnail: ' + message)

def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def bound(root, item):
    name = item['path']
    require(isinstance(name, str) and '\\' not in name and ':' not in name and '..' not in Path(name).parts, 'unsafe evidence path')
    path = root / name
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file() and not path.is_symlink(), 'missing or escaped evidence')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], 'changed evidence: ' + name)
    return path

def validate(root, record, approved_binding, added, covered, rejected, pixel_hash, page_dependencies):
    spec = record['spec']
    require(canonical(spec) == approved_binding, 'unreviewed specification')
    require(spec['route'] == 'watch.html' and spec['video_id'] == VIDEO_ID, 'wrong destination')
    asset = spec['asset']
    require(asset['path'] == ASSET and asset['sha256'] == SOURCE_SHA256, 'wrong approved asset')
    require(SOURCE_SHA256 not in rejected and ASSET in added and ASSET not in covered, 'rejected or duplicate coverage')
    path = bound(root, asset)
    with Image.open(path) as im:
        require(im.format == 'PNG' and im.size == (941, 1672) and getattr(im, 'n_frames', 1) == 1, 'changed image dimensions/format')
    require(pixel_hash(path) == asset['pixel_sha256'], 'changed decoded pixels')
    approval = json.loads(bound(root, spec['owner_approval']).read_text(encoding='utf8'))
    require(approval['owner'] == 'Wyatt' and approval['status'] == 'OWNER_APPROVED_EXACT_PORTRAIT' and approval['sha256'] == SOURCE_SHA256, 'missing exact owner approval')
    require(approval['review_limits'] == 'Fermi and Newton retained uncertainty about precise reciprocal pupil targets. Wyatt explicitly accepted this exact image; their historical findings are not rewritten as unconditional gaze approval.', 'historical uncertainty omitted')
    require(approval['exact_messages'] == ['Approve this full-height version'], 'changed owner evidence')
    bound(root, spec['lineage'])
    previous = json.loads(bound(root, spec['retained_square_delivery']).read_text(encoding='utf8'))
    require(canonical(previous['spec']) == 'ea7f86749d8ff6fd06e0fdc6be0f8154f948d52abb48cf51fac33cdf96b148ec', 'changed historical square specification')
    previous_asset = previous['spec']['asset']
    require(previous_asset['path'] == PREVIOUS_ASSET and previous_asset['sha256'] == PREVIOUS_SHA256, 'wrong retained square')
    previous_path = bound(root, previous_asset)
    require(pixel_hash(previous_path) == previous_asset['pixel_sha256'], 'changed retained square pixels')
    require(PREVIOUS_ASSET in added and PREVIOUS_ASSET not in covered and PREVIOUS_SHA256 not in rejected, 'retained square coverage mismatch')
    require(spec['historical_square_scope'] == 'Preserved original artifact and reviews; superseded for this Watch card by explicit owner-approved portrait. Historical page context is not current acceptance.', 'missing historical scope')
    context = spec['context']
    require(len({x['path'] for x in context}) == len(context), 'duplicate context')
    require(page_dependencies(root, 'watch.html') <= {x['path'] for x in context}, 'missing page context')
    for item in context:
        # Preserve the exact originally reviewed context, not a retroactive review.
        saved = {**item, 'path': HISTORICAL_CONTEXT.get(item['path'], item['path'])}
        bound(root, saved)
    data = json.loads((root / HISTORICAL_CONTEXT['docs/watch-shorts.json']).read_text(encoding='utf8'))
    first = data['shorts'][0]
    require([x['id'] for x in data['shorts']] == [VIDEO_ID, 'xzAenmOZ1Yk', 'vRzEDllHvlE', 'OSgN-cSJOPs'], 'wrong latest-four selection')
    require(first['thumbnail'] == ASSET and first['thumbnail_sha256'] == SOURCE_SHA256, 'card asset mismatch')
    require('object-fit: contain' in (root / 'watch-shorts.css').read_text(encoding='utf8'), 'crop-safe fit removed')
    reviewers = set()
    require(len(record['reviews']) == 3, 'three assembled reviews required')
    for item in record['reviews']:
        review = json.loads(bound(root, item).read_text(encoding='utf8'))
        who = review['reviewer']
        require(who in {'Albert', 'Fermi', 'Newton'} and who not in reviewers, 'wrong or duplicate reviewer')
        reviewers.add(who)
        require(review['decision'] == 'CONCUR_ASSEMBLED_OWNER_APPROVED' and review['spec_sha256'] == approved_binding, 'stale or negative assembled review')
        require(review['historical_pupil_uncertainty_preserved'] is True and review['desktop_phone_inspected'] is True and review['observations'], 'missing scoped visual review')
        require(set(review['evidence']) == {'desktop', 'phone'}, 'missing viewport evidence')
        for view in review['evidence'].values():
            require(len(view['sha256']) == 64 and view['description'], 'missing exact visual evidence')
        if who == 'Albert':
            require(review['direct_browser_interactions'] is True, 'root interaction review required')
    return {ASSET, PREVIOUS_ASSET}, {SOURCE_SHA256, PREVIOUS_SHA256}, {asset['pixel_sha256'], previous_asset['pixel_sha256']}
