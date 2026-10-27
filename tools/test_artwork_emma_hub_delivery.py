"""Pending/source/negative contracts only; synthetic receipts are never approval.

Does not execute supplied HTML/JS, launch a browser/server, or contact a network.
The genuine 20-asset positive family and old 15 negatives remain a separate run
after actual current evidence and an independently reviewed approval binding.
"""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import artwork_emma_hub_delivery as hub
import artwork_emma_story_delivery as old

ROOT = Path(__file__).resolve().parents[1]
PENDING_FIXTURE = 'docs/emma-hub-artwork-import/pending-record-fixture.json'
PENDING_FIXTURE_SHA256 = '56d3923e68ea6d39f5dee8f7f7db92fb0fccdd0a677794f69d1a1d0746aaa773'


class EmmaHubContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / PENDING_FIXTURE).read_bytes()
        if old.sha(raw) != PENDING_FIXTURE_SHA256:
            raise AssertionError('Explicit pending negative fixture changed')
        cls.record = json.loads(raw)
        cls.previous = json.loads((ROOT / hub.PREDECESSOR_PATH).read_text())

    def test_explicit_pending_fixture_cannot_pass(self):
        with patch.object(hub, 'APPROVED_RECORD_SHA256', None), self.assertRaises(ValueError):
            hub.require_finished(self.record)

    def test_status_and_missing_approval_both_fail_closed(self):
        record = copy.deepcopy(self.record)
        record.update(status='REVIEWED_EXACT_HUB_CONTEXT_SUCCESSOR', pending=[], normalized_at='2026-10-27T16:00:00+00:00')
        with patch.object(hub, 'APPROVED_RECORD_SHA256', None), self.assertRaises(ValueError):
            hub.require_finished(record)
        with patch.object(hub, 'APPROVED_RECORD_SHA256', old.canonical(self.record)), self.assertRaises(ValueError):
            hub.require_finished(self.record)

    def test_exact_archived_record_and_source_spec(self):
        self.assertEqual(old.sha((ROOT / hub.PREDECESSOR_PATH).read_bytes()), hub.PREDECESSOR_SHA256)
        self.assertEqual(old.canonical(self.previous), hub.PREDECESSOR_CANONICAL)
        pages = hub.check_spec(ROOT, self.record['spec'], self.previous, lambda root, route: {route})
        self.assertEqual(set(pages), set(hub.STORIES))
        for scene in self.previous['spec']['scenes']:
            before = next(x for x in scene['context'] if x['path'] == scene['route'])
            self.assertEqual(old.sha(pages[scene['route']]), before['sha256'])

    def test_current_claim_inventory_and_hoof_mutations_rejected(self):
        cases = [('new_asset_generation', True), ('historical_canonical_preflight_claim', True),
                 ('private_reference_bytes_published', True), ('rejection_history_preserved', False),
                 ('ride_limit', 'All four hooves visible'), ('inventory', {'owned_christ': 7})]
        for key, value in cases:
            spec = copy.deepcopy(self.record['spec']); spec[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                hub.check_spec(ROOT, spec, self.previous, lambda root, route: {route})

    def test_missing_or_duplicate_current_source_rejected(self):
        for mode in ('missing', 'duplicate', 'unknown'):
            spec = copy.deepcopy(self.record['spec'])
            if mode == 'missing': spec['sources'].pop()
            elif mode == 'duplicate': spec['sources'][-1] = spec['sources'][0]
            else: spec['sources'][-1]['path'] = 'unknown.html'
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                hub.check_spec(ROOT, spec, self.previous, lambda root, route: {route})

    def test_changed_current_source_hash_rejected(self):
        spec = copy.deepcopy(self.record['spec']); spec['sources'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            hub.check_spec(ROOT, spec, self.previous, lambda root, route: {route})

    def test_exact_six_entry_dependency_ignores_only_unrelated_adams_change(self):
        current = hub.manifest(ROOT)
        pointer = self.record['spec']['source_contract']
        hub.check_source_contract(pointer, current)
        unrelated = copy.deepcopy(current)
        unrelated['files']['adams-integration.css']['sha256'] = '0' * 64
        hub.check_source_contract(pointer, unrelated)
        # This pure subset test does not waive manifest(root)'s full actual hash
        # validation: independently approved unrelated changes need a new full
        # consumer manifest, but not a new receipt for unchanged Emma context.
        for route in {hub.HUB, *hub.STORIES}:
            changed = copy.deepcopy(current); changed['files'][route]['sha256'] = '0' * 64
            with self.subTest(route=route), self.assertRaises(ValueError):
                hub.check_source_contract(pointer, changed)
        changed = copy.deepcopy(current)
        changed['files'][hub.HUB]['historical']['inverse_spans'][0]['before'] = 'eA=='
        with self.assertRaises(ValueError):
            hub.check_source_contract(pointer, changed)

    def test_changed_asset_owner_reference_family_rejected(self):
        for key, value in [('owner_route', 'history/emma-elect-lady.html'),
                           ('owner_fragment', 'picture-other'), ('reference_route', 'other.html'),
                           ('asset_family_sha256', '0' * 64)]:
            spec = copy.deepcopy(self.record['spec']); spec['scenes'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                hub.check_spec(ROOT, spec, self.previous, lambda root, route: {route})

    def test_missing_duplicate_or_unbound_context_rejected(self):
        for mode in ('script', 'duplicate', 'dependency'):
            spec = copy.deepcopy(self.record['spec'])
            deps = lambda root, route: {route}
            if mode == 'script': spec['context'] = [x for x in spec['context'] if x['path'] != 'site-common.js']
            elif mode == 'duplicate': spec['context'].append(spec['context'][0])
            else: deps = lambda root, route: {route, 'missing-import.css'}
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                hub.check_spec(ROOT, spec, self.previous, deps)

    def test_missing_render_does_not_use_historical_artifact(self):
        with self.assertRaises(ValueError):
            hub.check_rendered(ROOT, None, self.record['spec'])

    def synthetic_render(self):
        return {'schema': 1, 'status': 'PASS', 'spec_sha256': old.canonical(self.record['spec']),
                'producer_head': '1' * 40, 'artifact_sha256': '2' * 64,
                'viewports': {v: {'scene_ids': list(old.SCENES), 'reference_journeys': True,
                                 'detail_reader_fullsize_focus': True,
                                 'evidence': [{'path': 'SYNTHETIC-TEST-NOT-REVIEW', 'bytes': 0, 'sha256': old.sha(b'')}]}
                              for v in ('desktop', 'phone')}}

    def test_render_missing_viewport_scene_journey_or_source_rejected(self):
        for mode in ('viewport', 'scene', 'journey', 'stale', 'producer', 'artifact'):
            value = self.synthetic_render()
            if mode == 'viewport': del value['viewports']['phone']
            elif mode == 'scene': value['viewports']['phone']['scene_ids'].pop()
            elif mode == 'journey': value['viewports']['phone']['reference_journeys'] = False
            elif mode == 'stale': value['spec_sha256'] = '0' * 64
            elif mode == 'producer': value['producer_head'] = ''
            else: value['artifact_sha256'] = ''
            with self.subTest(mode=mode), patch.object(hub, 'bound', return_value=json.dumps(value).encode()), self.assertRaises(ValueError):
                hub.check_rendered(ROOT, {'sha256': '3' * 64}, self.record['spec'])

    def test_empty_current_review_set_rejected(self):
        record = copy.deepcopy(self.record); record['reviews'] = []
        with self.assertRaises(ValueError):
            hub.check_reviews(ROOT, record, old.stamp('2026-10-27T16:00:00+00:00'), '3' * 64)

    def test_current_receipt_negatives_with_explicit_synthetic_baseline(self):
        record = copy.deepcopy(self.record)
        record['reviews'] = [{'path': 'SYNTHETIC-TEST-' + who, 'bytes': 0, 'sha256': '4' * 64}
                             for who in ('Fermi', 'Newton', 'Albert')]
        baseline = {}
        for who in ('Fermi', 'Newton', 'Albert'):
            evidence = {'path': 'SYNTHETIC-EVIDENCE-NOT-REVIEW', 'bytes': 0, 'sha256': old.sha(b'')}
            baseline['SYNTHETIC-TEST-' + who] = {
                'reviewer': who, 'decision': 'CONCUR', 'withdrawn': False,
                'spec_sha256': old.canonical(record['spec']), 'rendered_context_sha256': '3' * 64,
                'reviewed_at': '2026-10-27T16:01:00+00:00', 'actual_author': 'SYNTHETIC UNIT TEST ONLY',
                'external_worker_action_claimed': False, 'unchanged_source_art_reused': True,
                'current_placement_inspected': True, 'checks': {k: 'Synthetic contract input, not observations' for k in hub.CURRENT_CHECKS},
                'limits': ['Never usable as real review evidence'], 'evidence': [evidence],
                'rendered': {'desktop': evidence, 'phone': evidence}}
        normalized = old.stamp('2026-10-27T16:00:00+00:00')
        def payload(values):
            return lambda root, pointer: json.dumps(values[pointer['path']]).encode() if pointer['path'] in values else b''
        with patch.object(hub, 'bound', side_effect=payload(baseline)):
            hub.check_reviews(ROOT, record, normalized, '3' * 64)
        cases = [('decision', 'BLOCK'), ('withdrawn', True), ('spec_sha256', '0' * 64),
                 ('rendered_context_sha256', '0' * 64), ('reviewed_at', '2026-10-27T15:59:00+00:00'),
                 ('actual_author', ''), ('external_worker_action_claimed', True),
                 ('current_placement_inspected', False), ('checks', {}), ('evidence', [])]
        for field, value in cases:
            receipts = copy.deepcopy(baseline);receipts['SYNTHETIC-TEST-Fermi'][field] = value
            with self.subTest(field=field), patch.object(hub, 'bound', side_effect=payload(receipts)), self.assertRaises(ValueError):
                hub.check_reviews(ROOT, record, normalized, '3' * 64)
        receipts = copy.deepcopy(baseline);receipts['SYNTHETIC-TEST-Albert']['rendered'].pop('phone')
        with patch.object(hub, 'bound', side_effect=payload(receipts)), self.assertRaises(ValueError):
            hub.check_reviews(ROOT, record, normalized, '3' * 64)

    def test_duplicate_owner_outside_six_pages_rejected(self):
        # Real sitemap and six current sources; unrelated pages are source-only
        # synthetic no-owner documents for this isolated corpus predicate test.
        sources = {route: (ROOT / route).read_bytes() for route in {hub.HUB, *hub.STORIES}}
        sources['sitemap.xml'] = (ROOT / 'sitemap.xml').read_bytes()
        class Source:
            def __init__(self, raw): self.raw = raw
            def read_bytes(self): return self.raw
            def read_text(self, encoding='utf-8'): return self.raw.decode(encoding)
        def resolve(values): return lambda root, name: Source(values.get(name, b'<html><body></body></html>'))
        with patch.object(hub, 'local', side_effect=resolve(sources)):
            hub.check_unique_hub_owners(ROOT)
        sources['index.html'] = b'<figure data-exclusive-artwork="emma-story1-ride"></figure>'
        with patch.object(hub, 'local', side_effect=resolve(sources)), self.assertRaises(ValueError):
            hub.check_unique_hub_owners(ROOT)

    def test_historical_projection_rejects_unknown_page_before_assets(self):
        with self.assertRaises(ValueError):
            old._validate_historical(ROOT, self.previous, set(), set(), set(), None, None, {'unrelated.html': b'x'})

    def test_historical_projection_rejects_nonbytes_before_assets(self):
        with self.assertRaises(ValueError):
            old._validate_historical(ROOT, self.previous, set(), set(), set(), None, None,
                                     {next(iter(hub.STORIES)): 'not bytes'})

    def test_dispatch_does_not_return_historical_coverage_for_pending(self):
        with patch.object(hub, 'APPROVED_RECORD_SHA256', None), self.assertRaises(ValueError):
            old.validate(ROOT, self.record, set(), set(), set(), None, None)


    def test_pending_fixture_rejects_when_a_different_production_record_is_approved(self):
        with patch.object(hub, 'APPROVED_RECORD_SHA256', 'f' * 64), self.assertRaisesRegex(ValueError, 'unreviewed current hub record'):
            hub.require_finished(self.record)
        # A separate synthetic binding can pass only the preliminary status gate;
        # full validate still requires actual current sources/render/review evidence.
        finished = copy.deepcopy(self.record)
        finished.update(status='REVIEWED_EXACT_HUB_CONTEXT_SUCCESSOR', pending=[], normalized_at='2026-10-27T16:00:00+00:00')
        with patch.object(hub, 'APPROVED_RECORD_SHA256', old.canonical(finished)):
            self.assertEqual(hub.require_finished(finished), old.stamp(finished['normalized_at']))

    def raw_fixture(self):
        # Explicitly synthetic schema fixture, never a finished receipt/artifact.
        spec = self.record['spec']
        assets = [{k: a[k] for k in ('path', 'bytes', 'sha256')}
                  for scene in self.previous['spec']['scenes'] for a in scene['derivatives']]
        bases = ['emma-story' + str(i) + '-' + scene['id'] + '-review' for i, scene in enumerate(spec['scenes'], 1)]
        reader = {'href': 'https://www.churchofjesuschrist.org/study/scriptures/nt/luke/6?lang=eng&id=p12-p16#p12', 'numbers': [12,13,14,15,16]}
        hymn = {'href': 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/25?lang=eng', 'numbers': list(range(1,17))}
        stories = [{'base': base, 'sourceHref': 'https://example.invalid/SYNTHETIC-SOURCE'} for base in bases]
        stories[1]['reader'] = hymn
        contract = {'version': 1, 'ready': True, 'sources': spec['sources'], 'assets': assets,
                    'emma': {'route': '/' + hub.HUB, 'stories': stories, 'reader': reader}}
        summary = {'producer_head': '1'*40, 'artifact_sha256': '2'*64,
                   'qa_contract': {'sha256': '3'*64}, 'raw_report': {'bytes': 123, 'sha256': '4'*64}}
        artifact = {'schema': 1, 'source': 'PROVIDER_ARTIFACT_DOWNLOAD', 'artifact_id': '123', 'run_id': '456',
                    'producer_head': '1'*40, 'zip_bytes': 500, 'zip_sha256': '2'*64,
                    'report': {'archive_member': 'report.json', 'bytes': 123, 'sha256': '4'*64},
                    'zip_sha256_computed': True, 'report_member_readback_verified': True}
        # Frozen real source values; all resulting report/pixel rows below remain
        # explicitly synthetic unit-test data, never a runtime artifact.
        retained = json.loads((ROOT / 'docs/emma-hub-artwork-import/retained-reflection-source-contract.json').read_text())
        contract['emma']['reflections'] = copy.deepcopy(retained['reflections'])
        assets.extend(copy.deepcopy(retained['assets']))
        report = {'pass': True, 'timedOut': False, 'errors': [], 'contractSHA256': '3'*64,
                  'producer': {'sha': '1'*40, 'run': '456'}, 'checked': spec['sources'] + assets, 'profiles': [], 'network': [], 'screenshots': []}
        for name, (width, height, touch) in hub.PROFILES.items():
            profile = {'profile': {'name': name, 'width': width, 'height': height, 'touch': touch},
                       'pass': True, 'acceptanceErrors': [], 'images': [], 'journeys': []}
            for i, (scene, base) in enumerate(zip(spec['scenes'], bases)):
                a = next(a for a in assets if a['path'].endswith(base + '-640.webp'))
                profile['images'].append({'base': base, 'src': '/' + a['path'], 'figure': scene['owner_fragment'],
                    'inMain': True, 'dialog': False, 'hiddenAncestors': [], 'centerHit': True, 'position': 'static',
                    'naturalWidth': 640, 'naturalHeight': 427, 'documentTop': (i+1)*1000,
                    'rect': {'x': 10, 'y': 10, 'right': width-10, 'bottom': 210, 'width': width-20, 'height': 200},
                    'viewport': {'width': width, 'height': height}})
                report['network'].append({'profile': name, 'path': '/' + a['path'], 'status': 200, 'bytes': a['bytes'], 'sha256': a['sha256']})
                profile['journeys'].append({'label': base+'-reference-to-hub', 'from': '/'+scene['reference_route'], 'to': '/'+hub.HUB+'#'+scene['owner_fragment']})
                if name in {'desktop', 'phone'}:
                    profile['journeys'].append({'label': base+'-hub-details-fullsize-close', 'exactFocusReturned': True, 'source': stories[i]['sourceHref']})
            if name in {'desktop', 'phone'}:
                for label, art, data in [('emma-hub-emma-story2-hymnal-review-reader', True, hymn), ('emma-hub-scripture-reflection', False, reader)]:
                    profile['journeys'].append({'label': label, 'exactText': True, 'focusReturned': True, 'artworkRemainedOpen': art, **data})
            profile['reflectionImages'] = []
            if name in {'desktop', 'phone'}:
                for i, reflection in enumerate(contract['emma']['reflections']):
                    source = reflection['image']; asset = next(a for a in assets if a['path'].endswith(source['key']+'-review-640.webp'))
                    box = {'x': 10, 'y': 10, 'right': width-10, 'bottom': 210, 'width': width-20, 'height': 200}
                    viewport = {'width': width, 'height': height}
                    capture = name+'-emma-christ-'+source['key'][-2:]+'-context.jpg'
                    profile['reflectionImages'].append({'selector': reflection['selector'],
                        'image': {'src': '/'+asset['path'], 'alt': source['alt'], 'figure': source['figure'].lstrip('#'),
                                  'inMain': True, 'dialog': False, 'hiddenAncestors': [], 'centerHit': True, 'position': 'static',
                                  'naturalWidth': 640, 'naturalHeight': 427, 'documentTop': (i+1)*1000,
                                  'rect': copy.deepcopy(box), 'viewport': copy.deepcopy(viewport)},
                        'context': {'heading': source['heading'], 'sectionId': source['sectionId'],
                                    'previousSibling': copy.deepcopy(source['previousSibling']),
                                    'asideRect': copy.deepcopy(box), 'headingRect': copy.deepcopy(box),
                                    'textRects': [copy.deepcopy(box)], 'viewport': copy.deepcopy(viewport)},
                        'capture': capture, 'wholeAsideVisibilityNotAssumed': True})
                    report['screenshots'].append({'file': capture, 'bytes': 123, 'sha256': '5'*64, 'viewport': copy.deepcopy(viewport)})
                    report['network'].append({'profile': name, 'path': '/'+asset['path'], 'status': 200,
                                              'bytes': asset['bytes'], 'sha256': asset['sha256']})
            report['profiles'].append(profile)
        return report, contract, artifact, summary

    def check_raw(self, values):
        report, contract, artifact, summary = values
        hub.check_raw_report(report, contract, artifact, self.record['spec'], self.previous, summary)

    def test_explicit_synthetic_raw_schema_positive_only(self):
        self.check_raw(self.raw_fixture())

    def test_raw_failure_timeout_errors_and_profile_mutations_reject(self):
        for mode in ('fail', 'timeout', 'error', 'missing', 'duplicate', 'profilefail', 'acceptance', 'width'):
            values = self.raw_fixture(); report = values[0]
            if mode == 'fail': report['pass'] = False
            elif mode == 'timeout': report['timedOut'] = True
            elif mode == 'error': report['errors'].append('SYNTHETIC ERROR')
            elif mode == 'missing': report['profiles'].pop()
            elif mode == 'duplicate': report['profiles'][-1] = copy.deepcopy(report['profiles'][0])
            elif mode == 'profilefail': report['profiles'][0]['pass'] = False
            elif mode == 'acceptance': report['profiles'][0]['acceptanceErrors'].append('bad geometry')
            else: report['profiles'][0]['profile']['width'] = 1
            with self.subTest(mode=mode), self.assertRaises(ValueError): self.check_raw(values)

    def test_raw_source_image_network_and_journey_mutations_reject(self):
        for mode in ('source', 'image', 'hidden', 'response', 'reference', 'fullsize', 'reader'):
            values = copy.deepcopy(self.raw_fixture()); report = values[0]
            if mode == 'source':
                # Mutate both raw/contract inventories so equality alone cannot pass.
                report['checked'][0]['sha256'] = '0'*64; values[1]['sources'][0]['sha256'] = '0'*64
            elif mode == 'image': report['profiles'][0]['images'].pop()
            elif mode == 'hidden': report['profiles'][0]['images'][0]['hiddenAncestors'] = ['DETAILS']
            elif mode == 'response': report['network'][0]['sha256'] = '0'*64
            elif mode == 'reference': report['profiles'][0]['journeys'][0]['to'] = '/wrong.html'
            elif mode == 'fullsize': report['profiles'][0]['journeys'][1]['exactFocusReturned'] = False
            else: report['profiles'][0]['journeys'][-1]['numbers'] = [1]
            with self.subTest(mode=mode), self.assertRaises(ValueError): self.check_raw(values)

    def test_raw_producer_contract_and_artifact_member_mismatch_reject(self):
        for mode in ('head', 'run', 'contract', 'zip', 'member', 'verified'):
            values = self.raw_fixture(); report, contract, artifact, summary = values
            if mode == 'head': report['producer']['sha'] = '0'*40
            elif mode == 'run': report['producer']['run'] = '999'
            elif mode == 'contract': report['contractSHA256'] = '0'*64
            elif mode == 'zip': artifact['zip_sha256'] = '0'*64
            elif mode == 'member': artifact['report']['sha256'] = '0'*64
            else: artifact['report_member_readback_verified'] = False
            with self.subTest(mode=mode), self.assertRaises(ValueError): self.check_raw(values)


    def test_retained_reflection_missing_duplicate_reordered_rows_reject(self):
        for mode in ('missing', 'duplicate', 'reordered'):
            values = self.raw_fixture(); rows = values[0]['profiles'][0]['reflectionImages']
            if mode == 'missing': rows.pop()
            elif mode == 'duplicate': rows[-1] = copy.deepcopy(rows[0])
            else: rows.reverse()
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'retained-Christ context row'):
                self.check_raw(values)

    def test_retained_reflection_stale_contract_or_asset_reject(self):
        for mode in ('text', 'source', 'alt', 'adjacency', 'asset'):
            values = self.raw_fixture(); contract = values[1]; reflection = contract['emma']['reflections'][0]
            if mode == 'text': reflection['text'] = 'STALE SYNTHETIC COPY'
            elif mode == 'source': reflection['image']['src'] = '/wrong.webp'
            elif mode == 'alt': reflection['image']['alt'] = 'wrong'
            elif mode == 'adjacency': reflection['image']['previousSibling']['text'] = 'wrong'
            else:
                for a in contract['assets']:
                    if 'emma-c1-review-640.webp' in a['path']: a['sha256'] = '0' * 64
                values[0]['checked'] = contract['sources'] + contract['assets']
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'retained-Christ'):
                self.check_raw(values)

    def test_retained_reflection_failed_visibility_or_context_reject(self):
        for mode in ('hidden', 'decode', 'alt', 'heading', 'adjacency', 'box', 'claim'):
            values = self.raw_fixture(); row = values[0]['profiles'][1]['reflectionImages'][0]
            if mode == 'hidden': row['image']['hiddenAncestors'] = ['DETAILS']
            elif mode == 'decode': row['image']['naturalWidth'] = 0
            elif mode == 'alt': row['image']['alt'] = 'wrong'
            elif mode == 'heading': row['context']['heading'] = 'wrong'
            elif mode == 'adjacency': row['context']['previousSibling']['text'] = 'wrong'
            elif mode == 'box': row['context']['textRects'] = []
            else: row['wholeAsideVisibilityNotAssumed'] = False
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'retained-Christ'):
                self.check_raw(values)

    def test_retained_reflection_missing_duplicate_stale_capture_reject(self):
        for mode in ('missing', 'duplicate', 'viewport', 'name', 'hash'):
            values = self.raw_fixture(); report = values[0]
            if mode == 'missing': report['screenshots'].pop(0)
            elif mode == 'duplicate': report['screenshots'].append(copy.deepcopy(report['screenshots'][0]))
            elif mode == 'viewport': report['screenshots'][0]['viewport']['width'] = 1
            elif mode == 'name': report['profiles'][0]['reflectionImages'][0]['capture'] = 'wrong.jpg'
            else: report['screenshots'][0]['sha256'] = ''
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'retained-Christ capture'):
                self.check_raw(values)

    def test_retained_reflection_missing_or_changed_response_hash_reject(self):
        for mode in ('missing', 'hash', 'status'):
            values = self.raw_fixture(); report = values[0]
            row = next(n for n in report['network'] if n['profile'] == 'phone' and 'emma-c1-' in n['path'])
            if mode == 'missing': report['network'].remove(row)
            elif mode == 'hash': row['sha256'] = '0' * 64
            else: row['status'] = 404
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'retained-Christ actual response'):
                self.check_raw(values)

    def test_retained_reflection_capture_membership_metadata_is_bound(self):
        report, contract, artifact, summary = self.raw_fixture()
        # Synthetic manifest only: no actual provider/member verification claim.
        membership = {'schema': 1, 'source': 'VERIFIED_PROVIDER_CAPTURE_MEMBERSHIP',
                      'member_readback_verified': True,
                      **{k: copy.deepcopy(artifact[k]) for k in
                         ('artifact_id', 'run_id', 'producer_head', 'zip_bytes', 'zip_sha256', 'report')},
                      'captures': [{'archive_member': s['file'], 'bytes': s['bytes'], 'sha256': s['sha256']}
                                   for s in report['screenshots']]}
        hub.check_reflection_capture_evidence(report, artifact, membership)
        for mode in ('missing', 'duplicate', 'unknown', 'bytes', 'hash', 'artifact', 'report', 'unverified'):
            changed = copy.deepcopy(membership); captures = changed['captures']
            if mode == 'missing': captures.pop()
            elif mode == 'duplicate': captures[-1] = copy.deepcopy(captures[0])
            elif mode == 'unknown': captures[0]['archive_member'] = '../wrong.jpg'
            elif mode == 'bytes': captures[0]['bytes'] += 1
            elif mode == 'hash': captures[0]['sha256'] = '0' * 64
            elif mode == 'artifact': changed['artifact_id'] = '999'
            elif mode == 'report': changed['report']['sha256'] = '0' * 64
            else: changed['member_readback_verified'] = False
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'retained-Christ'):
                hub.check_reflection_capture_evidence(report, artifact, changed)


if __name__ == '__main__':
    unittest.main()
