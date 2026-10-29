import unittest
from pathlib import Path
import timeline_51_search_successor as successor
ROOT=Path(__file__).resolve().parents[1]
class SearchSuccessorTests(unittest.TestCase):
    def test_reconstructs_exact_prior_index(self):
        raw=(ROOT/'site-search-index.json').read_bytes()
        previous=successor.restore(raw)
        self.assertEqual(successor.sha(previous),'abcd13069b734ca5f25ecc003abef56717093b73c31e336ae84bd3d647ffabf1')
    def test_rejects_modified_index(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed event search index'):
            successor.restore((ROOT/'site-search-index.json').read_bytes()+b' ')
    def test_actual_producer(self):
        self.assertEqual(successor.validate_current()['changed_records'],56)
if __name__=='__main__': unittest.main()
