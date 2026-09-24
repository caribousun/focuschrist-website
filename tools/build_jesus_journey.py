"""Build the explicitly authorized nested Jesus Christ studies from reviewed content.

No page is published by this builder. --strict rejects missing or unreviewed art.
Sources and prose need semantic review; a successful build does not prove doctrine.
"""
from pathlib import Path
import argparse, hashlib, html, json, re

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/jesus-journey'
PARENT='/answers/jesus-christ-latter-day-saint-beliefs.html'
ORIGIN='https://focuschrist.com'
def E(value):
    text=str(value)
    if re.search(r'[\u00c2\u00c3]|\u00e2[\u0080-\u00bf\u2000-\u2122]|\ufffd',text):
        raise ValueError('Corrupted visitor-facing text: '+repr(text))
    return html.escape(text,quote=True)

def scripture(ref):
    path,label,verses=ref
    url='https://www.churchofjesuschrist.org/study/scriptures/'+path+'?lang=eng'
    if verses:
        if not re.fullmatch(r'\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*',verses):raise ValueError('Invalid verse selection '+verses)
        start=re.split(r'[-,]',verses)[0]; selection=','.join('p'+part.replace('-','-p') for part in verses.split(','))
        url+='&id='+selection+'#p'+start
    return f'<a class="fc-inline-scripture" href="{E(url)}" target="_blank" rel="noopener noreferrer">{E(label)}</a>'

def prose(text,refs):
    # Citation tokens are explicit; never guess reference ranges from prose.
    value=E(text)
    for i,ref in enumerate(refs):value=value.replace('{'+str(i)+'}',scripture(ref))
    if re.search(r'\{\d+\}',value):raise ValueError('Unresolved scripture token: '+text)
    return value

def validate_artwork_review(key, a, data=DATA, check_corrections=True):
    """Require an accepted verdict for these exact original pixels, never a sibling candidate."""
    record=a.get('review_record')
    if not record or Path(record).name != record or not (data/record).is_file():
        raise ValueError('Missing pixel review '+key)
    original=a.get('original_sha256','')
    if not re.fullmatch(r'[0-9a-f]{64}',original):raise ValueError('Missing original lineage '+key)
    corrections=data/'owner-corrections.json'
    if check_corrections and corrections.is_file():
        rejected=json.loads(corrections.read_text(encoding='utf-8')).get('rejections',[])
        if any(item.get('sha256')==original for item in rejected):
            raise ValueError('Owner-rejected original '+key)
    raw=(data/record).read_bytes()
    try:review=json.loads(raw)
    except (ValueError,UnicodeError) as exc:raise ValueError('Invalid pixel review '+key) from exc
    candidates=review.get('entries',review.get('candidates',[]))
    filename=Path(a.get('generated_path','').replace('\\','/')).name
    matches=[c for c in candidates if (c.get('sha256')==original and c.get('key')==key) or (not c.get('sha256') and filename and c.get('file')==filename)]
    if len(matches)!=1:raise ValueError('Review does not identify exact original '+key)
    candidate=matches[0]
    status=candidate.get('status',candidate.get('verdict',candidate.get('technical_verdict')))
    if status not in ('pass','pass_with_caption_conditions'):raise ValueError('Rejected pixel review '+key)
    if not candidate.get('sha256'):
        lineage=data/'legacy-review-lineage.json'
        bindings=json.loads(lineage.read_text(encoding='utf-8')).get('bindings',{}) if lineage.is_file() else {}
        binding=bindings.get(key,{})
        required={'original_sha256':original,'review_record':record,'review_sha256':hashlib.sha256(raw).hexdigest(),'generated_file':filename,'status':status}
        if any(binding.get(k)!=v for k,v in required.items()):raise ValueError('Unbound legacy pixel review '+key)

