"""Negative fixtures for incomplete Holy Ghost learner/source paths."""
import unittest
from holy_ghost_qa import ROOT, PAGE, Document, check_structure

class HolyGhostContractTests(unittest.TestCase):
    def parse(self, text):
        doc=Document(); doc.feed(text); return list(doc.root.walk())
    def setUp(self):
        self.text=(ROOT/PAGE).read_text(encoding='utf-8')
    def test_current_structure(self):
        self.assertEqual(len(check_structure(self.parse(self.text))),16)
    def test_low_resolution_talk_thumbnail_is_rejected(self):
        text=self.text.replace('/full/%211600%2C/0/default','/full/%21192%2C/0/default',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaisesRegex(AssertionError, 'high-resolution'): check_structure(self.parse(text))
    def test_wrong_talk_thumbnail_identity_is_rejected(self):
        text=self.text.replace('/vi/yAo2PrkFcr4/maxresdefault.jpg','/vi/wrong-video/maxresdefault.jpg',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaisesRegex(AssertionError, 'high-resolution'): check_structure(self.parse(text))
    def test_missing_talk_grid_is_rejected(self):
        text=self.text.replace('class="fc-resource-grid"','class="missing-resource-grid"',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaisesRegex(AssertionError, 'bounded resource grid'): check_structure(self.parse(text))
    def test_stranded_talk_card_is_rejected(self):
        nodes=self.parse(self.text)
        card=next(n for n in nodes if n.attrs.get('data-resource-key')=='holy-ghost-talk-4')
        card.parent=card.parent.parent
        with self.assertRaisesRegex(AssertionError, 'bounded resource grid'): check_structure(nodes)
    def test_missing_chapter_is_rejected(self):
        text=self.text.replace('class="jj-chapter" id="comforter"','class="missing-chapter" id="comforter"',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaises(AssertionError): check_structure(self.parse(text))
    def test_duplicate_artwork_identity_is_rejected(self):
        text=self.text.replace('data-exclusive-artwork="hg-nazareth"','data-exclusive-artwork="hg-baptism"',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaises(AssertionError): check_structure(self.parse(text))
    def test_external_counterfeit_scripture_is_rejected(self):
        text=self.text.replace('https://www.churchofjesuschrist.org/study/scriptures/nt/matt/3','https://untrusted.example/study/scriptures/nt/matt/3')
        self.assertNotEqual(text,self.text)
        with self.assertRaises(AssertionError): check_structure(self.parse(text))
    def test_lost_ask_return_is_rejected(self):
        text=self.text.replace('%2Fanswers%2Fholy-ghost.html%23holy-ghost-or-me','%2Fanswers.html')
        self.assertNotEqual(text,self.text)
        with self.assertRaises(AssertionError): check_structure(self.parse(text))
    def test_wrong_video_is_rejected(self):
        text=self.text.replace('data-video-id="AGS45Fd9nmE"','data-video-id="wrong-video"',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaises(AssertionError): check_structure(self.parse(text))
    def test_unregistered_hero_is_rejected(self):
        text=self.text.replace('data-hero-record="holy-ghost"','data-hero-record="unknown"',1)
        self.assertNotEqual(text,self.text)
        with self.assertRaises(AssertionError): check_structure(self.parse(text))

if __name__=='__main__': unittest.main()
