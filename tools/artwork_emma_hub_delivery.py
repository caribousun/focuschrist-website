"""Five unchanged Emma scenes in a genuinely new, reviewed hub context.

Pending records fail closed. Historical validation is explicit and never counted
as current placement, visual, ownership or release approval.
"""
import json
import re
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from artwork_emma_story_delivery import bound, canonical, local, require, sha, stamp, CHECKS, SCENES
from owner_integration_contract import HUB, STORIES, CANONICAL_SET_SHA256, Document, historical_bytes, validate_file, manifest

APPROVED_RECORD_SHA256 = '77f3e6d56634eab3f43179d243e4f26dcac0481409da16d6ab7d48197f979bf5'  # Actual own-author reviews; exact proposal remains under review.
RETAINED_REFLECTIONS_SHA256 = 'f5a6a39a9dd848275004bbf3dec894d5d3b36c3f6279457f34e52c9ab28aafa4'
RETAINED_ASSETS_SHA256 = '79aef2f504232a198cb658cb8c907891edc7d104505fadaa23d58dbfe81dfc2f'
PREDECESSOR_PATH = 'docs/emma-story-artwork-import/historical/ecfb-delivery.json'
PREDECESSOR_SHA256 = '8f212c5f2dd933ecc0c9267aebce5ddbe3cfbd61c718e40130a217fa7e8e424b'
PREDECESSOR_CANONICAL = '4223f7ff199d317771595d2539744f05a5557a32ed3754f612914ade66b839d3'
CURRENT_CHECKS = CHECKS | {'hub_ownership', 'reference_navigation', 'story_integration', 'christ_fit'}
SCRIPTS = {'site-common.js', 'topic-artwork-details.js', 'full-image-viewer.js', 'site-search.js'}
PROFILES = {'desktop': (1280, 900, False), 'phone': (390, 844, True),
            'narrow': (320, 568, True), 'landscape': (844, 390, True)}

# Exact supplemental context for two pre-existing hub stylesheets omitted from
# the original receipt. Producer and current repository blobs were verified
# equal. The retained report has no CSS response hashes; this is source-context
# evidence, not a claim that the original receipts individually named them.
SUPPLEMENT_SPEC_SHA256 = '5f1de193844aeeb108e8a474723188e8b5cf464eeacfa203f2cfe8802686baf9'
SUPPLEMENT_PRODUCER = '87cce928c366f3f5820fce1ae19bc989a952d982'
SUPPLEMENT = [
    {'path': 'guided-studies.css', 'bytes': 5688, 'sha256': '45349a7b3f0524a32989f827960bb543c6003944f0781958458bb25856ed0892'},
    {'path': 'targeted-six.css', 'bytes': 3484, 'sha256': '6234f992191650a688b93dc452215778b783fe9b3e0a9ed030a79641c4b0edc6'},
]


SUPPLEMENT_REVIEWS = [
    {'path': 'docs/emma-hub-artwork-import/css-context-review-albert.json', 'bytes': 1984, 'sha256': 'f4b735e1264453cc9ff7b8fdd92e2d43385b0da1d28bcaeccd8351d6c8dd26d1'},
    {'path': 'docs/emma-hub-artwork-import/css-context-review-independent.json', 'bytes': 2284, 'sha256': '72bb1082f1ce7add299a5ee6dab8813ad7307b5af6f6a21fd0416f8d73d334aa'},
]

def check_supplement_reviews(root):
    roles = set()
    for pointer in SUPPLEMENT_REVIEWS:
        review = json.loads(bound(root, pointer))
        role = review.get('reviewer')
        require(role in {'Albert', 'independent collaborating agent'} and role not in roles, 'supplement reviewer mismatch')
        require(review.get('decision') == 'CONCUR_EXACT_TWO_UNCHANGED_CSS_SOURCE_CONTEXT_SUPPLEMENT'
                and review.get('spec_sha256') == SUPPLEMENT_SPEC_SHA256
                and review.get('actual_render_producer') == SUPPLEMENT_PRODUCER, 'supplement review binding mismatch')
        require(review.get('actual_author') and review.get('observations') and review.get('limits'), 'incomplete supplement source review')
        stamp(review['reviewed_at'])
        sources = review.get('sources', [])
        require(len(sources) == len(SUPPLEMENT) and
                [{k: row.get(k) for k in ('path','bytes','sha256')} for row in sources] == SUPPLEMENT,
                'supplement review source mismatch')
        roles.add(role)
    require(roles == {'Albert', 'independent collaborating agent'}, 'supplement reviews missing')


