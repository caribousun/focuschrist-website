"""Source-bound history, original-page preservation and remote-media checks."""
from pathlib import Path
import hashlib, json, sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
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
assert section and len(section.select(':scope > section')) == 6
assert soup.select_one('nav a[href="#priesthood-and-temple-blessings"]')
assert len({v['image'] for v in media.values()}) == 6
for row in data['sections']:
    unit = section.select_one('#' + row['id'])
    assert [p.get_text() for p in unit.select(':scope > p')[:2]] == row['paragraphs']
    elements = list(unit.find_all(recursive=False))
    assert elements[1].name == 'p' and 'fc-resource-grid' in elements[2].get('class', []), 'Picture follows first narrative paragraph'
    item = media[row['id']]
    image = unit.select_one('img')
    assert image['src'] == item['image'] and image.find_parent('a')['href'] == item['url']
    assert item['reviewed'] and item['reuse_basis']
    assert {s['url'] for s in row['sources']} <= {a['href'] for a in unit.select('a[href]')}
    if '--remote-previews' in sys.argv:
        import io
        from urllib.request import urlopen
        from PIL import Image
        with urlopen(item['image'], timeout=30) as response:
            assert response.status == 200 and response.headers.get_content_type().startswith('image/')
            with Image.open(io.BytesIO(response.read())) as decoded:
                decoded.load()
                assert decoded.size == (item['width'], item['height'])
text = section.get_text(' ', strip=True)
for fact in ('June 1, 1978', 'June 8', 'June 9', 'September 30', 'Ambrose Palmer', '1979'):
    assert fact in text
temples = BeautifulSoup(read('answers/why-latter-day-saints-build-temples.html'), 'html.parser')
assert 'restriction' not in temples.select_one('#temple-worldwide-gathering').get_text().lower(), 'Do not associate the origins of the restriction with Hawaii'
assert temples.select_one('#temple-temples-today a[href="melchizedek-priesthood-restoration.html#priesthood-and-temple-blessings"]')
ids = [el['id'] for el in soup.select('[id]')]
assert len(ids) == len(set(ids))
print('PRIESTHOOD HISTORY PASS: six source-bound illustrated units; original hero/sections/art preserved; dated events and Temple relocation verified')
