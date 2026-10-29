"""Exact public Emma evidence protocol, with separately verified private evidence.

Hashes do not authenticate reviewers, establish historical provider timing, or
prove aesthetics. The private verifier must independently inspect the original
records and approve the exact statement before its hash is pinned here.
"""
import hashlib,json,re
from io import BytesIO
from pathlib import Path
from PIL import Image, __version__ as PIL_VERSION, features
from artwork_emma_story_delivery import bound,canonical,local,require,stamp
from artwork_emma_journey_delivery import ASSETS,SCENES,ID_MASTER,EXPRESSION,MANDATES,ROUTE

SUBJECT='docs/emma-journey-public/subject-draft.json'
VERIFICATION='docs/emma-journey-public/private-verification.json'
CHECK_REPORT='docs/emma-journey-public/pre-release-checks.json'
# Only exact statements independently checked against their private sources may
# be pinned. Missing pins are a hard release failure.
SUBJECT_SHA256='6495aaa91690e698ea304e7cbbee3ff3e40d5b8b490d2f656190056caeabc8a0'
VERIFICATION_SHA256='903e4289b665a8df19855e0b04e6e5bdb8989208db2b5bf3e83c496de6222613'
CHECK_REPORT_SHA256='4bdc6284a77bd01292a60ae33d834ddfb58995c148827b506f91bb681a6f94a1'
ARTWORK_DIAGNOSTIC_SHA256='f318c676e7924a58816ea19bac75258eaacff1e1525f2d2567840ecff5061dcc'
ARTWORK_VERIFIER_COMMITMENT='1f57b92308976fda71c75c28b63ec09c84921753868ad3bca4ec0e548bbd8fe4'
CODE_REVIEW_RECEIPT_SHA256='61e66ca0c94e58cd90a750e1b9689ff2686cce583041c42b92afd8d98f435d4a'
CODE_REVIEWER_COMMITMENT='f56645eb81e8ba97eba77865a589a417cae54ba6d533a6762adac31f19a844c2'
PRE_RELEASE_RECEIPT_SHA256='3f3c287bee2f42995949dfa5b9888d24eb30e6248648db4ebef5f12125578f54'
PRE_RELEASE_VERIFIER_COMMITMENT='0bbc0130d4bb79fa938a26dc2fe0ef25f218f8ef93773192e86fc822748063af'
PRIVATE_SPEC='d3d9cfbd51a6af4e699bcc39bc1fa7606e0cdb44fa47adb5704340034fdef3c8'
OWNER_METADATA='862623b24c30f66d73abedab2b87fae4f1f9ef62639c1e3382ddda8b114c9db4'
OWNER_READBACK='0e0e6d56df3997fdf201c5c92548c155021527b0c2dd2e47fe9ae0d75ce0b9fd'
OWNER_TIME_COMMITMENT='21e09b456fc7aa6088598993d3cebf49f177a621e15c3fafcf50e2ac77144d59'
OWNER_VERIFICATION_RECEIPT='9c5e571a16ec53475b0e08fe1ac79fe03cb00c9377469c9cd05a3d53abc1bfa5'
OPTIONAL_MANDATES={'docs/section-panel-design-mandate.md':'26a8028ec7c7393d070e6f8006662861e1651643dbf925092b19d364ace797fc'}
CHECKS={'source_and_prose','artwork_and_provenance','panel','gallery','search','navigation_and_controls','desktop_render','phone_render','narrow_render','validator_code_review'}
FINAL_CHECKS={'current_source','chronology_and_sources','retained_art','new_art','controls_and_navigation','desktop_render','phone_render'}
PRIVATE_PROOFS={'review_manifest','operator_certificate','independent_extraction','independent_lineage','original_target_recovery','original_target_map','reference_recovery','portable_policy','coordination_report','selected_preflight_description','selected_field_map'}
PIN_NAMES=('SUBJECT_SHA256','VERIFICATION_SHA256','CHECK_REPORT_SHA256','ARTWORK_DIAGNOSTIC_SHA256','ARTWORK_VERIFIER_COMMITMENT','CODE_REVIEW_RECEIPT_SHA256','CODE_REVIEWER_COMMITMENT','PRE_RELEASE_RECEIPT_SHA256','PRE_RELEASE_VERIFIER_COMMITMENT')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_pinned(root,path,pin):
 require(isinstance(pin,str) and re.fullmatch(r'[0-9a-f]{64}',pin) is not None,'public evidence pin pending')
 p=local(Path(root).resolve(),path)
 raw=p.read_bytes();require(sha(raw)==pin,'public evidence changed')
 return json.loads(raw)
