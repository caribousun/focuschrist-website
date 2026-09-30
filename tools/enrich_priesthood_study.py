"""Apply source-reviewed prose and twelve original, source-grounded artwork studies."""
from pathlib import Path
import html, json, re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'answers/race-priesthood-and-temple-blessings.html'
esc = lambda value: html.escape(str(value), quote=True)

def life_stories(soup):
    """Curate duplicated biographies into explicit, source-linked story blocks."""
    load=lambda name: json.loads((ROOT/'docs/priesthood-history'/name).read_text(encoding='utf-8'))
    e=load('elijah-able-study.json'); parts=e['sections']
    sources={x['id']:{'label':'Read the Church account','url':x['url']} for x in e['sources']}
    blocks=[
        {'title':'Faith and a missionary’s care','paragraphs':parts[0]['paragraphs'][:2]+parts[1]['paragraphs'],'sources':[sources['history'],sources['mission']]},
        {'title':'Work, family and a westward journey','paragraphs':[parts[0]['paragraphs'][2],parts[2]['paragraphs'][0]],'sources':[sources['history'],sources['database']]},
        {'title':'Continuing to serve and seeking temple blessings','paragraphs':[parts[0]['paragraphs'][3]]+parts[2]['paragraphs'][1:],'sources':[sources['history'],sources['database']]}
    ]
    green=load('green-flake-study.json')
    stories={'elijah-able':blocks,'jane-manning-james':load('jane-story.json')['subsections'],
             'green-flake':[{'title':x['heading'],'html':x['html']} for x in green['paragraphs']]}
    if not soup.select_one('#green-flake'):
        soup.select_one('#jane-manning-james').insert_after(BeautifulSoup('<section class="fc-deep-study" id="green-flake" aria-labelledby="green-flake-heading"><p class="fc-eyebrow">Remember and study</p><h2 id="green-flake-heading">Green Flake: a life beyond the trail</h2></section>','html.parser'))
    for directory in soup.select('.fc-source-directory nav, main > nav[aria-label="Study path"]'):
        if not directory.select_one('a[href="#green-flake"]'):
            directory.select_one('a[href="#jane-manning-james"]').insert_after(BeautifulSoup('<a href="#green-flake">Green Flake</a>','html.parser'))
    for n,section in enumerate(['restriction-history','elijah-able','jane-manning-james','green-flake','faith-across-nations','revelation-1978','belonging-and-responsibility'],1):
        soup.select_one('#'+section+' > .fc-eyebrow').string=f'{n:02d} · Remember and study'
    for section,rows in stories.items():
        unit=soup.select_one('#'+section)
        for old in list(unit.select(':scope > p:not(.fc-eyebrow):not(.fc-source-links)')): old.decompose()
        wrapper=soup.new_tag('div',attrs={'data-history-life':section})
        for index,row in enumerate(rows):
            block=soup.new_tag('div',attrs={'data-history-block':str(index)})
            markup='<h3>'+esc(row['title'])+'</h3>'
            markup+=row.get('html',''.join('<p>'+esc(p)+'</p>' for p in row.get('paragraphs',[])))
            if row.get('sources'):
                markup+='<p class="fc-source-links">'+' '.join('<a href="'+esc(x['url'])+'" target="_blank" rel="noopener noreferrer">'+esc(x['label'])+'</a>' for x in row['sources'])+'</p>'
            block.append(BeautifulSoup(markup,'html.parser'));wrapper.append(block)
        unit.select_one('h2').insert_after(wrapper)

