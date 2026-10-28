"""Exact current nine-source selection; no browser/network/full generation."""
import ast
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import owner_integration_contract as contract
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/build_art_gallery.py'
NAMES=(contract.HUB,*contract.STORIES,contract.LANDING,contract.CHART,contract.INTRO)

class CurrentGallerySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree=ast.parse(SOURCE.read_bytes())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='gallery_source')
        scope={'ROOT':ROOT}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),scope)
        cls.select=staticmethod(scope['gallery_source'])
    def test_all_nine_actual_current_sources_are_not_historical(self):
        inverse=Mock(side_effect=AssertionError('Current sources must not enter historical projection'))
        with patch.dict(sys.modules,{'artwork_display_delivery':types.SimpleNamespace(inverse=inverse)}):
            for name in NAMES:
                with self.subTest(name=name):
                    raw=(ROOT/name).read_bytes()
                    self.assertEqual(self.select(name,raw,ROOT),raw)
            inverse.assert_not_called()
    def test_other_current_source_byte_drift_is_rejected(self):
        for name in NAMES:
            if name == contract.LANDING:
                continue  # Timeline has a current semantic, not byte-exact, contract.
            raw=(ROOT/name).read_bytes()
            variants=[raw+b' ']
            if name == contract.HUB:
                variants += [raw.replace(b'</main>', b'<img src="/assets/page-art/emma-life/'+scene+b'-review-960.webp"></main>', 1) for scene in (b'emma-h2',b'emma-c2')]
            for changed in variants:
                with self.subTest(name=name,variant=len(changed)),self.assertRaisesRegex(AssertionError,'Current integration source drift'):
                    self.select(name,changed,ROOT)
    def test_timeline_current_semantics_accept_layout_and_reject_drift(self):
        raw=(ROOT/contract.LANDING).read_bytes()
        layout=raw.replace(b'fc-timeline-choice__body', b'fc-timeline-choice__body layout-v2', 1)
        self.assertNotEqual(layout,raw)
        self.assertEqual(self.select(contract.LANDING,layout,ROOT),layout)
        for old,new in (
            (b'Explore the story of the Restoration.',b'Changed visible copy.'),
            (b'latter-day-saint-church-history-timeline.html',b'other.html'),
            (b'church-history-grove.webp',b'other.webp'),
        ):
            with self.subTest(changed=old):
                self.assertIn(old,raw)
                with self.assertRaises(AssertionError):
                    self.select(contract.LANDING,raw.replace(old,new,1),ROOT)
    def test_unknown_route_keeps_existing_inverse(self):
        inverse=Mock(return_value=b'historical unrelated display')
        with patch.dict(sys.modules,{'artwork_display_delivery':types.SimpleNamespace(inverse=inverse)}):
            self.assertEqual(self.select('index.html',b'actual unrelated',ROOT),b'historical unrelated display')
            inverse.assert_called_once_with('index.html',b'actual unrelated')
    def test_near_names_do_not_gain_current_route_exception(self):
        inverse=Mock(return_value=b'old')
        with patch.dict(sys.modules,{'artwork_display_delivery':types.SimpleNamespace(inverse=inverse)}):
            for name in ('/history/emma-hale-smith.html','history/emma-hale-smith.html.extra','history/unknown.html'):
                self.assertEqual(self.select(name,b'raw',ROOT),b'old')
            self.assertEqual(inverse.call_count,3)
    def test_generator_calls_current_selector_and_preserves_missionary(self):
        source=SOURCE.read_text()
        self.assertIn("doc.feed(gallery_source(name, (ROOT / name).read_bytes()).decode('utf-8'))",source)
        self.assertIn("if name == 'missionary.html':",source)
        self.assertIn("doc.feed((ROOT / name).read_bytes().decode('utf-8'))",source)
    def test_search_reads_current_sources_and_generated_gallery(self):
        source=(ROOT/'tools/build_site_search.py').read_text()
        tree=ast.parse(source)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
        self.assertFalse(any(isinstance(n.func,ast.Name) and n.func.id in {'inverse','historical_bytes','restore'} for n in calls))
        self.assertIn("doc.feed((ROOT/path.lstrip('/')).read_text(encoding='utf-8'))",source)
        self.assertIn("gallery=json.loads((ROOT/'art-gallery.json').read_text(encoding='utf-8'))",source)
    def test_exact_current_ownership_references_are_preserved(self):
        hub=self.select(contract.HUB,(ROOT/contract.HUB).read_bytes(),ROOT)
        self.assertNotIn(b'emma-c2-review-',hub)
        self.assertNotIn(b'emma-h2-review-',hub)
        self.assertIn(b'<span id="picture-emma-h2" class="fc-legacy-picture-anchor"></span>',hub)
        for name,scene in contract.STORIES.items():
            raw=self.select(name,(ROOT/name).read_bytes(),ROOT)
            self.assertIn(('data-artwork-reference="'+scene+'"').encode(),raw)
            self.assertIn(('id="picture-'+scene+'"').encode(),hub)

if __name__=='__main__':unittest.main()
