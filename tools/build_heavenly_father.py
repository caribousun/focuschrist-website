"""Enrich the existing Father study while preserving its original art and bookmarks."""
from pathlib import Path
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from scripture_reference_preservation_qa import check_text_reference
import html, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/heavenly-father'
PAGE=ROOT/'answers/god-our-heavenly-father.html'
esc=html.escape
data=json.loads((DATA/'content-plan.json').read_text(encoding='utf-8'))
base=BeautifulSoup((DATA/'original-page.txt').read_text(encoding='utf-8'),'html.parser')
current=BeautifulSoup(PAGE.read_text(encoding='utf-8'),'html.parser')
# Preserve Wyatt's approved text-only link instead of restoring the retired preview.
retired=base.select('[data-linked-picture-reference="modern-scripture"]')
assert len(retired)==1
approved=check_text_reference(current)
retired[0].replace_with(BeautifulSoup(str(approved),'html.parser').article)
plan=BeautifulSoup((ROOT/'answers/plan-of-salvation.html').read_text(encoding='utf-8'),'html.parser')
route='/answers/god-our-heavenly-father.html'
art={
 'adam-eve-teach':('Adam and Eve listen and speak with a son and daughter beside a shelter.','Adam and Eve share what they have learned with their children. Their family’s story joins work and worship with teaching the next generation.'),
 'kept-record':('A woman points to a written record while a child and a man listen beside her.','A child looks up from a kept record as an adult explains. Moses describes children learning to read and write so that remembrance could outlive its first witnesses.'),
 'abraham-records':('Abraham holds an open scroll while Sarah sits beside him and listens.','Abraham and Sarah sit beside an open record. Abraham describes preserving knowledge received from earlier generations for the benefit of those still to come.'),
 'teach-on-the-way':('A woman carrying a basket listens to a boy as they walk along a hillside path.','A child speaks while an adult listens along the road. Deuteronomy calls families to speak of God at home and along the way.'),
 'kirtland-readers':('Three early Latter-day Saint readers discuss an open printed book at a wooden table.','Readers gather around an open book. Early Saints studied the Lectures on Faith as they sought to understand faith in God and the testimony they had received.')}

def source(s):
 cls=' class="fc-inline-scripture"' if '/scriptures/' in s['url'] else ''
 return f'<a{cls} href="{esc(s["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>'

def prose(text):
 # Named chapter references in teaching prose must open the actual scripture reader.
 text=esc(text)
 needle='Doctrine and Covenants 130:22'
 text=text.replace(needle,'<a target="_blank" rel="noopener noreferrer" class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/130?lang=eng&amp;id=p22#p22">'+needle+'</a>')
 return text.replace('Psalm 78','<a class="fc-inline-scripture" target="_blank" rel="noopener noreferrer" href="https://www.churchofjesuschrist.org/study/scriptures/ot/ps/78?lang=eng&amp;id=p1-p8#p1">Psalm 78</a>')

def picture(c):
 aid=c['scene']; alt,caption=art[aid];prefix='/assets/page-art/heavenly-father/'+('kept-record-v2' if aid=='kept-record' else aid)
 return f'''<figure class="jj-art fc-study-visual" id="picture-hf-{aid}" data-exclusive-artwork="hf-{aid}"><a href="{prefix}-full.webp" data-full-image-viewer aria-haspopup="dialog" aria-label="Explore artwork: {esc(c['title'],quote=True)}" data-full-image-alt="{esc(alt,quote=True)}"><img src="{prefix}-800.webp" srcset="{prefix}-800.webp 800w, {prefix}-1536.webp 1536w" sizes="(max-width:700px) calc(100vw - 36px),900px" width="1536" height="1024" style="--study-image-ratio:1536/1024" loading="lazy" decoding="async" alt="{esc(alt,quote=True)}"></a><figcaption><p class="fc-study-visual-label">Explore and study</p><h3>{esc(c['title'])}</h3><p>{esc(caption)}</p><p class="fc-study-visual-sources">{' '.join(source(s) for s in c['sources'])}</p></figcaption></figure>'''

