"""Owner-requirement closure for an explicitly reviewed active-consumer scope.

Integrity only: this cannot judge likeness or manufacture owner acceptance.
The gate pins the complete scope/family/objection contract independently of rows.
"""
from datetime import date, datetime
from collections import Counter
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def local(root, name):
    p = Path(name)
    require(not p.is_absolute() and '..' not in p.parts, 'Unsafe closure path')
    resolved = (root / p).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), 'Missing closure file: ' + name)
    return resolved


def bound(root, item):
    p = local(root, item['path'])
    require(hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], 'Stale closure hash: ' + item['path'])
    return p


def references(root, scope, asset_paths, site_origin):
    """Conservative exact path occurrence census, including HTML/JSON/JS/CSS.

    Scope is a reviewed, hash-pinned set, not a lexical Emma search. References
    in comments count too (fail closed). Computed paths/PDFs need explicit
    reviewed resolutions; this does not claim to parse arbitrary JavaScript.
    """
    result = Counter()
    asset_names = {Path(p).name for p in asset_paths}
    for item in scope:
        text = bound(root, item).read_text(encoding='utf-8').replace('\\/', '/')
        for token in re.findall(r'''[^\s\"'<>(),;{}\[\]=]+''', text):
            url = urlsplit(token)
            if url.scheme or url.netloc:
                origin = urlsplit(site_origin)
                if url.scheme not in ('', 'http', 'https') or url.netloc.lower() != origin.netloc.lower() or (url.scheme and url.scheme.lower() != origin.scheme.lower()):
                    continue
            path = unquote(url.path)
            if Path(path).name not in asset_names:
                continue
            # Consumers may be one or more levels below the site root.
            candidate = (root / Path(item['path']).parent / path).resolve() if not path.startswith('/') else (root / path.lstrip('/')).resolve()
            if candidate.is_relative_to(root.resolve()):
                rel = candidate.relative_to(root.resolve()).as_posix()
                if rel in asset_paths:
                    result[(item['path'], rel)] += 1
            # JSON/dynamic maps often store root-relative paths without '/'.
            if path in asset_paths and not (candidate.is_relative_to(root.resolve()) and candidate.relative_to(root.resolve()).as_posix() == path):
                result[(item['path'], path)] += 1
    return result


