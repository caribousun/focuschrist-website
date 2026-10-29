"""Fail-closed current mobile review and historical tool projection.

A normalized hash is structural. It does not authenticate a reviewer or grant
owner approval. The current code receipt remains unset until independently
verified against the actual finished code and original review evidence.
"""
import hashlib,json,re
from pathlib import Path
import timeline_world_mobile_successor as mobile
from timeline_search_index_successor import source
ROOT=Path(__file__).resolve().parents[1]
TREE_MANIFEST='docs/timeline-mobile-collapse/historical-tool-tree.json'
TREE_MANIFEST_SHA256='2365c9e4ba678edb61c7a0eada4ee6ef3c85f81b170214ad9b402b13c3537bea'
PRIOR_TREE='aaa382b3bfce68fe1fa43688a76e26c959daad5f076fb23e383e197e480efcb5'
PRIOR_CODE_REVIEW='docs/timeline-mobile-collapse/independent-code-review.json'
PRIOR_CODE_REVIEW_SHA256='bc6b5dec753b3f67405003d2e4613e22f0394845e715bb875e59a867993844c7'
CODE_REVIEW='docs/timeline-mobile-collapse/current-code-review.json'
MOBILE_CODE_REVIEW_SHA256=None
MOBILE_CODE_REVIEWER_COMMITMENT=None
MOBILE_CODE_REVIEW_RECEIPT_SHA256=None
MOBILE_IMPLEMENTER_COMMITMENT=None
PIN_NAMES=('MOBILE_CODE_REVIEW_SHA256','MOBILE_CODE_REVIEWER_COMMITMENT','MOBILE_CODE_REVIEW_RECEIPT_SHA256','MOBILE_IMPLEMENTER_COMMITMENT')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def validhash(value):return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None
def require(value,message):
 if not value:raise ValueError(message)
def project_tree(root,current):
 import timeline_current_index_closure as old
 raw=source(root,TREE_MANIFEST);require(sha(raw)==TREE_MANIFEST_SHA256,'Mobile tool-tree manifest changed')
 manifest=json.loads(raw);require(manifest.get('schema')==1 and manifest.get('prior_tree_sha256')==PRIOR_TREE and isinstance(manifest.get('previous'),dict),'Invalid mobile tool-tree manifest')
 previous=dict(current)
 for name,expected in manifest['previous'].items():
  require(name in previous,'Mobile projection path missing: '+name)
  if expected is None:del previous[name]
  else:require(validhash(expected),'Invalid mobile projection hash');previous[name]=expected
 require(old.canonical(previous)==PRIOR_TREE,'Mobile historical tool tree differs')
 return previous

def project_reviewed_tree(root,current):
 """Require genuine exact current evidence before using historical tool bytes."""
 import timeline_current_index_closure as old
 root=Path(root).resolve();mobile.validate_albert_content_review(root);mobile.validate_newton_visual_review(root)
 prior=source(root,PRIOR_CODE_REVIEW);require(sha(prior)==PRIOR_CODE_REVIEW_SHA256,'Prior bounded mobile code review changed')
 require(all(validhash(x) for x in (MOBILE_CODE_REVIEW_SHA256,MOBILE_CODE_REVIEWER_COMMITMENT,MOBILE_CODE_REVIEW_RECEIPT_SHA256)),'PENDING independently verified current mobile code review')
 require(validhash(MOBILE_IMPLEMENTER_COMMITMENT),'PENDING independently verified mobile implementer commitment')
 require(MOBILE_CODE_REVIEWER_COMMITMENT!=MOBILE_IMPLEMENTER_COMMITMENT,'Mobile code reviewer must be distinct from implementer')
 raw=source(root,CODE_REVIEW);require(sha(raw)==MOBILE_CODE_REVIEW_SHA256,'Current mobile code review changed')
 review=json.loads(raw)
 require(review.get('schema')=='timeline-mobile-current-code-review-v1' and review.get('scope')=='mobile_visual_gate_and_tool_tree_successor' and review.get('verdict')=='CONCUR_WITHIN_BOUNDED_CODE_SCOPE','Current mobile code review scope differs')
 require(review.get('reviewer_commitment')==MOBILE_CODE_REVIEWER_COMMITMENT and review.get('receipt_sha256')==MOBILE_CODE_REVIEW_RECEIPT_SHA256,'Current mobile reviewer evidence differs')
 require(review.get('implementer_commitment')==MOBILE_IMPLEMENTER_COMMITMENT,'Current mobile implementer association differs')
 require(review.get('page_sha256')==mobile.AFTER and review.get('controller_sha256')==mobile.CONTROLLER_SHA and review.get('browser_test_sha256')==mobile.BROWSER_TEST_SHA,'Current mobile reviewed subject differs')
 require(review.get('albert_review_sha256')==mobile.ALBERT_CONTENT_REVIEW_SHA and review.get('newton_review_sha256')==mobile.NEWTON_VISUAL_REVIEW_SHA and review.get('prior_code_review_sha256')==PRIOR_CODE_REVIEW_SHA256,'Current mobile review evidence differs')
 require(review.get('tree_manifest_sha256')==TREE_MANIFEST_SHA256 and review.get('current_tool_tree_sha256')==old.canonical(current),'Current reviewed mobile tool tree differs')
 require(old.timestamp(review.get('reviewed_at'))>=old.timestamp('2026-10-29T17:48:40Z'),'Mobile code review predates visual review')
 return project_tree(root,current)
