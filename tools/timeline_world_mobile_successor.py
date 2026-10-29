"""Exact mobile-controls source projection; mechanical only, not review or release."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGE='timelines/world-and-scripture-timeline.html'
CONTROLLER='timeline-mobile-collapse.js'
MANIFEST='docs/timeline-mobile-collapse/world-source-delta.json'
MANIFEST_SHA='4a5078da187cb1a4845e4bcd048dce70b07bbc663ca79e9b0bae9f5d274be1ed'
BEFORE='016e9896db70ff0a8a142503f289f2e0cbd2f4d96b73d667247dbb2a2370ceef'
AFTER='e6331171d55a522bd411bd27b58ebe23335d04313cab0426bee9b1c64f0d2805'
CONTROLLER_SHA='d1738fa1b95e3c2f2e6690175050e95f3183c9f334b8fe57e9af8a7f20170049'
ALBERT_CONTENT_REVIEW='docs/timeline-mobile-collapse/albert-content-review.json'
ALBERT_CONTENT_REVIEW_SHA='c2e89d1e0df8f5124b12f6babb7a2a7da22558bc7bea5339d7c17078a5563463'
NEWTON_VISUAL_REVIEW='docs/timeline-mobile-collapse/newton-visual-review.json'
NEWTON_VISUAL_REVIEW_SHA='71ae439b9d9af95d9d57f8911e65506dc5cff29e769758f74ea9a3825a0eaf7d'
BROWSER_TEST='tools/timeline_requested_browser_qa.js'
BROWSER_TEST_SHA='6217c553bae48a8c66804c85394e7ce2b3c7ed68f857e3ff718d327fd3a40c97'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def source(root,name):
 root=Path(root).resolve();parts=Path(name).parts;p=root.joinpath(*parts)
 assert not Path(name).is_absolute() and '..' not in parts
 assert all(not root.joinpath(*parts[:i]).is_symlink() for i in range(1,len(parts)+1))
 assert p.is_file() and p.resolve().is_relative_to(root),'Missing or unsafe mobile source'
 return p.read_bytes()
def restore(raw,root=ROOT):
 from timeline_world_webgl_successor import AFTER as WEBGL_AFTER,restore_page
 if sha(raw)==WEBGL_AFTER:raw=restore_page(raw,root)
 from timeline_world_tooltip_visual_successor import PAGE_AFTER as TOOLTIP_AFTER,validate_code_review
 if sha(raw)==TOOLTIP_AFTER:
  raw=validate_code_review(root)['visual_review']['previous_sources'][PAGE]
 manifest=source(root,MANIFEST);assert sha(manifest)==MANIFEST_SHA,'Mobile source manifest changed'
 row=json.loads(manifest);assert set(row)=={'schema','path','before_sha256','after_sha256','controller_path','controller_sha256','changes'}
 assert row['schema']==1 and row['path']==PAGE and row['before_sha256']==BEFORE and row['after_sha256']==AFTER
 assert row['controller_path']==CONTROLLER and row['controller_sha256']==CONTROLLER_SHA
 assert sha(source(root,CONTROLLER))==CONTROLLER_SHA,'Mobile controller changed'
 assert sha(raw)==AFTER,'Unreviewed mobile controls source'
 assert isinstance(row['changes'],list) and len(row['changes'])==5
 for item in reversed(row['changes']):
  assert set(item)=={'before_b64','after_b64'}
  before=base64.b64decode(item['before_b64'],validate=True);after=base64.b64decode(item['after_b64'],validate=True)
  assert before!=after and after and raw.count(after)==1,'Mobile successor context changed'
  raw=raw.replace(after,before,1)
 assert sha(raw)==BEFORE,'Mobile predecessor mismatch'
 return raw

def validate_albert_content_review(root=ROOT):
 """Bind the actual bounded wording/scope review; rendered review remains separate."""
 restore(source(root,PAGE),root)
 raw=source(root,ALBERT_CONTENT_REVIEW);assert sha(raw)==ALBERT_CONTENT_REVIEW_SHA,'Albert content review changed'
 review=json.loads(raw)
 assert review.get('schema')=='timeline-mobile-content-review-v1' and review.get('reviewer')=='Albert'
 assert review.get('reviewed_head')=='64c18e410febf0b761281da1457b65e8e1cf8aac'
 assert review.get('page_sha256')==AFTER and review.get('controller_sha256')==CONTROLLER_SHA
 assert review.get('verdict')=='CONCUR_UI_WORDING_AND_TARGET_SCOPE_ONLY'
 assert review.get('limits')==['not_render_acceptance','not_desktop_parity_proof','not_full_historical_source_reverification','not_owner_release_approval','draft_creation_authorization_pending']
 return review

def validate_newton_visual_review(root=ROOT):
 """Bind Newton's actual bounded visual review, not owner or release approval."""
 restore(source(root,PAGE),root)
 test=source(root,BROWSER_TEST)
 from timeline_world_tooltip_visual_successor import TEST_AFTER as TOOLTIP_TEST_AFTER,validate_code_review,restore_browser_test
 test=restore_browser_test(test,root)
 if sha(test)==TOOLTIP_TEST_AFTER:test=validate_code_review(root)['visual_review']['previous_sources'][BROWSER_TEST]
 assert sha(test)==BROWSER_TEST_SHA,'Reviewed mobile browser test changed'
 raw=source(root,NEWTON_VISUAL_REVIEW);assert sha(raw)==NEWTON_VISUAL_REVIEW_SHA,'Newton visual review changed'
 review=json.loads(raw)
 assert review.get('schema')==1 and review.get('reviewer_role')=='Newton independent visual reviewer'
 assert review.get('reviewed_at_utc')=='2026-10-29T17:48:40Z'
 assert review.get('source_receipt_sha256')=='a73cb645df0db59ce3051c3f93a76d2ad3f21a9e0d011c88f78f315ae40a3b30'
 assert review.get('candidate')=={'repository':'caribousun/focuschrist-website','pull_request':544,'head':'4680e7f9271aa6f85c0509af447e5245d3245555','checkout':'55353c653fb1f4cfe9142d1f54c2a7833873c0f8','checkout_tree':'a5f0adf29a8e4862262f41689229f6449291458e','page_sha256':AFTER,'controller_sha256':CONTROLLER_SHA,'browser_test_sha256':BROWSER_TEST_SHA}
 evidence=review.get('hosted_evidence')
 assert isinstance(evidence,dict) and evidence=={'run_id':40922753752,'attempt':1,'timeline_job_id':123620093002,'timeline_job_conclusion':'success','artifact_id':12919467124,'artifact_sha256':'afbe2d874b647bf619436d3c59efb07e169b77b22c6f4200220d2e09d50d8bca','timeline_report_sha256':'8ec5548d32f7e8e307a5d53eeddc0590b972bc534068f42d51aaea5bfa7f27d1','controls_report_sha256':'f7f26e2488813619811584ddfa17c74e4adbfc17870c76edfae452ee6b5bd485','desktop_parity_report_sha256':'302db4e5cfe66825cde8d687947c8fcb0aee3897af3d12b5702b5ec55e558d33'}
 assert review.get('verdict')=='Accepted only for changed disclosures in personally inspected hosted 390x844 phone and 1366x900 desktop pixels and separately reported automated browser-test scope.'
 assert review.get('limitations')==['The successful hosted interaction assertions were not personally rerun; they are distinguished from actual screenshot inspection.',"A phone map tooltip at the right edge shows only Lehi's fa…; no like-for-like baseline establishes whether it predates this candidate or was caused by it.",'Map provider tiles were unavailable or unverified in the hosted environment.','No physical-device, comprehensive accessibility, full-site, all-CI, owner-approval, production or release acceptance is claimed.']
 return review
