"""Build the separate illustrated research from the same reviewed PDF content."""
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'docs/joseph-portrait-research-content.json'
PAGE = ROOT / 'joseph-smith-likeness.html'
BEGIN = '<!-- BEGIN JOSEPH PORTRAIT RESEARCH -->'
END = '<!-- END JOSEPH PORTRAIT RESEARCH -->'

def inline(value, references=True):
    editorial=ROOT/'docs/joseph-research-editorial-map.json'
    if editorial.exists():
        for edit in json.loads(editorial.read_text(encoding='utf-8'))['changes']:
            if value==edit['original']:value=edit['replacement']
    value = re.sub(r'<link href="([^"]+)"[^>]*>', lambda m: '<a href="'+m[1]+'"'+(' target="_blank" rel="noopener noreferrer"' if m[1].startswith('http') else '')+'>', value)
    value = value.replace('</link>', '</a>').replace('<u>', '').replace('</u>', '')
    if references:
        def cite(match):
            nums=[]
            for part in match[1].split(','):
                bits=part.strip().split('-')
                nums.extend(range(int(bits[0]),int(bits[-1])+1))
            return '['+', '.join(f'<a href="#portrait-source-{n}" aria-label="Source {n}">{n}</a>' for n in nums)+']'
        value=re.sub(r'\[([0-9]+(?:\s*[-,]\s*[0-9]+)*)\]',cite,value)
    return value


ROUTE='joseph-smith-portrait-research.html'
VISUALS=ROOT/'docs/joseph-research-visuals.json'
FEATURES=ROOT/'docs/joseph-research-feature-studies.json'

def visual(record, describedby=None):
    src=record['src']; target=record['owner']; title=record['title']; caption=record['caption']
    delivery_path=ROOT/'docs/joseph-art-delivery.json'
    delivery=json.loads(delivery_path.read_text(encoding='utf-8')).get(src) if delivery_path.exists() else None
    image_src=delivery['default'] if delivery else src
    responsive=(' data-source-original="'+src+'" srcset="'+', '.join(v['asset']+' '+str(v['width'])+'w' for v in delivery['variants'])+'" sizes="(max-width: 600px) 94vw, 100vw"') if delivery else ''
    original=record.get('kind')=='original'
    attrs=(f'data-enriched-study-art="{record["id"]}" data-exclusive-artwork="{record["id"]}" data-research-art="{record["id"]}"' if original else 'data-research-reference="true"')
    detail=record.get('detail_window')
    crop_style=''
    img_style=f' style="width:{record["width"]}px;max-width:100%;height:auto;margin-inline:auto"' if record.get('native_display') else ''
    if detail:
        x,y,w,h=detail
        assert 0<=x and 0<=y and w>0 and h>0 and x+w<=record['width'] and y+h<=record['height']
        crop_style=f' class="research-detail-window" style="aspect-ratio:{w}/{h};max-width:{max(w,min(w*2,360))}px;margin-inline:auto"'
        img_style=f' style="width:{record["width"]/w*100:.6f}%;max-width:none;position:absolute;left:{-x/w*100:.6f}%;top:{-y/h*100:.6f}%;height:auto"'
    description=f' aria-describedby="{describedby}"' if describedby else ''
    label=record.get('label','Research reference')
    label_markup='' if original and label in {'New artwork · explanatory interpretation','New artwork · feature study','New artwork · historical interpretation'} else f'<p class="fc-study-visual-label">{label}</p>'
    return (f'<figure class="fc-study-visual research-visual" {attrs}{description}>'
        f'<a href="{src}"{crop_style} aria-haspopup="dialog" aria-label="Explore artwork: {html.escape(title,quote=True)}" data-topic-study="{target}" data-topic-study-label="{html.escape(record.get("owner_label","Visit the owning portrait study"),quote=True)}">'
        f'<img src="{image_src}"{responsive} width="{record["width"]}" height="{record["height"]}" alt="{html.escape(record["alt"],quote=True)}" loading="lazy" decoding="async"{img_style}></a>'
        f'<figcaption>{label_markup}<h4>{html.escape(title)}</h4><p>{inline(caption)}</p>'
        '<p class="fc-study-visual-sources">'+''.join(f'<a href="{html.escape(x["url"],quote=True)}"'+(' target="_blank" rel="noopener noreferrer"' if x['url'].startswith('https:') else '')+'>'+html.escape(x['label'])+'</a>' for x in record.get('sources',[]))+
        f'<a href="{target}">{html.escape(record.get("owner_label","Visit the owning portrait study"))}</a></p></figcaption></figure>')

