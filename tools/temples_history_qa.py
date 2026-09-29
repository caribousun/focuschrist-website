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

def assert_clean_source_text(text):
    for corrupt in ('\u00e2\u20ac\u201c', '\u00e2\u0080\u0093', '\ufffd'):
        assert corrupt not in text, 'Temple source text contains corrupted Unicode punctuation'

def check():
    soup = BeautifulSoup((ROOT / PAGE).read_text(encoding='utf-8'), 'html.parser')
    baseline = json.loads((ROOT / 'docs/temples/existing-page-baseline.json').read_text(encoding='utf-8'))
    current_sources = {img.get('src') for img in soup.select('img')}
    assert set(baseline['required_image_srcs']) <= current_sources, 'Preserve existing images and reference links'
    assert hashlib.sha256(str(soup.select_one('header')).encode()).hexdigest() == baseline['header_sha256'], 'Temple expansion must preserve existing hero markup'
    source_text = (ROOT / 'docs/temples/chapters.json').read_text(encoding='utf-8-sig')
    assert_clean_source_text(source_text)
    assert_clean_source_text((ROOT / PAGE).read_text(encoding='utf-8'))
    assert_clean_source_text('Moses 5:4\u201312')
    for corrupt in ('\u00e2\u20ac\u201c', '\u00e2\u0080\u0093', '\ufffd'):
        try:
            assert_clean_source_text('Moses 5:4' + corrupt + '12')
        except AssertionError:
            pass
        else:
            raise AssertionError('Corrupted-punctuation negative fixture escaped detection')
    raw = json.loads(source_text)
    chapters = raw if isinstance(raw, list) else raw['chapters']
    ready = json.loads((ROOT / 'docs/temples/art-ready.json').read_text(encoding='utf-8-sig'))
    nephi_review = json.loads((ROOT / 'docs/temples/nephi-source-first-review-20260929.json').read_text(encoding='utf-8'))
    rejected_hashes = {item['sha256'] for item in nephi_review['rejected']}
    nephi = ready['temple-nephite-temple']
    assert nephi['full'] == 'assets/page-art/temples/temple-nephite-timber-pattern-full.webp'
    assert nephi['source_sha256'] not in rejected_hashes
    assert hashlib.sha256((ROOT / nephi['full']).read_bytes()).hexdigest() == nephi_review['accepted']['sha256']
    for rejected in nephi_review['rejected']:
        if rejected.get('asset'):
            assert not (ROOT / rejected['asset']).exists(), 'Rejected Nephi artwork must not return'
    for asset in (ROOT / 'assets/page-art/temples').glob('*.webp'):
        assert hashlib.sha256(asset.read_bytes()).hexdigest() not in rejected_hashes, 'Renamed rejected Nephi artwork must not return'
    nephi_chapter = next(c for c in chapters if c['id'] == 'nephite-temple')
    assert 'artistic interpretation' in nephi_chapter['caption'].lower()
    assert 'exact appearance and materials are not recorded' in nephi_chapter['caption']
    figures = soup.select('#temple-history figure[data-exclusive-artwork]')
    pictures = [picture for chapter in chapters for picture in [chapter, *chapter.get('companions', [])]]
    assert len(chapters) == 20 and len(pictures) == 21, 'Twenty chapters plus one requested same-building companion'
    assert len(soup.select('figure[data-temple-companion="nephite-temple"]')) == 1
    assert len(chapters) >= 15 and len(figures) == len(pictures), 'Every chapter and explicitly requested companion illustrated'
    expected = {c['art_id'] for c in pictures}
    assert {f.get('data-exclusive-artwork') for f in figures} == expected
    assert len(soup.select('#temple-history .fc-temple-history__chapter')) == len(chapters)
    ids = Counter(el.get('id') for el in soup.select('[id]'))
    assert all(count == 1 for count in ids.values()), 'Unique chapter/picture/heading IDs'
    pixels = set()
    for chapter in pictures:
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
    print(f'Temple completeness QA passed: {len(chapters)} chapters and one requested companion; existing images and hero preserved; sources, chapters, reflections and onward study present.')

if __name__ == '__main__':
    check()
