"""Render the two reviewed Joseph leading artworks from their exact asset records."""
from pathlib import Path
import html
import json
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]

def hero_markup(key):
    data = json.loads((ROOT/'docs/joseph-hero-openings.json').read_text(encoding='utf-8'))
    record = data['heroes'][key]
    if record.get('status') != 'accepted':
        raise ValueError('Joseph leading artwork must have both finished-image reviews before use')
    original = record['asset']
    if not (ROOT/original).is_file():
        raise ValueError('Reviewed Joseph original is missing')
    esc = lambda value: html.escape(str(value), quote=True)
    variants = ', '.join(f"{item['asset']} {item['width']}w" for item in record['delivery']['variants'])
    route = 'joseph-smith-likeness.html' if key == 'gateway' else 'joseph-smith-portrait-research.html'
    ask = '/ask.html?' + urlencode({'art': 'Joseph Smith by the river' if key == 'gateway' else 'Joseph Smith and the portrait study',
                                  'topic': 'Joseph Smith and the historical evidence for his likeness',
                                  'return': '/' + route + '?hero=1'}) + '#ask-question'
    return (f'<a class="fc-visual-hero joseph-leading-hero" data-hero-viewer data-hero-record="{esc(record["record"])}" '
            f'data-exclusive-artwork="{esc(record["record"])}" aria-haspopup="dialog" href="{esc(original)}" '
            f'aria-label="Explore the Joseph Smith artwork and study options" data-full-image-alt="{esc(record["alt"])}" data-hero-ask="{esc(ask)}">'
            f'<img src="{esc(record["delivery"]["default"])}" srcset="{esc(variants)}" sizes="(max-width: 700px) 900px, 100vw" '
            f'width="{record["width"]}" height="{record["height"]}" alt="{esc(record["alt"])}" '
            f'fetchpriority="high" decoding="async" data-source-original="{esc(original)}"></a>')
