"""UNREVIEWED LOCAL DRAFT: exact current Emma owner successor.

This is a source/structure and explicit historical-fixture adapter. It does not
verify human authorship, rendered pixels, approval, or publication. The old
owner_integration_contract and its pinned manifest remain untouched. Integrate
only after independent review and real approval receipts exist.
"""
import hashlib,json,re,zlib,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from owner_integration_contract import Document, standard_chrome, one

MANIFEST_SHA256='3ae50af644843d26abc5e794262657336b60c7a4f204cab8ed1064f0159ae0d4'
HUB='history/emma-hale-smith.html'; RETIRED='history/emma-elect-lady.html'; HYMNS='history/emma-hymns.html'
MANIFEST_PATH=Path(__file__).with_name('owner-successor-manifest.json')
FIXTURES=Path(__file__).with_name('predecessors')
# No owner, final-page, or lineage review is fabricated: these gates are held.
OWNER_ACCEPTANCE_SHA256=None
FINAL_SOURCE_REVIEW_SHA256=None
CANONICAL_CURRENT='a1ab61c01083851deb33315bad3aacac48c9d2c85bb99323ec984dd2319e0551'
CANONICAL_PRIOR='ba19da4af6ba32219ff9555ecf5ddd466077acd9a6ee09a7d49f29c07d1f4284'
OLD={'emma-story1-ride','emma-story2-hymnal','emma-story3-quincy','emma-story4-hospitality','emma-story5-testimony','emma-h1','emma-h3','emma-h4','emma-h5'}
NEW={'emma-journey-'+f'{n:02}' for n in range(3,13)}
ORIGIN='emma-journey-origin'
SECTIONS={'03':'emma-beginnings','04':'emma-pen-family','05':'emma-pen-family','06':'emma-pen-family','07':'emma-relief-questions','08':'emma-household','09':'emma-household','10':'emma-household','11':'emma-household','12':'emma-remaining-years'}

def need(condition,msg):
 if not condition:raise AssertionError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_manifest():
 raw=MANIFEST_PATH.read_bytes();need(sha(raw)==MANIFEST_SHA256,'owner successor manifest is unreviewed or changed')
 d=json.loads(raw);need(d['schema']==1 and set(d['files'])=={HUB,RETIRED,HYMNS,'sitemap.xml'},'owner successor file shape')
 need(len(d['assets'])==33 and len(d['original_assets'])==11,'expected 33 derivatives and 11 source originals')
 return d

def safe(root,name):
 need(isinstance(name,str) and name and not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name and ':' not in name,'unsafe path')
 root=Path(root).resolve();parts=Path(name).parts
 for i in range(1,len(parts)+1):need(not root.joinpath(*parts[:i]).is_symlink(),'symlink in path: '+name)
 p=(root/name).resolve();need(p.is_relative_to(root) and p.is_file(),'missing/unsafe path: '+name);return p

def current_file(route,raw):
 d=read_manifest();need(route in d['files'],'unknown successor source')
 row=d['files'][route];need(len(raw)==row['current_bytes'] and sha(raw)==row['current_sha256'],'unreviewed current source: '+route)
 return row

def figure_bytes(raw,key):
 m=re.search(rb'<figure\b[^>]*\bdata-exclusive-artwork="'+re.escape(key.encode())+rb'"[^>]*>.*?</figure>',raw,re.S)
 need(m is not None,'missing preserved figure '+key);return m.group()

def predecessor_fixture(route):
 row=read_manifest()['files'][route];packed=safe(FIXTURES,route+'.zlib').read_bytes();need(len(packed)<1024*1024,'oversize predecessor fixture')
 decoder=zlib.decompressobj();raw=decoder.decompress(packed,row['before_bytes']+1)
 need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,'malformed/oversize predecessor compression')
 need(len(raw)==row['before_bytes'] and sha(raw)==row['before_sha256'],'changed predecessor fixture '+route);return raw

