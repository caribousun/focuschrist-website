import unittest
from pathlib import Path
import timeline_51_source_successor as successor

ROOT=Path(__file__).resolve().parents[1]

class TimelineDestinationSuccessorTests(unittest.TestCase):
    def test_exact_sources_reconstruct_prior_bytes(self):
        for name in sorted(successor.FILES):
            with self.subTest(name=name):
                current=(ROOT/name).read_bytes()
                prior=successor.restore(name,current)
                self.assertEqual(successor.advance_exact(name,prior),current)
                self.assertEqual(successor.advance_exact(name,prior+b' '),prior+b' ')
                self.assertEqual(successor.sha(prior),{
                    'church-history.html':'bc93f2c78c8899cf88084fe7d9c08486ece74d1a6c91f0845643b24ef0ce8c0d',
                    'pioneers.html':'b9275099d3a124a940e3c402d905c7994be2fbaf6fe69caebf28481e84078e4f',
                    'jesus-christ/mortal-ministry.html':'c29736b0c5fc00222b6031251513d01526881e044ce9acc28c749e8025fd7895',
                    'jesus-christ/restoration-and-today.html':'e8d47086219a5722fdac5ad10e89894057950dfe38e39f2f3e3a2d90574bb660',
                    'timeline-images.js':'0896201a1fdc35eab8333873ce9f3cd18b44fd948e9a04f2f93aa5d403618c18',
                    'timelines/life-of-christ-journey-map.html':'e8e6124f50a19d7cac839ec8b405e33b036284c57b8182d2e7776dc8af90c418',
                    'timelines/latter-day-saint-church-history-timeline.html':'d3aa8f0ee8947f1c1f8b6402cd5e0361e9c7498de84d91c058c608998431edc5',
                    'timelines/willie-and-martin-handcart-map.html':'1644dc3a513e34664f1f0db749d5e7c5c6776f59324a6a8e76ad0e913d6e21db',
                }[name])
    def test_changed_current_bytes_rejected(self):
        for name in sorted(successor.FILES):
            with self.subTest(name=name):
                current=(ROOT/name).read_bytes()
                with self.assertRaisesRegex(ValueError,'Unreviewed timeline destination source'):
                    successor.restore(name,current+b' ')
    def test_unrelated_file_unchanged(self):
        self.assertEqual(successor.restore('unrelated.txt',b'safe'),b'safe')

if __name__=='__main__': unittest.main()