def issha(s):return isinstance(s,str) and re.fullmatch(r'[0-9a-f]{64}',s) is not None

def validate_review_order(completed, verification_time, review_times):
 require(review_times and completed>=max([verification_time,*review_times]),'pre-release report predates required evidence')

def normalized_validator_hash(root):
 """Bind all validator code except its independently reviewed pins."""
 raw=local(Path(root).resolve(),'tools/emma_public_commitments.py').read_bytes().decode('utf-8')
 for name in PIN_NAMES:
  pattern=r'(?m)^'+re.escape(name)+r"=(?:None|'[0-9a-f]{64}')$"
  matches=list(re.finditer(pattern,raw));require(len(matches)==1,'missing, duplicate or malformed review pin assignment')
  raw=re.sub(pattern,name+'=<REVIEWED_PIN>',raw,count=1)
 return sha(raw.encode())

def reviewed_tool_tree_hash(root):
 """Bind every tool file and the QA and deployment workflows."""
 root=Path(root).resolve();result={};require(not (root/'tools').is_symlink(),'symlink tool root')
 for path in sorted((root/'tools').rglob('*')):
  require(not path.is_symlink(),'symlink inside reviewed tool tree')
  if not path.is_file():continue
  rel=path.relative_to(root).as_posix()
  result[rel]=normalized_validator_hash(root) if rel=='tools/emma_public_commitments.py' else sha(path.read_bytes())
 for name in ('site-qa.yml','deploy-pages.yml'):
  path='.github/workflows/'+name;result[path]=sha(local(root,path).read_bytes())
 return canonical(result)

