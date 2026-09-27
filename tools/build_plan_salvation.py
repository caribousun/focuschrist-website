"""Build only the Plan of Salvation page from reviewed content and resource inputs."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json, html, re
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/plan-of-salvation'
esc=html.escape
content=json.loads((DATA/'content.json').read_text(encoding='utf-8'))
resources=json.loads((DATA/'resources.json').read_text(encoding='utf-8'))['resources']
sources={s['id']:s for s in content['sources']}
base=BeautifulSoup((ROOT/'answers/holy-ghost.html').read_text(encoding='utf-8'),'html.parser')
route='/answers/plan-of-salvation.html'
ASSET={'belong':'newborn-v2','tend':'stewardship','care':'bedside-care','purpose':'moses-purpose','return':'return-v2','begin':'begin-v2'}
PLANNED_ALT={
'purpose':'Moses looks outward from a mountain.',
'earth':'Seed-bearing plants and fruit grow above rich soil.',
'labor':'Adam and Eve work together to cultivate the earth.',
'choose':'Lehi speaks with his son Jacob.',
'return':'Alma speaks directly with his son Corianton.',
'bore':'Two readers discuss an open scroll together.',
'burdens':'Members of a community share food and clothing.',
'small-voices':'A child shows a drawing to an attentive parent and grandparent.',
'between':'Two relatives look through family photographs together.',
'redemption-dead':'Joseph F. Smith sits with an open Bible.',
'rise':'Paul speaks to a gathering in Athens.',
'life-with-god':'Adults walk outside a temple.',
'long-view':'A person sets aside a phone to listen to a family member.',
'begin':'Lamoni’s father kneels in prayer while Aaron stands nearby.'}
CAPTIONS={'belong': 'A child is welcomed into mortal life. Abraham’s account invites us to see each person as someone whose story began before birth.', 'purpose': 'Moses looks out from the mountain. As he asks why the earth and its people exist, God answers with His purpose: our immortality and eternal life.', 'earth': 'Seedlings take root and a branch bears fruit. The Creation account describes an earth where life can grow and be sustained.', 'tend': 'An adult and child care for a young tree together. Receiving the earth as a gift also gives us work to do for the life around us.', 'labor': 'Adam and Eve work the soil together. Their story continues beyond Eden through shared labor, family life and learning to call upon God.', 'choose': 'Lehi speaks with Jacob near the end of his life. His counsel connects agency with the Redeemer who makes freedom possible.', 'care': 'A nurse listens while a relative holds the patient’s hand. Christ’s knowledge of suffering gives us reason to turn toward people in pain with care.', 'return': 'Alma speaks to Corianton with an open hand. He addresses his son’s wrongdoing without leaving him without a way to repent and return.', 'bore': 'Two readers discuss an open scroll together. Isaiah’s words about the suffering servant help us study the Savior’s willingness to bear sorrow and sin.', 'burdens': 'Food and cloth pass from one person to another. The people gathered by Alma shared according to need as they learned to live their covenant together.', 'small-voices': 'A child shows her drawing to adults who stop to listen. The account in Third Nephi reminds us that children have a place in a community gathered around Christ.', 'between': 'Two relatives preserve a family photograph together. Alma’s teaching offers hope that a person’s life continues beyond death while resurrection is still ahead.', 'redemption-dead': 'Joseph F. Smith sits with an open Bible. His account begins with pondering the scriptures and leads to a wider understanding of Christ’s work among the dead.', 'life-with-god': 'People greet one another on the temple grounds. Covenants invite us to prepare for life with God through the choices and relationships of daily life.', 'long-view': 'A father sets aside his phone to listen to his daughter. An eternal perspective can begin with giving someone our attention today.', 'begin': 'Lamoni’s father kneels in prayer while Aaron stands nearby. His willingness to give up his sins turns a question about eternal life into a personal response to God.'}
review={}
def collect(x):
    if isinstance(x,dict):
        if x.get('id') and x.get('alt'):review[x['id']]=x
        for v in x.values():collect(v)
    elif isinstance(x,list):
        for v in x:collect(v)
for f in DATA.glob('*.json'):collect(json.loads(f.read_text(encoding='utf-8-sig')))
def link(s):
    cls=' class="fc-inline-scripture"' if '/scriptures/' in s['url'] else ''
    return f'<a{cls} href="{esc(s["url"],quote=True)}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>'
def paragraph(text):
    rendered=esc(text)
    rendered=rendered.replace('Doctrine and Covenants 76', '<a class="fc-inline-scripture" href="'+esc(sources['glory']['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">Doctrine and Covenants 76</a>')
    rendered=rendered.replace('John 20', '<a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/nt/john/20?lang=eng" target="_blank" rel="noopener noreferrer">John 20</a>')
    return rendered

def refs(ids):return ' '.join(link(sources[k]) for k in ids)
def ask(topic,anchor):
    return '/ask.html?'+urlencode({'topic':topic,'return':route+'#'+anchor})+'#ask-question'
missing=[]
def picture(u):
    aid=ASSET.get(u['id'],u['id'])
    prefix='/assets/page-art/plan-of-salvation/'+aid
    record=review.get(aid,{})
    alt=record.get('alt',PLANNED_ALT.get(u['id'],u['title']))
    for suffix in ('800','1536','full'):
        path=prefix+'-'+suffix+'.webp'
        if not (ROOT/path.lstrip('/')).exists():missing.append(path)
    from PIL import Image
    small=ROOT/(prefix+'-800.webp').lstrip('/')
    small_width=Image.open(small).width if small.exists() else 800
    caption=CAPTIONS[u['id']]
    return f'''<figure class="jj-art fc-study-visual" id="picture-pos-{u['id']}" data-exclusive-artwork="pos-{u['id']}"><a href="{prefix}-full.webp" data-full-image-viewer aria-haspopup="dialog" aria-label="Explore artwork: {esc(u['title'],quote=True)}" data-full-image-alt="{esc(alt,quote=True)}"><img src="{prefix}-800.webp" srcset="{prefix}-800.webp {small_width}w, {prefix}-1536.webp 1536w" sizes="(max-width:700px) calc(100vw - 36px),900px" width="1536" height="1024" style="--study-image-ratio:1536/1024" loading="lazy" decoding="async" alt="{esc(alt,quote=True)}"></a><figcaption><p class="fc-study-visual-label">Explore and study</p><h3>{esc(u['title'])}</h3><p>{esc(caption)}</p><p class="fc-study-visual-sources">{refs(u['source_ids'])}</p></figcaption></figure>'''
def reference(u):
    path=ROOT/u['art']['reference_owner']
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    needle=u['art'].get('reference_title') or ('We saw Him' if u['id']=='glory' else 'He eats before them')
    title=next((x for x in soup.find_all(['h2','h3','h4']) if x.get_text(' ',strip=True)==needle),None)
    if not title:raise ValueError('Missing registered reference '+needle)
    fig=title.find_parent('figure')
    if not fig:raise ValueError('Reference is not in owning figure')
    img=fig.find('img');dest='/'+u['art']['reference_owner']+'#'+u['art'].get('reference_anchor',fig.get('id','main-content'))
    src=img['src']
    if not src.startswith('/'):src='/'+str((Path(u['art']['reference_owner']).parent/src).as_posix())
    bridge={'known':'The risen Jesus who ate with His disciples is also the Son entrusted with judgment. Return to their witness of His living body.','glory':'Joseph Smith and Sidney Rigdon began their account with testimony of the living Christ. Read that witness alongside the promises of glory.','rise':'Paul invites the people of Athens to seek the God who gives life. Follow his words toward the promise of resurrection and judgment.'}[u['id']]
    return f'''<article class="fc-resource-card pos-owned-reference"><a href="{esc(dest)}" class="fc-resource-card__image" aria-label="Continue to {esc(needle)} in its study"><img src="{esc(src)}" alt="{esc(img.get('alt',''),quote=True)}" width="{img.get('width','1536')}" height="{img.get('height','1024')}" loading="lazy" decoding="async"></a><div class="fc-resource-card__body"><p class="fc-resource-card__kind">Continue the study</p><h3><a href="{esc(dest)}">{esc(needle)}</a></h3><p>{esc(bridge)}</p></div></article>'''
head=base.head
for el in list(head.select('link[href*="holy-ghost-video"],style')):el.decompose()
head.title.string='The Plan of Salvation | focusChrist'
description='Follow the plan of salvation through scripture: life before birth, Creation, agency, Jesus Christ, covenants, resurrection and eternal life.'
head.find('link',rel='canonical')['href']='https://focuschrist.com'+route
for tag in head.find_all('meta'):
    key=tag.get('name',tag.get('property',''))
    if key in ('description','og:description','twitter:description'):tag['content']=description
    if key in ('og:title','twitter:title'):tag['content']='The Plan of Salvation | focusChrist'
    if key=='og:url':tag['content']='https://focuschrist.com'+route
    if key=='og:image':tag['content']='https://focuschrist.com/assets/heroes/plan-of-salvation-hero-full.webp'
style=base.new_tag('link',rel='stylesheet',href='../plan-of-salvation.css?v=20260927-study-1');head.append(style)
nav=str(base.body.find('nav',recursive=False))
hero=f'''<header class="fc-topic-opening" aria-labelledby="plan-page-title"><figure class="pos-opening-art" id="picture-pos-hero" data-exclusive-artwork="pos-hero"><a class="fc-visual-hero fc-visual-hero--christ fc-visual-hero--portrait fc-answer-detail-hero fc-topic-unique-hero" href="/assets/heroes/plan-of-salvation-hero-full.webp" data-hero-viewer data-hero-record="plan-of-salvation" data-hero-ask="{esc(ask('Jesus Christ and eternal life','redeemer'),quote=True)}" data-full-image-alt="Jesus lifts His eyes toward heaven as He prays to the Father." aria-label="Explore artwork: Jesus prays for eternal life" aria-haspopup="dialog" style="--topic-hero-desktop:url('/assets/heroes/plan-of-salvation-hero-1600.webp');--topic-hero-mobile:url('/assets/heroes/plan-of-salvation-hero-mobile.webp')"></a></figure><section class="fc-page-intro" aria-labelledby="plan-page-title"><div class="fc-container--standard"><p class="fc-eyebrow">Answers · Foundational study</p><h1 class="fc-display" id="plan-page-title">The Plan of Salvation</h1><p class="fc-topic-subtitle">{esc(content['subtitle'])}</p><a class="fc-scroll-cue" href="#main-content" aria-label="Continue to the Plan of Salvation study"><span>Continue</span><span aria-hidden="true">↓</span></a></div></section></header>'''
main=['<main class="jj-wrap jj-main" id="main-content">','<div class="jj-reading pos-introduction">'+''.join('<p>'+esc(p)+'</p>' for p in content['introduction'])+'</div>','<nav class="jj-local-nav fc-actions fc-study-nav" aria-label="In this study" data-journey-subject="The Plan of Salvation">']
main+=['<a href="#'+c['id']+'">'+esc(c['title'])+'</a>' for c in content['chapters']]
main+=['</nav>']
for c in content['chapters']:
    main.append(f'<section class="jj-chapter" id="{c["id"]}"><h2>{esc(c["title"])}</h2>')
    for u in c['units']:
        main.append(f'<div class="pos-study-unit" id="study-{u["id"]}"><h3>{esc(u["title"])}</h3><div class="jj-reading">'+''.join('<p>'+paragraph(p)+'</p>' for p in u['paragraphs'])+'</div>')
        main.append('<p class="fc-study-visual-sources">'+refs(u['source_ids'])+'</p>')
        kind=u['art']['type']
        if kind=='existing-owner-reference':main.append(reference(u))
        elif kind!='hero-reference':main.append(picture(u))
        main.append(f'<details class="jj-reflection"><summary>Pause and consider</summary><p>{esc(u["reflection"])}</p></details></div>')
    if c['number']==10:
        main.append('<h3>Keep learning with these messages</h3><div class="fc-resource-grid">')
        for r in resources:
            t=r['thumbnail']
            main.append(f'''<article class="fc-resource-card" data-resource-key="{esc(r['id'])}"><a class="fc-resource-card__image" href="{esc(r['url'],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Open {esc(r['title'],quote=True)}"><img src="{esc(t['url'],quote=True)}" width="{t['width']}" height="{t['height']}" alt="{esc(r['title'],quote=True)} official message preview" loading="lazy" decoding="async"><span class="fc-resource-card__play" aria-hidden="true">▶</span></a><div class="fc-resource-card__body"><p class="fc-resource-card__kind">{esc(r['kind'])}</p><h3><a href="{esc(r['url'],quote=True)}" target="_blank" rel="noopener noreferrer">{esc(r['title'])}</a></h3><p>{paragraph(r['suggested_invitation'])}</p><p class="fc-resource-card__source">{esc(r['speaker'])} · {esc(r['date'])}</p></div></article>''')
        main.append('</div>')
    main.append('<p class="fc-actions"><a href="'+esc(ask(c['title'],c['id']),quote=True)+'">Ask about this chapter</a></p></section>')
main.append('<nav class="jj-actions fc-actions" id="continue-study" aria-label="Continue studying">')
for p in content['onward_paths']:main.append(f'<a href="{esc(p["href"],quote=True)}">{esc(p["label"])}</a>')
main.append('<a href="/answers.html">Answers Library</a></nav></main>')
scripts=[]
for el in base.body.find_all('script',recursive=False):
    if 'holy-ghost-video' not in el.get('src',''):scripts.append(str(el))
output='<!DOCTYPE html>\n<html lang="en">'+str(head)+'<body class="fc-site fc-answer-depth fc-topic-page fc-jesus-journey">'+nav+hero+'\n'.join(main)+str(base.body.footer)+''.join(scripts)+'</body></html>\n'
# Preserve exact standard snippets required by the shared HTML contract.
output=re.sub(r'<link href="(https://focuschrist.com/answers/plan-of-salvation.html)" rel="canonical"\s*/>',r'<link rel="canonical" href="\1">',output)
output=re.sub(r'<meta content="([^"]*)" name="description"\s*/>',r'<meta name="description" content="\1">',output)
output=re.sub(r'<script defer="" src="([^"]+)"></script>',r'<script src="\1" defer></script>',output)
(ROOT/'answers/plan-of-salvation.html').write_text(output,encoding='utf-8',newline='\n')
print(json.dumps({'page':'answers/plan-of-salvation.html','chapters':len(content['chapters']),'new_body_figures':sum(u['art']['type'] not in ('hero-reference','existing-owner-reference') for c in content['chapters'] for u in c['units']),'reference_previews':sum(u['art']['type']=='existing-owner-reference' for c in content['chapters'] for u in c['units']),'missing_delivery_paths':missing},indent=2))
