#!/usr/bin/env python3
"""Gate dedicated topic destinations, complete openings, study content and migration."""
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 d=Document();d.feed(p.read_text(encoding="utf-8"));return list(d.root.walk())
errors=[]
nodes=read(ROOT/'answers.html')
pills=next(n for n in nodes if n.has('fc-answers-jump-links'))
links=[n for n in pills.walk() if n.tag=='a']
assert len(links)==16
assert len({n.attrs['href'] for n in links})==16
for link in links:
 href=link.attrs['href'];u=urlsplit(href)
 assert not u.fragment and not u.scheme, 'Every topic opens a dedicated local page'
 p=ROOT/u.path;ns=read(p)
 headings=[n for n in ns if n.tag=='h1']
 assert len(headings)==1 and headings[0].text().strip()==link.text().strip(), href+': heading matches topic'
 if p.name=='general-conference.html':continue
 opening=next(n for n in ns if n.has('fc-topic-opening'))
 assert any(n.has('fc-visual-hero') for n in opening.walk()),href+': image in first screen'
 assert any(n.has('fc-page-intro') for n in opening.walk()),href+': title in first screen'
 assert any(n.has('fc-scroll-cue') and n.attrs.get('href')=='#main-content' for n in opening.walk()),href+': continue action'
 assert any(n.tag=='body' and n.has('fc-topic-page') for n in ns)
 assert sum('topic-study-pages.css?' in n.attrs.get('href','') for n in ns)==1
 main=next(n for n in ns if n.tag=='main')
 assert main.order>opening.order and len(main.text().split())>200,href+': substantive study after opening'
 hero=next(n for n in ns if 'data-hero-viewer' in n.attrs)
 return_path=parse_qs(urlsplit(hero.attrs['data-hero-ask']).query)['return'][0]
 assert urlsplit(return_path).path=='/'+href,href+': art study returns to same page'
stand=read(ROOT/'answers/stand-forever.html');look=read(ROOT/'answers/look-unto-me-doctrine-and-covenants-6-36.html')
keys={'stand-lord-i-believe','stand-faith-choice','stand-spiritual-momentum'}
assert keys <= {n.attrs.get('data-resource-key') for n in stand}
assert not keys & {n.attrs.get('data-resource-key') for n in look},'Stand Forever videos moved, not duplicated'
assert any(n.attrs.get('href')=='stand-forever.html' for n in look),'original page preserves a study pathway'
grief=read(ROOT/'answers/grief-and-faith.html')
for slug in ['nt/john/11','bofm/alma/7','bofm/mosiah/18']:
 assert any('churchofjesuschrist.org/study/scriptures/'+slug in n.attrs.get('href','') for n in grief)
assert any('data-full-image-viewer' in n.attrs for n in grief),'approved grief artwork remains viewable'
assert not any('/media/video/' in n.attrs.get('href','') for n in grief),'reading-only grief study has no duplicate video'
print('TOPIC STUDY PAGES QA PASS: 16 distinct pill destinations; complete openings, same-page hero return, and source-preserving migrations')
