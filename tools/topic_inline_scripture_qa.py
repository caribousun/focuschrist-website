#!/usr/bin/env python3
"""Check real topic DOM, canonical chapter identity, and available verse selections."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,unquote
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
def nodes(file):
 d=Document();d.feed(file.read_text(encoding='utf-8'));return list(d.root.walk())
def clean(text):return ' '.join(text.split())
EMMA_STORIES = ('history/emma-elect-lady.html', 'history/emma-hymns.html', 'history/emma-last-testimony.html', 'history/emma-relief-society.html', 'history/emma-winter-crossing.html')
HISTORICAL_STORIES = ('history/john-tanner.html', 'history/eleazer-miller.html', 'history/john-rowe-moyle.html', 'history/emma-hale-smith.html')

def checked_history_routes(actual):
 assert len(actual)==len(set(actual)), "Duplicate history owner"
 assert set(actual)==set(HISTORICAL_STORIES)|set(EMMA_STORIES), "Exact four historical and five Emma owners required"
 return list(HISTORICAL_STORIES)+list(EMMA_STORIES)

def check_scriptures(root, paths, featured):
 ROOT=root
 catalog={}
 for file in (ROOT/'scripture-data').rglob('*.json'):
  data=json.loads(file.read_text(encoding='utf-8'))
  if 'verses' not in data:continue
  key=file.relative_to(ROOT/'scripture-data').as_posix()[:-5]
  book=re.sub(r'\s+\d+$','',clean(data['title']))
  catalog[book]=key.rsplit('/',1)[0]
 catalog['D&C']='dc-testament/dc';catalog['Psalms']='ot/ps'
 books='|'.join(re.escape(k) for k in sorted(catalog,key=len,reverse=True))
 reference=re.compile(r'(?<![\w])('+books+r')\s+(\d+)(?::(\d+(?:[–-]\d+)?(?:\s*,\s*\d+(?:[–-]\d+)?)*))?')
 count=0
 for path in paths:
  ns=nodes(ROOT/path);main=next(n for n in ns if n.tag=='main')
  for node in main.walk():
   parent=node;linked=False
   while parent:
    linked=linked or parent.tag=='a';parent=parent.parent
   if not linked:
    assert not reference.search(clean(' '.join(node.words))),path+': explicit scripture remains unlinked: '+' '.join(node.words)
   if node.tag=='a':assert not any(n.tag=='a' for n in node.walk() if n is not node),path+': nested anchor'
   if not (node.has('fc-inline-scripture') or ((path in featured or path in EMMA_STORIES) and node.tag=='a' and re.search(r'/study/scriptures/(?:ot|nt|bofm|dc-testament|pgp)/[^/]+/\d+',node.attrs.get('href','')))):continue
   count+=1;u=urlsplit(node.attrs['href']);prefix='/study/scriptures/'
   assert u.netloc=='www.churchofjesuschrist.org' and u.path.startswith(prefix)
   key=u.path[len(prefix):];file=ROOT/'scripture-data'/(key+'.json');assert file.is_file(),path+': unavailable scripture chapter '+key
   data=json.loads(file.read_text(encoding='utf-8'));params=parse_qs(u.query)
   assert params.get('lang')==['eng']
   if params.get('id'):
    selection=params['id'][0];assert re.fullmatch(r'p\d+(?:-p\d+)?(?:,p\d+(?:-p\d+)?)*',selection)
    numbers=list(map(int,re.findall(r'\d+',selection)))
    for part in selection.split(','):
     bounds=list(map(int,re.findall(r'\d+',part)));assert 1<=bounds[0]<=bounds[-1]<=len(data['verses'])
    assert u.fragment=='p'+str(numbers[0])
   match=reference.search(clean(node.text()))
   if match:
    assert key==catalog[match[1]]+'/'+match[2],path+': scripture label links to wrong chapter'
    if match[3] and (node.has('fc-inline-scripture') or params.get('id') or path in EMMA_STORIES):
     expected=','.join('p'+part.strip().replace('–','-').replace('-','-p') for part in match[3].split(','))
     assert params.get('id')==[expected],path+': verse selection differs from label'
 return count

def main():
 paths=['index.html']+[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'answers').glob('*.html'))]+['general-conference.html']
 assert len(paths)==27 and {'answers/abrahamic-covenant.html','answers/holy-ghost.html','answers/plan-of-salvation.html','answers/race-priesthood-and-temple-blessings.html'}.issubset(paths), 'Home and all permanent topic studies must be checked'
 # Discover the Featured Art destinations from their public gallery links. Body prose
 # was previously outside this gate, so missing citations passed picture-panel QA.
 featured=sorted({n.attrs['href'] for n in nodes(ROOT/'art.html') if n.tag=='a' and 'data-artwork-detail' in n.attrs and n.attrs.get('href','').startswith('art-study/')})
 assert len(featured)==4, 'Check every Featured Art study destination'
 paths+=featured
 history_stories = ['history/john-tanner.html', 'history/eleazer-miller.html', 'history/john-rowe-moyle.html']
 emma_story = 'history/emma-hale-smith.html'
 paths += checked_history_routes([p.relative_to(ROOT).as_posix() for p in (ROOT/'history').glob('*.html')])
 count=check_scriptures(ROOT, paths, featured)
 print(f"TOPIC INLINE SCRIPTURE QA PASS: {len(paths)} checked bodies, {count} scripture links, canonical chapters, exact verse selections, no nested anchors")

if __name__=="__main__": main()
