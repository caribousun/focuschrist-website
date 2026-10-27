"""Mutation fixtures only; synthetic data never constitutes current evidence."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import adams_header_evidence_successor as s
import adams_source_import as dispatch

ROOT=Path(__file__).resolve().parents[1]

class HeaderEvidenceSuccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/s.prior.MANIFEST).read_bytes())['spec']
        cls.contract=json.loads((ROOT/'tools/owner_integration_qa_contract.json').read_bytes())

    def current_fixture(self):
        value=copy.deepcopy(self.old)
        for i,r in enumerate(value['context']):
            if r['path']==s.CSS['path']:value['context'][i]=dict(s.CSS)
        value['qa']['helper']=dict(s.HELPER);value['qa']['owner_contract']=dict(s.OWNER_CONTRACT)
        for key in ('report','run_identity','capture_manifest','owner_report','owner_capture_manifest'):
            value['qa'][key]['path']='docs/adams-header-evidence-successor/fixture-'+key+'.json'
        value['qa']['producer']['run_id']='99999999999' # synthetic negative/shape testing only
        return value

    def test_production_pending_cannot_approve(self):
        # A missing actual pin must always block, regardless of installed state.
        with patch.multiple(s,APPROVED_RECORD_SHA256=None,APPROVED_SPEC_SHA256=None,APPROVED_PROVIDER_SHA256=None):
            with self.assertRaises(ValueError):s.validate(ROOT,set(),set(),set())

    def test_integrated_dispatch_has_no_legacy_fallback(self):
        # This checks only routing under deliberately pending synthetic pins.
        with patch.multiple(s,APPROVED_RECORD_SHA256=None,APPROVED_SPEC_SHA256=None,APPROVED_PROVIDER_SHA256=None), patch.object(s.prior,'validate',side_effect=AssertionError('legacy fallback forbidden')):
            with self.assertRaisesRegex(ValueError,'pending'):
                dispatch.validate(ROOT,set(),set(),set())

    def test_integrated_sources_cannot_fall_back_if_manifest_missing(self):
        with patch.multiple(s,APPROVED_RECORD_SHA256=None,APPROVED_SPEC_SHA256=None,APPROVED_PROVIDER_SHA256=None):
            for name in ('timelines/adams-1881-introduction.html','adams-integration.css'):
                with self.subTest(name=name),tempfile.TemporaryDirectory() as td:
                    root=Path(td);p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
                    with self.assertRaisesRegex(ValueError,'pending'):
                        dispatch.validate(root,set(),set(),set())
            with tempfile.TemporaryDirectory() as td:
                # A genuinely pre-integration tree retains the old fail-closed path.
                with self.assertRaisesRegex(ValueError,'missing or unsafe file'):
                    dispatch.validate(Path(td),set(),set(),set())

    def test_only_exact_css_and_evidence_delta(self):
        current=self.current_fixture();s.validate_spec_delta(self.old,current)
        variants=[]
        bad=copy.deepcopy(current);bad['context'][0]=dict(s.OLD_CSS);variants.append(bad)
        bad=copy.deepcopy(current);bad['assets'][0]['sha256']='0'*64;variants.append(bad)
        bad=copy.deepcopy(current);bad['context'][1]['sha256']='0'*64;variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['states']=100;variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['helper']['sha256']='0'*64;variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['owner_contract']['sha256']='0'*64;variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['report']['path']=self.old['qa']['report']['path'];variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['producer']['run_id']=self.old['qa']['producer']['run_id'];variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['owner_report']['path']=bad['qa']['report']['path'];variants.append(bad)
        bad=copy.deepcopy(current);bad['qa']['extra']='unexpected';variants.append(bad)
        for i,bad in enumerate(variants):
            with self.subTest(i=i),self.assertRaises((ValueError,KeyError,TypeError)):s.validate_spec_delta(self.old,bad)

    def test_exact_historical_css_and_helper_projection(self):
        prior=s.historical_reader(ROOT,s.OLD_CSS);self.assertEqual(len(prior),4965)
        for key in ('helper','owner_helper','owner_contract'):
            expected=self.old['qa'][key];raw=s.historical_reader(ROOT,expected);self.assertEqual(len(raw),expected['bytes'])
        altered=dict(s.OLD_CSS,sha256='0'*64)
        with self.assertRaises(ValueError):s.historical_reader(ROOT,altered)

    def test_old_actual_qa_and_receipts_remain_historical_only(self):
        record=json.loads((ROOT/s.prior.MANIFEST).read_bytes());s.prior.validate_reviews(ROOT,record)
        s.qa_checks.validate_qa(ROOT,record['spec'],helper_reader=s.historical_reader)

    def test_actual_role_assignment_is_exact_and_authors_distinct(self):
        assignment=json.loads((ROOT/'docs/adams-header-evidence-successor/review-role-assignment.json').read_bytes())
        self.assertEqual(s.canonical(assignment),s.APPROVED_ASSIGNMENT_SHA256)
        self.assertEqual(assignment['roles'],s.REVIEW_ASSIGNMENTS)
        self.assertEqual(len(set(assignment['roles'].values())),3)
        altered=copy.deepcopy(assignment);altered['roles']['Newton']=altered['roles']['Fermi']
        self.assertNotEqual(s.canonical(altered),s.APPROVED_ASSIGNMENT_SHA256)

    def test_current_review_fixture_rejects_boolean_or_missing_evidence(self):
        spec=self.current_fixture();keys=('report','run_identity','capture_manifest','owner_report','owner_capture_manifest')
        evidence=[spec['qa'][k] for k in keys];spec_sha='a'*64;rows=[];objects={}
        for who in ('Fermi','Newton','Albert'):
            name='fixture-'+who;rows.append({'reviewer':who,'author_id':s.REVIEW_ASSIGNMENTS[who],'receipt':{'path':name}})
            objects[name]={'schema':1,'reviewer':who,'review_role':who,'author_id':s.REVIEW_ASSIGNMENTS[who],'role_scope':'task-specific fixture only','role_assignment_sha256':s.APPROVED_ASSIGNMENT_SHA256,'decision':'CONCUR','spec_sha256':spec_sha,'reviewed_at':'2026-10-27T21:00:00+00:00','source_rights_checked':True,'finished_pixels':True,'desktop_phone_inspected':True,'mandate_readback':{'files':[{'path':'fixture-mandate','sha256':'f'*64}],'applicable_requirements':['fixture requirement']},'finished_candidate_follows_mandates':True,'observations':'fixture only','limits':['fixture only'],'evidence':copy.deepcopy(evidence)}
        for item in evidence:objects[item['path']]={'fixture':True}
        record={'reviews':rows};assignment={'schema':1,'appointed_by':'Albert','author_id':'/root','scope':'fixture-only task roles','roles':dict(s.REVIEW_ASSIGNMENTS)}
        def fake_bound(root,item):return json.dumps(objects[item['path']]).encode()
        with patch.object(s,'bound',side_effect=fake_bound):
            s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)
            wrong=copy.deepcopy(assignment);wrong['roles']['Newton']=wrong['roles']['Fermi']
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,wrong)
            objects['fixture-Fermi']['role_assignment_sha256']='0'*64
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)
            objects['fixture-Fermi']['role_assignment_sha256']=s.APPROVED_ASSIGNMENT_SHA256
            objects['fixture-Fermi']['author_id']='/wrong/author'
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)
            objects['fixture-Fermi']['author_id']=s.REVIEW_ASSIGNMENTS['Fermi'];objects['fixture-Fermi']['schema']=True
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)
            objects['fixture-Fermi']['schema']=1;objects['fixture-Fermi']['finished_candidate_follows_mandates']=False
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)
            objects['fixture-Fermi']['finished_candidate_follows_mandates']=True;objects['fixture-Fermi']['mandate_readback']['files'][0]['sha256']='bad'
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)
            objects['fixture-Fermi']['mandate_readback']['files'][0]['sha256']='f'*64;objects['fixture-Fermi']['evidence'].pop()
            with self.assertRaises(ValueError):s.validate_current_reviews(ROOT,record,spec_sha,spec,assignment)

    def test_provider_cross_bindings_reject_mismatches(self):
        identity={'head_sha':'1'*40,'checkout_sha':'2'*40,'tree_sha':'3'*40,'run_id':'10','job_id':'11','artifact_id':'12','artifact_bytes':123,'artifact_sha256':'a'*64}
        capture={'run_id':'10','job_id':'13','artifact_id':'14','artifact_bytes':456,'artifact_sha256':'b'*64,'capture_count':74}
        owner={'producer':{'sha':identity['checkout_sha'],'run':'10','event':'pull_request'},'checked':self.contract['sources']+self.contract['assets']}
        provider={'repository':'caribousun/focuschrist-website','event':'pull_request','pr_number':531,'ref':'refs/pull/531/merge','base_sha':'4'*40,'parents':['4'*40,identity['head_sha']],**{k:identity[k] for k in ('head_sha','checkout_sha','tree_sha','run_id')},'timeline_job_id':'11','timeline_artifact_id':'12','timeline_artifact_bytes':123,'timeline_artifact_sha256':'a'*64,'owner_job_id':'13','owner_artifact_id':'14','owner_artifact_bytes':456,'owner_artifact_sha256':'b'*64,'timeline_job_conclusion':'success','owner_job_conclusion':'success','source_blobs':{'adams-integration.css':'70a3a767c87096dbc60fc4d01f469d9dd8e54a2a','tools/adams_chart_browser_qa.js':'03baf35e2b1525a343cd2bf23422df142dd16038','tools/owner_integration_qa_contract.json':'2fdb9f261db7af4e1213d243daefeac417eb5311'}}
        spec=self.current_fixture();q=spec['qa'];values={q['run_identity']['path']:identity,q['owner_report']['path']:owner,q['owner_capture_manifest']['path']:capture,s.OWNER_CONTRACT['path']:self.contract}
        def fake_bound(root,item):return json.dumps(values[item['path']]).encode()
        with patch.object(s,'bound',side_effect=fake_bound):
            s.validate_owner_provenance(ROOT,spec,provider)
            for key in ('run_id','checkout_sha','owner_job_id','owner_artifact_id','owner_artifact_sha256','timeline_job_id','timeline_artifact_id','timeline_artifact_sha256','owner_job_conclusion','pr_number','ref','parents'):
                bad=copy.deepcopy(provider);bad[key]='wrong'
                with self.subTest(key=key),self.assertRaises(ValueError):s.validate_owner_provenance(ROOT,spec,bad)
            bad=copy.deepcopy(provider);bad['owner_job_id']=bad['timeline_job_id']
            with self.assertRaises(ValueError):s.validate_owner_provenance(ROOT,spec,bad)
            bad=copy.deepcopy(provider);bad['source_blobs']['adams-integration.css']='0'*40
            with self.assertRaises(ValueError):s.validate_owner_provenance(ROOT,spec,bad)
            values[q['owner_report']['path']]['checked'].pop()
            with self.assertRaises(ValueError):s.validate_owner_provenance(ROOT,spec,provider)

if __name__=='__main__':unittest.main()
