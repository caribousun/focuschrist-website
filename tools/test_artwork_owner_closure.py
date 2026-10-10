"""Isolated synthetic integrity fixtures; no real pixel/owner acceptance claims."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()
