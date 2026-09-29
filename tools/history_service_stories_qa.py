"""Guard the three sourced lives, official film destinations, and temple connections."""
from pathlib import Path
import json
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
soup = BeautifulSoup((ROOT / 'church-history.html').read_text(encoding='utf-8'), 'html.parser')
stories = {
    'john-tanner': '2010-07-0139-treasure-in-heaven-the-john-tanner-story',
    'eleazer-miller': '2010-07-0048-a-man-without-eloquence',
    'john-rowe-moyle': '2010-07-0140-only-a-stonecutter',
}
for key, slug in stories.items():
    nodes = soup.select('#' + key)
    assert len(nodes) == 1, key
    section = nodes[0]
    paragraphs = section.select(':scope > div > article > p')[:4]
    count = sum(len(p.get_text(' ', strip=True).split()) for p in paragraphs)
    assert 250 <= count <= 350, (key, count)
    assert soup.select_one(f'nav[aria-label="Stories of testimony and service"] a[href="#{key}"]')
    scripture = section.select('a.fc-inline-scripture')
    assert len(scripture) == 2 and all('/study/scriptures/' in a['href'] and '#p' in a['href'] for a in scripture)
    media = section.select_one('.fc-resource-card__image')
    assert media['href'] == 'https://www.churchofjesuschrist.org/media/video/' + slug + '?lang=eng'
    assert media.select_one('img')['src'].startswith('https://www.churchofjesuschrist.org/imgs/')
    assert '/full/!640,/0/default' in media.select_one('img')['src'], 'Use the verified official video poster, not an unverified social crop'
    if '--remote-previews' in sys.argv:
        import io
        from urllib.request import urlopen
        from PIL import Image
        img = media.select_one('img')
        with urlopen(img['src'], timeout=30) as response:
            assert response.status == 200 and response.headers.get_content_type().startswith('image/'), key
            with Image.open(io.BytesIO(response.read())) as decoded:
                decoded.load()
                assert decoded.size == (int(img['width']), int(img['height'])), (key, decoded.size)
    assert 'Dramatization' in section.get_text() and 'The Church of Jesus Christ of Latter-day Saints' in section.get_text()
    assert not section.select('[data-exclusive-artwork], [data-topic-art]'), 'Official film previews are not original artwork'
chapters = json.loads((ROOT / 'docs/temples/chapters.json').read_text(encoding='utf-8'))
temples = BeautifulSoup((ROOT / 'answers/why-latter-day-saints-build-temples.html').read_text(encoding='utf-8'), 'html.parser')
for chapter_id, story_id in [('kirtland-house','john-tanner'),('salt-lake-building','john-rowe-moyle')]:
    chapter = next(c for c in chapters if c['id'] == chapter_id)
    expected = '../church-history.html#' + story_id
    assert chapter['related_study']['url'] == expected
    assert temples.select_one(f'#temple-{chapter_id} a[href="{expected}"]')
assert '1889' in soup.select_one('#john-rowe-moyle').get_text()
assert 'Carter reported' in soup.select_one('#john-tanner').get_text()
print('PASS: three sourced narrative entries, six verse destinations, three official films, two temple connections')