def require_finished(record):
    require(APPROVED_RECORD_SHA256 is not None, 'pending current hub independent/root approval')
    require(canonical(record) == APPROVED_RECORD_SHA256, 'unreviewed current hub record')
    require(record.get('schema') == 2 and record.get('status') == 'REVIEWED_EXACT_HUB_CONTEXT_SUCCESSOR'
            and record.get('pending') == [], 'unfinished hub context')
    return stamp(record['normalized_at'])


def check_source_contract(pointer, current_manifest):
    # Full-manifest approval remains enforced by manifest(root). The artwork
    # receipt depends only on its exact six source/inverse entries, not Adams CSS.
    require(pointer.get('path') == 'docs/owner-integration-contract/source-manifest.json'
            and pointer.get('binding_scope') == 'EXACT_SIX_EMMA_ENTRIES', 'unknown Emma source contract')
    routes = {HUB, *STORIES}
    require(routes <= set(current_manifest['files']), 'missing current Emma contract entry')
    entries = {route: current_manifest['files'][route] for route in sorted(routes)}
    require(canonical(entries) == pointer.get('emma_entries_sha256'), 'changed Emma source/inverse contract')


def check_spec(root, spec, predecessor, page_dependencies, historical_pages=None):
    # Explicit historical inputs are exact 63fafd predecessor source bytes.
    # Never use them for current ownership or assembled rendering claims.
    historical_pages = historical_pages or {}
    require(set(historical_pages) <= {HUB, *STORIES}, 'unknown historical hub source')
    def source_bound(item):
        if item['path'] not in historical_pages:
            return bound(root, item)
        local(root, item['path'])
        raw = historical_pages[item['path']]
        require(isinstance(raw, bytes) and len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'changed historical hub source')
        return raw
    require(spec.get('registration_class') == 'EXACT_FIVE_EMMA_HUB_CONTEXT_SUCCESSOR', 'unknown hub family')
    for field in ('historical_canonical_preflight_claim', 'new_asset_generation', 'private_reference_bytes_published'):
        require(spec.get(field) is False, 'false hub claim: ' + field)
    require(spec.get('rejection_history_preserved') is True, 'rejection history removed')
    require(spec.get('ride_limit') == predecessor['spec']['ride_limit'], 'hoof limitation changed')
    require(spec.get('inventory') == {'owned_emma': 9, 'owned_christ': 4, 'total_owned': 13, 'hero_reference': 1}, 'false hub inventory')
    require(isinstance(spec.get('owner_scope'), str) and spec['owner_scope'].strip(), 'missing bounded owner scope')
    source_rows = spec['sources']
    routes = {HUB, *STORIES}
    require(len(source_rows) == 6 and {x['path'] for x in source_rows} == routes, 'six current source endpoints required')
    check_source_contract(spec['source_contract'], manifest(root))
    previous_pages = {}
    for item in source_rows:
        route = item['path']
        raw = source_bound(item)
        if route in historical_pages:
            # Confirm both the actual source and its exact explicitly historical
            # projection before running the old historical inverse.
            from owner_journey_successor import historical_fixture
            actual = local(root, route).read_bytes()
            require(historical_fixture(route, actual, root) == raw, 'historical projection mismatch')
            previous = historical_bytes(route, actual, root)
        else:
            validate_file(route, raw, root)
            previous = historical_bytes(route, raw, root)
        if item['path'] in STORIES:
            previous_pages[item['path']] = previous
    expected = []
    for number, old in enumerate(predecessor['spec']['scenes'], 1):
        expected.append({'id': old['id'], 'owner_route': HUB,
                         'owner_fragment': 'picture-emma-story' + str(number) + '-' + old['id'],
                         'reference_route': old['route'],
                         'asset_family_sha256': canonical([old['original'], *old['derivatives']])})
    require(spec['scenes'] == expected, 'asset/owner/reference family changed')
    context = spec['context']
    names = {x['path'] for x in context}
    require(len(names) == len(context) and routes | SCRIPTS <= names, 'missing/duplicate current context')
    for route in routes:
        missing = page_dependencies(root, route) - names
        if missing:
            require(route == HUB and canonical(spec) == SUPPLEMENT_SPEC_SHA256
                    and missing == {item['path'] for item in SUPPLEMENT},
                    'missing current page/CSS context')
            for item in SUPPLEMENT:
                bound(root, item)
            check_supplement_reviews(root)
    for item in context:
        source_bound(item)
    return previous_pages


