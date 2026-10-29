"""A retirement exception must require the exact redirect and canonical sitemap."""
import tempfile
import unittest
from pathlib import Path
from sitewide_artwork_review_qa import exclude_verified_emma_redirect
from owner_journey_successor import RETIRED

ROOT = Path(__file__).resolve().parents[1]

class VerifiedRedirectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / RETIRED).parent.mkdir(parents=True)
        for name in (RETIRED, 'sitemap.xml'):
            (self.root / name).write_bytes((ROOT / name).read_bytes())

    def test_only_the_verified_retired_route_is_excluded(self):
        pages = {RETIRED, 'history/unexpected.html', 'index.html'}
        exclude_verified_emma_redirect(self.root, pages)
        self.assertEqual(pages, {'history/unexpected.html', 'index.html'})

    def test_changed_redirect_or_sitemap_fails_closed(self):
        for name in (RETIRED, 'sitemap.xml'):
            path = self.root / name
            original = path.read_bytes()
            path.write_bytes(original + b' ')
            with self.subTest(path=name), self.assertRaises(AssertionError):
                exclude_verified_emma_redirect(self.root, {RETIRED})
            path.write_bytes(original)

    def test_missing_redirect_not_silently_excused(self):
        with self.assertRaises(KeyError):
            exclude_verified_emma_redirect(self.root, {'index.html'})

if __name__ == '__main__':
    unittest.main()
