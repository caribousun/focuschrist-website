"""Fail-closed final tooltip code review and historical tool-tree projection.

Review pins must be populated only from a genuine independently reviewed final
candidate. Provider-backed visual verification and owner release approval remain
separate; this structural adapter does not authenticate people or approve release.
"""
import hashlib,json,re
from pathlib import Path
import timeline_world_tooltip_visual_successor as tooltip
import timeline_world_mobile_successor as mobile
from timeline_world_mobile_release_successor import MOBILE_IMPLEMENTER_COMMITMENT
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/timeline-mobile-collapse/tooltip-tool-tree.json'
MANIFEST_SHA256='950282bcd7ceebe0adb8ad35073a969763e71d3852f61e05b4711db6c070e044'
PRIOR_TREE='69f383f0133a0e52ebe77f1762fd8f144acd32e3df3278bdff0c90df135cd1bc'
CODE_REVIEW='docs/timeline-mobile-collapse/tooltip-final-integration-code-review.json'
CODE_REVIEW_SHA256=None
CODE_REVIEWER_COMMITMENT=None
CODE_RECEIPT_SHA256=None
PIN_NAMES=('CODE_REVIEW_SHA256','CODE_REVIEWER_COMMITMENT','CODE_RECEIPT_SHA256')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def validhash(value):return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None
def require(value,message):
 if not value:raise ValueError(message)
def project_tree(root,current):
 import timeline_current_index_closure as old
 raw=mobile.source(root,MANIFEST);require(sha(raw)==MANIFEST_SHA256,'Tooltip tool-tree manifest changed')
 doc=json.loads(raw);require(doc.get('schema')==1 and doc.get('prior_tree_sha256')==PRIOR_TREE and isinstance(doc.get('previous'),dict),'Invalid tooltip tool-tree manifest')
 previous=dict(current)
 for name,value in doc['previous'].items():
  require(name in previous,'Tooltip projection path missing: '+name)
  if value is None:del previous[name]
  else:require(validhash(value),'Invalid tooltip predecessor hash');previous[name]=value
 require(old.canonical(previous)==PRIOR_TREE,'Tooltip historical tool tree differs')
 return previous

def project_reviewed_tree(root,current):
 """Check the actual current review before restoring prior code bytes."""
 import timeline_current_index_closure as old
 root=Path(root).resolve();tooltip.validate_code_review(root)
 require(all(validhash(x) for x in (CODE_REVIEW_SHA256,CODE_REVIEWER_COMMITMENT,CODE_RECEIPT_SHA256)),'PENDING independent final tooltip integration code review')
 require(validhash(MOBILE_IMPLEMENTER_COMMITMENT) and CODE_REVIEWER_COMMITMENT!=MOBILE_IMPLEMENTER_COMMITMENT,'Final tooltip reviewer must differ from a valid implementer')
 raw=mobile.source(root,CODE_REVIEW);require(sha(raw)==CODE_REVIEW_SHA256,'Final tooltip code review changed');review=json.loads(raw)
 require(review.get('schema')=='timeline-tooltip-final-integration-code-v1' and review.get('scope')=='tooltip_integration_and_exact_tool_tree' and review.get('verdict')=='CONCUR_WITHIN_BOUNDED_CODE_SCOPE','Final tooltip code review scope differs')
 require(review.get('reviewer_commitment')==CODE_REVIEWER_COMMITMENT and review.get('receipt_sha256')==CODE_RECEIPT_SHA256,'Final tooltip reviewer evidence differs')
 require(review.get('implementer_commitment')==MOBILE_IMPLEMENTER_COMMITMENT,'Final tooltip implementer association differs')
 require(review.get('page_sha256')==tooltip.PAGE_AFTER and review.get('browser_test_sha256')==tooltip.TEST_AFTER and review.get('controller_sha256')==mobile.CONTROLLER_SHA,'Final tooltip source differs')
 require(review.get('visual_review_sha256')==tooltip.REVIEW_SHA and review.get('prior_code_review_sha256')==tooltip.CODE_REVIEW_SHA and review.get('source_manifest_sha256')==tooltip.MANIFEST_SHA and review.get('tree_manifest_sha256')==MANIFEST_SHA256,'Final tooltip review inputs differ')
 for field,name in (('provider_diagnostic_sha256','tools/world_provider_browser_diagnostic.js'),('provider_diagnostic_test_sha256','tools/test_world_provider_browser_diagnostic.js')):
  require(review.get(field)==sha(mobile.source(root,name)),'Final tooltip diagnostic subject differs')
 require(review.get('current_tool_tree_sha256')==old.canonical(current),'Final reviewed tooltip tool tree differs')
 require(old.timestamp(review.get('reviewed_at'))>=old.timestamp('2026-10-29T18:57:42Z'),'Final tooltip review predates prior review')
 return project_tree(root,current)
