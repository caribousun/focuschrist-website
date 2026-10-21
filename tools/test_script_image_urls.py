"""Literal scanner regressions; these are not browser interaction evidence."""
import unittest,json
from topic_artwork_uniqueness_qa import script_image_urls

class ScriptImageURLs(unittest.TestCase):
    def test_remote_url_apostrophe_does_not_become_local_tail(self):
        url="https://example.org/Joseph's House, October1925.png"
        self.assertEqual(list(script_image_urls('const source="'+url+'";')),[url])

    def test_same_quotes_preserve_real_apostrophe_filename(self):
        self.assertEqual(list(script_image_urls('const image="assets/Joseph\'s House.png";')),["assets/Joseph's House.png"])

    def test_escaped_quotes_and_slashes(self):
        self.assertEqual(list(script_image_urls(r'''const a='assets/Joseph\'s.png'; const b="assets/a\"b.png"; const c="https:\/\/example.org\/image.png";''')),["assets/Joseph's.png",'assets/a"b.png','https://example.org/image.png'])

    def test_all_delimiters_query_and_uppercase_extensions(self):
        self.assertEqual(list(script_image_urls('"a.PNG?size=2";\'b.webp#x\';`c.gif`;')),['a.PNG?size=2','b.webp#x','c.gif'])

    def test_inner_quote_and_unmatched_closer_do_not_form_path(self):
        self.assertEqual(list(script_image_urls('"a prose apostrophe\'s House.png and other text"')),[])
        self.assertEqual(list(script_image_urls("'missing.png\"")),[])

    def test_templates_and_unrelated_strings_remain_excluded(self):
        self.assertEqual(list(script_image_urls('`${base}/image.png`; "notes"; "file.txt";')),[])

    def test_attribution_html_inside_json_is_not_a_local_image(self):
        credit='This file was derived from: Alma Being Carried to His Father\'s House, October1925.png. <a href="https://commons.wikimedia.org/example.png">Source</a>'
        self.assertEqual(list(script_image_urls('const credits='+json.dumps({'credit':credit})+';')),[])

    def test_download_name_is_not_an_image_url(self):
        for value in ['"book-of-mormon-internal-map.png"', "'book-of-mormon-internal-map.png'", 'book-of-mormon-internal-map.png']:
            html='<a href="/assets/timeline/book-of-mormon-internal-map.png" download='+value+'>Download</a>'
            self.assertEqual(list(script_image_urls(html)),['/assets/timeline/book-of-mormon-internal-map.png'])

    def test_real_script_filename_survives_download_name_mask(self):
        html='<a href="/assets/map.png" download="map.png">Save</a><script>const image="map.png";</script>'
        self.assertEqual(list(script_image_urls(html)),['/assets/map.png','map.png'])
        self.assertEqual(list(script_image_urls('const download="map.png";')),['map.png'])

    def test_missing_url_attributes_still_reported(self):
        html='<a download="map.png" href="missing-map.png">Save</a><img src="missing-image.png">'
        self.assertEqual(list(script_image_urls(html)),['missing-map.png','missing-image.png'])

    def test_download_like_text_does_not_hide_other_attribute_or_script(self):
        self.assertEqual(list(script_image_urls('<a data-download="missing.png" download>Save</a>')),['missing.png'])
        self.assertEqual(list(script_image_urls('<script>const value="download=map.png"; const image="missing.png";</script>')),['download=map.png','missing.png'])
        self.assertEqual(list(script_image_urls('<a href="missing.png" download="/unknown/image.png">Save</a>')),['missing.png','/unknown/image.png'])

    def credits_fixture(self):
        return {f'/assets/world-scripture/{i:064x}.jpg':{'title':'Title.png','author':'Creator','credit':"This file was derived from: Father's House, October1925.png",'license':'Public domain','license_url':'','source':'https://example.org/source.png','original':'https://example.org/original.jpg','notice':'Existing copy'}for i in range(193)}

    def test_exact_credit_schema_preserves_asset_keys_and_url_fields(self):
        credits=self.credits_fixture();text='const PHOTO_CREDITS='+json.dumps(credits)+'; const image="assets/real missing.png";'
        urls=list(script_image_urls(text,'timelines/world-and-scripture-timeline.html'))
        self.assertTrue(set(credits)<=set(urls))
        self.assertIn('https://example.org/source.png',urls)
        self.assertIn('https://example.org/original.jpg',urls)
        self.assertIn('assets/real missing.png',urls)
        self.assertFalse(any('October1925' in url or url=='Title.png'for url in urls))
        self.assertIn('Title.png',list(script_image_urls(text,'unrelated.html')))

    def test_unknown_or_malformed_credit_schema_fails_closed(self):
        for mutation in ['field','count','type','path','duplicate']:
            credits=self.credits_fixture();key=next(iter(credits))
            if mutation=='field':credits[key]['new_image']='assets/unknown.png'
            if mutation=='count':credits.pop(key)
            if mutation=='type':credits[key]['credit']=[]
            if mutation=='path':credits['/unknown.png']=credits.pop(key)
            text='const PHOTO_CREDITS='+json.dumps(credits)+';'
            if mutation=='duplicate':text+=text
            with self.assertRaises(ValueError):list(script_image_urls(text,'timelines/world-and-scripture-timeline.html'))

if __name__=='__main__':unittest.main()
