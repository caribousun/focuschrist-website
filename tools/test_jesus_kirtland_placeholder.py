"""The owner-requested removal must not weaken other scene minimums."""
import copy
import unittest
from jesus_journey_qa import owner_requested_kirtland_placeholder

class KirtlandPlaceholderTests(unittest.TestCase):
    def setUp(self):
        self.keys=['rt-vision-1832','rt-persuasion','rt-spirit-messengers','rt-sung-testimony',
                   'rt-accessible-home','rt-sacrament-preparation','rt-patmos-vision']
        self.page={'url':'/jesus-christ/restoration-and-today.html','sections':[
            {'id':'kirtland','blocks':[{'reference_picture':{
                'href':'/church-history.html#kirtland-temple',
                'thumbnail':'assets/page-art/church-history/kirtland-temple-960.webp'}}]}]}
    def test_exact_owner_removal_allowed(self):
        self.assertTrue(owner_requested_kirtland_placeholder(self.page,self.keys))
    def test_other_branch_missing_scene_and_rejected_art_fail(self):
        changed=copy.deepcopy(self.page);changed['url']='/jesus-christ/before-bethlehem.html'
        self.assertFalse(owner_requested_kirtland_placeholder(changed,self.keys))
        for keys in [self.keys[:-1],self.keys[:-1]+['rt-kirtland-appearance'],self.keys+[self.keys[0]]]:
            self.assertFalse(owner_requested_kirtland_placeholder(self.page,keys))
    def test_missing_or_wrong_owner_reference_fails(self):
        for field,value in [('href','/church-history.html#missing'),('thumbnail','rejected.webp')]:
            changed=copy.deepcopy(self.page)
            changed['sections'][0]['blocks'][0]['reference_picture'][field]=value
            self.assertFalse(owner_requested_kirtland_placeholder(changed,self.keys))
        self.page['sections'][0]['blocks']=[]
        self.assertFalse(owner_requested_kirtland_placeholder(self.page,self.keys))
    def test_reintroducing_rejected_art_in_chapter_fails(self):
        self.page['sections'][0]['blocks'].append({'reference_art':'rt-kirtland-appearance'})
        self.assertFalse(owner_requested_kirtland_placeholder(self.page,self.keys))

if __name__=='__main__':unittest.main()
