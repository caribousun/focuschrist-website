"""Isolated synthetic integrity fixtures; no real pixel/owner acceptance claims."""
import copy
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from collections import Counter
from unittest.mock import patch
from artwork_owner_closure import canonical, validate, references


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, data in {'new.webp': b'new', 'old.webp': b'owner failed', 'ref.png': b'reference', 'proof.json': b'actual fixture evidence', 'index.html': b'<img src="new.webp">', 'church.html': b'<img src="new.webp">'}.items():
            (self.root/name).write_bytes(data)
        self.asset = dict(self.file('new.webp'), pixel_sha256=self.pixel(self.root/'new.webp'))
        self.contract = {'inventory_complete': True, 'site_origin':'https://focuschrist.com', 'exception_families':[], 'family_ids': ['SITE05'], 'references': [self.file('ref.png')], 'exceptions': [], 'required_objections': [{'id':'owner03','scope':'SITE05'}], 'consumer_scope': [self.file('index.html'), self.file('church.html')], 'known_asset_paths': ['new.webp', 'old.webp'], 'rejected_by_family': {'SITE05':[dict(self.file('old.webp'),pixel_sha256=self.pixel(self.root/'old.webp'))]}, 'unresolved_consumers': [], 'nonliteral_resolution_evidence': []}
        row={'id':'SITE05','source_sha256':self.asset['sha256'],'assets':[self.asset], 'consumers':[{'path':'index.html','asset':'new.webp','occurrences':1},{'path':'church.html','asset':'new.webp','occurrences':1}], 'body':{'status':'not_pregnant','visible_pregnancy':False,'scene_date':'1842-03-17','findings':'Actual body fixture finding','pregnancy_evidence':[],'dated_relationship':''}}
        self.data={'schema':1,'status':'agent_reviewed_correction_pending_owner_acceptance','contract':self.contract,'owner_objections':copy.deepcopy(self.contract['required_objections']),'families':[row]}
        self.reviews()

    def file(self,name):
        return {'path':name,'sha256':hashlib.sha256((self.root/name).read_bytes()).hexdigest()}

    @staticmethod
    def pixel(path):
        return hashlib.sha256(b'decoded-fixture:'+path.read_bytes()).hexdigest()

    def reviews(self):
        r=self.data['families'][0]
        binding=canonical({k:r[k] for k in ('id','source_sha256','assets','consumers','body')})
        def review(role,actor):
            return {'role':role,'actual_actor':actor,'binding_sha256':binding,'verdict':'PASS','withdrawn':False,'reviewed_at':'2026-10-10T14:00:00Z','likeness_findings':'Synthetic exact likeness fixture finding','body_findings':'Synthetic independent body fixture finding','full_native_inspected':True,'display_scale_inspected':True,'reference_binding':canonical(self.contract['references']),'evidence':[self.file('proof.json')]}
        r['reviews']=[review('Fermi','actor-f'),review('Newton','actor-n')];r['root_review']=review('root','actor-r')

    def run_gate(self,final=False):
        return validate(self.root,self.data,canonical(self.contract),self.pixel,final)

    def rejects(self,message):
        with self.assertRaisesRegex(ValueError,message): self.run_gate()

    def test_exact_synthetic_local_pass_not_owner_acceptance(self):
        self.assertFalse(self.run_gate()['owner_accepted'])

    def test_original_failed_card_cannot_pass_even_rebound_reviews(self):
        r=self.data['families'][0];r['assets']=[dict(self.file('old.webp'),pixel_sha256=self.pixel(self.root/'old.webp'))];r['source_sha256']=r['assets'][0]['sha256'];self.reviews();self.rejects('Owner-rejected active pixels')

    def test_renamed_rejected_pixels_fail(self):
        (self.root/'new.webp').write_bytes((self.root/'old.webp').read_bytes());r=self.data['families'][0];r['assets']=[dict(self.file('new.webp'),pixel_sha256=self.pixel(self.root/'new.webp'))];r['source_sha256']=r['assets'][0]['sha256'];self.reviews();self.rejects('Owner-rejected active pixels')

    def test_missing_homepage_consumer(self):
        self.data['families'][0]['consumers'].pop(0);self.reviews();self.rejects('Active consumer closure mismatch')

    def test_hidden_old_card_discovered(self):
        (self.root/'index.html').write_text('<img src="old.webp">');self.contract['consumer_scope'][0]=self.file('index.html');self.rejects('Active consumer closure mismatch')

    def test_stale_asset(self):
        (self.root/'new.webp').write_bytes(b'changed');self.rejects('Stale closure hash')

    def test_duplicate_actual_actor(self):
        self.data['families'][0]['reviews'][1]['actual_actor']='actor-f';self.rejects('Distinct actual reviewers')

    def test_no_likeness_finding(self):
        self.data['families'][0]['reviews'][0]['likeness_findings']='';self.rejects('Separate likeness/body')

    def test_open_owner_objection(self):
        self.data['status']='OPEN';self.rejects('Owner closure OPEN')

    def test_objection_deleted(self):
        self.data['owner_objections']=[];self.rejects('Owner objection history changed')

    def test_exception_change_requires_new_reviewed_contract(self):
        binding=canonical(self.contract);self.contract['exceptions']=[self.file('new.webp')]
        with self.assertRaisesRegex(ValueError,'Unreviewed owner closure contract'):validate(self.root,self.data,binding,self.pixel)

    def test_unknown_or_postpartum_does_not_authorize_pregnancy(self):
        for status in ('unknown','postpartum'):
            with self.subTest(status=status):
                b=self.data['families'][0]['body'];b.update(status=status,visible_pregnancy=True);self.reviews();self.rejects('Visible pregnancy lacks')

    def test_outside_pregnancy_dates(self):
        b=self.data['families'][0]['body'];b.update(status='pregnant_supported',visible_pregnancy=True,pregnancy_evidence=[self.file('proof.json')],dated_relationship='Bound dated source',supported_from='1843-01-01',supported_to='1843-09-01',scene_timing={'precision':'exact','label':b['scene_date']});self.reviews();self.rejects('Pregnancy evidence outside')

    def test_supported_pregnancy_structure(self):
        b=self.data['families'][0]['body'];b.update(status='pregnant_supported',visible_pregnancy=True,pregnancy_evidence=[self.file('proof.json')],dated_relationship='Bound dated source',supported_from='1842-01-01',supported_to='1842-09-01',scene_timing={'precision':'exact','label':b['scene_date']});self.reviews();self.assertEqual(self.run_gate()['owner_requirement_integrity'],'PASS')

    def test_honest_season_label_and_mismatch(self):
        b=self.data['families'][0]['body'];b.update(status='pregnant_supported',visible_pregnancy=True,scene_date='Spring1828',pregnancy_evidence=[self.file('proof.json')],dated_relationship='Source supports pregnancy throughout depicted spring setting',scene_timing={'precision':'source_label','label':'Spring1828','applicability_label':'Spring1828','applicability_finding':'Exact depicted historical setting supported','source':self.file('proof.json')});self.reviews();self.assertEqual(self.run_gate()['owner_requirement_integrity'],'PASS')
        b['scene_timing']['applicability_label']='Spring1829';self.reviews();self.rejects('Pregnancy evidence label mismatch')

    def test_honest_interval(self):
        b=self.data['families'][0]['body'];b.update(status='pregnant_supported',visible_pregnancy=True,scene_date='Early December1827',pregnancy_evidence=[self.file('proof.json')],dated_relationship='Fixture source supports bounded range',supported_from='1827-10-01',supported_to='1828-01-01',scene_timing={'precision':'interval','label':'Early December1827','start':'1827-12-01','end':'1827-12-10','interval_basis':'Explicit reviewed fictional fixture bound, not invented real historical dates','source':self.file('proof.json')});self.reviews();self.assertEqual(self.run_gate()['owner_requirement_integrity'],'PASS')

    def test_url_origins_and_json_slashes(self):
        (self.root/'index.html').write_text(r'<img src="https://external.example/new.webp"><img src="https://focuschrist.com/new.webp"><script>"https:\/\/focuschrist.com\/new.webp"</script><img src="//external.example/new.webp">')
        got=references(self.root,[self.file('index.html')],{'new.webp'},'https://focuschrist.com')
        self.assertEqual(dict(got),{('index.html','new.webp'):2})

    def test_exact_exemption_without_fabricated_date_or_reviews(self):
        r=self.data['families'][0];r['exempt']=True;self.contract['exceptions']=[self.file('new.webp')];self.contract['exception_families']=[{'id':'SITE05','assets':[self.file('new.webp')]}];r.pop('body');r.pop('reviews');r.pop('root_review')
        self.assertEqual(self.run_gate()['owner_requirement_integrity'],'PASS')
        self.contract['exception_families'][0]['assets']=[self.file('old.webp')];self.rejects('Exception asset set changed')

    def test_unknown_computed_consumer(self):
        self.contract['unresolved_consumers']=['unknown dynamic path'];self.rejects('Unresolved computed/PDF')

    def test_final_requires_owner_and_current_public_evidence(self):
        with self.assertRaisesRegex(ValueError,'Owner acceptance still pending'):self.run_gate(True)
        self.data['status']='owner_accepted';self.data['owner_acceptance']={'kind':'direct_owner_acceptance','subject_sha256':canonical({'families':self.data['families'],'owner_objections':self.data['owner_objections']}),'evidence':self.file('proof.json')}
        self.data['public_closeout']={'subject_sha256':'old','deployment_commit':'fixture-commit','current_consumers':[['church.html','new.webp',1],['index.html','new.webp',1]],'native_evidence':[self.file('proof.json')],'byte_evidence':[self.file('proof.json')]}
        with self.assertRaisesRegex(ValueError,'Public evidence predates'):self.run_gate(True)
        self.data['public_closeout']['subject_sha256']=canonical(self.data['families']);self.assertTrue(self.run_gate(True)['final'])

    def test_old_owner_acceptance_cannot_accept_changed_reviewed_subject(self):
        self.data['status']='owner_accepted';self.data['owner_acceptance']={'kind':'direct_owner_acceptance','subject_sha256':canonical({'families':self.data['families'],'owner_objections':self.data['owner_objections']}),'evidence':self.file('proof.json')}
        self.data['families'][0]['body']['findings']='Different actual reviewed body';self.reviews();self.rejects('Owner acceptance bound to different')


