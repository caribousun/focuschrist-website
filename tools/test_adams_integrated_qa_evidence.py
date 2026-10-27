"""Hosted current evidence and negative mutations; no synthetic acceptance."""
import copy
import json
import unittest
from pathlib import Path
import adams_integrated_qa_evidence as gate
import adams_header_evidence_successor as successor

ROOT=Path(__file__).resolve().parents[1]
class IntegratedReportTests(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((ROOT/'docs/adams-integrated-context/delivery.json').read_bytes())['spec']
        qa=self.spec['qa']
        self.viewer=json.loads((ROOT/qa['report']['path']).read_bytes())
        self.identity=json.loads((ROOT/qa['run_identity']['path']).read_bytes())
        self.captures=json.loads((ROOT/qa['capture_manifest']['path']).read_bytes())
        self.owner=json.loads((ROOT/qa['owner_report']['path']).read_bytes())
    def viewer_check(self):gate.validate_qa_report(self.spec,self.viewer,self.identity,self.captures)
    def test_actual_bound_reports_are_explicitly_historical(self):
        # New helper and owner contract must never masquerade as old report inputs.
        with self.assertRaises(ValueError):gate.validate_qa(ROOT,self.spec)
        gate.validate_qa(ROOT,self.spec,helper_reader=successor.historical_reader)

    def test_viewer_failure_rejected(self):
        self.viewer['results'][1]['pass']=False
        with self.assertRaises(ValueError):self.viewer_check()
    def test_missing_journey_rejected(self):
        self.viewer['results'][0]['states'][0]['label']='missing'
        with self.assertRaises(ValueError):self.viewer_check()
    def test_producer_mismatch_rejected(self):
        self.identity['run_id']='wrong'
        with self.assertRaises(ValueError):self.viewer_check()
    def test_capture_mismatch_rejected(self):
        self.captures['captures'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):self.viewer_check()
    def test_tile_bytes_rejected(self):
        self.viewer['network'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):self.viewer_check()
    def test_owner_failure_rejected(self):
        self.owner['pass']=False
        with self.assertRaises(ValueError):gate.validate_owner_report(self.spec,self.owner)
    def test_owner_geometry_rejected(self):
        self.owner['profiles'][0]['openingComparison']['current']['hero']['width']+=5
        with self.assertRaises(ValueError):gate.validate_owner_report(self.spec,self.owner)
    def test_owner_missing_navigation_rejected(self):
        self.owner['profiles'][0]['journeys']=[]
        with self.assertRaises(ValueError):gate.validate_owner_report(self.spec,self.owner)
    def test_owner_missing_search_rejected(self):
        self.owner['profiles'][0]['searchStates']=[]
        with self.assertRaises(ValueError):gate.validate_owner_report(self.spec,self.owner)
if __name__=='__main__':unittest.main()
