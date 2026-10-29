"""Current event-index successor with fail-closed review evidence.

Historical projections do not review current work. This structural gate cannot
identify or authenticate people: exact pinned public commitments must be
independently checked against the genuine, privately retained receipts before
pins are populated. A synthetic test record is never release evidence.
"""
import hashlib,json,re
from pathlib import Path
import timeline_51_search_successor as event_search
import timeline_search_index_successor as prior_search

# These pins intentionally remain unset until the named actual evidence exists
# and an independent verifier has checked each public projection against it.
CONTENT_REVIEW_SHA256='7a08e8798c222fce04665b7e51b334783b61c7c67cb230cf444a5713b8397ec1'
CONTENT_VERIFIER_COMMITMENT='25275b95cc2c78a6aef8f6ac29e2400b0fac0290ab5ec12f9946448301ee8133'
CONTENT_VERIFICATION_RECEIPT_SHA256='a06a04a3f602b9ce40f1c8e69b4bd5d0fd29d8395fa77961465fdd5ee31df913'
INDEX_REVIEW_SHA256='677b4f5abb87b4bfe1b98c5049b479cd0b91e33a71b28be0891125c205e94b63'
INDEX_REVIEWER_COMMITMENT='fb7d32270b9d7d33bed53b1af38ec4db679c132e997454e47b0b34a9863b2e12'
INDEX_RECEIPT_SHA256='041db07ca772c32f9e904913031a9b2ef25c7d53692a7e86538e8ce4f8327446'
CODE_REVIEW_SHA256='b956a91994fa3c301d9262e4d0e2a60e4f3bd65acbd50dbf02666a62f4828ee4'
CODE_REVIEWER_COMMITMENT='25275b95cc2c78a6aef8f6ac29e2400b0fac0290ab5ec12f9946448301ee8133'
CODE_RECEIPT_SHA256='73f827dfdf773285078be9809ee47e4024e3091ec65ee4ca5794e65a2ddf8cf2'
TREE_MANIFEST_SHA256='a421662305d8123685088b6b1b47d2d324af280199f4f204628107ec3b464abd'
PIN_NAMES=('CONTENT_REVIEW_SHA256','CONTENT_VERIFIER_COMMITMENT','CONTENT_VERIFICATION_RECEIPT_SHA256','INDEX_REVIEW_SHA256','INDEX_REVIEWER_COMMITMENT','INDEX_RECEIPT_SHA256','CODE_REVIEW_SHA256','CODE_REVIEWER_COMMITMENT','CODE_RECEIPT_SHA256','TREE_MANIFEST_SHA256')
CONTENT_REVIEW='docs/timeline-51-current/content-review.json'
INDEX_REVIEW='docs/timeline-51-current/index-review.json'
CODE_REVIEW='docs/timeline-51-current/code-review.json'
TREE_MANIFEST='docs/timeline-51-current/historical-tool-tree.json'
PRIOR_LEDGER='1ba70ebc7b9bb6117d91773934fe5fa4241148144aebf537beb20a9209edfbe9'
PRIOR_TREE='929671f585832ec0e544b52ae620b88dbd4f05545a5eedca6077bf898c7cc097'
SOURCE_HEAD='79e8d90a490ac97f8d6cf7fc90b5271f58c2db4a'
SOURCE_RECEIPTS={'fermi':'ad27c554ce249e9a727dabe22347136f3c9119f68e9cb547cff3d7fd44f9f6b1','newton':'cb99d44e6727519765d048914eead52e6610062ebbf8d23856fa6078945a1f34','albert_prior':'95845eff27c74e014fa7b9b04271b76d2b3bdfec8d993bfc0414583a64851d2a','albert_delta':'dc6cd2550a673756d0988f696e2bc73173371f271dc5d74d61ef039ad6540f21'}
CONTENT_ROLE_SCOPES={'fermi':'fifty_prior_sections_plus_independence_rock_and_audit_delta','newton':'forty_nine_prior_sections_plus_independence_rock_and_audit_delta','albert':'prior_fifty_sections_and_bounded_editorial_delta'}
CONTENT_ACTORS={'fermi':'8276c460675434ee0641f18e14c9c558a28112c85692b94c8ed299c898f886a8','newton':'0313af4b58e8e5165df0b4195356279bde1b81994fd8b237fdec02497f63d2c3','albert':'94a6b447580330f9f2b609422537b04239ff3a39df9137e32efd559f1a2935cb'}
SOURCE_FILES=frozenset({'timeline-images.js','timelines/latter-day-saint-church-history-timeline.html','timelines/life-of-christ-journey-map.html','timelines/willie-and-martin-handcart-map.html','docs/reviews/timeline-51-destination-bindings.json','docs/reviews/timeline-51-source-evidence.json','docs/reviews/timeline-51-event-destinations-20261029.csv','jesus-christ/mortal-ministry.html','jesus-christ/restoration-and-today.html','pioneers.html','church-history.html'})
CONTENT_PAGES=frozenset({'church-history.html','pioneers.html','jesus-christ/mortal-ministry.html','jesus-christ/restoration-and-today.html','timelines/life-of-christ-journey-map.html','timelines/willie-and-martin-handcart-map.html','timelines/latter-day-saint-church-history-timeline.html'})
PANEL='aaa49fb307fa5e3251e7ed054d2443f637db94a0361a4ba3621d267ed1ab5532'
GALLERY='df6a8c33fc3bd70dbf38675fdb21b984914e5598a42f70025e67de5ddfceb4f8'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validhash(value):return isinstance(value,str) and re.fullmatch(r'[0-9a-f]{64}',value) is not None
def require(ok,message):
 if not ok:raise ValueError(message)
