"""Exact reviewed page binding and adversarial mutations; run from repository root."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('mandate', ROOT / 'tools/art_study_current_mandate_qa.py')
mandate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mandate)

class BytesPage:
    def __init__(self, raw):
        self.raw = raw
    def read_bytes(self):
        return self.raw

class ExactFeaturedBinding(unittest.TestCase):
    def test_four_routes_accept_only_reviewed_bytes_or_exact_css_inverse(self):
        self.assertEqual(len(mandate.REVIEWED_PAGE_HASHES), 4)
        for route, expected in mandate.REVIEWED_PAGE_HASHES.items():
            with self.subTest(route=route):
                raw = (ROOT / route).read_bytes()
                self.assertTrue(mandate.reviewed_page_binding(BytesPage(raw), route, expected))
                old = raw.replace(mandate.CURRENT_SHARED_STYLE, mandate.OLD_SHARED_STYLE)
                self.assertTrue(mandate.reviewed_page_binding(BytesPage(old), route, expected))
                mutations = {
                    'body': raw + b'changed',
                    'duplicate_answer': raw + mandate.CURRENT_ANSWER_STYLE,
                    'mixed_answer': raw + mandate.OLD_ANSWER_STYLE,
                    'unknown_answer_version': raw.replace(mandate.CURRENT_ANSWER_STYLE, b'answer-styles.css?v=unknown'),
                    'whitespace': raw + b' ',
                    'duplicate_current_link': raw + mandate.CURRENT_SHARED_STYLE,
                    'old_and_current': raw + mandate.OLD_SHARED_STYLE,
                    'unknown_version': raw.replace(b'20261005-mobile-study-rows-1', b'20261004-unknown'),
                    'source_href': raw.replace(b'https://www.churchofjesuschrist.org/', b'https://example.com/'),
                    'different_css': raw.replace(b'answer-styles.css', b'other-styles.css'),
                }
                for label, changed in mutations.items():
                    with self.subTest(mutation=label):
                        self.assertNotEqual(changed, raw)
                        self.assertFalse(mandate.reviewed_page_binding(BytesPage(changed), route, expected))
                self.assertFalse(mandate.reviewed_page_binding(BytesPage(raw), 'not-reviewed.html', expected))
                self.assertFalse(mandate.reviewed_page_binding(BytesPage(raw), route, '0' * 64))

if __name__ == '__main__':
    unittest.main()
