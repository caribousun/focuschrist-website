"""Release completeness gate for the owner-authorized temple-history expansion."""
from pathlib import Path
from collections import Counter
import hashlib
import json
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'answers/why-latter-day-saints-build-temples.html'

def check():
    soup = BeautifulSoup((ROOT / PAGE).read_text(encoding='utf-8'), 'html.parser')
    baseline = json.loads((ROOT / 'docs/temples/existing-page-baseline.json').read_text(encoding='utf-8'))
    current_sources = {img.get('src') for img in soup.select('img')}
    assert set(baseline['required_image_srcs']) <= current_sources, 'Preserve existing images and reference links'
    assert hashlib.sha256(str(soup.select_one('header')).encode()).hexdigest() == baseline['header_sha256'], 'Temple expansion must preserve existing hero markup'
    raw = json.loads((ROOT / 'docs/temples/chapters.json').read_text(encoding='utf-8-sig'))
    chapters = raw if isinstance(raw, list) else raw['chapters']
    ready = json.loads((ROOT / 'docs/temples/art-ready.json').read_text(encoding='utf-8-sig'))
    figures = soup.select('#temple-history figure[data-exclusive-artwork]')
    assert len(figures) >= 15 and len(figures) == len(chapters), 'At least fifteen additional originals, every chapter illustrated'
    expected = {c['art_id'] for c in chapters}
    assert {f.get('data-exclusive-artwork') for f in figures} == expected
    assert len(soup.select('#temple-history .fc-temple-history__chapter')) == len(chapters)
    ids = Counter(el.get('id') for el in soup.select('[id]'))
    assert all(count == 1 for count in ids.values()), 'Unique chapter/picture/heading IDs'
    pixels = set()
    for chapter in chapters:
        figure = soup.select_one(f'figure[data-exclusive-artwork="{chapter["art_id"]}"]')
        record = ready[chapter['art_id']]
        assert record.get('reviewed') is True, 'Reviewed art required'
        assert figure.select_one('a').get('href') == '../' + record['full']
        for key in ('full', 'thumbnail'):
            file = ROOT / record[key]
            assert file.is_file(), file
            with Image.open(file) as image:
                if key == 'full':
                    assert image.size == (record['width'], record['height'])
                    digest = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
                    assert digest not in pixels, 'Renamed duplicate image cannot count as another original'
                    pixels.add(digest)
        links = figure.select('figcaption .fc-study-visual-sources a[href]')
        assert links and all(urlsplit(a.get('href')).hostname in ('www.churchofjesuschrist.org', 'newsroom.churchofjesuschrist.org', 'www.josephsmithpapers.org') for a in links)
        assert [a.get('href') for a in links] == [s['url'] for s in chapter['sources'][:3]], 'Exact chapter source destinations'
        section = figure.parent
        section_urls = {a.get('href') for a in section.select('a[href]')}
        assert {s['url'] for s in chapter['sources']} <= section_urls, 'Long source lists must not silently lose fourth and later citations'
    for a in soup.select('#temple-history a[href^="#"]'):
        assert a.get('href')[1:] in ids, 'Broken chapter navigation'
    assert len(soup.select('details')) >= 3
    assert len(soup.select('#continue-study a[href]')) >= 3
    assert soup.select('script[src^="../topic-artwork-details.js"]')
    print(f'Temple completeness QA passed: {len(chapters)} additional distinct originals; existing images and hero preserved; sources, chapters, reflections and onward study present.')

if __name__ == '__main__':
    check()
