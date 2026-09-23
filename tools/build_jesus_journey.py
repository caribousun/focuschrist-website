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

def card(item):
    return f'<a class="jj-card" href="{E(item[0])}"><h3>{E(item[1])}</h3><p>{E(item[2])}</p><span class="jj-card-action">Continue this study →</span></a>'

def render(page,registry,strict):
    source=(ROOT/'answers/jesus-christ-latter-day-saint-beliefs.html').read_text(encoding='utf-8')
    nav=re.search(r'<nav class="nav".*?</nav>',source,re.S).group(0).replace('href="../','href="/')
    footer=re.search(r'<footer.*?</footer>',source,re.S).group(0).replace('href="../','href="/')
    crumbs=[('/answers.html','Answers'),(PARENT,'Jesus Christ')]+page.get('ancestors',[])
    breadcrumb='<nav aria-label="Breadcrumb"><ol class="jj-breadcrumbs">'+''.join(f'<li><a href="{E(url)}">{E(title)}</a><span aria-hidden="true"> / </span></li>' for url,title in crumbs)+f'<li aria-current="page">{E(page["title"])}</li></ol></nav>'
    css=['answer-styles.css?v=20260909-warm','site-system.css?v=20260920-opening-copy-1','site-header.css?v=20260920-menu-wrap-2','connected-study.css?v=20260919-pill-labels','full-image-viewer.css?v=20260905-viewport','artwork-details.css?v=20260909-warm','artwork-actions.css?v=20260909-warm','topic-artwork-details.css?v=20260908-exclusive-final','resource-cards.css?v=20260909-warm','site-search.css?v=20260914-standard-rails-1','jesus-journey.css?v=20260923-1']
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
    for section in page['sections']:
        refs=section.get('refs',[])
        blocks=[f'<section class="jj-chapter" id="{E(section["id"])}"><p class="jj-kicker">{E(section.get("eyebrow","Read and discover"))}</p><h2>{E(section["title"])}</h2>']
        for block in section.get('blocks',[]):
            if isinstance(block,str):blocks.append('<div class="jj-reading"><p>'+prose(block,refs)+'</p></div>')
            elif 'art' in block:blocks.append(artwork(block['art'],registry,strict))
            elif 'heading' in block:blocks.append('<h3>'+E(block['heading'])+'</h3>')
            elif 'cards' in block:blocks.append('<div class="jj-directory">'+''.join(card(c) for c in block['cards'])+'</div>')
            elif 'questions' in block:blocks.append('<aside class="jj-reflection"><h3>Pause and consider</h3><ul>'+''.join('<li>'+prose(q,refs)+'</li>' for q in block['questions'])+'</ul></aside>')
        if refs:blocks.append('<div class="jj-actions fc-actions">'+''.join(scripture(r) for r in refs)+'</div>')
        blocks.append('</section>');sections.append(''.join(blocks))
    if page.get('related'):sections.append('<section class="jj-chapter" id="continue-study"><h2>Continue with Jesus Christ</h2><div class="jj-directory">'+''.join(card(c) for c in page['related'])+'</div></section>')
    sources=page.get('sources',[])
    if sources:sections.append('<section class="jj-chapter" id="sources"><h2>Sources for further study</h2><ul class="jj-source-list">'+''.join(f'<li><a href="{E(s[0])}" target="_blank" rel="noopener noreferrer">{E(s[1])}</a></li>' for s in sources)+'</ul></section>')
    local='<nav class="jj-local-nav fc-actions" aria-label="In this study">'+''.join(f'<a href="#{E(s["id"])}">{E(s.get("nav",s["title"]))}</a>' for s in page['sections'])+'</nav>'
    scripts=['site-common.js?v=20260923-jesus-nested-1','site-search.js?v=20260919-focused-answers-1','full-image-viewer.js?v=20260914-reopen-1','topic-artwork-details.js?v=20260923-onward-label-1']
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