def validate_statement(root,subject):
 require(subject.get('schema')=='emma-public-subject-v1' and subject.get('classification')=='commitments_to_privately_verified_evidence','wrong public subject')
 require(subject.get('private_spec_sha256')==PRIVATE_SPEC and subject.get('source_manifest_sha256')==subject['bindings']['source_manifest_sha256'],'private subject mismatch')
 require(subject.get('provider_telemetry')=='UNKNOWN' and subject.get('historical_decision_times')=='UNKNOWN' and subject.get('original_target_ordering')=='current_recovery_and_operator_attestation','invented provider or historical timing')
 require(subject.get('historical_decisions')==44 and subject.get('preflight_decisions')==22 and subject.get('negative_history_entries')==22,'historical decision coverage mismatch')
 proofs=subject.get('private_evidence_sha256');require(isinstance(proofs,dict) and set(proofs)==PRIVATE_PROOFS and all(issha(v) for v in proofs.values()),'private evidence commitments missing')
 require(subject.get('owner_metadata_commitment')==OWNER_METADATA and subject.get('owner_private_readback_commitment')==OWNER_READBACK and subject.get('owner_scope')=='conditional_on_required_checks','owner conditional commitment mismatch')
 require(subject.get('owner_accepted_at_commitment')==OWNER_TIME_COMMITMENT and 'owner_accepted_at' not in subject,'owner acceptance time commitment mismatch')
 require(subject.get('rejected_filename_only_status')=='no_digest_recorded_distinct_traced_input_identifiers_no_global_exclusion_claim','filename-only exclusion status missing')
 require(subject.get('exclusion_scope')=='checked_creation_baseline_and_sitewide_registries_including_owner_rejections','exclusion scope mismatch')
 forbidden=subject.get('excluded_asset_sha256');require(isinstance(forbidden,list) and len(forbidden)==len(set(forbidden))==19 and all(issha(x) for x in forbidden) and {'5059b4aa414bf57dc9c46608c5c05255810c81faafb472808dfbd9370efdea73','a2bfece984203573f2d7bd1ecdbf64f97822211bf081c2ca29494e6dc0b420ff'}<=set(forbidden),'asset exclusion commitments incomplete')
 scenes=subject.get('scenes');require(isinstance(scenes,list) and len(scenes)==11 and {x['id'] for x in scenes}==set(SCENES),'scene coverage mismatch')
 decision_set=set();source_map={};assets=set()
 for row in scenes:
  i=row['id'];origin=i=='origin';require(row.get('kind')==('PERSON_FREE_CONTEXT' if origin else 'EMMA_CHARACTER'),'scene classification mismatch')
  require(issha(row.get('prompt_sha256')) and row['prompt_sha256'] not in forbidden and row.get('decision_timestamp_status')=='UNKNOWN','scene prompt or time mismatch')
  ds=row.get('decision_commitments');require(isinstance(ds,dict) and set(ds)=={'fermi_preflight','newton_preflight','fermi_finished','newton_finished'} and all(issha(v) for v in ds.values()),'scene review commitments missing')
  decision_set.update(ds.values());inputs=row.get('input_sha256_in_order');require(isinstance(inputs,list) and all(issha(v) and v not in forbidden for v in inputs),'invalid or rejected generation input')
  if origin:require(row.get('operation')=='generate' and inputs==[],'origin generation inputs mismatch')
  elif row.get('operation')=='generate':require(inputs==[ID_MASTER,EXPRESSION],'wrong generation references')
  else:require(row.get('operation')=='edit' and len(inputs)==3 and inputs[1:]==[ID_MASTER,EXPRESSION],'wrong edited input ordering')
  orig=row['original'];source_map[i]=orig['sha256'];name='assets/page-art/emma-journey/originals/emma-journey-'+i+'-source.png';require(orig['path']==name and orig['sha256'] not in forbidden,'wrong or rejected source image')
  base='assets/page-art/emma-journey/emma-journey-'+i;der=row['derivatives'];require(len(der)==3 and {x['path'] for x in der}=={base+'-'+str(w)+'.webp' for w in (640,960,1536)},'derivative family mismatch')
  for a in [orig,*der]:require(a['path'] not in assets,'duplicate asset');assets.add(a['path'])
 require(len(decision_set)==44 and assets==ASSETS,'missing or duplicate decisions or assets')
 roles=subject.get('reviews');require(isinstance(roles,list) and len(roles)==3 and {r['role'] for r in roles}=={'Fermi','Newton','Albert'},'current roles missing')
 require(len({r.get('actor_commitment') for r in roles})==3 and all(issha(r.get('actor_commitment')) for r in roles),'independent actor commitments missing')
 for r in roles:
  require(all(issha(r.get(k)) for k in ('assembled_receipt_sha256','final_receipt_sha256')) and set(r.get('final_checks',[]))==FINAL_CHECKS,'current review coverage incomplete')
  stamp(r['reconfirmed_at']);stamp(r['final_review_at']);mandates=r.get('mandate_bindings');require(isinstance(mandates,dict) and MANDATES<=set(mandates) and set(mandates)<=MANDATES|set(OPTIONAL_MANDATES),'current mandate coverage mismatch')
  for path in mandates:
   raw=local(Path(root).resolve(),path).read_bytes();require(sha(raw)==mandates[path] and (path not in OPTIONAL_MANDATES or mandates[path]==OPTIONAL_MANDATES[path]),'current mandate changed')
  require(r.get('scene_source_sha256')==source_map,'current source-scene coverage mismatch')
  if r['role'] in ('Fermi','Newton'):
   require(issha(r.get('handoff_receipt_sha256')) and r.get('full_resolution_inspected') is True and r.get('face_details_inspected') is True and set(r.get('face_scene_ids',[]))==set(SCENES)-{'origin'},'specialist handoff or pixel coverage missing')
  else:require(r.get('handoff_receipt_sha256') is None and r.get('full_resolution_inspected') is False and r.get('face_details_inspected') is False and r.get('face_scene_ids')==[],'Albert scope overstated')
 return scenes,assets,source_map

