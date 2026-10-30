"""Focused gallery successor tests; synthetic receipts are never release evidence."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import art_gallery_hero_successor as gate

ROOT=Path(__file__).resolve().parents[1]

class GallerySuccessorTests(unittest.TestCase):
 def test_actual_ledger_and_source_reconstruct_exact_predecessor(self):
  raw=(ROOT/'content-audit.json').read_bytes()
  self.assertEqual(gate.sha(gate.previous_ledger(ROOT,raw)),gate.PRIOR_LEDGER_SHA)
  html=(ROOT/'art-gallery.html').read_bytes()
  self.assertEqual(gate.sha(gate.previous_html(html)),gate.PRIOR_HTML_SHA)
  with self.assertRaisesRegex(ValueError,'HTML changed'):gate.previous_html(html+b' ')
  with self.assertRaisesRegex(ValueError,'ledger changed'):gate.previous_ledger(ROOT,raw+b' ')
  original=gate.source
  for name in ('art-gallery.html','art-gallery.css'):
   with self.subTest(name=name),patch.object(gate,'source',side_effect=lambda root,path:original(root,path)+(b' ' if path==name else b'')),self.assertRaisesRegex(ValueError,'source changed'):
    gate.previous_ledger(ROOT,raw)

 def test_exact_tree_projection_rejects_unknown_and_missing(self):
  current={name:'a'*64 for name in gate.PREVIOUS_TOOLS}
  current['tools/unchanged.py']='b'*64
  wanted={'tools/unchanged.py':'b'*64,**{name:value for name,value in gate.PREVIOUS_TOOLS.items() if value is not None}}
  canonical=lambda tree:gate.PRIOR_TREE if tree==wanted else '0'*64
  self.assertEqual(gate.project_tree(current,canonical),wanted)
  with self.assertRaisesRegex(ValueError,'historical tool tree differs'):gate.project_tree(dict(current,**{'tools/unknown.py':'c'*64}),canonical)
  missing=dict(current);missing.pop(next(iter(gate.PREVIOUS_TOOLS)))
  with self.assertRaisesRegex(ValueError,'path missing'):gate.project_tree(missing,canonical)

 def test_current_code_review_is_required_and_distinct(self):
  current={'tools/synthetic.py':'a'*64}
  with self.assertRaisesRegex(ValueError,'PENDING independent'):gate.project_reviewed_tree(ROOT,current,lambda _: 'f'*64)
  review={'schema':'art-gallery-current-code-review-v1','scope':'gallery_hero_and_exact_tool_tree','verdict':'CONCUR_WITHIN_BOUNDED_CODE_SCOPE','reviewer_commitment':'1'*64,'implementer_commitment':'2'*64,'receipt_sha256':'3'*64,'html_sha256':gate.HTML_SHA,'css_sha256':gate.CSS_SHA,'ledger_sha256':gate.LEDGER_SHA,'current_tool_tree_sha256':'f'*64,'prior_tool_tree_sha256':gate.PRIOR_TREE,'reviewed_at':'2026-10-30T05:07:00Z'}
  raw=json.dumps(review).encode()
  with patch.object(gate,'CODE_REVIEW_SHA256',gate.sha(raw)),patch.object(gate,'CODE_REVIEWER_COMMITMENT','1'*64),patch.object(gate,'IMPLEMENTER_COMMITMENT','2'*64),patch.object(gate,'CODE_RECEIPT_SHA256','3'*64),patch.object(gate,'CURRENT_TREE_SHA256','f'*64),patch.object(gate,'source',return_value=raw),patch.object(gate,'project_tree',return_value={'prior':'synthetic'}):
   self.assertEqual(gate.project_reviewed_tree(ROOT,current,lambda _: 'f'*64),{'prior':'synthetic'})
   with patch.object(gate,'IMPLEMENTER_COMMITMENT','1'*64),self.assertRaisesRegex(ValueError,'must differ'):gate.project_reviewed_tree(ROOT,current,lambda _: 'f'*64)
   with self.assertRaisesRegex(ValueError,'tree differs'):gate.project_reviewed_tree(ROOT,current,lambda _: 'e'*64)
   with patch.object(gate,'source',return_value=raw+b' '),self.assertRaisesRegex(ValueError,'review changed'):gate.project_reviewed_tree(ROOT,current,lambda _: 'f'*64)
   for field,value in [('verdict','UNREVIEWED'),('html_sha256','0'*64),('ledger_sha256','0'*64),('prior_tool_tree_sha256','0'*64),('receipt_sha256','0'*64)]:
    changed=copy.deepcopy(review);changed[field]=value;bad=json.dumps(changed).encode()
    with self.subTest(field=field),patch.object(gate,'CODE_REVIEW_SHA256',gate.sha(bad)),patch.object(gate,'source',return_value=bad),self.assertRaises(ValueError):gate.project_reviewed_tree(ROOT,current,lambda _: 'f'*64)
   earlier=copy.deepcopy(review);earlier['reviewed_at']='2026-10-30T05:06:00Z';bad=json.dumps(earlier).encode()
   with patch.object(gate,'CODE_REVIEW_SHA256',gate.sha(bad)),patch.object(gate,'source',return_value=bad),self.assertRaisesRegex(ValueError,'predates label'):gate.project_reviewed_tree(ROOT,current,lambda _: 'f'*64)

if __name__=='__main__':unittest.main()
