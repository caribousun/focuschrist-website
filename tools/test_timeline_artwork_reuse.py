"""Independent deterministic data/rights negatives; no real review assertions."""
import copy
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch
from pathlib import Path
import timeline_artwork_reuse as gate

class ReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.before=(cls.root/gate.BASELINE).read_text(encoding='utf-8')
        cls.original=gate.declaration(cls.before,'DATA')
        cls.credits=gate.declaration(cls.before,'PHOTO_CREDITS')

    def candidate(self, mutate=None):
        rows=copy.deepcopy(self.original)
        for i in (25,28):rows[i].update(img=gate.ASSET,imgpage=gate.OWNER,credit='Artwork: focuschrist.com')
        credits={k:copy.deepcopy(v) for k,v in self.credits.items() if k not in gate.RETIRED}
        if mutate:mutate(rows,credits)
        return 'const DATA = '+json.dumps(rows)+';\nconst PHOTO_CREDITS = '+json.dumps(credits)+';'

    def test_exact_two_replacements(self):
        self.assertEqual(gate.validate_delta(self.before,self.candidate())['active_photos'],191)

    def test_unrelated_record_changed(self):
        with self.assertRaisesRegex(ValueError,'Unrelated DATA'):
            gate.validate_delta(self.before,self.candidate(lambda d,c:d[29].update(name='changed')))

    def test_historical_field_changed(self):
        with self.assertRaisesRegex(ValueError,'historical entry'):
            gate.validate_delta(self.before,self.candidate(lambda d,c:d[25].update(lat=0)))

    def test_wrong_owner_or_missing_credit(self):
        for field,value in [('imgpage','https://commons.wikimedia.org/wiki/File:first-hope.webp'),('credit','')]:
            with self.assertRaises(ValueError):
                gate.validate_delta(self.before,self.candidate(lambda d,c:d[28].update({field:value})))

    def test_rights_changed(self):
        def alter(d,c):c[next(iter(c))]['author']='invented'
        with self.assertRaisesRegex(ValueError,'rights inventory'):
            gate.validate_delta(self.before,self.candidate(alter))

    def test_retired_reference_elsewhere_rejected(self):
        with self.assertRaisesRegex(ValueError,'live reference'):
            gate.validate_delta(self.before,self.candidate()+'\n'+next(iter(gate.RETIRED)))

    def test_no_approval_default(self):
        with patch.object(gate,'APPROVED_REUSE',None):
            with self.assertRaisesRegex(ValueError,'pending finished review'):
                gate.validate(self.root,self.candidate().encode())

    def test_new_scanner_inventory_and_wrong_retirement(self):
        from topic_artwork_uniqueness_qa import script_image_urls
        urls=set(script_image_urls(self.candidate(),gate.PAGE))
        self.assertIn(gate.ASSET,urls)
        self.assertFalse(urls&gate.RETIRED)
        with self.assertRaises(ValueError):
            list(script_image_urls(self.candidate(lambda d,c:d[25].update(imgpage='wrong')),gate.PAGE))

class ActualOverlayTests(unittest.TestCase):
    """Copy real reviewed delivery into isolation; never mutate its evidence."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);real=Path(__file__).resolve().parents[1]
        self.record=json.loads((real/gate.MANIFEST).read_text(encoding='utf-8'))
        names=[gate.MANIFEST,gate.BASELINE,gate.PAGE,gate.ASSET.lstrip('/')]
        names += [r['evidence']['path'] for r in self.record['reviews']]
        for name in names:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(real/name,target)
        self.current=(self.root/gate.PAGE).read_bytes()

    def check(self):return gate.validate(self.root,self.current)

    def test_actual_reviewed_overlay(self):
        self.assertEqual(gate.sha(self.check()),gate.BASELINE_SHA)

    def test_missing_review_evidence(self):
        (self.root/self.record['reviews'][0]['evidence']['path']).unlink()
        with self.assertRaisesRegex(ValueError,'Missing/outside evidence'):self.check()

    def test_changed_review_evidence(self):
        (self.root/self.record['reviews'][0]['evidence']['path']).write_bytes(b'Unreviewed replacement')
        with self.assertRaisesRegex(ValueError,'Changed review evidence'):self.check()

    def test_changed_final_page(self):
        self.current+=b' '
        with self.assertRaisesRegex(ValueError,'Changed final page'):self.check()

    def test_changed_existing_artwork(self):
        (self.root/gate.ASSET.lstrip('/')).write_bytes(b'Changed image')
        with self.assertRaisesRegex(ValueError,'Changed existing artwork bytes'):self.check()

    def test_missing_existing_artwork(self):
        (self.root/gate.ASSET.lstrip('/')).unlink()
        with self.assertRaisesRegex(ValueError,'Missing/outside evidence'):self.check()

    def test_changed_baseline(self):
        (self.root/gate.BASELINE).write_bytes(b'Changed historical page')
        with self.assertRaisesRegex(ValueError,'Changed historical page baseline'):self.check()

    def test_manifest_unreviewed_change(self):
        self.record['reviews'][0]['decision']='REJECT'
        (self.root/gate.MANIFEST).write_text(json.dumps(self.record),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Unreviewed artwork reuse manifest'):self.check()

    def test_missing_manifest(self):
        (self.root/gate.MANIFEST).unlink()
        with self.assertRaisesRegex(ValueError,'Missing/outside evidence'):self.check()

if __name__=='__main__':unittest.main()
