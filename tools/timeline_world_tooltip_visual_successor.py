"""Validate the bounded tooltip visual receipt and reconstruct reviewed predecessors.

This verifies exact evidence structure; it does not authenticate reviewers,
verify external map providers, or grant owner or release approval. It is not
wired into the release gate while current code and provider reviews are pending.
"""
import base64,hashlib,json
from pathlib import Path
import timeline_world_mobile_successor as mobile
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/timeline-mobile-collapse/tooltip-source-delta.json'
MANIFEST_SHA='934c65c74e0a30589abeca265dccfb158682e89aa94e63e039cd1fe3f4be6a26'
REVIEW='docs/timeline-mobile-collapse/newton-tooltip-visual-review.json'
REVIEW_SHA='0772e94a71e6fc9a8297317a22e75985945533facf73c3754b3c6d523393c692'
CODE_REVIEW='docs/timeline-mobile-collapse/independent-tooltip-code-review.json'
CODE_REVIEW_SHA='5a35a198921a38bf224deaa86388a186925208945d17bc4549f9b7f7012f4b41'
BASE='adcad6a89a114917461305cba82178719e20b310'
HEAD='b6a5f277394d672b5f234984eafcee1448d226b4'
PAGE_AFTER='d67a067e9d90d64b992d21382d07307a91b3770132b1d6db3b451e46683c69a1'
TEST_AFTER='729bd30fcece4b72ec0bba3bbfcd61ca13765daa9ece266c6cd6f1b2161a6dd8'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def reconstruct(root=ROOT):
 root=Path(root).resolve();raw=mobile.source(root,MANIFEST)
 if sha(raw)!=MANIFEST_SHA:raise ValueError('Changed tooltip source manifest')
 doc=json.loads(raw)
 if doc.get('schema')!=1 or doc.get('base_commit')!=BASE or not isinstance(doc.get('files'),list):raise ValueError('Invalid tooltip source manifest')
 rows=doc['files'];expected={mobile.PAGE:(mobile.AFTER,PAGE_AFTER,2),mobile.BROWSER_TEST:(mobile.BROWSER_TEST_SHA,TEST_AFTER,1)}
 if len(rows)!=len(expected) or {r.get('path') for r in rows}!=set(expected):raise ValueError('Tooltip source paths differ')
 prior={}
 for row in rows:
  name=row['path'];before_hash,after_hash,n=expected[name]
  if row.get('before_sha256')!=before_hash or row.get('after_sha256')!=after_hash:raise ValueError('Tooltip source hashes differ')
  current=mobile.source(root,name)
  if sha(current)!=after_hash:raise ValueError('Unreviewed tooltip source: '+name)
  changes=row.get('changes')
  if not isinstance(changes,list) or len(changes)!=n:raise ValueError('Invalid tooltip source changes')
  for item in reversed(changes):
   if set(item)!={'before_b64','after_b64'}:raise ValueError('Invalid tooltip source change')
   try:before=base64.b64decode(item['before_b64'],validate=True);after=base64.b64decode(item['after_b64'],validate=True)
   except (ValueError,TypeError) as exc:raise ValueError('Invalid tooltip source encoding') from exc
   if not after or before==after or current.count(after)!=1:raise ValueError('Tooltip source context differs')
   current=current.replace(after,before,1)
  if sha(current)!=before_hash:raise ValueError('Tooltip predecessor differs: '+name)
  prior[name]=current
 if sha(mobile.source(root,mobile.CONTROLLER))!=mobile.CONTROLLER_SHA:raise ValueError('Mobile controller changed')
 return prior