class PortableReferenceTests(unittest.TestCase):
    def census(self, text):
        import json
        import posixpath
        from pathlib import PurePosixPath
        from unittest.mock import patch
        import artwork_owner_closure as module
        class PosixModel(PurePosixPath):
            def resolve(self):
                return PosixModel(posixpath.normpath(str(self)))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'page.json'
            source.write_text(text, encoding='utf-8')
            item = {'path':'page.json', 'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            native = module.references(root, [item], {'assets/a.webp'}, 'https://focuschrist.com')
            # Execute the same scanner with POSIX path semantics; only the
            # hash-bound input read is supplied by this private fixture.
            with patch.object(module, 'Path', PosixModel), patch.object(module, 'bound', return_value=source):
                posix = module.references(PosixModel('/site'), [item], {'assets/a.webp'}, 'https://focuschrist.com')
            self.assertEqual(native, posix)
            return sum(native.values())

    def test_json_escaped_quote_selector(self):
        import json
        self.assertEqual(self.census(json.dumps({'selector':'<img src="assets/a.webp">'})), 1)

    def test_json_escaped_slash(self):
        self.assertEqual(self.census('{"src":"assets\\/a.webp"}'.replace('\\\\/', '\\/')), 1)

    def test_external_origin_does_not_count(self):
        self.assertEqual(self.census('<img src="https://other.example/assets/a.webp">'), 0)

    def test_parent_escape_does_not_count(self):
        self.assertEqual(self.census('<img src="../assets/a.webp">'), 0)



class ExplicitPredecessorRetirementCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json, artwork_owner_closure as c
        cls.gate = c
        # These tests exercise the exact pre-journey scope in an isolated
        # predecessor tree. They do not inspect or certify current output.
        import subprocess
        import artwork_display_delivery as display
        from owner_journey_successor import predecessor_fixture
        from emma_journey_indices_contract import BASE_BLOBS, git_blob
        actual = Path(__file__).resolve().parents[1]
        closure = json.loads((actual/'docs/artwork-correction-reviews.json').read_text())['owner_requirement_closure']
        cls.contract = closure['contract']
        cls.expected = Counter({(x['path'],x['asset']):x['occurrences'] for row in closure['families'] for x in row['consumers']})
        cls.scope = cls.contract['consumer_scope']
        cls.assets = set(cls.contract['known_asset_paths'])
        cls.origin = cls.contract['site_origin']
        cls.fixture = tempfile.TemporaryDirectory(prefix='emma-closure-predecessor-')
        cls.addClassCleanup(cls.fixture.cleanup)
        cls.root = Path(cls.fixture.name)
        snapshots = {}; reviewed = {}
        for name in {x['path'] for x in cls.scope} | {'docs/exclusive-artwork-ownership.json'}:
            out=cls.root/name; out.parent.mkdir(parents=True,exist_ok=True)
            # Pull all content from one exact named base, not the actual new
            # visitor tree. Generated blobs additionally retain explicit pins.
            if name in c.CURRENT_GENERATED_INDICES:
                raw=subprocess.check_output(['git','cat-file','blob',BASE_BLOBS[name]],cwd=actual,timeout=30)
                assert git_blob(raw)==BASE_BLOBS[name], 'wrong predecessor index blob'
            else:
                raw=subprocess.check_output(['git','show','63fafd9594949160f912b3c1ca0e39b52432df34:'+name],cwd=actual,timeout=30)
            if name == 'history/emma-hale-smith.html':
                assert raw == predecessor_fixture(name), 'wrong predecessor page fixture'
            snapshots[name]=raw
            # Old bound() checks the reviewed-byte view, but references() then
            # counts the raw file. Preserve both separately in this isolated
            # fixture, and stop mapping the moment raw bytes are altered.
            reviewed[name]=raw if name in c.CURRENT_GENERATED_INDICES or name == 'docs/exclusive-artwork-ownership.json' else display.inverse(name,raw)
            out.write_bytes(raw)
        old_reviewed=display.reviewed_bytes
        def fixture_reviewed(path):
            path=Path(path)
            try: name=path.resolve().relative_to(cls.root.resolve()).as_posix()
            except ValueError: return old_reviewed(path)
            raw=path.read_bytes()
            return reviewed[name] if name in snapshots and raw == snapshots[name] else raw
        cls.patch_reviewed=patch.object(display,'reviewed_bytes',side_effect=fixture_reviewed)
        cls.patch_reviewed.start();cls.addClassCleanup(cls.patch_reviewed.stop)
        cls.current = c.current_retirement_census(cls.root,cls.scope,cls.assets,cls.origin,cls.expected)

    def test_predecessor_census_and_retirement_contract(self):
        # Exact old view only: not current visitor or generated-index evidence.
        self.assertEqual((len(self.current),sum(self.current.values())),(107,160))
        self.assertEqual(self.expected-self.current,Counter(self.gate.H2_REMOVED))

    def test_each_current_source_or_registry_byte_drift_rejected(self):
        original=Path.read_bytes
        for name in self.gate.CURRENT_SCOPE_PINS:
            target=self.root/name
            def mutate(path):
                raw=original(path)
                return raw+b' ' if path==target else raw
            with self.subTest(name=name),patch.object(Path,'read_bytes',mutate):
                with self.assertRaisesRegex(ValueError,'Current retirement source drift'):
                    self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_retired_or_unexpected_consumers_rejected(self):
        for pair in [('history/emma-hale-smith.html','assets/page-art/emma-life/emma-h2-review-960.webp'),('history/emma-hale-smith.html','assets/page-art/emma-life/emma-c2-review-960.webp'),('index.html','assets/page-art/emma-life/emma-h1-review-960.webp')]:
            changed=self.current.copy();changed[pair]+=1
            with self.subTest(pair=pair),patch.object(self.gate,'references',return_value=changed):
                with self.assertRaisesRegex(ValueError,'Active consumer closure mismatch'):
                    self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_generated_index_schema_and_unrelated_changes(self):
        original=Path.read_bytes
        for name in self.gate.CURRENT_GENERATED_INDICES:
            target=self.root/name
            for bad in (b'{', b'{}'):
                def read(path): return bad if path==target else original(path)
                with self.subTest(name=name,bad=bad),patch.object(Path,'read_bytes',read):
                    with self.assertRaisesRegex(ValueError,'current index'):
                        self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected)
            data=json.loads(original(target))
            if name == 'site-search-index.json': data['records'][0]['text'] += ' unrelated current text'
            else: data['artworks'][0]['title'] += ' unrelated current text'
            changed=json.dumps(data,ensure_ascii=False).encode('utf8')
            def read(path): return changed if path==target else original(path)
            with self.subTest(name=name),patch.object(Path,'read_bytes',read):
                self.assertEqual(self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected),self.current)

    def test_actual_index_retired_reference_is_rejected(self):
        original=Path.read_bytes
        for name in self.gate.CURRENT_GENERATED_INDICES:
            target=self.root/name;data=json.loads(original(target))
            if name == 'site-search-index.json': data['records'][0]['text'] += ' assets/page-art/emma-life/emma-h2-review-960.webp'
            else: data['artworks'][0]['title'] += ' assets/page-art/emma-life/emma-c2-review-960.webp'
            changed=json.dumps(data,ensure_ascii=False).encode('utf8')
            def read(path): return changed if path==target else original(path)
            with self.subTest(name=name),patch.object(Path,'read_bytes',read):
                with self.assertRaisesRegex(ValueError,'Active consumer closure mismatch'):
                    self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_actual_index_missing_active_reference_is_rejected(self):
        original=Path.read_bytes;target=self.root/'site-search-index.json'
        raw=original(target);needle=b'assets/page-art/bom-evidences/josephemma-identity-v4-960.webp'
        self.assertEqual(raw.count(needle),1)
        changed=raw.replace(needle,b'assets/removed-reference.webp',1)
        json.loads(changed)  # The modified index is still valid JSON.
        def read(path): return changed if path==target else original(path)
        with patch.object(Path,'read_bytes',read):
            with self.assertRaisesRegex(ValueError,'Active consumer closure mismatch'):
                self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_duplicate_index_entries_are_rejected(self):
        original=Path.read_bytes
        for name in self.gate.CURRENT_GENERATED_INDICES:
            target=self.root/name;data=json.loads(original(target))
            if name=='site-search-index.json': data['records'].append(data['records'][0])
            else: data['artworks'].append(data['artworks'][0])
            changed=json.dumps(data,ensure_ascii=False).encode('utf8')
            def read(path): return changed if path==target else original(path)
            with self.subTest(name=name),patch.object(Path,'read_bytes',read):
                with self.assertRaisesRegex(ValueError,'Duplicate current index'):
                    self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_scope_and_origin_drift_are_rejected(self):
        for scope in (self.scope[:-1],self.scope+[self.scope[0]]):
            with self.assertRaisesRegex(ValueError,'consumer scope drift'):
                self.gate.current_retirement_census(self.root,scope,self.assets,self.origin,self.expected)
        with self.assertRaisesRegex(ValueError,'origin drift'):
            self.gate.current_retirement_census(self.root,self.scope,self.assets,'https://other.example',self.expected)
        with self.assertRaisesRegex(ValueError,'asset scope drift'):
            self.gate.current_retirement_census(self.root,self.scope,set(list(self.assets)[:-1]),self.origin,self.expected)

    def test_historical_removal_is_not_blanket_waived(self):
        changed=self.expected.copy();changed[next(iter(self.gate.H2_REMOVED))]-=1
        with self.assertRaisesRegex(ValueError,'Historical H2 census drift'):
            self.gate.current_retirement_census(self.root,self.scope,self.assets,self.origin,changed)

