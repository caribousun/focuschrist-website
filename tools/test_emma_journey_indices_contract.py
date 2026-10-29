"""Synthetic fixtures only; these are not regenerated site index artifacts."""
from pathlib import Path
import ast, copy, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import emma_journey_indices_contract as e
class N:
 def __init__(self,cls='',tag='aside'):self.attrs={'class':cls};self.tag=tag
class PanelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  source=(ROOT/'tools/section_panel_surface_qa.py').read_text();tree=ast.parse(source)
  func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='assert_integrated_panel_owners');scope={};exec(compile(ast.Module(body=[func],type_ignores=[]),'fixture','exec'),scope);cls.check=staticmethod(scope[func.name])
 def test_exact_current_scopes(self):
  self.check('history/emma-hale-smith.html',[]);self.check('timeline.html',[N('fc-timeline-choice','article') for _ in range(5)])
  for page,nodes in [('history/emma-hale-smith.html',[N('fc-life-scripture-reflection')]),('another.html',[N('fc-life-scripture-reflection')]),('timeline.html',[N('fc-timeline-choice','article')]*4),('other.html',[N('fc-timeline-choice','article')])]:
   with self.subTest(page=page),self.assertRaises(AssertionError):self.check(page,nodes)
class IndexTests(unittest.TestCase):
 def setUp(self):
  def art(id,full,page,thumb=None):return {'id':id,'fullImage':full,'thumbnail':thumb or 'thumb','occurrences':[{'id':'occ-'+id,'page':page,'selector':'unchanged'}]}
  self.other=art('other','/assets/x.webp','/answers/study.html');retained=[art('old-'+str(i),'/assets/page-art/emma-life/'+x+'-review-1536.webp',e.HUB) for i,x in enumerate(e.RETAINED)]
  new=[art('new-'+str(i),'/assets/page-art/emma-journey/'+x+'-1536.webp',e.HUB,'/assets/page-art/emma-journey/'+x+'-960.webp') for i,x in enumerate(e.NEW)]
  oldg={'pages':[e.HUB,e.OLD,e.HYMN,'/answers/study.html'],'artworks':[self.other]+retained};newg={'pages':[e.HUB,e.HYMN,'/answers/study.html'],'artworks':[self.other]+retained+new}
  oldr=[{'url':x} for x in [e.HUB,e.OLD,e.HYMN,'/answers/study.html']+['/art-gallery.html?picture='+x['id'] for x in oldg['artworks']]];newr=[{'url':x} for x in [e.HUB,e.HYMN,'/answers/study.html']+[e.HUB+'#'+x for x in e.SECTIONS]+['/art-gallery.html?picture='+x['id'] for x in newg['artworks']]]
  self.before={'gallery':oldg,'search':{'pages':oldg['pages'],'records':oldr},'panel':{'canonical_pages':[x.lstrip('/') for x in oldg['pages']],'candidate_classes':{'unchanged':{'pages':['answers/study.html']}}}}
  self.after={'gallery':newg,'search':{'pages':newg['pages'],'records':newr},'panel':{'canonical_pages':[x.lstrip('/') for x in newg['pages']],'candidate_classes':{'unchanged':{'pages':['answers/study.html']}}}}
 def test_synthetic_happy_path(self):self.assertEqual(e.check(self.before,self.after)['new_emma_images'],10)
 def test_mutations_rejected(self):
  for name in ('remove_new','remove_retained','extra_owner','old_route','wrong_source','drop_section','old_fragment','duplicate_panel','changed_retained','duplicate_retained','unrelated_gallery','unrelated_metadata','unrelated_panel','unrelated_search','retired_class'):
   a=copy.deepcopy(self.after)
   if name=='remove_new':a['gallery']['artworks'].pop()
   if name=='remove_retained':a['gallery']['artworks'].pop(1)
   if name=='extra_owner':a['gallery']['artworks'][-1]['occurrences'].append({'page':'/other.html'})
   if name=='old_route':a['search']['pages'].append(e.OLD)
   if name=='wrong_source':a['gallery']['artworks'][-1]['thumbnail']='/wrong.webp'
   if name=='drop_section':a['search']['records']=[r for r in a['search']['records'] if not r['url'].endswith(e.SECTIONS[0])]
   if name=='old_fragment':a['search']['records'].append({'url':e.OLD+'#reflect'})
   if name=='duplicate_panel':a['panel']['canonical_pages'].append(a['panel']['canonical_pages'][0])
   if name=='changed_retained':a['gallery']['artworks'][1]['thumbnail']='/changed.webp'
   if name=='duplicate_retained':a['gallery']['artworks'][1]['occurrences'].append(copy.deepcopy(a['gallery']['artworks'][1]['occurrences'][0]))
   if name=='unrelated_gallery':a['gallery']['artworks'][0]['occurrences'][0]['selector']='changed'
   if name=='unrelated_metadata':a['gallery']['artworks'][0]['thumbnail']='/wrong-unrelated.webp'
   if name=='unrelated_panel':a['panel']['candidate_classes']['unchanged']['pages']=[]
   if name=='unrelated_search':a['search']['records'][-1]['url']='/bad-url'
   if name=='retired_class':a['panel']['candidate_classes']['fc-life-scripture-reflection']={'count':1}
   with self.subTest(name=name),self.assertRaises(AssertionError):e.check(self.before,a)
if __name__=='__main__':unittest.main()
