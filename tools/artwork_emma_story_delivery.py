"""Exact five-scene Emma current-equivalence proposal; no retroactive preflight.

Pending records cannot pass. This family does not grant generic raster coverage,
waive other gates, or infer owner approval from a technical receipt.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
from PIL import Image

MANIFEST = 'docs/emma-story-artwork-import/delivery.json'
APPROVED_RECORD_SHA256 = '52d00b1b8b2177fab0ba0b75f9549b8b026ce390817cd0c300d3666421534325'  # Set only after exact independent/root finished review.
SCENES = {
    'ride': ('history/emma-elect-lady.html', '947d1f4be80ec82e193d8ad38164d3bbc0c1ad82e2aa31fc59a9a454936c545c'),
    'hymnal': ('history/emma-hymns.html', 'b20a78f3af80f987df0220e157c32244f463cb37e25e0128aff8f5e42987e42b'),
    'quincy': ('history/emma-winter-crossing.html', '9dd0cbe00e0e54a5b2d584a2ecdce3e7d6d83ae31117a32ed9c4e5c67545307e'),
    'hospitality': ('history/emma-relief-society.html', '7429139f23722f6e6f86785fe6090b45a20c172405cd9c56207a8816f4617d3c'),
    'testimony': ('history/emma-last-testimony.html', 'c236d424cb558fff657048e286410bf1f6cb5cb841513a4568a8d0449fa34af1'),
}
CHECKS = {'identity', 'age', 'expression_gaze', 'atmosphere', 'environment',
          'characters_realism', 'period_sources', 'anatomy', 'uniqueness', 'desktop_phone'}


def require(ok, message):
    if not ok:
        raise ValueError('Emma exact artwork delivery: ' + message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def local(root, name):
    require(isinstance(name, str) and name and not Path(name).is_absolute()
            and '\\' not in name and ':' not in name and '..' not in Path(name).parts, 'unsafe path')
    p = root / name
    require(not any(part.is_symlink() for part in [p, *p.parents] if part != root.parent), 'symlink evidence')
    require(p.resolve().is_relative_to(root.resolve()) and p.is_file(), 'missing local evidence: ' + name)
    return p


def bound(root, item):
    raw = local(root, item['path']).read_bytes()
    require(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'changed evidence: ' + item['path'])
    return raw


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None, 'timezone required')
    return result


def chronology(record, normalized):
    require(isinstance(record, dict), 'missing generation-time classification')
    status = record.get('status')
    if status == 'UNKNOWN_NOT_INFERRED':
        require(record.get('timestamp') is None and record.get('basis'), 'unknown time falsely populated')
    else:
        require(status == 'DOCUMENTED' and record.get('basis'), 'unsupported time classification')
        require(stamp(record['timestamp']) < normalized, 'generation after normalization')
    require(record.get('file_mtime_used') is False, 'mtime is not generation evidence')


def validate(root, record, added, covered, rejected, pixel_hash, page_dependencies):
    require(APPROVED_RECORD_SHA256 is not None, 'pending independent/root exact record review')
    require(canonical(record) == APPROVED_RECORD_SHA256, 'unreviewed record bytes')
    require(record.get('schema') == 1 and record.get('status') == 'REVIEWED_EXACT_CURRENT_EQUIVALENCE', 'unfinished record')
    spec = record['spec']
    require(spec['registration_class'] == 'EXACT_FIVE_EMMA_CURRENT_EQUIVALENCE'
            and spec['historical_canonical_preflight_claim'] is False, 'false historical approval')
    require({s['id']: s['route'] for s in spec['scenes']} == {k:v[0] for k,v in SCENES.items()}
            and len(spec['scenes']) == 5, 'scene expansion/omission')
    require(spec['private_reference_bytes_published'] is False, 'private references not allowed')
    require(spec['rejection_history_preserved'] is True, 'rejection history removed')
    require(spec['ride_limit'] == 'Far hind hoof naturally occluded; full four-hoof visibility not established', 'hoof limit changed')
    normalized = stamp(record['normalized_at'])
    assets, hashes, pixels = set(), set(), set()
    for number, (scene_id, (route, original_sha)) in enumerate(SCENES.items(), 1):
        scene = next(s for s in spec['scenes'] if s['id'] == scene_id)
        original = scene['original']
        expected_original = 'assets/page-art/emma-life/originals/emma-' + scene_id + '-selected.png'
        require(original['path'] == expected_original and original['sha256'] == original_sha, 'wrong selected original')
        expected_derivatives = {f'assets/page-art/emma-life/emma-story{number}-{scene_id}-review-{w}.webp' for w in (640,960,1536)}
        require(len(scene['derivatives']) == 3 and {a['path'] for a in scene['derivatives']} == expected_derivatives, 'derivative family drift')
        require(scene['historical_source_review_scope'] == 'SOURCE_ART_ONLY_NOT_ASSEMBLED', 'historical scope inflated')
        require(scene['derivative_relation'] == 'PROPORTIONAL_REENCODING_NOT_PIXEL_IDENTICAL_LANCZOS', 'false lossless claim')
        require(scene['source_provenance']['historical_canonical_preflight'] == 'NOT_CLAIMED'
                and scene['source_provenance']['actual_receipt_pins'], 'missing genuine source evidence')
        chronology(scene['generation_time'], normalized)
        for receipt in scene['source_provenance']['actual_receipt_pins']:
            bound(root, receipt)
        original_size = tuple(original['dimensions'])
        for a in [original, *scene['derivatives']]:
            bound(root, a)
            require(a['sha256'] not in rejected, 'rejected asset')
            require(pixel_hash(local(root,a['path'])) == a['pixel_sha256'], 'decoded pixel drift')
            with Image.open(local(root,a['path'])) as im:
                require(getattr(im,'n_frames',1) == 1 and list(im.size) == a['dimensions'], 'dimensions/animation drift')
                if a is not original:
                    require(im.height == round(original_size[1]*im.width/original_size[0]), 'nonproportional derivative')
            require(a['path'] not in assets and a['sha256'] not in hashes and a['pixel_sha256'] not in pixels, 'duplicate asset')
            assets.add(a['path']); hashes.add(a['sha256']); pixels.add(a['pixel_sha256'])
        context = scene['context']
        require(len({a['path'] for a in context}) == len(context), 'duplicate context')
        require(page_dependencies(root,route) <= {a['path'] for a in context}, 'missing page/CSS context')
        for item in context:
            bound(root,item)
        class Sources(HTMLParser):
            paths = None
            def handle_starttag(self, tag, attrs):
                for key, value in attrs:
                    if key in {'src', 'href'} and value:
                        self.add(value)
                    elif key == 'srcset' and value:
                        for entry in value.split(','):
                            self.add(entry.strip().split()[0])
            def add(self, value):
                target = urlsplit(urljoin('https://focuschrist.com/'+route, value))
                if target.hostname == 'focuschrist.com':
                    self.paths.add(unquote(target.path).lstrip('/'))
        parser = Sources(); parser.paths = set()
        parser.feed(local(root,route).read_text(encoding='utf-8'))
        require(expected_derivatives <= parser.paths, 'derivative not consumed by scene')
    require(len(assets) == 20 and assets <= added and not assets & covered, 'coverage overlap/omission')
    binding = canonical(spec)
    reviewers = set()
    for pointer in record['reviews']:
        receipt = json.loads(bound(root,pointer))
        who = receipt['reviewer']
        require(who in {'Fermi','Newton','Albert'} and who not in reviewers, 'reviewer missing/duplicate')
        require(receipt['decision'] == 'CONCUR' and receipt['spec_sha256'] == binding
                and receipt.get('withdrawn') is False, 'negative/stale review')
        require(stamp(receipt['reviewed_at']) >= normalized, 'backdated current equivalence')
        require(receipt['source_provenance_verified'] is True and receipt['actual_derivatives_inspected'] is True
                and receipt['assembled_context_inspected'] is True, 'unperformed review')
        require(set(receipt['checks']) == CHECKS and all(isinstance(v,str) and v.strip() for v in receipt['checks'].values()), 'missing actual observations')
        require(receipt['limits'] and receipt['evidence'], 'missing bounded evidence')
        for item in receipt['evidence']:
            bound(root,item)
        if who == 'Albert':
            require(set(receipt['rendered']) == {'desktop','phone'}, 'both viewport evidence required')
            for item in receipt['rendered'].values():
                bound(root,item)
        reviewers.add(who)
    require(reviewers == {'Fermi','Newton','Albert'}, 'three actual current reviews required')
    return assets, hashes, pixels
