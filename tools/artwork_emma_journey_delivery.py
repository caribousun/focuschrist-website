"""DRAFT exact new Emma journey delivery. Never a substitute for actual reviews.

The record pin is intentionally unset until actual source/preflight/finished,
assembled page, and owner evidence has been independently reviewed. Synthetic
fixtures may exercise this code, but cannot fill the real pin.
"""
from pathlib import Path
from datetime import datetime
from PIL import Image, __version__ as PIL_VERSION, features
import hashlib,json
from io import BytesIO
from artwork_emma_story_delivery import local,bound,canonical,require,stamp,CHECKS

MANIFEST='docs/emma-journey-artwork/delivery.json'
APPROVED_RECORD_SHA256=None
SCENES=tuple(f'{i:02}' for i in range(3,13))+('origin',)
ID_MASTER='7d0a07cc673d244ccd54d478c53d1e68d248e39d9b1101f87dfe3681cbb839d1'
EXPRESSION='f6d2493babf5d2ab7a6e118a57827f7db05e6aea934feb5739256987ec186688'
ROUTE='history/emma-hale-smith.html'
MANDATES={'AGENTS.md','docs/historical-character-identity.md','docs/focuschrist-enrichment-and-stewardship-prompt.md'}
CHRONOLOGY={
 '03':('exact','1827-01-18','1827-01-18',(22,22)),
 '04':('period','1828-06-15','1828-06-30',(23,23)),
 '05':('exact','1830-06-28','1830-06-28',(25,25)),
 '06':('period','1831-05-01','1831-05-31',(26,26)),
 '07':('period','1842-03-17','1843-12-31',(37,39)),
 '08':('exact','1844-07-17','1844-07-17',(40,40)),
 '09':('period','1844-09-01','1844-10-31',(40,40)),
 '10':('period','1846-09-01','1846-09-30',(42,42)),
 '11':('period','1860-04-01','1860-04-30',(55,55)),
 '12':('period','1879-01-01','1879-04-30',(74,74)),
 'origin':('exact','1804-07-10','1804-07-10',None),
}


def asset_paths():
 out=set()
 for s in SCENES:
  base='assets/page-art/emma-journey/emma-journey-'+s
  out.add('assets/page-art/emma-journey/originals/emma-journey-'+s+'-source.png')
  out.update(base+'-'+str(w)+'.webp' for w in (640,960,1536))
 return out
ASSETS=frozenset(asset_paths())

def receipt(root,pointer,expected_reviewer,stage,binding,rejected,face,mandates):
 raw=bound(root,pointer);r=json.loads(raw)
 require(r.get('reviewer')==expected_reviewer and r.get('stage')==stage and r.get('verdict')=='PASS' and r.get('withdrawn') is False,'wrong, negative, withdrawn or duplicate reviewer')
 require(r.get('binding_sha256')==binding,'stale review binding')
 require(r.get('mandate_bindings')==mandates,'reviewer has not bound exact current mandate readback')
 require(isinstance(r.get('receipt_id'),str) and r['receipt_id'].strip(),'missing receipt id')
 if stage=='preflight':require(r.get('reviewed_before_generation') is True,'preflight sequence not attested')
 require(isinstance(r.get('actual_actor'),str) and r['actual_actor'].strip() and isinstance(r.get('observations'),str) and r['observations'].strip(),'missing actual reviewer/observations')
 stamp(r['reviewed_at'])
 require(isinstance(r.get('evidence'),list) and r['evidence'],'review evidence absent')
 for entry in r['evidence']:
  raw=bound(root,entry);require(hashlib.sha256(raw).hexdigest() not in rejected,'rejected review evidence')
 if stage=='finished':
  require(r.get('full_resolution_inspected') is True and (not face or r.get('face_details_inspected') is True),'finished pixels not fully inspected')
  require(set(r.get('checks',{}))==CHECKS and all(isinstance(x,str) and x.strip() for x in r['checks'].values()),'missing finished observations')
 return r