def check_unique_hub_owners(root):
    """Inspect the actual canonical corpus, not only the changed six pages."""
    locations = {scene: [] for scene in STORIES.values()}
    routes = []
    for node in ET.fromstring(local(root, 'sitemap.xml').read_bytes()).findall('{*}url/{*}loc'):
        url = urlsplit(node.text)
        require(url.scheme == 'https' and url.netloc == 'focuschrist.com' and not url.query and not url.fragment,
                'unknown canonical inventory URL')
        routes.append(url.path.lstrip('/') or 'index.html')
    require(len(routes) == len(set(routes)) == 139 and {HUB, *STORIES} <= set(routes), 'missing/duplicate canonical owner inventory')
    require(sha('\n'.join(sorted(routes)).encode()) == CANONICAL_SET_SHA256, 'changed canonical ownership inventory')
    for route in routes:
        nodes = Document(local(root, route).read_text(encoding='utf-8')).root.walk()
        for node in nodes:
            scene = node.attrs.get('data-exclusive-artwork')
            if scene in locations:
                require(node.tag == 'figure', 'unexpected artwork owner element')
                locations[scene].append(route)
    require(all(paths == [HUB] for paths in locations.values()), 'duplicate/missing hub ownership in canonical corpus')


def check_reflection_capture_evidence(report, artifact, membership):
    """Verify public metadata for private/provider pixels; do not publish rasters."""
    require(membership.get('schema') == 1
            and membership.get('source') == 'VERIFIED_PROVIDER_CAPTURE_MEMBERSHIP'
            and membership.get('member_readback_verified') is True,
            'retained-Christ actual capture membership not verified')
    require(all(membership.get(k) == artifact.get(k) for k in
                ('artifact_id', 'run_id', 'producer_head', 'zip_bytes', 'zip_sha256', 'report')),
            'retained-Christ capture membership artifact/report mismatch')
    expected = {name + '-emma-christ-c' + str(number) + '-context.jpg'
                for name in ('desktop', 'phone') for number in (1, 3, 4, 5)}
    captures = membership.get('captures', [])
    require(len(captures) == 8 and {c.get('archive_member') for c in captures} == expected,
            'retained-Christ capture membership missing/duplicate/unknown')
    for capture in captures:
        shots = [s for s in report.get('screenshots', []) if s.get('file') == capture['archive_member']]
        require(len(shots) == 1 and all(capture.get(k) == shots[0].get(k) for k in ('bytes', 'sha256')),
                'retained-Christ capture member bytes/hash differ from actual raw report')


