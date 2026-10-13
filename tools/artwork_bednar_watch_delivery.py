"""Exact approved Bednar derivative and current four-card Watch review binding."""
import json
from PIL import Image
from artwork_watch_thumbnail_delivery import bound, canonical, require
from build_watch_shorts import render, START, END

ASSET = 'assets/shorts/bednar-holy-ghost-or-me-approved-20261013.png'
ASSET_SHA256 = '440b4a9f6388dbb0a0791745e4d7a21a8763b908b82cf64a4b57a37ab3c9d6a0'
MASTER_SHA256 = '039bdeba99cd441f548e6fb1db61dc458dba814340821914c9e6a8f93f830eb1'
VIDEO_ID = '-LvOxhI8YY0'
LATEST_IDS = [VIDEO_ID, 'zIntX6aoq1g', 'xzAenmOZ1Yk', 'vRzEDllHvlE']


def validate(root, record, approved_binding, added, covered, rejected, pixel_hash, page_dependencies):
    spec = record['spec']
    require(canonical(spec) == approved_binding, 'unreviewed Bednar specification')
    require(spec['route'] == 'watch.html' and spec['video_id'] == VIDEO_ID, 'wrong Bednar destination')
    asset = spec['asset']
    require(asset['path'] == ASSET and asset['sha256'] == ASSET_SHA256, 'wrong Bednar derivative')
    require(ASSET in added and ASSET not in covered and ASSET_SHA256 not in rejected, 'Bednar coverage mismatch')
    path = bound(root, asset)
    with Image.open(path) as im:
        require(im.format == 'PNG' and im.size == (941, 1672) and getattr(im, 'n_frames', 1) == 1, 'changed Bednar dimensions')
    require(pixel_hash(path) == asset['pixel_sha256'], 'changed Bednar pixels')
    approval = json.loads(bound(root, spec['owner_approval']).read_text(encoding='utf8'))
    require(approval['owner'] == 'Wyatt' and approval['master_sha256'] == MASTER_SHA256 and approval['status'] == 'OWNER_APPROVED_EXACT_SOURCE', 'missing Bednar owner approval')
    require(approval['exact_messages'] == ['The stream is disconnect but I approve the latest thumbnail and short to get published on our social', 'and also the focus site updated on the watch page with this latest short'], 'changed Bednar owner evidence')
    lineage = json.loads(bound(root, spec['lineage']).read_text(encoding='utf8'))
    require(lineage['source_sha256'] == MASTER_SHA256 and lineage['derivative_sha256'] == ASSET_SHA256 and lineage['source_dimensions'] == [3764, 6688] and lineage['dimensions'] == [941, 1672], 'changed Bednar lineage')
    require(lineage['method'] == 'Exact quarter-size Lanczos3 resampling; no crop, compositing, repaint or sharpening.', 'changed Bednar derivation')
    publication = json.loads(bound(root, spec['publication']).read_text(encoding='utf8'))
    require(publication['status'] == 'VERIFIED_PUBLIC' and publication['latest_ids'] == LATEST_IDS and publication['public_url'] == 'https://www.youtube.com/shorts/' + VIDEO_ID, 'Bednar public verification missing')
    require(publication['observer'] == 'Albert' and publication['observed_at'] and publication['evidence'], 'Bednar publication evidence missing')
    context = spec['context']
    require(len({x['path'] for x in context}) == len(context), 'duplicate Bednar context')
    require(page_dependencies(root, 'watch.html') | {'docs/watch-shorts.json', 'watch-shorts.js'} <= {x['path'] for x in context}, 'missing current Watch context')
    for item in context:
        bound(root, item)
    data = json.loads((root / 'docs/watch-shorts.json').read_text(encoding='utf8'))
    require([x['id'] for x in data['shorts']] == LATEST_IDS, 'wrong current latest-four order')
    require(data['shorts'][0]['thumbnail'] == ASSET and data['shorts'][0]['thumbnail_sha256'] == ASSET_SHA256 and data['shorts'][0]['thumbnail_dimensions'] == [941, 1672], 'Bednar card asset mismatch')
    old = json.loads((root / 'docs/watch-bednar/history/watch-shorts.json').read_text(encoding='utf8'))
    require(data['shorts'][1:] == old['shorts'][:3], 'retained cards changed')
    page = (root / 'watch.html').read_text(encoding='utf8')
    require(page.count(START) == page.count(END) == 1, 'ambiguous current Watch section')
    require(page[page.index(START):page.index(END) + len(END)] == render(data), 'current Watch card markup mismatch')
    require('object-fit: contain' in (root / 'watch-shorts.css').read_text(encoding='utf8'), 'crop-safe fit removed')
    require(len(record['reviews']) == 3, 'three current Watch reviewers required')
    reviewers = set()
    for item in record['reviews']:
        review = json.loads(bound(root, item).read_text(encoding='utf8'))
        who = review['reviewer']
        require(who in {'Albert', 'Fermi', 'Newton'} and who not in reviewers, 'wrong current Watch reviewer')
        reviewers.add(who)
        require(review['decision'] == 'CONCUR_CURRENT_WATCH' and review['spec_sha256'] == approved_binding, 'stale current Watch review')
        require(review['desktop_phone_inspected'] is True and review['all_four_cards_inspected'] is True and review['historical_spannaus_limits_preserved'] is True and review['observations'], 'incomplete current Watch review')
        require(set(review['evidence']) == {'desktop', 'phone'}, 'missing current Watch viewport evidence')
        for evidence in review['evidence'].values():
            require(len(evidence['sha256']) == 64 and evidence['description'], 'invalid current viewport evidence')
        if who == 'Albert':
            require(review['direct_browser_interactions'] is True, 'root Watch interactions missing')
    return {ASSET}, {ASSET_SHA256}, {asset['pixel_sha256']}