class ActualJourneyCensusTests(unittest.TestCase):
    """Real current source/index census. A mocked review is never acceptance.

    Runs against the full checkout and freshly generated current indices. The
    ordinary release gate separately requires real, pinned, direct evidence.
    """
    @classmethod
    def setUpClass(cls):
        import artwork_owner_closure as old, emma_journey_closure_successor as journey
        cls.old, cls.journey = old, journey
        cls.root=Path(__file__).resolve().parents[1]
        closure=json.loads((cls.root/'docs/artwork-correction-reviews.json').read_text())['owner_requirement_closure']
        contract=closure['contract']; cls.scope=contract['consumer_scope']; cls.assets=set(contract['known_asset_paths']); cls.origin=contract['site_origin']
        cls.expected=Counter({(x['path'],x['asset']):x['occurrences'] for row in closure['families'] for x in row['consumers']})

    def test_actual_current_generated_index_and_retained_asset_census(self):
        # Suppress only the human-review step for this technical test. All
        # actual current source, generator and retained-census checks still run.
        with patch.object(self.journey,'check_review',return_value={}):
            got=self.journey.current_census(self.root,self.scope,self.assets,self.origin,self.expected)
        expected=self.expected.copy()
        for pair in self.old.H2_REMOVED: del expected[pair]
        self.assertEqual(got,expected)
        self.assertEqual(hashlib.sha256((self.root/self.journey.HUB).read_bytes()).hexdigest(),self.journey.CURRENT_HUB_SHA256)

    def test_current_emma_census_rejects_wrong_pin_and_changed_bytes(self):
        row = next(x for x in self.scope if x['path'] == self.journey.HUB)
        wrong = dict(row, sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'Current Emma closure source drift'):
            self.old.references(self.root, [wrong], self.assets, self.origin, current_emma=True)
        row = dict(row, sha256=self.journey.CURRENT_HUB_SHA256)
        target=self.root/self.journey.HUB; original=Path.read_bytes
        def mutate(path):
            raw=original(path)
            return raw+b' ' if path==target else raw
        with patch.object(Path, 'read_bytes', mutate):
            with self.assertRaisesRegex(ValueError, 'Current Emma closure source drift'):
                self.old.references(self.root, [row], self.assets, self.origin, current_emma=True)

    def test_actual_current_source_drift_fails_before_review(self):
        target=self.root/self.journey.HUB; original=Path.read_bytes
        def mutate(path):
            raw=original(path)
            return raw+b' ' if path==target else raw
        with patch.object(Path,'read_bytes',mutate), patch.object(self.journey,'check_review',side_effect=AssertionError('review must not run')):
            with self.assertRaisesRegex(ValueError,'current hub bytes drift'):
                self.journey.current_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_actual_current_stale_gallery_fails_before_review(self):
        target=self.root/'art-gallery.json'; original=Path.read_bytes
        data=json.loads(original(target)); data['artworks'][0]['title'] += ' unauthorized drift'
        altered=json.dumps(data,ensure_ascii=False).encode('utf8')
        def mutate(path):
            return altered if path==target else original(path)
        with patch.object(Path,'read_bytes',mutate), patch.object(self.journey,'check_review',side_effect=AssertionError('review must not run')):
            with self.assertRaisesRegex(AssertionError,'gallery differs from full-tree producer'):
                self.journey.current_census(self.root,self.scope,self.assets,self.origin,self.expected)

    def test_unset_review_pin_is_pending_not_accepted(self):
        import timeline_current_index_closure as timeline
        if self.journey.APPROVED_REVIEW_SHA256 is None:
            with self.assertRaisesRegex(ValueError,'PENDING actual current closure and owner review'):
                self.journey.check_review(self.root)
        elif timeline.CODE_REVIEW_SHA256 is None:
            with self.assertRaisesRegex(ValueError,'PENDING independently verified current review'):
                self.journey.check_review(self.root)
        elif (__import__('timeline_51_current_successor').INDEX_REVIEW_SHA256 is None or
              __import__('timeline_51_current_successor').CODE_REVIEW_SHA256 is None):
            with self.assertRaisesRegex(ValueError,'PENDING independently verified Timeline event review'):
                self.journey.check_review(self.root)
        else:
            self.journey.check_review(self.root)

if __name__ == '__main__':
    unittest.main()
