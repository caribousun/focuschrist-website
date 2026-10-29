"""Fail-closed final tooltip code review and historical tool-tree projection.

Review pins must be populated only from a genuine independently reviewed final
candidate. Provider-backed visual verification and owner release approval remain
separate; this structural adapter does not authenticate people or approve release.
A later matched run requires independent review or reconciliation; the pinned
subject proves only which static run and source the submitted review addresses.
"""
import hashlib,json,re
from pathlib import Path
import timeline_world_tooltip_visual_successor as tooltip
import timeline_world_mobile_successor as mobile
from timeline_world_mobile_release_successor import MOBILE_IMPLEMENTER_COMMITMENT
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/timeline-mobile-collapse/tooltip-tool-tree.json'
MANIFEST_SHA256='5a4deb7627d333842606f0de24cbf3ba633b892957466034de4ae99948765ca4'
PRIOR_TREE='69f383f0133a0e52ebe77f1762fd8f144acd32e3df3278bdff0c90df135cd1bc'
CODE_REVIEW='docs/timeline-mobile-collapse/tooltip-final-integration-code-review.json'
CODE_REVIEW_SHA256=None
CODE_REVIEWER_COMMITMENT=None
CODE_RECEIPT_SHA256=None
# Actual independent provider screenshot review remains pending until supplied.
PROVIDER_REVIEW='docs/timeline-mobile-collapse/independent-provider-visual-review.json'
PROVIDER_REVIEW_SHA256='75f0c77147ebafd5d6457442ca5673c61530b7b9d1ca88d4e467f53ecc2b3b12'
PROVIDER_REVIEWER_COMMITMENT='525f8397911fea9f0d93b899cc987fd2a84c7aa01374e7735bc5622336381da6'
PROVIDER_RECEIPT_SHA256='102e91434dfd855d911546f6c6b9bc6353ba3128f994fa46e5a1ef377a5b2789'
PROVIDER_SUBJECT_SHA256='96630184666a659e173bb0cb875fc2c7269424b2a79d9321f724d4d675e09908'
PIN_NAMES=('CODE_REVIEW_SHA256','CODE_REVIEWER_COMMITMENT','CODE_RECEIPT_SHA256','PROVIDER_REVIEW_SHA256','PROVIDER_REVIEWER_COMMITMENT','PROVIDER_RECEIPT_SHA256','PROVIDER_SUBJECT_SHA256')
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

def validate_provider_visual_review(root):
 """Structural binding only; the genuine reviewer and receipt require independent verification."""
 require(all(validhash(x) for x in (PROVIDER_REVIEW_SHA256,PROVIDER_REVIEWER_COMMITMENT,PROVIDER_RECEIPT_SHA256,PROVIDER_SUBJECT_SHA256)), 'PENDING independent provider visual review')
 require(validhash(MOBILE_IMPLEMENTER_COMMITMENT) and PROVIDER_REVIEWER_COMMITMENT!=MOBILE_IMPLEMENTER_COMMITMENT,'Provider visual reviewer must differ from a valid implementer')
 raw=mobile.source(root,PROVIDER_REVIEW);require(sha(raw)==PROVIDER_REVIEW_SHA256,'Provider visual review changed');review=json.loads(raw)
 require(review.get('schema')=='timeline-provider-visual-review-v1' and review.get('scope')=='provider_desktop_phone_pixels' and review.get('verdict')=='CONCUR_WITHIN_BOUNDED_VISUAL_SCOPE','Provider visual review scope differs')
 require(review.get('reviewer_commitment')==PROVIDER_REVIEWER_COMMITMENT and review.get('receipt_sha256')==PROVIDER_RECEIPT_SHA256,'Provider visual reviewer evidence differs')
 diagnostic=review.get('observed_diagnostic');offline=review.get('offline_evaluation')
 require(isinstance(diagnostic,dict) and isinstance(offline,dict),'Provider visual source or correlation missing')
 # These are selected unchanged fields from the independently authored record.
 subject={key:review.get(key) for key in ('run_id','timeline_job_id','artifact_id','head','checkout','page_sha256','artifact_sha256','report_sha256','desktop_screenshot_sha256','phone_screenshot_sha256','raw_status')}
 subject.update({'diagnostic_source_commit':diagnostic.get('source_commit'),'diagnostic_sha256':diagnostic.get('sha256'),'offline_classifier_sha256':offline.get('classifier_sha256'),'offline_receipt_sha256':offline.get('receipt_sha256'),'desktop_correlation':offline.get('desktop_classification')})
 import timeline_current_index_closure as old
 require(old.canonical(subject)==PROVIDER_SUBJECT_SHA256,'Provider visual review subject differs')
 for field in ('run_id','timeline_job_id','artifact_id'):
  require(type(subject[field]) is int and subject[field]>0,'Provider visual run identity invalid: '+field)
 for field in ('head','checkout','diagnostic_source_commit'):
  require(isinstance(subject[field],str) and re.fullmatch(r'[0-9a-f]{40}',subject[field]) is not None,'Provider visual source identity invalid: '+field)
 require(subject['diagnostic_source_commit']==subject['head'],'Provider diagnostic source commit differs')
 require(subject['page_sha256']==tooltip.PAGE_AFTER,'Provider visual review page differs')
 for field in ('diagnostic_sha256','artifact_sha256','report_sha256','desktop_screenshot_sha256','phone_screenshot_sha256','offline_classifier_sha256','offline_receipt_sha256'):
  require(validhash(subject[field]),'Provider visual review evidence missing: '+field)
 require(subject['raw_status']=='Historical run and desktop diagnostic FAIL; phone diagnostic PASS. No historical job result was changed.' and subject['desktop_correlation']=='MATCHED_RENDERER_CANCELLATION','Provider visual diagnostic outcomes differ')
 return review

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
 for field,name in (('provider_diagnostic_sha256','tools/world_provider_browser_diagnostic.js'),('provider_diagnostic_test_sha256','tools/test_world_provider_browser_diagnostic.js'),('provider_cancellation_classifier_sha256','tools/world_provider_cancellation_review.js'),('provider_cancellation_classifier_test_sha256','tools/test_world_provider_cancellation_review.js')):
  require(review.get(field)==sha(mobile.source(root,name)),'Final tooltip diagnostic subject differs')
 require(review.get('current_browser_test_sha256')==sha(mobile.source(root,mobile.BROWSER_TEST)) and review.get('resize_test_manifest_sha256')==tooltip.RESIZE_TEST_MANIFEST_SHA,'Final resize test review inputs differ')
 require(review.get('current_tool_tree_sha256')==old.canonical(current),'Final reviewed tooltip tool tree differs')
 require(old.timestamp(review.get('reviewed_at'))>=old.timestamp('2026-10-29T18:57:42Z'),'Final tooltip review predates prior review')
 validate_provider_visual_review(root)
 return project_tree(root,current)
