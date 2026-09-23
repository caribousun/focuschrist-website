"""Visitor-facing visual coverage, bookmark and reference-ownership regressions.

Reads saved HTML and canonical content; never calls the page builders.
Run with unittest discovery alongside the existing journey review gates.
"""
import json
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/jesus-journey'
PARENT = '/answers/jesus-christ-latter-day-saint-beliefs.html'
LEGACY_OWNERS = {
    '/assets/page-art/birth-of-christ/12-nativity-hero-800.webp': '/birth-of-christ.html',
    '/assets/page-art/birth-of-christ/03-nephi-vision-800.webp': '/birth-of-christ.html',
    '/assets/page-art/atonement/servant-960.webp': '/atonement.html',
    '/assets/history/first-vision-800.webp': '/church-history.html',
    '/assets/page-art/atonement/cross-angled-rear-approved-960.webp': '/atonement.html',
    '/assets/page-art/exclusive/mormon-nephi-purpose-800.webp': '/answers/what-is-the-book-of-mormon.html',
    '/assets/page-art/life-after-death/martha-800.webp': '/answers/what-happens-after-death.html',
    '/assets/page-art/topics/christ-praying-800.webp': '/answers/prayer-and-personal-revelation.html',
}


def parse(text):
    doc = Document()
    doc.feed(text)
    return doc.root


def local_path(value, page):
    return unquote(urlsplit(urljoin('https://focuschrist.com' + page, value)).path)


def is_reference_picture(image, page):
    if image.tag != 'img':
        return False
    if image.has('jj-card-preview'):
        return True
    if page == '/birth-of-christ.html':
        ancestor = image.parent
        while ancestor is not None:
            if ancestor.attrs.get('id') == 'continue-study':
                return True
            ancestor = ancestor.parent
    return False


def group_errors(doc, expected_sections):
    """A bookmark survives even when its section shares a selectable chapter."""
    errors = []
    nodes = list(doc.walk())
    counts = Counter(n.attrs['id'] for n in nodes if n.attrs.get('id'))
    ids = {n.attrs['id']: n for n in nodes if n.attrs.get('id')}
    navs = [n for n in nodes if n.has('jj-local-nav')]
    if len(navs) != 1:
        return ['Expected one chapter navigation']
    nav = navs[0]
    targets = [unquote(n.attrs['href'][1:]) for n in nav.walk()
               if n.tag == 'a' and n.attrs.get('href', '').startswith('#')]
    if len(targets) != len(set(targets)):
        errors.append('Duplicate chapter choice')
    sections = [n for n in nodes if n.has('jj-chapter') and n.parent is nav.parent]
    section_ids = {n.attrs.get('id'): n for n in sections}
    for section in expected_sections:
        sid = section['id']
        if counts[sid] != 1 or sid not in section_ids:
            errors.append('Missing or duplicated preserved anchor: ' + sid)
            continue
        actual = section_ids[sid].attrs.get('data-chapter-group')
        if actual != section.get('chapter_group'):
            errors.append('Canonical chapter grouping lost: ' + sid)
    groups = {}
    for sid in targets:
        if sid not in section_ids:
            errors.append('Chapter link has no direct section: ' + sid)
    for sid, section in section_ids.items():
        if sid not in targets:
            continue  # Related studies and source appendices are not chapter choices.
        leader = section.attrs.get('data-chapter-group', sid)
        owner = section_ids.get(leader)
        if owner is None or leader not in targets:
            errors.append('Missing chapter group leader: ' + sid)
            continue
        if owner.attrs.get('data-chapter-group') or owner.order > section.order:
            errors.append('Chained or forward chapter group: ' + sid)
        groups.setdefault(leader, []).append(section)
    for leader, members in groups.items():
        images = [n for member in members for n in member.walk()
                  if n.tag == 'img' and n.attrs.get('src')]
        if not images:
            errors.append('Selectable chapter has no picture: ' + leader)
    return errors


