"""Exact reviewed import of existing owner-supplied Adams chart media.

No generated-art preflight, physical-device certification or site release is
inferred. Review records are byte-bound decisions, not authenticated signatures.
"""
import hashlib
import json
import math
import re
from pathlib import Path

MANIFEST = 'docs/adams-chart-import/delivery.json'
PREFIX = 'assets/adams-chart/'
APPROVED_SPEC = 'b64d24874d509ce0d6d4d8434a619b3471a45d6867008a3dc78d8ca5f315913b'
APPROVED_REVIEWS = 'd7972af292adeb00ab32eb218633196bfcb969d5e3e76d65bde234ee836cee95'
RASTERS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif', '.bmp', '.tif', '.tiff'}


def require(ok, message):
    if not ok:
        raise ValueError('Adams source import: ' + message)


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def local(root, name):
    require(isinstance(name, str) and bool(name) and not name.startswith('/') and '\\' not in name and ':' not in name and '..' not in Path(name).parts, 'unsafe path')
    p = root / name
    require(p.is_file() and p.resolve().is_relative_to(root.resolve()), 'missing or unsafe file: ' + name)
    require(not any(q.is_symlink() for q in [p, *p.parents] if q == root or root in q.parents), 'symlink path')
    return p


def bound(root, item):
    p = local(root, item['path'])
    raw = p.read_bytes()
    if item['path'] == 'timelines/adams-1881-chart.html':
        from timeline_adams_diagnostic_successor import AFTER, restore
        if hashlib.sha256(raw).hexdigest() == AFTER:
            raw = restore(raw, root)
    require(len(raw) == item['bytes'], 'changed size: ' + item['path'])
    require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'changed bytes: ' + item['path'])
    return raw


def validate_reviews(root, record):
    require(record.get('schema') == 1, 'unknown schema')
    require(record.get('status') == 'REVIEWED_EXACT_SOURCE_IMPORT', 'finished review still pending')
    require(canonical(record['spec']) == APPROVED_SPEC, 'unreviewed exact specification')
    reviews = record['reviews']
    require(canonical(reviews) == APPROVED_REVIEWS, 'unapproved finished receipts')
    require(len(reviews) == 3 and {r['reviewer'] for r in reviews} == {'Galileo', 'Newton', 'Albert'}, 'missing independent/root review')
    for review in reviews:
        require(review.get('decision') == 'CONCUR' and review.get('spec_sha256') == APPROVED_SPEC, 'stale or negative review')
        require(review.get('source_rights_checked') is True and review.get('finished_pixels') is True and review.get('desktop_phone_inspected') is True, 'unperformed review')
        require(review.get('observations') and review.get('limits') and review.get('evidence'), 'missing bounded evidence')
        for item in review['evidence']:
            bound(root, item)