def pinned(root,path,pin):
 require(validhash(pin),'PENDING independently verified Timeline event review: '+path)
 raw=prior_search.source(root,path);require(sha(raw)==pin,'Changed Timeline event review evidence: '+path)
 value=json.loads(raw);require(isinstance(value,dict),'Invalid Timeline event review evidence: '+path)
 return value

def validate_content(root):
 review=pinned(root,CONTENT_REVIEW,CONTENT_REVIEW_SHA256)
 require(review.get('schema')=='timeline-51-content-review-v1' and review.get('scope')=='bounded_current_source_content' and review.get('verdict')=='CONCUR','Wrong current content review scope')
 require(review.get('source_head')==SOURCE_HEAD and review.get('source_receipts')==SOURCE_RECEIPTS,'Current content receipt commitments differ')
 require(review.get('reviewer_commitments')==CONTENT_ACTORS and len(set(CONTENT_ACTORS.values()))==3,'Current content reviewer association differs')
 require(review.get('role_scopes')==CONTENT_ROLE_SCOPES,'Current content reviewer scope differs')
 require(validhash(CONTENT_VERIFIER_COMMITMENT) and validhash(CONTENT_VERIFICATION_RECEIPT_SHA256),'PENDING content receipt verification')
 require(CONTENT_VERIFIER_COMMITMENT not in CONTENT_ACTORS.values(),'Content receipt verifier must be independent of all content reviewers')
 require(review.get('verifier_commitment')==CONTENT_VERIFIER_COMMITMENT and review.get('verification_receipt_sha256')==CONTENT_VERIFICATION_RECEIPT_SHA256,'Current content receipt verification differs')
 paths=review.get('reviewed_file_sha256');require(isinstance(paths,dict) and set(paths)==SOURCE_FILES,'Current content source scope differs')
 for name in SOURCE_FILES:require(validhash(paths[name]) and sha(prior_search.source(root,name))==paths[name],'Current reviewed content changed: '+name)
 require(review.get('limits')=={'needles':'unresolved','pacific_springs':'context_only','primary_exhaustive':False,'rights':False,'visual':False,'runtime':False,'whole_site':False,'code':False,'index':False,'owner':False,'release':False},'Current content review limits missing')
 return review

def project_ledger(root,review):
 import static_content_audit as audit
 raw=prior_search.source(root,'content-audit.json');data=json.loads(raw);rows=data.get('documents');require(isinstance(rows,list),'Current content ledger invalid')
 require(len({r.get('path') for r in rows})==len(rows),'Duplicate current content rows');seen=set();output=[]
 for row in rows:
  name=row.get('path')
  if name not in CONTENT_PAGES:output.append(row);continue
  seen.add(name);path=Path(root)/name;require(row.get('reviewed_timeline_51_source_sha256')==review['reviewed_file_sha256'][name],'Current ledger source binding missing: '+name)
  require(row.get('published_text_sha256')==audit.content_hash(path),'Current ledger text binding missing: '+name)
  if name in audit.INLINE_SCRIPT_ROUTES:require(row.get('reviewed_inline_script_sha256')==audit.inline_script_hash(path),'Current timeline script review missing: '+name)
  require(row.get('timeline_51_content_review')=={'path':CONTENT_REVIEW,'sha256':CONTENT_REVIEW_SHA256},'Current ledger review binding missing: '+name)
  previous=row.get('prior_timeline_51_content_review');require(isinstance(previous,dict) and previous.get('path')==name,'Prior content ledger record missing: '+name)
  additions={'prior_timeline_51_content_review','timeline_51_content_review','reviewed_timeline_51_source_sha256'}
  require(set(row)<=set(previous)|additions,'Unexpected current content ledger field: '+name)
  mutable={'published_text_sha256','reviewed_inline_script_sha256','authoritative_sources'}
  require(all(row.get(key)==value for key,value in previous.items() if key not in mutable),'Historical content metadata changed: '+name)
  prior_sources=previous.get('authoritative_sources',[]);current_sources=row.get('authoritative_sources',[])
  require(isinstance(prior_sources,list) and isinstance(current_sources,list) and set(prior_sources)<=set(current_sources),'Historical content sources removed: '+name)
  output.append(previous)
 require(seen==CONTENT_PAGES,'Current content ledger coverage missing')
 reconstructed=(json.dumps(dict(data,documents=output),ensure_ascii=False,indent=2)+'\n').encode();require(sha(reconstructed)==PRIOR_LEDGER,'Historical content ledger mismatch')
 require(audit.ROOT.resolve()==Path(root).resolve() and audit.validate()==0,'Current content audit failed')
 return reconstructed

