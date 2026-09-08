#!/usr/bin/env python3
"""Check every additional contextual figure against its reviewed placement ledger."""
import json,re,hashlib
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from answer_study_qa import Document
from production_hardening_qa import image_dimensions
ROOT=Path(__file__).resolve().parents[1]
def nodes(p):
 d=Document();d.feed(p.read_text(encoding='utf-8'));return list(d.root.walk())
placements=[]
for ledger in sorted((ROOT/'docs').glob('five-picture-placement-*.json')):
 data=json.loads(ledger.read_text(encoding='utf-8'));placements.extend(data['placements'])
assert placements,'Missing reviewed five-picture manifests'
review=json.loads((ROOT/'docs/five-picture-image-review.json').read_text(encoding='utf-8'))
assert len(review['approved'])==2
for record in review['approved']:
 for asset in record['assets']:
  assert hashlib.sha256((ROOT/asset['path']).read_bytes()).hexdigest()==asset['sha256'],asset['path']+' changed after image review'
for page in [*sorted((ROOT/'answers').glob('*.html')),ROOT/'general-conference.html']:
 text=page.read_text(encoding='utf-8')
 assert not re.search(r'christ-disciples-(?:800|1536)\.webp',text),'Owner-flagged image reused'
 for rejected in review['excluded']:
  assert rejected['source'].replace('\\','/').rsplit('/',1)[-1] not in text,'Rejected generation referenced'
 ns=nodes(page)
 if any(n.has('fc-study-visual') for n in ns):
  assert len([n for n in ns if n.tag=='link' and 'topic-art.css?' in n.attrs.get('href','')])==1,str(page)+' missing contextual artwork CSS' 
actual={}
for page in [*sorted((ROOT/'answers').glob('*.html')),ROOT/'general-conference.html']:
 ns=nodes(page)
 for f in ns:
  if f.tag!='figure' or 'data-five-picture-mandate' not in f.attrs:continue
  im=next(n for n in f.walk() if n.tag=='img');key=(page.relative_to(ROOT).as_posix(),(page.parent/im.attrs['src']).resolve())
  assert key not in actual,'Repeated same body image: '+str(key)
  actual[key]=(f,page,ns)
assert len(actual)==len(placements),'Markup and additional artwork manifests differ'
for i in placements:
 f,page,ns=actual.pop((i['page'],(ROOT/i['asset']).resolve()))
 parent=f.parent
 while parent and not (parent.attrs.get('id')==i['section'] or any(n.tag in ('h2','h3') and n.attrs.get('id')==i['section'] for n in parent.children)):parent=parent.parent
 assert parent is not None,(i['page'],i['section'])
 context=[]
 for n in parent.walk():
  if n.tag not in ('p','h2','h3'):continue
  ancestor=n.parent;inside_figure=False
  while ancestor and ancestor is not parent:
   inside_figure=inside_figure or ancestor.tag=='figure' or ancestor.has('fc-resource-card');ancestor=ancestor.parent
  if not inside_figure and n.text().strip():context.append(n)
 assert context,'Artwork needs nearby study context: '+str((i['page'],i['section']))
 cap=next(n for n in f.children if n.tag=='figcaption');title=next(n for n in cap.children if n.tag=='h3')
 assert title.text().strip()==i['title'] and i['description'] in cap.text()
 a=next(n for n in f.children if n.tag=='a');assert 'data-full-image-viewer' in a.attrs
 im=next(n for n in a.walk() if n.tag=='img')
 assert (page.parent/a.attrs['href']).resolve()==(ROOT/i['fullAsset']).resolve()
 assert im.attrs.get('alt')==i['alt'] and im.attrs.get('loading')=='lazy' and im.attrs.get('decoding')=='async'
 fullsize=image_dimensions(ROOT/i['fullAsset']);smallsize=image_dimensions(ROOT/i['asset'])
 assert fullsize==(i['width'],i['height'])
 ratio=re.search(r'--study-image-ratio:\s*(\d+)\s*/\s*(\d+)',im.attrs.get('style',''));assert ratio,'Missing reserved native image ratio'
 assert abs((int(ratio[1])/int(ratio[2]))/(smallsize[0]/smallsize[1])-1)<.01
 assert str(smallsize[0])+'w' in im.attrs.get('srcset','') and str(fullsize[0])+'w' in im.attrs.get('srcset','')
 assert (int(im.attrs['width']),int(im.attrs['height']))==fullsize
 assert abs((fullsize[0]/fullsize[1])/(smallsize[0]/smallsize[1])-1)<.01
 links=[n for n in cap.walk() if n.tag=='a'];assert [n.attrs['href'] for n in links]==i['sources']
 for link in links:
  u=urlsplit(link.attrs['href']);assert u.netloc=='www.churchofjesuschrist.org'
  if u.path.startswith('/study/general-conference/'):
   assert i['page']=='general-conference.html' and parse_qs(u.query).get('lang')==['eng'];continue
  assert u.path.startswith('/study/scriptures/') and link.has('fc-inline-scripture')
  key=u.path.split('/study/scriptures/')[1];data=json.loads((ROOT/'scripture-data'/(key+'.json')).read_text(encoding='utf-8'))
  q=parse_qs(u.query);assert q.get('lang')==['eng']
  if 'id' in q:
   sel=q['id'][0];assert re.fullmatch(r'p\d+(?:-p\d+)?',sel)
   nums=list(map(int,re.findall(r'\d+',sel)));assert 1<=nums[0]<=nums[-1]<=len(data['verses']) and u.fragment=='p'+str(nums[0])
 assert len([n for n in ns if n.tag=='script' and 'full-image-viewer.js' in n.attrs.get('src','')])==1
assert not actual
print(f'FIVE PICTURE MANIFEST QA PASS: {len(placements)} additional figures, exact assets/captions/sources, portable intrinsic checks and full viewers')
