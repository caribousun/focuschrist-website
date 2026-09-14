from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
errors=[];pages=0;external=0
for p in ROOT.rglob('*.html'):
 if set(p.relative_to(ROOT).parts)&{'docs','tools','.git','node_modules'}:continue
 d=Document();d.feed(p.read_text(encoding='utf-8'));nodes=list(d.root.walk())
 nav=next((n for n in nodes if n.has('nav-links')),None)
 if nav:
  pages+=1;center=[n for n in nav.walk() if n.has('fc-nav-atonement')]
  links={n.attrs.get('href','').split('/')[-1] for n in nav.walk() if n.tag=='a'}
  if not {'index.html','ask.html','answers.html','art.html','missionary.html','church-history.html','pioneers.html','watch.html','about.html'}<=links:errors.append(str(p)+': missing core navigation link')
  for marker in ('missionary','history','watch'):
   if not any('data-focuschrist-primary-'+marker in n.attrs for n in nav.walk()):errors.append(str(p)+': missing runtime insertion guard '+marker)
  if len(center)!=1 or not center[0].attrs.get('href','').endswith('atonement.html'):errors.append(str(p)+': missing unique center destination')
  if len([n for n in nav.children if n.has('fc-nav-side')])!=2:errors.append(str(p)+': missing balanced navigation wings')
 for a in (n for n in nodes if n.tag=='a'):
  u=urlsplit(a.attrs.get('href',''))
  if u.scheme not in {'http','https'} or u.hostname in {'focuschrist.com','www.focuschrist.com'}:continue
  external+=1
  if a.attrs.get('target')!='_blank' or not {'noopener','noreferrer'}<=set(a.attrs.get('rel','').split()):errors.append(str(p)+': external destination must open safely in new tab')
assert not errors,'\n'.join(errors)
print(f'NAVIGATION QA PASS: {pages} centered headers, {external} external links')