def validate_verification(root,subject,subject_sha):
 proof=read_pinned(root,VERIFICATION,VERIFICATION_SHA256)
 require(proof.get('schema')=='emma-independent-private-verification-v1' and proof.get('subject_sha256')==subject_sha and proof.get('verdict')=='PASS','private verification is absent or stale')
 require(proof.get('verdict_scope')=='bounded_projection_only' and proof.get('verification_model')=='direct_projection_with_attributed_private_verification','private verification scope overstated')
 require(proof.get('scope')==['exact_public_projection','distinct_actual_reviewers','historical_preflight_and_finished','ordered_generation_inputs','filename_only_owner_rejection','conditional_owner_readback'],'private verification scope incomplete')
 require(proof.get('limitations')==['not_provider_telemetry','historical_clock_times_unknown','not_owner_gate_waiver','not_release_approval','filename_only_identifier_comparison_not_digest'],'private verification limits changed')
 require(issha(proof.get('private_receipt_sha256')),'private verification receipt commitment missing')
 require(proof.get('owner_verification_receipt_sha256')==OWNER_VERIFICATION_RECEIPT and proof.get('owner_accepted_at_commitment')==OWNER_TIME_COMMITMENT and proof.get('owner_preceded_verification') is True,'private conditional owner chronology not verified')
 when=stamp(proof['verified_at']);require(stamp(proof['owner_verifier_event_at'])<=when,'owner verification event postdates certificate');return when

def validate_artwork(root,added,covered,rejected,pixel_hash,page_dependencies):
 subject=read_pinned(root,SUBJECT,SUBJECT_SHA256);scenes,expected,_=validate_statement(root,subject);validate_verification(root,subject,SUBJECT_SHA256)
 require(expected<=added and not expected&covered,'44 assets unavailable or covered twice')
 require(all(row['prompt_sha256'] not in rejected and not (set(row['input_sha256_in_order'])&rejected) for row in scenes),'runtime rejection includes prompt or generation input')
 context=subject.get('page_context');require(isinstance(context,list) and page_dependencies(root,ROUTE)<={x['path'] for x in context},'incomplete public page context')
 for p in context:bound(root,p)
 assets=set();hashes=set();pixels=set()
 require(PIL_VERSION=='12.2.0' and features.version('webp')=='1.6.0','wrong recorded derivative encoder')
 for row in scenes:
  original=row['original'];der=row['derivatives'];orig_raw=bound(root,original);require(sha(orig_raw) not in rejected,'owner rejected source')
  for entry in [original,*der]:
   raw=bound(root,entry);require(sha(raw) not in rejected and sha(raw) not in subject['excluded_asset_sha256'] and sha(raw) not in hashes and entry['pixel_sha256'] not in pixels,'duplicate or rejected bytes or pixels')
   path=Path(root)/entry['path'];require(pixel_hash(path)==entry['pixel_sha256'],'image pixel drift')
   with Image.open(path) as im:require(getattr(im,'n_frames',1)==1 and list(im.size)==entry['dimensions'],'image dimensions or frames changed')
   assets.add(entry['path']);hashes.add(sha(raw));pixels.add(entry['pixel_sha256'])
  require(original['dimensions']==[1536,1024] and {d['dimensions'][0] for d in der}=={640,960,1536},'wrong derivative dimensions')
  with Image.open(BytesIO(orig_raw)) as im:
   for d in der:
    width=d['dimensions'][0];scaled=im if width==1536 else im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
    out=BytesIO();scaled.save(out,format='WEBP',quality=92,method=6);require(out.getvalue()==bound(root,d),'derivative reproduction mismatch')
 return assets,hashes,pixels

