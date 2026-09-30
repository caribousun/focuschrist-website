"""Assemble the source-reviewed priesthood history, preserving existing page sections."""
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/priesthood-history/sections.json'
MEDIA = ROOT / 'docs/priesthood-history/visuals.json'
PAGE = ROOT / 'answers/melchizedek-priesthood-restoration.html'
START = '<!-- priesthood-blessings-history:start -->'
END = '<!-- priesthood-blessings-history:end -->'
esc = lambda s: html.escape(str(s), quote=True)

def link(label, url, cls=''):
    return f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'

def prose(text):
    return esc(text).replace('Official Declaration 2', link('Official Declaration 2', 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/od/2?lang=eng', 'fc-inline-scripture'))

def build():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    media = json.loads(MEDIA.read_text(encoding='utf-8'))
    assert set(media) == {s['id'] for s in data['sections']}, 'Every history unit needs meaningful verified media'
    for item in media.values():
        assert item.get('resource_key') and item.get('reviewed') and item.get('reuse_basis') and item.get('width') and item.get('height')
    out = [START, f'<section class="fc-deep-study" id="{esc(data["anchor"])}" aria-labelledby="priesthood-blessings-heading">',
           f'<h2 id="priesthood-blessings-heading">{esc(data["title"])}</h2>', f'<p>{esc(data["introduction"])}</p>']
    for section in data['sections']:
        item = media[section['id']]
        out += [f'<section id="{esc(section["id"])}" aria-labelledby="{esc(section["id"])}-heading">',
                f'<h3 id="{esc(section["id"])}-heading">{esc(section["title"])}</h3>',
                f'<p>{prose(section["paragraphs"][0])}</p>']
        out += [f'<div class="fc-resource-grid"><article class="fc-resource-card" data-resource-key="{esc(item["resource_key"])}"><a class="fc-resource-card__image" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(item["action"])}"><img src="{esc(item["image"])}" width="{item["width"]}" height="{item["height"]}" alt="{esc(item["alt"])}" loading="lazy" decoding="async"><span class="fc-resource-card__play" aria-hidden="true">▶</span></a><div class="fc-resource-card__body"><p class="fc-resource-card__kind">{esc(item["kind"])}</p><h4>{link(item["action"], item["url"])}</h4><p>{esc(item["caption"])}</p><p class="fc-resource-card__source">{esc(item["credit"])}</p></div></article></div>']
        out += [f'<p>{prose(p)}</p>' for p in section['paragraphs'][1:]]
        out += ['<p class="fc-study-visual-sources">' + ' '.join(link(s['label'], s['url']) for s in section['sources']) + '</p></section>']
    out += ['<h3>Read the scriptures in context</h3><p>Read the declaration alongside scripture about God’s invitation to all His children and the responsibility to serve with gentleness.</p><div class="fc-actions">',
            ' '.join(link(s['label'],s['url'],'fc-button fc-inline-scripture') for s in data['scriptures']),
            '</div></section>', END]
    text = PAGE.read_text(encoding='utf-8')
    block = '\n'.join(out)
    if START in text:
        text = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        anchor = '<section class="fc-deep-study" id="service-study">'
        assert anchor in text
        text = text.replace(anchor, block + '\n' + anchor, 1)
        text = text.replace('<a href="#service-study">Serve with care</a>', '<a href="#priesthood-and-temple-blessings">Lives and the 1978 revelation</a><a href="#service-study">Serve with care</a>', 1)
    PAGE.write_text(text, encoding='utf-8', newline='\n')

if __name__ == '__main__':
    build()
