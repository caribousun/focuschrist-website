"""Cross-page previews preserve Birth's canonical artwork ownership."""
import unittest
from birth_of_christ_qa import ROOT, PAGE, Parser, unlinked_exclusive_references

class BirthReferenceOwnership(unittest.TestCase):
    def check_preview(self, markup, page=None):
        asset=(ROOT/'assets/page-art/birth-of-christ/03-nephi-vision-800.webp').resolve()
        return unlinked_exclusive_references(page or ROOT/'jesus-christ/example.html', Parser(markup).root, {asset})
    image='<img src="/assets/page-art/birth-of-christ/03-nephi-vision-800.webp">'
    def test_linked_owner_reference(self):
        self.assertFalse(self.check_preview('<a href="../birth-of-christ.html#prophets-witness">'+self.image+'</a>'))
    def test_wrong_owner_rejected(self):
        self.assertTrue(self.check_preview('<a href="../atonement.html">'+self.image+'</a>'))
    def test_unlinked_rejected_even_with_adjacent_owner_link(self):
        self.assertTrue(self.check_preview('<a href="../birth-of-christ.html">Study</a>'+self.image))
    def test_same_page_duplicate_not_reference(self):
        self.assertTrue(self.check_preview('<a href="#prophets-witness">'+self.image+'</a>',PAGE))
    def test_valid_preview_does_not_mask_unlinked_duplicate(self):
        self.assertTrue(self.check_preview('<a href="../birth-of-christ.html">'+self.image+'</a>'+self.image))
    def test_external_impostor_owner_rejected(self):
        self.assertTrue(self.check_preview('<a href="https://example.org/birth-of-christ.html">'+self.image+'</a>'))

if __name__=='__main__': unittest.main()
