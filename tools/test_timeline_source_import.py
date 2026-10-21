"""Synthetic review records test rejection, never production review approval."""
import copy,json,hashlib,shutil,tempfile,unittest
from pathlib import Path
import timeline_source_import as gate

class TimelineImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        real=Path(__file__).resolve().parents[1]
        cls.record=json.loads((real/gate.MANIFEST).read_text(encoding='utf-8'))
        spec=cls.record['spec']
        for item in spec['assets']+spec['licenses']+[spec['page'],spec['credits'],spec['lineage']]:
            dest=cls.root/item['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(real/item['path'],dest)
        cls.record['status']='REVIEWED_EXACT_SOURCE_IMPORT';cls.record['reviews']=[]
        for role in ['Albert','Fermi','Newton']:
            name='docs/world-scripture-import/synthetic-'+role+'.txt';raw=b'Synthetic test fixture, not actual concurrence.'
            (cls.root/name).write_bytes(raw)
            cls.record['reviews'].append({'reviewer':role,'decision':'CONCUR','spec_sha256':gate.canonical(spec),'finished_pixels':True,'source_rights_checked':True,'evidence':{'path':name,'sha256':hashlib.sha256(raw).hexdigest()}})
        cls.paths={a['path'] for a in spec['assets']}

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def run_record(self, record, covered=None, rejected=None, repin=False):
        original=self.record
        expected=gate.canonical(record['spec'] if repin else original['spec'])
        if repin:
            for r in record['reviews']:r['spec_sha256']=expected
        (self.root/gate.MANIFEST).write_text(json.dumps(record),encoding='utf-8')
        return gate.validate(self.root,self.paths,covered or set(),rejected or set(),expected,gate.canonical(record['reviews'] if repin else original['reviews']))

    def test_positive_exact_fixture(self):self.assertEqual(self.run_record(copy.deepcopy(self.record)),self.paths)

    def test_pending_cannot_pass(self):
        r=copy.deepcopy(self.record);r['status']='PENDING_FINISHED_REVIEW'
        with self.assertRaisesRegex(ValueError,'unfinished'):self.run_record(r)

    def test_forged_finished_review_rejected(self):
        r=copy.deepcopy(self.record);r['reviews'][0]['evidence']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'unreviewed finished'):self.run_record(r)

    def test_missing_asset_rejected_even_if_rebound(self):
        r=copy.deepcopy(self.record);r['spec']['assets'].pop()
        with self.assertRaisesRegex(ValueError,'missing or duplicate'):self.run_record(r,repin=True)

    def test_misclassified_creation_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['precreation_claim']=True
        with self.assertRaisesRegex(ValueError,'misclassified'):self.run_record(r,repin=True)

    def test_wrong_owner_page_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['page']['path']='index.html'
        with self.assertRaisesRegex(ValueError,'wrong owning'):self.run_record(r,repin=True)

    def test_bad_bytes_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['assets'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'changed bytes'):self.run_record(r,repin=True)

    def test_path_escape_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['lineage']['path']='../escape.md'
        with self.assertRaisesRegex(ValueError,'unsafe path'):self.run_record(r,repin=True)

    def test_rejected_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'rejected or renamed'):self.run_record(copy.deepcopy(self.record),rejected={self.record['spec']['assets'][0]['sha256']})

    def test_duplicate_coverage_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlapping'):self.run_record(copy.deepcopy(self.record),covered={next(iter(self.paths))})

    def test_missing_license_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['licenses'].pop()
        with self.assertRaisesRegex(ValueError,'missing bundled'):self.run_record(r,repin=True)

    def test_unknown_reviewer_rejected(self):
        r=copy.deepcopy(self.record);r['reviews'][0]['reviewer']='Unapproved'
        with self.assertRaisesRegex(ValueError,'missing independent'):self.run_record(r,repin=True)

    def test_wrong_role_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['assets'][0]['role']='new-generation'
        with self.assertRaisesRegex(ValueError,'incorrect provenance'):self.run_record(r,repin=True)

    def test_wrong_dimensions_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['assets'][0]['dimensions']=[1,1]
        with self.assertRaisesRegex(ValueError,'changed dimensions'):self.run_record(r,repin=True)

    def test_wrong_archive_rejected(self):
        r=copy.deepcopy(self.record);r['spec']['archive_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'changed source archive'):self.run_record(r,repin=True)

    def test_negative_review_rejected(self):
        r=copy.deepcopy(self.record);r['reviews'][0]['decision']='REJECT'
        with self.assertRaisesRegex(ValueError,'stale or negative'):self.run_record(r,repin=True)

    def test_reviewed_pixels_required(self):
        r=copy.deepcopy(self.record);r['reviews'][0]['finished_pixels']=False
        with self.assertRaisesRegex(ValueError,'unperformed'):self.run_record(r,repin=True)

    def test_mismatched_credit_rejected(self):
        r=copy.deepcopy(self.record)
        next(a for a in r['spec']['assets'] if a['role']=='source-photo')['credit_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'unreviewed attribution'):self.run_record(r,repin=True)

    def test_public_domain_not_fabricated_license(self):
        credits=json.loads((self.root/self.record['spec']['credits']['path']).read_text(encoding='utf-8'))
        empty=[c for c in credits.values() if not c['license_url']]
        self.assertEqual(len(empty),51)
        self.assertTrue(all(c['license']=='Public domain' for c in empty))
        self.assertEqual(self.run_record(copy.deepcopy(self.record)),self.paths)

if __name__=='__main__':unittest.main()