def check_reflection_rows(report, contract, profile, assets):
    """Require actual retained-Christ context rows, not just five new Emma scenes."""
    name = profile['profile']['name']
    if name not in {'desktop', 'phone'}:
        return
    reflections = contract.get('emma', {}).get('reflections', [])
    require(canonical(reflections) == RETAINED_REFLECTIONS_SHA256,
            'stale retained-Christ source/context contract')
    expected_paths = {'assets/page-art/emma-life/emma-c' + str(c) + '-review-' + str(w) + '.webp'
                      for c in (1, 3, 4, 5) for w in (640, 960, 1536)}
    selected = [assets[p] for p in sorted(expected_paths) if p in assets]
    require(len(selected) == 12 and canonical(selected) == RETAINED_ASSETS_SHA256,
            'retained-Christ approved source bytes changed/missing')
    rows = profile.get('reflectionImages', [])
    require(len(rows) == 4 and [r.get('selector') for r in rows] == [r['selector'] for r in reflections],
            'missing/duplicate/reordered retained-Christ context row')
    width, height, _ = PROFILES[name]
    viewport = {'width': width, 'height': height}
    previous_top = -1
    for row, expected in zip(rows, reflections):
        image = row.get('image', {}); source = expected['image']; context = row.get('context', {})
        path = image.get('src', '').lstrip('/')
        require(path in expected_paths and path.startswith('assets/page-art/emma-life/' + source['key'] + '-review-'),
                'retained-Christ displayed family changed')
        require(image.get('alt') == source['alt'] and image.get('figure') == source['figure'].lstrip('#')
                and image.get('inMain') is True and image.get('dialog') is False
                and image.get('hiddenAncestors') == [] and image.get('centerHit') is True
                and image.get('position') not in {'fixed', 'absolute'}, 'retained-Christ image not visibly in current main flow')
        require(image.get('naturalWidth', 0) > 0 and image.get('naturalHeight', 0) > 0
                and image.get('documentTop', -1) > previous_top, 'retained-Christ decode/order failed')
        previous_top = image['documentTop']
        rect = image.get('rect', {})
        require(image.get('viewport') == viewport and rect.get('width', 0) > 0 and rect.get('height', 0) > 0
                and rect.get('x', -2) >= -1 and rect.get('right', width + 2) <= width + 1
                and rect.get('bottom', 0) > 0 and rect.get('y', height) < height,
                'retained-Christ actual viewport bounds failed')
        require(context.get('heading') == source['heading'] and context.get('sectionId') == source['sectionId']
                and context.get('previousSibling') == source['previousSibling'] and context.get('viewport') == viewport,
                'retained-Christ narrative adjacency/context changed')
        boxes = [context.get('asideRect', {}), context.get('headingRect', {}), *context.get('textRects', [])]
        require(len(boxes) == 3 and all(b.get('width', 0) > 0 and b.get('height', 0) > 0 for b in boxes)
                and row.get('wholeAsideVisibilityNotAssumed') is True,
                'retained-Christ context bounds missing/false whole-aside claim')
        capture = name + '-emma-christ-' + source['key'][-2:] + '-context.jpg'
        shots = [s for s in report.get('screenshots', []) if s.get('file') == capture]
        require(row.get('capture') == capture and len(shots) == 1 and shots[0].get('viewport') == viewport
                and isinstance(shots[0].get('bytes'), int) and 0 < shots[0]['bytes'] <= 1048576
                and re.fullmatch(r'[0-9a-f]{64}', shots[0].get('sha256', '')) is not None,
                'retained-Christ capture missing/duplicate/unbound')
        asset = assets[path]
        require(any(n.get('profile') == name and n.get('path') == '/' + path and n.get('status') == 200
                    and n.get('bytes') == asset['bytes'] and n.get('sha256') == asset['sha256']
                    for n in report['network']), 'retained-Christ actual response bytes/hash missing')