def validate_render_files(root,subject,rejected):
 """Bind the two diagnostic screenshots as evidence, not page artwork."""
 rendered=subject['bindings'].get('rendered')
 require(isinstance(rendered,dict) and set(rendered)=={'desktop','phone'},'desktop and phone render bindings required')
 expected={'desktop':'docs/emma-journey-release/render/desktop-opening.jpg','phone':'docs/emma-journey-release/render/phone-opening.jpg'}
 paths=set()
 for label,minimum in (('desktop',1024),('phone',240)):
  row=rendered[label];entry=row['image'];require(entry['path']==expected[label],'unexpected render evidence path')
  raw=bound(root,entry);require(sha(raw) not in rejected and sha(raw) not in subject['excluded_asset_sha256'],'excluded or rejected render evidence')
  width=row['viewport_width'];height=row['viewport_height'];require(isinstance(width,int) and not isinstance(width,bool) and isinstance(height,int) and not isinstance(height,bool) and width>=minimum and height>=240 and (label!='phone' or width<=600),'invalid render viewport')
  with Image.open(BytesIO(raw)) as im:require(im.format in ('PNG','JPEG') and im.width==width and im.height>=height and getattr(im,'n_frames',1)==1,'render dimensions or format mismatch');im.verify()
  with Image.open(BytesIO(raw)) as im:im.load()
  paths.add(entry['path'])
 return paths

def cover_render_files(root,subject,added,covered,rejected):
 paths=validate_render_files(root,subject,rejected)
 require(paths<=added and not paths&covered,'Emma render evidence overlap or omission')
 return paths

