"""Guard the owner's Evidences scope. Pixel review remains a separate release gate."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'book-of-mormon-evidences.html'
TOPICS = {'reading-paths', 'translation', 'manuscripts', 'english-language', 'witnesses', 'literary-patterns', 'voices', 'ancient-context', 'open-questions', 'come-to-christ', 'study-method', 'source-library'}
IDENTITIES = {
    'assets/heroes/home-christ-signature-approved-20260907.png': '4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b',
    'assets/identities/joseph-smith-owner-approved-20260914.png': '518f1b28b894418b5ad876a3004cdc54f798ad33a6910afaaaa69a5d1785a827',
}


def check():
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(PAGE + ': ' + message)
    text = (ROOT / PAGE).read_text(encoding='utf-8')
    doc = Document(); doc.feed(text)
    nodes = list(doc.root.walk())
    main = next((n for n in nodes if n.tag == 'main'), None)
    if main is None:
        return [PAGE + ': missing main']
    content = list(main.walk())
    ids = [n.attrs['id'] for n in nodes if n.attrs.get('id')]
    require(len(ids) == len(set(ids)), 'duplicate IDs')
    require(len(main.text().split()) >= 6000, 'requires at least 6000 words of study')
    nav = next((n for n in content if n.has('bom-study-navigation')), None)
    links = [n.attrs.get('href', '') for n in nav.walk() if n.tag == 'a'] if nav else []
    require(len(links) == 12 and {x.removeprefix('#') for x in links} == TOPICS, 'requires all 12 topic navigation targets exactly once')
    require(TOPICS.issubset(ids), 'topic destination missing')
    require(any(n.tag == 'a' and 'ask.html?study=Book%20of%20Mormon%20Evidences' in n.attrs.get('href', '') for n in content), 'contextual Ask pathway missing')
    require(text.count('topic-artwork-details.js?v=20260914-historical-sources-1') == 1, 'native topic-panel controller missing or duplicated')
    require(text.count('topic-artwork-details.css?v=20260908-exclusive-final') == 1, 'approved native topic-panel styles missing or duplicated')
    figures = [n for n in content if n.tag == 'figure' and n.has('fc-study-visual')]
    require(len(figures) == 23, f'owner requires 23 supporting pictures, found {len(figures)}')
    assets = []
    for figure in figures:
        triggers = [n for n in figure.children if n.tag == 'a' and any(c.tag == 'img' for c in n.walk())]
        require(len(triggers) == 1, 'each supporting figure needs exactly one direct native-panel image trigger')
        if not triggers:
            continue
        trigger = triggers[0]; asset = urlsplit(trigger.attrs.get('href', '')).path
        assets.append(asset)
        require(not any(k in trigger.attrs for k in ('data-artwork-detail', 'data-hero-viewer')), asset + ': trigger would bypass topic-panel enrollment')
        require(trigger.attrs.get('aria-haspopup') == 'dialog', asset + ': dialog semantics missing')
        require('data-full-image-viewer' not in trigger.attrs, asset + ': supporting picture must enter the native study panel before full-size viewing')
        require(bool(trigger.attrs.get('data-topic-study')), asset + ': onward study action missing')
        caption = next((n for n in figure.children if n.tag == 'figcaption'), None)
        require(caption is not None and len(caption.text().split()) >= 35, asset + ': meaningful reflection missing')
        require(caption is not None and any(n.tag == 'a' and urlsplit(n.attrs.get('href', '')).hostname == 'www.churchofjesuschrist.org' for n in caption.walk()), asset + ': official source pill missing')
    heroes = [n for n in nodes if n.tag == 'a' and 'data-hero-viewer' in n.attrs]
    require(len(heroes) == 1, 'requires one hero in addition to 23 supporting pictures')
    if heroes:
        require(heroes[0].attrs.get('data-hero-record') == 'bom-evidences', 'dedicated native hero record missing')
        assets.append(urlsplit(heroes[0].attrs.get('href', '')).path)
    require(len(assets) == len(set(assets)), 'artwork assets repeated within the study')
    entries = json.loads((ROOT / 'docs/art-study-image-review.json').read_text(encoding='utf-8'))['pages'].get(PAGE, [])
    require(len(entries) == 24, f'review ledger requires 24 images including hero, found {len(entries)}')
    require({x.get('asset') for x in entries} == set(assets), 'page assets and reviewed ledger disagree')
    for entry in entries:
        asset = entry.get('asset', ''); path = (ROOT / asset).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'missing reviewed asset ' + asset)
        require(entry.get('reviewed') is True and bool(entry.get('tone')), 'unreviewed image or missing expression review: ' + asset)
        if path.is_file():
            require(hashlib.sha256(path.read_bytes()).hexdigest() == entry.get('sha256'), 'reviewed image bytes changed: ' + asset)
            with Image.open(path) as image:
                require(image.format == 'WEBP', 'full asset must be WebP: ' + asset)
                require(image.size == (entry.get('width'), entry.get('height')), 'reviewed full dimensions changed: ' + asset)
        if entry.get('slot') == 'hero':
            require(bool(entry.get('gaze_review')), 'hero requires explicit reviewed mutual-gaze record')
    for asset, expected in IDENTITIES.items():
        path = ROOT / asset
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'approved identity master changed: ' + asset)
    cards = [n for n in content if n.has('fc-resource-card')]
    coverage = json.loads((ROOT / 'docs/resource-page-coverage.json').read_text(encoding='utf-8')).get(PAGE, [])
    keys = [n.attrs.get('data-resource-key') for n in cards]
    require(len(cards) == 3 and len(set(keys)) == 3 and set(keys) == set(coverage), 'requires exactly three distinct inventoried video cards')
    require('IMAGE SLOT:' not in text, 'pending artwork slots remain')
    return errors


if __name__ == '__main__':
    failures = check()
    if failures:
        raise SystemExit('\n'.join(failures))
    print('Evidences QA PASS: 23 native supporting pictures plus hero, 12 topics, 3 videos, source reflections, reviewed bytes and protected identity masters')