def check_raw_report(report, contract, artifact, spec, predecessor, summary):
    """Read the producer's raw fields, not merely an authored PASS wrapper."""
    require(report.get('pass') is True and report.get('timedOut') is False
            and report.get('errors') == [], 'raw focused report failed/timed out')
    require(contract.get('version') == 1 and contract.get('ready') is True, 'unfinished raw report contract')
    require(report.get('contractSHA256') == summary['qa_contract']['sha256'], 'raw report contract mismatch')
    require(artifact.get('schema') == 1 and artifact.get('source') == 'PROVIDER_ARTIFACT_DOWNLOAD',
            'missing actual downloaded-artifact manifest')
    require(artifact.get('zip_sha256') == summary['artifact_sha256']
            and isinstance(artifact.get('zip_bytes'), int) and artifact['zip_bytes'] > 0,
            'downloaded archive identity mismatch')
    require(str(artifact.get('artifact_id', '')).isdigit() and str(artifact.get('run_id', '')).isdigit(),
            'missing provider artifact/run identity')
    require(artifact.get('producer_head') == summary['producer_head']
            and report.get('producer', {}).get('sha') == summary['producer_head']
            and str(report['producer'].get('run')) == str(artifact['run_id']), 'raw report producer/run mismatch')
    member = artifact.get('report', {})
    require(member.get('archive_member') and not member['archive_member'].startswith('/')
            and '..' not in member['archive_member'].split('/'), 'unsafe/missing raw report archive member')
    require(member.get('bytes') == summary['raw_report']['bytes']
            and member.get('sha256') == summary['raw_report']['sha256'], 'raw report not bound to downloaded archive')
    require(artifact.get('zip_sha256_computed') is True and artifact.get('report_member_readback_verified') is True,
            'download/member verification not established')
    checked = report.get('checked')
    require(isinstance(checked, list) and checked == contract.get('sources', []) + contract.get('assets', []),
            'raw checked input inventory differs from actual contract')
    require(len({x['path'] for x in checked}) == len(checked), 'duplicate raw checked input')
    by_path = {x['path']: x for x in checked}
    for source in spec['sources']:
        require(by_path.get(source['path']) == source, 'raw report current source hash mismatch')
    derivatives = {a['path']: a for scene in predecessor['spec']['scenes'] for a in scene['derivatives']}
    for path, asset in derivatives.items():
        require(by_path.get(path) == {k: asset[k] for k in ('path', 'bytes', 'sha256')},
                'raw report approved image hash mismatch')
    profiles = report.get('profiles', [])
    require(len(profiles) == 4 and {p.get('profile', {}).get('name') for p in profiles} == set(PROFILES),
            'raw report missing/duplicate profile')
    network = report.get('network')
    require(isinstance(network, list), 'raw network evidence missing')
    bases = ['emma-story' + str(n) + '-' + s['id'] + '-review'
             for n, s in enumerate(spec['scenes'], 1)]
    story_contracts = contract.get('emma', {}).get('stories', [])
    require(contract.get('emma', {}).get('route') == '/' + HUB
            and len(story_contracts) == 5 and [s.get('base') for s in story_contracts] == bases,
            'raw contract does not describe current five hub scenes')
    for profile in profiles:
        config = profile['profile']; name = config['name']
        require((config.get('width'), config.get('height'), config.get('touch')) == PROFILES[name],
                'raw viewport profile changed')
        require(profile.get('pass') is True and profile.get('acceptanceErrors') == [] and not profile.get('error'),
                'raw profile failed')
        check_reflection_rows(report, contract, profile, by_path)
        images = profile.get('images', [])
        require(len(images) == 5 and [x.get('base') for x in images] == bases, 'raw profile omitted/reordered hub image')
        previous_top = -1
        for image, scene, base in zip(images, spec['scenes'], bases):
            path = image.get('src', '').lstrip('/')
            require(path in derivatives and any(path == 'assets/page-art/emma-life/' + base + '-' + str(w) + '.webp'
                                                for w in (640, 960, 1536)), 'raw displayed derivative not approved')
            require(image.get('figure') == scene['owner_fragment'] and image.get('inMain') is True
                    and image.get('dialog') is False and image.get('hiddenAncestors') == []
                    and image.get('centerHit') is True and image.get('position') not in {'fixed', 'absolute'},
                    'raw hub image was not visible in normal main flow')
            require(image.get('naturalWidth', 0) > 0 and image.get('naturalHeight', 0) > 0
                    and image.get('documentTop', -1) > previous_top, 'raw image decode/chronology failed')
            previous_top = image['documentTop']
            rect = image.get('rect', {}); viewport = image.get('viewport', {})
            require(rect.get('width', 0) > 0 and rect.get('height', 0) > 0
                    and rect.get('x', -2) >= -1 and rect.get('right', config['width'] + 2) <= config['width'] + 1
                    and rect.get('bottom', 0) > 0 and rect.get('y', config['height']) < config['height']
                    and viewport == {'width': config['width'], 'height': config['height']}, 'raw hub image viewport bounds failed')
            asset = derivatives[path]
            require(any(row.get('profile') == name and row.get('path') == '/' + path and row.get('status') == 200
                        and row.get('bytes') == asset['bytes'] and row.get('sha256') == asset['sha256'] for row in network),
                    'raw image response bytes/hash missing')
        journeys = profile.get('journeys', [])
        for scene, base, story_contract in zip(spec['scenes'], bases, story_contracts):
            matches = [j for j in journeys if j.get('label') == base + '-reference-to-hub']
            require(len(matches) == 1 and matches[0].get('from') == '/' + scene['reference_route']
                    and matches[0].get('to') == '/' + HUB + '#' + scene['owner_fragment'], 'raw reference journey missing/wrong owner')
            if name in {'desktop', 'phone'}:
                full = [j for j in journeys if j.get('label') == base + '-hub-details-fullsize-close']
                require(len(full) == 1 and full[0].get('exactFocusReturned') is True
                        and full[0].get('source') == story_contract.get('sourceHref'), 'raw detail/source/fullsize/focus journey missing')
        if name in {'desktop', 'phone'}:
            for label, art_open, reader_contract in [
                    ('emma-hub-emma-story2-hymnal-review-reader', True, story_contracts[1].get('reader', {})),
                    ('emma-hub-scripture-reflection', False, contract['emma'].get('reader', {}))]:
                reader = [j for j in journeys if j.get('label') == label]
                require(len(reader) == 1 and reader[0].get('exactText') is True
                        and reader[0].get('focusReturned') is True and reader[0].get('artworkRemainedOpen') is art_open,
                        'raw scripture reader/focus journey missing')
                require(reader_contract.get('href') and reader_contract.get('numbers')
                        and reader[0].get('href') == reader_contract['href']
                        and reader[0].get('numbers') == reader_contract['numbers'], 'raw scripture selection/source mismatch')


