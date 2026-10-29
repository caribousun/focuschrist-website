"""Exact current Timeline content-ledger successor; historical projection only.

Current source review and the actual content audit remain separate requirements.
The old ledger and its review claims are preserved, not reissued.
"""
import copy,hashlib,json
from pathlib import Path
from timeline_search_index_successor import source
ROOT=Path(__file__).resolve().parents[1]
BEFORE='3e56b5a2eb5f86e4cc0ea19c69efdbe8861873e02d36b88ab203f99bab1a6b6d'
AFTER='1ba70ebc7b9bb6117d91773934fe5fa4241148144aebf537beb20a9209edfbe9'
REVIEW='docs/timeline-controls-successor/current-content-review.json'
REVIEW_SHA256='ee25fb9c83e81ec24580493de7a29d8f9ce94022c1b6cfc92bdebbc99acd4875'
ROUTES={'answers/jesus-christ-latter-day-saint-beliefs.html','timelines/world-and-scripture-timeline.html','timelines/adams-1881-chart.html'}
ADAMS='timelines/adams-1881-chart.html'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def restore(raw,root=ROOT):
 assert sha(raw)==AFTER,'Unreviewed current content ledger'
 review_raw=source(root,REVIEW);assert sha(review_raw)==REVIEW_SHA256,'Changed current content review'
 review=json.loads(review_raw);assert review['schema']=='timeline-current-content-review-v1' and review['verdict']=='CONCUR_WITHIN_BOUNDED_SCOPE' and review['scope']=='source_and_destination_context_only'
 assert review['private_receipt_sha256']=='b7b2786f649f3e20c186e3cd03b11228d01b2375947223e8062202b86b42e5c7'
 data=json.loads(raw);rows=data['documents'];assert len({r['path'] for r in rows})==len(rows)
 seen=set()
 for n,row in enumerate(rows):
  name=row['path']
  if name not in ROUTES:continue
  seen.add(name);binding=row['current_timeline_review'];assert binding['scope']=='source_and_destination_context_only'
  assert binding['reviewed_source_sha256']==review['source_sha256'][name] and binding['visible_text_sha256']==review['visible_text_sha256'][name] and binding['reviewed_at']==review['reviewed_at']
  assert binding['evidence']=={'path':REVIEW,'sha256':REVIEW_SHA256,'bytes':len(review_raw)}
  raw_source=source(root,name)
  if name=='timelines/world-and-scripture-timeline.html':
   from timeline_world_mobile_successor import AFTER as MOBILE_AFTER, restore as restore_mobile
   if sha(raw_source)==MOBILE_AFTER:raw_source=restore_mobile(raw_source,root)
  assert sha(raw_source)==review['source_sha256'][name],'Current content source changed'
  if name==ADAMS:
   assert row['reviewed_source_sha256']==review['source_sha256'][name] and row['published_text_sha256']==review['visible_text_sha256'][name]
   previous=row['prior_timeline_diagnostic_review'];assert isinstance(previous,dict) and previous['path']==name
   rows[n]=copy.deepcopy(previous)
  else:
   assert row['reviewed_current_timeline_sha256']==review['source_sha256'][name]
   previous=dict(row);del previous['current_timeline_review'];del previous['reviewed_current_timeline_sha256'];rows[n]=previous
 assert seen==ROUTES,'Current content review coverage missing'
 result=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(result)==BEFORE,'Historical content ledger not exactly reconstructed'
 return result
