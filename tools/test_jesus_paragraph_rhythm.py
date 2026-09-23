"""Check saved chapter prose rhythm independently of renderer placement rules.

Captions, source-only links and navigation-card descriptions are not narrative.
Grouped subsection boundaries and optional reflection disclosures do not reset
a prose run. This structural test complements semantic and browser review.
"""
import unittest
from pathlib import Path

from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'jj-kicker', 'fc-eyebrow', 'fc-study-visual-sources',
            'fc-resource-card__source', 'fc-resource-card__kind', 'fc-footnote',
            'jj-actions', 'jj-card', 'fc-resource-card'}


def parse(text):
    doc = Document()
    doc.feed(text)
    return doc.root


def ancestors(node):
    while node is not None:
        yield node
        node = node.parent


def unlinked_text(node):
    if node.tag == 'a':
        return ''
    return ''.join(c if isinstance(c, str) else unlinked_text(c)
                   for c in node.content)


def narrative_events(section):
    for node in section.walk():
        if node.tag == 'img' and node.attrs.get('src'):
            yield 'image'
        elif node.tag == 'p' and node.text().strip():
            lineage = list(ancestors(node))
            if any(n.tag in {'figure', 'figcaption', 'nav'} or
                   any(n.has(cls) for cls in EXCLUDED) for n in lineage):
                continue
            if any(n.tag == 'article' for n in lineage) and any(
                    n.has('fc-study-grid') for n in lineage):
                continue
            if any(n.tag == 'a' for n in node.walk()) and not unlinked_text(
                    node).strip(' \t\n\r.·|,;:—–-'):
                continue
            yield 'paragraph'


def rhythm_errors(document):
    nodes = list(document.walk())
    ids = {n.attrs.get('id'): n for n in nodes if n.attrs.get('id')}
    navs = [n for n in nodes if n.has('jj-local-nav')]
    if len(navs) != 1:
        return ['Expected one chapter navigation']
    targets = [n.attrs['href'][1:] for n in navs[0].walk()
               if n.tag == 'a' and n.attrs.get('href', '').startswith('#')]
    errors, groups = [], {}
    for target in targets:
        if target not in ids:
            errors.append('Missing chapter: ' + target)
            continue
        section = ids[target]
        leader = section.attrs.get('data-chapter-group', target)
        groups.setdefault(leader, []).extend(narrative_events(section))
    for leader, events in groups.items():
        run = 0
        for event in events + ['end']:
            if event == 'paragraph':
                run += 1
            else:
                if run > 2:
                    errors.append(f'{leader}: {run} narrative paragraphs before {event}')
                run = 0
    return errors


class ParagraphRhythm(unittest.TestCase):
    def fixture(self, content, joined=''):
        nav = '<nav class="jj-local-nav"><a href="#one">One</a>'
        if joined:
            nav += '<a href="#two">Two</a>'
        html = nav + '</nav><section id="one">' + content + '</section>'
        if joined:
            html += '<section id="two" data-chapter-group="one">' + joined + '</section>'
        return rhythm_errors(parse(html))

    def test_all_saved_journey_chapters(self):
        paths = [ROOT / 'answers/jesus-christ-latter-day-saint-beliefs.html',
                 ROOT / 'birth-of-christ.html',
                 *sorted((ROOT / 'jesus-christ').rglob('*.html'))]
        self.assertEqual(len(paths), 78)
        for path in paths:
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertEqual(rhythm_errors(parse(path.read_text(encoding='utf-8'))), [])

    def test_centered_picture_is_valid(self):
        self.assertEqual(self.fixture('<p>A</p><p>B</p><img src="a.webp"><p>C</p><p>D</p>'), [])

    def test_top_picture_with_four_paragraphs_fails(self):
        self.assertTrue(self.fixture('<img src="a.webp">' + '<p>Prose</p>' * 4))

    def test_leading_three_paragraphs_fail(self):
        self.assertTrue(self.fixture('<p>Prose</p>' * 3 + '<img src="a.webp">'))

    def test_group_boundary_does_not_reset_run(self):
        self.assertTrue(self.fixture('<img src="a.webp"><p>A</p><p>B</p>', '<p>C</p>'))

    def test_optional_reflection_counts(self):
        self.assertTrue(self.fixture('<img src="a.webp"><p>A</p><p>B</p><details><p>C</p></details>'))

    def test_captions_sources_and_card_copy_are_excluded(self):
        content = '<figure><img src="a.webp"><figcaption><p>Caption</p></figcaption></figure>'
        content += '<p>A</p><p><a href="source">Luke 15</a> · <a href="source2">Matthew 18</a></p>'
        content += '<p class="fc-study-visual-sources">Sources</p><p class="jj-kicker">Study</p>'
        content += '<a class="jj-card"><p>Destination description</p></a><p>B</p>'
        self.assertEqual(self.fixture(content), [])

    def test_linked_narrative_still_counts(self):
        self.assertTrue(self.fixture('<img src="a.webp"><p>A</p><p>B</p><p>Read <a href="source">Luke</a> with care.</p>'))


if __name__ == '__main__':
    unittest.main()
