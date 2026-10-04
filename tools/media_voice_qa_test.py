"""Prevent visitor caption production notes without banning historical uncertainty."""
import tempfile
import unittest
import json
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
    def test_resource_artwork_disclaimer_is_rejected(self):
        self.assertTrue(self.flagged('<article class="fc-resource-card"><p>The original artwork illustrates receiving attentive help; it does not portray a particular person from the talk.</p></article>'))
        self.assertFalse(self.flagged('<article class="fc-resource-card"><p>Elder Jeffrey R. Holland teaches compassion, patience, and the value of qualified care during mental and emotional suffering.</p></article>'))
    def test_hidden_picture_panel_imagined_room_note_is_rejected(self):
        for copy in ['This room imagines a quiet moment within that longer search.',
                     'The setting imagines a moment before the journey.',
                     'This scene imagines the hymn’s hope in the daily work of continuing together.']:
            self.assertTrue(self.flagged('<figcaption data-picture-panel-copy hidden><p>'+copy+'</p></figcaption>'))
        for copy in ['Brigham Young studied the Book of Mormon before joining the Church.',
                     'The record does not establish which room the visitors entered.',
                     'The family imagined what their new home might be like.']:
            self.assertFalse(self.flagged('<figcaption data-picture-panel-copy hidden><p>'+copy+'</p></figcaption>'))
    def test_history_source_regeneration_preserves_footer_only_disclosure(self):
        from build_history_stories import DATA, render
        stories=json.loads((DATA/'stories.json').read_text(encoding='utf-8'))['stories']
        ready=json.loads((DATA/'art-ready.json').read_text(encoding='utf-8'))
        for story in stories:
            generated=render(story,ready)
            self.assertEqual(self.flagged(generated),[],story['id'])
        miller=next(story for story in stories if story['id']=='eleazer-miller')
        hero=miller['hero_unit_id']
        ready[hero]['caption']+=' This room imagines a quiet moment within that longer search.'
        self.assertTrue(self.flagged(render(miller,ready)))
    def test_pioneer_music_visible_and_detail_notes_are_covered(self):
        note='This scene imagines the hymn’s hope in the daily work of continuing together.'
        self.assertTrue(self.flagged('<article class="pioneer-music-card"><p>'+note+'</p></article>'))
        self.assertTrue(self.flagged('<article hidden><p data-detail-paragraph>'+note+'</p></article>'))
        self.assertFalse(self.flagged('<article class="pioneer-music-card"><p>A mother and child share a glance as their family walks beside the wagon. The road still stretches ahead.</p></article>'))
    def test_alt_adopted_likeness_production_note_is_rejected(self):
        self.assertTrue(self.flagged('<img alt="Sitting for a painted likeness in a new illustration using our adopted Joseph likeness">'))
        for text in ['An 1842 painted likeness of Joseph Smith.',
                     'A portrait with disputed identification.',
                     'Close view of Joseph Smith’s mouth, upper lip and chin.']:
            self.assertFalse(self.flagged('<img alt="'+text+'">'))
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