def validate_assets(root):
 d=read_manifest();expected=set()
 for key in NEW|{ORIGIN}:
  for width in (640,960,1536):expected.add('assets/page-art/emma-journey/'+key+'-'+str(width)+'.webp')
 need(set(d['assets'])==expected,'new asset names differ from exact owner set')
 originals={'assets/page-art/emma-journey/originals/'+key+'-source.png' for key in NEW|{ORIGIN}}
 need(set(d['original_assets'])==originals,'original source names differ from exact owner set')
 folder=Path(root)/'assets/page-art/emma-journey';need(folder.is_dir() and not folder.is_symlink(),'missing/unsafe artwork namespace')
 observed=set()
 for item in folder.rglob('*'):
  need(not item.is_symlink(),'symlink inside artwork namespace')
  if item.is_file():observed.add(item.relative_to(Path(root)).as_posix())
  elif item.is_dir():need(item.relative_to(folder).as_posix()=='originals','unknown directory in artwork namespace')
  else:need(False,'unknown filesystem entry')
 need(observed==expected or observed==expected|originals,'unknown, missing or incomplete artwork namespace')
 for name,row in {**d['assets'],**({} if observed==expected else d['original_assets'])}.items():
  raw=safe(root,name).read_bytes();need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'new asset changed: '+name)
 return len(expected)

def validate_hub(raw,root):
 current_file(HUB,raw);before=predecessor_fixture(HUB);text=raw.decode('utf-8');nodes=list(Document(text).root.walk())
 ids=[n.attrs['id'] for n in nodes if 'id' in n.attrs];need(len(ids)==len(set(ids)),'duplicate ID')
 previous_nodes=list(Document(before.decode('utf-8')).root.walk());oldids={n.attrs['id'] for n in previous_nodes if 'id' in n.attrs}
 need(oldids<=set(ids),'missing existing anchor');standard_chrome(nodes)
 for pattern,label in [(rb'(<figure class="fc-life-hero".*?</figure>)','hero'),(rb'(<nav aria-label="Primary navigation".*?</nav>)','header'),(rb'(<footer class="fc-footer".*?</footer>)','footer'),(rb'(<div class="fc-life-reading fc-life-opening">.*?</details></div>)','opening')]:
  a=re.findall(pattern,before,re.S);b=re.findall(pattern,raw,re.S);need(len(a)==len(b)==1 and a[0]==b[0],label+' changed')
 for k in OLD:need(figure_bytes(raw,k)==figure_bytes(before,k),'existing Emma image/caption changed: '+k)
 figures=[n for n in nodes if n.tag=='figure' and 'data-exclusive-artwork' in n.attrs]
 keys=[n.attrs['data-exclusive-artwork'] for n in figures];need(len(keys)==len(set(keys))==20 and set(keys)==OLD|NEW|{ORIGIN},'exact 20 distinct figure owners required')
 for fig in figures:
  key=fig.attrs['data-exclusive-artwork']
  # A figure is not visible by default if any ancestor is a closed disclosure
  # or explicitly hidden. This is a source check, not a browser-render pass.
  n=fig.parent
  while n:
   need(not (n.tag=='details' and 'open' not in n.attrs) and 'hidden' not in n.attrs and n.attrs.get('aria-hidden','').lower()!='true','figure hidden by ancestor: '+key)
   n=n.parent
  if key in OLD:continue
  need(fig.attrs.get('id')=='picture-'+key and fig.attrs.get('data-topic-art')==key,'wrong owner/detail ID '+key)
  parents=[];n=fig.parent
  while n:parents.append(n.attrs.get('id'));n=n.parent
  need(('emma-beginnings' if key==ORIGIN else SECTIONS[key[-2:]]) in parents,'wrong chronological section '+key)
  link=one(fig.children,lambda n:n.tag=='a' and n.attrs.get('aria-haspopup')=='dialog',key+' detail trigger')
  im=one(list(link.walk()),lambda n:n.tag=='img',key+' image');need(bool(im.attrs.get('alt','').strip()),'missing alt '+key)
  base='/assets/page-art/emma-journey/'+key
  need(link.attrs.get('href')==base+'-1536.webp' and im.attrs.get('src')==base+'-960.webp','wrong image mapping '+key)
  for width in (640,960,1536):need(base+'-'+str(width)+'.webp '+str(width)+'w' in im.attrs.get('srcset',''),'srcset drift '+key)
  cap=one(fig.children,lambda n:n.tag=='figcaption' and 'data-picture-panel-copy' in n.attrs and 'hidden' in n.attrs,key+' caption')
  one(list(cap.walk()),lambda n:n.tag=='a' and bool(n.attrs.get('href')),key+' source')
 ordered=[k[-2:] for k in keys if k in NEW];need(ordered==list(SECTIONS),'new scenes not chronological')
 for control in ['data-print-companion="emma"','data-print-study="emma"','data-save-study="/history/emma-hale-smith.html"','id="continue-study"']:
  need(control in text,'missing study control: '+control)
 validate_assets(root)
 return {'route':HUB,'sha256':sha(raw),'validation':'current source structure, not rendered or owner approval'}

