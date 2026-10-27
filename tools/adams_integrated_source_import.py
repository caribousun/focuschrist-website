"""Exact integrated Adams context, with preserved historical V9 source tests.

Approval literals bind actual current hosted evidence and three independently
authored reviews. Full source, report and historical checks remain required.
"""
import hashlib
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from adams_source_import_v9 import require, canonical, local, bound, PREFIX, RASTERS

MANIFEST = 'docs/adams-integrated-context/delivery.json'
APPROVED_RECORD = '837e311fe10ac1a5f804daf477a71178f242da6369df001a3774041462717923'
APPROVED_SPEC = '5fb32aca33885b60b334ca5bcc4bede36663fe3ecd8557300bfea67155e1c5dc'
ASSET_SPEC = 'e3f6cf881bca5607c33899cb42016066413d7f54d9ed6ed72e47ec2a1630abc3'
CONTEXT_PATHS = {'timeline.html', 'timelines/adams-1881-chart.html',
                 'timelines/adams-1881-introduction.html', 'adams-integration.css',
                 'adams-integration.js'}

class Tags(HTMLParser):
    def __init__(self, raw):
        super().__init__(); self.tags = []; self.feed(raw.decode('utf-8'))
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

def validate_context(root, spec):
    rows = spec['context']
    require(len(rows) == len(CONTEXT_PATHS) and {r['path'] for r in rows} == CONTEXT_PATHS, 'exact five integrated context files')
    content = {r['path']: bound(root, r) for r in rows}
    shared = spec['shared_dependencies']
    names = {'site-system.css','site-header.css','site-search.css','site-common.js','site-search.js','timeline-experiences.css','unified-opening.css','unified-opening.js','timeline-mobile-study.css'}
    require(len(shared) == len(names) and {r['path'] for r in shared} == names, 'exact shared dependency set')
    for item in shared: bound(root, item)
    require(canonical(spec['assets']) == ASSET_SPEC, 'existing331 asset specification changed')
    require(spec.get('context_kind') == 'OWNER_REQUESTED_CANONICAL_HEADER_AND_INTRODUCTION', 'context kind')
    for name in ('timelines/adams-1881-chart.html', 'timelines/adams-1881-introduction.html'):
        tags = Tags(content[name]).tags
        require(sum(t == 'nav' and a.get('data-focuschrist-header') == 'standard' for t,a in tags) == 1, 'canonical header missing/duplicate')
        require(sum(t == 'footer' and a.get('data-focuschrist-footer') == 'standard' for t,a in tags) == 1, 'canonical footer missing/duplicate')
        require(sum('data-site-search-trigger' in a for _,a in tags) == 1, 'shared search trigger missing/duplicate')
        require(any(t == 'script' and a.get('src') == '../site-search.js?v=20260919-focused-answers-1' for t,a in tags), 'shared search controller missing')
    usage = spec['asset_use']
    expected = {'timelines/adams-1881-chart.html':'exact331tilemap',
                'timelines/adams-1881-introduction.html':['assets/adams-chart/adams-16-0-0.jpg','assets/adams-chart/adams-64-0-0.jpg'],
                'timeline.html':['assets/adams-chart/adams-64-0-0.jpg']}
    require(usage == expected, 'same-chart reference ownership changed')
    for name in ('timelines/adams-1881-introduction.html','timeline.html'):
        images = [a.get('src','').removeprefix('../') for t,a in Tags(content[name]).tags if t == 'img' and 'assets/adams-chart/' in a.get('src','')]
        require(sorted(images) == sorted(expected[name]), 'chart reference missing/duplicated or unexpected')
    require(b'fc-adams-strip' not in content['timelines/adams-1881-chart.html'].split(b'</head>',1)[1], 'old pre-chart strip retained')
    return content

def validate_reviews(root, record):
    require(APPROVED_RECORD is not None and canonical(record) == APPROVED_RECORD, 'current exact record still pending/unapproved')
    require(type(record.get('schema')) is int and record.get('schema') == 1 and record.get('status') == 'REVIEWED_EXACT_INTEGRATED_CONTEXT', 'unfinished current context')
    require(APPROVED_SPEC is not None and canonical(record['spec']) == APPROVED_SPEC, 'current specification mismatch')
    rows = record.get('reviews')
    require(isinstance(rows,list) and len(rows) == 3 and {r['reviewer'] for r in rows} == {'Fermi','Newton','Albert'}, 'three own current reviews required')
    for row in rows:
        own = json.loads(bound(root, row['receipt']))
        require(type(own.get('schema')) is int and own['schema'] == 1, 'current receipt schema')
        stamp = datetime.fromisoformat(own.get('reviewed_at', ''))
        require(stamp.tzinfo is not None, 'current receipt timestamp timezone')
        require(own.get('reviewer') == row['reviewer'] and own.get('spec_sha256') == APPROVED_SPEC and own.get('decision') == 'CONCUR', 'stale/negative/misattributed current receipt')
        require(own.get('source_rights_checked') is True and own.get('finished_pixels') is True and own.get('desktop_phone_inspected') is True, 'current review scope incomplete')
        require(own.get('observations') and own.get('limits') and own.get('evidence'), 'current observations/evidence/limits required')
        for item in own['evidence']: bound(root,item)

