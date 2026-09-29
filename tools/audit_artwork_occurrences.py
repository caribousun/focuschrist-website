#!/usr/bin/env python3
"""Reproducible occurrence/lineage audit; candidates require visual adjudication.

Run: python tools/audit_artwork_occurrences.py --output work/artwork-audit-current
Uses public HTML, local CSS/JS literal references, generated gallery ownership data,
and the dated independent pixel-family report. It never infers runtime visibility
from a literal or treats shared-base narrative edits as identical images.
"""
import argparse
import json,sys,re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from topic_artwork_uniqueness_qa import scan,local_asset,public_pages
parser=argparse.ArgumentParser();parser.add_argument('--output',default='work/artwork-audit-current');args=parser.parse_args()
out=root/args.output;out.mkdir(parents=True,exist_ok=True)
base=scan(root);(out/'existing-lineage-scan.json').write_text(json.dumps(base,indent=2)+'\n')
parent={a:a for g in base['familyUsages'].values() for a in g['assets']}
def find(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
def union(a,b):
 if a in parent and b in parent:parent[find(b)]=find(a)
for g in base['familyUsages'].values():
 for a in g['assets'][1:]:union(g['assets'][0],a)
# Include fresh independent exact and high-confidence visual families, including gallery originals.
pixels=json.loads((root/'docs/artwork-uniqueness-audit-20260929/pixel-families.json').read_text())
for item in pixels['assets']:
 a=item['path'];parent.setdefault(a,a)
for group in pixels['source_family_groups']:
 for a in group[1:]:union(group[0],a)
for pair in pixels['pairs']:
 if pair['method']=='SIFT_homography' and pair.get('inlier_ratio',0)>=0.8 and pair.get('inliers',0)>=30:union(pair['a'],pair['b'])
joins=[];source_seen={}
def walk(x,path):
 if isinstance(x,list):
  for v in x:walk(v,path)
 elif isinstance(x,dict):
  # A single per-image record, not a document-wide collection.
  fields=['asset','full','thumbnail','responsive','desktop','mobile','path','original','source_original']
  assets=[x[k].lstrip('/') for k in fields if isinstance(x.get(k),str) and x[k].lstrip('/') in parent]
  for k in ['published_assets','assets']:
   if isinstance(x.get(k),list) and (x.get('source_sha256') or x.get('source_path')):
    assets += [v.get('path') for v in x[k] if isinstance(v,dict) and v.get('path') in parent]
  if assets:
   for a in assets[1:]:union(assets[0],a)
   for k in ['source_sha256','source_decoded_rgb_sha256','source_original','source_path','source_file']:
    v=x.get(k)
    if not isinstance(v,str) or not v:continue
    token=(k,v.replace('\\','/'))
    if token in source_seen:union(assets[0],source_seen[token]);joins.append({'record':str(path.relative_to(root)),'field':k,'assets':[assets[0],source_seen[token]]})
    source_seen[token]=assets[0]
  for v in x.values():walk(v,path)
for p in (root/'docs').rglob('*.json'):
 try:walk(json.loads(p.read_text(encoding='utf-8-sig')),p)
 except (ValueError,UnicodeError):pass
rows=[];pages={}
for p in public_pages(root):
 rel=p.relative_to(root).as_posix();s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser');pages[rel]=s
 for i,img in enumerate(s.find_all('img')):
  asset=local_asset(p,img.get('src',''),root)
  if asset not in parent:continue
  ancestors=list(img.parents);fig=img.find_parent('figure');link=img.find_parent('a');section=img.find_parent(id=True)
  classes=' '.join(' '.join(n.get('class',[])) for n in ancestors if n.name)
  if any(n.name in ['noscript','template','dialog'] for n in ancestors):role='fallback-or-detail'
  elif 'fc-resource-card' in classes or asset.startswith('assets/resources/'):role='official-resource-thumbnail'
  elif re.search(r'(?:favicon|logo|icon|flag)',asset,re.I):role='interface-or-brand'
  else:role='artwork'
  target=None
  if link:
   u=urlsplit(link.get('href',''))
   if (not u.netloc or u.netloc in ['focuschrist.com','www.focuschrist.com']) and u.path.endswith('.html'):
    q=(root/u.path.lstrip('/') if u.path.startswith('/') or u.netloc else p.parent/u.path).resolve()
    if q.is_relative_to(root.resolve()):target={'page':q.relative_to(root.resolve()).as_posix(),'fragment':unquote(u.fragment)}
  explicit=any(n.has_attr('data-linked-picture-reference') for n in ancestors if n.name)
  rows.append({'page':rel,'image_index':i,'asset':asset,'family':find(asset),'role':role,'alt':img.get('alt',''),'section':section.get('id') if section else None,'figure':bool(fig),'target':target,'explicit_reference':explicit,'classes':classes[-400:]})
for rel,soup in pages.items():
 page=root/rel
 for node in soup.select('[style]'):
  for url in re.findall(r"url\(['\"]?([^)'\"]+)",node.get('style','')):
   asset=local_asset(page,url,root)
   if asset not in parent:continue
   family=find(asset)
   if any(r['page']==rel and r['family']==family for r in rows):continue
   rows.append({'page':rel,'image_index':None,'asset':asset,'family':family,'role':'artwork','alt':node.get('data-full-image-alt',''),'section':node.get('id'),'figure':node.name=='figure','target':None,'explicit_reference':False,'classes':' '.join(node.get('class',[])),'source_type':'inline-style-picture'})
for row in rows:
 t=row['target']
 if row['role']!='artwork' or not t or t['page']==row['page']:continue
 owner_matches=[r for r in rows if r['page']==t['page'] and r['family']==row['family'] and r['role']=='artwork']
 fragment_exists=not t['fragment'] or (t['page'] in pages and pages[t['page']].find(id=t['fragment']) is not None)
 if owner_matches and fragment_exists:row['role']='crosspage-owner-reference';row['reference_validation']='same original exists at destination; fragment exists if specified'
 elif row['explicit_reference']:row['reference_validation']='UNVERIFIED owner original or fragment'
groups={}
for r in rows:
 if r['role']=='artwork':groups.setdefault(r['family'],[]).append(r)
findings=[{'family':k,'owning_occurrences':v,'pages':sorted({r['page'] for r in v}),'status':'needs_rendered_adjudication'} for k,v in groups.items() if len(v)>1]
result={'public_html_count':len(pages),'image_occurrences':len(rows),'owning_families':len(groups),'candidate_duplicate_families':len(findings),'findings':findings,'occurrences':rows,'lineage_joins':joins,'limitations':['Static img occurrences; CSS/JS literal references retained in existing-lineage-scan, not presumed visible owners. Dynamic generated cards require runtime/asset-index review.','Crosspage link qualifies only when same-family original exists on destination and fragment resolves; owning role can still require visible-context review.','Same-page responsive img toggles or hidden views require rendered adjudication before declaring violation.']}
# Literal references are evidence of loading or potential use, not rendered owners.
consumers={}
for rel,soup in pages.items():
 for node,attr in [(n,'href') for n in soup.select('link[href]')]+[(n,'src') for n in soup.select('script[src]')]:
  url=urlsplit(node[attr]);file=(root/url.path.lstrip('/') if url.path.startswith('/') else (root/rel).parent/url.path).resolve()
  if not url.netloc and file.is_relative_to(root):consumers.setdefault(file.relative_to(root).as_posix(),[]).append(rel)
literals=[]
for rel,used_by in consumers.items():
 file=root/rel
 if not file.is_file() or file.suffix not in {'.css','.js'}:continue
 text=file.read_text(encoding='utf8')
 values=re.findall(r"url\(['\"]?([^)'\"]+)",text) if file.suffix=='.css' else re.findall(r"['\"]([^'\"\n]+\.(?:webp|png|jpe?g|avif))['\"]",text)
 for value in sorted(set(values)):
  asset=local_asset(file,value,root)
  if asset and (root/asset).is_file():literals.append({'source_file':rel,'asset':asset,'consumers':used_by,'kind':'stylesheet-literal' if file.suffix=='.css' else 'script-literal','visibility':'not inferred'})
gallery=json.loads((root/'art-gallery.json').read_text(encoding='utf8'))
result['css_js_literals']=literals
result['dynamic_gallery']={'source':'art-gallery.json','stats':gallery.get('stats'),'records':len(gallery.get('artworks',[])),'interpretation':'Generated gallery is an index of owner occurrences, not additional original pictures; validate with build_art_gallery.py --check and art-gallery runtime checks. No claim every lazy/runtime state was visually traversed.'}
result['coverage']='Public HTML img and inline CSS pictures; loaded local CSS/JS literal image references; generated gallery index metadata. Pixel corpus is dated independent evidence; responsive variants and shared-base edits require adjudication.'
(out/'occurrence-ledger.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['public_html_count','image_occurrences','owning_families','candidate_duplicate_families']}))