def validate_redirect(raw):
 current_file(RETIRED,raw);text=raw.decode('utf8')
 need('<meta name="robots" content="noindex, follow">' in text,'retired page indexable')
 need('<link rel="canonical" href="https://focuschrist.com/history/emma-hale-smith.html">' in text,'canonical target changed')
 need('window.location.replace("emma-hale-smith.html" + window.location.search + hash)' in text,'query/hash preserving redirect missing')
 need('<noscript>' in text and 'href="emma-hale-smith.html"' in text,'no-JS manual link missing')
 return {'route':RETIRED,'sha256':sha(raw),'validation':'compatibility source, not canonical article'}

def validate_hymns(raw):
 current_file(HYMNS,raw);need(b'href="emma-hale-smith.html#heading-elect-lady-right-person">Previous: The right person' in raw,'previous story still targets retired page')
 return {'route':HYMNS,'sha256':sha(raw),'validation':'current source binding'}

def validate_canonical(raw):
 current_file('sitemap.xml',raw);urls=[e.text for e in ET.fromstring(raw).findall('{*}url/{*}loc')];routes=[]
 for u in urls:
  x=urlsplit(u);need(x.scheme=='https' and x.netloc=='focuschrist.com' and not x.query and not x.fragment,'unknown canonical URL');routes.append(x.path.lstrip('/') or 'index.html')
 need(len(routes)==len(set(routes))==138 and HUB in routes and RETIRED not in routes,'wrong canonical owner set')
 need(sha('\n'.join(sorted(routes)).encode())==CANONICAL_CURRENT,'unknown canonical set change')
 return routes

def historical_fixture(route,current,root):
 """Never a current DOM or URL. Validate actual candidate, then project old bytes."""
 need(route in (HUB,RETIRED,HYMNS),'unsupported historical projection')
 if route==HUB:validate_hub(current,root)
 elif route==RETIRED:validate_redirect(current)
 else:validate_hymns(current)
 return predecessor_fixture(route)

def historical_routes(current_sitemap):
 """Explicit old route fixture; NEVER use as current sitemap/list of owners."""
 routes=validate_canonical(current_sitemap);old=routes+[RETIRED]
 need(len(old)==139 and sha('\n'.join(sorted(old)).encode())==CANONICAL_PRIOR,'historical canonical reconstruction mismatch')
 return old


# The current delivery validator runs before this gate in artwork_creation_gate.
# This is an additional exact-source/render/owner boundary, never a replacement
# for the original, derivative, independent-pixel, or aggregate artwork gates.
FINAL_SOURCE_REVIEW_PATH='docs/emma-journey-release/final-source-review.json'
OWNER_ACCEPTANCE_PATH='docs/emma-journey-release/owner-acceptance.json'
RELEASE_CHECKS={'current_source','chronology_and_sources','retained_art','new_art',
                'controls_and_navigation','desktop_render','phone_render'}

def _canonical(value):
 return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8'))

def _bound(root, entry):
 need(isinstance(entry,dict) and set(entry)=={'path','bytes','sha256'},'invalid evidence binding')
 name=entry['path'];need(isinstance(name,str) and name and not Path(name).is_absolute() and '..' not in Path(name).parts,'unsafe evidence path')
 need(isinstance(entry['bytes'],int) and not isinstance(entry['bytes'],bool) and entry['bytes']>0,'invalid evidence size')
 need(isinstance(entry['sha256'],str) and re.fullmatch(r'[0-9a-f]{64}',entry['sha256']) is not None,'invalid evidence digest')
 # Check each component, not merely the final file, to exclude symlink escapes.
 for i in range(1,len(Path(name).parts)+1):need(not Path(root).joinpath(*Path(name).parts[:i]).is_symlink(),'symlink evidence path')
 raw=safe(root,name).read_bytes();need(len(raw)==entry['bytes'] and sha(raw)==entry['sha256'],'evidence bytes drift: '+name)
 return raw

