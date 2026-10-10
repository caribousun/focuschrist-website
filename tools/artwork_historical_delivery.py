"""Private candidate: exact historical/source and delivery coverage, never precreation.

Not wired into the site. The ledger and its independently reviewed binding remain
pending; an incomplete record cannot authorize even partial coverage.
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import PurePosixPath

EXPECTED_COUNTS = {
    **{'Emma-' + name: 4 for name in ('h1', 'h2', 'h3', 'h4', 'h5', 'c1', 'c2', 'c3', 'c4', 'c5')},
    'SITE02': 2, 'SITE04': 1, 'SITE05': 2, 'SITE06': 4, 'SITE13': 4,
}
EXPECTED_AUTHORITY = {
    **{name: 'owner_exception' for name in ('Emma-h2', 'Emma-h3', 'Emma-c2', 'Emma-c3', 'Emma-c4', 'Emma-c5', 'SITE02', 'SITE04')},
    'Emma-h1': 'historical_reconciliation', 'Emma-c1': 'historical_reconciliation',
    'Emma-h4': 'prospective_v2', 'Emma-h5': 'prospective_v2',
    'SITE05': 'reviewed_correction', 'SITE06': 'reviewed_correction', 'SITE13': 'reviewed_correction',
}


def check(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def local(root, name):
    check(isinstance(name, str) and '\\' not in name, 'Noncanonical relative path')
    parts = PurePosixPath(name)
    check(not parts.is_absolute() and '..' not in parts.parts and ':' not in name, 'Unsafe evidence path')
    path = root / name
    check(path.is_file() and not path.is_symlink(), 'Missing or linked evidence')
    check(path.resolve().is_relative_to(root.resolve()), 'Evidence escapes site')
    return path


def evidence(root, item, rejected):
    path = local(root, item['path'])
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    check(actual == item['sha256'] and actual not in rejected, 'Changed or rejected evidence: ' + item['path'])
    return path


def validate(root, record, approved_binding, added, existing_coverage, rejected, pixel_hash):
    """Return paths plus original hashes/pixels for the existing duplicate checks."""
    check(record.get('schema') == 1 and record.get('status') == 'REVIEWED_EXACT_EVIDENCE', 'Coverage ledger remains pending')
    spec = record['spec']
    binding = canonical(spec)
    check(approved_binding is not None and binding == approved_binding, 'Unreviewed coverage ledger binding')
    families = spec['families']
    check(len(families) == len(EXPECTED_COUNTS), 'Wrong family count')
    check({f['id'] for f in families} == set(EXPECTED_COUNTS), 'Wrong or duplicate family set')
    covered, hashes, pixels = set(), set(), set()
    from PIL import Image
    for family in families:
        identity = family['id']
        check(family['authority_kind'] == EXPECTED_AUTHORITY[identity], 'Wrong historical authority type')
        check(family.get('precreation_claim') is (family['authority_kind'] == 'prospective_v2'), 'Misrepresented historical approval')
        source = family['source']
        # Some accepted masters remain in the private evidence archive. A public
        # source-lineage receipt binds their exact digest; do not add the master
        # as a new public raster merely to satisfy the coverage adapter.
        check(isinstance(source.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', source['sha256']) and source['sha256'] not in rejected, 'Invalid source digest')
        evidence(root, source['lineage_receipt'], rejected)
        if source.get('public_asset') is not None:
            evidence(root, {'path': source['public_asset'], 'sha256': source['sha256']}, rejected)
        for item in family['evidence']:
            evidence(root, item, rejected)
        required = {'source_lineage', 'finished_pixels', 'delivery_pixels'}
        check(required <= set(family['evidence_roles']), 'Missing required evidence role')
        for role, indices in family['evidence_roles'].items():
            check(indices and all(type(n) is int and 0 <= n < len(family['evidence']) for n in indices), 'Unbound evidence role ' + role)
        if family['authority_kind'] == 'historical_reconciliation':
            check(family.get('original_full_spec_existed') is False, 'Invented historical full spec')
            check(family.get('material_historical_additions') == [], 'Historical semantic additions')
            audits = family['current_reconciliation_audits']
            check(len(audits) == 2 and len({a['actual_actor'] for a in audits}) == 2, 'Two distinct current reconciliation actors required')
            for audit in audits:
                receipt = json.loads(evidence(root, audit, rejected).read_text(encoding='utf-8'))
                check(receipt['stage'] == 'reconciliation' and receipt['verdict'] == 'PASS' and receipt['withdrawn'] is False, 'Missing actual reconciliation')
                check(receipt['actual_actor'] == audit['actual_actor'], 'Borrowed audit identity')
                check(receipt['frozen_payload_binding'] == family['frozen_payload_binding'], 'Wrong frozen payload audit')
                check(receipt['material_historical_additions'] == [] and receipt['semantic_coverage_verified'] is True, 'Historical audit does not establish exact semantics')
                check(datetime.fromisoformat(receipt['reviewed_at']) >= datetime.fromisoformat(family['frozen_payload_serialized_at']), 'Backdated current reconciliation')
        elif family['authority_kind'] == 'owner_exception':
            check(family['exception_source_sha256'] == source['sha256'], 'Exception covers a different original')
            check(family.get('exception_scope') == 'historical_precreation_evidence_only', 'Expanded owner exception')
            check('direct_owner_exception' in family['evidence_roles'], 'Missing actual owner exception')
        elif family['authority_kind'] == 'prospective_v2':
            check({'prospective_approval', 'generation_result'} <= set(family['evidence_roles']), 'Missing genuine prospective lineage')
        else:
            check({'correction_authorization', 'protected_pixel_result'} <= set(family['evidence_roles']), 'Missing correction lineage')
        assets = family['assets']
        check(len(assets) == EXPECTED_COUNTS[identity], 'Wrong exact family coverage')
        family_hashes, family_pixels = set(), set()
        for item in assets:
            name = item['path']
            check(name in added and name not in covered and name not in existing_coverage, 'Duplicate or non-new raster coverage')
            path = evidence(root, item, rejected)
            check(path.stat().st_size == item['bytes'], 'Wrong asset size')
            check(item['source_sha256'] == source['sha256'], 'Derivative bound to wrong source')
            with Image.open(path) as image:
                check(image.size == (item['width'], item['height']) and image.mode == item['mode'], 'Wrong raster dimensions or mode')
            decoded = pixel_hash(path)
            check(decoded == item['pixel_sha256'], 'Changed decoded pixels')
            family_hashes.add(item['sha256']); family_pixels.add(decoded); covered.add(name)
        check(not (family_hashes & hashes) and not (family_pixels & pixels), 'Duplicate artwork across families')
        hashes |= family_hashes; pixels |= family_pixels
    check(len(covered) == 53, 'Incomplete exact raster coverage')
    return covered, hashes, pixels
