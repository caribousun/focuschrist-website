"""Assemble reviewed prose and explicit art placements; retain unfinished art records.

Build with --strict and run jesus_journey_qa.py before any release.
"""
from pathlib import Path
import json,re
from jesus_art_placement import place_artwork
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/jesus-journey'
def read(name):return json.loads((DATA/name).read_text(encoding='utf-8'))
def write(name,data):(DATA/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pages=[]
for name in ['branch-content-reviewed.json','parable-content-reviewed.json','parable-collections-reviewed.json']:
    if (DATA/name).exists():pages+=read(name)
by_url={p['url']:p for p in pages}
if len(by_url)!=len(pages):raise ValueError('Duplicate page URL')
registry=read('artworks.json')
plans=[]
for name in ['parable-art-plan.json','branch-art-plan.json','collection-art-plan.json']:
    if (DATA/name).exists():
        data=read(name);plans+=data['entries'] if isinstance(data,dict) else data
placements={}
paragraph_positions={a['key']:a['afterParagraph'] for a in plans if 'afterParagraph' in a}
for a in plans:
    key=a['key'];owner=a['ownerURL'];section=a['sectionId']
    if owner not in by_url:raise ValueError('Art owner not in page inventory: '+owner)
    sections={s['id']:s for s in by_url[owner]['sections']}
    if section not in sections:raise ValueError('Art section not in page: '+section)
    if key not in registry:
        registry[key]={
          'title':a['title'],'alt':a['alt'],'caption':a['caption'],'refs':a['refs'],
          'owner':owner.lstrip('/'),'section':section,'role':'body',
          'depicts_christ':a.get('depicts_christ',False),'reviewed':False,'owner_approved':False,
          'status':'planned; generation and visual review required',
          'asset':'assets/page-art/jesus-journey/'+key+'-full.webp',
          'thumbnail':'assets/page-art/jesus-journey/'+key+'-960.webp','original':key+'.png'}
    if registry[key]['owner']!=owner.lstrip('/'):raise ValueError('Conflicting art ownership '+key)
    registry[key]['section']=section
    placements.setdefault((owner,section),[]).append(key)
    patch=a.get('section_patch')
    if patch:raise ValueError('Review and apply section patch to source prose before assembling: '+key)
for (url,section),keys in placements.items():
    sec=next(s for s in by_url[url]['sections'] if s['id']==section)
    sec['blocks']=place_artwork(sec['blocks'],keys,paragraph_positions)
collections=[p for p in pages if p.get('kind')=='collection']
if not collections:
    collection_names={'mercy','neighbor','hearing','kingdom','stewardship','watchfulness'}
    collections=[p for p in pages if Path(p['url']).stem in collection_names]
teacher=by_url.get('/jesus-christ/teachings-and-parables.html')
if teacher and collections:
    teacher['sections'].insert(0,{'id':'parable-paths','title':'Explore the parables of Jesus','eyebrow':'Six paths through His teaching','blocks':[
      'Jesus teaches through stories and comparisons drawn from ordinary life. These six paths help you explore their settings, notice their questions, and consider how to receive His word. Read each teaching in its Gospel context; the themes are study aids.',
      {'cards':[[p['url'],p['title'],p['intro']] for p in collections]},
      'The library includes 47 main parables and judgment pictures, together with 16 related comparisons and allegories. Counts vary according to how short comparisons are grouped. These labels describe this study library, not an official fixed count.']})
def exact_refs(value):
    if isinstance(value,dict):
        for key,v in value.items():
            if key=='refs':
                for ref in v:
                    match=re.search(r':([0-9,\s–-]+)$',ref[1])
                    if match:
                        selected=match[1].replace('–','-').replace(' ','')
                        if re.fullmatch(r'\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*',selected):ref[2]=selected
            else:exact_refs(v)
    elif isinstance(value,list):
        for v in value:exact_refs(v)
exact_refs(pages);exact_refs(registry)
write('pages.json',pages);write('artworks.json',registry)
main=read('main-content.json');exact_refs(main);write('main-content.json',main)
print(f'Assembled {len(pages)} studies and {len(plans)} planned body scenes. Unfinished scenes remain explicit.')
