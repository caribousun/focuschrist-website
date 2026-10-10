"""Validate exact reviewed local corrections without rewriting frozen history.

The approved binding is supplied by the independently reviewed gate. New families
require a new exact ledger binding; no directory or automatic family allowance.
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import PurePosixPath

KINDS = {'original', 'generated_donor', 'masked_composite', 'color_adjustment'}
STAGES = {'owner_scope', 'donor_preflight', 'donor_result', 'composite_preflight',
          'composite_result', 'body_finished', 'color_preflight', 'color_result',
          'source_finished', 'encoding_preflight', 'encoding_result', 'delivery_finished'}
REVIEW_STAGES = {'donor_preflight', 'composite_preflight', 'body_finished',
                 'color_preflight', 'source_finished', 'encoding_preflight', 'delivery_finished'}
FINISHED_STAGES = {'body_finished', 'source_finished', 'delivery_finished'}

def check(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sha(value):
    check(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value), 'Invalid digest')
    return value

def local(root, name):
    check(isinstance(name, str) and name and '\\' not in name and ':' not in name, 'Noncanonical correction path')
    p = PurePosixPath(name)
    check(not p.is_absolute() and '..' not in p.parts and str(p) == name, 'Unsafe correction path')
    path = root / name
    check(path.is_file() and path.resolve().is_relative_to(root.resolve()), 'Missing or escaping correction file')
    check(not any(q.is_symlink() for q in [path, *path.parents] if q != root.parent), 'Linked correction file')
    return path

def evidence(root, item, rejected):
    path = local(root, item['path'])
    check(digest(path) == sha(item['sha256']) and item['sha256'] not in rejected, 'Changed or rejected correction evidence')
    return path

def stamp(value):
    check(isinstance(value, str), 'Missing recorded review date')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    check(dt.tzinfo is not None, 'Review date must include timezone')
    return dt

def safe_public(value):
    text = json.dumps(value, ensure_ascii=False)
    check(not re.search(r'(?i)(\b[a-z]:[\\/]|file://|/Users/|\\\\Users\\\\|docs.google.com/document/d/)', text), 'Private path or authority document in public receipt')

def validate(root, record, approved_binding, added, existing_coverage, rejected, pixel_hash, baseline_inventory):
    check(record.get('schema') == 1 and record.get('status') == 'REVIEWED_EXACT_EVIDENCE', 'Correction ledger pending')
    spec = record['spec']
    check(approved_binding is not None and canonical(spec) == approved_binding == record.get('approved_binding'), 'Unapproved correction binding')
    check(spec.get('kind') == 'reviewed_local_corrections' and spec.get('precreation_claim') is False, 'Incorrect correction authority claim')
    safe_public(record)
    families = spec['families']
    check(isinstance(families, list) and families, 'Empty correction coverage')
    ids = [f['id'] for f in families]
    check(len(set(ids)) == len(ids), 'Duplicate correction family')
    covered, hashes, pixels = set(), set(), set()
    receipt_ids = set()
    validated_families = {}
    expression_kinds = {'reviewed_prior_source', 'expression_donor', 'expression_composite'}
    expression_stages = {'owner_scope', 'expression_donor_preflight', 'expression_donor_result',
                         'expression_composite_preflight', 'expression_composite_result',
                         'source_finished', 'encoding_preflight', 'encoding_result', 'delivery_finished'}
    identity_ids = {'SITE01_IDENTITY': 'SITE01', 'SITE02_IDENTITY': 'SITE02', 'SITE05_IDENTITY': 'SITE05'}
    identity_kinds = {'reviewed_existing_source', 'generated_neutral_intermediate', 'generated_identity_fill'}
    identity_stages = {'owner_scope', 'neutral_preflight', 'neutral_result', 'identity_preflight',
                       'identity_result', 'source_finished', 'encoding_preflight', 'encoding_result', 'delivery_finished'}
    from PIL import Image
    for family in families:
        check(family.get('authority_kind') == 'reviewed_local_correction' and family.get('precreation_claim') is False, 'Invented canonical precreation')
        identity = family['id']
        expression = identity == 'SITE07_EXPRESSION'
        identity_fill = identity in identity_ids
        if identity_fill:
            check(family.get('immutable_originals', []) == [], 'Identity prior is not a new immutable-original declaration')
            scene = identity_ids[identity]
            check(family.get('scene_family_id') == scene, 'Wrong identity scene')
            if scene == 'SITE01':
                prior = validated_families.get(scene)
                check(family.get('prior_kind') == 'reviewed_correction', 'Wrong identity prior class')
            else:
                check(family.get('prior_kind') == 'historical_delivery', 'Wrong identity prior class')
                # This registry has already passed the existing historical adapter.
                historical = json.loads((root / 'docs/artwork-historical-delivery-reviews.json').read_text(encoding='utf-8'))
                matches = [f for f in historical['spec']['families'] if f['id'] == scene]
                check(len(matches) == 1, 'Missing historical identity source')
                prior = matches[0]
            check(prior is not None and family.get('prior_record_id') == scene and canonical(prior) == family.get('prior_record_sha256'), 'Missing or changed identity prior record')
            expected_preserved = [{'path': a['path'], 'sha256': a['sha256']} for a in prior['assets']]
            check(family['preserved_assets'] == expected_preserved, 'Identity preservation set changed')
            for a in family['preserved_assets']:
                check(a['path'] in existing_coverage or a['path'] in covered, 'Identity source lacks prior reviewed coverage')
                evidence(root, a, rejected)
            check(family['prior_source'] in expected_preserved, 'Identity input is not preserved prior asset')
            refs = family['identity_references']
            check(refs == [
                {'path': 'assets/identities/emma-smith-owner-approved-20260930.png', 'sha256': '7d0a07cc673d244ccd54d478c53d1e68d248e39d9b1101f87dfe3681cbb839d1'},
                {'path': 'assets/page-art/emma-life/emma-h4-review.png', 'sha256': '24e0b13c84cabae92c972034f1fc775162b2800a93e4b14d876ca16c31a269ea'},
                {'path': 'assets/identities/emma-smith-approved-gentle-smile-20260930.png', 'sha256': 'f6d2493babf5d2ab7a6e118a57827f7db05e6aea934feb5739256987ec186688'},
            ], 'Wrong approved identity references or order')
            for a in refs: evidence(root, a, rejected)
        if expression:
            check(family.get('scene_family_id') == 'SITE07' and family.get('prior_record_id') == 'SITE07', 'Wrong expression scene or prior record')
            prior = validated_families.get('SITE07')
            check(prior is not None and canonical(prior) == family.get('prior_record_sha256'), 'Missing or changed reviewed prior record')
            prior_final = next(n for n in prior['lineage'] if n['id'] == prior['final_source_id'])
            check(prior_final['kind'] == 'masked_composite', 'Expression prior must be accepted body composite')
        check(re.fullmatch(r'[A-Za-z0-9_-]+', identity), 'Invalid correction identity')
        actors = family['current_reviewers']
        check(set(actors) == {'executor', 'independent', 'root'} and len(set(actors.values())) == 3, 'Three distinct current actors required')
        check(all(isinstance(a, str) and a.strip() for a in actors.values()), 'Missing actor identity')
        originals = [] if identity_fill else family['immutable_originals']
        check(identity_fill or (originals and len({x['path'] for x in originals}) == len(originals)), 'Missing or duplicate originals')
        for item in originals:
            check(item['path'] in baseline_inventory, 'Correction source is not immutable baseline')
            evidence(root, item, rejected)
        if expression:
            check(originals == prior['immutable_originals'], 'Expression immutable baseline differs from prior record')
        nodes = family['lineage']
        check(nodes and len({n['id'] for n in nodes}) == len(nodes), 'Duplicate lineage identity')
        indexed = {}; node_hashes = set()
        excluded = set(family['excluded_pixel_ancestors'])
        check(all(sha(x) for x in excluded), 'Invalid excluded ancestry')
        for node in nodes:
            check(node['kind'] in (identity_kinds if identity_fill else expression_kinds if expression else KINDS) and node['id'] not in indexed, 'Invalid lineage kind')
            h = sha(node['sha256'])
            check(h not in rejected and h not in excluded and h not in node_hashes, 'Rejected or duplicate pixel ancestor')
            parents = node['parents']
            check(isinstance(parents, list) and len(set(parents)) == len(parents) and all(p in indexed for p in parents), 'Unordered, missing or duplicate lineage parent')
            if identity_fill:
                if node['kind'] == 'reviewed_existing_source':
                    check(not parents and h == family['prior_source']['sha256'], 'Wrong identity prior pixels')
                elif node['kind'] == 'generated_neutral_intermediate':
                    check(len(parents) == 1 and indexed[parents[0]]['kind'] == 'reviewed_existing_source', 'Wrong neutral input ancestry')
                else:
                    check(len(parents) == 1 and indexed[parents[0]]['kind'] == 'generated_neutral_intermediate', 'Identity fill must use exact neutral input')
            elif expression:
                if node['kind'] == 'reviewed_prior_source':
                    check(not parents and h == prior_final['sha256'], 'Wrong reviewed prior source')
                elif node['kind'] == 'expression_donor':
                    check(len(parents) == 1 and indexed[parents[0]]['kind'] == 'reviewed_prior_source', 'Expression donor reference differs from accepted body')
                else:
                    check(len(parents) == 2 and {indexed[p]['kind'] for p in parents} == {'reviewed_prior_source', 'expression_donor'}, 'Wrong expression composite ancestry')
            elif node['kind'] == 'original':
                check(not parents and h in {x['sha256'] for x in originals}, 'Wrong immutable original')
            elif node['kind'] == 'generated_donor':
                check(len(parents) == 1 and indexed[parents[0]]['kind'] == 'original', 'Donor reference is not original')
            elif node['kind'] == 'masked_composite':
                check(len(parents) == 2 and {indexed[p]['kind'] for p in parents} == {'original', 'generated_donor'}, 'Wrong body composite ancestry')
            else:
                check(len(parents) == 1 and indexed[parents[0]]['kind'] == 'masked_composite', 'Color adjustment must preserve accepted body source')
            indexed[node['id']] = node; node_hashes.add(h)
        final = indexed[family['final_source_id']]
        body = indexed[family['body_source_id']]
        if identity_fill:
            check(body['kind'] == 'reviewed_existing_source' and final['kind'] == 'generated_identity_fill', 'Invalid identity final source')
        elif expression:
            check(body['kind'] == 'reviewed_prior_source' and final['kind'] == 'expression_composite', 'Invalid expression final source')
        else:
            check(body['kind'] == 'masked_composite' and final['kind'] in {'masked_composite', 'color_adjustment'}, 'Invalid final correction source')
        expected_kinds = sorted(identity_kinds) if identity_fill else sorted(expression_kinds) if expression else ['original', 'generated_donor', 'masked_composite'] + (['color_adjustment'] if final['kind'] == 'color_adjustment' else [])
        check(sorted(n['kind'] for n in nodes) == sorted(expected_kinds), 'Disconnected or extra correction lineage')
        donor_result = 'neutral_result' if identity_fill else 'expression_donor_result' if expression else 'donor_result'
        donor_preflight = 'neutral_preflight' if identity_fill else 'expression_donor_preflight' if expression else 'donor_preflight'
        composite_result = 'identity_result' if identity_fill else 'expression_composite_result' if expression else 'composite_result'
        composite_preflight = 'identity_preflight' if identity_fill else 'expression_composite_preflight' if expression else 'composite_preflight'
        donor_node = next(n for n in nodes if n['kind'] == ('generated_neutral_intermediate' if identity_fill else 'expression_donor' if expression else 'generated_donor'))
        check(family['stage_subjects'][donor_result] == donor_node['sha256'], 'Donor result differs from pixel ancestor')
        required = identity_stages if identity_fill else expression_stages if expression else STAGES if final['kind'] == 'color_adjustment' else STAGES - {'color_preflight', 'color_result'}
        review_stages = {s for s in required if s.endswith(('preflight', 'finished'))}
        receipts = family['evidence']
        by_stage = {s: [] for s in required}
        for item in receipts:
            receipt = json.loads(evidence(root, item, rejected).read_text(encoding='utf-8'))
            safe_public(receipt)
            check(receipt.get('schema') == 1 and receipt.get('family') == identity, 'Borrowed correction evidence')
            check(receipt['id'] not in receipt_ids, 'Reused correction receipt')
            receipt_ids.add(receipt['id'])
            stage = receipt['stage']
            check(stage in required and receipt.get('withdrawn') is False, 'Wrong or withdrawn stage')
            check(receipt.get('actual_actor') == item['actual_actor'] and receipt.get('stage') == item['stage'], 'Borrowed actor or stage')
            sha(receipt['source_report_sha256'])
            stamp(receipt['normalized_at'])
            # Source records without timestamps stay explicitly undated. The
            # normalization date is never substituted for historical event time.
            if receipt['source_recorded_at'] is not None:
                stamp(receipt['source_recorded_at'])
            check(isinstance(receipt['findings'], str) and receipt['findings'].strip(), 'Empty functional findings')
            check(receipt['subject_sha256'] == family['stage_subjects'][stage], 'Review bound to wrong stage source')
            sha(receipt['subject_sha256'])
            if stage in review_stages:
                check(receipt['verdict'] == 'CONCUR', 'Missing actual stage concurrence')
            if stage in FINISHED_STAGES:
                check(receipt.get('pixels_inspected') is True and receipt['actual_actor'] in actors.values(), 'Missing current actual pixel reviewer')
            by_stage[stage].append(receipt)
        check(set(family['stage_subjects']) == required and all(by_stage.values()), 'Missing correction evidence stage')
        check(family['stage_subjects']['source_finished'] == final['sha256'], 'Wrong finished source binding')
        if not expression and not identity_fill:
            check(family['stage_subjects']['body_finished'] == body['sha256'], 'Wrong finished body binding')
        check(family['stage_subjects'][composite_result] == (final if expression or identity_fill else body)['sha256'], 'Wrong composite execution result')
        for result in by_stage[donor_result]:
            check(result['spec_sha256'] == family['stage_subjects'][donor_preflight], 'Donor execution differs from reviewed specification')
        for result in by_stage['encoding_result']:
            check(result['spec_sha256'] == family['stage_subjects']['encoding_preflight'], 'Encoding execution differs from reviewed specification')
        if identity_fill:
            for result in by_stage[donor_result]:
                check(result['tool'] == 'image_gen.imagegen' and result['input_sha256'] == [family['prior_source']['sha256']], 'Wrong actual neutral generation inputs')
            for result in by_stage[composite_result]:
                check(result['spec_sha256'] == family['stage_subjects'][composite_preflight], 'Identity execution differs from reviewed specification')
                check(result['tool'] == 'image_gen.imagegen' and result['input_sha256'] == [a['sha256'] for a in family['identity_references']] + [donor_node['sha256']], 'Wrong actual identity generation inputs')
                check(result.get('preservation_basis') == 'actual_finished_visual_review_not_pixel_equality' and 'protected_pixel_checks' not in result, 'Invented identity pixel equality')
        for result in ([] if identity_fill else by_stage[composite_result]):
            if expression:
                check(result['spec_sha256'] == family['stage_subjects'][composite_preflight], 'Expression execution differs from reviewed specification')
            proof = result['protected_pixel_checks']
            check(type(proof['changed_pixels']) is int and proof['changed_pixels'] > 0 and proof['outside_changed_pixels'] == 0 and proof['protected_changed_pixels'] == 0, 'Body protection proof failed')
        if final['kind'] == 'color_adjustment':
            check(family['stage_subjects']['color_result'] == final['sha256'], 'Wrong color execution result')
            for result in by_stage['color_result']:
                proof = result['protected_pixel_checks']
                check(type(proof['changed_pixels']) is int and proof['changed_pixels'] > 0 and proof['outside_changed_pixels'] == 0 and proof['accepted_body_changed_pixels'] == 0, 'Color protection proof failed')
        for stage in review_stages:
            people = {r['actual_actor'] for r in by_stage[stage]}
            check(len(people) >= 2, 'Paired actual review missing')
            if stage in FINISHED_STAGES:
                check(people == set(actors.values()), 'Missing current finished pixel reviewer')
        assets = family['assets']
        check(len(assets) >= 2 and len({a['path'] for a in assets}) == len(assets), 'Invalid correction delivery set')
        check(set(family['asset_allowlist']) == {a['path'] for a in assets} and len(family['asset_allowlist']) == len(assets), 'Incorrect exact asset allowlist')
        check(family['stage_subjects']['delivery_finished'] == canonical(assets), 'Delivery reviews are not bound to exact asset set')
        original_assets = [a for a in assets if a['role'] == 'source']
        check(len(original_assets) == 1 and original_assets[0]['sha256'] == final['sha256'] and original_assets[0]['format'] == 'PNG', 'Wrong final lossless source')
        family_hashes, family_pixels = set(), set()
        for item in assets:
            name = item['path']
            check(name in added and name not in covered and name not in existing_coverage and name not in baseline_inventory, 'Overlapping or non-new correction coverage')
            check(item['source_sha256'] == final['sha256'], 'Wrong derivative source')
            check(item['role'] in {'source', 'derivative'} and (item['role'] == 'source' or item['format'] == 'WEBP'), 'Invalid delivery role or format')
            check(PurePosixPath(name).suffix == { 'PNG': '.png', 'WEBP': '.webp' }[item['format']], 'Wrong delivery file extension')
            path = evidence(root, item, rejected)
            check(path.stat().st_size == item['bytes'], 'Wrong correction file size')
            with Image.open(path) as im:
                check(getattr(im, 'n_frames', 1) == 1 and im.mode == item['mode'] == 'RGB', 'Invalid correction pixel mode')
                check(list(im.size) == item['dimensions'] and im.format == item['format'], 'Wrong correction dimensions or format')
            pixel = pixel_hash(path)
            check(pixel == item['pixel_sha256'], 'Wrong decoded correction pixels')
            check(item['sha256'] not in family_hashes and pixel not in family_pixels, 'Duplicate delivery pixels or bytes')
            family_hashes.add(item['sha256']); family_pixels.add(pixel); covered.add(name)
        check(not family_hashes & hashes and not family_pixels & pixels, 'Duplicate correction families')
        hashes |= family_hashes; pixels |= family_pixels
        validated_families[identity] = family
    if 'SITE07_EXPRESSION' in validated_families:
        expected = {'SITE01': 'SITE01', 'SITE07': 'SITE07_EXPRESSION', 'SITE08': 'SITE08',
                    'SITE09': 'SITE09', 'SITE10': 'SITE10', 'SITE11': 'SITE11', 'SITE12': 'SITE12'}
        original_records = {'SITE01', 'SITE07', 'SITE07_EXPRESSION', 'SITE08', 'SITE09', 'SITE10', 'SITE11', 'SITE12'}
        present_identity = set(validated_families) & set(identity_ids)
        check(not present_identity or present_identity == set(identity_ids), 'Incomplete exact identity batch')
        if present_identity:
            expected.update({scene: version for version, scene in identity_ids.items()})
        check(set(validated_families) == original_records | present_identity, 'Wrong exact successor record set')
        check(spec.get('current_scene_records') == expected, 'Wrong exact current scene mapping')
    else:
        check('current_scene_records' not in spec, 'Current scene mapping requires reviewed successor')
    return covered, hashes, pixels
