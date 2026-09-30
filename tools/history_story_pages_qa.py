"""The owner-requested illustrated lives belong to History, with exact reviewed scene sets."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'docs/history-stories'
stories = json.loads((DATA/'stories.json').read_text(encoding='utf-8'))['stories']
ready = json.loads((DATA/'art-ready.json').read_text(encoding='utf-8'))
reviews = json.loads((ROOT/'docs/history-story-art-fermi-review-20260929.json').read_text(encoding='utf-8'))['images']
accepted = {(entry['source_original'], entry['sha256']) for entry in reviews if entry['result'] == 'pass'}
rejected = {entry['source_original'] for entry in reviews if entry['result'] == 'rejected'}
expression_edits = json.loads((DATA/'miller-expression-edits-20260929.json').read_text(encoding='utf-8'))['edits']
for edit in expression_edits:
    art = ready[edit['id']]
    assert edit['independent_review']['result'] == 'pass'
    assert art['source_sha256'] == edit['editedPath_sha256'], 'Do not reintroduce superseded Miller expressions'
    assert art['sha256'] != edit['superseded_export']['sha256']
all_hashes = []
hub = BeautifulSoup((ROOT/'church-history.html').read_text(encoding='utf-8'), 'html.parser')
for story in stories:
    slug = story['id']
    page = ROOT/f'history/{slug}.html'
    soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    assert soup.select_one(f'link[rel="canonical"][href="https://focuschrist.com/history/{slug}.html"]')
    ids = [node['id'] for node in soup.select('[id]')]
    assert len(ids) == len(set(ids)), 'Duplicate IDs'
    expected_count = {'john-tanner': 7, 'eleazer-miller': 9, 'john-rowe-moyle': 7}[slug]
    assert len(soup.select('main figure')) == expected_count, 'Exact accepted original count; no repeated hero'
    assert len(soup.select('main .fc-visual-hero')) == 1
    assert len(story['units']) == expected_count
    assert [u['id'] for u in story['units']] == story['reviewed_scene_ids']
    assert not (ROOT/f'answers/{slug}.html').exists(), 'These are History stories, not Answers topics'
    first = soup.select_one(f'#{story["hero_unit_id"]}')
    assert first.select_one('figure > a.fc-visual-hero')
    stops = [a['href'] for a in soup.select('.fc-life-directory ol a')]
    assert stops[:expected_count] == ['#heading-'+story['units'][0]['id']] + ['#'+u['id'] for u in story['units'][1:]], 'Directory must land before each body picture, not skip it'
    for unit in story['units']:
        section = soup.select_one('#'+unit['id'])
        art = ready[unit['id']]
        figure = section.select_one('figure')
        assert figure['data-exclusive-artwork'] == unit['id']
        assert figure.select_one('a')['href'] == '../'+art['full']
        assert figure.select_one('img')['alt'] == art['alt']
        assert figure.select_one('figcaption h3').get_text() == unit['title']
        assert figure.select_one('figcaption .fc-study-visual-sources a')
        assert figure.select_one('figcaption[data-picture-panel-copy][hidden]'), 'Picture metadata belongs inside the study panel, not duplicated in the reading flow'
        paragraphs = section.select(':scope > .fc-life-reading > p:not(.fc-eyebrow)')
        assert 1 <= len(paragraphs) <= 2
        assert [p.get_text() for p in paragraphs] == unit['paragraphs']
        digest = hashlib.sha256((ROOT/art['full']).read_bytes()).hexdigest()
        assert digest == art['sha256'] and art['reviewed']
        assert (art['source_original'], art['source_sha256']) in accepted
        assert art['source_original'] not in rejected, 'Rejected role/architecture variant cannot re-enter under a new asset name'
        all_hashes.append(digest)
    assert len(soup.select('#reflect .fc-life-reflection')) == 3
    assert len(soup.select('#official-film .fc-resource-card')) == 1
    for anchor in soup.select('a[href^="#"]'):
        assert soup.select_one(anchor['href']), 'Missing local story stop'
    entry = hub.select_one('#'+slug)
    assert entry and entry.select_one(f'a[href="history/{slug}.html"]')
    scene = {'john-tanner': 'tanner-healing-witness', 'eleazer-miller': 'miller-simple-witness', 'john-rowe-moyle': 'moyle-wooden-leg'}[slug]
    assert entry.get('data-linked-picture-reference') == scene
    assert len(entry.select('img')) == 1
    preview = entry.select_one('a.fc-history-life-preview')
    assert preview['href'] == f'history/{slug}.html#picture-{scene}'
    assert preview.img['src'] == ready[scene]['thumbnail'] and preview.img['alt'] == ready[scene]['alt']
    assert not entry.select('[data-topic-art], [data-exclusive-artwork], [data-hero-viewer]'), 'Hub previews link to their owner; no duplicate study controller or art ownership'
    assert len(entry.get_text(' ', strip=True).split()) < 100, 'History hub remains a compact entrance'
assert len(set(all_hashes)) == 23, 'Twenty-three distinct originals, not renamed copies'
moyle = next(s for s in stories if s['id'] == 'john-rowe-moyle')
assert any('wooden' in p.lower() for u in moyle['units'] for p in u['paragraphs'])
assert 'wooden' in ready['moyle-wooden-leg']['alt'].lower(), 'Required wooden-leg scene must be visibly described'
css = (ROOT/'history-stories.css').read_text(encoding='utf-8')
assert all(token in css for token in ('var(--fc-panel-fill)', 'var(--fc-panel-border)', 'var(--fc-panel-shadow)'))
assert not re.search(r'(?:^|[;{])\s*(?:height|min-height|max-height|object-fit)\s*:', css), 'Shared standard hero geometry must remain authoritative'
shared_css = (ROOT/'site-system.css').read_text(encoding='utf-8')
assert 'aspect-ratio: 2048 / 684;' in shared_css and '--fc-mobile-hero-height: clamp(320px, 115vw, 800px)' in shared_css
frame = json.loads((DATA/'frame-review-20260929.json').read_text(encoding='utf-8'))
assert abs(frame['desktop']['width']/frame['desktop']['height']-2048/684) < .001
subprocess.run([sys.executable, str(ROOT/'tools/build_history_stories.py'), '--check'], check=True)
print('PASS: three dedicated History pages, twenty-three original scene studies, narrative rhythm, source attribution and preserved hub bookmarks')

hub_css = (ROOT/'church-history.css').read_text(encoding='utf-8')
assert '.fc-history-life-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; }' in hub_css
assert '.fc-history-life-body p { margin: 0 0 24px; }' in hub_css
assert '.fc-history-life-preview img { display: block; width: 100%; height: auto; }' in hub_css
assert '@media (max-width: 959px) { .fc-history-life-grid { grid-template-columns: 1fr; } }' in hub_css
assert hub.select_one('link[href="church-history.css?v=20260929-pictured-entries-1"]')

assert '.fc-life-story main figure[id^="picture-"] { scroll-margin-top: calc(max(52px, 3.25rem) + 24px); }' in css

tanner_units = {u['id']: u for story in stories if story['id'] == 'john-tanner' for u in story['units']}
arrington_units = ['tanner-journey-kirtland', 'tanner-temple-support', 'tanner-debt-forgiven']
arrington_words = sum(len(text.split()) for key in arrington_units for text in ((tanner_units[key]['paragraphs'][:1] if key == 'tanner-temple-support' else tanner_units[key]['paragraphs']) + [ready[key]['caption']]))
assert arrington_words <= 200, 'Aggregate source budget includes complete narrative allocations and all related picture captions'
assert any('Doctrine and Covenants 109' in p for p in tanner_units['tanner-temple-support']['paragraphs'][1:]), 'Preserve independently sourced temple prayer context'
assert next(u for u in moyle['units'] if u['id'] == 'moyle-wooden-leg')['paragraphs'][1].startswith('The Ensign Peak Foundation’s site history reports'), 'Attribute museum display claim without implying independent artifact authentication'
