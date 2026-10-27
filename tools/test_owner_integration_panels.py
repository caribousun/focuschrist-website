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
        with patch.object(q, 'canonical', return_value=[CHART, INTRO, LANDING, HUB, *STORIES]):
            return q.inventory(config or self.config())

    def test_actual_nine_current_sources_and_explicit_counts(self):
        result = self.current()
        self.assertNotIn('fc-adams-note', result['candidate_classes'])
        self.assertEqual(result['candidate_classes']['fc-adams-timeline-card']['count'], 1)
        self.assertEqual(result['candidate_classes']['fc-adams-timeline-card']['pages'], [LANDING])
        self.assertEqual(result['candidate_classes']['fc-life-scripture-reflection']['count'], 4)
        self.assertEqual(result['candidate_classes']['fc-life-scripture-reflection']['pages'], [HUB])
        self.assertEqual(result['candidate_classes']['fc-timeline-note']['count'], 1)

    def test_each_new_explicit_classification_is_required(self):
        for group, name in [('delegated_classes', 'fc-adams-timeline-card'), ('excluded_classes', 'fc-life-scripture-reflection')]:
            changed = self.config(); del changed[group][name]
            with self.assertRaisesRegex(AssertionError, 'Unclassified panel-like class: ' + name):
                self.current(changed)

    def test_unknown_or_escaped_classes_are_not_excused(self):
        for token, error in [('fc-adams-note', 'Obsolete standalone note'), ('fc-adams-timeline-card', 'Exact integrated panel owner'), ('fc-life-scripture-reflection', 'Exact integrated panel owner'), ('fc-adams-unreviewed-card', 'Unclassified panel-like class')]:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder); (root/'other.html').write_text('<div class="'+token+'">x</div>')
                with patch.object(q, 'ROOT', root), patch.object(q, 'canonical', return_value=['other.html']):
                    with self.assertRaisesRegex(AssertionError, error): q.inventory(self.config())

    def test_missing_or_duplicate_current_modifier_is_rejected(self):
        for route, token, attribute, count in [
            (LANDING, 'fc-adams-timeline-card', 'class="fc-adams-timeline-card"', 1),
            (HUB, 'fc-life-scripture-reflection', 'class="fc-life-reflection fc-life-scripture-reflection"', 4),
        ]:
            source = (q.ROOT/route).read_text()
            self.assertEqual(source.count(attribute), count)
            missing = source.replace(attribute, attribute.replace(token, 'changed'), 1)
            for changed in [missing, source+'<aside class="'+token+'">extra</aside>']:
                parser=q.Document();parser.feed(changed)
                with self.assertRaises(AssertionError): q.assert_integrated_panel_owners(route, list(parser.root.walk()))

if __name__ == '__main__':
    unittest.main()
