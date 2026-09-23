"""Verify the saved Shorts cards, generator freshness and existing Watch content."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '0c1a128074455293c59d2ee10591e53e842be87f'


def nodes(text):
    doc = Document()
    doc.feed(text)
    return list(doc.root.walk())


def signature(node):
    return node.tag, tuple(sorted(node.attrs.items())), tuple(
        item if isinstance(item, str) else signature(item) for item in node.content)


class WatchShorts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / 'watch.html').read_text(encoding='utf-8')
        cls.data = json.loads((ROOT / 'docs/watch-shorts.json').read_text(encoding='utf-8'))

    def test_four_distinct_ordered_native_previews_and_fallbacks(self):
        records = self.data['shorts']
        ids = [r['id'] for r in records]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(ids)), 4)
        cards = [n for n in nodes(self.page) if n.has('watch-short')]
        self.assertEqual([c.attrs.get('data-short-id') for c in cards], ids)
        for record, card in zip(records, cards):
            with self.subTest(video=record['id']):
                self.assertRegex(record['id'], r'^[A-Za-z0-9_-]{11}$')
                children = list(card.walk())
                image = next(n for n in children if n.tag == 'img')
                self.assertEqual(image.attrs['src'], record['thumbnail'])
                thumbnail = urlsplit(image.attrs['src'])
                self.assertEqual((thumbnail.scheme, thumbnail.netloc), ('https', 'i.ytimg.com'))
                self.assertTrue(thumbnail.path.startswith('/vi/' + record['id'] + '/'))
                self.assertEqual((image.attrs['width'], image.attrs['height']), ('405', '720'))
                self.assertEqual(next(n.text() for n in children if n.tag == 'h3'), record['title'])
                links = [n for n in children if n.tag == 'a']
                self.assertEqual(len(links), 3)
                self.assertTrue(all(n.attrs['href'] == 'https://www.youtube.com/shorts/' + record['id'] for n in links))
                triggers = [n for n in links if 'data-short-play' in n.attrs]
                self.assertEqual(len(triggers), 2)
                self.assertTrue(all(n.attrs['data-short-play'] == record['id'] for n in triggers))
                self.assertEqual(sum(n.has('watch-short-preview') for n in triggers), 1)
                self.assertEqual(sum(n.has('watch-short-open') for n in triggers), 1)
                self.assertFalse(any(n.has('watch-short-open') for n in next(n for n in children if n.has('watch-short-media')).walk()))
                self.assertFalse(any(n.tag == 'iframe' for n in children))

    def test_original_hero_opening_and_twenty_church_cards_preserved(self):
        old = nodes(subprocess.check_output(['git', 'show', BASELINE + ':watch.html'], cwd=ROOT).decode('utf-8'))
        current = nodes(self.page)
        for label, predicate, count in (
            ('hero', lambda n: n.has('fc-visual-hero'), 1),
            ('opening', lambda n: n.has('fc-page-intro'), 1),
            ('Church video cards', lambda n: 'data-watch-video' in n.attrs, 20),
        ):
            with self.subTest(part=label):
                before = [signature(n) for n in old if predicate(n)]
                after = [signature(n) for n in current if predicate(n)]
                self.assertEqual(len(before), count)
                self.assertEqual(after, before)

    def test_generator_current(self):
        result = subprocess.run([sys.executable, str(ROOT / 'tools/build_watch_shorts.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generator_rejects_stale_saved_card_without_writing(self):
        with tempfile.TemporaryDirectory(prefix='watch-shorts-qa-') as folder:
            temporary = Path(folder)
            (temporary / 'tools').mkdir()
            (temporary / 'docs').mkdir()
            shutil.copyfile(ROOT / 'tools/build_watch_shorts.py', temporary / 'tools/build_watch_shorts.py')
            shutil.copyfile(ROOT / 'docs/watch-shorts.json', temporary / 'docs/watch-shorts.json')
            stale = self.page.replace('Latest from Focus Shorts', 'Stale saved heading', 1)
            self.assertNotEqual(stale, self.page)
            page = temporary / 'watch.html'
            page.write_text(stale, encoding='utf-8')
            before = page.read_bytes()
            result = subprocess.run([sys.executable, str(temporary / 'tools/build_watch_shorts.py'), '--check'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('stale', result.stdout + result.stderr)
            self.assertEqual(page.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