def unit(c):
 out=f'<div class="hf-study-unit" id="study-hf-{c["id"]}"><h3>{esc(c["title"])}</h3><div class="jj-reading">'+''.join('<p>'+prose(p)+'</p>' for p in c['paragraphs'])+'</div>'
 out+='<p class="fc-study-visual-sources">'+' '.join(source(s) for s in c['sources'])+'</p>'
 if c['scene'] in art:out+=picture(c)
 if c['scene']=='existing-enos-preview':
  ref=c['reference'];dest='/'+ref['owner']+'#'+ref['anchor'];asset='/assets/page-art/book-of-mormon-stories/05-enos-prayer-960.webp'
  out+=f'<article class="hf-owned-reference fc-resource-card" data-linked-picture-reference="enos-prayer"><a class="fc-resource-card__image" href="{dest}"><img src="{asset}" width="1536" height="1024" alt="Enos kneels alone in an evening woodland, with hunting equipment set aside." loading="lazy" decoding="async"></a><div class="fc-resource-card__body"><p class="fc-resource-card__kind">Continue the study</p><h3><a href="{dest}">Prayer grows beyond one person</a></h3><p>Follow Enos from remembered words into prayer for himself and for others.</p></div></article>'
 if c['scene']=='existing-restoration-preview':out+='<p><a href="who-was-joseph-smith.html">Continue with Joseph Smith’s account and the Restoration study</a></p>'
 out+=f'<details class="jj-reflection"><summary>Pause and consider</summary><p>{esc(c["reflection"])}</p></details></div>'
 return BeautifulSoup(out,'html.parser')

# Owner-expanded introduction uses the existing retained-copy reading flow.
intro_copy=base.new_tag('p', attrs={'class':'fc-page-intro-copy'})
intro_copy.string='What does it mean to know God as our Father? Read about His love through scripture and the experiences of people who sought Him, then bring your own questions to the study.'
base.select_one('.fc-topic-opening .fc-topic-subtitle').insert_after(intro_copy)

main=base.main
old={s['id']:s.extract() for s in main.find_all('section',recursive=False)}
creation=main.select_one('figure.fc-foundation-art').extract()
oldnav=main.select_one('.fc-study-nav');oldnav.decompose()
for leftover in list(main.children):
 if getattr(leftover,'name',None) not in ('div','p'):leftover.extract()
main['class']=['jj-wrap','jj-main']
base.body['class']=list(dict.fromkeys(base.body.get('class',[])+['fc-jesus-journey','fc-heavenly-father']))
old['begin-study'].h2.string='How knowledge of God reaches us'
for p in old['begin-study'].find_all('p'):
 if 'The portrait in the opening' in p.get_text():p.string='Jesus Christ invites us to know the Father. Begin with the scriptural accounts of people receiving that invitation and passing it to another generation.'
chapters=data['chapters'];byid={c['id']:c for c in chapters}
for c in chapters[:2]:old['begin-study'].append(unit(c))

def new_section(cid,title,units):
 node=base.new_tag('section',id=cid);node['class']=['jj-chapter','fc-deep-study'];node['data-connected-study']='';node['data-scripture-study']=''
 h=base.new_tag('h2');h.string=title;node.append(h)
 for c in units:node.append(unit(c))
 return node

ordered=[old['begin-study'],new_section('abraham-inherited-records','Abraham preserves what he received',[chapters[2]]),new_section('teach-along-the-way','Teaching in the ordinary hours',[chapters[3]]),new_section('inherited-words-personal-prayer','Enos seeks for himself',[chapters[4]]),new_section('the-son-shows-the-father','Jesus reveals the Father',[chapters[5]]),old['pray-to-the-father'],new_section('restoration-witness','The Restoration and learning to believe',[chapters[6],chapters[7]]),old['seek-god'],old['divine-purpose'],old['nourish-faith'],old['watch-and-study'],old['personal-reflection'],old['official-sources'],old['continue-study']]
groups={'pray-to-the-father':'the-son-shows-the-father','personal-reflection':'watch-and-study','official-sources':'watch-and-study','continue-study':'watch-and-study'}
old['seek-god'].append(creation)
for s in ordered:
 s['class']=list(dict.fromkeys(s.get('class',[])+['jj-chapter']))
 if s['id'] in groups:s['data-chapter-group']=groups[s['id']]
 h=s.find('h2',recursive=False)
 if h:h.string=re.sub(r'^\d+\.\s*','',h.get_text())
 if s['id'] not in groups:
  params=urlencode({'topic':h.get_text(),'return':route+'#'+s['id']})
  s.append(BeautifulSoup('<p class="fc-actions hf-chapter-ask"><a href="'+esc('/ask.html?'+params+'#ask-question',quote=True)+'">Ask about this chapter</a></p>','html.parser'))