def check_rendered(root, pointer, spec, predecessor=None):
    require(isinstance(pointer, dict), 'missing actual rendered context')
    rendered = json.loads(bound(root, pointer))
    require(rendered.get('schema') == 1 and rendered.get('status') == 'PASS', 'unfinished rendered context')
    require(rendered.get('spec_sha256') == canonical(spec), 'stale rendered source/spec')
    require(re.fullmatch(r'[0-9a-f]{40}', rendered.get('producer_head', '')) is not None,
            'missing actual producer head')
    require(re.fullmatch(r'[0-9a-f]{64}', rendered.get('artifact_sha256', '')) is not None,
            'missing actual artifact binding')
    require(set(rendered.get('viewports', {})) == {'desktop', 'phone'}, 'both current viewport families required')
    expected = {s['id'] for s in spec['scenes']}
    for value in rendered['viewports'].values():
        require(len(value['scene_ids']) == 5 and set(value['scene_ids']) == expected,
                'render omitted/duplicated integrated scene')
        require(value.get('reference_journeys') is True and value.get('detail_reader_fullsize_focus') is True,
                'current ownership/navigation journeys unfinished')
        require(value.get('evidence'), 'missing actual viewport evidence')
        for item in value['evidence']:
            bound(root, item)
    require(isinstance(predecessor, dict), 'raw artwork predecessor required')
    for key in ('raw_report', 'qa_contract', 'artifact_binding'):
        require(isinstance(rendered.get(key), dict), 'missing actual ' + key)
    report = json.loads(bound(root, rendered['raw_report']))
    contract = json.loads(bound(root, rendered['qa_contract']))
    artifact = json.loads(bound(root, rendered['artifact_binding']))
    check_raw_report(report, contract, artifact, spec, predecessor, rendered)
    require(isinstance(rendered.get('capture_membership'), dict), 'missing actual capture membership metadata')
    membership = json.loads(bound(root, rendered['capture_membership']))
    check_reflection_capture_evidence(report, artifact, membership)
    return pointer['sha256']