def build():
    data=json.loads(CONTENT.read_text(encoding='utf-8'))
    visuals=json.loads(VISUALS.read_text(encoding='utf-8')) if VISUALS.exists() else {}
    features=json.loads(FEATURES.read_text(encoding='utf-8')) if FEATURES.exists() else {}
    image_captions=[r.get('caption') for r in visuals.values()]+[c.get('caption') for r in visuals.values() for c in r.get('companions',[])]
    parts=[BEGIN,'<section id="portrait-research" class="joseph-research" aria-labelledby="portrait-research-title">',
      '<header class="research-opening"><p class="fc-eyebrow">Joseph Smith · Portrait Research</p><h1 id="portrait-research-title">The evidence behind our Joseph</h1><p>What history supports, what remains uncertain, and how we made our portrait.</p><div class="research-mode-switch fc-actions" role="group" aria-label="Reading view" hidden><button class="fc-button fc-button--primary" type="button" data-research-mode="chapters" aria-pressed="true">Chapter view</button><button class="fc-button" type="button" data-research-mode="all" aria-pressed="false">Read all</button></div><nav class="research-opening-links" aria-label="Study downloads and return"><a href="assets/research/focuschrist-joseph-evidence.pdf" download>Download the PDF</a><a href="joseph-smith-likeness.html#our-portrait">Return to the portrait study</a></nav></header>',
      '''<p class="research-mode-status" role="status" aria-live="polite" hidden></p><nav class="research-chapters" aria-label="Research chapters"><a class="fc-study-panel" href="#portrait-section-1"><span>01 · The question</span><strong>Meet the portrait</strong><span>Our verdict and its limits</span></a><a class="fc-study-panel" href="#portrait-section-4"><span>02 · The records</span><strong>What survives</strong><span>Masks, sittings and descriptions</span></a><a class="fc-study-panel" href="#portrait-section-6"><span>03 · The face</span><strong>Look feature by feature</strong><span>Sixteen traits, with evidence</span></a><a class="fc-study-panel" href="#portrait-section-10"><span>04 · The decisions</span><strong>How the image was made</strong><span>Creation, retention and future study</span></a><a class="fc-study-panel" href="#portrait-section-12"><span>05 · The open questions</span><strong>Keep the sources in view</strong><span>Discovery, conflicts and source index</span></a></nav><details class="research-directory"><summary>Go directly to a research topic</summary><nav aria-label="Portrait research contents"><ol class="research-contents">''']
    for sec in data['sections']:
        if sec['id']!='section-2':parts.append(f'<li><a href="#portrait-{sec["id"]}">{html.escape(sec["title"])}</a></li>')
    parts.append('</ol></nav></details>')
    slots=[]
    for sec in data['sections']:
        sid=sec['id']; source_section=int(sid.split('-')[1])>=13
        parts.append(f'<section class="research-part" id="portrait-{sid}" aria-labelledby="portrait-{sid}-title"><p class="fc-eyebrow">{int(sid.split("-")[1]):02d} · The research</p><h2 id="portrait-{sid}-title">{html.escape(sec["title"])}</h2>')
        if sid=='section-11':
            parts.append('<dl class="research-evidence-stages"><div class="fc-study-panel"><dt>Recorded creation</dt><dd>The project identity record names Joseph’s masks as primary proportional references and Hyrum’s as comparative. The original prompt and intermediate fitting records have not been recovered.</dd></div><div class="fc-study-panel"><dt>Actually examined afterward</dt><dd>The retained portrait’s visible features, historical descriptions, cast histories and source publications were qualitatively reviewed. Newly consulted evidence is identified as later research.</dd></div><div class="fc-study-panel"><dt>Still proposed</dt><dd>Pose-controlled measurements, blinded comparisons and a restrained hair or lash variation have not been performed. Museum photogrammetry records casts; it does not validate this portrait.</dd></div></dl>')
        if source_section: parts.append('<details class="research-source-index"><summary>Read the complete source entries</summary>')
        pending=[]; count=0; block_no=0; trait_count=0
        def flush():
            nonlocal pending,count,block_no,trait_count
            if not pending:return
            block_no+=1; slot=f'{sid}-{block_no}'
            slots.append({'slot':slot,'section':sec['title'],'text':re.sub('<[^>]+>',' ',''.join(pending))[:140]})
            v=visual(visuals[slot]) if slot in visuals else ''
            comparison=slot in visuals and bool(visuals[slot].get('companions'))
            if comparison:
                note_id=f'research-comparison-note-{slot}'
                documents=all('/joseph-documents/' in c['src'] and 'mask-pair' not in c['src'] for c in [visuals[slot],*visuals[slot]['companions']])
                note='These pages identify the publication and its description. The publication date is separate from the remembered event and from any earlier letter.' if documents else 'Separate source views retain their own proportions. They are not aligned, warped, or matched to an anatomical scale. Keep pose, lighting and the cast’s condition in mind.'
                group_label='Publication pages and source context' if documents else 'Separate source views, without anatomical registration'
                if any(c.get('kind')=='original' for c in [visuals[slot],*visuals[slot]['companions']]):
                    note='The historical image and newly made artwork have different roles. Labels identify the surviving source and the interpreted scenes; neither is an anatomically registered comparison.'
                    group_label='Historical evidence and new interpretive artwork'
                v=f'<div class="research-comparison-group" aria-label="{group_label}">'+visual(visuals[slot],note_id)+''.join(visual(c,note_id) for c in visuals[slot]['companions'])+f'<div role="note" id="{note_id}" class="research-comparison-note">{note}</div></div>'
            parts.append(f'<div class="research-reading-block{ " research-reading-block--illustrated" if v else ""}{ " research-reading-block--comparison" if comparison else ""}" id="research-block-{slot}" data-research-reading-block="{slot}"><div class="research-reading-copy">'+''.join(pending)+'</div>'+v+'</div>')
            pending=[]; count=0; trait_count=0
        for b in sec['blocks']:
            kind=b['kind']
            if sid=='section-2' and kind!='box':continue
            if kind=='paragraph':
                t=b['html']; style=b.get('style','body')
                if t in image_captions or any(inline(t)==inline(c) for c in image_captions if c):continue
                if style=='title' or t.startswith('Prepared for Wyatt. Use the navigation bar'):continue
                if source_section and style!='source':
                    flush();parts.append(f'<p class="research-source-note">{inline(t)}</p>');continue
                if style=='source':
                    flush();n=re.match(r'<b>\[(\d+)\]</b>',t)[1]
                    parts.append(f'<p class="research-source" id="portrait-source-{n}">{inline(t,False)}</p>');continue
                if style=='sub':
                    if count>=2 or (sid=='section-4' and t.startswith('Maudsley:')):flush()
                    pending.append(f'<h3>{inline(t)}</h3>');continue
                if count>=2:flush()
                cls=' class="fc-eyebrow"' if style=="eyebrow" else ''
                tag='div' if style=='eyebrow' else 'p'
                pending.append(f'<{tag}{cls}>{inline(t)}</{tag}>');count+=(style!='eyebrow')
            elif kind=='box':
                if count>=2:flush()
                pending.append(f'<aside class="fc-study-panel"><h3>{inline(b["title"])}</h3><p>{inline(b["html"])}</p></aside>');count+=1
            elif kind=='image':
                # Image records are displayed through the explicit, source-labelled visual map.
                continue
            elif kind=='trait':
                feature_id=b['title'].split()[0]
                if feature_id in features:
                    flush()
                    feature=features[feature_id]
                    parts.append(f'<article class="research-feature-study" id="research-feature-{feature_id}" data-research-feature="{feature_id}"><header><p class="fc-eyebrow">Look closely · Follow the evidence</p><h3>{html.escape(b["title"])}</h3></header><div class="research-feature-reasoning"><p><strong>In our portrait.</strong> {inline(b["observed"])}</p><p><strong>The historical evidence.</strong> {inline(b["evidence"])}</p><p><strong>Our assessment.</strong> {inline(b["verdict"])}</p></div>')
                    parts.append('<div class="research-feature-images">'+''.join(visual(record) for record in feature['visuals'])+'</div>')
                    for paragraph in feature.get('explanation',[]):
                        parts.append(f'<p class="research-feature-explanation">{inline(paragraph)}</p>')
                    parts.append('<div class="research-feature-limits"><h4>What this can and cannot tell us</h4><p>'+inline(feature['limits'])+'</p></div></article>')
                    continue
                if pending and not trait_count:flush()
                pending.append(f'<article class="research-trait"><h3>{html.escape(b["title"])}</h3><p><strong>What is visible.</strong> {inline(b["observed"])}</p><p><strong>Evidence.</strong> {inline(b["evidence"])}</p><p><strong>Decision.</strong> {inline(b["verdict"])}</p></article>');trait_count+=1
                if trait_count==2:flush()
            elif kind=='table':
                flush()
                for row_index,row in enumerate(b['rows']):
                    # Keep the three contemporary letters together: no scan of
                    # these original manuscripts was recovered for this study.
                    if sid=='section-5' and row_index<3:
                        if row_index==0:
                            pending.append('<div class="research-table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+inline(h)+'</th>' for h in b['headers'])+'</tr></thead><tbody>')
                        pending.append('<tr>'+''.join(f'<td data-label="{html.escape(h,quote=True)}">{inline(t)}</td>' for h,t in zip(b['headers'],row))+'</tr>')
                        if row_index==2:
                            pending.append('</tbody></table></div>');flush();block_no+=2
                    else:
                        pending.append('<div class="research-table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+inline(h)+'</th>' for h in b['headers'])+'</tr></thead><tbody><tr>'+''.join(f'<td data-label="{html.escape(h,quote=True)}">{inline(t)}</td>' for h,t in zip(b['headers'],row))+'</tr></tbody></table></div>');flush()
            else:raise ValueError(kind)
        flush()
        for slot,record in visuals.items():
            if record.get('after_section')!=sid:continue
            parts.append(f'<div id="research-block-{slot}" class="research-reading-block research-reading-block--illustrated" data-research-reading-block="{slot}"><div class="research-reading-copy"><p class="research-reflection-label">A Gospel reflection</p><h3>{inline(record["reflection_title"])}</h3><p>{inline(record["reflection_text"])}</p></div>{visual(record)}</div>')
        if source_section:parts.append('</details>')
        if sid=='section-15':
            records=json.loads((ROOT/'docs/joseph-research-document-sources.json').read_text(encoding='utf-8'))['records']
            parts.append('<details class="research-source-index research-document-gallery"><summary>Inspect all ten historical document pages</summary><div class="research-source-gallery">')
            for record in records:
                parts.append(visual(dict(kind='reference',src=record['asset'],width=record['width'],height=record['height'],title=record['id'].replace('-',' ').title(),alt=record['caption'],caption=record['caption'],owner='#portrait-section-15',owner_label='Return to the source index',label='Full historical page',sources=[dict(url=record['source_url'],label='Read the archival scan')])) )
            parts.append('</div></details>')
        n=int(sid.split('-')[1]); previous=f'<a href="#portrait-section-{n-1}">← Previous section</a>' if n>1 else '<a href="#portrait-research">Research contents ↑</a>'
        following=f'<a href="#portrait-section-{n+1}">Next: {html.escape(data["sections"][n]["title"])} →</a>' if n<15 else '<a href="joseph-smith-likeness.html#our-portrait">Return to the portrait study →</a>'
        parts.append(f'<nav class="research-section-nav" aria-label="Continue from {html.escape(sec["title"],quote=True)}">{previous}{following}</nav></section>')
    parts.append('<nav class="research-chapter-controls" aria-label="Continue through the research chapters" hidden><a class="fc-button" data-research-previous href="#portrait-section-1">Previous chapter</a><a class="fc-button fc-button--primary" data-research-next href="#portrait-section-4">Next chapter</a></nav><div class="fc-actions"><a class="fc-button fc-button--primary" href="assets/research/focuschrist-joseph-evidence.pdf" download>Download the complete PDF</a><a class="fc-button" href="joseph-smith-likeness.html#our-portrait">Return to the portrait study</a></div></section>'+END)
    parts.insert(-1,'<section class="research-study-onward" aria-labelledby="research-study-onward-title"><h2 id="research-study-onward-title">Keep studying with care</h2><dl class="research-evidence-stages"><div class="fc-study-panel"><dt>Read the witness in context</dt><dd>Choose one description. What was written at the time, and what reached us through a later publication?</dd></div><div class="fc-study-panel"><dt>Separate confidence from faith</dt><dd>Which conclusions belong to historical evidence, which to artistic interpretation, and which to spiritual conviction? Read <a target="_blank" rel="noopener noreferrer" href="https://www.churchofjesuschrist.org/study/scriptures/nt/1-thes/5?lang=eng&amp;id=p21#p21">1 Thessalonians 5:21</a>.</dd></div><div class="fc-study-panel"><dt>Leave room for correction</dt><dd>What new source would change your view? Follow the invitation to seek learning in <a target="_blank" rel="noopener noreferrer" href="https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/88?lang=eng&amp;id=p118#p118">Doctrine and Covenants 88:118</a>.</dd></div></dl><div class="fc-actions"><a class="fc-button" href="joseph-smith-likeness.html">Joseph’s portrait study</a><a class="fc-button" href="church-history.html">Church History</a><a class="fc-button" href="answers/melchizedek-priesthood-restoration.html">Restoration history and sources</a><a class="fc-button" href="ask.html?topic=Joseph+Smith+portraits+and+death+masks&amp;return=%2Fjoseph-smith-portrait-research.html#ask-question">Ask about Joseph’s appearance</a></div></section>')
    # Keep the view selector available while reading without duplicating controls.
    opening_index=next(i for i,x in enumerate(parts) if '<header class="research-opening"' in x)
    opening=parts[opening_index]
    switch_start=opening.index('<div class="research-mode-switch')
    switch_end=opening.index('</div>',switch_start)+6
    mode_control=opening[switch_start:switch_end]
    opening_links=opening[switch_end:].replace('</header>','')
    parts[opening_index:opening_index+1]=[opening[:switch_start]+'</header>',mode_control,opening_links]
    # Let the reader meet the portrait before the chapter directory.
    start=next(i for i,x in enumerate(parts) if 'research-mode-status' in x)
    finish=next(i for i,x in enumerate(parts) if x=='</ol></nav></details>')
    directory=parts[start:finish+1]
    del parts[start:finish+1]
    after_first=next(i for i,x in enumerate(parts) if 'Continue from Our focusChrist Joseph' in x)+1
    parts[after_first:after_first]=directory
    main=PAGE.read_text(encoding='utf-8')
    landing=BEGIN+'\n<section id="portrait-research" class="likeness-chapter"><p class="fc-eyebrow">The evidence behind the portrait</p><h2>Portrait Research</h2><p>Explore the full illustrated research in its own study: the historical records, the feature-by-feature audit, how our portrait was created, and the questions that remain.</p><div class="fc-actions"><a class="fc-button fc-button--primary" href="'+ROUTE+'">Portrait Research</a></div></section>\n'+END
    main=main.split(BEGIN)[0]+landing+main.split(END)[1]
    main=main.replace('href="#portrait-research">Read the complete portrait research','href="'+ROUTE+'">Portrait Research')
    main=main.replace('<a class="fc-button fc-button--primary" href="'+ROUTE+'">Portrait Research</a></nav>','</nav>')
    if 'class="fc-actions joseph-research-primary-entry"' not in main:
        main=main.replace('href="#continue-study">6 · Keep exploring</a></nav>','href="#continue-study">6 · Keep exploring</a></nav><div class="fc-actions joseph-research-primary-entry"><a class="fc-button fc-button--primary" href="'+ROUTE+'">Portrait Research</a></div>')
    if 'href="'+ROUTE+'">PORTRAIT RESEARCH</a>' not in main:
        main=main.replace('aria-current="page">JOSEPH SMITH</a>','aria-current="page">JOSEPH SMITH</a><a href="'+ROUTE+'">PORTRAIT RESEARCH</a>')
    main=main.replace('joseph-smith-research.css?v=20261003-research-1','joseph-smith-research.css?v=20261003-separate-research-2')
    main=main.replace('joseph-smith-research.css?v=20261003-separate-research-2','joseph-smith-research.css?v=20261003-closing-spacing-3')
    PAGE.write_text(main,encoding='utf-8',newline='\n')
    head=main.split('<a class="fc-visual-hero')[0]
    head=re.sub(r'<title>.*?</title>','<title>Joseph Smith Portrait Research | focusChrist</title>',head)
    head=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="The complete historical research behind the focusChrist Joseph Smith portrait: masks, written descriptions, art, sources, and the limits of reconstruction.">',head)
    head=head.replace('https://focuschrist.com/joseph-smith-likeness.html','https://focuschrist.com/'+ROUTE)
    head=head.replace('Joseph Smith: The Face Behind the History','Joseph Smith Portrait Research')
    head=head.replace('class="fc-site fc-likeness-page"','class="fc-site fc-likeness-page fc-portrait-research-page"')
    head=head.replace('<a href="joseph-smith-likeness.html" class="active" aria-current="page">JOSEPH SMITH</a>','<a href="joseph-smith-likeness.html">JOSEPH SMITH</a>').replace('<a href="'+ROUTE+'">PORTRAIT RESEARCH</a>','<a href="'+ROUTE+'" class="active" aria-current="page">PORTRAIT RESEARCH</a>')
    head=head.replace('topic-artwork-details.js?v=20260930-history-records-1','topic-artwork-details.js?v=20261003-research-sources-1').replace('topic-artwork-details.js?v=20261003-joseph-family-sources-1','topic-artwork-details.js?v=20261003-research-sources-1')
    head=head.replace('</head>','<script src="joseph-smith-research.js?v=20261003-chapters-1" defer></script>\n</head>')
    footer=main.split('</main>',1)[1]
    (ROOT/ROUTE).write_text(head+'<main id="main-content" class="likeness-main">\n'+'\n'.join(parts)+'\n</main>'+footer,encoding='utf-8',newline='\n')
    print(json.dumps({'output':ROUTE,'slots':slots,'visuals':len(visuals),'status':'LOCAL SCAFFOLD: visual slots must receive reviewed images before release'},indent=2))

if __name__=='__main__':build()