def _json_bound(root,entry):
 try:return json.loads(_bound(root,entry))
 except (ValueError,UnicodeDecodeError) as e:raise AssertionError('malformed evidence JSON') from e

def _time(value):
 from datetime import datetime
 need(isinstance(value,str),'missing review time')
 try: t=datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError as e: raise AssertionError('invalid review time') from e
 need(t.tzinfo is not None and t.utcoffset() is not None,'review time lacks timezone');return t

def release_gate(root=None,delivery_record=None):
 """Validate pinned actual review and direct acceptance; missing proof fails closed.

 Structural hashes and fields cannot authenticate human identities or prove that
 pixels were inspected; reviewers must independently verify the portable records
 and their evidence before setting pins. Synthetic fixtures are never approval.
 """
 need(OWNER_ACCEPTANCE_SHA256 is not None and FINAL_SOURCE_REVIEW_SHA256 is not None,'PENDING actual exact owner acceptance and independent finished-source review')
 need(root is not None and isinstance(delivery_record,dict),'missing current checkout or delivery record')
 from artwork_emma_journey_delivery import APPROVED_RECORD_SHA256, MANIFEST as DELIVERY_PATH
 from artwork_emma_story_delivery import canonical
 need(APPROVED_RECORD_SHA256 is not None and canonical(delivery_record)==APPROVED_RECORD_SHA256,'unreviewed current artwork delivery record')
 root=Path(root).resolve()
 # Re-read actual current source and every source PNG; source-only validate_assets
 # permits preview-only 33 derivatives, but release specifically requires 44.
 for path,validator in ((HUB,lambda b:validate_hub(b,root)),(RETIRED,validate_redirect),(HYMNS,validate_hymns),('sitemap.xml',validate_canonical)):
  validator(safe(root,path).read_bytes())
 manifest=read_manifest()
 for name,row in manifest['original_assets'].items():
  raw=safe(root,name).read_bytes();need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'missing or changed source original')
 # The accepted delivery file must be exactly the separately pinned, previously
 # validated record, not merely a caller-supplied object with a matching label.
 try: disk_record=json.loads(safe(root,DELIVERY_PATH).read_bytes())
 except (ValueError,UnicodeDecodeError) as e: raise AssertionError('malformed artwork delivery record') from e
 need(disk_record==delivery_record and canonical(disk_record)==APPROVED_RECORD_SHA256,'delivery record differs from current file')
 final_raw=safe(root,FINAL_SOURCE_REVIEW_PATH).read_bytes();need(sha(final_raw)==FINAL_SOURCE_REVIEW_SHA256,'unreviewed final source/render record')
 try:final=json.loads(final_raw)
 except (ValueError,UnicodeDecodeError) as e: raise AssertionError('malformed final source/render record') from e
 need(final.get('schema')==1 and final.get('status')=='REVIEWED_EXACT_CURRENT','wrong final review record')
 b=final.get('bindings');need(isinstance(b,dict) and set(b)=={'source_manifest_sha256','delivery_spec_sha256','page_sha256','redirect_sha256','hymns_sha256','sitemap_sha256','rendered'},'wrong final review bindings')
 need(b['source_manifest_sha256']==MANIFEST_SHA256 and b['delivery_spec_sha256']==canonical(delivery_record['spec']),'source or delivery binding drift')
 for path,key in ((HUB,'page_sha256'),(RETIRED,'redirect_sha256'),(HYMNS,'hymns_sha256'),('sitemap.xml','sitemap_sha256')):need(b[key]==sha(safe(root,path).read_bytes()),'reviewed source mismatch '+path)
 rendered=b['rendered'];need(isinstance(rendered,dict) and set(rendered)=={'desktop','phone'},'desktop and phone renders required')
 for label, minimum in (('desktop',1024),('phone',240)):
  item=rendered[label];need(isinstance(item,dict) and set(item)=={'image','viewport_width','viewport_height'},'malformed render binding')
  w=item['viewport_width'];h=item['viewport_height'];need(isinstance(w,int) and not isinstance(w,bool) and isinstance(h,int) and not isinstance(h,bool) and w>=minimum and h>=240,'invalid viewport')
  if label=='phone':need(w<=600,'phone viewport too wide')
  raw=_bound(root,item['image']);need(raw.startswith(b'\x89PNG\r\n\x1a\n'),'render evidence must be PNG')
  from PIL import Image
  from io import BytesIO
  try:
   with Image.open(BytesIO(raw)) as im:need(im.format=='PNG' and im.width==w and im.height>=h and getattr(im,'n_frames',1)==1,'render dimensions mismatch');im.verify()
  except (OSError,ValueError) as e:raise AssertionError('invalid render PNG') from e
 binding=_canonical(b);reviews=final.get('reviews');need(isinstance(reviews,list) and len(reviews)==3,'three separate assembled reviews required')
 actors={};dates=[];receipt_paths=set()
 for pointer in reviews:
  need(isinstance(pointer,dict) and isinstance(pointer.get('path'),str),'invalid review receipt pointer')
  need(pointer['path'] not in receipt_paths,'reused review receipt');receipt_paths.add(pointer['path']);review=_json_bound(root,pointer)
  who=review.get('reviewer');actor=review.get('actual_actor');need(who in {'Fermi','Newton','Albert'} and who not in actors,'duplicate or unknown reviewer')
  need(isinstance(actor,str) and actor.strip() and actor not in actors.values(),'reviewers not distinct')
  need(review.get('stage')=='final_source_and_render' and review.get('verdict')=='PASS' and review.get('withdrawn') is False and review.get('binding_sha256')==binding,'stale or negative final review')
  checks=review.get('checks');need(isinstance(checks,dict) and set(checks)==RELEASE_CHECKS and all(isinstance(x,str) and x.strip() for x in checks.values()),'missing review observations')
  evidence=review.get('evidence');need(isinstance(evidence,list) and evidence,'reviewer evidence absent')
  for item in evidence:_bound(root,item)
  dates.append(_time(review.get('reviewed_at')));actors[who]=actor
 need(set(actors)=={'Fermi','Newton','Albert'},'missing independent reviewer')
 # Same actors as the independently reviewed artwork assembled receipts.
 assembled=delivery_record.get('assembled_reviews');need(isinstance(assembled,list) and len(assembled)==3,'artwork assembled reviews missing')
 seen=set()
 for pointer in assembled:
  art=_json_bound(root,pointer);who=art.get('reviewer');need(who in actors and who not in seen and art.get('actual_actor')==actors[who] and art.get('stage')=='assembled' and art.get('verdict')=='PASS' and art.get('withdrawn') is False,'artwork and final reviewer mismatch');seen.add(who)
 owner_pointer=delivery_record.get('owner_acceptance');need(isinstance(owner_pointer,dict) and owner_pointer.get('path')==OWNER_ACCEPTANCE_PATH and owner_pointer.get('sha256')==OWNER_ACCEPTANCE_SHA256,'artwork and release must bind the same owner acceptance')
 owner_raw=_bound(root,owner_pointer);need(sha(owner_raw)==OWNER_ACCEPTANCE_SHA256,'unreviewed owner receipt')
 try:owner=json.loads(owner_raw)
 except (ValueError,UnicodeDecodeError) as e: raise AssertionError('malformed owner receipt') from e
 need(owner.get('kind')=='direct_owner_acceptance' and owner.get('actor')=='Wyatt' and owner.get('verdict')=='ACCEPT' and owner.get('withdrawn') is False,'direct owner acceptance missing or withdrawn')
 need(owner.get('subject_sha256')==canonical(delivery_record['spec']) and owner.get('release_review_sha256')==FINAL_SOURCE_REVIEW_SHA256,'owner accepted different delivery or final review')
 need(_time(owner.get('accepted_at'))>=max(dates),'owner acceptance predates final review')
 evidence=owner.get('evidence');need(isinstance(evidence,list) and evidence,'owner source evidence absent')
 for item in evidence:_bound(root,item)
 return {'status':'validated exact source/render and owner receipt; identity and visual judgment require independent verification','review_sha256':FINAL_SOURCE_REVIEW_SHA256,'owner_sha256':OWNER_ACCEPTANCE_SHA256}