def reference_errors(doc, page, owner_by_image, documents):
    errors = []
    for image in doc.walk():
        if not is_reference_picture(image, page):
            continue
        source = urlsplit(image.attrs.get('src', ''))
        if source.scheme or source.netloc:
            errors.append('Reference picture must use its saved local asset')
            continue
        asset = local_path(image.attrs.get('src', ''), page)
        owner = owner_by_image.get(asset)
        anchor = image.parent
        while anchor is not None and anchor.tag != 'a':
            anchor = anchor.parent
        if anchor is None:
            errors.append('Reference picture has no link: ' + asset)
            continue
        href = anchor.attrs.get('href', '')
        url = urlsplit(urljoin('https://focuschrist.com' + page, href))
        target = unquote(url.path)
        if owner is None or target != owner or target == page:
            errors.append('Reference must link to its different owning page: ' + asset)
            continue
        if url.netloc != 'focuschrist.com':
            errors.append('Reference owner link leaves the site: ' + asset)
        target_doc = documents.get(target)
        if target_doc is None:
            errors.append('Reference owner page is missing: ' + target)
        elif url.fragment and not any(n.attrs.get('id') == unquote(url.fragment)
                                       for n in target_doc.walk()):
            errors.append('Reference owner bookmark is missing: ' + href)
    return errors


class SavedJourneyVisualCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(name):
            return json.loads((DATA / name).read_text(encoding='utf-8'))
        cls.parent = read('main-content.json')
        cls.pages = [cls.parent]
        for name in ('branch-content-reviewed.json', 'parable-content-reviewed.json',
                     'parable-collections-reviewed.json'):
            cls.pages.extend(read(name))
        cls.registry = read('artworks.json')
        cls.owners = dict(LEGACY_OWNERS)
        for record in cls.registry.values():
            if record.get('thumbnail'):
                asset = '/' + record['thumbnail']
                owner = '/' + record['owner']
                if asset in cls.owners and cls.owners[asset] != owner:
                    raise AssertionError('Reference original has conflicting owners: ' + asset)
                cls.owners[asset] = owner
        paths = {p['url'] for p in cls.pages} | set(cls.owners.values())
        cls.documents = {url: parse((ROOT / url.lstrip('/')).read_text(encoding='utf-8'))
                         for url in paths}

    def test_every_canonical_chapter_has_picture_and_preserved_anchors(self):
        for page in self.pages:
            with self.subTest(page=page['url']):
                self.assertEqual([], group_errors(self.documents[page['url']], page['sections']))

    def test_every_reference_links_to_exact_other_owner(self):
        for url in [p['url'] for p in self.pages] + ['/birth-of-christ.html']:
            with self.subTest(page=url):
                self.assertEqual([], reference_errors(self.documents[url], url,
                                                      self.owners, self.documents))
                for image in self.documents[url].walk():
                    if is_reference_picture(image, url):
                        self.assertTrue(image.attrs.get('alt', '').strip())
                        self.assertTrue((ROOT / local_path(image.attrs['src'], url).lstrip('/')).is_file())

    def test_all_owned_originals_keep_one_owning_figure(self):
        seen = Counter()
        for page in self.pages:
            for figure in self.documents[page['url']].walk():
                key = figure.attrs.get('data-journey-art')
                if key is None:
                    continue
                with self.subTest(page=page['url'], key=key):
                    self.assertIn(key, self.registry)
                    self.assertEqual('/' + self.registry[key]['owner'], page['url'])
                    pictures = [n for n in figure.walk() if n.tag == 'img']
                    self.assertEqual(1, len(pictures))
                    self.assertFalse(urlsplit(pictures[0].attrs.get('src', '')).netloc)
                    self.assertEqual('/' + self.registry[key]['thumbnail'],
                                     local_path(pictures[0].attrs.get('src', ''), page['url']))
                    self.assertTrue((ROOT / self.registry[key]['thumbnail']).is_file())
                    seen[key] += 1
        self.assertEqual(set(self.registry), set(seen))
        self.assertTrue(all(count == 1 for count in seen.values()), seen)

    def test_reference_previews_do_not_repeat_on_receiving_page(self):
        for url in [p['url'] for p in self.pages] + ['/birth-of-christ.html']:
            pictures = [local_path(n.attrs['src'], url) for n in self.documents[url].walk()
                        if is_reference_picture(n, url)]
            self.assertEqual(len(pictures), len(set(pictures)), 'Repeated reference picture: ' + url)

    def test_parent_journey_cards_include_birth_and_all_have_pictures(self):
        doc = self.documents[PARENT]
        opening = next(n for n in doc.walk() if n.attrs.get('id') == 'jesus-journey')
        cards = [n for n in opening.walk() if n.has('jj-card')]
        self.assertIn('/birth-of-christ.html', [local_path(c.attrs['href'], PARENT) for c in cards])
        self.assertGreaterEqual(len(cards), 8)
        all_parent_cards = [n for n in doc.walk() if n.has('jj-card')]
        for card in all_parent_cards:
            self.assertTrue(any(n.tag == 'img' and n.attrs.get('src') for n in card.walk()),
                            'Missing parent-card picture: ' + card.attrs.get('href', ''))

    def test_main_branch_onward_links_follow_displayed_parent_order(self):
        opening = next(n for n in self.documents[PARENT].walk()
                       if n.attrs.get('id') == 'jesus-journey')
        route = [local_path(n.attrs['href'], PARENT) for n in opening.walk() if n.has('jj-card')]
        self.assertEqual(len(route), len(set(route)))
        for current, following in zip(route, route[1:]):
            if not current.startswith('/jesus-christ/'):
                continue  # Birth has its established companion navigation.
            with self.subTest(page=current):
                onward = [n for n in self.documents[current].walk()
                          if n.attrs.get('id') == 'next-study']
                self.assertEqual(1, len(onward))
                choices = [local_path(n.attrs['href'], current) for n in onward[0].walk()
                           if n.has('jj-card')]
                self.assertEqual([following], choices)

    def test_all_twelve_birth_companion_choices_have_pictures(self):
        doc = self.documents['/birth-of-christ.html']
        chapters = [n for n in doc.walk() if 'data-connected-study' in n.attrs]
        self.assertEqual(12, len(chapters))
        for chapter in chapters:
            self.assertTrue(any(n.tag == 'img' and n.attrs.get('src') for n in chapter.walk()),
                            'Birth chapter has no picture: ' + chapter.attrs.get('id', ''))


