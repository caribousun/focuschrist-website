"""Independently compare the illustrated PDF with the current research page."""
from pathlib import Path
import hashlib, json, re, unicodedata
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import fitz

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'joseph-smith-portrait-research.html'
PDF = ROOT / 'assets/research/focuschrist-joseph-evidence.pdf'
BASE = 'https://focuschrist.com/joseph-smith-portrait-research.html'

def norm(value):
    value = unicodedata.normalize('NFKD', value).casefold()
    return ''.join(c for c in value if c.isalnum())

def main():
    soup = BeautifulSoup(HTML.read_text(encoding='utf-8'), 'html.parser')
    roots = soup.select('section.research-part, section.research-study-onward')
    assert len(soup.select('section.research-part')) == 15
    assert len(soup.select('.research-feature-study')) == 16
    document = fitz.open(PDF)
    text = '\n'.join(page.get_text() for page in document)
    normalized = norm(text)
    missing = []
    checked = 0
    for root in roots:
        for element in root.select('h2,h3,h4,p,td,th,li,dt,dd'):
            # Repeated web section/feature eyebrows are replaced by book running
            # heads and section numbers; they carry no research content.
            if element.find_parent('nav') or 'fc-eyebrow' in element.get('class', []):
                continue
            value = element.get_text(' ', strip=True)
            if len(norm(value)) < 4:
                continue
            checked += 1
            if norm(value) not in normalized:
                missing.append(value)
    links = [link for page in document for link in page.get_links()]
    actual_uris = {link.get('uri') for link in links if link.get('uri')}
    expected_uris = {urljoin(BASE, a['href']) for root in roots for a in root.select('a[href]')
                     if not a['href'].startswith('#') and not a.find('img') and not a.find_parent('nav')}
    missing_uris = sorted(expected_uris - actual_uris)
    original_uris = {urljoin(BASE, figure.select_one('a:has(img)')['href'])
                     for figure in soup.select('figure[data-research-art]')}
    missing_original_uris = sorted(original_uris - actual_uris)
    image_placements = sum(len(p.get_image_info()) for p in document)
    expected_image_placements = len(soup.select('figure')) + 1  # Cover portrait.
    bookmarks = document.get_toc()
    expected_bookmarks = 1 + len(soup.select('section.research-part')) + len(soup.select('.research-feature-study')) + 1
    bad_internal = [x for x in links if x.get('kind') == fitz.LINK_GOTO and not 0 <= x.get('page', -1) < len(document)]
    empty_pages = [i+1 for i,p in enumerate(document) if len(norm(p.get_text())) < 15 and not p.get_images()]
    out_of_bounds = []
    for i,page in enumerate(document):
        for word in page.get_text('words'):
            if word[0] < -1 or word[1] < -1 or word[2] > page.rect.width+1 or word[3] > page.rect.height+1:
                out_of_bounds.append({'page':i+1,'word':word[4]})
    report = {'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
              'html_sha256':hashlib.sha256(HTML.read_bytes()).hexdigest(),
              'pages':len(document),'substantive_text_blocks_checked':checked,
              'missing_text':missing,'expected_external_links':len(expected_uris),
              'missing_external_links':missing_uris,'link_annotations':len(links),
              'bad_internal_links':bad_internal,'empty_pages':empty_pages,
              'out_of_page_text':out_of_bounds,'bookmarks':len(bookmarks),
              'expected_bookmarks':expected_bookmarks,
              'image_placements':image_placements,'expected_image_placements':expected_image_placements,
              'original_image_links':len(original_uris),'missing_original_image_links':missing_original_uris,
              'limits':'Text/link/geometry checks do not replace independent rendered-page visual review.'}
    report['pass'] = not (missing or missing_uris or missing_original_uris or bad_internal or empty_pages or out_of_bounds) and image_placements == expected_image_placements and len(bookmarks) == expected_bookmarks and len(original_uris) == 10
    print(json.dumps(report,ensure_ascii=False,indent=2))
    assert report['pass'], 'PDF is incomplete or has invalid links/page geometry'

if __name__ == '__main__':
    main()
