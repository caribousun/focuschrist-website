"""Current explicit panel owners; whole canonical equality remains the normal CLI."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import section_panel_surface_qa as q
from owner_integration_contract import CHART, INTRO, LANDING, HUB, STORIES

class OwnerIntegrationPanelTests(unittest.TestCase):
    def config(self):
        return json.loads(q.CONFIG.read_text())

    def current(self, config=None):
        with patch.object(q, 'canonical', return_value=[CHART, INTRO, LANDING, HUB, *(p for p in STORIES if p != 'history/emma-elect-lady.html')]):
            return q.inventory(config or self.config())

    def test_actual_eight_current_sources_and_explicit_counts(self):
        result = self.current()
        self.assertNotIn('fc-adams-note', result['candidate_classes'])
        self.assertNotIn('fc-adams-timeline-card', result['candidate_classes'])
        self.assertEqual(result['styled_surface_candidates']['fc-timeline-choice']['pages'], [LANDING])
        self.assertIn('timeline.css', result['styled_surface_candidates']['fc-timeline-choice']['stylesheets'])
        self.assertEqual(result['styled_surface_candidates']['fc-timeline-choice']['disposition'], 'coordinated_stylesheet_owner')
        self.assertNotIn('fc-life-scripture-reflection', result['candidate_classes'])
        self.assertEqual(result['candidate_classes']['fc-timeline-note']['count'], 1)

    def test_each_new_explicit_classification_is_required(self):
        for group, name, error in [('delegated_classes', 'fc-timeline-choice', 'Unclassified rounded/bordered/filled surface')]:
            changed = self.config(); del changed[group][name]
            with self.assertRaisesRegex(AssertionError, error + ': ' + name):
                self.current(changed)

    def test_unknown_or_escaped_classes_are_not_excused(self):
        for token, error in [('fc-adams-note', 'Obsolete standalone note'), ('fc-adams-timeline-card', 'Obsolete Adams feature'), ('fc-timeline-choice', 'Exact integrated panel owner'), ('fc-life-scripture-reflection', 'Retired Emma reflection class returned'), ('fc-adams-unreviewed-card', 'Unclassified panel-like class')]:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder); (root/'other.html').write_text('<div class="'+token+'">x</div>')
                with patch.object(q, 'ROOT', root), patch.object(q, 'canonical', return_value=['other.html']):
                    with self.assertRaisesRegex(AssertionError, error): q.inventory(self.config())

    def test_missing_or_duplicate_current_modifier_is_rejected(self):
        for route, token, attribute, count in [
            (LANDING, 'fc-timeline-choice', 'class="fc-timeline-choice"', 5),
        ]:
            source = (q.ROOT/route).read_text()
            self.assertEqual(source.count(attribute), count)
            missing = source.replace(attribute, attribute.replace(token, 'changed'), 1)
            for changed in [missing, source+'<aside class="'+token+'">extra</aside>']:
                parser=q.Document();parser.feed(changed)
                with self.assertRaises(AssertionError): q.assert_integrated_panel_owners(route, list(parser.root.walk()))
        # A retired modifier is rejected even if placed back on its old owner.
        parser=q.Document();parser.feed((q.ROOT/HUB).read_text()+'<aside class="fc-life-scripture-reflection">extra</aside>')
        with self.assertRaisesRegex(AssertionError,'Retired Emma reflection class returned'):
            q.assert_integrated_panel_owners(HUB,list(parser.root.walk()))

if __name__ == '__main__':
    unittest.main()
