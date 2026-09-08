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
catalog={}
for file in (ROOT/'scripture-data').rglob('*.json'):
 data=json.loads(file.read_text(encoding='utf-8'))
 if 'verses' not in data:continue
 key=file.relative_to(ROOT/'scripture-data').as_posix()[:-5]
 book=re.sub(r'\s+\d+$','',clean(data['title']))
 catalog[book]=key.rsplit('/',1)[0]
catalog['D&C']='dc-testament/dc';catalog['Psalms']='ot/ps'
books='|'.join(re.escape(k) for k in sorted(catalog,key=len,reverse=True))
reference=re.compile(r'(?<![\w])('+books+r')\s+(\d+)(?::(\d+)(?:[–-](\d+))?)?')
paths=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'answers').glob('*.html'))]+['general-conference.html']
assert len(paths)==19, 'All permanent topic studies must be checked'
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
  if not node.has('fc-inline-scripture'):continue
  count+=1;u=urlsplit(node.attrs['href']);prefix='/study/scriptures/'
  assert u.netloc=='www.churchofjesuschrist.org' and u.path.startswith(prefix)
  key=u.path[len(prefix):];file=ROOT/'scripture-data'/(key+'.json');assert file.is_file(),path+': unavailable scripture chapter '+key
  data=json.loads(file.read_text(encoding='utf-8'));params=parse_qs(u.query)
  assert params.get('lang')==['eng']
  if params.get('id'):
   selection=params['id'][0];assert re.fullmatch(r'p\d+(?:-p\d+)?',selection)
   numbers=list(map(int,re.findall(r'\d+',selection)));assert 1<=numbers[0]<=numbers[-1]<=len(data['verses'])
   assert u.fragment=='p'+str(numbers[0])
  match=reference.search(clean(node.text()))
  if match:
   assert key==catalog[match[1]]+'/'+match[2],path+': scripture label links to wrong chapter'
   if match[3] and (node.has('fc-inline-scripture') or params.get('id')):assert params.get('id')==['p'+match[3]+('-p'+match[4] if match[4] else '')],path+': verse selection differs from label'
print(f'TOPIC INLINE SCRIPTURE QA PASS: all19 topic destinations, {count} scripture links, canonical chapters, exact verse selections, no nested anchors')
