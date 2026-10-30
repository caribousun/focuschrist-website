"""Bounded gallery successor; structural checks do not authenticate reviewers.

The actual independent code-review pins remain unset until an authorised
reviewer checks the final subject. Visual and owner acceptance are separate.
"""
import hashlib, json, re
from pathlib import Path

HTML_SHA='7af78f9aceb3cf9fe8de572336bf8fae3c826ce798bc2b8b5b3bc1aacbf4a586'
PRIOR_HTML_SHA='67e419a67ab8062e5a4ae2bfb397608a495e6ff94af02bdd4d9fd5e6a8d622a2'
CSS_SHA='e2f7a4aa16877c7abc14733844f5fa0c61b867d78e257d4ee5b9a2896a498f40'
PRIOR_CSS_SHA='f9bebefb1b4a70a73efdbef6344b40973394521caa5682660a472256530d151a'
LEDGER_SHA='9045712bca0edde386b131700a8b929e6b082400cf82cf528810bf3addcabc82'
PRIOR_LEDGER_SHA='dfbc6689ae4ad6f1fc9867efb5e9fe041cc64934fa98ccbe1c3f1932bf976ea6'
PRIOR_TREE='07ad3d30c0ef458edae2c44bba8d9a988277a164200e3fee4821a193d6fa4923'
REVIEW_PATH='docs/art-gallery-hero/current-code-review.json'
CODE_REVIEW_SHA256=None
CODE_REVIEWER_COMMITMENT=None
IMPLEMENTER_COMMITMENT=None
CODE_RECEIPT_SHA256=None
CURRENT_TREE_SHA256=None
PIN_NAMES=('CODE_REVIEW_SHA256','CODE_REVIEWER_COMMITMENT','IMPLEMENTER_COMMITMENT','CODE_RECEIPT_SHA256','CURRENT_TREE_SHA256')
PREVIOUS_TOOLS={
 '.github/workflows/site-qa.yml':'e1bdb7b235a8091695150181d0f9b6e7f825886fd5db8cd1321f566165b475d1',
 'tools/art_gallery_hero_browser_qa.js':None,
 'tools/test_art_gallery_hero_browser_qa.js':None,
 'tools/art_gallery_hero_successor.py':None,
 'tools/test_art_gallery_hero_successor.py':None,
 'tools/sitewide_artwork_review_qa.py':'bf65c8bd7e1464fe18bb5b7a615880e32518db8f102c0df7b1877a30a1b2e7f9',
 'tools/timeline_51_current_successor.py':'68aa3a6190b3eda0ae19ccd7daf14a73c4b4b7e39b2fa084db20a1f95ad75d9f',
 'tools/timeline_current_index_closure.py':'3c9a25a2c1e4457602d69be309018feb04c8359a7d415c86a02daf5a52e893da',
 'tools/test_timeline_51_current_successor.py':'b7eefb6050fe2388e8bc3688d62455251b1ff5ad390b07cc28d2680b7e3d647b',
 'tools/continue_motion_binding.py':'54022366d3519a3042a42d28f16fafaac8e790ef632bd6c8d8e9dcab2d4a02fb',
 'tools/test_continue_motion_binding.py':'6bbc015e53403454ed20f7761cbb5bcf1f9cb226356b8fda068af7260c9a6773',
}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validhash(value):return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None
def require(value,message):
 if not value:raise ValueError(message)
def source(root,name):
 root=Path(root).resolve();parts=Path(name).parts
 require(not Path(name).is_absolute() and '..' not in parts,'Invalid gallery source path')
 require(all(not root.joinpath(*parts[:i]).is_symlink() for i in range(1,len(parts)+1)),'Gallery source uses symlink')
 path=(root/name).resolve();require(path.is_relative_to(root) and path.is_file(),'Missing or unsafe gallery source')
 return path.read_bytes()

def previous_html(html):
 require(sha(html)==HTML_SHA,'Current gallery HTML changed')
 new=b'<a class="fc-gallery-hero" href="art.html" aria-label="Explore the Art &amp; Study opening artwork"></a>\n'
 cue=b'<a class="fc-button fc-gallery-desktop-continue" href="#fc-opening-next" aria-label="Continue"><span aria-hidden="true">Continue</span></a>\n'
 tools=b'<div class="fc-gallery-tools fc-mobile-scroll-target" id="fc-opening-next" role="search" aria-label="Find artwork">'
 old_tools=b'<div class="fc-gallery-tools" role="search" aria-label="Find artwork">'
 new_version=b'art-gallery.css?v=20261030-gallery-hero-1';old_version=b'art-gallery.css?v=20261010-gallery-fit-1'
 require(html.count(new)==1 and html.count(cue)==1 and html.count(tools)==1 and html.count(new_version)==1,'Gallery link, Continue target or version differs')
 old_html=html.replace(new,b'',1).replace(cue,b'',1).replace(tools,old_tools,1).replace(new_version,old_version,1)
 require(sha(old_html)==PRIOR_HTML_SHA,'Prior gallery HTML differs')
 return old_html