def validate(root,record,added,covered,rejected,pixel_hash,page_dependencies):
 require(APPROVED_RECORD_SHA256 is not None,'Emma journey exact record pending independent and owner review')
 require(canonical(record)==APPROVED_RECORD_SHA256,'Emma journey unreviewed record')
 require(record.get('schema')==1 and record.get('status')=='REVIEWED_EXACT_EMMA_JOURNEY','wrong delivery record')
 require(ASSETS<=added and not ASSETS&covered,'exact 44 new assets must be available and disjoint before review')
 spec=record['spec'];require(spec.get('route')==ROUTE,'wrong journey owner')
 source=spec['page_source'];require(source['path']==ROUTE,'wrong page source');bound(root,source)
 page_context=spec['page_context'];names={x['path'] for x in page_context};require(len(names)==len(page_context) and page_dependencies(root,ROUTE)<=names,'incomplete page context')
 for e in page_context:bound(root,e)
 rows=spec['scenes'];ids=[x['id'] for x in rows];require(len(ids)==len(set(ids))==11 and set(ids)==set(SCENES),'wrong or duplicate scene set')
 all_assets=set();hashes=set();pixels=set();original_hashes=set();original_pixels=set();receipt_ids=set();reviewer_actors={};common_mandates=None
 for row in rows:
  id=row['id'];origin=id=='origin';pre=row['preflight']
  require(row.get('kind')==('PERSON_FREE_CONTEXT' if origin else 'EMMA_CHARACTER'),'incorrect person-free/character classification')
  require(pre.get('scene_id')==id and pre.get('route')==ROUTE and pre.get('source_urls') and all(u.startswith('https://') for u in pre['source_urls']),'wrong scene or missing sources')
  prompt=bound(root,pre['prompt']);require(hashlib.sha256(prompt).hexdigest() not in rejected,'rejected prompt')
  refs=pre.get('references');require(isinstance(refs,list),'missing references')
  for ref in refs:bound(root,ref)
  require(([r['sha256'] for r in refs]==[] if origin else [r['sha256'] for r in refs]==[ID_MASTER,EXPRESSION]),'wrong approved reference inputs')
  require(pre.get('characters')==([] if origin else ['Emma Hale Smith']),'wrong named character set')
  require(all(isinstance(pre.get(k),str) and pre[k].strip() for k in ('setting','period_clothing','scene_action')),'missing scene history/wardrobe/action')
  chronology=pre.get('chronology') or {};expected=CHRONOLOGY[id]
  require((chronology.get('kind'),chronology.get('start'),chronology.get('end'),tuple(chronology['age_range']) if chronology.get('age_range') is not None else None)==expected and chronology.get('basis'),'unreviewed scene-specific date/age classification')
  mandates=pre.get('mandates');require(isinstance(mandates,list) and len(mandates)==len(MANDATES) and {m.get('path') for m in mandates}==MANDATES,'exact current mandate set required')
  mandate_map={m['path']:m['sha256'] for m in mandates}
  if common_mandates is None:common_mandates=mandate_map
  else:require(mandate_map==common_mandates,'inconsistent mandate versions across scenes')
  for m in mandates:bound(root,m)
  if pre.get('edit_target'):
   require(not origin,'person-free origin was not edited');target=bound(root,pre['edit_target']);require(hashlib.sha256(target).hexdigest() not in rejected,'rejected edit target')
  prebind=canonical(pre);reviews=row['reviews']
  require(set(reviews)=={'fermi_preflight','newton_preflight','fermi_finished','newton_finished'},'exact separate review set required')
  pre_receipts=[receipt(root,reviews[name],who,'preflight',prebind,rejected,False,mandate_map) for name,who in [('fermi_preflight','Fermi'),('newton_preflight','Newton')]]
  scene_binding=canonical({k:v for k,v in row.items() if k!='reviews'})
  finished_receipts=[receipt(root,reviews[name],who,'finished',scene_binding,rejected,not origin,mandate_map) for name,who in [('fermi_finished','Fermi'),('newton_finished','Newton')]]
  for r in pre_receipts+finished_receipts:
   require(r['receipt_id'] not in receipt_ids,'receipt reused across scenes or stages');receipt_ids.add(r['receipt_id'])
   who=r['reviewer'];actor=r['actual_actor'];require(who not in reviewer_actors or reviewer_actors[who]==actor,'reviewer actor changed');reviewer_actors[who]=actor
  require(reviewer_actors['Fermi']!=reviewer_actors['Newton'],'reviewers are not distinct')
  generation=json.loads(bound(root,row['generation_lineage']))
  require(generation.get('actor')=='Albert' and generation.get('scene_id')==id and generation.get('prompt_sha256')==pre['prompt']['sha256'] and generation.get('output_sha256')==row['original']['sha256'],'generation provenance mismatch')
  require(generation.get('reference_sha256')==[x['sha256'] for x in refs] and generation.get('edit_target_sha256')==(pre['edit_target']['sha256'] if pre.get('edit_target') else None),'generation input order/target mismatch')
  require(generation.get('provider_model') and generation.get('provider_job_id') and generation.get('call_timestamp_status') in ('UNKNOWN_NOT_INFERRED','DOCUMENTED'),'unclassified generation metadata')
  require(generation.get('no_unlisted_inputs') is True and generation.get('evidence'),'generation operator evidence absent')
  for x in generation['evidence']:bound(root,x)
  ordering=json.loads(bound(root,generation['preflight_sequence_evidence']))
  require(ordering.get('actor')=='Albert' and ordering.get('scene_id')==id and ordering.get('prompt_sha256')==pre['prompt']['sha256'] and ordering.get('output_sha256')==row['original']['sha256'] and ordering.get('preflight_receipt_ids')==[r['receipt_id'] for r in pre_receipts] and ordering.get('both_preflights_preceded_generation') is True and ordering.get('evidence'),'actual preflight sequencing attestation missing')
  for x in ordering['evidence']:bound(root,x)
  if generation['call_timestamp_status']=='UNKNOWN_NOT_INFERRED':
   require(generation.get('call_timestamp') is None and generation.get('unknown_timestamp_basis'),'invented generation time')
  else:
   when=stamp(generation['call_timestamp'])
   require(all(stamp(r['reviewed_at'])<when for r in pre_receipts) and all(stamp(r['reviewed_at'])>=when for r in finished_receipts),'review timing inconsistent')
  base='assets/page-art/emma-journey/emma-journey-'+id
  orig=row['original'];need_orig='assets/page-art/emma-journey/originals/emma-journey-'+id+'-source.png';require(orig['path']==need_orig,'wrong original path')
  deriv=row['derivatives'];require(len(deriv)==3 and {d['path'] for d in deriv}=={base+'-'+str(w)+'.webp' for w in (640,960,1536)},'wrong exact derivative family')
  lineage=row['derivative_lineage'];require(lineage.get('pillow_version')==PIL_VERSION and lineage.get('libwebp_version')==features.version('webp') and lineage.get('resampling')=='LANCZOS' and lineage.get('quality')==92 and lineage.get('method')==6,'unmatched derivative encoder configuration')
  for a in [orig,*deriv]:
   raw=bound(root,a);require(hashlib.sha256(raw).hexdigest() not in rejected,'rejected asset')
   require(a['path'] not in all_assets and a['sha256'] not in hashes and a['pixel_sha256'] not in pixels,'duplicate family asset or pixels')
   actual=pixel_hash(local(root,a['path']));require(actual==a['pixel_sha256'],'decoded pixel drift')
   with Image.open(local(root,a['path'])) as im:
    require(getattr(im,'n_frames',1)==1 and list(im.size)==a['dimensions'],'asset dimensions/animation drift')
    if a is not orig:require(im.height==round(orig['dimensions'][1]*im.width/orig['dimensions'][0]),'nonproportional derivative')
   all_assets.add(a['path']);hashes.add(a['sha256']);pixels.add(a['pixel_sha256'])
  require(orig['dimensions']==[1536,1024] and {d['dimensions'][0] for d in deriv}=={640,960,1536},'source or derivative dimensions')
  with Image.open(local(root,orig['path'])) as im:
   for d in deriv:
    width=d['dimensions'][0];resize=im if width==1536 else im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
    output=BytesIO();resize.save(output,format='WEBP',quality=92,method=6)
    require(output.getvalue()==local(root,d['path']).read_bytes(),'derivative does not deterministically reproduce from source')
  require(row['derivative_lineage']['source_sha256']==orig['sha256'] and row['derivative_lineage']['method'] and row['derivative_lineage']['evidence'],'missing derivative lineage')
  for x in row['derivative_lineage']['evidence']:bound(root,x)
  original_hashes.add(orig['sha256']);original_pixels.add(orig['pixel_sha256'])
 require(all_assets==ASSETS and all_assets<=added and not all_assets&covered,'exact 44 new assets required without overlap')
 binding=canonical(spec);reviewers=set()
 for pointer in record['assembled_reviews']:
  obj=json.loads(bound(root,pointer));who=obj.get('reviewer');require(who in {'Fermi','Newton','Albert'} and who not in reviewers,'duplicate or unknown assembled reviewer')
  require(obj.get('mandate_bindings')==mandate_map,'assembled reviewer mandate readback mismatch')
  require(obj.get('stage')=='assembled' and obj.get('verdict')=='PASS' and obj.get('withdrawn') is False and obj.get('binding_sha256')==binding,'stale assembled review')
  require(obj.get('actual_actor') and obj.get('observations') and obj.get('evidence') and obj.get('full_context_inspected') is True,'missing assembled review evidence');stamp(obj['reviewed_at'])
  if who in reviewer_actors:require(obj['actual_actor']==reviewer_actors[who],'assembled reviewer actor mismatch')
  else:require(obj['actual_actor'] not in reviewer_actors.values(),'root reviewer is not distinct');reviewer_actors[who]=obj['actual_actor']
  require(set(obj.get('checks',{}))==CHECKS and all(isinstance(x,str) and x.strip() for x in obj['checks'].values()),'assembled review observations incomplete')
  for x in obj['evidence']:bound(root,x)
  if who=='Albert':
   require(set(obj.get('rendered',{}))=={'desktop','phone'},'root desktop/phone evidence required')
   for x in obj['rendered'].values():bound(root,x)
  reviewers.add(who)
 require(reviewers=={'Fermi','Newton','Albert'},'all three assembled reviewers required')
 acceptance=json.loads(bound(root,record['owner_acceptance']))
 require(acceptance.get('kind')=='direct_owner_acceptance' and acceptance.get('actor')=='Wyatt' and acceptance.get('verdict')=='ACCEPT' and acceptance.get('subject_sha256')==binding and acceptance.get('evidence'),'owner acceptance missing or stale')
 for x in acceptance['evidence']:bound(root,x)
 return all_assets,hashes,pixels
