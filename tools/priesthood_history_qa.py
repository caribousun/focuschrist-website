"""Source-led history, preserved parent bookmarks and official-media checks.

Source/content review and rendered accessibility remain separate requirements.
"""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib, json, sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CHILD = 'answers/race-priesthood-and-temple-blessings.html'
read = lambda p: (ROOT / p).read_text(encoding='utf-8')
data = json.loads(read('docs/priesthood-history/sections.json'))
media = json.loads(read('docs/priesthood-history/visuals.json'))
baseline = json.loads(read('docs/priesthood-history/existing-page-baseline.json'))
soup = BeautifulSoup(read(baseline['page']), 'html.parser')
assert hashlib.sha256(str(soup.select_one('header')).encode()).hexdigest() == baseline['header_sha256']
for key, digest in baseline['preserved_sections'].items():
    assert hashlib.sha256(str(soup.select_one('#' + key)).encode()).hexdigest() == digest, ('Preserve existing section', key)
assert set(baseline['image_sources']) <= {img.get('src') for img in soup.select('img')}
section = soup.select_one('#priesthood-and-temple-blessings')
assert section and not section.select(':scope > section'), 'Parent must introduce the dedicated study'
assert len(section.select(':scope > p')) >= 2
assert section.select_one('a[href="race-priesthood-and-temple-blessings.html"]')
assert soup.select_one('nav a[href="#priesthood-and-temple-blessings"]')
assert not section.select('[data-resource-key]'), 'History media belongs on its dedicated page'
child = BeautifulSoup(read(CHILD), 'html.parser')
main = child.select_one('main#main-content')
assert main and child.select_one('header.fc-source-opening h1').get_text() == data['title']
assert not child.select('[data-hero-viewer], [data-exclusive-artwork], [data-topic-art]'), 'Use official historical resources, not generated scenes'
assert set(media) == {row['id'] for row in data['sections']} and len(media) == 6
assert len({v['image'] for v in media.values()}) == 6
assert len(main.select('[data-resource-key]')) == 6
for row in data['sections']:
    bookmark = section.select_one('#' + row['id'])
    assert bookmark and bookmark.find_parent('details'), ('Retain parent bookmark', row['id'])
    assert bookmark.select_one('a')['href'] == CHILD.removeprefix('answers/') + '#' + row['id']
    unit = main.select_one('section#' + row['id'])
    narrative = unit.select(':scope > p:not(.fc-eyebrow):not(.fc-source-links)') if unit else []
    assert [p.get_text() for p in narrative] == row['paragraphs'], ('Published history differs from source-reviewed text', row['id'])
    elements = [el for el in unit.find_all(recursive=False) if 'fc-eyebrow' not in el.get('class', [])]
    assert elements[1].name == 'p' and 'fc-resource-grid' in elements[2].get('class', []), 'Picture follows first narrative paragraph'
    item = media[row['id']]
    card = unit.select_one('[data-resource-key]')
    image = card.select_one('img')
    assert card['data-resource-key'] == item['resource_key']
    assert image['src'] == item['image'] and image.find_parent('a')['href'] == item['url']
    assert image.find_parent('a').get('class') == ['fc-resource-card__image']
    assert (int(image['width']), int(image['height'])) == (item['width'], item['height'])
    assert item['reviewed'] and item['reuse_basis']
    assert urlsplit(item['image']).hostname == 'www.churchofjesuschrist.org'
    assert {s['url'] for s in row['sources']} <= {a['href'] for a in unit.select('a[href]')}
    assert child.select_one('nav a[href="#' + row['id'] + '"]')
    if '--remote-previews' in sys.argv:
        import io
        from urllib.request import urlopen
        from PIL import Image
        with urlopen(item['image'], timeout=30) as response:
            assert response.status == 200 and response.headers.get_content_type().startswith('image/')
            with Image.open(io.BytesIO(response.read())) as decoded:
                decoded.load()
                assert decoded.size == (item['width'], item['height'])
# Restrict study-source destinations, without changing the site's shared navigation.
for anchor in main.select('a[href]'):
    parsed = urlsplit(anchor['href'])
    if parsed.scheme or parsed.netloc:
        assert parsed.scheme == 'https' and parsed.hostname == 'www.churchofjesuschrist.org', ('Non-Church study source', anchor['href'])
text = main.get_text(' ', strip=True)
for fact in ('June 1, 1978', 'June 8', 'September 30', 'Ambrose Palmer', '1979'):
    assert fact in text
assert 'no documented revelation' in text and 'disavows' in text
assert len(main.select('#guided-practice details')) >= 3
assert main.select_one('#continue-study a[href="melchizedek-priesthood-restoration.html#priesthood-and-temple-blessings"]')
assert main.select_one('a[href*="ask.html?"]')
assert main.select_one('#begin-study a[href*="gospel-topics-essays/race-and-the-priesthood"]')
assert main.select_one('#begin-study a[href*="gospel-topics/race-and-the-church-of-jesus-christ-of-latter-day-saints"]')
temples = BeautifulSoup(read('answers/why-latter-day-saints-build-temples.html'), 'html.parser')
assert 'restriction' not in temples.select_one('#temple-worldwide-gathering').get_text().lower(), 'Do not associate the origins of the restriction with Hawaii'
assert temples.select_one('#temple-temples-today a[href="melchizedek-priesthood-restoration.html#priesthood-and-temple-blessings"]')
for page in (soup, child):
    ids = [el['id'] for el in page.select('[id]')]
    assert len(ids) == len(set(ids)), 'Duplicate page IDs'
print('PRIESTHOOD HISTORY PASS: source-led child, six Church-media units, parent bookmarks and original sections/art preserved; source review remains separate')
