#!/usr/bin/env python3
"""Count distinct contextual body artwork; hero and source preview cards never count."""
import hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document
from production_hardening_qa import image_dimensions
ROOT=Path(__file__).resolve().parents[1]

def ancestors(node):
 while node.parent:
  node=node.parent
  yield node

def identity(path):
 return re.sub(r'-(?:320|640|800|900|1200|1536|2048)$','',path.stem)

def audit():
 results=[]
 for page in [*sorted((ROOT/'answers').glob('*.html')),ROOT/'general-conference.html']:
  doc=Document();doc.feed(page.read_text(encoding='utf-8'));nodes=list(doc.root.walk())
  images=[];unique=set();hashes=set();sections=set();issues=[]
  for n in nodes:
   if n.tag!='img':continue
   chain=list(ancestors(n))
   if not any(a.tag=='main' for a in chain) or any(a.has('fc-resource-card') or a.has('fc-topic-opening') or a.has('gc-intro') or a.tag=='dialog' for a in chain):continue
   figure=next((a for a in chain if a.tag=='figure' or a.has('fc-marriage-era')),None)
   if not figure or not figure.text().strip():continue
   section=next((a for a in chain if a.tag=='section'),None)
   location=figure.attrs.get('id','reading-'+str(figure.order))
   src=n.attrs.get('src','');u=urlsplit(src)
   if u.scheme:issues.append('Body artwork requires an inventoried local original: '+src);continue
   file=(page.parent/u.path).resolve();assert file.is_file(),file
   key=identity(file);digest=hashlib.sha256(file.read_bytes()).hexdigest()
   dims=image_dimensions(file);htmlratio=int(n.attrs['width'])/int(n.attrs['height']) if n.attrs.get('width') and n.attrs.get('height') else None
   if htmlratio and abs(htmlratio/(dims[0]/dims[1])-1)>.01:issues.append('HTML intrinsic ratio differs from source: '+src)
   images.append(dict(src=src,section=location,native=list(dims)))
   if key not in unique and digest not in hashes:unique.add(key);hashes.add(digest);sections.add(location)
  if len(unique)<5:issues.append(f'Needs five distinct body pictures; found {len(unique)}')
  if len(sections)<3:issues.append(f'Pictures must be distributed through at least three reading locations; found {len(sections)}')
  results.append(dict(page=page.relative_to(ROOT).as_posix(),distinct=len(unique),sections=len(sections),images=images,issues=issues))
 return results
if __name__=='__main__':
 results=audit();print(json.dumps(results,indent=2));sys.exit(any(r['issues'] for r in results))
