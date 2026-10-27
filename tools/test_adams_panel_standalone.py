"""Twelve finite Adams panel/standalone tests; full inventory equality stays in CI."""
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import section_panel_surface_qa as q
from adams_standalone_opening import ADAMS_ROUTE

ROOT = Path(__file__).resolve().parents[1]


class AdamsPanelTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'docs/section-panel-surfaces.json').read_text())
        self.data = (ROOT / ADAMS_ROUTE).read_bytes()

    def one_page_inventory(self, config=None):
        with patch.object(q, 'canonical', return_value=[ADAMS_ROUTE]):
            return q.inventory(config or self.config)

    def test_exact_two_toolbar_notes_and_no_shared_surfaces(self):
        actual = self.one_page_inventory()
        row = actual['candidate_classes']['fc-adams-note']
        self.assertEqual(row, {'count': 2, 'pages': [ADAMS_ROUTE], 'tags': ['p'], 'disposition': 'excluded_with_reason', 'reason': self.config['excluded_classes']['fc-adams-note']})
        self.assertEqual(set(actual['candidate_classes']), {'fc-adams-note'})
        self.assertTrue(all(r['count'] == 0 for r in actual['surface_selectors'].values()))
        self.assertEqual(actual['styled_surface_candidates']['controls']['pages'], [ADAMS_ROUTE])

    def test_exact_classification_is_required(self):
        changed = copy.deepcopy(self.config); del changed['excluded_classes']['fc-adams-note']
        with self.assertRaisesRegex(AssertionError, 'Unclassified panel-like class: fc-adams-note'):
            self.one_page_inventory(changed)

    def test_note_class_cannot_escape_its_owner(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'other.html').write_bytes(self.data)
            with patch.object(q, 'ROOT', root), patch.object(q, 'canonical', return_value=['other.html']):
                with self.assertRaisesRegex(AssertionError, 'outside exact standalone owner'): q.inventory(self.config)

    def test_similar_unknown_note_remains_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'other.html').write_text('<p class="fc-adams-note-new">x</p>')
            with patch.object(q, 'ROOT', root), patch.object(q, 'canonical', return_value=['other.html']):
                with self.assertRaisesRegex(AssertionError, 'Unclassified panel-like class: fc-adams-note-new'): q.inventory(self.config)

    def test_changed_adams_source_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / ADAMS_ROUTE; path.parent.mkdir(); path.write_bytes(self.data + b' ')
            with patch.object(q, 'ROOT', root), patch.object(q, 'canonical', return_value=[ADAMS_ROUTE]):
                with self.assertRaisesRegex(AssertionError, 'opening bytes changed'): q.inventory(self.config)

    def check_stylesheet_route(self, route, data):
        # Minimal controlled CSS satisfies the unchanged unrelated preconditions;
        # this exercises q.check's real per-route branch, not the whole site CLI.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / route; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
            (root / 'site-system.css').write_text('/* BEGIN OWNER SECTION PANEL SURFACES */\n:root{--fc-panel-fill:var(--fc-card-fill);--fc-panel-shadow:inset 0 0 0 1px var(--fc-line)}\n/* END OWNER SECTION PANEL SURFACES */\n/* BEGIN OWNER MISSION PANEL ROW */\nbody.fc-site .fc-missionary-work-grid{gap:18px;border:0;background:none}\n/* END OWNER MISSION PANEL ROW */')
            (root / 'missionary.css').write_text('\n'.join('.fc-missionary-work-grid{grid-template-columns:' + n + ';}' for n in ('repeat(4, minmax(0, 1fr))', 'repeat(2, minmax(0, 1fr))', '1fr')))
            with patch.object(q, 'ROOT', root):
                q.check({'surface_selectors': [], 'version': self.config['version']}, {'canonical_pages': [route], 'surface_selectors': {}})

    def test_exact_adams_standalone_stylesheet_branch(self):
        self.check_stylesheet_route(ADAMS_ROUTE, self.data)
        with self.assertRaisesRegex(AssertionError, 'opening bytes changed'):
            self.check_stylesheet_route(ADAMS_ROUTE, self.data + b' ')

    def test_unknown_standalone_without_shared_css_fails(self):
        with self.assertRaisesRegex(AssertionError, 'missing current shared stylesheet'):
            self.check_stylesheet_route('timelines/unknown.html', self.data)

    def test_old_shared_stylesheet_rule_retained(self):
        good = ('<link rel="stylesheet" href="../site-system.css?v=' + self.config['version'] + '">').encode()
        self.check_stylesheet_route('other.html', good)
        with self.assertRaisesRegex(AssertionError, 'missing current shared stylesheet'):
            self.check_stylesheet_route('other.html', good.replace(self.config['version'].encode(), b'stale'))

    def test_inventory_and_config_only_add_reviewed_owner(self):
        current = json.loads((ROOT / 'docs/section-panel-inventory.json').read_text())
        self.assertEqual(len(current['canonical_pages']), 138)
        self.assertEqual(current['canonical_pages'].count(ADAMS_ROUTE), 1)
        current['canonical_pages'].remove(ADAMS_ROUTE)
        del current['candidate_classes']['fc-adams-note']
        current['styled_surface_candidates']['controls']['pages'].remove(ADAMS_ROUTE)
        self.assertEqual(current['candidate_classes']['fc-timeline-note']['count'], 2)
        current['candidate_classes']['fc-timeline-note']['count'] = 1
        raw = (json.dumps(current, ensure_ascii=False, indent=2) + '\n').encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), '9c3442425c7113310b76f254853107a04b937576cc0d3f7e63bf7fa093caaadc')
        config = copy.deepcopy(self.config); del config['excluded_classes']['fc-adams-note']
        self.assertEqual(hashlib.sha256((json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode()).hexdigest(), '722a3bfdb987a59b49a3a79c75d25d600ab95b2d87000d15477de0e7ee3fb6d0')

    def landing_note_row(self, data):
        # Parse only inert source through the production inventory function.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'timeline.html').write_bytes(data)
            with patch.object(q, 'ROOT', root), patch.object(q, 'canonical', return_value=['timeline.html']):
                return q.inventory(self.config)['candidate_classes']['fc-timeline-note']

    def assert_landing_note_inventory(self, data):
        saved = json.loads((ROOT / 'docs/section-panel-inventory.json').read_text())
        self.assertEqual(self.landing_note_row(data), saved['candidate_classes']['fc-timeline-note'], 'Landing note inventory drift')

    def test_exact_landing_note_count_matches_inventory(self):
        data = (ROOT / 'timeline.html').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), 'fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578')
        self.assertEqual(self.landing_note_row(data)['count'], 2)
        self.assert_landing_note_inventory(data)

    def test_removed_and_duplicated_landing_note_reject_inventory(self):
        data = (ROOT / 'timeline.html').read_bytes()
        note = b'<p class="fc-timeline-note">This nineteenth century chart sets the history of the Bible and the history of the nations side by side across one long timeline, inviting the reader to follow both together.</p>'
        self.assertEqual(data.count(note), 1)
        for changed, count in ((data.replace(note, b'', 1), 1), (data.replace(note, note + note, 1), 3)):
            with self.subTest(discovered_count=count):
                self.assertEqual(self.landing_note_row(changed)['count'], count)
                with self.assertRaisesRegex(AssertionError, 'Landing note inventory drift'):
                    self.assert_landing_note_inventory(changed)

    def test_all_historical_code_and_tests_preserved(self):
        text = (ROOT / 'tools/section_panel_surface_qa.py').read_text()
        extra = 'from adams_standalone_opening import ADAMS_ROUTE, assert_adams_opening\n'
        call = '        assert_adams_note_owner(page,nodes)\n'
        branch = '        if p == ADAMS_ROUTE:\n            assert_adams_opening(p,(ROOT/p).read_bytes())\n            continue\n'
        for item in (extra, call, branch): self.assertEqual(text.count(item), 1); text = text.replace(item, '')
        text, count = re.subn(r'def assert_adams_note_owner\(page, nodes\):\n.*?\n(?=def inventory\()', '', text, flags=re.S)
        self.assertEqual(count, 1)
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), '708289f927adbadbcd8417d823d1dfa122126ab8b426f5b1561aca40d4fc2261')
        self.assertEqual(hashlib.sha256((ROOT / 'tools/test_section_panel_standalone.py').read_bytes()).hexdigest(), '049ebb8077ea6c77d3e5b39abb727f110d901a32e312961ee78806606fb3c154')


if __name__ == '__main__':
    unittest.main()
