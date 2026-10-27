"""Synthetic negative fixtures only. Never creates a real producer approval."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import adams_index_producer_successor as s
import adams_integration_indices as integration

class ProducerSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='index-producer-fixture-')
        self.addCleanup(self.temp.cleanup); self.root=Path(self.temp.name)
        self.old_css=b'fixture-old-css\n'; self.new_css=self.old_css+b'fixture-new-css\n'
        self.patchers=[patch.object(s,'OLD_CSS_BYTES',len(self.old_css)),patch.object(s,'OLD_CSS_SHA',s.digest(self.old_css)),patch.object(s,'NEW_CSS_BYTES',len(self.new_css)),patch.object(s,'NEW_CSS_SHA',s.digest(self.new_css))]
        for p in self.patchers: p.start(); self.addCleanup(p.stop)
        inputs=set(s.FRONTEND_INPUTS)|set(s.GENERATORS)|{'sitemap.xml'}
        old=[];new=[]
        for name in sorted(inputs):
            before=self.old_css if name==s.CSS else ('synthetic '+name).encode()
            after=self.new_css if name==s.CSS else before
            self.put(name,after)
            old.append(self.input_row(name,before));new.append(self.input_row(name,after))
        outputs=[];after_hash={'timeline.html':'fixture-not-used'}
        for name in sorted(set(integration.AFTER)-{'timeline.html'}):
            raw=('synthetic output '+name).encode(); self.put(name,raw)
            outputs.append({'path':name,'bytes':len(raw),'sha256':s.digest(raw)});after_hash[name]=s.digest(raw)
        p=patch.object(s,'AFTER',after_hash);p.start();self.addCleanup(p.stop)
        self.prior={'run_id':1,'job_id':2,'artifact_id':3,'producer_commit':'1'*40,'producer_tree':'2'*40,'inputs':old,'outputs':outputs}
        self.put(s.PRODUCER_MANIFEST,json.dumps(self.prior).encode())
        p=patch.object(s,'PRODUCER_SHA',s.canonical(self.prior));p.start();self.addCleanup(p.stop)
        self.record={'schema':1,'repository':'caribousun/focuschrist-website','event':'pull_request','producer_ref':'refs/pull/531/merge',
          'head_sha':'b'*40,'producer_commit':'c'*40,'producer_tree':'d'*40,'producer_parents':['a'*40,'b'*40],
          'run_id':11,'job_id':12,'artifact_id':13,'job_conclusion':'success','artifact_bytes':42,'artifact_sha256':'e'*64,
          'inputs':new,'outputs':copy.deepcopy(outputs),'scope':'SYNTHETIC TEST ONLY','release_claim':False}
        self.write_record(self.record)

    def put(self,name,raw):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    def input_row(self,name,raw): return {'path':name,'bytes':len(raw),'sha256':s.digest(raw),'git_blob_sha1':s.git_blob(raw)}
    def write_record(self,record): self.put(s.SUCCESSOR_MANIFEST,json.dumps(record).encode())
    def validate_synthetic(self,record=None):
        record=self.record if record is None else record
        self.write_record(record)
        # Patch only inside this disposable test process; production pin is real evidence.
        with patch.object(s,'APPROVED_RECORD_SHA256',s.canonical(record)):
            return s.validate_successor(self.root)
    def rejects(self,record):
        with self.assertRaises((ValueError,KeyError,TypeError)): self.validate_synthetic(record)

    def test_unset_and_real_pin_reject_synthetic_record(self):
        with patch.object(s,'APPROVED_RECORD_SHA256',None), self.assertRaisesRegex(ValueError,'PENDING'):s.validate_successor(self.root)
        with self.assertRaisesRegex(ValueError,'independently reviewed'):s.validate_successor(self.root)
    def test_synthetic_positive_only_under_test_patch(self):
        self.assertEqual(self.validate_synthetic()['scope'],'SYNTHETIC TEST ONLY')
        self.assertEqual(s.APPROVED_RECORD_SHA256,'ddba5124f94156f686af422ca9e385bd5ec8d95f05a45192aa1c2455beb2d693')
    def test_stale_unpinned_or_tampered_record_rejected(self):
        with patch.object(s,'APPROVED_RECORD_SHA256','0'*64), self.assertRaises(ValueError):s.validate_successor(self.root)
        self.put(s.PRODUCER_MANIFEST,b'{}')
        with self.assertRaises(ValueError):self.validate_synthetic()
    def test_no_old_provider_identity_can_be_reused(self):
        for key in ('run_id','job_id','artifact_id','producer_commit','producer_tree'):
            value=copy.deepcopy(self.record);value[key]=self.prior[key];self.rejects(value)
    def test_bad_provenance_and_placeholder_release_claim_rejected(self):
        cases=[('repository','wrong'),('event','push'),('producer_ref','refs/pull/530/merge'),('head_sha','bad'),('producer_tree','z'*40),('producer_parents',['a'*40,'c'*40]),('artifact_sha256','bad'),('artifact_bytes',True),('job_conclusion','failure'),('release_claim',True),('schema',True)]
        for key,val in cases:
            with self.subTest(key=key):
                rec=copy.deepcopy(self.record);rec[key]=val;self.rejects(rec)
    def test_missing_duplicate_extra_and_changed_input_rejected(self):
        for mode in ('missing','duplicate','extra','changed_non_css'):
            rec=copy.deepcopy(self.record)
            if mode=='missing':rec['inputs'].pop()
            elif mode=='duplicate':rec['inputs'][-1]=copy.deepcopy(rec['inputs'][0])
            elif mode=='extra':rec['inputs'].append(copy.deepcopy(rec['inputs'][0]))
            else:
                row=next(x for x in rec['inputs'] if x['path']!=s.CSS);row['sha256']='0'*64
            with self.subTest(mode=mode): self.rejects(rec)
    def test_actual_css_and_each_index_drift_rejected(self):
        for name in [s.CSS,*[x['path'] for x in self.record['outputs']]]:
            path=self.root/name;raw=path.read_bytes();path.write_bytes(raw+b' ')
            with self.subTest(name=name), self.assertRaises(ValueError): self.validate_synthetic()
            path.write_bytes(raw)
    def test_changed_candidate_cannot_hide_old_prefix_or_output(self):
        changed=b'wrong-prefix'+b'new-suffix';self.put(s.CSS,changed)
        row=next(x for x in self.record['inputs'] if x['path']==s.CSS);row.update(self.input_row(s.CSS,changed))
        with patch.object(s,'NEW_CSS_BYTES',len(changed)), patch.object(s,'NEW_CSS_SHA',s.digest(changed)), self.assertRaises(ValueError): self.validate_synthetic()
        self.put(s.CSS,self.new_css);rec=copy.deepcopy(self.record)
        raw=b'another output';name=rec['outputs'][0]['path'];self.put(name,raw);rec['outputs'][0].update(bytes=len(raw),sha256=s.digest(raw))
        with self.assertRaises(ValueError):self.validate_synthetic(rec)
    def test_missing_or_symlink_file_rejected(self):
        name=next(x['path'] for x in self.record['inputs'] if x['path']!=s.CSS)
        path=self.root/name;path.unlink()
        with self.assertRaises(ValueError):self.validate_synthetic()
        target=self.root/'untrusted-copy';target.write_bytes(b'no');path.symlink_to(target)
        with self.assertRaises(ValueError):self.validate_synthetic()
    def test_current_entrypoint_rejects_old_and_unknown_css_even_when_record_is_pinned(self):
        with patch.object(s,'APPROVED_RECORD_SHA256',s.canonical(self.record)):
            self.assertEqual(integration.validate_producer(self.root)['scope'],'SYNTHETIC TEST ONLY')
            for wrong in (self.old_css,b'unknown'):
                self.put(s.CSS,wrong)
                with self.assertRaises(ValueError):integration.validate_producer(self.root)
        self.assertEqual(s.APPROVED_RECORD_SHA256,'ddba5124f94156f686af422ca9e385bd5ec8d95f05a45192aa1c2455beb2d693')

if __name__=='__main__': unittest.main()
