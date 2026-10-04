exec((__import__('pathlib').Path(__file__).parent/'review_inventory.py').read_text().split('rows=[]')[0])
import re
from urllib.parse import urlsplit,unquote
old=json.loads((P/'fermi/lineage-assets-current.json').read_text()); prior={r['path']:r['file_sha256'] for r in old}
files={p.relative_to(S).as_posix():sha(p) for p in S.rglob('*') if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.avif'} and not set(p.relative_to(S).parts)&{'.git','work','node_modules','outputs','tools','tests','.venv'}}
changed=[p for p,h in files.items() if p in prior and prior[p]!=h]; added=[p for p in files if p not in prior]; removed=[p for p in prior if p not in files]
assert not changed and not removed
assert set(added)=={x[k] for x in new for k in ['asset','thumbnail']}
ret=json.loads(Path('C:/Users/wyatt/Documents/Codex/2026-10-04/three-art-studies-enriched-continuation/work/fermi/retained15-review.json').read_text())['rows']
targets={x['asset']:{'owner':x['owner_route'],'christ':x['depicts_christ'],'sha256':x['sha256']} for x in ret}
targets.update({x['asset']:{'owner':x['page'],'christ':x['christ'],'sha256':x['sha256']} for x in new})
aliases={asset:asset for asset in targets}
aliases.update({asset.replace('/full/','/thumbs/'):asset for asset in targets})
occ=[]; pages=[]
for p in sorted(S.rglob('*.html')):
 if set(p.relative_to(S).parts)&{'.git','work','node_modules','outputs','tools','tests','.venv'}:continue
 route=p.relative_to(S).as_posix();pages.append(route);soup=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
 for tag in soup.find_all(True):
  for attr in ['src','href','poster','data-src','data-full','data-full-src','data-image','srcset']:
   for value in re.split(r'[,\s]+',tag.get(attr,'')):
    u=urlsplit(value)
    if u.scheme or u.netloc or not u.path:continue
    asset=posixpath.normpath(unquote(u.path).lstrip('/') if u.path.startswith('/') else posixpath.join(posixpath.dirname(route),unquote(u.path)))
    if asset in aliases:
     owner=targets[aliases[asset]]['owner']; parent=tag.find_parent(lambda x:x.name in ['section','figure'] and x.get('id'))
     occ.append({'route':route,'asset':asset,'original':aliases[asset],'tag':tag.name,'attribute':attr,'owner_matches':owner==route,'section':parent.get('id') if parent else None})
bad=[x for x in occ if not x['owner_matches']]
gallery=BeautifulSoup((S/'art.html').read_text(encoding='utf8'),'html.parser'); refs=[];resources={}
for row in json.loads((W/'inventory.json').read_text()):
 route=row['route']; slug=Path(route).stem;hero=row['images'][0]; target='gallery-original-'+slug;node=gallery.find(id=target)
 assert node and node.img['data-full-src']==hero['asset']
 assert '../art.html#'+target in hero['links']
 refs.append({'route':route,'asset':hero['asset'],'sha256':sha(S/hero['asset']),'target':'../art.html#'+target,'target_asset':node.img['data-full-src'],'target_matches':True})
 resources[route]=[{'asset':x['asset'],'sha256':sha(S/x['asset'])} for x in row['images'][1:] if not x['supporting']]
proof={'status':'MECHANICAL_EVIDENCE_REQUIRES_REVIEW','raster_count':len(files),'prior_count':len(prior),'unchanged_prior_count':len(prior),'added':added,'changed':changed,'removed':removed,'html_count':len(pages),'occurrences':occ,'unexpected_owner_occurrences':bad,'references':refs,'resource_exclusions':resources,'targets':targets,'prior_receipts':[{'path':str(P/'fermi'/n),'sha256':sha(P/'fermi'/n)} for n in ['lineage-review-current27.json','lineage-final3-review.json','lineage-final3-scan.json']]}
(W/'final-lineage-scan.json').write_text(json.dumps(proof,indent=2))
print(json.dumps({k:v for k,v in proof.items() if k not in ['occurrences','targets','added']},indent=2))