def validate_release(root):
 """Require the separately pinned conditional acceptance check report."""
 from timeline_search_index_successor import AFTER as TIMELINE_SEARCH_SHA
 current_search=local(Path(root).resolve(),'site-search-index.json').read_bytes()
 projection=None
 if sha(current_search)==TIMELINE_SEARCH_SHA:
  from timeline_current_index_closure import prepare
  projection=prepare(root)
 def reviewed_bound(entry):
  if projection is not None and entry.get('path') in ('site-search-index.json','content-audit.json'):
   raw=projection['historical_search' if entry['path']=='site-search-index.json' else 'historical_content_audit']
   require(len(raw)==entry['bytes'] and sha(raw)==entry['sha256'],'historical index or content evidence changed')
   return raw
  return bound(root,entry)
 subject=read_pinned(root,SUBJECT,SUBJECT_SHA256);validate_statement(root,subject);verification_time=validate_verification(root,subject,SUBJECT_SHA256)
 from owner_journey_successor import validate_hub,validate_redirect,validate_hymns,validate_canonical,HUB,RETIRED,HYMNS
 root=Path(root);bindings=subject['bindings']
 for route,key,fn in ((HUB,'page_sha256',lambda b:validate_hub(b,root)),(RETIRED,'redirect_sha256',validate_redirect),(HYMNS,'hymns_sha256',validate_hymns),('sitemap.xml','sitemap_sha256',validate_canonical)):
  raw=local(root.resolve(),route).read_bytes();require(sha(raw)==bindings[key],'current reviewed source changed');fn(raw)
 require(bindings['delivery_spec_sha256']==PRIVATE_SPEC and bindings['source_manifest_sha256']==subject['source_manifest_sha256'],'reviewed delivery binding mismatch')
 validate_render_files(root,subject,set())
 report=read_pinned(root,CHECK_REPORT,CHECK_REPORT_SHA256)
 require(report.get('schema')=='emma-public-pre-release-checks-v1' and report.get('status')=='PASS' and report.get('subject_sha256')==SUBJECT_SHA256,'pre-release report absent or stale')
 require(report.get('verification_sha256')==VERIFICATION_SHA256 and issha(PRE_RELEASE_RECEIPT_SHA256) and report.get('private_checks_receipt_sha256')==PRE_RELEASE_RECEIPT_SHA256 and issha(PRE_RELEASE_VERIFIER_COMMITMENT) and report.get('verifier_commitment')==PRE_RELEASE_VERIFIER_COMMITMENT,'independent pre-release verification missing')
 checks=report.get('checks');require(isinstance(checks,dict) and set(checks)==CHECKS,'pre-release checks incomplete')
 completed=stamp(report['completed_at']);review_times=[stamp(r['reconfirmed_at']) for r in subject['reviews']]+[stamp(r['final_review_at']) for r in subject['reviews']]
 source_evidence=checks['source_and_prose'].get('evidence',[]);indexed={x['path']:x for x in source_evidence if isinstance(x,dict) and 'path' in x}
 index_path='docs/emma-journey-public/index-review-commitments.json';confirm_path='docs/emma-journey-public/closure-confirmations.json'
 require(index_path in indexed and confirm_path in indexed,'current closure review evidence missing')
 index=json.loads(bound(root,indexed[index_path]));confirm=json.loads(bound(root,indexed[confirm_path]))
 require(index.get('subject_sha256')==SUBJECT_SHA256 and confirm.get('subject_sha256')==SUBJECT_SHA256,'current closure review subject changed')
 review_times.extend(stamp(x['reviewed_at']) for x in index['reviews']);review_times.extend((stamp(confirm['fermi']['confirmed_at']),stamp(confirm['albert']['reviewed_at'])))
 validate_review_order(completed,verification_time,review_times)
 for name,item in checks.items():
  require(item.get('status')=='PASS' and stamp(item['completed_at'])<=completed and isinstance(item.get('evidence'),list) and item['evidence'],'pre-release check missing: '+name)
  for entry in item['evidence']:reviewed_bound(entry)
  if name=='source_and_prose':require(stamp(item['completed_at'])>=max(review_times),'source check predates reviews')
  if name in ('panel','gallery','search'):require(stamp(item['completed_at'])>=max(review_times),'index check predates current closure reviews')
  if name=='artwork_and_provenance':
   require(item.get('method')=='separate_pre_release_validation' and len(item['evidence'])==1,'artwork validation must be separate')
   evidence=json.loads(bound(root,item['evidence'][0]))
   require(evidence.get('schema')=='emma-independent-pre-release-artwork-v1' and evidence.get('status')=='PASS' and evidence.get('subject_sha256')==SUBJECT_SHA256 and evidence.get('verification_sha256')==VERIFICATION_SHA256,'pre-release artwork subject mismatch')
   require(evidence.get('final_release_command_used') is False and evidence.get('covered_set_status')=='not_checked_aggregate_pending' and evidence.get('asset_count')==44,'pre-release artwork scope overstated')
   require(issha(ARTWORK_DIAGNOSTIC_SHA256) and evidence.get('private_diagnostic_sha256')==ARTWORK_DIAGNOSTIC_SHA256 and issha(ARTWORK_VERIFIER_COMMITMENT) and evidence.get('verifier_commitment')==ARTWORK_VERIFIER_COMMITMENT,'independent artwork verifier evidence pending or changed')
   require(stamp(evidence['completed_at'])<=stamp(item['completed_at']),'artwork proof postdates check')
  if name=='validator_code_review':
   require(len(item['evidence'])==1,'exact code review proof required')
   review=json.loads(bound(root,item['evidence'][0]));require(review.get('schema')=='emma-public-validator-review-v1' and review.get('status')=='PASS' and review.get('subject_sha256')==SUBJECT_SHA256,'code review subject mismatch')
   require(issha(CODE_REVIEW_RECEIPT_SHA256) and review.get('private_receipt_sha256')==CODE_REVIEW_RECEIPT_SHA256 and issha(CODE_REVIEWER_COMMITMENT) and review.get('verifier_commitment')==CODE_REVIEWER_COMMITMENT,'code reviewer evidence pending or changed')
   validator=projection['historical_validator_sha256'] if projection else normalized_validator_hash(root)
   tree=projection['historical_tool_tree_sha256'] if projection else reviewed_tool_tree_hash(root)
   require(review.get('normalized_validator_sha256')==validator,'reviewed validator logic changed')
   require(review.get('reviewed_tool_tree_sha256')==tree,'reviewed tool tree or workflow changed')
   require(stamp(review['completed_at'])<=stamp(item['completed_at']),'code review postdates check')
 return {'status':'validated public commitments, private attestation and conditional checks; not live verification'}