def validate_visual_review(root=ROOT):
 """Bind the actual inspected screenshots and report, retaining explicit limits."""
 root=Path(root).resolve();prior=reconstruct(root);raw=mobile.source(root,REVIEW)
 if sha(raw)!=REVIEW_SHA:raise ValueError('Tooltip visual review changed')
 review=json.loads(raw);candidate=review.get('candidate',{});evidence=review.get('hosted_evidence',{})
 if review.get('schema')!=1 or review.get('reviewer_role')!='Newton independent visual reviewer' or review.get('reviewed_at_utc')!='2026-10-29T18:46:52Z':raise ValueError('Tooltip reviewer differs')
 if review.get('verdict')!='Pass for the inspected tooltip and disclosure pixels and the reported hosted interaction scope only; not release or owner approval.':raise ValueError('Tooltip review scope differs')
 if candidate.get('repository')!='caribousun/focuschrist-website' or candidate.get('pull_request')!=544 or candidate.get('head')!=HEAD or candidate.get('page_sha256')!=PAGE_AFTER or candidate.get('test_sha256')!=TEST_AFTER or candidate.get('controller_sha256')!=mobile.CONTROLLER_SHA:raise ValueError('Tooltip review subject differs')
 if evidence.get('run_id')!=40931777047 or evidence.get('timeline_job_id')!=123652298134 or evidence.get('timeline_job_conclusion')!='success' or evidence.get('artifact_id')!=12924265396:raise ValueError('Tooltip hosted evidence differs')
 if not any('real provider-backed tiles' in line and 'unverified' in line for line in review.get('limits',[])):raise ValueError('Provider limitation missing')
 return {'review':review,'previous_sources':prior}

def validate_code_review(root=ROOT):
 """Bind the existing standalone code review; final integration remains pending."""
 root=Path(root).resolve();visual=validate_visual_review(root);raw=mobile.source(root,CODE_REVIEW)
 if sha(raw)!=CODE_REVIEW_SHA:raise ValueError('Tooltip code review changed')
 review=json.loads(raw)
 if review.get('schema')!='timeline-tooltip-independent-code-review-v1' or review.get('scope')!='tooltip_source_delta_and_standalone_visual_successor' or review.get('verdict')!='CONCUR_WITHIN_BOUNDED_CODE_SCOPE':raise ValueError('Tooltip code review scope differs')
 if review.get('reviewed_source_head')!=HEAD or review.get('source_successor_head')!='dc0bbca7ea2168c39eaf7f67637651aa894e47d0' or review.get('page_sha256')!=PAGE_AFTER or review.get('browser_test_sha256')!=TEST_AFTER or review.get('controller_sha256')!=mobile.CONTROLLER_SHA:raise ValueError('Tooltip code review subject differs')
 if review.get('visual_review_sha256')!=REVIEW_SHA or review.get('source_manifest_sha256')!=MANIFEST_SHA:raise ValueError('Tooltip code review inputs differ')
 if review.get('successor_sha256')!='36ee1be79127890a2d6b0eb46ee63bedf82ac92b5e375429d5cfcbd24a5516f9' or review.get('successor_test_sha256')!='87c9c12e65d4b8a2d257ee645a4dba7b411c70f538b987ed6e328bde08a332f2':raise ValueError('Tooltip code review historic inputs differ')
 if review.get('reviewer_commitment')!='25275b95cc2c78a6aef8f6ac29e2400b0fac0290ab5ec12f9946448301ee8133' or review.get('receipt_sha256')!='04f2508f1dd2aaf7d6973e7864c8bd60ec17c28e1da5a637fab702bb9534b19a' or review.get('reviewed_at')!='2026-10-29T18:57:42Z':raise ValueError('Tooltip code reviewer differs')
 from timeline_world_mobile_release_successor import MOBILE_IMPLEMENTER_COMMITMENT,validhash
 if not validhash(MOBILE_IMPLEMENTER_COMMITMENT) or review['reviewer_commitment']==MOBILE_IMPLEMENTER_COMMITMENT:raise ValueError('Tooltip code reviewer must differ from implementer with a valid commitment')
 limits=review.get('limits',[])
 if not any('not yet wired into release gate' in line for line in limits) or not any('provider' in line and 'verification' in line for line in limits):raise ValueError('Tooltip code review limits missing')
 return {'code_review':review,'visual_review':visual}