def artwork(key,registry,strict):
    if key not in registry:raise ValueError('Missing artwork record '+key)
    a=registry[key]
    if not all(a.get(k) and (ROOT/a[k]).is_file() for k in ('asset','thumbnail')):
        if strict:raise ValueError('Unfinished artwork '+key)
        return ''
    if strict and not a.get('reviewed'):raise ValueError('Unreviewed artwork '+key)
    if strict:
        validate_artwork_review(key,a)
        for field in ('asset','thumbnail'):
            actual=hashlib.sha256((ROOT/a[field]).read_bytes()).hexdigest()
            if actual!=a.get(field+'_sha256'):raise ValueError('Changed reviewed derivative '+key)
    w,h=a['width'],a['height']
    full='/'+a['asset'];thumb='/'+a['thumbnail']
    return f'''<figure class="jj-art fc-study-visual" data-journey-art="{E(key)}" id="picture-{E(key)}"><a href="{E(full)}" data-full-image-viewer aria-haspopup="dialog" aria-label="Explore artwork: {E(a['title'])}" data-full-image-alt="{E(a['alt'])}"><img src="{E(thumb)}" width="{w}" height="{h}" style="--study-image-ratio:{w}/{h}" loading="lazy" decoding="async" alt="{E(a['alt'])}"></a><figcaption><p class="fc-study-visual-label">Explore and study</p><h3>{E(a['title'])}</h3><p>{E(a['caption'])}</p><p class="fc-study-visual-sources">{' · '.join(scripture(r) for r in a['refs'])}</p></figcaption></figure>'''

def card(item, preview=None):
    image=''
    if preview:
        image=f'<img class="jj-card-preview" src="/{E(preview["thumbnail"])}" width="{preview["width"]}" height="{preview["height"]}" loading="lazy" decoding="async" alt="{E(preview["alt"])}">'
    return f'<a class="jj-card" href="{E(item[0])}">{image}<h3>{E(item[1])}</h3><p>{E(item[2])}</p><span class="jj-card-action">Open study →</span></a>'

def reference_art(block,registry,page):
    """A linked preview retains its original owning page and never counts as new art."""
    if 'reference_art' in block:
        a=registry[block['reference_art']]
        if a['owner']==page['url'].lstrip('/'):raise ValueError('Same-page original cannot be repeated as a reference')
        href='/'+a['owner']+'#picture-'+block['reference_art']
    else:
        a=block['reference_picture'];href=a['href']
        if href.split('#')[0]==page['url']:raise ValueError('Same-page reference picture')
    return '<div class="jj-directory jj-art-reference">'+card([href,a['title'],a['caption']],a)+'</div>'