def previous_ledger(root,raw):
 """Validate the actual label change, then reconstruct the exact prior ledger."""
 require(sha(raw)==LEDGER_SHA,'Current gallery content ledger changed')
 html=source(root,'art-gallery.html');css=source(root,'art-gallery.css')
 require(sha(html)==HTML_SHA and sha(css)==CSS_SHA,'Current gallery source changed')
 previous_html(html)
 start=b'\n.fc-gallery-intro {\n';end=b'.fc-gallery-intro h1 { margin: 12px 0 18px; }'
 require(css.count(start)==1 and css.count(end)==1 and css.index(start)<css.index(end),'Gallery CSS boundary differs')
 previous=css[:css.index(start)+1]+b'.fc-gallery-intro { max-width: 760px; margin: 0 auto 32px; text-align: center; }\n'+css[css.index(end):]
 require(sha(previous)==PRIOR_CSS_SHA,'Prior gallery CSS differs')
 data=json.loads(raw);rows=data.get('documents');require(isinstance(rows,list),'Invalid current content ledger')
 matches=[r for r in rows if r.get('path')=='art-gallery.html'];require(len(matches)==1,'Gallery ledger row missing or duplicated')
 row=matches[0];label=row.get('current_gallery_label_review');prior=row.get('prior_gallery_review')
 require(isinstance(label,dict) and label.get('reviewer')=='independent ChatGPT technical reviewer' and label.get('reviewed_at_utc')=='2026-10-30T05:06:43.465650088Z','Gallery label review differs')
 require(label.get('source_sha256')==HTML_SHA and label.get('predecessor_source_sha256')==PRIOR_HTML_SHA and label.get('predecessor_text_sha256')=='5ee7fb5b84f81c0dae5ed03bcc782434446bf72816d425cac6c87795802ace24','Gallery label source binding differs')
 require(row.get('published_text_sha256')=='8a68f9ae9d38cff355b1b5058d76198968d76e188c73bf55426572b574560489','Gallery label text differs')
 require(isinstance(prior,dict) and prior.get('path')=='art-gallery.html','Prior gallery review missing')
 result=(json.dumps(dict(data,documents=[prior if r is row else r for r in rows]),ensure_ascii=False,indent=2)+'\n').encode()
 require(sha(result)==PRIOR_LEDGER_SHA,'Prior gallery ledger differs')
 return result

def project_tree(current,canonical):
 prior=dict(current)
 for name,expected in PREVIOUS_TOOLS.items():
  require(name in prior,'Gallery tool projection path missing: '+name)
  if expected is None:del prior[name]
  else:prior[name]=expected
 require(canonical(prior)==PRIOR_TREE,'Gallery historical tool tree differs')
 return prior

def project_reviewed_tree(root,current,canonical):
 """Require independent current code evidence before any old-tree projection."""
 pins=(CODE_REVIEW_SHA256,CODE_REVIEWER_COMMITMENT,IMPLEMENTER_COMMITMENT,CODE_RECEIPT_SHA256,CURRENT_TREE_SHA256)
 require(all(validhash(x) for x in pins),'PENDING independent gallery current-code review')
 require(CODE_REVIEWER_COMMITMENT!=IMPLEMENTER_COMMITMENT,'Gallery reviewer must differ from implementer')
 raw=source(root,REVIEW_PATH);require(sha(raw)==CODE_REVIEW_SHA256,'Gallery code review changed')
 review=json.loads(raw)
 require(review.get('schema')=='art-gallery-current-code-review-v1' and review.get('scope')=='gallery_hero_and_exact_tool_tree' and review.get('verdict')=='CONCUR_WITHIN_BOUNDED_CODE_SCOPE','Gallery code review scope differs')
 require(review.get('reviewer_commitment')==CODE_REVIEWER_COMMITMENT and review.get('implementer_commitment')==IMPLEMENTER_COMMITMENT and review.get('receipt_sha256')==CODE_RECEIPT_SHA256,'Gallery code review identities differ')
 require(review.get('html_sha256')==HTML_SHA and review.get('css_sha256')==CSS_SHA and review.get('ledger_sha256')==LEDGER_SHA,'Gallery code review sources differ')
 require(review.get('current_tool_tree_sha256')==CURRENT_TREE_SHA256==canonical(current) and review.get('prior_tool_tree_sha256')==PRIOR_TREE,'Gallery code review tree differs')
 from timeline_current_index_closure import timestamp
 require(timestamp(review.get('reviewed_at'))>=timestamp('2026-10-30T05:06:43.465650088Z'),'Gallery code review predates label review')
 return project_tree(current,canonical)
