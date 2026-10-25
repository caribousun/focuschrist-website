"""Negative controls for exact historical recovery, not motion visual approval."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import continue_motion_binding as gate
import settings_successor as settings

class MotionBindingTests(unittest.TestCase):
    def test_every_exact_predecessor(self):
        data=gate.mapping()
        for name,row in data['files'].items():
            current=(gate.ROOT/name).read_bytes()
            from world_companion_successor import restore as restore_world
            from missionary_close_successor import restore as restore_close
            from commission_hand_successor import restore as restore_hand
            from answer_bank_successor import restore as restore_bank
            from display_gate_successor import restore as restore_gate
            from citation_rendering_successor import restore as restore_citation
            from bank_serve_decoupling_successor import restore as restore_decoupling
            from evaluator_corrections_successor import restore as restore_eval
            self.assertEqual(gate.sha(restore_world(name,settings.restore(name,restore_close(name,restore_hand(name,restore_bank(name,restore_gate(name,restore_eval(name,restore_citation(name,restore_decoupling(name,current)))))))))),row['after_sha256'],name)
            self.assertEqual(gate.sha(gate.restore(name,current)),row['before_sha256'],name)

    def test_exact_successors_and_unknown_input_rejected(self):
        for name,row in gate.mapping()['files'].items():
            current=(gate.ROOT/name).read_bytes()
            old=gate.restore(name,current)
            from missionary_close_successor import advance as advance_close
            self.assertEqual(gate.advance(name,old),advance_close(name,settings.advance(name,current)),name)
            self.assertEqual(gate.advance(name,old+b' '),old+b' ',name)
            self.assertEqual(gate.advance('unknown/'+name,old),old,name)

    def test_prospective_override_uses_exact_same_historical_chain(self):
        from artwork_creation_gate import content_bytes
        name='church-history.html'
        raw=(gate.ROOT/name).read_bytes()
        expected=content_bytes(gate.ROOT,name)
        self.assertEqual(content_bytes(gate.ROOT,name,{name:raw}),expected)
        self.assertEqual(content_bytes(gate.ROOT,name,{name:raw+b' '}),raw+b' ')

    def test_unknown_route_not_normalized(self):
        raw=(gate.ROOT/'index.html').read_bytes()
        self.assertEqual(gate.restore('unknown.html',raw),raw)

    def test_display_code_inverse_rejects_unrelated_bytes(self):
        from timeline_source_import import before_motion_code_evidence,restore_code_evidence,REVIEWED_CODE_INVERSES
        name='tools/artwork_display_delivery.py';raw=(gate.ROOT/name).read_bytes()
        self.assertEqual(gate.sha(before_motion_code_evidence(name,raw)),REVIEWED_CODE_INVERSES[name]['current'])
        self.assertEqual(gate.sha(restore_code_evidence(name,raw)),REVIEWED_CODE_INVERSES[name]['previous'])
        for changed in [raw+b' ',raw.replace(b'before_motion(name,',b'before_motion(other,',1)]:
            self.assertNotEqual(changed,raw)
            self.assertEqual(before_motion_code_evidence(name,changed),changed)
        self.assertEqual(before_motion_code_evidence('other/'+name,raw),raw)

    def test_one_unknown_byte_not_normalized(self):
        raw=(gate.ROOT/'index.html').read_bytes()+b' '
        self.assertEqual(gate.restore('index.html',raw),raw)

    def test_mixed_cache_not_normalized(self):
        raw=(gate.ROOT/'index.html').read_bytes().replace(b'20261021-continue-motion-1',b'20261021-unreviewed-motion-1',1)
        self.assertEqual(gate.restore('index.html',raw),raw)

    def test_prior_bytes_not_changed(self):
        raw=(gate.ROOT/'index.html').read_bytes();prior=gate.restore('index.html',raw)
        self.assertEqual(gate.restore('index.html',prior),prior)

    def test_context_snapshot_outside_repository_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'index.html';raw=(gate.ROOT/'index.html').read_bytes();path.write_bytes(raw)
            self.assertEqual(gate.reviewed_bytes(path),raw)

    def test_all_six_existing_delivery_context_records(self):
        import importlib
        for stem in ['seasonal','four-scene','answers-six','six-scene','gabriel-owner','three-reviewed']:
            module=importlib.import_module('artwork_'+stem.replace('-','_')+'_delivery')
            record=json.loads((gate.ROOT/('docs/artwork-'+stem+'-delivery-reviews.json')).read_text(encoding='utf-8'))
            def walk(value):
                if isinstance(value,dict):
                    if set(value)>={'path','sha256'} and (gate.ROOT/value['path']).is_file():
                        self.assertEqual(module.digest(gate.ROOT/value['path']),value['sha256'],stem+':'+value['path'])
                    for child in value.values():walk(child)
                elif isinstance(value,list):
                    for child in value:walk(child)
            walk(record)

    def test_display_review_evidence_including_page_snapshots(self):
        from timeline_source_import import restore_code_evidence
        record=json.loads((gate.ROOT/'docs/image-delivery-20261019.json').read_text(encoding='utf-8'))
        for review in record['reviews']:
            for item in review['evidence']:
                self.assertEqual(gate.sha(restore_code_evidence(item['path'],(gate.ROOT/item['path']).read_bytes())),item['sha256'],item['path'])

    def test_mapping_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/gate.MAP;p.parent.mkdir(parents=True)
            data=copy.deepcopy(gate.mapping());data['files']['index.html']['before_sha256']='0'*64;p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Unknown motion predecessor map'):gate.mapping(root)

    def test_ask_html_citation_chain_composes(self):
        from citation_rendering_successor import restore as restore_citation
        from bank_serve_decoupling_successor import restore as restore_decoupling
        from answer_bank_successor import restore as restore_bank
        name='ask.html'
        row=gate.mapping()['files'][name]
        current=(gate.ROOT/name).read_bytes()
        self.assertEqual(gate.sha(restore_decoupling(name,current)),'4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9',name)
        projected=restore_citation(name,restore_decoupling(name,current))
        self.assertEqual(gate.sha(projected),'735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612',name)
        self.assertEqual(gate.sha(restore_bank(name,projected)),row['after_sha256'],name)
        self.assertEqual(gate.sha(gate.restore(name,current)),row['before_sha256'],name)
        self.assertEqual(gate.advance(name,gate.restore(name,current)),current,name)

    def test_site_common_decoupling_chain_composes(self):
        from evaluator_corrections_successor import restore as restore_eval
        from display_gate_successor import restore as restore_gate
        from bank_serve_decoupling_successor import restore as restore_decoupling
        name='site-common.js'
        row=gate.mapping()['files'][name]
        current=(gate.ROOT/name).read_bytes()
        projected=restore_decoupling(name,current)
        self.assertEqual(gate.sha(projected),'54cfb9fc5de9c5ab76133cb32843053ee6c5700ff0fe11d8bedd470de3412a77',name)
        self.assertEqual(gate.sha(restore_eval(name,projected)),'9090c0bf19a4093f881bf0d1f9f95236ec1db8d61a7072251d807f5c9ce3a041',name)
        self.assertEqual(gate.sha(restore_gate(name,restore_eval(name,projected))),row['after_sha256'],name)
        self.assertEqual(gate.sha(gate.restore(name,current)),row['before_sha256'],name)
        self.assertEqual(gate.advance(name,gate.restore(name,current)),current,name)

    def test_pending_review_cannot_pass(self):
        with patch.object(gate,'APPROVED_REVIEWS',None):
            with self.assertRaisesRegex(ValueError,'finished review PENDING'):gate.check()

if __name__=='__main__':unittest.main()
