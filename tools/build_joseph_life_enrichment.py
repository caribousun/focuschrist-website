"""Render accepted Joseph family illustrations without exposing draft slots."""
import html
import json
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

def build():
    data = json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8-sig'))
    accepted = [s for s in data['scenes'] if s.get('image_status') == 'accepted' and s.get('image')]
    for s in accepted:
        if not (ROOT/s['image']['src']).is_file():
            raise ValueError('Accepted image missing: '+s['id'])
    delivery=json.loads((ROOT/'docs/joseph-art-delivery.json').read_text(encoding='utf-8'))
    out = [START, '<section id="joseph-family-life" class="likeness-chapter joseph-life-enrichment"><p class="fc-eyebrow">Faith in daily life</p><h2>Family, service and remembrance</h2><p>Meet Joseph, Emma and Hyrum through documented moments of work, love and faith. These new illustrations invite reflection; the sources beside them distinguish recorded history from artistic interpretation.</p>']
    out.append('<nav class="joseph-life-nav" aria-label="Family and service scenes">'+''.join(f'<a href="#life-{esc(s["id"])}">{esc(s["heading"])}</a>' for s in accepted)+'<a href="#life-remembrance">Forgiveness and remembrance</a></nav>')
    for s in accepted:
        im=s['image']; sid='life-'+s['id']; title=esc(s['heading']); alt=esc(im['alt']); src=esc(im['src'])
        delivered=delivery[im['src']]
        image_src=esc(delivered['default'])
        srcset=esc(', '.join(v['asset']+' '+str(v['width'])+'w' for v in delivered['variants']))
        out.append(f'<article id="{sid}" class="joseph-life-scene"><p class="fc-eyebrow">{esc(s["date_label"])}</p><h3>{title}</h3>')
        out.extend('<p>'+esc(p)+'</p>' for p in s['paragraphs'])
        out.append(f'<figure class="fc-study-visual likeness-art" data-enriched-study-art="{sid}" data-exclusive-artwork="{sid}"><a href="{src}" aria-haspopup="dialog" aria-label="Explore artwork: {title}" data-full-image-alt="{alt}" data-topic-study="joseph-smith-likeness.html#{sid}" data-topic-study-label="Return to this family study"><img src="{image_src}" data-source-original="{src}" srcset="{srcset}" sizes="(max-width: 600px) 94vw, 100vw" width="{im["width"]}" height="{im["height"]}" alt="{alt}" loading="lazy" decoding="async"></a><figcaption><h4 class="joseph-life-caption-title" hidden>{title}</h4><p class="fc-study-visual-label">New artistic interpretation</p><p>{esc(s["interpretation_limit"])}</p>{sources(s)}</figcaption></figure>')
        out.append('<p class="joseph-life-reflection"><strong>Consider:</strong> '+esc(s['reflection'])+'</p></article>')
    c=data['closing'];out.append('<section id="life-remembrance" class="joseph-life-closing"><h3>'+esc(c['heading'])+'</h3>')
    out.extend('<p>'+esc(p)+'</p>' for p in c['paragraphs'])
    out.extend(['<p class="joseph-life-source-note">'+esc(c['interpretation_limit'])+'</p>',sources(c),'<p class="joseph-life-reflection"><strong>Consider:</strong> '+esc(c['reflection'])+'</p></section></section>',END])
    block='\n'.join(out);path=ROOT/'joseph-smith-likeness.html';page=path.read_text(encoding='utf-8')
    if START in page:
        a=page.index(START);b=page.index(END,a)+len(END);page=page[:a]+block+page[b:]
    else:
        marker='<section id="continue-study"'
        if marker not in page: raise ValueError('Insertion anchor missing')
        page=page.replace(marker,block+'\n'+marker,1)
    path.write_text(page,encoding='utf-8',newline='\n')
    print(f'Rendered {len(accepted)} accepted scenes; draft slots omitted.')

if __name__=='__main__': build()