def validate(root, closure, expected_contract, pixel_hash, final=False):
    require(closure.get('schema') == 1, 'Unknown owner closure schema')
    contract = closure['contract']
    require(canonical(contract) == expected_contract, 'Unreviewed owner closure contract')
    require(contract.get('inventory_complete') is True, 'Consumer classification unresolved')
    require(closure.get('status') == 'agent_reviewed_correction_pending_owner_acceptance' or closure.get('status') == 'owner_accepted', 'Owner closure OPEN')
    require(contract['required_objections'], 'Owner objection history missing')
    require(closure['owner_objections'] == contract['required_objections'], 'Owner objection history changed')
    rows = closure['families']
    require(len(rows) == len(contract['family_ids']) and {r['id'] for r in rows} == set(contract['family_ids']), 'Missing or duplicate Emma family')
    require(len(set(contract['family_ids'])) == len(contract['family_ids']), 'Duplicate required family')
    for item in contract['references'] + contract['exceptions']:
        bound(root, item)
    scope = contract['consumer_scope']
    require(len({x['path'] for x in scope}) == len(scope), 'Duplicate consumer scope')
    all_assets = {}
    expected = Counter()
    for row in rows:
        assets = row['assets']
        require(assets, 'Missing active delivery assets')
        for asset in assets:
            require(asset['path'] not in all_assets, 'Duplicate active asset')
            p = bound(root, asset)
            require(pixel_hash(p) == asset['pixel_sha256'], 'Stale decoded pixels')
            all_assets[asset['path']] = asset
        require(row['source_sha256'] in {x['sha256'] for x in assets}, 'Final source not bound')
        rejected = contract['rejected_by_family'].get(row['id'], [])
        for asset in assets:
            require(not any(asset['sha256'] == x['sha256'] or asset['pixel_sha256'] == x['pixel_sha256'] for x in rejected), 'Owner-rejected active pixels')
        # Each actual consumer/asset pair must be present, no listed phantom rows.
        for c in row['consumers']:
            pair = (c['path'], c['asset'])
            require(c['asset'] in {a['path'] for a in assets} and pair not in expected, 'Invalid or duplicate consumer')
            require(type(c['occurrences']) is int and c['occurrences'] > 0, 'Invalid consumer occurrence count')
            expected[pair] = c['occurrences']
        require(row['consumers'], 'Family has no active consumer')
        if row.get('exempt') is True:
            exemption = [x for x in contract['exception_families'] if x['id'] == row['id']]
            require(len(exemption) == 1, 'Unknown exempt family')
            require({(a['path'], a['sha256']) for a in assets} == {(a['path'], a['sha256']) for a in exemption[0]['assets']}, 'Exception asset set changed')
            require(all(a in contract['exceptions'] for a in exemption[0]['assets']), 'Exception not bound to exact authority')
            # Exact original exemption: still hash/pixel/consumer-bound, but no
            # fabricated new body date or new appearance-review requirement.
            continue
        require(row['id'] not in {x['id'] for x in contract['exception_families']}, 'Exception classification changed')
        body = row['body']
        require(body['status'] in {'pregnant_supported', 'not_pregnant', 'postpartum', 'unknown'}, 'Unknown body status')
        require(type(body['visible_pregnancy']) is bool, 'Missing actual body assessment')
        require(body['scene_date'] and body['findings'].strip(), 'Missing dated body finding')
        if body['visible_pregnancy']:
            require(body['status'] == 'pregnant_supported', 'Visible pregnancy lacks historical authorization')
            require(body['pregnancy_evidence'] and body['dated_relationship'].strip(), 'Missing dated pregnancy evidence')
            timing = body['scene_timing']
            precision = timing['precision']
            require(precision in {'exact', 'interval', 'source_label'}, 'Unknown scene date precision')
            require(timing['label'] == body['scene_date'], 'Scene date label mismatch')
            if precision == 'exact':
                first = last = date.fromisoformat(body['scene_date'])
                require(date.fromisoformat(body['supported_from']) <= first <= date.fromisoformat(body['supported_to']), 'Pregnancy evidence outside scene date')
            elif precision == 'interval':
                first, last = date.fromisoformat(timing['start']), date.fromisoformat(timing['end'])
                require(first <= last and date.fromisoformat(body['supported_from']) <= first and last <= date.fromisoformat(body['supported_to']), 'Pregnancy evidence outside scene interval')
                require(timing['interval_basis'].strip(), 'Missing honest interval basis')
                bound(root, timing['source'])
            else:
                # Historical 'Spring1828' may lack exact endpoints. Require an
                # explicit paired applicability finding for that SAME label;
                # never manufacture month/day endpoints from the season name.
                require(timing['applicability_label'] == body['scene_date'] and timing['applicability_finding'].strip(), 'Pregnancy evidence label mismatch')
                bound(root, timing['source'])
            for item in body['pregnancy_evidence']:
                bound(root, item)
        subject = canonical({k: row[k] for k in ('id', 'source_sha256', 'assets', 'consumers', 'body')})
        reused_display = row.get('appearance_basis') == 'unchanged_assets_reused_display'
        if reused_display:
            preserved = [x for x in contract.get('unchanged_display_families', []) if x['id'] == row['id']]
            require(len(preserved) == 1 and preserved[0]['assets'] == assets, 'Reused display pixels changed')
        reviews = row['reviews']
        require(len(reviews) == 2 and {x['role'] for x in reviews} == {'Fermi', 'Newton'} and len({x['actual_actor'] for x in reviews}) == 2, 'Distinct actual reviewers required')
        for review in reviews + [row['root_review']]:
            require(review['binding_sha256'] == subject and review['verdict'] == 'PASS' and review.get('withdrawn') is False, 'Stale or negative appearance review')
            require(review['actual_actor'].strip() and review['reviewed_at'].strip(), 'Missing actual review attribution')
            require(datetime.fromisoformat(review['reviewed_at'].replace('Z', '+00:00')).tzinfo is not None, 'Review time needs timezone')
            require(review['likeness_findings'].strip() and review['body_findings'].strip(), 'Separate likeness/body findings required')
            require(review['full_native_inspected'] is True, 'Missing actual native inspection')
            if reused_display:
                require(review['display_scale_inspected'] is False and review.get('display_evidence_class') == 'historical_actual_unchanged_pixels', 'Historical display cannot claim new inspection')
                require(review.get('historical_display_inspected') is True and review.get('historical_display_evidence'), 'Missing actual historical display evidence')
                require(review['historical_display_evidence'] == preserved[0]['display_evidence_by_actor'].get(review['actual_actor']), 'Wrong historical display actor or evidence')
                for item in review['historical_display_evidence']:
                    bound(root, item)
            else:
                require(review['display_scale_inspected'] is True, 'Missing actual appearance inspection')
            require(review['reference_binding'] == canonical(contract['references']), 'Wrong identity/body reference')
            require(review['evidence'], 'Missing appearance evidence')
            for item in review['evidence']:
                bound(root, item)
        require(row['root_review']['role'] == 'root' and row['root_review']['actual_actor'] not in {x['actual_actor'] for x in reviews}, 'Root review not distinct')
    require(set(all_assets) <= set(contract['known_asset_paths']), 'Unclassified active asset')
    discovered = references(root, scope, set(contract['known_asset_paths']), contract['site_origin'])
    require(discovered == expected, 'Active consumer closure mismatch')
    # Resolved computed/PDF consumers are separate signed-off evidence, never
    # silently guessed by this literal scanner.
    require(contract['unresolved_consumers'] == [], 'Unresolved computed/PDF consumer')
    for item in contract['nonliteral_resolution_evidence']:
        bound(root, item)
    if closure['status'] == 'owner_accepted':
        require(closure.get('owner_acceptance'), 'Owner acceptance evidence missing')
        acceptance = closure['owner_acceptance']
        require(acceptance['kind'] == 'direct_owner_acceptance' and acceptance['subject_sha256'] == canonical({'families': rows, 'owner_objections': closure['owner_objections']}), 'Owner acceptance bound to different pixels or objections')
        bound(root, acceptance['evidence'])
    if final:
        require(closure['status'] == 'owner_accepted', 'Owner acceptance still pending')
        public = closure['public_closeout']
        require(public['subject_sha256'] == canonical(rows), 'Public evidence predates correction')
        require(public['deployment_commit'] and public['current_consumers'] == sorted([[*x, n] for x, n in expected.items()]), 'Public consumers incomplete')
        require(public['native_evidence'] and public['byte_evidence'], 'Current public evidence missing')
        for item in public['native_evidence'] + public['byte_evidence']:
            bound(root, item)
    return {'owner_requirement_integrity': 'PASS', 'owner_accepted': closure['status'] == 'owner_accepted', 'final': final}
