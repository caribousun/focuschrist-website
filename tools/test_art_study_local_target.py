"""URL resolution regression: correct roots without bypassing existence checks."""
import importlib.util
import os
import sys
from pathlib import Path
import unittest

SITE = Path(os.environ.get('SITE_ROOT', Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(SITE / 'tools'))
spec = importlib.util.spec_from_file_location('art_study_enrichment_qa', SITE / 'tools/art_study_enrichment_qa.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)

class LocalTargetTests(unittest.TestCase):
    def setUp(self):
        self.page = SITE / 'art-study/the-good-shepherd.html'

    def test_root_relative_existing_destination(self):
        target = qa.local_target(self.page, '/art-study/the-living-christ.html?from=study#begin')
        self.assertEqual(target, (SITE / 'art-study/the-living-christ.html').resolve())
        self.assertTrue(target.is_file())

    def test_root_relative_missing_stays_missing(self):
        target = qa.local_target(self.page, '/missing-art-study-fixture-never-create.html')
        self.assertEqual(target, (SITE / 'missing-art-study-fixture-never-create.html').resolve())
        self.assertFalse(target.is_file())

    def test_ordinary_relative_keeps_page_directory(self):
        self.assertEqual(qa.local_target(self.page, 'be-still.html#begin'), (SITE / 'art-study/be-still.html').resolve())
        self.assertEqual(qa.local_target(self.page, '../art.html'), (SITE / 'art.html').resolve())

    def test_external_and_fragment_links_are_not_local_files(self):
        for href in ['https://www.churchofjesuschrist.org/study/scriptures/nt/john/10', '#begin', 'mailto:review@example.test', 'tel:123']:
            with self.subTest(href=href):
                self.assertIsNone(qa.local_target(self.page, href))

    def test_path_escape_remains_detectable(self):
        target = qa.local_target(self.page, '/../../outside-fixture.html')
        self.assertFalse(target.is_relative_to(SITE.resolve()))

if __name__ == '__main__':
    unittest.main()
