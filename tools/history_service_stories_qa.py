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
    entry = soup.select_one('#' + key)
    assert entry and entry.select_one(f'a[href="history/{key}.html"]'), 'Preserved History bookmark must lead to its dedicated story'
    story_page = BeautifulSoup((ROOT / f'history/{key}.html').read_text(encoding='utf-8'), 'html.parser')
    section = story_page.select_one('main')
    scripture = story_page.select('#reflect a.fc-inline-scripture')
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
    assert not section.select_one('#official-film').select('[data-exclusive-artwork], [data-topic-art]'), 'Official film previews are not original artwork'
chapters = json.loads((ROOT / 'docs/temples/chapters.json').read_text(encoding='utf-8'))
temples = BeautifulSoup((ROOT / 'answers/why-latter-day-saints-build-temples.html').read_text(encoding='utf-8'), 'html.parser')
for chapter_id, story_id in [('kirtland-house','john-tanner'),('salt-lake-building','john-rowe-moyle')]:
    chapter = next(c for c in chapters if c['id'] == chapter_id)
    expected = '../church-history.html#' + story_id
    assert chapter['related_study']['url'] == expected
    assert temples.select_one(f'#temple-{chapter_id} a.fc-temple-history__related-link[href="{expected}"]')
assert {a['href'] for a in temples.select('a.fc-temple-history__related-link')} == {'../church-history.html#john-tanner', '../church-history.html#john-rowe-moyle', 'melchizedek-priesthood-restoration.html#priesthood-and-temple-blessings'}, 'Hitbox class is restricted to the three explicit contextual studies'
css = (ROOT / 'temples-history.css').read_text(encoding='utf-8')
hitbox_rule = '.fc-temple-history__chapter a.fc-temple-history__related-link { display: inline-block; max-width: 100%; vertical-align: top; overflow-wrap: anywhere; }'
assert hitbox_rule in css
assert hitbox_rule not in css.replace('display: inline-block;', 'display: inline;'), 'Inline mutation must lose the continuous-hitbox contract'
assert '1889' in (ROOT/'history/john-rowe-moyle.html').read_text(encoding='utf-8')
assert 'In Carter’s account' in (ROOT/'history/john-tanner.html').read_text(encoding='utf-8')
print('PASS: three compact History entrances, six verse destinations, three official films, two temple connections')