def validate_semantic_successor(result):
    """Current actual report semantics, separate from exact source/evidence pins."""
    semantics = result.get('semantics')
    require(isinstance(semantics, dict), 'QA missing semantic evidence')
    heading = semantics.get('heading')
    links = semantics.get('continuations')
    require(isinstance(heading, dict), 'QA missing H1 evidence')
    require(heading.get('selector') == 'h1.title' and heading.get('tag') == 'H1' and heading.get('text') == 'Adams’ Chart · 1881', 'QA H1 identity')
    require(heading.get('fontWeight') == '700' and isinstance(heading.get('fontFamily'), str) and 'Georgia' in heading['fontFamily'] and heading.get('margins') == ['0px'] * 4, 'QA H1 styling')
    width = result['profile']['width']; height = result['profile']['height']
    expected_font = 22 if width >= 900 else min(23, max(16, width * .048))
    require(isinstance(heading.get('fontSize'), (int, float)) and math.isfinite(heading['fontSize']) and abs(heading['fontSize'] - expected_font) <= .02, 'QA H1 responsive size')
    require(isinstance(links, list) and len(links) == 2 and all(isinstance(n, dict) for n in links), 'QA continuation count')
    expected_links = [('.fc-adams-back', '../timeline.html#choose-timeline', 'Back to timelines'), ('.fc-adams-home', '../index.html', 'FocusChrist Home')]
    for node, expected in zip(links, expected_links):
        require((node.get('selector'), node.get('href'), node.get('text')) == expected and node.get('tag') == 'A', 'QA continuation identity')
    initial = next((state for state in result['states'] if state['label'] == 'initial-fit'), None)
    require(initial is not None, 'QA missing initial semantic geometry')
    for node in [heading, *links]:
        require(node.get('visible') is True and node.get('hit') is True, 'QA semantic visibility/hit')
        require(all(isinstance(node.get(k), (int, float)) and not isinstance(node.get(k), bool) and math.isfinite(node[k]) for k in ('x', 'y', 'right', 'bottom', 'width', 'height')), 'QA semantic finite geometry')
        require(node['width'] > 0 and node['height'] > 0 and node['x'] >= -1 and node['y'] >= -1 and node['right'] <= width + 1 and node['bottom'] <= height + 1, 'QA semantic physical bounds')
        require(abs(node['right'] - node['x'] - node['width']) <= 1 and abs(node['bottom'] - node['y'] - node['height']) <= 1, 'QA semantic box consistency')
    require(all(n['bottom'] <= initial['viewport']['y'] + 1 for n in links), 'QA continuations must remain above chart')


def validate_qa_report(spec, report, identity, captures):
    """Semantic checks after exact evidence byte binding; also unit-testable data."""
    require(report['sourceSHA256'] == spec['page']['sha256'] and report['landingSHA256'] == spec['landing']['sha256'], 'QA source identity')
    require(report['assetCount'] == 331 and report['assetBytes'] == 119541095, 'QA asset totals')
    rows = spec['assets']
    digest_input = ''.join(f"{r['path']}\0{r['bytes']}\0{r['sha256']}\n" for r in sorted(rows, key=lambda r: r['path']))
    require(report['assetSetSHA256'] == hashlib.sha256(digest_input.encode()).hexdigest(), 'QA asset digest')
    results = report['results']
    require(report['timedOut'] is False and len(results) == 4, 'QA timeout or profile count')
    require([r['profile'] for r in results] == spec['qa']['profiles'], 'QA profiles')
    require(all(r['pass'] is True and not r.get('error') and not r.get('issues') for r in results), 'QA failed profile')
    require(sum(len(r['states']) for r in results) == spec['qa']['states'] == 101, 'QA state count')
    require(all(r['initialFitOverlayOverlap'] == [] for r in results), 'QA initial chart obstruction')
    required = {'initial-fit', 'one-to-one', 'right-tap', 'left-tap', 'down-tap', 'up-tap', 'next-section', 'start', 'end', 'reset-fit', 'zoom-in', 'zoom-out', 'full-view', 'exit-full-view', 'fill-screen', 'exit-fill-screen', 'restore-map', 'map-navigation', 'final-reset', 'history-back-viewer', 'reload-viewer', 'home-history-back-viewer'}
    for result in results:
        validate_semantic_successor(result)
        labels = [s['label'] for s in result['states']]
        require(len(labels) == len(set(labels)) and required <= set(labels), 'QA missing or duplicate journey')
        if result['profile']['width'] <= 899 and result['profile']['height'] <= 700:
            require({'restore-arrows', 'compact-clear-fit'} <= set(labels), 'QA compact restore/close')
        for state in result['states']:
            tile = state['firstTile']; inline = tile['inline']; rect = tile['rect']; vp = state['viewport']
            require(abs(vp['y'] - state['toolbar']['bottom']) <= 1, 'QA toolbar overlap')
            require(abs(rect['width'] - inline['width']) <= 1 and abs(rect['height'] - inline['height']) <= 1 and abs(rect['x'] - vp['x'] - inline['left']) <= 1 and abs(rect['y'] - vp['y'] - inline['top']) <= 1, 'QA rendered geometry')
    shots = [shot for result in results for shot in result['screenshots']]
    require(len(shots) == report['screenshots'] == spec['qa']['screenshot_count'] == 24, 'QA screenshot count')
    require(len({s['file'] for s in shots}) == 24, 'QA duplicate screenshot')
    require(all(0 < s['bytes'] <= 1024 * 1024 and re.fullmatch(r'[a-z0-9-]+\.jpg', s['file']) for s in shots), 'QA screenshot limits')
    require(sum(s['bytes'] for s in shots) == report['screenshotBytes'] <= 23 * 1024 * 1024, 'QA screenshot bytes')
    require(captures['capture_count'] == 24 and sorted(captures['captures'], key=lambda r: r['file']) == sorted(shots, key=lambda r: r['file']), 'capture manifest mismatch')
    require(captures['raw_report_sha256'] == spec['qa']['report']['sha256'], 'capture report identity')
    require(identity['run_id'] == captures['run_id'] == 40486830674 and identity['artifact_id'] == captures['artifact_id'] == 12726195196, 'run/artifact identity')
    require(identity['artifact_bytes'] == captures['artifact_bytes'] == 2102256 and identity['artifact_sha256'] == captures['artifact_sha256'], 'artifact bytes')
    require(identity['head_sha'] == 'ae03684acc0ff56d622028755d7d97ce8902288a' and identity['timeline_job_id'] == 122130602263 and identity['timeline_conclusion'] == 'success', 'Timeline identity')
    require(identity['release_claim'] is False and identity['workflow_conclusion'] == 'failure', 'unsupported whole-site acceptance')
    require(identity.get('repository') == 'caribousun/focuschrist-website' and identity.get('event') == 'pull_request' and identity.get('producer_ref') == 'refs/pull/530/merge', 'producer context')
    require(identity.get('producer_checkout_sha') == '5465aacfbae9c80733e41f258e213eb6f37266d6' and identity.get('producer_base_sha') == 'b4e023cfbe5e98b1191571f8ed3ca97c5a9f0c8b', 'producer merge identity')
    assets = {'/' + r['path']: r for r in rows}; profiles = {r['profile']['name'] for r in results}
    require(0 < len(report['network']) <= report['requestCount'] <= 2000, 'QA request bound')
    for response in report['network']:
        expected = assets.get(response['path'])
        require(expected is not None and response['profile'] in profiles and response['status'] == 200 and response['bytes'] == expected['bytes'] and response['sha256'] == expected['sha256'], 'QA tile response')
    require(sum(r['bytes'] for r in report['network']) == report['tileResponseBytes'] <= 256 * 1024 * 1024, 'QA response byte bound')


