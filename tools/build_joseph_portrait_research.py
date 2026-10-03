"""Build the in-page research from the same structured content as the PDF."""
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'docs/joseph-portrait-research-content.json'
PAGE = ROOT / 'joseph-smith-likeness.html'
BEGIN = '<!-- BEGIN JOSEPH PORTRAIT RESEARCH -->'
END = '<!-- END JOSEPH PORTRAIT RESEARCH -->'

def inline(value, references=True):
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

def build():
    data=json.loads(CONTENT.read_text(encoding='utf-8'))
    sections=data['sections']
    parts=[BEGIN, '<section id="portrait-research" class="likeness-chapter joseph-research" aria-labelledby="portrait-research-title">', '<p class="fc-eyebrow">The portrait research</p><h2 id="portrait-research-title">Our focusChrist Joseph: evidence and interpretation</h2>', '<p>Follow the historical records behind this study, examine the portrait feature by feature, and see where the evidence leaves room for interpretation.</p>', '<div class="fc-actions"><a class="fc-button fc-button--primary" href="assets/research/focuschrist-joseph-evidence.pdf" download>Download the complete research PDF</a><a class="fc-button" href="#our-portrait">Return to how the portrait was developed</a></div>', '<nav class="fc-study-panel" aria-label="Portrait research contents"><h3>In this research</h3><ol class="research-contents">']
    for s in sections:
        if s['id']!='section-2':parts.append(f'<li><a href="#portrait-{s["id"]}">{html.escape(s["title"])}</a></li>')
    parts.append('</ol></nav>')
    excluded=[]
    for s in sections:
        # Paper page numbers and PDF-specific navigation become real HTML links.
        if s['id']=='section-2':
            blocks=[b for b in s['blocks'] if b['kind']=='box']
        else: blocks=s['blocks']
        parts.append(f'<section class="research-part" id="portrait-{s["id"]}" aria-labelledby="portrait-{s["id"]}-title"><h3 id="portrait-{s["id"]}-title">{html.escape(s["title"])}</h3>')
        for b in blocks:
            kind=b['kind']
            if kind=='paragraph':
                t=b['html']; style=b.get('style','body')
                if style=='title':continue
                if t.startswith('Prepared for Wyatt. Use the navigation bar'):
                    excluded.append(t);continue
                if style=='source':
                    n=re.match(r'<b>\[(\d+)\]</b>',t)[1]
                    parts.append(f'<p class="research-source" id="portrait-source-{n}">{inline(t,False)}</p>')
                else:
                    tag='h4' if style=='sub' else 'p'
                    cls=' class="fc-eyebrow"' if style=='eyebrow' else ''
                    parts.append(f'<{tag}{cls}>{inline(t)}</{tag}>')
            elif kind=='box':parts.append(f'<aside class="fc-study-panel"><h4>{inline(b["title"])}</h4><p>{inline(b["html"])}</p></aside>')
            elif kind=='trait':parts.append(f'<article class="research-trait"><h4>{html.escape(b["title"])}</h4><p><strong>What is visible.</strong> {inline(b["observed"])}</p><p><strong>Evidence.</strong> {inline(b["evidence"])}</p><p><strong>Decision.</strong> {inline(b["verdict"])}</p></article>')
            elif kind=='table':
                parts.append('<div class="research-table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+inline(h)+'</th>' for h in b['headers'])+'</tr></thead><tbody>')
                for row in b['rows']:parts.append('<tr>'+''.join(f'<td data-label="{html.escape(h,quote=True)}">{inline(t)}</td>' for h,t in zip(b['headers'],row))+'</tr>')
                parts.append('</tbody></table></div>')
            elif kind=='image':
                # The approved portrait and mask already occur on this page.
                # Keep their owning display and link to it rather than duplicate.
                is_mask='death-mask' in b['path']
                target='joseph-mask-comparison' if is_mask else 'likeness-title'
                label='Examine Joseph’s historical mask and the adopted portrait' if is_mask else 'Examine the unchanged adopted portrait'
                parts.append(f'<div class="research-reference"><a href="#{target}">{label} ↑</a></div>')
            else:raise ValueError('Unsupported content block '+kind)
        parts.append('<p class="research-return"><a href="#portrait-research">Return to research contents ↑</a></p></section>')
    parts.extend(['<div class="fc-actions"><a class="fc-button fc-button--primary" href="assets/research/focuschrist-joseph-evidence.pdf" download>Download the research PDF</a><a class="fc-button" href="#face-in-motion">Continue the illustrated study</a></div>','</section>',END])
    page=PAGE.read_text(encoding='utf-8')
    fragment='\n'.join(parts)
    if BEGIN in page:page=page.split(BEGIN)[0]+fragment+page.split(END)[1]
    else:page=page.replace('</main>',fragment+'\n</main>',1)
    css='<link rel="stylesheet" href="joseph-smith-research.css?v=20261003-research-1">'
    if css not in page:page=page.replace('</head>',css+'\n</head>',1)
    entry='<p class="joseph-research-entry">The research now follows the portrait feature by feature, from the shape preserved in the masks to written descriptions of hair, eyes and complexion. It also separates the documented creation of our image from the historical review that followed.</p><div class="fc-actions"><a class="fc-button fc-button--primary" href="#portrait-research">Read the complete portrait research</a></div>'
    if 'class="joseph-research-entry"' not in page:
        marker='<details class="likeness-evidence"><summary>Explore our process:'
        page=page.replace(marker,entry+'\n'+marker,1)
    PAGE.write_text(page,encoding='utf-8',newline='\n')
    print(json.dumps({'sections':len(sections),'excluded_paper_navigation':excluded,'image_reuse':'Existing portrait and mask owning displays linked, no repeated pixels','output':PAGE.name}))

if __name__=='__main__':build()
