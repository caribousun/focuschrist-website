"""Exact current Emma placement metadata; preserved approval is not new review."""
import copy
import hashlib
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = 'history/emma-hale-smith.html'
STORIES = ('emma-story1-ride', 'emma-story2-hymnal', 'emma-story3-quincy',
           'emma-story4-hospitality', 'emma-story5-testimony')
RETIRED = ('emma-c2', 'emma-h2')
ADDED_FIELDS = {'prior_placement', 'placement_source_sha256', 'current_placement',
                'placement_status', 'placement_note'}


class Source(HTMLParser):
    def __init__(self, raw):
        super().__init__(); self.figures = {}; self.ids = set(); self.links = []
        self.figure = None; self.caption = False; self.paragraph = False; self.copy = {}
        self.feed(raw.decode('utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('href'): self.links.append(attrs['href'])
        if tag == 'figure':
            self.figure = attrs.get('id')
            assert self.figure not in self.figures, 'duplicate figure id'
            self.figures[self.figure] = attrs
        if tag == 'figcaption' and self.figure: self.caption = True
        if tag == 'p' and self.caption and 'fc-study-visual-sources' not in attrs.get('class', '').split():
            self.paragraph = True; self.copy.setdefault(self.figure, [])

    def handle_endtag(self, tag):
        if tag == 'p': self.paragraph = False
        if tag == 'figcaption': self.caption = False
        if tag == 'figure': self.figure = None

    def handle_data(self, data):
        if self.paragraph: self.copy[self.figure].append(data)


def check_registry(registry, historical, pages):
    archive = historical['replacements']
    assert len(archive) == 7 and {r['name'] for r in archive} == set(STORIES + RETIRED)
    by_name = {r['name']: r for r in registry['replacements']}
    assert len(by_name) == len(registry['replacements']), 'duplicate registry identity'
    hub = Source(pages[HUB]); digest = hashlib.sha256(pages[HUB]).hexdigest()
    for old in archive:
        row = by_name[old['name']]
        assert row['status'] == old['status'] == 'approved', 'artwork approval changed'
        assert row['prior_placement'] == {k: old[k] for k in ('page', 'slotId', 'description')}
        assert row['placement_source_sha256'] == digest, 'stale placement source'
        assert isinstance(row['placement_note'], str) and row['placement_note'].strip()
        restored = {k: v for k, v in row.items() if k not in ADDED_FIELDS}
        restored['page'] = old['page']; restored['description'] = old['description']
        assert restored == old, 'asset/hash/lineage or unrelated field changed'
        if row['name'] in STORIES:
            assert row['page'] == HUB and row['placement_status'] == 'active'
            assert row['current_placement'] == {'page': HUB, 'slotId': old['slotId']}
            figure = hub.figures[old['slotId']]
            assert figure.get('data-exclusive-artwork') == row['name'] == figure.get('data-topic-art')
            assert row['description'] == ' '.join(''.join(hub.copy[old['slotId']]).split()), 'stale current caption'
            reference = Source(pages[old['page']])
            assert 'emma-hale-smith.html#' + old['slotId'] in reference.links
            assert not any(f.get('data-exclusive-artwork') == row['name'] or f.get('data-topic-art') == row['name']
                           for f in reference.figures.values()), 'reference still owns artwork'
        else:
            assert row['page'] == old['page'] and row['slotId'] == old['slotId']
            assert row['placement_status'] == 'retired' and row['current_placement'] is None
            assert row['slotId'] not in hub.figures, 'retired figure still present'
    assert 'picture-emma-h2' in hub.ids and 'picture-emma-c2' not in hub.ids


class EmmaRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / 'docs/exclusive-artwork-ownership.json').read_text())
        cls.historical = json.loads((ROOT / 'docs/emma-hub-content-audit/pre-integration-ownership-records.json').read_text())
        names = {HUB} | {r['page'] for r in cls.historical['replacements']}
        cls.pages = {name: (ROOT / name).read_bytes() for name in names}
        # The placement registry is historical evidence; validate the actual
        # successor first, then compare the exact pinned predecessor pages.
        from owner_journey_successor import historical_fixture
        for name in (HUB, 'history/emma-elect-lady.html', 'history/emma-hymns.html'):
            cls.pages[name] = historical_fixture(name, cls.pages[name], ROOT)

    def check(self, registry=None, pages=None):
        check_registry(self.registry if registry is None else registry, self.historical,
                       self.pages if pages is None else pages)

    def row(self, name=STORIES[0]):
        registry = copy.deepcopy(self.registry)
        return registry, next(r for r in registry['replacements'] if r['name'] == name)

    def test_current_seven_placements_preserve_approved_artwork(self):
        self.check()

    def test_wrong_current_owner_rejected(self):
        registry, row = self.row(); row['page'] = row['prior_placement']['page']
        with self.assertRaises(AssertionError): self.check(registry)

    def test_wrong_current_fragment_rejected(self):
        registry, row = self.row(); row['current_placement']['slotId'] = 'wrong'
        with self.assertRaises(AssertionError): self.check(registry)

    def test_stale_description_rejected(self):
        registry, row = self.row(); row['description'] = row['prior_placement']['description']
        with self.assertRaises(AssertionError): self.check(registry)

    def test_changed_source_lineage_rejected(self):
        registry, row = self.row(); row['source_sha256'] = '0' * 64
        with self.assertRaises(AssertionError): self.check(registry)

    def test_changed_asset_hash_rejected(self):
        registry, row = self.row(); assets = row.get('assets', row.get('published_assets'))
        assets[0]['sha256'] = '0' * 64
        with self.assertRaises(AssertionError): self.check(registry)

    def test_artwork_approval_not_retired_with_placement(self):
        registry, row = self.row('emma-c2'); row['status'] = 'rejected'
        with self.assertRaises(AssertionError): self.check(registry)

    def test_retired_placement_cannot_claim_current_owner(self):
        registry, row = self.row('emma-h2'); row['current_placement'] = {'page': HUB, 'slotId': row['slotId']}
        with self.assertRaises(AssertionError): self.check(registry)

    def test_false_previous_placement_rejected(self):
        registry, row = self.row(); row['prior_placement']['page'] = HUB
        with self.assertRaises(AssertionError): self.check(registry)

    def test_duplicate_registry_identity_rejected(self):
        registry, row = self.row(); registry['replacements'].append(copy.deepcopy(row))
        with self.assertRaises(AssertionError): self.check(registry)

    def test_changed_source_bytes_rejected(self):
        pages = dict(self.pages); pages[HUB] += b'\n'
        with self.assertRaises(AssertionError): self.check(pages=pages)


if __name__ == '__main__':
    unittest.main()