def enrich():
    soup = BeautifulSoup(PAGE.read_text(encoding='utf-8'), 'html.parser')
    prose = json.loads((ROOT/'docs/priesthood-history/deeper-study.json').read_text(encoding='utf-8'))
    pictures = json.loads((ROOT/'docs/priesthood-history/body-pictures.json').read_text(encoding='utf-8'))
    for old in soup.select('[data-enrichment-study], .fc-history-picture, [data-history-life]'):
        old.decompose()
    if any(p.get('placement',{}).get('kind')=='story-block' for p in pictures):
        life_stories(soup)
    for section, markup in prose.items():
        soup.select_one('#'+section).append(BeautifulSoup(markup,'html.parser'))
    for n, item in enumerate(pictures):
        candidates = [item['scripture'], item['doctrine'], {'label': 'Historical source' if item['artwork_kind']=='historical interpretation' else 'Study source', 'url':item['source']}]
        sources = list({entry['url']: entry for entry in reversed(candidates)}.values())[::-1]
        links = ' '.join(f'<a class="fc-inline-scripture" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>' if '/scriptures/' in s['url'] else f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>' for s in sources)
        caption=esc(item['caption']).replace('Official Declaration 2','<a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/dc-testament/od/2?lang=eng">Official Declaration 2</a>')
        markup = f'''<figure class="fc-history-picture" id="picture-history-{item['id']}">
<a href="/{item['asset']}" aria-haspopup="dialog" aria-label="Explore picture: {esc(item['study_title'])}"><img src="/{item['asset']}" width="{item['width']}" height="{item['height']}" loading="lazy" decoding="async" alt="{esc(item['alt'])}"></a>
<figcaption><p class="fc-study-visual-label">Picture and study</p><h3>{esc(item['study_title'])}</h3><p>{caption}</p><p class="fc-study-visual-sources">{links}</p></figcaption></figure>'''
        figure = BeautifulSoup(markup,'html.parser')
        unit = soup.select_one('#'+item['section'])
        placement=item['placement']
        if placement['kind']=='story-block':
            block=unit.select_one('[data-history-block="'+str(placement['block'])+'"]')
            paragraphs=block.select(':scope > p:not(.fc-source-links)')
            paragraphs[min(placement.get('after_paragraph',1),len(paragraphs))-1].insert_after(figure)
        elif placement['kind']=='narrative-start':
            unit.select_one(':scope > p:not(.fc-eyebrow)').insert_after(figure)
        elif placement['kind']=='deeper-second-heading':
            deeper=unit.select_one('[data-enrichment-study]')
            deeper.select('h3')[1].insert_before(figure)
    for asset in ['artwork-details.css?v=20260909-warm','artwork-actions.css?v=20260929-picture-source-pills-1','topic-artwork-details.css?v=20260927-anchor-alignment-1','full-image-viewer.css?v=20260905-viewport']:
        filename=asset.split('?')[0]
        for old in list(soup.select('link[href]')):
            if old['href'].split('?')[0].split('/')[-1]==filename: old.decompose()
        tag=soup.new_tag('link',rel='stylesheet',href='../'+asset);soup.head.append(tag)
    for asset in ['topic-artwork-details.js?v=20260930-history-records-1','full-image-viewer.js?v=20260914-reopen-1']:
        if not soup.select_one('script[src*="'+asset.split('?')[0]+'"]'):
            tag=soup.new_tag('script',src='../'+asset,defer='');soup.body.append(tag)
    soup.select_one('link[href*="priesthood-history-study.css"]')['href']='../priesthood-history-study.css?v=20260930-enriched-4'
    common=soup.select_one('script[src*="site-common.js"]')
    if common: common['src']='../site-common.js?v=20260930-art-disclosure-3'
    for node in list(soup.main.find_all(string=re.compile('Official Declaration 2'))):
        if node.find_parent('a'): continue
        markup=esc(str(node)).replace('Official Declaration 2','<a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/dc-testament/od/2?lang=eng">Official Declaration 2</a>')
        node.replace_with(BeautifulSoup(markup,'html.parser'))
    for link in soup.select('a[href]'):
        if link['href'].startswith(('https://','http://')):
            link['target']='_blank'; link['rel']=['noopener','noreferrer']
    PAGE.write_text(str(soup),encoding='utf-8',newline='\n')

if __name__ == '__main__':
    enrich()
