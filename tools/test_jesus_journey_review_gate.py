"""Negative fixtures for exact-candidate review binding and draft visibility."""
import copy, hashlib, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import build_jesus_journey as builder

class ReviewBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.data=Path(self.tmp.name)
        self.art={'review_record':'review.json','original_sha256':'a'*64,'generated_path':'C:/generated/scene.png'}
        self.candidate={'key':'scene','sha256':'a'*64,'status':'pass_with_caption_conditions'}
        self.save()
    def save(self):
        (self.data/'review.json').write_text(json.dumps({'entries':[self.candidate]}),encoding='utf-8')
    def verify(self):builder.validate_artwork_review('scene',self.art,self.data)
    def test_exact_accepted_candidate_passes(self):self.verify()
    def test_owner_rejection_overrides_technical_pass(self):
        (self.data/'owner-corrections.json').write_text(json.dumps({'rejections':[{'key':'scene','sha256':'a'*64}]}),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Owner-rejected original'):self.verify()
    def test_changed_original_rejected(self):
        self.art['original_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'exact original'):self.verify()
    def test_rejected_candidate_rejected(self):
        self.candidate['status']='revise';self.save()
        with self.assertRaisesRegex(ValueError,'Rejected'):self.verify()
    def test_wrong_scene_rejected(self):
        self.candidate['key']='other';self.save()
        with self.assertRaisesRegex(ValueError,'exact original'):self.verify()
    def test_missing_review_rejected(self):
        self.art['review_record']='absent.json'
        with self.assertRaisesRegex(ValueError,'Missing pixel review'):self.verify()
    def test_ambiguous_candidates_rejected(self):
        (self.data/'review.json').write_text(json.dumps({'entries':[self.candidate,self.candidate]}))
        with self.assertRaisesRegex(ValueError,'exact original'):self.verify()
    def legacy(self):
        self.candidate={'file':'scene.png','technical_verdict':'pass'};self.save()
        binding={'original_sha256':'a'*64,'review_record':'review.json','review_sha256':hashlib.sha256((self.data/'review.json').read_bytes()).hexdigest(),'generated_file':'scene.png','status':'pass'}
        (self.data/'legacy-review-lineage.json').write_text(json.dumps({'bindings':{'scene':binding}}))
    def test_bound_legacy_passes(self):self.legacy();self.verify()
    def test_legacy_review_changed_rejected(self):
        self.legacy();self.candidate['note']='changed';self.save()
        with self.assertRaisesRegex(ValueError,'Unbound legacy'):self.verify()
    def test_legacy_original_changed_rejected(self):
        self.legacy();self.art['original_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'Unbound legacy'):self.verify()
    def test_draft_is_noindex_and_actions_use_shared_contract(self):
        parent=self.data/'answers/jesus-christ-latter-day-saint-beliefs.html';parent.parent.mkdir()
        parent.write_text('<nav class="nav"></nav><footer></footer>')
        page={'url':'/answers/jesus-christ/test.html','title':'Test','intro':'Test','description':'Test','sections':[]}
        with patch.object(builder,'ROOT',self.data):
            draft=builder.render(page,{},False);strict=builder.render(page,{},True)
        self.assertIn('content="noindex,nofollow"',draft)
        self.assertIn('content="index,follow,max-image-preview:large"',strict)
        self.assertIn('class="jj-local-nav fc-actions"',draft)
        self.assertIn('class="jj-actions jj-return fc-actions"',draft)

class EncodingTests(unittest.TestCase):
    def test_corrupt_input_source_label_rejected(self):
        for corrupt in ('John 1:35\u00e2\u20ac\u201c42','John 1:35\u00c3\u00a2\u00e2\u201a\u00ac42','John 1:35\ufffd42'):
            with self.assertRaisesRegex(ValueError,'Corrupted visitor-facing text'):
                builder.scripture(['nt/john/1',corrupt,'35-42'])
        self.assertIn('John 1:35\u201342',builder.scripture(['nt/john/1','John 1:35\u201342','35-42']))
    def test_rendered_visible_navigation_and_source_separator(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            parent=root/'answers/jesus-christ-latter-day-saint-beliefs.html';parent.parent.mkdir()
            parent.write_text('<nav class="nav"></nav><footer></footer>',encoding='utf-8')
            for name in ('full.webp','thumb.webp'):(root/name).write_bytes(b'fixture')
            ref=['nt/john/1','John 1:1','1']
            art={'asset':'full.webp','thumbnail':'thumb.webp','width':10,'height':10,'title':'Scene','alt':'Scene','caption':'Study','refs':[ref,ref]}
            page={'url':'/jesus-christ/test.html','title':'Test','intro':'Test','description':'Test','sections':[{'id':'study','title':'Study','refs':[ref],'blocks':[{'art':'scene'},{'cards':[['/answers.html','Answers','Continue']]}]}]}
            with patch.object(builder,'ROOT',root):output=builder.render(page,{'scene':art},False)
        self.assertIn('Begin the study \u2193',output)
        self.assertIn('Open study \u2192',output)
        self.assertIn('</a> \u00b7 <a',output)
        for corrupt in ('\u00c2\u00b7','\u00e2\u2020','\ufffd'):self.assertNotIn(corrupt,output)

if __name__=='__main__':unittest.main()
