"""A linked preview may refer to genuine artwork on another owning page only."""
import unittest
from pathlib import Path
from answer_study_qa import Document
from topic_artwork_uniqueness_qa import linked_reference,is_owning_page_reference

class ReferenceOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(__file__).resolve().parents[1]
        doc=Document();doc.feed('<section id="scene"><figure><img src="/art/original.webp"></figure></section>')
        self.parsed={'owner.html':list(doc.root.walk())}
        self.identities={'art/original.webp':'same-original','art/thumb.webp':'same-original','art/other.webp':'different'}
    def reference(self,html):
        doc=Document();doc.feed(html)
        n=next(n for n in doc.root.walk() if n.tag=='img')
        return {'family':'same-original','linked_reference':linked_reference(n,self.root/'receiver.html',self.root)}
    def test_exact_other_owner_and_existing_anchor_are_allowed(self):
        r=self.reference('<a href="owner.html#scene"><img src="art/thumb.webp"></a>')
        self.assertTrue(is_owning_page_reference(r,'owner.html',self.parsed,self.identities,self.root))
    def test_missing_anchor_wrong_owner_and_unowned_family_fail(self):
        for href in ['owner.html#missing','wrong.html','receiver.html','https://example.com/owner.html']:
            with self.subTest(href=href):
                r=self.reference('<a href="'+href+'"><img src="art/thumb.webp"></a>')
                self.assertFalse(is_owning_page_reference(r,'owner.html',self.parsed,self.identities,self.root))
        r=self.reference('<a href="owner.html"><img src="art/thumb.webp"></a>');r['family']='different'
        self.assertFalse(is_owning_page_reference(r,'owner.html',self.parsed,self.identities,self.root))
    def test_unlinked_and_owned_figure_cannot_claim_reference_exception(self):
        for html in ['<img src="art/thumb.webp">','<figure><a href="owner.html"><img src="art/thumb.webp"></a></figure>']:
            self.assertIsNone(self.reference(html)['linked_reference'])

if __name__=='__main__':unittest.main()
