#!/usr/bin/env python3
"""Focused source check for this Timeline selector; not a site/release gate.

Use --changed with every changed path since the validated base. Unknown/shared
paths fail closed with BROAD VALIDATION REQUIRED. --baseline is the exact base
Timeline file, e.g. `git show BASE:timeline.html > /tmp/timeline-base.html`.
"""
import argparse, hashlib, json, sys
from html.parser import HTMLParser
from pathlib import Path

BASE_SHA256 = 'c910ae58c2f8feccf1d59f44b154d31f224436b79538e86bf73774c65b0b8c4c'
ALLOWED = {'timeline.html','timeline.css','tools/timeline_selector_check.py','tools/timeline_selector_browser_qa.js','docs/timeline-selector-dependencies.json'}
DESTINATIONS = [
 ('Church History Timeline','timelines/latter-day-saint-church-history-timeline.html','assets/timelines/church-history-grove.webp'),
 ('Willie and Martin Handcart Journey','timelines/willie-and-martin-handcart-map.html','assets/timelines/handcart-journey.webp'),
 ('Life of Christ Timeline','timelines/life-of-christ-journey-map.html','assets/page-art/jesus-journey/mm-twelve-depart-960.webp'),
 ('World & Scripture Timeline','timelines/world-and-scripture-timeline.html','assets/page-art/answers-study/answers-two-witnesses-960.webp'),
 ("Adams' 1881 Chart of History",'timelines/adams-1881-introduction.html','assets/adams-chart/adams-16-0-0.jpg'),
]
class Node:
 def __init__(self, tag='', attrs=(), parent=None): self.tag,self.attrs,self.parent,self.children,self.text=tag,dict(attrs),parent,[],''
 def walk(self):
  yield self
  for c in self.children: yield from c.walk()
 def content(self): return ' '.join((self.text+' '+' '.join(c.content() for c in self.children)).split())
class Parser(HTMLParser):
 void=set('area base br col embed hr img input link meta param source track wbr'.split())
 def __init__(self, text):
  super().__init__(convert_charrefs=True); self.root=Node();self.stack=[self.root];self.feed(text)
 def handle_starttag(self, tag, attrs):
  n=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(n)
  if tag not in self.void:self.stack.append(n)
 def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:del self.stack[i:];break
 def handle_data(self,data):self.stack[-1].text+=data

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'));ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--changed',nargs='+',required=True);a=ap.parse_args()
 unknown=set(a.changed)-ALLOWED
 if unknown: print('BROAD VALIDATION REQUIRED: unknown/shared changes:',', '.join(sorted(unknown)));return 2
 if not {'timeline.html','timeline.css'}<=set(a.changed): print('BROAD VALIDATION REQUIRED: incomplete change list');return 2
 raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA256,'unrecognized baseline bytes'
 old=raw.decode();new=(a.root/'timeline.html').read_text();css=(a.root/'timeline.css').read_text()
 # Everything outside the requested section remains byte-identical, other than the CSS version.
 prefix_old=old.split('<section id="choose-timeline"',1)[0].replace('timeline.css?v=20261020-world-scripture-1','timeline.css?v=20261028-timeline-card-center-1')
 assert new.split('<section id="choose-timeline"',1)[0]==prefix_old,'opening/chrome changed'
 note='<p class="fc-timeline-note">Open a story along the way and take time with the people behind each moment.</p>'
 assert new.count(note)==1 and new.split(note,1)[1].split('</main>',1)[0]=='\n</div></section>\n','unexpected markup after selector'
 assert new.split('</main>',1)[1]==old.split('</main>',1)[1],'footer changed'
 nodes=list(Parser(new).root.walk()); ids=[n.attrs['id'] for n in nodes if 'id' in n.attrs];assert len(ids)==len(set(ids)),'duplicate IDs'
 sections=[n for n in nodes if n.attrs.get('id')=='choose-timeline'];assert len(sections)==1
 cards=[n for n in sections[0].walk() if n.tag=='article' and 'fc-timeline-choice' in n.attrs.get('class','').split()];assert len(cards)==5
 for card,(name,href,image) in zip(cards,DESTINATIONS):
  descendants=list(card.walk()); links=[x for x in descendants if x.tag=='a'];imgs=[x for x in descendants if x.tag=='img'];titles=[x for x in descendants if x.tag=='h3']
  assert len(links)==len(imgs)==len(titles)==1 and links[0].attrs.get('href')==href
  assert links[0].attrs.get('aria-label')=='Explore the '+name or (name.startswith('Adams') and links[0].attrs.get('aria-label')=='Explore '+name)
  assert titles[0].content()==name and imgs[0].attrs.get('src')==image and imgs[0].attrs.get('alt')==''
  assert links[0] in list(card.walk()) and imgs[0] in list(links[0].walk()) and titles[0] in list(links[0].walk())
 assert cards[-1].attrs.get('id')=='adams-1881' and ids.count('adams-1881')==1
 assert 'fc-adams-timeline-card' not in new and 'fc-actions fc-timeline-choices' not in new
 assert all(t in css for t in ('flex-wrap: wrap','justify-content: center','--fc-panel-border','--fc-panel-fill','--fc-radius','focus-visible','@media (max-width: 700px)'))
 assert 'display: none' not in css and 'visibility: hidden' not in css
 print(json.dumps({'status':'PASS','scope':'five cards, links, image references, landmark, unchanged opening/footer, scoped CSS; source only','changed':a.changed}))
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print('FAIL:',e,file=sys.stderr);sys.exit(1)
