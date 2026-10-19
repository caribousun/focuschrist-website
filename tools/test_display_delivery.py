"""Exact restoration and deterministic display lineage rejection cases."""
import copy, hashlib, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import artwork_display_delivery as delivery

ROOT=Path(__file__).resolve().parents[1]

class DisplayDelivery(unittest.TestCase):
    def test_hero_display_copy_overrides_only_the_artwork_pseudo_element(self):
        css=(ROOT/'home-presentation.css').read_text(encoding='utf8')
        self.assertEqual(css.count(delivery.CSS),1)
        self.assertIn('body.fc-home-presentation .fc-home-hero::before {',delivery.CSS)
        self.assertNotIn('body.fc-home-presentation .fc-home-hero {',delivery.CSS)

    def test_search_inverse_is_single_reviewed_phrase_and_rejects_other_changes(self):
        import json
        data=(ROOT/'site-search-index.json').read_bytes()
        restored=delivery.inverse('site-search-index.json',data)
        current=json.loads(data);prior=json.loads(restored)
        self.assertEqual(current['pages'],prior['pages'])
        changed=[(a,b) for a,b in zip(current['records'],prior['records']) if a!=b]
        self.assertEqual(len(changed),1)
        a,b=changed[0];self.assertEqual(a['url'],'/come-follow-me.html')
        self.assertEqual({k:v for k,v in a.items() if k!='text'},{k:v for k,v in b.items() if k!='text'})
        self.assertIn('Explore the October 2026 General Conference study collection.',a['text'])
        self.assertIn('Explore the April 2026 General Conference study collection.',b['text'])
        for bad in [data+b' ',data.replace(b'Explore the October',b'Explore the November',1)]:
            self.assertEqual(delivery.inverse('site-search-index.json',bad),bad)

    def test_exact_consumer_inverse_restores_original_binding(self):
        for name in delivery.BASELINE:
            if name.startswith('tools/'): continue
            with self.subTest(name=name):
                data=(ROOT/name).read_bytes()
                self.assertEqual(delivery.sha(delivery.inverse(name,data)),delivery.BASELINE[name])

    def test_extra_edits_near_matches_and_duplicate_deltas_are_not_normalized(self):
        for name in delivery.BASELINE:
            if name.startswith('tools/'): continue
            data=(ROOT/name).read_bytes()
            for changed in [data+b'\n<!-- unreviewed -->',data.replace(b'20261019',b'20261020',1),data+data]:
                if changed==data: continue
                with self.subTest(name=name):
                    self.assertEqual(delivery.inverse(name,changed),changed)
                    self.assertNotEqual(delivery.sha(changed),delivery.BASELINE[name])
        data=(ROOT/'index.html').read_bytes()
        self.assertEqual(delivery.inverse('other/index.html',data),data)

    def test_all_five_actual_derivatives_match_exact_lineage(self):
        self.assertEqual(delivery.validate_pixels(ROOT),{r['path'] for r in delivery.ASSETS})

    def test_source_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); row=delivery.ASSETS[0]
            for field in ('source','path'):
                path=root/row[field];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/row[field]).read_bytes())
            (root/row['source']).write_bytes(b'changed source')
            with patch.object(delivery,'ASSETS',[row]),self.assertRaisesRegex(ValueError,'source bytes changed'):
                delivery.validate_pixels(root)

    def test_decoded_alpha_drift_rejected_even_if_compressed_hash_is_rebound(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);row=copy.deepcopy(delivery.ASSETS[0])
            source=root/row['source'];source.parent.mkdir(parents=True);source.write_bytes((ROOT/row['source']).read_bytes())
            target=root/row['path']
            with Image.open(source) as im:
                im=im.convert('RGBA');pixel=im.getpixel((0,0));im.putpixel((0,0),pixel[:3]+((pixel[3]+1)%256,));im.save(target,format='WEBP',lossless=True,exact=True)
            row['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
            with patch.object(delivery,'ASSETS',[row]),self.assertRaisesRegex(ValueError,'decoded display or alpha drift'):
                delivery.validate_pixels(root)

    def test_missing_actual_finished_reviews_blocks_release(self):
        paths={r['path'] for r in delivery.ASSETS}
        with patch.object(delivery,'validate_pixels',return_value=paths):
            import json
            record=json.loads((ROOT/'docs/image-delivery-20261019.json').read_text())
            record['reviews']=[]
            with patch.object(delivery.json,'loads',return_value=record),self.assertRaisesRegex(ValueError,'three actual finished reviewers required'):
                delivery.validate(ROOT,paths,set())

    def test_unknown_extra_raster_cannot_gain_display_coverage(self):
        paths={r['path'] for r in delivery.ASSETS}
        with patch.object(delivery,'validate_pixels',return_value=paths),self.assertRaisesRegex(ValueError,'unsupported additional display raster'):
            delivery.validate(ROOT,paths|{'assets/unauthorized.webp'},set())

if __name__=='__main__':unittest.main()
