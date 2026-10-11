"""Private exact Answers-family validator, bound to audited graph/census.

Not installed. No actual current-equivalence record is yet authorized; genuine
review receipts and resolution of the observed interaction hold remain required.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup

SCENES={
 'answers-connected-conversation':('connected-study','fictional-contemporary'),
 'answers-neighbor-service':('connected-study','fictional-contemporary'),
 'answers-two-witnesses':('connected-study','still-life'),
 'answers-family-hopes':('connected-study','fictional-contemporary'),
 'answers-keep-your-place':('saved-studies','still-life'),
 'answers-companion-bench':('study-companions','fictional-contemporary'),
}
EXPECTED_GRAPH='bae70b5dcbff59f2d74173382c9817adcbdb4025055b8001144641dbb8c72041'
EXPECTED_CENSUS='aa1848d63cea01cae0cda86cdc154d51ab2ba8c123a0bbe6ad3d7241d69c4e6d'

def require(ok,message):
 if not ok:raise ValueError('Answers six delivery: '+message)
def canonical(value):
 return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def local(root,name):
 require(isinstance(name,str) and not Path(name).is_absolute() and '\\' not in name and ':' not in name,'unsafe local path')
 p=(root/name).resolve();require(p.is_relative_to(root.resolve()) and p.is_file(),'missing or unsafe local file '+name)
 return p
def timestamp(value):
 t=dt.datetime.fromisoformat(value.replace('Z','+00:00'));require(t.tzinfo is not None,'naive timestamp');return t
def hash64(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)

def validate(root,record,approved_binding,added,covered,rejected,pixel_hash,page_dependencies):
 require(EXPECTED_GRAPH is not None and EXPECTED_CENSUS is not None,'private draft pins not frozen')
 require(record.get('schema')==1 and canonical(record)==approved_binding,'unreviewed exact record')
 spec=record['spec'];binding=canonical(spec)
 require(spec['registration_class']=='CURRENT_EQUIVALENCE' and spec['owner_final_image_acceptance']=='not-claimed','registration/owner claim drift')
 require(spec['route']=='answers.html' and len(spec['scenes'])==6 and {s['id'] for s in spec['scenes']}==set(SCENES),'only exact six Answers scenes permitted')
 graph=spec['generation_graph'];nodes={n['id']:n for n in graph}
 require(len(graph)==9 and len(nodes)==9 and canonical(graph)==EXPECTED_GRAPH,'exact native graph changed')
 for n in graph:
  require(n['source_sha256'] not in rejected and hash64(n['source_sha256']),'forbidden/invalid source ancestor')
  require(hash64(n['stored_prompt_sha256']) and n['stored_prompt_sha256']==n['dispatched_prompt_sha256'],'prompt identity drift')
  require(n['prompt_binding_basis'] in {'hash-bound-reviewed-file-plus-native-load-store-dispatch','literal-loaded-prompt-plus-native-dispatch-variable-flow'},'unproven prompt binding')
  require(n['event_hash_basis']=='UTF8 JSONL line excluding line ending','event digest basis drift')
  require(timestamp(n['prompt_load']['timestamp'])<=timestamp(n['dispatch']['timestamp'])<timestamp(n['completion']['timestamp']),'generation chronology reversed')
  require(n['actual_load_outputs'],'missing actual prompt load proof')
  for e in [n['prompt_load'],n['dispatch'],n['completion'],*n['actual_load_outputs']]:require(hash64(e['event_sha256']),'invalid native event digest')
  for e in n['actual_load_outputs']:
   require(timestamp(n['prompt_load']['timestamp'])<=timestamp(e['timestamp'])<=timestamp(n['dispatch']['timestamp']),'load-output chronology reversed')
  recovery=n['output_path_recovery']
  require(hash64(recovery['event_sha256']) and timestamp(n['completion']['timestamp'])<=timestamp(recovery['timestamp']),'invalid output-path recovery evidence')
  require(len(n['references'])==len(set(n['references'])),'duplicate source reference')
  for parent in n['references']:
   require(parent in nodes and timestamp(nodes[parent]['completion']['timestamp'])<timestamp(n['dispatch']['timestamp']),'unresolved/future predecessor')
  require(n['generation_mode'] in {'original','edit'},'generation mode drift')
  require((n['generation_mode']=='original' and n['references']==[]) or (n['generation_mode']=='edit' and len(n['references'])==1),'reference-input drift')
 require(spec['historical_preparation_audit']['reviewer']=='Newton' and spec['historical_preparation_audit']['status']=='CURRENT_NODE_AUDIT_COMPLETE_HISTORICAL_PREPARATION_NOT_CLAIMED' and spec['historical_preparation_audit']['limitations'],'missing bounded historical audit')
 require('final_preparation' not in spec,'invented historical normalization')
 page=local(root,'answers.html');soup=BeautifulSoup(page.read_bytes(),'html.parser')
 census=spec['original_owner_census'];require(canonical(census)==EXPECTED_CENSUS,'original-owner classification changed')
 require(len(census)==15 and sum(r['depicts_christ'] is True for r in census)==8,'complete owner count/Christ ratio changed')
 require(len({r['src'] for r in census})==15,'duplicate owner census')
 for row in census:
  imgs=soup.find_all('img',src=row['src']);require(len(imgs)==1,'owner image missing/duplicated')
  require(canonical(dict(imgs[0].attrs))==row['markup_sha256'],'original owner markup changed')
  require(digest(local(root,row['src'].split('?',1)[0]))==row['sha256'],'original owner pixels changed')
 all_src=[i.get('src','') for i in soup.find_all('img')]
 require(len(all_src)==19,'unexpected current page image count')
 excluded=spec['excluded_image_sources'];require(len(excluded)==4 and set(all_src)=={r['src'] for r in census}|set(excluded),'unclassified image or reference')
 assets=set();hashes=set();pixels=set();latest=max(timestamp(s['final_generated_at']) for s in spec['scenes'])
 for s in spec['scenes']:
  sid=s['id'];section,kind=SCENES[sid]
  require(s['route']=='answers.html' and s['owning_section']==section and s['scene_kind']==kind and s['depicts_christ'] is False and s['identity_claim']=='none','scene classification drift')
  require(s['historical_claim'] is False,'fictional/still-life misrepresented as historical')
  expected={f'assets/page-art/answers-study/{sid}-original.png',*[f'assets/page-art/answers-study/{sid}-{size}.webp' for size in ['640','960','full']]}
  require(len(s['assets'])==4 and {a['path'] for a in s['assets']}==expected,'asset family expansion/omission')
  masters=[a for a in s['assets'] if a['kind']=='original'];require(len(masters)==1 and masters[0]['path'].endswith('-original.png'),'wrong original asset')
  chain=s['generation_ids']
  require(bool(chain) and len(chain)==len(set(chain)) and all(n in nodes for n in chain),'bad scene generation chain')
  require(all(nodes[n]['scene_id']==sid for n in chain),'cross-scene generation chain')
  require(nodes[chain[0]]['generation_mode']=='original' and chain==[n['id'] for n in graph if n['scene_id']==sid],'incomplete or reordered scene ancestry')
  master=masters[0];final=nodes[chain[-1]]
  require(final['source_sha256']==master['sha256'] and final['completion']['timestamp']==s['final_generated_at'] and final['delivery_status']=='final-reviewed-source','wrong final source')
  for previous,current in zip(s['generation_ids'],s['generation_ids'][1:]):require(nodes[current]['references']==[previous],'scene ancestry drift')
  with Image.open(local(root,master['path'])) as source:original=source.convert('RGB')
  for a in s['assets']:
   p=local(root,a['path']);require(digest(p)==a['sha256'] and a['sha256'] not in rejected,'asset bytes changed/rejected')
   require(pixel_hash(p)==a['pixel_sha256'],'pixel digest changed')
   with Image.open(p) as im:
    require(im.size==(a['width'],a['height']) and getattr(im,'n_frames',1)==1,'wrong raster geometry/animation')
    target=original if a['width']==original.width else original.resize((a['width'],round(original.height*a['width']/original.width)),Image.Resampling.LANCZOS)
    require(im.size==target.size and im.convert('RGB').tobytes()==target.tobytes(),'lossless decoded equivalence failed')
   assets.add(a['path']);hashes.add(a['sha256']);pixels.add(a['pixel_sha256'])
  figures=soup.find_all('figure',id=sid);require(len(figures)==1 and figures[0].get('data-original-artwork')==sid,'owning figure missing/duplicate')
  require(figures[0].find_parent(id=section) is not None,'wrong owning section')
  require(len(figures[0].select('[data-artwork-detail="'+sid+'"]'))==1,'missing owning dialog trigger')
  require(len(soup.select('[data-artwork-detail-content="'+sid+'"]'))==1,'missing/duplicate detail record')
 context=spec['context'];bindings={r['path']:r['sha256'] for r in context}
 require(len(bindings)==len(context) and page_dependencies(root,'answers.html')<=set(bindings),'missing/duplicate page dependency')
 require({'answers.html','answers-illustrated-study.css','answers-artwork-dialog.css','answers-artwork-dialog.js'}<=set(bindings),'missing actual dialog/style binding')
 for path,value in bindings.items():require(digest(local(root,path))==value,'rendered context drift '+path)
 require(len(assets)==24 and assets<=added and not assets&covered,'coverage requires24 distinct new raster paths')
 reviews={}
 for pointer in record['reviews']:
  p=local(root,pointer['path']);require(digest(p)==pointer['sha256'],'review bytes changed');r=json.loads(p.read_bytes());who=r['reviewer']
  require(who in {'Fermi','Newton','Albert'} and who not in reviews,'unexpected/duplicate reviewer')
  require(r['decision']=='CONCUR' and r['spec_sha256']==binding,'missing exact concurrence')
  require(timestamp(r['reviewed_at'])>=latest and timestamp(r['reviewed_at'])>=timestamp(record['normalized_at']),'backdated current equivalence')
  require(r['no_individual_owner_acceptance_claim'] is True and r['evidence'] and r['limits'],'missing truthful review scope')
  if who in {'Fermi','Newton'}:
   require(all(r[k] is True for k in ['private_source_and_event_verification','derivative_pixel_review','complete_owner_classification','assembled_context_review']),'missing independent finished scope')
  else:require(r['desktop_phone_direct_browser_review'] is True,'missing actual root browser review')
  reviews[who]=r
 require(set(reviews)=={'Fermi','Newton','Albert'},'three actual current reviewers required')
 return assets,hashes,pixels