def render(page,registry,strict):
    source=(ROOT/'answers/jesus-christ-latter-day-saint-beliefs.html').read_text(encoding='utf-8')
    nav=re.search(r'<nav class="nav".*?</nav>',source,re.S).group(0).replace('href="../','href="/')
    footer=re.search(r'<footer.*?</footer>',source,re.S).group(0).replace('href="../','href="/')
    crumbs=[('/answers.html','Answers'),(PARENT,'Jesus Christ')]+page.get('ancestors',[])
    breadcrumb='<nav aria-label="Breadcrumb"><ol class="jj-breadcrumbs">'+''.join(f'<li><a href="{E(url)}">{E(title)}</a><span aria-hidden="true"> / </span></li>' for url,title in crumbs)+f'<li aria-current="page">{E(page["title"])}</li></ol></nav>'
    css=['answer-styles.css?v=20260909-warm','site-system.css?v=20260924-motion-rails-1','site-header.css?v=20260920-menu-wrap-2','connected-study.css?v=20260919-pill-labels','full-image-viewer.css?v=20260905-viewport','artwork-details.css?v=20260909-warm','artwork-actions.css?v=20260909-warm','topic-artwork-details.css?v=20260908-exclusive-final','resource-cards.css?v=20260909-warm','site-search.css?v=20260924-narrow-reading-1','jesus-journey.css?v=20260923-chapter-cards-1']
    head=''.join(f'<link rel="stylesheet" href="/{x}">' for x in css)
    url=ORIGIN+page['url']
    page_art=[registry[b['art']] for s in page['sections'] for b in s.get('blocks',[]) if isinstance(b,dict) and 'art' in b and b['art'] in registry and registry[b['art']].get('asset') and registry[b['art']].get('reviewed')]
    share=page_art[0]['asset'] if page_art else 'assets/heroes/topics/jesus-desktop.webp'
    share_alt=page_art[0]['alt'] if page_art else 'Jesus Christ'
    head+=f'<meta property="og:image" content="{ORIGIN}/{E(share)}"><meta property="og:image:alt" content="{E(share_alt)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(page["title"])}"><meta name="twitter:description" content="{E(page["description"])}"><meta name="twitter:image" content="{ORIGIN}/{E(share)}">'
    robots='index,follow,max-image-preview:large' if strict else 'noindex,nofollow'
    head+=f'<link rel="canonical" href="{url}"><meta name="description" content="{E(page["description"])}"><meta name="robots" content="{robots}"><meta property="og:type" content="article"><meta property="og:site_name" content="focusChrist"><meta property="og:title" content="{E(page["title"])}"><meta property="og:description" content="{E(page["description"])}"><meta property="og:url" content="{url}">'
    head+='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':'Article','headline':page['title'],'mainEntityOfPage':url,'isPartOf':{'@type':'WebPage','url':ORIGIN+PARENT},'publisher':{'@type':'Organization','name':'focusChrist','url':ORIGIN}})+'</script>'
    sections=[]
    used_previews=set()
    for section in page['sections']:
        refs=section.get('refs',[])
        group=f' data-chapter-group="{E(section["chapter_group"])}"' if section.get('chapter_group') else ''
        blocks=[f'<section class="jj-chapter" id="{E(section["id"])}"{group}><p class="jj-kicker">{E(section.get("eyebrow","Read and discover"))}</p><h2>{E(section["title"])}</h2>']
        content=list(section.get('blocks',[]))
        opening_after=section.get('opening_visual_after_paragraphs',1 if section.get('keep_intro_before_art') else None)
        if opening_after is not None:
            visual=next((i for i,b in enumerate(content) if isinstance(b,dict) and any(k in b for k in ('art','cards','reference_art','reference_picture'))),None)
            if visual is not None:
                first_visual=content.pop(visual)
                prose_positions=[i for i,b in enumerate(content) if isinstance(b,str)]
                if type(opening_after) is not int or not 1<=opening_after<=len(prose_positions):raise ValueError('Invalid opening visual paragraph placement '+section['id'])
                content.insert(prose_positions[opening_after-1]+1,first_visual)
        # An immediate scene can welcome the reader before its opening paragraph.
        # Keep later scenes and the explicitly sequenced Bountiful departure in context.
        context_first={'bn-households-return','bb-abram-stars','mc-withered-hand','mc-official-servants','tp-withered-fig-tree','tp-writing-ground','bn-man-raised'}
        early_scene={'tp-lamp-salt','tp-lilies-birds','tp-vine-pruning','rt-accessible-home'}
        early=next((i for i,b in enumerate(content) if isinstance(b,dict) and b.get('art') in early_scene),None)
        if early is not None and opening_after is None:content.insert(0,content.pop(early))
        if opening_after is None and len(content)>1 and isinstance(content[0],str) and isinstance(content[1],dict) and 'art' in content[1] and content[1]['art'] not in context_first:
            content.insert(0,content.pop(1))
        opening_directory=not any(isinstance(b,dict) and 'art' in b for b in content)
        if opening_directory and opening_after is None:
            directory=next((i for i,b in enumerate(content) if isinstance(b,dict) and 'cards' in b),None)
            if directory is not None:content.insert(0,content.pop(directory))
        for block in content:
            if isinstance(block,str):blocks.append('<div class="jj-reading"><p>'+prose(block,refs)+'</p></div>')
            elif 'art' in block:blocks.append(artwork(block['art'],registry,strict))
            elif 'reference_art' in block or 'reference_picture' in block:blocks.append(reference_art(block,registry,page))
            elif 'heading' in block:blocks.append('<h3>'+E(block['heading'])+'</h3>')
            elif 'cards' in block:
                previews={a['owner']:a for a in reversed(list(registry.values())) if a.get('reviewed') and a.get('thumbnail')}
                # The existing Nativity companion has its own artwork registry.
                previews['birth-of-christ.html']={'thumbnail':'assets/page-art/birth-of-christ/12-nativity-hero-800.webp','width':800,'height':360,'alt':'Mary lays her swaddled newborn in a manger while Joseph watches nearby.'}
                previews['atonement.html']={'thumbnail':'assets/page-art/atonement/servant-960.webp','width':1536,'height':1024,'alt':'Jesus kneels with a basin and towel. He asks His disciples to follow His example of service.'}
                rendered_cards=[]
                for c in block['cards']:
                    preview=previews.get(c[0].lstrip('/'))
                    if preview and preview['thumbnail'] in used_previews:
                        preview=next((a for a in registry.values() if a.get('owner')==c[0].lstrip('/') and a.get('reviewed') and a.get('thumbnail') not in used_previews),None)
                        if preview is None and c[0]=='/birth-of-christ.html':
                            preview={'thumbnail':'assets/page-art/birth-of-christ/03-nephi-vision-800.webp','width':800,'height':533,'alt':'Mary cradles the infant Jesus and looks into His eyes.'}
                    if preview:used_previews.add(preview['thumbnail'])
                    rendered_cards.append(card(c,preview))
                blocks.append('<div class="jj-directory">'+''.join(rendered_cards)+'</div>')
            elif 'questions' in block:blocks.append('<aside class="jj-reflection"><h3>Pause and consider</h3><ul>'+''.join('<li>'+prose(q,refs)+'</li>' for q in block['questions'])+'</ul></aside>')
        if refs:blocks.append('<div class="jj-actions fc-actions">'+''.join(scripture(r) for r in refs)+'</div>')
        blocks.append('</section>');sections.append(''.join(blocks))
    journey=json.loads((DATA/'main-content.json').read_text(encoding='utf-8'))
    route=next(b['cards'] for b in journey['sections'][0]['blocks'] if isinstance(b,dict) and 'cards' in b)
    current=next((i for i,c in enumerate(route) if c[0]==page['url']),None)
    if current is not None and current+1<len(route):
        next_study=route[current+1]
        sections.append('<section class="jj-chapter" id="next-study"><h2>Continue with Jesus Christ</h2><p>Next study in the journey</p><div class="jj-directory">'+card(next_study)+'</div></section>')
    if page.get('related'):sections.append('<section class="jj-chapter" id="continue-study"><h2>Related studies</h2><div class="jj-directory">'+''.join(card(c) for c in page['related'])+'</div></section>')
    sources=page.get('sources',[])
    if sources:sections.append('<section class="jj-chapter" id="sources"><h2>Sources for further study</h2><ul class="jj-source-list">'+''.join(f'<li><a href="{E(s[0])}" target="_blank" rel="noopener noreferrer">{E(s[1])}</a></li>' for s in sources)+'</ul></section>')
    local=f'<nav class="jj-local-nav fc-actions" aria-label="In this study" data-journey-subject="{E(page["title"])}">'+''.join(f'<a href="#{E(s["id"])}">{E(s.get("nav",s["title"]))}</a>' for s in page['sections'])+'</nav>'
    scripts=['jesus-journey.js?v=20260923-chapter-cards-1','site-common.js?v=20260923-sensitive-welcome-1','site-search.js?v=20260919-focused-answers-1','full-image-viewer.js?v=20260914-reopen-1','topic-artwork-details.js?v=20260923-next-study-1']
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(page['title'])} | focusChrist</title>{head}</head><body class="fc-site fc-jesus-journey"><a class="fc-skip-link" data-focuschrist-skip-link="true" href="#main-content">Skip to study</a>{nav}<header class="jj-opening"><div class="jj-wrap">{breadcrumb}<p class="fc-eyebrow">{E(page.get('eyebrow','Come to know Jesus Christ'))}</p><h1>{E(page['title'])}</h1><p class="lede">{E(page['intro'])}</p><a class="fc-button" href="#main-content">Begin the study ↓</a></div></header><main class="jj-wrap jj-main" id="main-content">{local}{''.join(sections)}<nav class="jj-actions jj-return fc-actions" aria-label="Return to the journey"><a href="{E(crumbs[-1][0])}">Return to {E(crumbs[-1][1])}</a><a href="{PARENT}#jesus-journey">Explore the whole Jesus Christ journey</a></nav></main>{footer}<script>function toggleMenu(){{var m=document.getElementById('hamburgerMenu');if(m)m.classList.toggle('show');}}</script>{''.join(f'<script src="/{s}" defer></script>' for s in scripts)}</body></html>'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--strict',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    pages=json.loads((DATA/'pages.json').read_text(encoding='utf-8'))
    registry=json.loads((DATA/'artworks.json').read_text(encoding='utf-8'))
    seen=set()
    for page in pages:
        if page['url'] in seen:raise ValueError('Duplicate URL')
        seen.add(page['url'])
        target=ROOT/page['url'].lstrip('/');expected=render(page,registry,args.strict)
        if args.check:
            if not target.is_file() or target.read_text(encoding='utf-8')!=expected:raise ValueError('Stale generated study '+page['url'])
        else:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(expected,encoding='utf-8',newline='\n')
    print(f'Built {len(pages)} nested studies; strict={args.strict}. Publication and semantic/visual verification are separate.')

if __name__=='__main__':main()