class VisualCoverageNegativeFixtures(unittest.TestCase):
    def test_artless_choice_and_missing_old_anchor_are_rejected(self):
        doc = parse('<main><nav class="jj-local-nav"><a href="#a">A</a></nav>'
                    '<section class="jj-chapter" id="a"><h2>A</h2></section></main>')
        errors = group_errors(doc, [{'id': 'a'}, {'id': 'old-bookmark'}])
        self.assertTrue(any('no picture' in e for e in errors))
        self.assertTrue(any('preserved anchor' in e for e in errors))

    def test_invalid_and_chained_group_leaders_are_rejected(self):
        doc = parse('<main><nav class="jj-local-nav"><a href="#a">A</a><a href="#b">B</a></nav>'
                    '<section class="jj-chapter" id="a" data-chapter-group="b"><img src="a.webp"></section>'
                    '<section class="jj-chapter" id="b" data-chapter-group="gone"></section></main>')
        errors = group_errors(doc, [])
        self.assertTrue(any('Chained or forward' in e for e in errors))
        self.assertTrue(any('Missing chapter group' in e for e in errors))

    def test_reference_cannot_be_relabelled_as_same_page_or_wrong_owner(self):
        for href in ('/receiving.html', '/wrong.html'):
            doc = parse('<a href="' + href + '"><img class="jj-card-preview" src="/art.webp"></a>')
            self.assertTrue(reference_errors(doc, '/receiving.html',
                                             {'/art.webp': '/owner.html'}, {}))

    def test_missing_reference_bookmark_is_rejected(self):
        doc = parse('<a href="/owner.html#lost"><img class="jj-card-preview" src="/art.webp"></a>')
        self.assertTrue(any('bookmark' in e for e in reference_errors(
            doc, '/receiving.html', {'/art.webp': '/owner.html'}, {'/owner.html': parse('<main></main>')})))

    def test_remote_image_cannot_impersonate_saved_original(self):
        doc = parse('<a href="/owner.html"><img class="jj-card-preview" '
                    'src="https://other.example/art.webp"></a>')
        self.assertTrue(any('saved local' in e for e in reference_errors(
            doc, '/receiving.html', {'/art.webp': '/owner.html'}, {'/owner.html': parse('<main></main>')})))


if __name__ == '__main__':
    unittest.main()