def validate_index(root):
 # Always execute the real full-tree producer before accepting review metadata.
 result=event_search.validate_current(root);raw=prior_search.source(root,'site-search-index.json');previous=event_search.restore(raw,root)
 before=json.loads(previous);after=json.loads(raw);a={r['url']:r for r in before['records']};b={r['url']:r for r in after['records']}
 changed=sorted(u for u in a.keys()|b.keys() if a.get(u)!=b.get(u));emma=lambda rows:{u:r for u,r in rows.items() if u.startswith('/history/emma-')}
 require(len(changed)==56 and emma(a)==emma(b) and len(emma(a))==71,'Current index delta or Emma records differ')
 review=pinned(root,INDEX_REVIEW,INDEX_REVIEW_SHA256)
 require(review.get('schema')=='timeline-51-index-review-v1' and review.get('scope')=='actual_current_index_delta' and review.get('verdict')=='CONCUR','Wrong current index review scope')
 require(validhash(INDEX_REVIEWER_COMMITMENT) and validhash(INDEX_RECEIPT_SHA256),'PENDING independent current index review')
 require(review.get('reviewer_commitment')==INDEX_REVIEWER_COMMITMENT and review.get('receipt_sha256')==INDEX_RECEIPT_SHA256,'Current index reviewer evidence differs')
 require(review.get('prior_search_sha256')==event_search.BEFORE and review.get('current_search_sha256')==event_search.AFTER and review.get('search_manifest_sha256')==event_search.MANIFEST_SHA,'Current reviewed index bytes differ')
 require(review.get('source_sha256')==event_search.manifest(root)['source_sha256'] and review.get('changed_urls')==changed and review.get('emma_unchanged_records')==71,'Current reviewed index scope differs')
 require(review.get('panel_sha256')==PANEL==sha(prior_search.source(root,'docs/section-panel-inventory.json')) and review.get('gallery_sha256')==GALLERY==sha(prior_search.source(root,'art-gallery.json')),'Current reviewed panel or gallery differs')
 return previous,review,result

def project_tree(root,current):
 import timeline_current_index_closure as old
 manifest=pinned(root,TREE_MANIFEST,TREE_MANIFEST_SHA256);require(manifest.get('schema')==1 and manifest.get('prior_tree_sha256')==PRIOR_TREE and isinstance(manifest.get('previous'),dict),'Invalid Timeline event tree projection')
 prior=dict(current)
 for name,old_hash in manifest['previous'].items():
  require(name in prior,'Tree projection path missing: '+name)
  if old_hash is None:del prior[name]
  else:require(validhash(old_hash),'Invalid tree predecessor hash');prior[name]=old_hash
 require(old.canonical(prior)==PRIOR_TREE,'Historical Timeline tool tree mismatch')
 return prior

def prepare(root):
 """Validate current producer and genuine reviews, then project old evidence."""
 import timeline_current_index_closure as old
 root=Path(root).resolve();previous_search,index_review,_=validate_index(root);content=validate_content(root);previous_ledger=project_ledger(root,content)
 code=pinned(root,CODE_REVIEW,CODE_REVIEW_SHA256)
 require(code.get('schema')=='timeline-51-code-review-v1' and code.get('scope')=='current_event_successor_and_tool_tree' and code.get('verdict')=='CONCUR','Wrong current code review scope')
 require(validhash(CODE_REVIEWER_COMMITMENT) and validhash(CODE_RECEIPT_SHA256),'PENDING independent current code review')
 require(code.get('reviewer_commitment')==CODE_REVIEWER_COMMITMENT and code.get('receipt_sha256')==CODE_RECEIPT_SHA256 and CODE_REVIEWER_COMMITMENT!=INDEX_REVIEWER_COMMITMENT,'Independent code reviewer evidence differs')
 require(code.get('content_review_sha256')==CONTENT_REVIEW_SHA256 and code.get('index_review_sha256')==INDEX_REVIEW_SHA256 and code.get('content_ledger_sha256')==sha(prior_search.source(root,'content-audit.json')) and code.get('tree_manifest_sha256')==TREE_MANIFEST_SHA256,'Current code review inputs differ')
 require(old.timestamp(code.get('reviewed_at'))>=old.timestamp(index_review.get('reviewed_at')),'Code review predates index review')
 current=old.tool_tree(root);require(code.get('tool_tree_sha256')==old.canonical(current),'Current reviewed tool tree differs')
 prior=project_tree(root,current)
 return {'previous_search':previous_search,'previous_ledger':previous_ledger,'previous_tool_tree':prior}
