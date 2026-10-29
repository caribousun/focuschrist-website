"""Pending, independently verified current Timeline index and code review.

This structural adapter does not authenticate reviewers. Pins may be filled
only after independent verification of real, privately retained source receipts.
The historic Emma owner and review records are not changed or renewed.
"""
import hashlib,json,re
from pathlib import Path
from datetime import datetime
import timeline_search_index_successor as index

INDEX_REVIEW_SHA256='12e8961b940808e54a41515b6294983a4af0cf6cfc29a527e84f7e5767dbebe7'
CODE_REVIEW_SHA256=None
INDEX_REVIEW='docs/timeline-controls-successor/current-index-review.json'
CODE_REVIEW='docs/timeline-controls-successor/current-code-review.json'
TREE_PROJECTION='docs/timeline-controls-successor/historical-tool-tree.json'
PRIOR_TREE='75294c0737257b29faec3078ce83f82b093d888bca095329fa5425bfbb944559'
PANEL='aaa49fb307fa5e3251e7ed054d2443f637db94a0361a4ba3621d267ed1ab5532'
GALLERY='df6a8c33fc3bd70dbf38675fdb21b984914e5598a42f70025e67de5ddfceb4f8'

def sha(b):return hashlib.sha256(b).hexdigest()
def validhash(v):return isinstance(v,str) and re.fullmatch(r'[0-9a-f]{64}',v) is not None
def canonical(v):return sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
def timestamp(value):
 try:t=datetime.fromisoformat(value.replace('Z','+00:00'))
 except (ValueError,TypeError,AttributeError) as exc:raise ValueError('invalid reviewer time') from exc
 if t.tzinfo is None:raise ValueError('reviewer time needs timezone')
 return t

def pinned(root,path,pin):
 if not validhash(pin):raise ValueError('PENDING independently verified current review: '+path)
 raw=index.source(root,path)
 if sha(raw)!=pin:raise ValueError('Changed current review evidence: '+path)
 return json.loads(raw)

def tool_tree(root):
 """Current tree, normalized only for the two independently verified pins."""
 import emma_public_commitments as public
 root=Path(root).resolve();files={};directory=root/'tools'
 if directory.is_symlink():raise ValueError('symlink tool root')
 for p in sorted(directory.rglob('*')):
  if p.is_symlink():raise ValueError('symlink in current tool tree')
  if not p.is_file():continue
  name=p.relative_to(root).as_posix();raw=p.read_bytes()
  if name=='tools/emma_public_commitments.py':files[name]=public.normalized_validator_hash(root);continue
  if name=='tools/timeline_current_index_closure.py':
   text=raw.decode()
   for key in ('INDEX_REVIEW_SHA256','CODE_REVIEW_SHA256'):
    pattern=r'(?m)^'+key+r"=(?:None|'[0-9a-f]{64}')$"
    if len(re.findall(pattern,text))!=1:raise ValueError('missing or invalid review pin')
    text=re.sub(pattern,key+'=<REVIEWED_PIN>',text)
   raw=text.encode()
  files[name]=sha(raw)
 for name in ('.github/workflows/site-qa.yml','.github/workflows/deploy-pages.yml'):
  files[name]=sha(index.source(root,name))
 return files

def project_old_tree(root,current):
 m=json.loads(index.source(root,TREE_PROJECTION))
 if m.get('schema')!=1 or m.get('prior_tree_sha256')!=PRIOR_TREE or not isinstance(m.get('previous'),dict):raise ValueError('invalid historical tool projection')
 prior=dict(current)
 for name,old in m['previous'].items():
  if name not in prior:raise ValueError('tool projection names absent current file')
  if old is None:del prior[name]
  elif validhash(old):prior[name]=old
  else:raise ValueError('invalid historical file hash')
 if canonical(prior)!=PRIOR_TREE:raise ValueError('historical tool tree mismatch')
 return prior

def prepare(root):
 """Bind genuine current receipts and verify historical and current subjects."""
 root=Path(root).resolve();review=pinned(root,INDEX_REVIEW,INDEX_REVIEW_SHA256);code=pinned(root,CODE_REVIEW,CODE_REVIEW_SHA256)
 if review.get('schema')!='timeline-current-index-review-v1' or review.get('scope')!='three_changed_records_and_unchanged_emma_indices' or review.get('verdict')!='CONCUR':raise ValueError('current index review absent or wrong scope')
 if not all(validhash(review.get(k)) for k in ('reviewer_commitment','private_receipt_sha256')):raise ValueError('index reviewer evidence missing')
 reviewed_at=timestamp(review.get('reviewed_at'))
 urls=review.get('changed_urls')
 if (review.get('prior_search_sha256'),review.get('current_search_sha256'))!=(index.BEFORE,index.AFTER) or review.get('source_sha256')!=index.SOURCES or not isinstance(urls,list) or len(urls)!=len(index.CHANGED) or set(urls)!=index.CHANGED or review.get('emma_records_unchanged') is not True:raise ValueError('index review subject differs')
 if review.get('panel_sha256')!=PANEL or review.get('gallery_sha256')!=GALLERY:raise ValueError('reviewed panel/gallery differ')
 if sha(index.source(root,'docs/section-panel-inventory.json'))!=PANEL or sha(index.source(root,'art-gallery.json'))!=GALLERY:raise ValueError('current panel/gallery differ')
 index.validate_current(root);historical=index.restore(index.source(root,'site-search-index.json'),root)
 if code.get('schema')!='timeline-index-successor-code-review-v1' or code.get('scope')!='current_successor_and_exact_tool_tree' or code.get('verdict')!='CONCUR':raise ValueError('current code review absent or wrong scope')
 if not all(validhash(code.get(k)) for k in ('reviewer_commitment','private_receipt_sha256','current_tool_tree_sha256')) or code['reviewer_commitment']==review['reviewer_commitment']:raise ValueError('independent code reviewer evidence missing')
 if code.get('index_review_sha256')!=INDEX_REVIEW_SHA256 or code.get('search_manifest_sha256')!=sha(index.source(root,index.MANIFEST)) or code.get('historical_tree_manifest_sha256')!=sha(index.source(root,TREE_PROJECTION)):raise ValueError('current code review inputs differ')
 if timestamp(code.get('reviewed_at'))<reviewed_at:raise ValueError('code review predates current index review')
 current=tool_tree(root);prior=project_old_tree(root,current)
 if canonical(current)!=code['current_tool_tree_sha256']:raise ValueError('current reviewed tool tree differs')
 return {'historical_search':historical,'historical_tool_tree_sha256':canonical(prior),'historical_validator_sha256':prior['tools/emma_public_commitments.py']}
