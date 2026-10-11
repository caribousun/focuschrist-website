"""Exact reviewed additions stay reproducible without permitting unreviewed generated changes."""
from pathlib import Path
import json,shutil,tempfile,unittest
from six_scene_journey_render import apply
ROOT=Path(__file__).resolve().parents[1]
class SixSceneJourneyRender(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        names=['docs/artwork-six-scene-delivery-reviews.json','docs/six-scene-artwork/journey-render-additions.json']
        record=json.loads((ROOT/names[0]).read_bytes());names += [r['path'] for r in record['reviews']]
        for name in names:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        self.rows=json.loads((self.root/names[1]).read_bytes())
    def baseline(self,route):
        text=(ROOT/route).read_text(encoding='utf8');row=self.rows[route]
        for key in ['section','style','script']:
            self.assertEqual(text.count(row[key]),1);text=text.replace(row[key],'',1)
        return text
    def test_two_exact_current_outputs(self):
        for route in self.rows:self.assertEqual(apply(self.root,route,self.baseline(route),True),(ROOT/route).read_text(encoding='utf8'))
    def test_altered_baseline_and_replayed_output_rejected(self):
        for route in self.rows:
            for text in [self.baseline(route)+' ',(ROOT/route).read_text(encoding='utf8')]:
                with self.assertRaises(ValueError):apply(self.root,route,text,True)
    def test_missing_duplicate_or_wrong_anchor_rejected(self):
        for route,row in self.rows.items():
            for text in [self.baseline(route).replace(row['section_anchor'],'',1),self.baseline(route)+row['section_anchor'],self.baseline(route).replace('</head>','</header>',1)]:
                with self.assertRaises(ValueError):apply(self.root,route,text,True)
    def test_data_mutations_rejected(self):
        name='docs/six-scene-artwork/journey-render-additions.json';p=self.root/name;original=p.read_bytes()
        for change in ['section','reviewed_render_sha256','baseline_render_sha256']:
            rows=json.loads(original);route=next(iter(rows));rows[route][change]+='unreviewed';p.write_text(json.dumps(rows),encoding='utf8')
            with self.assertRaises(ValueError):apply(self.root,route,self.baseline(route),True)
        p.write_bytes(original)
    def test_changed_real_review_pin_rejected(self):
        record=json.loads((self.root/'docs/artwork-six-scene-delivery-reviews.json').read_bytes());p=self.root/record['reviews'][0]['path'];p.write_bytes(p.read_bytes()+b' ');route=next(iter(self.rows))
        with self.assertRaises(ValueError):apply(self.root,route,self.baseline(route),True)
    def test_unrelated_routes_and_draft_not_extended(self):
        self.assertEqual(apply(self.root,'index.html','unchanged',True),'unchanged')
        for route in self.rows:self.assertEqual(apply(self.root,route,'draft output',False),'draft output')
if __name__=='__main__':unittest.main()
