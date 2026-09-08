#!/usr/bin/env python3
"""Static scanner regression fixtures; this is NOT browser runtime QA."""
import tempfile,unittest,json,hashlib
from PIL import Image
from pathlib import Path
from topic_artwork_uniqueness_qa import scan,family_name

class ExclusivityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for name in ['answers','art-study','docs','assets']:(self.root/name).mkdir()
        for prefix in ['a','conference']:
            for i in range(5):self.image(f'{prefix}-{i}-800.webp', (i*30, 80 if prefix=='a' else 160, 100))
        self.study=self.root/'answers/a.html'
        self.study.write_text(self.page('a','../'),encoding='utf-8')
        (self.root/'general-conference.html').write_text(self.page('conference',''),encoding='utf-8')
        (self.root/'index.html').write_text('<main>Home</main>',encoding='utf-8')
    def tearDown(self):self.temp.cleanup()
    def image(self,name,color=(19,37,51),width=800):
        Image.new('RGB',(width,8),color).save(self.root/'assets'/name,lossless=True)
    def manifest(self,paths,filename='exclusive-artwork-review.json'):
        records=[{'source_sha256':'a'*64,'published_assets':[{'path':path,'sha256':hashlib.sha256((self.root/path).read_bytes()).hexdigest()}]} for path in paths]
        (self.root/'docs'/filename).write_text(json.dumps({'assets':records}),encoding='utf-8')
    def page(self,prefix,rel):
        return '<main>'+''.join(f'<section id="s{i}"><p>Study context</p><figure><img src="{rel}assets/{prefix}-{i}-800.webp"><figcaption>Distinct contextual image {i}</figcaption></figure></section>' for i in range(5))+'</main>'
    def result(self):return next(x for x in scan(self.root)['pages'] if x['page']=='answers/a.html')
    def test_separate_art_passes(self):self.assertEqual(self.result()['issues'],[])
    def test_resized_use_in_other_page_preview_fails(self):
        self.image('a-0-1536.webp',width=1536)
        (self.root/'index.html').write_text('<a href="assets/a-0-1536.webp">Preview</a>',encoding='utf-8')
        result=self.result();self.assertEqual(result['exclusiveCount'],4);self.assertTrue(result['issues'])
    def test_renamed_exact_copy_fails(self):
        (self.root/'assets/unrelated-name.png').write_bytes((self.root/'assets/a-0-800.webp').read_bytes())
        (self.root/'index.html').write_text('<img src="assets/unrelated-name.png">',encoding='utf-8')
        self.assertEqual(self.result()['exclusiveCount'],4)
    def test_five_exclusive_plus_shared_extra_still_fails(self):
        self.image('shared.webp')
        self.study.write_text(self.page('a','../').replace('</main>','<figure><img src="../assets/shared.webp"><figcaption>Extra art</figcaption></figure></main>'),encoding='utf-8')
        (self.root/'index.html').write_text('<img src="assets/shared.webp">',encoding='utf-8')
        result=self.result();self.assertEqual(result['exclusiveCount'],5);self.assertTrue(result['issues'])
    def test_embedded_css_is_a_public_use(self):
        (self.root/'index.html').write_text('<style>.scene{background:url("assets/a-0-800.webp")}</style>',encoding='utf-8')
        self.assertEqual(self.result()['exclusiveCount'],4)
    def test_all_documented_widths_share_family(self):
        for width in [320,640,800,900,1200,1400,1536,1672,1726,2048]:
            self.assertEqual(family_name(f'assets/scene-{width}.webp'),'assets/scene')
    def test_hidden_detail_image_is_a_public_use(self):
        (self.root/'index.html').write_text('<div data-detail-image="assets/a-0-800.webp"></div>',encoding='utf-8')
        self.assertEqual(self.result()['exclusiveCount'],4)
    def test_nested_published_page_is_included(self):
        (self.root/'study').mkdir();(self.root/'study/deeper.html').write_text('<img src="../assets/a-0-800.webp">',encoding='utf-8')
        self.assertEqual(self.result()['exclusiveCount'],4)
    def test_separate_review_records_share_source_lineage(self):
        self.image('another-encoding.png')
        (self.root/'index.html').write_text('<img src="assets/another-encoding.png">',encoding='utf-8')
        self.manifest(['assets/a-0-800.webp','assets/another-encoding.png'])
        self.assertEqual(self.result()['exclusiveCount'],4)

    def test_decoded_pixels_join_different_encodings_without_manifest(self):
        with Image.open(self.root/'assets/a-0-800.webp') as im:im.save(self.root/'assets/another-encoding.png')
        (self.root/'index.html').write_text('<img src="assets/another-encoding.png">')
        self.assertEqual(self.result()['exclusiveCount'],4)

    def test_missing_asset_fails_and_never_counts(self):
        (self.root/'assets/a-0-800.webp').unlink()
        result=self.result()
        self.assertEqual(result['exclusiveCount'],4)
        self.assertTrue(any('Missing public image' in x for x in result['issues']))

    def test_corrupt_asset_fails(self):
        (self.root/'assets/a-0-800.webp').write_bytes(b'not an image')
        self.assertEqual(self.result()['exclusiveCount'],4)
        self.assertTrue(scan(self.root)['assetIssues'])

    def test_unrelated_assets_array_cannot_merge_images(self):
        paths=[f'assets/a-{i}-800.webp' for i in range(5)]
        (self.root/'docs/exclusive-artwork-review.json').write_text(json.dumps({'assets':[{'path':p} for p in paths]}))
        self.assertEqual(self.result()['exclusiveCount'],5)

    def test_numeric_suffix_without_matching_width_is_not_alias(self):
        self.image('a-0-2026.webp',width=10)
        (self.root/'index.html').write_text('<img src="assets/a-0-2026.webp">')
        self.assertEqual(self.result()['exclusiveCount'],5)

    def test_external_css_and_import_are_public_references(self):
        (self.root/'styles').mkdir()
        (self.root/'styles/main.css').write_text('@import "nested.css";')
        (self.root/'styles/nested.css').write_text('.scene{background:url("../assets/a-0-800.webp")}')
        (self.root/'index.html').write_text('<link rel="stylesheet" href="styles/main.css">')
        self.assertEqual(self.result()['exclusiveCount'],4)

    def test_external_script_literal_is_public_reference(self):
        (self.root/'main.js').write_text('image.src="assets/a-0-800.webp";')
        (self.root/'index.html').write_text('<script src="main.js"></script>')
        self.assertEqual(self.result()['exclusiveCount'],4)

    def test_linked_caption_prose_is_preserved(self):
        self.study.write_text(self.page('a','../').replace('Distinct contextual image 0','<p>Study <a href="https://example.org">John 1</a> with care.</p>'))
        self.assertIn('with care.',self.result()['figures'][0]['description'])

    def test_review_asset_hash_mismatch_fails(self):
        self.manifest(['assets/a-0-800.webp'])
        self.image('a-0-800.webp',color=(99,99,99))
        self.assertTrue(any('SHA-256 mismatch' in x for x in self.result()['issues']))

    def test_hero_and_resource_preview_do_not_count(self):
        self.study.write_text(self.page('a','../').replace('<section id="s0">','<section class="fc-topic-opening" id="s0">').replace('<section id="s1">','<section class="fc-resource-card" id="s1">'))
        self.assertEqual(self.result()['exclusiveCount'],3)

    def test_source_action_paragraph_is_not_description(self):
        self.study.write_text(self.page('a','../').replace('Distinct contextual image 0','<p>Useful linked <a href="https://example.org">study prose</a>.</p><p class="fc-study-visual-sources"><a href="https://example.org">Source action</a></p>'))
        self.assertIn('study prose',self.result()['figures'][0]['description'])
        self.assertNotIn('Source action',self.result()['figures'][0]['description'])

    def test_held_review_cannot_count(self):
        self.manifest(['assets/a-0-800.webp'])
        path=self.root/'docs/exclusive-artwork-review.json'
        data=json.loads(path.read_text());data['assets'][0]['status']='held';path.write_text(json.dumps(data))
        self.assertEqual(self.result()['exclusiveCount'],4)

if __name__=='__main__':unittest.main()
