"""Guard study grids against empty desktop cells and orphaned narrow media.

Structural regression gate; desktop/phone rendering remains a separate check.
"""
import argparse
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PAIRS = {'birth-of-christ.html': 4, 'answers/what-happens-after-death.html': 3, 'answers/what-is-the-book-of-mormon.html': 6}


def style(node):
    return {key.strip().lower(): re.sub(r'\s+', '', value).lower()
            for key, value in re.findall(r'([\w-]+)\s*:\s*([^;]+)', node.attrs.get('style', ''))}


def inspect_html(html, label):
    doc = Document(); doc.feed(html)
    nodes = list(doc.root.walk()); errors = []; pair_count = 0
    images = Counter(n.attrs.get('src') for n in nodes if n.tag == 'img')
    for node in nodes:
        if node.has('fc-study-grid'):
            children = node.children
            if children and len(children) % 2 and all(c.tag == 'article' for c in children):
                last = children[-1]
                if style(last).get('grid-column') != '1/-1':
                    errors.append(f'{label}: odd article study grid leaves an empty cell')
        if node.has('fc-resource-grid'):
            section = node.parent
            protected = section and section.attrs.get('aria-labelledby') == 'bom-watch-title'
            if protected or 'data-balanced-resource-row' in node.attrs:
                css = style(node)
                if node.attrs.get('data-balanced-resource-row') != 'wrap' or css.get('display') != 'flex' or css.get('flex-wrap') != 'wrap':
                    errors.append(f'{label}: resource row must wrap and fill available width')
                if len(node.children) != 3 or any(not child.has('fc-resource-card') or style(child).get('flex') != '11260px' for child in node.children):
                    errors.append(f'{label}: all three resource cards must grow to fill their row')
        if node.has('fc-study-media-row'):
            parent = node.parent
            while parent and not parent.has('fc-study-feature--illustrated'):
                parent = parent.parent
            if parent is None:
                errors.append(f'{label}: narrow media row lacks illustrated layout ancestor')
        if node.has('fc-study-media-pair'):
            pair_count += 1
            css = style(node)
            if css.get('display') != 'grid' or css.get('grid-template-columns') != 'repeat(auto-fit,minmax(min(100%,300px),1fr))' or css.get('gap') != '24px' or css.get('align-items') != 'start':
                errors.append(f'{label}: media pair lost responsive desktop/phone grid')
            figures = [n for n in node.children if n.tag == 'figure' and n.has('fc-study-visual')]
            cards = [n for n in node.children if n.tag == 'article' and n.has('fc-resource-card')]
            if len(node.children) != 2 or len(figures) != 1 or len(cards) != 1:
                errors.append(f'{label}: media pair must contain exactly one artwork and one resource')
            if node.attrs.get('data-bom-story-resource') and any(style(card).get('width') != '100%' or style(card).get('max-width') != 'none' for card in cards):
                errors.append(f'{label}: Book of Mormon paired resource retains narrow width cap')
            for figure in figures:
                art_images = [n for n in figure.walk() if n.tag == 'img']
                if len(art_images) != 1 or any(not n.attrs.get('src') or images[n.attrs['src']] != 1 for n in art_images):
                    errors.append(f'{label}: paired artwork is missing or repeated elsewhere on page')
    return errors, pair_count


def self_test():
    pair = '<div class="fc-study-media-pair" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:24px;align-items:start"><article class="fc-resource-card"><img src="video.jpg"></article><figure class="fc-study-visual"><img src="art.webp"></figure></div>'
    grid = '<div class="fc-study-grid"><article></article><article></article><article style="grid-column:1 / -1"></article></div>'
    resource_row = '<section aria-labelledby="bom-watch-title"><div class="fc-resource-grid" data-balanced-resource-row="wrap" style="display:flex;flex-wrap:wrap">' + '<article class="fc-resource-card" style="flex:1 1 260px"></article>' * 3 + '</div></section>'
    positive = resource_row + grid + pair + '<div class="fc-study-feature--illustrated"><div class="fc-study-media-row"></div></div>'
    assert not inspect_html(positive, 'positive')[0]
    cases = {
        'orphaned third resource': resource_row.replace('flex:1 1 260px', 'flex:0 1 260px'),
        'missing resource balance': resource_row.replace(' data-balanced-resource-row="wrap"', ''),
        'nonwrapping resources': resource_row.replace('flex-wrap:wrap', 'flex-wrap:nowrap'),
        'empty fourth cell': grid.replace(' style="grid-column:1 / -1"', ''),
        'standalone media row': '<div class="fc-study-media-row"></div>',
        'fixed desktop pair': pair.replace('repeat(auto-fit,minmax(min(100%,300px),1fr))', '1fr 1fr'),
        'missing paired artwork': pair.replace('<figure class="fc-study-visual"><img src="art.webp"></figure>', ''),
        'repeated artwork': pair + '<img src="art.webp">',
    }
    for name, html in cases.items():
        assert inspect_html(html, name)[0], f'negative fixture escaped: {name}'
    print(f'Study section balance self-test PASS: positive and {len(cases)} negative fixtures')


def check():
    pages = sorted({urlsplit(n.text).path.lstrip('/') or 'index.html'
                    for n in ET.parse(ROOT / 'sitemap.xml').getroot().findall('{*}url/{*}loc')
                    if urlsplit(n.text).path.endswith('.html') or urlsplit(n.text).path == '/'})
    errors = []; pairs = {}
    for page in pages:
        path = ROOT / page
        if not path.is_file():
            errors.append(f'{page}: canonical HTML missing'); continue
        found, count = inspect_html(path.read_text(encoding='utf-8'), page)
        errors.extend(found)
        if count: pairs[page] = count
    for page, expected in EXPECTED_PAIRS.items():
        if pairs.get(page, 0) != expected:
            errors.append(f'{page}: expected {expected} preserved media/art pairings')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'Study section balance QA PASS: {len(pages)} canonical pages; {sum(pairs.values())} responsive media/art pairs; no orphaned narrow rows or odd article-grid holes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    self_test() if args.self_test else check()
