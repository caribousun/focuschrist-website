"""Exact reviewed page binding and adversarial mutations; run from repository root."""
import importlib.util
import unittest
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('mandate', ROOT / 'tools/art_study_current_mandate_qa.py')
mandate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mandate)

# Preserve historical token tests against the exact page preceding the reviewed chalk addition.
def historical_test_bytes(route):
    raw = (ROOT / route).read_bytes()
    if route != 'art-study/suffer-the-little-children.html':
        return raw
    assert hashlib.sha256(raw).hexdigest() == 'dfb6e15e77cfc2930ae3b3837819cdf989310cbf7d0ae836cf9fd613e8e83249'
    assert raw.count(b'<link rel="stylesheet" href="../four-scene-artwork.css">\n') == 1
    raw = raw.replace(b'<link rel="stylesheet" href="../four-scene-artwork.css">\n', b'', 1)
    assert raw.count(b'<section class="fc-deep-study" id="christ-children-colorful-day" data-connected-study>\n<h2>Delight in what a child creates</h2>\n<figure class="fc-art-story" data-exclusive-artwork="christ-children-colorful-day"><a data-art-study-supporting href="../assets/page-art/christ-world/christ-children-colorful-day-full.webp" aria-haspopup="dialog" aria-label="Explore artwork: Delight in what a child creates" data-full-image-alt="Christ holds yellow chalk beside a sun drawing while children make colorful pictures in a courtyard." data-topic-study="#continue-study" data-topic-study-label="Continue the surrounding study"><img style="--study-image-ratio:1586/992;aspect-ratio:auto 1586/992" src="../assets/page-art/christ-world/christ-children-colorful-day-960.webp" srcset="../assets/page-art/christ-world/christ-children-colorful-day-480.webp 480w, ../assets/page-art/christ-world/christ-children-colorful-day-960.webp 960w, ../assets/page-art/christ-world/christ-children-colorful-day-full.webp 1586w" sizes="(max-width:700px) calc(100vw - 36px), 960px" width="1586" height="992" loading="lazy" decoding="async" alt="Christ holds yellow chalk beside a sun drawing while children make colorful pictures in a courtyard."></a><figcaption><p class="fc-study-visual-label">Explore and study</p><p>A bright afternoon, with something for everyone to add.</p><p>A rainbow spreads across the courtyard, and Christ has added a yellow sun beside it. The children have chalk and ideas of their own. He pauses to enjoy the boy&#x27;s company, joining the play with the same attention He gives the drawing. There is time to create, look and laugh together.</p><p>In <a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&amp;id=p13-p16#p13" target="_blank" rel="noopener noreferrer">Mark 10</a>, Jesus welcomes children and blesses them. Giving a child our attention can begin with taking an interest in what they are making. We can join in without taking over, listen to their ideas and share their delight. Being together is part of the gift.</p><p>What is a child eager to show you?</p><p class="fc-study-visual-sources"><a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&amp;id=p13-p16#p13" target="_blank" rel="noopener noreferrer">Mark 10:13-16</a></p></figcaption></figure>\n</section>\n') == 1
    raw = raw.replace(b'<section class="fc-deep-study" id="christ-children-colorful-day" data-connected-study>\n<h2>Delight in what a child creates</h2>\n<figure class="fc-art-story" data-exclusive-artwork="christ-children-colorful-day"><a data-art-study-supporting href="../assets/page-art/christ-world/christ-children-colorful-day-full.webp" aria-haspopup="dialog" aria-label="Explore artwork: Delight in what a child creates" data-full-image-alt="Christ holds yellow chalk beside a sun drawing while children make colorful pictures in a courtyard." data-topic-study="#continue-study" data-topic-study-label="Continue the surrounding study"><img style="--study-image-ratio:1586/992;aspect-ratio:auto 1586/992" src="../assets/page-art/christ-world/christ-children-colorful-day-960.webp" srcset="../assets/page-art/christ-world/christ-children-colorful-day-480.webp 480w, ../assets/page-art/christ-world/christ-children-colorful-day-960.webp 960w, ../assets/page-art/christ-world/christ-children-colorful-day-full.webp 1586w" sizes="(max-width:700px) calc(100vw - 36px), 960px" width="1586" height="992" loading="lazy" decoding="async" alt="Christ holds yellow chalk beside a sun drawing while children make colorful pictures in a courtyard."></a><figcaption><p class="fc-study-visual-label">Explore and study</p><p>A bright afternoon, with something for everyone to add.</p><p>A rainbow spreads across the courtyard, and Christ has added a yellow sun beside it. The children have chalk and ideas of their own. He pauses to enjoy the boy&#x27;s company, joining the play with the same attention He gives the drawing. There is time to create, look and laugh together.</p><p>In <a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&amp;id=p13-p16#p13" target="_blank" rel="noopener noreferrer">Mark 10</a>, Jesus welcomes children and blesses them. Giving a child our attention can begin with taking an interest in what they are making. We can join in without taking over, listen to their ideas and share their delight. Being together is part of the gift.</p><p>What is a child eager to show you?</p><p class="fc-study-visual-sources"><a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&amp;id=p13-p16#p13" target="_blank" rel="noopener noreferrer">Mark 10:13-16</a></p></figcaption></figure>\n</section>\n', b'', 1)
    assert raw.count(b'</main><footer class="fc-footer" data-focuschrist-footer="standard"><p>\xc2\xa9 2026 focusChrist. All are welcome here.</p><p><a href="https://www.youtube.com/@theRisen636" target="_blank" rel="noopener noreferrer">@theRisen636</a></p><p data-focuschrist-independence="footer">focusChrist is an independent faith-based website and is not an official website of, sponsored by, or endorsed by The Church of Jesus Christ of Latter-day Saints. For official Church information, visit <a href="https://www.churchofjesuschrist.org/" target="_blank" rel="noopener noreferrer">ChurchofJesusChrist.org</a>.</p><p data-focuschrist-artwork-disclosure="footer">Artwork on focusChrist includes AI-generated artistic interpretations. Illustrative and reconstructed details are not photographs or eyewitness records of the people or events shown.</p></footer><script>function toggleMenu(){var m=document.getElementById(\'hamburgerMenu\');if(m)m.classList.toggle(\'show\');}</script><script src="../four-scene-artwork.js" defer></script>\n</body></html>\n') == 1
    raw = raw.replace(b'</main><footer class="fc-footer" data-focuschrist-footer="standard"><p>\xc2\xa9 2026 focusChrist. All are welcome here.</p><p><a href="https://www.youtube.com/@theRisen636" target="_blank" rel="noopener noreferrer">@theRisen636</a></p><p data-focuschrist-independence="footer">focusChrist is an independent faith-based website and is not an official website of, sponsored by, or endorsed by The Church of Jesus Christ of Latter-day Saints. For official Church information, visit <a href="https://www.churchofjesuschrist.org/" target="_blank" rel="noopener noreferrer">ChurchofJesusChrist.org</a>.</p><p data-focuschrist-artwork-disclosure="footer">Artwork on focusChrist includes AI-generated artistic interpretations. Illustrative and reconstructed details are not photographs or eyewitness records of the people or events shown.</p></footer><script>function toggleMenu(){var m=document.getElementById(\'hamburgerMenu\');if(m)m.classList.toggle(\'show\');}</script><script src="../four-scene-artwork.js" defer></script>\n</body></html>\n', b'</main><footer class="fc-footer" data-focuschrist-footer="standard"><p>\xc2\xa9 2026 focusChrist. All are welcome here.</p><p><a href="https://www.youtube.com/@theRisen636" target="_blank" rel="noopener noreferrer">@theRisen636</a></p><p data-focuschrist-independence="footer">focusChrist is an independent faith-based website and is not an official website of, sponsored by, or endorsed by The Church of Jesus Christ of Latter-day Saints. For official Church information, visit <a href="https://www.churchofjesuschrist.org/" target="_blank" rel="noopener noreferrer">ChurchofJesusChrist.org</a>.</p><p data-focuschrist-artwork-disclosure="footer">Artwork on focusChrist includes AI-generated artistic interpretations. Illustrative and reconstructed details are not photographs or eyewitness records of the people or events shown.</p></footer><script>function toggleMenu(){var m=document.getElementById(\'hamburgerMenu\');if(m)m.classList.toggle(\'show\');}</script></body></html>\n', 1)
    assert hashlib.sha256(raw).hexdigest() == '2770a4f6e18a72cf2dcfba00f3d18188bd72b636fe91a4bf2c75c5808655c7f2'
    return raw

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
                raw = historical_test_bytes(route)
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
            raw = historical_test_bytes(route)
            versions = [
                (mandate.CURRENT_COMMON_SCRIPT, mandate.OLD_COMMON_SCRIPT),
                (mandate.CONTAINED_ANSWER_STYLE, mandate.BUFFER_ANSWER_STYLE),
                (mandate.CURRENT_ART_STYLE, mandate.OLD_ART_STYLE),
            ]
            for current, previous in [
                (b'full-image-viewer.js?v=20261009-titled-downloads-1', b'full-image-viewer.js?v=20261006-versions-1' if route in mandate.VISIBLE_ART_ROUTES else b'full-image-viewer.js?v=20260914-reopen-1'),
                (b'full-image-viewer.css?v=20261007-viewer-controls-1', b'full-image-viewer.css?v=20261006-versions-1'),
                (b'topic-artwork-details.js?v=20261009-settled-continue-2', b'topic-artwork-details.js?v=20261004-study-return-1'),
            ]:
                self.assertEqual(raw.count(current), 1)
                for mutation in (raw + current, raw + previous, raw.replace(current, previous),
                                 raw.replace(current, current + b'-unknown'), raw.replace(current, b'unrelated.js?v=1')):
                    self.assertNotEqual(mutation, raw)
                    self.assertFalse(mandate.reviewed_page_binding(BytesPage(mutation), route, expected))
            if route in mandate.VISIBLE_ART_ROUTES:
                versions.append((mandate.CURRENT_HERO_SCRIPT, mandate.OLD_HERO_SCRIPT))
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
                for current, previous in (pair for pair in mandate.VIEWER_TOKEN_INVERSES if b'.js?' in pair[0]):
                    changed = raw.replace(b'full-image-viewer.js?v=20261009-titled-downloads-1', current)
                    self.assertNotEqual(changed, raw)
                    self.assertFalse(mandate.reviewed_page_binding(BytesPage(changed), route, expected))
            else:
                self.assertEqual(raw.count(mandate.VISIBLE_IMAGE_HELPER), 1)
                for mutation in (
                    raw + mandate.VISIBLE_IMAGE_HELPER,
                    raw.replace(mandate.VISIBLE_IMAGE_HELPER, mandate.VISIBLE_IMAGE_HELPER.replace(b'visible-art-1', b'unknown')),
                    raw.replace(mandate.VISIBLE_IMAGE_HELPER, mandate.VISIBLE_IMAGE_HELPER.replace(b'defer', b'async')),
                ):
                    self.assertFalse(mandate.reviewed_page_binding(BytesPage(mutation), route, expected))


    def test_current_children_exact_binding(self):
        route = 'art-study/suffer-the-little-children.html'
        raw = (ROOT / route).read_bytes()
        expected = 'dfb6e15e77cfc2930ae3b3837819cdf989310cbf7d0ae836cf9fd613e8e83249'
        self.assertTrue(mandate.reviewed_page_binding(BytesPage(raw), route, expected))
        for changed in (raw + b' ', raw.replace(b'christ-children-colorful-day', b'changed-child-scene'), raw.replace(b'Christ', b'Changed', 1)):
            self.assertNotEqual(changed, raw)
            self.assertFalse(mandate.reviewed_page_binding(BytesPage(changed), route, expected))

if __name__ == '__main__':
    unittest.main()
