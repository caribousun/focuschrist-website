"""Current selector panel ownership, independent of archived prior UI."""
import unittest
from pathlib import Path
import section_panel_surface_qa as q
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
def nodes(raw):
 d=Document();d.feed(raw.decode('utf8'));return list(d.root.walk())
class TimelinePanelOwners(unittest.TestCase):
 def test_current_five_and_old_panel_absent(self):
  raw=(ROOT/'timeline.html').read_bytes();q.assert_integrated_panel_owners('timeline.html',nodes(raw))
  needle=b'<article class="fc-timeline-choice">';self.assertIn(needle,raw)
  with self.assertRaises(AssertionError):q.assert_integrated_panel_owners('timeline.html',nodes(raw.replace(needle,b'<article>',1)))
  with self.assertRaises(AssertionError):q.assert_integrated_panel_owners('timeline.html',nodes(raw.replace(needle,b'<article class="fc-timeline-choice fc-adams-timeline-card">',1)))
if __name__=='__main__':unittest.main()
