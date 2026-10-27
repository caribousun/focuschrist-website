"""Actual five-file context checks and bounded negative controls; no browser."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import adams_integrated_source_import as gate
import adams_header_evidence_successor as successor

ROOT = Path(__file__).resolve().parents[1]

class IntegratedContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='adams-integrated-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = json.loads((ROOT / gate.MANIFEST).read_bytes())
        self.spec = self.record['spec']
        for item in self.spec['context'] + self.spec['shared_dependencies']:
            # This test exercises immutable prior semantics. The actual current
            # CSS must pass the strict successor before projecting its old prefix.
            raw = (successor.historical_reader(ROOT,item) if item['path']==successor.CSS['path']
                   else (ROOT / item['path']).read_bytes())
            self.assertEqual(len(raw), item['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item['sha256'])
            p = self.root / item['path']; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)

    def alter(self, path, before, after):
        item = next(x for x in self.spec['context'] if x['path'] == path)
        p = self.root / path; raw=p.read_bytes(); self.assertIn(before,raw)
        raw=raw.replace(before,after,1);p.write_bytes(raw)
        # Synthetic repin exercises semantic predicates, not source-digest failure.
        item.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

    def test01_actual_five_context_files(self):
        self.assertEqual(set(gate.validate_context(self.root,self.spec)),gate.CONTEXT_PATHS)
    def test02_missing_header(self):
        self.alter('timelines/adams-1881-chart.html',b'data-focuschrist-header="standard"',b'data-focuschrist-header="unknown"')
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test03_missing_footer(self):
        self.alter('timelines/adams-1881-chart.html',b'data-focuschrist-footer="standard"',b'data-focuschrist-footer="unknown"')
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test04_missing_search(self):
        self.alter('timelines/adams-1881-introduction.html',b'data-site-search-trigger',b'data-unknown-trigger')
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test05_wrong_search_controller(self):
        self.alter('timelines/adams-1881-chart.html',b'site-search.js?v=20260919-focused-answers-1',b'site-search.js?v=unknown')
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test06_missing_context_owner(self):
        self.spec['context'].pop()
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test07_duplicate_context_owner(self):
        self.spec['context'].append(copy.deepcopy(self.spec['context'][0]))
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test08_existing_asset_spec_drift(self):
        self.spec['assets'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test09_wrong_reference_owner(self):
        self.spec['asset_use']['timeline.html']=[]
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test10_missing_detail_reference(self):
        self.alter('timelines/adams-1881-introduction.html',b'adams-16-0-0.jpg',b'adams-16-1-0.jpg')
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test11_pending_is_not_approval(self):
        with patch.multiple(gate,APPROVED_RECORD=None,APPROVED_SPEC=None):
            with self.assertRaises(ValueError):gate.validate_reviews(self.root,self.record)
    def test12_missing_reviews_even_with_synthetic_pin(self):
        self.record['status']='REVIEWED_EXACT_INTEGRATED_CONTEXT';self.record['reviews']=[]
        with patch.multiple(gate,APPROVED_RECORD=gate.canonical(self.record),APPROVED_SPEC=gate.canonical(self.spec)):
            with self.assertRaises(ValueError):gate.validate_reviews(self.root,self.record)

    def test13_unknown_context_path(self):
        self.spec['context'][0]['path']='unrelated.html'
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test14_symlink_context_file(self):
        name=self.spec['context'][0]['path'];p=self.root/name
        target=self.root/'inert-copy';target.write_bytes(p.read_bytes());p.unlink();p.symlink_to(target)
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test15_wrong_record_schema(self):
        for schema in (True,2,'1'):
            self.record['schema']=schema;self.record['status']='REVIEWED_EXACT_INTEGRATED_CONTEXT'
            with patch.multiple(gate,APPROVED_RECORD=gate.canonical(self.record),APPROVED_SPEC=gate.canonical(self.spec)):
                with self.assertRaises(ValueError):gate.validate_reviews(self.root,self.record)
    def test16_pending_receipt_scope(self):
        self.record['status']='REVIEWED_EXACT_INTEGRATED_CONTEXT'
        self.record['reviews']=[]
        for who in ('Fermi','Newton','Albert'):
            own={'schema':1,'reviewer':who,'reviewed_at':'2026-10-27T00:00:00+00:00','decision':'CONCUR','spec_sha256':gate.canonical(self.spec),'source_rights_checked':True,'finished_pixels':False,'desktop_phone_inspected':False,'observations':'Synthetic negative control only','limits':['not actual review'],'evidence':[]}
            raw=json.dumps(own).encode();name='negative-fixture-'+who+'.json';(self.root/name).write_bytes(raw)
            self.record['reviews'].append({'reviewer':who,'receipt':{'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}})
        with patch.multiple(gate,APPROVED_RECORD=gate.canonical(self.record),APPROVED_SPEC=gate.canonical(self.spec)):
            with self.assertRaises(ValueError):gate.validate_reviews(self.root,self.record)

    def test17_missing_shared_dependency(self):
        self.spec['shared_dependencies'].pop()
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test18_changed_shared_dependency(self):
        p=self.root/self.spec['shared_dependencies'][0]['path'];p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)
    def test19_symlink_shared_dependency(self):
        p=self.root/self.spec['shared_dependencies'][0]['path'];target=self.root/'shared-copy';target.write_bytes(p.read_bytes());p.unlink();p.symlink_to(target)
        with self.assertRaises(ValueError):gate.validate_context(self.root,self.spec)

if __name__=='__main__':unittest.main()
