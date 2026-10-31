"""Exact WebGL fallback successor; historical projections do not approve release."""
import base64,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGE='timelines/world-and-scripture-timeline.html'
TEST='tools/test_world_webgl_fallback.js'
SOURCE_MANIFEST='docs/timeline-webgl-fallback/source-delta.json'
SOURCE_MANIFEST_SHA256='40ce7ebb0982c4868c4399a9a1e1619281fed8f58ed419101d604529e30f580e'
BEFORE='d67a067e9d90d64b992d21382d07307a91b3770132b1d6db3b451e46683c69a1'
AFTER='40602f8dfa0bd9683993620d1ff106cbdc192a8a200a475135e5286219772a99'
TEST_SHA256='2633b18153478a0a59621bb34d137718b3f05b92d02d5dc8b3591bd835afd3ba'
SOURCE_HEAD='1e7b1ad96278be36d0350010fff7568d0d830b6b'
PRIOR_TREE='07ad3d30c0ef458edae2c44bba8d9a988277a164200e3fee4821a193d6fa4923'
TREE_MANIFEST='docs/timeline-webgl-fallback/tool-tree.json'
TREE_MANIFEST_SHA256='398718af3075c796e99d8c188d9828c88693af42b6088e995d1e17e0e114fcd7'
REVIEW='docs/timeline-webgl-fallback/independent-code-review.json'
WEBGL_REVIEW_SHA256='374a8176c455c84f716360a831357fdf02c48fe1b2f2812adeda3510aaeacd0a'
WEBGL_REVIEWER_COMMITMENT='25275b95cc2c78a6aef8f6ac29e2400b0fac0290ab5ec12f9946448301ee8133'
WEBGL_RECEIPT_SHA256='7c624ad85ce1897aacf434bf56d1bb63f958a243153a50c977a035a0c7e9b2d7'
WEBGL_SOURCE_RECEIPT_SHA256='ab5ab96eda5e5f08dfffcf65ce41ef82e95a8f36e5b201fa5d1f95ef6bc41709'
PIN_NAMES=('WEBGL_REVIEW_SHA256','WEBGL_REVIEWER_COMMITMENT','WEBGL_RECEIPT_SHA256','WEBGL_SOURCE_RECEIPT_SHA256')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def validhash(value):return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None
def require(value,message):
 if not value:raise ValueError(message)
def source(root,name):
 root=Path(root).resolve();parts=Path(name).parts;p=root.joinpath(*parts)
 require(not Path(name).is_absolute() and '..' not in parts,'Unsafe WebGL evidence path')
 require(all(not root.joinpath(*parts[:i]).is_symlink() for i in range(1,len(parts)+1)) and p.is_file() and p.resolve().is_relative_to(root),'Missing or unsafe WebGL evidence: '+name)
 return p.read_bytes()
def restore_page(raw,root=ROOT):
 """Reconstruct only exact predecessor bytes; this is not a current review."""
 if sha(raw)==BEFORE:return raw
 require(sha(raw)==AFTER,'Unreviewed WebGL fallback page')
 manifest=source(root,SOURCE_MANIFEST);require(sha(manifest)==SOURCE_MANIFEST_SHA256,'WebGL source manifest changed')
 doc=json.loads(manifest);require(doc.get('schema')==1 and doc.get('path')==PAGE and doc.get('before_sha256')==BEFORE and doc.get('after_sha256')==AFTER,'Invalid WebGL source manifest')
 changes=doc.get('changes');require(isinstance(changes,list) and len(changes)==2,'Invalid WebGL source changes')
 for item in reversed(changes):
  require(isinstance(item,dict) and set(item)=={'before_b64','after_b64'},'Invalid WebGL source change')
  try:before=base64.b64decode(item['before_b64'],validate=True);after=base64.b64decode(item['after_b64'],validate=True)
  except (ValueError,TypeError) as exc:raise ValueError('Invalid WebGL source encoding') from exc
  require(after and before!=after and raw.count(after)==1,'WebGL source context differs');raw=raw.replace(after,before,1)
 require(sha(raw)==BEFORE,'WebGL source predecessor differs');return raw

def validate_review(root=ROOT,current=None):
 """Require real independent review of actual source and test; this does not authenticate identities."""
 from timeline_world_mobile_release_successor import MOBILE_IMPLEMENTER_COMMITMENT
 import timeline_current_index_closure as old
 root=Path(root).resolve();restore_page(source(root,PAGE),root)
 require(sha(source(root,PAGE))==AFTER and sha(source(root,TEST))==TEST_SHA256,'Current WebGL source or regression changed')
 require(all(validhash(x) for x in (WEBGL_REVIEW_SHA256,WEBGL_REVIEWER_COMMITMENT,WEBGL_RECEIPT_SHA256,WEBGL_SOURCE_RECEIPT_SHA256)),'PENDING independent WebGL code and source review')
 require(validhash(MOBILE_IMPLEMENTER_COMMITMENT) and WEBGL_REVIEWER_COMMITMENT!=MOBILE_IMPLEMENTER_COMMITMENT,'WebGL reviewer must differ from implementer')
 raw=source(root,REVIEW);require(sha(raw)==WEBGL_REVIEW_SHA256,'WebGL code review changed');review=json.loads(raw)
 require(review.get('schema')=='timeline-webgl-fallback-review-v1' and review.get('scope')=='webgl_source_test_and_tool_tree' and review.get('verdict')=='CONCUR_WITHIN_BOUNDED_CODE_SCOPE','WebGL review scope differs')
 require(review.get('reviewer_commitment')==WEBGL_REVIEWER_COMMITMENT and review.get('implementer_commitment')==MOBILE_IMPLEMENTER_COMMITMENT and review.get('receipt_sha256')==WEBGL_RECEIPT_SHA256 and review.get('source_review_receipt_sha256')==WEBGL_SOURCE_RECEIPT_SHA256,'WebGL reviewer evidence differs')
 require(review.get('source_head')==SOURCE_HEAD and review.get('page_before_sha256')==BEFORE and review.get('page_after_sha256')==AFTER and review.get('regression_test_sha256')==TEST_SHA256,'WebGL reviewed source differs')
 require(review.get('source_manifest_sha256')==SOURCE_MANIFEST_SHA256 and review.get('tree_manifest_sha256')==TREE_MANIFEST_SHA256 and review.get('previous_tool_tree_sha256')==PRIOR_TREE,'WebGL review inputs differ')
 current=old.tool_tree(root) if current is None else current
 require(review.get('current_tool_tree_sha256')==old.canonical(current),'WebGL reviewed tool tree differs')
 return review

def project_tree(root,current):
 import timeline_current_index_closure as old
 raw=source(root,TREE_MANIFEST);require(sha(raw)==TREE_MANIFEST_SHA256,'WebGL tool-tree manifest changed');doc=json.loads(raw)
 require(doc.get('schema')==1 and doc.get('prior_tree_sha256')==PRIOR_TREE and isinstance(doc.get('previous'),dict),'Invalid WebGL tool-tree manifest')
 previous=dict(current)
 for name,value in doc['previous'].items():
  require(name in previous,'WebGL projection path missing: '+name)
  if value is None:del previous[name]
  else:require(validhash(value),'Invalid WebGL predecessor hash');previous[name]=value
 require(old.canonical(previous)==PRIOR_TREE,'WebGL historical tool tree differs');return previous

def project_reviewed_tree(root,current):
 validate_review(root,current);return project_tree(root,current)
