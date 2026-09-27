"""Prevent visitor caption production notes without banning historical uncertainty."""
import tempfile
import unittest
from pathlib import Path
from media_voice_qa import MediaVoiceParser, voice_matches, public_pages

class MediaVoiceRegression(unittest.TestCase):
    def captures(self, html):
        p=MediaVoiceParser(); p.feed(html); p.close(); return p.captures
    def flagged(self, html):
        return [c for c in self.captures(html) if voice_matches(c['text'], c['kind'])]
    def test_owner_examples_rejected_across_caption_markup(self):
        for copy in ['Let this <em>imagined encounter</em> encourage you.',
                     'Historical accounts guide the scene; they do not preserve this exact session.',
                     'The landscape, clothing, and kneeling posture are artistic choices.',
                     'This imagined devotional scene brings comfort.',
                     'This devotional interpretation looks to His willing response.']:
            self.assertTrue(self.flagged('<figure><figcaption>'+copy+'</figcaption></figure>'))
    def test_hidden_modal_records_are_not_skipped(self):
        self.assertTrue(self.flagged('<section hidden><p data-detail-paragraph>Let this imagined encounter begin your study.</p></section>'))
    def test_modal_alt_and_custom_caption_are_covered(self):
        for html in ['<img alt="An artistic interpretation of Jesus walking.">',
                     '<a data-full-image-alt="Devotional interpretation of Jesus teaching."></a>',
                     '<a data-detail-image-alt="This imagined scene shows a family."></a>',
                     '<a data-full-image-alt="This imagined encounter teaches care."></a>',
                     '<div class="fc-foundation-card-copy">Historical accounts guide the scene.</div>']:
            self.assertTrue(self.flagged(html))
    def test_teaching_prose_not_caught_as_caption(self):
        self.assertFalse(self.flagged('<main><p>Historical accounts guide the scene; they do not preserve this exact session.</p></main>'))
    def test_material_historical_uncertainty_remains_allowed(self):
        for text in ['Luke does not tell us how Simon felt.',
                     'The exact date of this visit is not known.',
                     'The death masks do not establish hair, eye, or skin color.',
                     'No recorded account describes an appearance of Christ at North Platte.',
                     'Book of Mormon geography has not been established.',
                     'The prayer was not recorded word for word.']:
            self.assertFalse(self.flagged('<figcaption>'+text+'</figcaption>'),text)
    def test_only_public_routes_enter_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'sitemap.xml').write_text('<urlset><url><loc>https://focuschrist.com/</loc></url></urlset>')
            for name in ['index.html','404.html','answers/example.html','work/archive.html','tools/fixture.html']:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<p>fixture</p>')
            self.assertEqual({p.relative_to(root).as_posix() for p in public_pages(root)}, {'index.html','404.html','answers/example.html'})

if __name__=='__main__': unittest.main()
