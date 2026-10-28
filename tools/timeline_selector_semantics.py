"""Current Timeline content and navigation obligations, not visual approval.

Wrappers, classes and styles may change without changing this contract. Actual
browser geometry/visibility and repository-wide gates remain separate.
"""
from timeline_selector_check import Parser, DESTINATIONS

INTRO='Follow the life of Jesus Christ, the unfolding story of the Restoration, and the journeys of those who lived it. Choose a timeline to explore its stories, dates, and places.'
NOTE='Open a story along the way and take time with the people behind each moment.'
DESCRIPTIONS=['Explore the story of the Restoration.','Follow the Willie and Martin companies.','Walk through the Savior’s earthly ministry.','See scripture alongside world history.','Explore a nineteenth-century view of history.']
EXPECTED=' '.join(['Choose a timeline', INTRO]+sum(([name,description,'Explore timeline'] for (name,_,_),description in zip(DESTINATIONS,DESCRIPTIONS)),[])+[NOTE])
def one(nodes,predicate,label):
 found=[n for n in nodes if predicate(n)];assert len(found)==1,'Expected exactly one '+label;return found[0]
def validate(raw):
 nodes=list(Parser(raw.decode('utf8')).root.walk())
 ids=[n.attrs['id'] for n in nodes if 'id' in n.attrs];assert len(ids)==len(set(ids)),'Duplicate ID'
 section=one(nodes,lambda n:n.attrs.get('id')=='choose-timeline','timeline selector'); group=list(section.walk())
 main=one(nodes,lambda n:n.tag=='main','main landmark')
 opening='People, places, and moments of faith Timeline Explore the life of Jesus Christ, Restoration history, and the Willie and Martin handcart journeys. Follow events in order and open the linked sources to meet the people behind them.'
 assert main.content()==opening+' '+EXPECTED,'Unexpected main content'
 assert section.content()==EXPECTED,'Timeline visible selector content changed'
 assert not any('hidden' in n.attrs or n.attrs.get('aria-hidden')=='true' for n in group if n.tag!='span'),'Hidden selector content'
 cards=[n for n in group if n.tag=='article'];assert len(cards)==5,'Expected five cards'
 for i,(card,(name,href,image),description) in enumerate(zip(cards,DESTINATIONS,DESCRIPTIONS)):
  children=list(card.walk());link=one(children,lambda n:n.tag=='a','card link');title=one(children,lambda n:n.tag=='h3','card title');img=one(children,lambda n:n.tag=='img','card image');paragraph=one(children,lambda n:n.tag=='p','card description')
  assert title.content()==name and paragraph.content()==description and img.attrs.get('src')==image and img.attrs.get('alt')==''
  assert link.attrs.get('href')==href and link.attrs.get('aria-label')==('Explore '+name if i==4 else 'Explore the '+name)
  descendants=list(link.walk());assert title in descendants and img in descendants and paragraph in descendants,'Card not wholly linked'
 assert cards[-1].attrs.get('id')=='adams-1881' and ids.count('adams-1881')==1
 one(nodes,lambda n:n.tag=='h1' and n.content()=='Timeline','page title')
 one(nodes,lambda n:n.tag=='a' and n.attrs.get('data-hero-record')=='timeline' and n.attrs.get('href')=='assets/heroes/timeline.png','existing hero')
 one(nodes,lambda n:n.tag=='nav' and n.attrs.get('data-focuschrist-header')=='standard','standard header')
 one(nodes,lambda n:n.tag=='footer' and n.attrs.get('data-focuschrist-footer')=='standard','standard footer')
 one(nodes,lambda n:n.attrs.get('data-focuschrist-independence')=='footer','independence footer')
 one(nodes,lambda n:n.attrs.get('data-focuschrist-artwork-disclosure')=='footer','artwork footer')
 return True