def validate_qa(root, record):
    spec = record['spec']; qa = spec['qa']
    bound(root, qa['helper'])
    raw = bound(root, qa['report'])
    require(len(raw) <= 1024 * 1024, 'QA report byte bound')
    report = json.loads(raw)
    identity = json.loads(bound(root, qa['run_identity']))
    capture_items = [e for r in record['reviews'] for e in r['evidence'] if e['path'].endswith('/capture-manifest.json')]
    require(len(capture_items) == 3 and all(e == capture_items[0] for e in capture_items), 'capture evidence binding')
    captures = json.loads(bound(root, capture_items[0]))
    validate_qa_report(spec, report, identity, captures)


def validate_source(root, record, added, covered, rejected):
    """Data-only validation, not finished review or general release coverage."""
    require(record.get('schema') == 1, 'unknown schema')
    spec = record['spec']
    require(canonical(spec) == APPROVED_SPEC, 'unreviewed exact specification')
    require(spec['kind'] == 'EXISTING_OWNER_SUPPLIED_CHART' and spec['precreation_claim'] is False, 'misclassified creation')
    require(spec['canvas'] == {'width': 50195, 'height': 5347, 'tile': 1024, 'levels': [1, 4, 16, 64]}, 'canvas/grid drift')
    page = bound(root, spec['page']).decode('utf-8')
    bound(root, spec['landing'])
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
    # Reject pending/stale receipts and evidence before expensive JPEG decoding.
    validate_reviews(root, record)
    validate_qa(root, record)
    return validate_source(root, record, added, covered, rejected)
