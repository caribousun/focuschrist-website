"""Hero preservation and builder transaction regression; not pixel approval."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
import build_history_stories as builder
import artwork_creation_gate as gate

ROOT = Path(__file__).resolve().parents[1]
# Load just the pure structural assertion; the QA script itself is a release gate.
source = ast.parse((ROOT/'tools/history_story_pages_qa.py').read_text(encoding='utf-8'))
function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'assert_story_figures')
ns = {}
exec(compile(ast.Module(body=[function], type_ignores=[]), '<history figure assertion>', 'exec'), ns)
assert_story_figures = ns['assert_story_figures']

class HeroBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'site'; self.root.mkdir()
        self.data = self.root/'docs/history-stories'; self.data.mkdir(parents=True)
        self.stories = json.loads((ROOT/'docs/history-stories/stories.json').read_text(encoding='utf-8'))['stories']
        self.ready = json.loads((ROOT/'docs/history-stories/art-ready.json').read_text(encoding='utf-8'))
        for name in ['navigation.html.template','footer.html.template']:
            (self.data/name).write_bytes((ROOT/'docs/history-stories'/name).read_bytes())
        (self.root/'church-history.html').write_bytes((ROOT/'church-history.html').read_bytes())
        self.before = {}
        for story in self.stories:
            p = self.root/'history'/f'{story["id"]}.html'; p.parent.mkdir(exist_ok=True); p.write_text('UNCHANGED '+story['id'])
            self.before[p] = p.read_bytes()
            for unit in story['units'] + ([story['hero']] if 'hero' in story else []):
                art = self.ready[unit['id']]
                for key in ['full','thumbnail','desktop']:
                    if key not in art: continue
                    asset = self.root/art[key]; asset.parent.mkdir(parents=True,exist_ok=True); asset.write_bytes(unit['id'].encode())
                art['sha256'] = hashlib.sha256((self.root/art['full']).read_bytes()).hexdigest()
                if 'desktop' in art: art['desktop_sha256'] = hashlib.sha256((self.root/art['desktop']).read_bytes()).hexdigest()
                art['reviewed'] = True; art['desktop_reviewed'] = True
        self.before[self.root/'church-history.html'] = (self.root/'church-history.html').read_bytes()
        self.save()
        self.addCleanup(patch.stopall)
        patch.object(builder,'ROOT',self.root).start(); patch.object(builder,'DATA',self.data).start()

    def save(self):
        (self.data/'stories.json').write_text(json.dumps({'stories':self.stories}))
        (self.data/'art-ready.json').write_text(json.dumps(self.ready))

    def call(self,args,gate_effect=None):
        with patch('sys.argv',['build_history_stories.py',*args]), patch.object(gate,'run',side_effect=gate_effect) as check:
            builder.build()
            return check

    def unchanged(self):
        for path,data in self.before.items(): self.assertEqual(path.read_bytes(),data)

    def test_gate_failure_precedes_every_public_write(self):
        with self.assertRaisesRegex(ValueError,'missing finished'):
            self.call([],ValueError('missing finished'))
        self.unchanged()

    def test_story_option_is_not_gate_bypass(self):
        with self.assertRaisesRegex(ValueError,'missing finished'):
            self.call(['--story','eleazer-miller'],ValueError('missing finished'))
        self.unchanged()

    def test_success_writes_exact_prevalidated_bytes(self):
        captured = {}
        def observe(root,mode,**kwargs):
            self.assertEqual(mode,'use'); self.unchanged(); captured.update(kwargs['page_overrides'])
        self.call([],observe)
        self.assertEqual(set(captured),{p.relative_to(self.root).as_posix() for p in self.before})
        for name,data in captured.items(): self.assertEqual((self.root/name).read_bytes(),data)

    def test_preview_does_not_write_public_routes(self):
        destination = self.root.parent/'preview'
        self.ready['miller-teaching-brigham']['reviewed'] = False
        self.ready['miller-teaching-brigham']['desktop_reviewed'] = False
        self.save()
        calls = self.call(['--story','eleazer-miller','--preview-output',str(destination)])
        self.unchanged()
        self.assertTrue((destination/'history/eleazer-miller.html').is_file())
        self.assertEqual([c.args[1:] for c in calls.call_args_list],[('preflight','eleazer-teaching-brigham-hero'),('preflight','eleazer-teaching-brigham-desktop-extension')])

    def test_preview_preflight_failure_writes_nothing(self):
        destination = self.root.parent/'preview'
        with self.assertRaisesRegex(ValueError,'bad preflight'):
            self.call(['--preview-output',str(destination)],ValueError('bad preflight'))
        self.assertFalse(destination.exists()); self.unchanged()

    def test_preview_rejects_repo_descendant_and_ancestor(self):
        for destination in [self.root,self.root/'work',self.root.parent]:
            with self.subTest(destination=destination),self.assertRaisesRegex(AssertionError,'outside'):
                self.call(['--preview-output',str(destination)])
            self.unchanged()

    def test_unreviewed_hero_blocks_normal_build(self):
        self.ready['miller-teaching-brigham']['reviewed'] = False; self.save()
        with self.assertRaises(AssertionError): self.call([])
        self.unchanged()

    def test_exact_eleven_figures_preserves_first_body(self):
        story = next(s for s in self.stories if s['id']=='eleazer-miller')
        soup = BeautifulSoup(builder.render(story,self.ready),'html.parser')
        self.assertEqual(assert_story_figures(story,soup)['id'],'miller-teaching-brigham')
        self.assertEqual(len(soup.select('main figure')),11)
        self.assertEqual(soup.select_one('meta[property="og:image"]')['content'],'https://focuschrist.com/'+self.ready['miller-teaching-brigham']['full'])

    def test_first_original_omission_and_duplicate_and_wrong_hero_fail(self):
        story = next(s for s in self.stories if s['id']=='eleazer-miller')
        html = builder.render(story,self.ready)
        for kind in ['omit','duplicate','wronghero','move']:
            soup=BeautifulSoup(html,'html.parser')
            original=soup.select_one('.fc-life-body-start > figure')
            if kind=='omit': original.decompose()
            if kind=='duplicate': original.insert_after(copy.copy(original))
            if kind=='wronghero': original.a['class']=['fc-visual-hero']
            if kind=='move': soup.select_one('#reflect').append(original.extract())
            with self.subTest(kind=kind),self.assertRaises(AssertionError): assert_story_figures(story,soup)

if __name__=='__main__': unittest.main()