nav=base.new_tag('nav');nav['class']=['jj-local-nav','fc-actions','fc-study-nav'];nav['aria-label']='Chapters in this study';nav['data-journey-subject']='God, our Heavenly Father'
for s in ordered:
 a=base.new_tag('a',href='#'+s['id']);a.string=s.h2.get_text();nav.append(a)
main.append(nav)
for s in ordered:main.append(s)
# Source inventory covers the new narrative and preserves every original source link.
source_intro=old['official-sources'].find('p',recursive=False)
source_intro.clear();source_intro.append('Read the scriptural accounts behind this study, then explore the early Saints’ discussion of faith. The Lectures on Faith links are historical readings; current teaching about the Godhead is grounded in scripture and the Church’s current study guides.')
source_list=old['official-sources'].find('ul')
for c in chapters:
 li=base.new_tag('li');li.append(c['title']+': ')
 for index,ref in enumerate(c['sources']):
  if index:li.append(' ')
  li.append(BeautifulSoup(source(ref),'html.parser'))
 source_list.append(li)
watch_intro=old['watch-and-study'].find('p',recursive=False)
watch_intro.string='Study how the Savior helps us know the Father, then consider how covenant discipleship can shape daily life. Choose a message, read its sources and keep one question to ponder.'
resources=json.loads((DATA/'resources.json').read_text(encoding='utf-8'))
nelson=next(r for r in resources if r['title']=='Overcome the World and Find Rest')
ni=old['watch-and-study'].select_one('[data-resource-key="god-overcome-world"] img')
for attr in ('width','height'):ni[attr]=str(nelson['thumbnail'][attr])
ni['src']=nelson['thumbnail']['url']
holland=next(r for r in resources if r['title']=='The Grandeur of God');thumb=holland['thumbnail'];url=esc(holland['url'],quote=True)
card=f'<article class="fc-resource-card" data-resource-key="father-grandeur-god"><a class="fc-resource-card__image" href="{url}" target="_blank" rel="noopener noreferrer"><img src="{esc(thumb["url"],quote=True)}" width="{thumb["width"]}" height="{thumb["height"]}" alt="Jeffrey R. Holland — The Grandeur of God official message preview" loading="lazy" decoding="async"></a><div class="fc-resource-card__body"><p class="fc-resource-card__kind">General Conference</p><h3><a href="{url}" target="_blank" rel="noopener noreferrer">The Grandeur of God</a></h3><p>Jeffrey R. Holland invites us to see the Father’s character in the words, compassion and sacrifice of Jesus Christ.</p><p class="fc-resource-card__source">Jeffrey R. Holland · October 2003</p></div></article>'
old['watch-and-study'].select_one('.fc-resource-grid').append(BeautifulSoup(card,'html.parser'))
for path in data['onward_paths']:
 if not old['continue-study'].find('a',href=path['href']):
  a=base.new_tag('a',href=path['href']);a['class']=['fc-button'];a.string=path['label'];old['continue-study'].select_one('.fc-actions').append(a)
# Take shared dependency versions from current checked-in consumers, not frozen history.
for tag in base.select('script[src],link[href]'):
 attr='src' if tag.name=='script' else 'href';stem=tag[attr].split('?')[0]
 match=next((n for n in current.select(f'{tag.name}[{attr}]') if n[attr].split('?')[0]==stem),None)
 if match:tag[attr]=match[attr]
for dependency in ['jesus-journey.css']:
 tag=next(n for n in plan.select('link[href]') if dependency in n['href']);base.head.append(BeautifulSoup(str(tag),'html.parser'))
script=next(n for n in plan.select('script[src]') if 'jesus-journey.js' in n['src']);base.body.append(BeautifulSoup(str(script),'html.parser'))
output=str(base)+'\n'
output=re.sub(r'<link href="(https://focuschrist.com/answers/god-our-heavenly-father.html)" rel="canonical"\s*/>',r'<link rel="canonical" href="\1">',output)
output=re.sub(r'<meta content="([^"]*)" name="description"\s*/>',r'<meta name="description" content="\1">',output)
output=re.sub(r'<script defer="" src="([^"]+)"></script>',r'<script src="\1" defer></script>',output)
if '--check' in sys.argv:
 if PAGE.read_text(encoding='utf-8')!=output:raise SystemExit('Heavenly Father page is stale')
 print('Heavenly Father builder check PASS')
else:
 PAGE.write_text(output,encoding='utf-8',newline='\n');print('Built Heavenly Father study: ten chapter groups, five new originals, existing artwork preserved')
