"""Integrity and negative tests; synthetic mutations are not review evidence."""
import copy,json,re,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import emma_public_commitments as m

ROOT=Path(__file__).resolve().parents[1]
class PublicStatement(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.good=json.loads((ROOT/m.SUBJECT).read_bytes())
 def test_exact_statement_structure(self):
  rows,assets,sources=m.validate_statement(ROOT,self.good)
  self.assertEqual((len(rows),len(assets),len(sources)),(11,44,11))
 def test_mutations_fail_closed(self):
  def missing_decision(x):x['scenes'][0]['decision_commitments'].pop('newton_preflight')
  def duplicate_actor(x):x['reviews'][1]['actor_commitment']=x['reviews'][0]['actor_commitment']
  def rejected_input(x):x['scenes'][0]['input_sha256_in_order'][0]=x['excluded_asset_sha256'][0]
  def false_pixel(x):x['reviews'][0]['face_scene_ids'].pop()
  def no_handoff(x):x['reviews'][0]['handoff_receipt_sha256']=None
  def overstate_albert(x):x['reviews'][2]['full_resolution_inspected']=True
  def no_proof(x):x['private_evidence_sha256'].pop('independent_extraction')
  def invent_time(x):x['historical_decision_times']='VERIFIED'
  def owner_waiver(x):x['owner_scope']='unconditional'
  def no_exclusion(x):x['excluded_asset_sha256'].pop()
  for f in (missing_decision,duplicate_actor,rejected_input,false_pixel,no_handoff,overstate_albert,no_proof,invent_time,owner_waiver,no_exclusion):
   bad=copy.deepcopy(self.good);f(bad)
   with self.subTest(mutation=f.__name__),self.assertRaises((ValueError,KeyError)):m.validate_statement(ROOT,bad)
 def test_pins_remain_unset_until_review(self):
  with patch.object(m,'SUBJECT_SHA256',None),self.assertRaisesRegex(ValueError,'pin pending'):
   m.read_pinned(ROOT,m.SUBJECT,m.SUBJECT_SHA256)
 def test_new_runtime_rejection_blocks_input(self):
  import hashlib
  sp=ROOT/m.SUBJECT;vp=ROOT/m.VERIFICATION
  if not vp.is_file():self.skipTest('private verification has not been projected')
  with patch.object(m,'SUBJECT_SHA256',hashlib.sha256(sp.read_bytes()).hexdigest()),patch.object(m,'VERIFICATION_SHA256',hashlib.sha256(vp.read_bytes()).hexdigest()):
   rejected={self.good['scenes'][0]['input_sha256_in_order'][0]}
   with self.assertRaisesRegex(ValueError,'runtime rejection'):
    m.validate_artwork(ROOT,set(m.ASSETS),set(),rejected,lambda _:None,lambda *_:set())
 def test_code_hash_masks_only_exact_review_pins(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);f=root/'tools/emma_public_commitments.py';f.parent.mkdir()
   original=(ROOT/'tools/emma_public_commitments.py').read_text();f.write_text(original)
   digest=m.normalized_validator_hash(root)
   changed,n=re.subn(r"(?m)^SUBJECT_SHA256=(?:None|'[0-9a-f]{64}')$","SUBJECT_SHA256='"+'a'*64+"'",original,count=1)
   self.assertEqual(n,1);self.assertNotEqual(changed,original);f.write_text(changed);self.assertEqual(m.normalized_validator_hash(root),digest)
   f.write_text(original+'\n# changed logic\n');self.assertNotEqual(m.normalized_validator_hash(root),digest)
   f.write_text(original+'\nSUBJECT_SHA256=None\n')
   with self.assertRaisesRegex(ValueError,'duplicate'):m.normalized_validator_hash(root)
 def test_reviewed_tree_binds_bytecode(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);f=root/'tools/emma_public_commitments.py';f.parent.mkdir()
   f.write_bytes((ROOT/'tools/emma_public_commitments.py').read_bytes())
   workflow=root/'.github/workflows/site-qa.yml';workflow.parent.mkdir(parents=True);workflow.write_bytes(b'fixture')
   (workflow.parent/'deploy-pages.yml').write_bytes(b'fixture deploy workflow')
   before=m.reviewed_tool_tree_hash(root);(root/'tools/new_module.pyc').write_bytes(b'fixture bytecode')
   self.assertNotEqual(m.reviewed_tool_tree_hash(root),before)
 def test_pinned_and_mandate_ancestor_symlinks_are_rejected(self):
  import hashlib
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'docs').symlink_to(ROOT/'docs',target_is_directory=True)
   raw=(ROOT/m.SUBJECT).read_bytes()
   with self.assertRaisesRegex(ValueError,'symlink'):
    m.read_pinned(root,m.SUBJECT,hashlib.sha256(raw).hexdigest())
   (root/'AGENTS.md').write_bytes((ROOT/'AGENTS.md').read_bytes())
   with self.assertRaisesRegex(ValueError,'symlink'):
    m.validate_statement(root,self.good)
 def test_render_evidence_exact_paths_and_runtime_rejections(self):
  paths=m.validate_render_files(ROOT,self.good,set())
  self.assertEqual(paths,{'docs/emma-journey-release/render/desktop-opening.jpg','docs/emma-journey-release/render/phone-opening.jpg'})
  changed=copy.deepcopy(self.good);changed['bindings']['rendered']['phone']['image']['path']='unrelated.jpg'
  with self.assertRaisesRegex(ValueError,'unexpected render evidence path'):m.validate_render_files(ROOT,changed,set())
  rejected={self.good['bindings']['rendered']['phone']['image']['sha256']}
  with self.assertRaisesRegex(ValueError,'excluded or rejected render evidence'):m.validate_render_files(ROOT,self.good,rejected)
  changed=copy.deepcopy(self.good);changed['bindings']['rendered']['desktop']['viewport_width']=1400
  with self.assertRaisesRegex(ValueError,'render dimensions'):m.validate_render_files(ROOT,changed,set())
  with self.assertRaisesRegex(ValueError,'overlap or omission'):m.cover_render_files(ROOT,self.good,paths-{'docs/emma-journey-release/render/phone-opening.jpg'},set(),set())
  with self.assertRaisesRegex(ValueError,'overlap or omission'):m.cover_render_files(ROOT,self.good,paths,{next(iter(paths))},set())
  changed=copy.deepcopy(self.good);changed['excluded_asset_sha256'].append(changed['bindings']['rendered']['phone']['image']['sha256'])
  with self.assertRaisesRegex(ValueError,'excluded or rejected render evidence'):m.validate_render_files(ROOT,changed,set())
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for path in paths:
    out=root/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/path).read_bytes())
   changed=copy.deepcopy(self.good);entry=changed['bindings']['rendered']['desktop']['image'];raw=b'not an image';(root/entry['path']).write_bytes(raw)
   entry['bytes']=len(raw);entry['sha256']=m.sha(raw)
   from PIL import UnidentifiedImageError
   with self.assertRaises(UnidentifiedImageError):m.validate_render_files(root,changed,set())
if __name__=='__main__':unittest.main()
