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
                    'unknown_answer_version': raw.replace(mandate.CONTAINED_ANSWER_STYLE, b'answer-styles.css?v=unknown'),
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

    def test_exact_baseline_and_hero_token_inverses(self):
        self.assertEqual(mandate.VISIBLE_ART_ROUTES, {
            'art-study/be-still.html', 'art-study/suffer-the-little-children.html',
            'art-study/the-good-shepherd.html',
        })
        for route, expected in mandate.REVIEWED_PAGE_HASHES.items():
            raw = (ROOT / route).read_bytes()
            versions = [
                (mandate.CURRENT_COMMON_SCRIPT, mandate.OLD_COMMON_SCRIPT),
                (mandate.CONTAINED_ANSWER_STYLE, mandate.BUFFER_ANSWER_STYLE),
                (mandate.CURRENT_ART_STYLE, mandate.OLD_ART_STYLE),
            ]
            if route in mandate.VISIBLE_ART_ROUTES:
                versions.append((mandate.CURRENT_HERO_SCRIPT, mandate.OLD_HERO_SCRIPT))
                versions.extend(mandate.VIEWER_TOKEN_INVERSES)
            for current, previous in versions:
                with self.subTest(route=route, token=current):
                    self.assertEqual(raw.count(current), 1)
                    self.assertTrue(mandate.reviewed_page_binding(BytesPage(raw.replace(current, previous)), route, expected))
                    for mutation in (raw + current, raw + previous,
                                     raw.replace(current, current + b'-unknown'),
                                     raw.replace(current, b'unrelated.js?v=1')):
                        self.assertFalse(mandate.reviewed_page_binding(BytesPage(mutation), route, expected))
            if route not in mandate.VISIBLE_ART_ROUTES:
                self.assertEqual(raw.count(mandate.OLD_HERO_SCRIPT), 1)
                changed = raw.replace(mandate.OLD_HERO_SCRIPT, mandate.CURRENT_HERO_SCRIPT)
                self.assertFalse(mandate.reviewed_page_binding(BytesPage(changed), route, expected))
                self.assertFalse(mandate.reviewed_page_binding(BytesPage(raw + mandate.VISIBLE_IMAGE_HELPER), route, expected))
                for current, previous in mandate.VIEWER_TOKEN_INVERSES:
                    self.assertFalse(mandate.reviewed_page_binding(BytesPage(raw.replace(previous, current)), route, expected))
            else:
                self.assertEqual(raw.count(mandate.VISIBLE_IMAGE_HELPER), 1)
                for mutation in (
                    raw + mandate.VISIBLE_IMAGE_HELPER,
                    raw.replace(mandate.VISIBLE_IMAGE_HELPER, mandate.VISIBLE_IMAGE_HELPER.replace(b'visible-art-1', b'unknown')),
                    raw.replace(mandate.VISIBLE_IMAGE_HELPER, mandate.VISIBLE_IMAGE_HELPER.replace(b'defer', b'async')),
                ):
                    self.assertFalse(mandate.reviewed_page_binding(BytesPage(mutation), route, expected))

if __name__ == '__main__':
    unittest.main()