def check_reviews(root, record, normalized, rendered_sha):
    reviewers, receipt_paths = set(), set()
    for pointer in record['reviews']:
        require(pointer['path'] not in receipt_paths, 'duplicate current receipt path')
        receipt_paths.add(pointer['path'])
        receipt = json.loads(bound(root, pointer))
        who = receipt.get('reviewer')
        require(who in {'Fermi', 'Newton', 'Albert'} and who not in reviewers, 'missing/duplicate current reviewer')
        require(receipt.get('decision') == 'CONCUR' and receipt.get('withdrawn') is False,
                'negative/withdrawn current review')
        require(receipt.get('spec_sha256') == canonical(record['spec']) and receipt.get('rendered_context_sha256') == rendered_sha,
                'stale current-context review')
        require(stamp(receipt['reviewed_at']) >= normalized, 'backdated current review')
        require(isinstance(receipt.get('actual_author'), str) and receipt['actual_author'].strip(), 'actual reviewer identity missing')
        require(receipt.get('external_worker_action_claimed') is False, 'external worker action not established')
        require(receipt.get('unchanged_source_art_reused') is True and receipt.get('current_placement_inspected') is True,
                'historical art reuse must not impersonate current placement review')
        require(set(receipt.get('checks', {})) == CURRENT_CHECKS
                and all(isinstance(v, str) and v.strip() for v in receipt['checks'].values()), 'missing current observations')
        require(receipt.get('limits') and receipt.get('evidence'), 'missing current evidence/limits')
        for item in receipt['evidence']:
            bound(root, item)
        if who == 'Albert':
            require(set(receipt.get('rendered', {})) == {'desktop', 'phone'}, 'root actual desktop/phone inspection required')
            for item in receipt['rendered'].values():
                bound(root, item)
        reviewers.add(who)
    require(reviewers == {'Fermi', 'Newton', 'Albert'}, 'three genuine current-context reviews required')


def check_supplement_producer(root, pointer):
    rendered = json.loads(bound(root, pointer))
    require(rendered.get('producer_head') == SUPPLEMENT_PRODUCER, 'supplement producer mismatch')


def validate(root, record, added, covered, rejected, pixel_hash, page_dependencies, historical_validate):
    normalized = require_finished(record)
    spec = record['spec']
    pointer = spec['predecessor']
    require(pointer['path'] == PREDECESSOR_PATH and pointer['sha256'] == PREDECESSOR_SHA256,
            'wrong historical ecfb record')
    predecessor = json.loads(bound(root, pointer))
    require(canonical(predecessor) == PREDECESSOR_CANONICAL == pointer['canonical_sha256']
            and canonical(predecessor['spec']) == pointer['spec_sha256'], 'historical record/spec changed')
    previous_pages = check_spec(root, spec, predecessor, page_dependencies)
    check_unique_hub_owners(root)
    rendered_sha = check_rendered(root, record['rendered_context'], spec, predecessor)
    check_supplement_producer(root, record['rendered_context'])
    check_reviews(root, record, normalized, rendered_sha)
    # Every original assertion still runs on the genuine predecessor record and
    # its exact restored five page bytes. Current sources/reviews passed above.
    return historical_validate(root, predecessor, added, covered, rejected,
                               pixel_hash, page_dependencies, previous_pages)


def validate_explicit_historical(root, record, added, covered, rejected, pixel_hash,
                                 page_dependencies, historical_validate, historical_pages):
    """Validate the old receipt and its predecessor as historical evidence only.

    The caller must first validate actual current source and corpus. This function
    does not say the historical rendered report shows today's page.
    """
    from owner_journey_successor import HUB as JHUB, RETIRED, HYMNS
    require(set(historical_pages) == {JHUB, RETIRED, HYMNS}, 'historical inputs incomplete')
    # Independently enforce the actual current boundary even when this explicitly
    # historical entrypoint is called outside the ordinary dispatcher.
    from artwork_emma_journey_retained import validate_current
    validate_current(root)
    def old_dependencies(r, route):
        return page_dependencies(r, route, page_overrides=historical_pages)
    normalized = require_finished(record)
    spec = record['spec']; pointer = spec['predecessor']
    require(pointer['path'] == PREDECESSOR_PATH and pointer['sha256'] == PREDECESSOR_SHA256,
            'wrong historical ecfb record')
    predecessor = json.loads(bound(root, pointer))
    require(canonical(predecessor) == PREDECESSOR_CANONICAL == pointer['canonical_sha256']
            and canonical(predecessor['spec']) == pointer['spec_sha256'], 'historical record/spec changed')
    previous_pages = check_spec(root, spec, predecessor, old_dependencies, historical_pages)
    # Do not call the old 139-page "current" uniqueness census on today's site.
    # The successor validates the actual current 138-route census separately.
    rendered_sha = check_rendered(root, record['rendered_context'], spec, predecessor)
    check_supplement_producer(root, record['rendered_context'])
    check_reviews(root, record, normalized, rendered_sha)
    return historical_validate(root, predecessor, added, covered, rejected, pixel_hash,
                               old_dependencies, previous_pages)
