"""Render accepted Joseph family illustrations without exposing draft slots."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- BEGIN JOSEPH LIFE ENRICHMENT -->'
END = '<!-- END JOSEPH LIFE ENRICHMENT -->'

def esc(value):
    return html.escape(str(value), quote=True)

def sources(row):
    return '<p class="fc-study-visual-sources">' + ''.join(
        f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>'
        for s in row['sources']) + '</p>'

def archival_figure(record):
    asset='../'+record['asset']
    title=esc(record['title'])
    return ('<figure id="'+esc(record['id'])+'" class="fc-study-visual joseph-family-archive" data-historical-reference="true">'
      '<a href="'+esc(asset)+'" aria-haspopup="dialog" aria-label="Explore historical image: '+title+'" data-topic-study="who-was-joseph-smith.html#'+esc(record['owning_section'])+'" data-topic-study-label="Return to this family history">'
      '<img src="'+esc(asset)+'" width="'+str(record['width'])+'" height="'+str(record['height'])+'" alt="'+esc(record['alt'])+'" loading="lazy" decoding="async"></a>'
      '<figcaption><h4>'+title+'</h4><p>'+esc(record['caption'])+'</p><p class="fc-study-visual-sources"><a href="'+esc(record['source_url'])+'" target="_blank" rel="noopener noreferrer">'+esc(record['source_label'])+'</a></p></figcaption></figure>')

def build_bridge(data):
    path=ROOT/'joseph-smith-likeness.html'
    page=path.read_text(encoding='utf-8')
    if any(marker in page for marker in ('\u00e2\u20ac', '\u00c2\u00a9', '\ufffd')):
        raise ValueError('Bridge encoding corruption detected; restore reviewed UTF-8 source before building')
    routes={
      'living-portrait':'joseph-smith-portrait-research.html#portrait-section-1',
      'death-masks':'joseph-smith-portrait-research.html#portrait-section-4',
      'joseph-mask-comparison':'joseph-smith-portrait-research.html#portrait-section-4',
      'hyrum-mask-comparison':'joseph-smith-portrait-research.html#portrait-section-11',
      'portraits-from-life':'joseph-smith-portrait-research.html#portrait-section-4',
      'our-portrait':'joseph-smith-portrait-research.html#portrait-section-11',
      'face-in-motion':'joseph-smith-portrait-research.html#research-feature-14',
      'joseph-family-life':'answers/who-was-joseph-smith.html#joseph-family-life',
      'life-remembrance':'answers/who-was-joseph-smith.html#life-remembrance',
      'continue-study':'answers/who-was-joseph-smith.html#continue-study',
      'portrait-research':'joseph-smith-portrait-research.html'}
    for scene in data['scenes']:
        routes['life-'+scene['id']]='answers/who-was-joseph-smith.html#life-'+scene['id']
    # The former full study remains a stable entrance for saved and shared links.
    page=re.sub(r'<a\b[^>]*class="fc-visual-hero[^"<>]*"[^>]*>[\s\S]*?</a>', '',page,count=1)
    intro='<section class="joseph-bridge-intro"><p class="fc-eyebrow">Joseph Smith</p><h1>Explore his life and the portrait</h1><p>Follow Joseph and Emma through their family story, or look closely at the evidence behind our Joseph.</p></section>'
    page=re.sub(r'<section\b[^>]*class="(?:fc-page-intro|joseph-bridge-intro)"[^>]*>[\s\S]*?</section>',lambda _:intro,page,count=1)
    block='<main id="main-content" class="likeness-main"><section class="likeness-chapter" id="joseph-study-entrance"><h2>Where would you like to begin?</h2><div class="fc-actions"><a class="fc-button fc-button--primary" href="answers/who-was-joseph-smith.html#joseph-family-life">Joseph, Emma and their families</a><a class="fc-button fc-button--primary" href="joseph-smith-portrait-research.html">The journey to our Joseph</a></div><p><a href="answers/who-was-joseph-smith.html">Explore Joseph’s life and ministry</a>, including his parents, siblings, marriage, children and the people who shared his work.</p><p><a href="joseph-smith-portrait-research.html">Follow the illustrated portrait journey</a> through casts, portraits, remembered encounters and the making of our Joseph.</p><details><summary>Find an earlier study link</summary><ul>'
    for ident,target in routes.items():
        label=ident.replace('life-','').replace('-',' ').capitalize()
        block+='<li id="'+esc(ident)+'"><a href="'+esc(target)+'">'+esc(label)+'</a></li>'
    block+='</ul></details></section></main>'
    page=re.sub(r'<main\b[^>]*>[\s\S]*?</main>',lambda _:block,page,count=1)
    page=page.replace('joseph-smith-likeness.css?v=20260927-anchor-alignment-1','joseph-smith-likeness.css?v=20261004-compact-bridge-1')
    page=re.sub(r'<title>.*?</title>','<title>Joseph Smith: Life and Portrait | focusChrist</title>',page,count=1)
    page=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Explore Joseph and Emma Smith’s family story, or follow the illustrated historical journey behind the focusChrist Joseph portrait.">',page,count=1)
    if 'joseph-study-bridge.js' not in page:
        page=page.replace('</head>','<script src="joseph-study-bridge.js?v=20261004-journeys-1" defer></script>\n</head>')
    script="/* Preserve old study anchors while each picture has one owning page. */\n(function(){'use strict';\nconst routes="+json.dumps(routes,ensure_ascii=False,separators=(',',':'))+";\nfunction follow(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}if(Object.prototype.hasOwnProperty.call(routes,id)){location.replace(new URL(routes[id],location.href).href);}}\nwindow.addEventListener('hashchange',follow);follow();\n})();\n"
    (ROOT/'joseph-study-bridge.js').write_text(script,encoding='utf-8',newline='\n')
    path.write_text(page,encoding='utf-8',newline='\n')

def build():
    data = json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8-sig'))
    accepted_by_id = {s['id']:s for s in data['scenes'] if s.get('image_status') == 'accepted' and s.get('image')}
    accepted = [accepted_by_id[k] for k in data['scene_order'] if k in accepted_by_id]
    for s in accepted:
        if not (ROOT/s['image']['src']).is_file():
            raise ValueError('Accepted image missing: '+s['id'])
    delivery=json.loads((ROOT/'docs/joseph-art-delivery.json').read_text(encoding='utf-8'))
    out = [START, '<section id="joseph-family-life" class="fc-deep-study joseph-life-enrichment"><p class="fc-eyebrow">Faith in daily life</p><h2>Family, service and remembrance</h2><p>Meet Joseph, Emma and Hyrum through moments of work, love and faith.</p>']
    records=json.loads((ROOT/'docs/joseph-family-records.json').read_text(encoding='utf-8'))
    archives=json.loads((ROOT/'docs/joseph-family-archival-art.json').read_text(encoding='utf-8'))['items']
    lucy=json.loads((ROOT/'docs/joseph-lucy-family-stories.json').read_text(encoding='utf-8'))
    lucy_ready=[story for story in lucy['stories'] if story.get('image_status')=='accepted' and story.get('image')]
    if lucy_ready:
        out.append('<section id="lucy-family-stories" class="joseph-lucy-stories"><h3>'+esc(lucy['heading'])+'</h3>')
        out.extend('<p>'+esc(p)+'</p>' for p in lucy['introduction'])
        out.append('<details class="joseph-story-menu"><summary>Choose a story from Lucy’s history</summary><nav class="joseph-life-nav" aria-label="Stories from Lucy Mack Smith">'+''.join('<a href="#'+esc(story['id'])+'">'+esc(story['heading'])+'</a>' for story in lucy_ready)+'</nav></details>')
        for story in lucy_ready:
            im=story['image'];asset='../'+im['src'];delivered=story['delivery']
            image_src='../'+delivered['default'];image_set=', '.join('../'+v['asset']+' '+str(v['width'])+'w' for v in delivered['variants'])
            if not (ROOT/im['src']).is_file():raise ValueError('Lucy story image missing: '+story['id'])
            out.append('<article id="'+esc(story['id'])+'" class="joseph-life-scene"><p class="fc-eyebrow">'+esc(story['date_label'])+'</p><h3>'+esc(story['heading'])+'</h3>')
            out.extend('<p>'+esc(p)+'</p>' for p in story['paragraphs'])
            out.append('<figure class="fc-study-visual likeness-art" data-exclusive-artwork="'+esc(story['id'])+'"><a href="'+esc(asset)+'" aria-haspopup="dialog" aria-label="Explore artwork: '+esc(story['heading'])+'" data-topic-study="who-was-joseph-smith.html#'+esc(story['id'])+'" data-topic-study-label="Return to this family story"><img src="'+esc(image_src)+'" data-source-original="'+esc(asset)+'" srcset="'+esc(image_set)+'" sizes="(max-width: 600px) 94vw, 100vw" width="'+str(im['width'])+'" height="'+str(im['height'])+'" alt="'+esc(im['alt'])+'" loading="lazy" decoding="async"></a><figcaption><h4 class="joseph-life-caption-title" hidden>'+esc(story['heading'])+'</h4><p>'+esc(story['visitor_caption'])+'</p>'+sources(story)+'</figcaption></figure></article>')
        out.append('</section>')
    out.append('<section id="joseph-family-records" class="joseph-family-records"><h3>'+esc(records['heading'])+'</h3>')
    out.extend('<p>'+esc(p)+'</p>' for p in records['introduction'])
    for family in records['families']:
        out.append('<article id="'+esc(family['id'])+'" class="joseph-family-record"><h4>'+esc(family['heading'])+'</h4>')
        out.extend('<p>'+esc(p)+'</p>' for p in family['paragraphs'])
        out.append('<details class="joseph-family-list"><summary>Read the complete family list: '+str(len(family['members']))+' children</summary><div class="joseph-family-table"><table><thead><tr>'+''.join('<th scope="col">'+esc(c)+'</th>' for c in family['columns'])+'</tr></thead><tbody>')
        for name, dates in family['members']:
            out.append('<tr><th scope="row">'+esc(name)+'</th><td>'+esc(dates)+'</td></tr>')
        out.append('</tbody></table></div>')
        if family.get('note'):out.append('<p>'+esc(family['note'])+'</p>')
        out.append('</details>')
        out.append(sources(family))
        pictures=[im for im in archives if im['owning_section']==family['id']]
        if pictures:
            out.append('<div class="joseph-family-archives">'+''.join(archival_figure(im) for im in pictures)+'</div>')
        out.append('</article>')
    out.append('</section><h3>Moments in their shared life</h3>')
    out.append('<details class="joseph-story-menu"><summary>Choose a moment in their shared life</summary><nav class="joseph-life-nav" aria-label="Family and service scenes">'+''.join(f'<a href="#life-{esc(s["id"])}">{esc(s["heading"])}</a>' for s in accepted)+'<a href="#life-remembrance">Forgiveness and remembrance</a></nav></details>')
    for s in accepted:
        im=s['image']; sid='life-'+s['id']; title=esc(s['heading']); alt=esc(im['alt']); src=esc('../'+im['src']); art_id=esc(s.get('existing_art_id',sid))
        delivered=delivery.get(im['src']) or s['delivery']
        image_src=esc('../'+delivered['default'])
        srcset=esc(', '.join('../'+v['asset']+' '+str(v['width'])+'w' for v in delivered['variants']))
        out.append(f'<article id="{sid}" class="joseph-life-scene"><p class="fc-eyebrow">{esc(s["date_label"])}</p><h3>{title}</h3>')
        out.extend('<p>'+esc(p)+'</p>' for p in s['paragraphs'])
        out.append(f'<figure class="fc-study-visual likeness-art" data-enriched-study-art="{art_id}" data-exclusive-artwork="{art_id}"><a href="{src}" aria-haspopup="dialog" aria-label="Explore artwork: {title}" data-full-image-alt="{alt}" data-topic-study="who-was-joseph-smith.html#{sid}" data-topic-study-label="Return to this family study"><img src="{image_src}" data-source-original="{src}" srcset="{srcset}" sizes="(max-width: 600px) 94vw, 100vw" width="{im["width"]}" height="{im["height"]}" alt="{alt}" loading="lazy" decoding="async"></a><figcaption><h4 class="joseph-life-caption-title" hidden>{title}</h4><p>{esc(s["visitor_caption"])}</p>{sources(s)}</figcaption></figure>')
        out.append('<p class="joseph-life-reflection"><strong>Consider:</strong> '+esc(s['reflection'])+'</p></article>')
    c=data['closing'];out.append('<section id="life-remembrance" class="joseph-life-closing"><h3>'+esc(c['heading'])+'</h3>')
    out.extend('<p>'+esc(p)+'</p>' for p in c['paragraphs'])
    out.extend(['<p class="joseph-life-source-note">'+esc(c['visitor_source_note'])+'</p>',sources(c),'<p class="joseph-life-reflection"><strong>Consider:</strong> '+esc(c['reflection'])+'</p></section></section>',END])
    block='\n'.join(out);path=ROOT/data['owning_page'];page=path.read_text(encoding='utf-8')
    if START in page:
        a=page.index(START);b=page.index(END,a)+len(END);page=page[:a]+block+page[b:]
    else:
        match=re.search(r'<section\b[^>]*\bid="guided-application"[^>]*>',page)
        if not match:raise ValueError('Biography insertion anchor missing')
        page=page[:match.start()]+block+'\n'+page[match.start():]
    if '../joseph-family-life.css' not in page:
        page=page.replace('</head>','<link rel="stylesheet" href="../joseph-family-life.css?v=20261004-family-1">\n</head>')
    if '<a href="#joseph-family-life">' not in page:
        page=page.replace('<a href="#guided-application">Guided application</a>','<a href="#joseph-family-life">Family and daily life</a><a href="#guided-application">Guided application</a>',1)
    if lucy_ready and '<a href="#lucy-family-stories">' not in page:
        page=page.replace('<a href="#joseph-family-life">Family and daily life</a>','<a href="#joseph-family-life">Family and daily life</a><a href="#lucy-family-stories">Lucy’s family stories</a>',1)
    # One compact page menu retains the established study navigation links.
    if '<details class="joseph-page-menu">' not in page:
        page=re.sub(r'(<nav class="fc-study-nav" aria-label="On this study page">[\s\S]*?</nav>)',r'<details class="joseph-page-menu"><summary>Explore this Joseph study</summary>\1</details>',page,count=1)
    page=page.replace('href="../joseph-smith-likeness.html"','href="../joseph-smith-portrait-research.html"')
    page=page.replace('Explore an art-led companion study of Joseph’s death masks, portraits, and the likeness developed for focusChrist.','Follow the pictures and historical accounts that bring us to our Joseph.')
    page=page.replace('Open the portrait story →','Follow the portrait journey →')
    path.write_text(page,encoding='utf-8',newline='\n')
    build_bridge(data)
    print(f'Rendered {len(accepted)} accepted scenes in the biography; legacy likeness entrance preserved.')

if __name__=='__main__': build()