def validate_source(root, record, added, covered, rejected):
    """Data-only validation, not finished review or general release coverage."""
    require(record.get('schema') == 1, 'unknown schema')
    spec = record['spec']
    require(canonical(spec) == APPROVED_SPEC, 'unreviewed exact specification')
    require(spec['kind'] == 'EXISTING_OWNER_SUPPLIED_CHART' and spec['precreation_claim'] is False, 'misclassified creation')
    require(spec['canvas'] == {'width': 50195, 'height': 5347, 'tile': 1024, 'levels': [1, 4, 16, 64]}, 'canvas/grid drift')
    page = bound(root, spec['page']).decode('utf-8')
    bound(root, spec['landing'])
    validate_context(root, spec)
    rows = spec['assets']; paths = {r['path'] for r in rows}
    require(len(rows) == len(paths) == spec['total_images'] == 331, 'missing or duplicate assets')
    require(paths <= added and not paths & covered, 'absent or overlapping coverage')
    require({p for p in added if p.startswith(PREFIX)} == paths, 'unexpected chart raster')
    expected_keys = {f'{level}:{col}:{row}' for level in [1, 4, 16, 64] for col in range((50195 + level * 1024 - 1) // (level * 1024)) for row in range((5347 + level * 1024 - 1) // (level * 1024))}
    require({r['key'] for r in rows} == expected_keys, 'incomplete tile grid')
    assignments = re.findall(r'assets\["([0-9]+:[0-9]+:[0-9]+)"\]="(/assets/adams-chart/[^"\s]+)"', page)
    require(len(assignments) == 331 and len(dict(assignments)) == 331, 'asset assignment count')
    require(dict(assignments) == {r['key']: '/' + r['path'] for r in rows}, 'asset map mismatch')
    for p in (root / 'docs/adams-chart-import').rglob('*'):
        require(p.suffix.lower() not in RASTERS, 'additional public review raster')
    total = 0
    from PIL import Image
    for row in rows:
        require(re.fullmatch(r'assets/adams-chart/adams-(1|4|16|64)-[0-9]+-[0-9]+\.jpg', row['path']) is not None, 'noncanonical tile path')
        require(row['path'] == PREFIX + 'adams-' + row['key'].replace(':', '-') + '.jpg', 'wrong tile identity')
        level, col, y = map(int, row['key'].split(':'))
        require(row['dimensions'] == [min(1024, (50195 + level - 1) // level - col * 1024), min(1024, (5347 + level - 1) // level - y * 1024)], 'grid dimensions')
        require(row['sha256'] not in rejected, 'rejected bytes')
        raw = bound(root, row); total += len(raw)
        with Image.open(local(root, row['path'])) as image:
            require(image.format == 'JPEG' and list(image.size) == row['dimensions'], 'format/dimensions')
            image.verify()
        with Image.open(local(root, row['path'])) as image:
            image.load()
    require(total == spec['total_bytes'] == 119541095, 'byte total')
    require(spec['work']['source_file_page'] in page and 'courtesy of the David Rumsey Map Collection' in page, 'missing visitor credit')
    require('The image is in the public domain.' in page and 'CC BY-NC-SA' not in page, 'attribution drift')
    return paths


def validate(root, added, covered, rejected):
    record = json.loads(local(root, MANIFEST).read_text(encoding='utf-8'))
    validate_reviews(root, record)
    from adams_source_import_v9 import validate_reviews as validate_historical_reviews
    historical = json.loads(bound(root, record['spec']['historical_record']))
    validate_historical_reviews(root, historical)
    require(historical['spec']['assets'] == record['spec']['assets'], 'historical asset ownership changed')
    # Report adapter is separately source-reviewed once the exact hosted schema
    # is frozen; absent reports/adapter cannot approve a current context.
    from adams_integrated_qa_evidence import validate_qa
    validate_qa(root, record['spec'])
    return validate_source(root, record, added, covered, rejected)
