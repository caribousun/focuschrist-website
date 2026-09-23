"""Preserve approved Home artwork and verify navigational picture references."""
import copy
import json
import re
import subprocess
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from PIL import Image
from answer_study_qa import Document
from topic_artwork_uniqueness_qa import family_name

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '0cf872b8194e22f6aeb2659be34d63ccd7e2b908'
MANIFEST = ROOT / 'docs/home-presentation-references-20260923.json'


def parse(text):
    doc = Document()
    doc.feed(text)
    return doc.root


def tree(node):
    return (node.tag, tuple(sorted(node.attrs.items())), tuple(
        item if isinstance(item, str) else tree(item) for item in node.content))


def local(value, owner='index.html'):
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        return None
    return urlsplit(urljoin('/' + owner, value)).path.lstrip('/')


def ancestors(node):
    while node:
        yield node
        node = node.parent


def purpose_row_errors(css):
    """The existing three-card pathway grid needs a full last row at two columns."""
    clean = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    compact = lambda value: re.sub(r'\s+', '', value)
    matching = []
    for match in re.finditer(r'@media\s*([^{}]+)\{', clean):
        if compact(match.group(1)) != '(min-width:701px)and(max-width:980px)':
            continue
        start, end, depth = match.end(), match.end(), 1
        while end < len(clean) and depth:
            depth += (clean[end] == '{') - (clean[end] == '}')
            end += 1
        for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', clean[start:end - 1]):
            if 'body.fc-home-presentation.fc-home-purpose-paths>:last-child' in [compact(s) for s in selectors.split(',')]:
                matching.extend(compact(v) for v in re.findall(r'grid-column\s*:\s*([^;]+)', body))
    return [] if matching and all(value == '1/-1' for value in matching) else [
        'Home purpose pathways must complete the final row only at the reviewed 701–980px breakpoint']


def check(home, baseline, manifest, root=ROOT):
    errors = []
    nodes, old = list(parse(home).walk()), list(parse(baseline).walk())
    protected = {
        'approved hero': lambda n: n.has('fc-home-hero'),
        'owned figures': lambda n: n.tag == 'figure',
        'detail records': lambda n: 'data-artwork-detail-content' in n.attrs,
        'detail dialog': lambda n: n.attrs.get('id') == 'artworkDetailDialog',
    }
    for name, select in protected.items():
        actual, expected = [tree(n) for n in nodes if select(n)], [tree(n) for n in old if select(n)]
        if Counter(actual) != Counter(expected):
            errors.append('Changed or duplicated ' + name)
    if sum(n.tag == 'figure' for n in nodes) != 3:
        errors.append('Home must retain exactly three owned figures')
    old_ids = Counter(n.attrs['id'] for n in old if n.attrs.get('id'))
    ids = Counter(n.attrs['id'] for n in nodes if n.attrs.get('id'))
    if any(ids[key] != count for key, count in old_ids.items()) or any(count > 1 for count in ids.values()):
        errors.append('Existing anchors must survive exactly once')
    old_links = {n.attrs['href'] for n in old if n.tag == 'a' and local(n.attrs.get('href', '')) is not None
                 and urlsplit(n.attrs.get('href', '')).path.endswith('.html')}
    links = {n.attrs.get('href', '') for n in nodes if n.tag == 'a'}
    if not old_links <= links:
        errors.append('Existing static study/core links missing: ' + str(sorted(old_links - links)))
    if not any(local(n.attrs.get('href', '')) == 'answers/jesus-christ-latter-day-saint-beliefs.html'
               and any(a.tag == 'main' for a in ancestors(n)) and not any('hidden' in a.attrs for a in ancestors(n))
               for n in nodes if n.tag == 'a' and n.attrs.get('href')):
        errors.append('Visible static Jesus journey entry missing')
    if any(n.tag == 'link' and local(n.attrs.get('href', '')) == 'jesus-journey.css' for n in nodes):
        errors.append('Home must not import journey-only stylesheet')
    refs = manifest['references']
    expected = {r['key']: r for r in refs}
    previews = [n for n in nodes if 'data-home-reference' in n.attrs]
    if len(refs) != 9 or len(expected) != 9 or Counter(n.attrs['data-home-reference'] for n in previews) != Counter(expected.keys()):
        errors.append('Exactly nine unique manifest reference previews required')
    used = []
    for preview in previews:
        key = preview.attrs['data-home-reference']
        if key not in expected:
            continue
        ref = expected[key]
        images = [n for n in preview.walk() if n.tag == 'img']
        if preview.tag != 'a' or preview.attrs.get('href') != ref['href'] or len(images) != 1:
            errors.append(key + ': exact owner link and one preview image required')
            continue
        if any(a.tag == 'figure' or 'data-journey-art' in a.attrs for a in ancestors(preview)) or any('data-artwork-detail' in n.attrs for n in preview.walk()):
            errors.append(key + ': preview must remain a navigational reference')
        image = images[0]
        asset, owner = local(image.attrs.get('src', '')), local(ref['href'])
        if asset != ref['src'] or image.attrs.get('alt') != ref['alt']:
            errors.append(key + ': image or alternative text differs from manifest')
        if not owner or owner == 'index.html' or not owner.endswith('.html') or not (root / owner).is_file():
            errors.append(key + ': missing or invalid different owner')
            continue
        owner_nodes = list(parse((root / owner).read_text(encoding='utf-8')).walk())
        fragment = urlsplit(ref['href']).fragment
        if not fragment or not any(n.attrs.get('id') == fragment for n in owner_nodes):
            errors.append(key + ': owner anchor missing')
        family = family_name(asset or '')
        used.append(family)
        # Watch's source is an existing video-resource thumbnail, not an owned figure.
        if not any(n.tag == 'img' and family_name(local(n.attrs.get('src', ''), owner) or '') == family for n in owner_nodes):
            errors.append(key + ': destination does not contain this image family')
        if asset and (root / asset).is_file():
            with Image.open(root / asset) as source:
                size = source.size
            if size != (ref['width'], ref['height']) or tuple(image.attrs.get(x) for x in ('width', 'height')) != tuple(map(str, size)):
                errors.append(key + ': actual image dimensions must be reserved')
        else:
            errors.append(key + ': image missing')
    if len(used) != len(set(used)):
        errors.append('Duplicate Home reference image family')
    return errors


class HomePresentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = (ROOT / 'index.html').read_text(encoding='utf-8')
        cls.baseline = subprocess.check_output(['git', 'show', BASELINE + ':index.html'], cwd=ROOT).decode('utf-8')
        cls.manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))

    def test_actual_home(self):
        self.assertEqual(self.manifest['baseline'], BASELINE)
        self.assertEqual(check(self.home, self.baseline, self.manifest), [])

    def test_bad_owner_rejected_even_if_manifest_agrees(self):
        manifest = copy.deepcopy(self.manifest)
        old = manifest['references'][0]['href']
        manifest['references'][0]['href'] = 'about.html#main-content'
        self.assertTrue(check(self.home.replace(old, 'about.html#main-content'), self.baseline, manifest))

    def test_missing_anchor_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        old = manifest['references'][0]['href']
        new = old.split('#')[0] + '#missing-home-fixture'
        manifest['references'][0]['href'] = new
        self.assertTrue(check(self.home.replace(old, new), self.baseline, manifest))

    def test_duplicate_preview_rejected(self):
        self.assertTrue(check(self.home.replace('data-home-reference="weekly"', 'data-home-reference="atonement"'), self.baseline, self.manifest))

    def test_owned_figure_alteration_rejected(self):
        self.assertTrue(check(self.home.replace('Seek, study, and remember Jesus Christ.</figcaption>', 'Changed caption.</figcaption>'), self.baseline, self.manifest))

    def test_purpose_row_completion(self):
        self.assertEqual(purpose_row_errors((ROOT / 'home-presentation.css').read_text(encoding='utf-8')), [])

    def test_missing_purpose_row_rule_rejected(self):
        css = '@media(min-width:701px) and (max-width:980px){body.fc-home-presentation .fc-home-purpose-paths > :last-child{grid-column:1 / -1;}}'
        self.assertEqual(purpose_row_errors(css), [])
        self.assertTrue(purpose_row_errors(css.replace('grid-column:1 / -1;', '')))


if __name__ == '__main__':
    unittest.main()
