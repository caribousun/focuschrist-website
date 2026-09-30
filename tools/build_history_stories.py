"""Build three dedicated History studies only from reviewed prose and artwork."""
from pathlib import Path
import hashlib
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/history-stories'
esc = lambda value: html.escape(str(value), quote=True)

def source_link(source):
    cls = 'fc-inline-scripture' if '/study/scriptures/' in source['url'] else ''
    return f'<a class="{cls}" href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(source["label"])}</a>'

def prose(text, sources):
    text = esc(text)
    for source in sources:
        if '/study/scriptures/' in source['url']:
            text = text.replace(esc(source['label']), source_link(source))
            if '/dc/109?' in source['url'] and source['label'] != 'Doctrine and Covenants 109':
                text = text.replace('Doctrine and Covenants 109', source_link(dict(source, label='Doctrine and Covenants 109')))
            if source['label'].startswith('1 Corinthians'):
                named = dict(source, label=source['label'].replace('1 Corinthians', 'First Corinthians'))
                text = text.replace(esc(named['label']), source_link(named))
    dc = {'label': 'Doctrine and Covenants 110', 'url': 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/110?lang=eng'}
    return text.replace(dc['label'], source_link(dc))

def figure(unit, art, hero=False):
    caption = f'<h3>{esc(unit["title"])}</h3><p>{esc(art["caption"])}</p><p class="fc-study-visual-sources">' + ' '.join(source_link(s) for s in unit['sources']) + '</p>'
    cls = 'fc-life-hero' if hero else 'fc-study-visual fc-life-picture'
    anchor_cls = 'fc-visual-hero' if hero else ''
    image = art['full'] if hero else art['thumbnail']
    loading = 'loading="eager" fetchpriority="high"' if hero else 'loading="lazy"'
    extra = ' data-picture-panel-copy hidden'
    img = f'<img src="../{esc(image)}" width="{art["width"]}" height="{art["height"]}" alt="{esc(art["alt"])}" {loading} decoding="async">'
    if hero:
        img = f'<picture class="fc-mobile-scene-picture"><source media="(min-width: 701px)" srcset="../{esc(art["desktop"])}">{img}</picture>'
    return f'<figure class="{cls}" id="picture-{esc(unit["id"])}" data-exclusive-artwork="{esc(unit["id"])}" data-topic-art="{esc(unit["id"])}"><a class="{anchor_cls}" href="../{esc(art["full"])}" aria-label="Explore artwork: {esc(unit["title"])}" aria-haspopup="dialog" data-full-image-alt="{esc(art["alt"])}">{img}</a><figcaption{extra}>{caption}</figcaption></figure>'

def render(story, ready):
    slug = story['id']
    base = (ROOT / 'church-history.html').read_text(encoding='utf-8')
    css = re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', base)
    css = [x for x in css if not x.startswith('church-history.css')]
    css.append('history-stories.css?v=20260930-history-opening-4')
    scripts = ['site-common.js?v=20260930-unified-opening-1', 'full-image-viewer.js?v=20260914-reopen-1', 'topic-artwork-details.js?v=20260930-history-records-1', 'site-search.js?v=20260919-focused-answers-1']
    out = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">', f'<title>{esc(story["name"])} | Church History | focusChrist</title>', f'<meta name="description" content="{esc(story["introduction"])}"><link rel="canonical" href="https://focuschrist.com/history/{slug}.html">']
    out += [f'<meta property="og:url" content="https://focuschrist.com/history/{slug}.html">', f'<meta property="og:title" content="{esc(story["name"])} | Church History | focusChrist">', f'<meta property="og:description" content="{esc(story["introduction"])}">', f'<meta property="og:image" content="https://focuschrist.com/{ready[story["units"][0]["id"]]["full"]}">', '<meta name="twitter:card" content="summary_large_image">']
    out += [f'<link rel="stylesheet" href="../{x}">' for x in css]
    out += [f'<script src="../{x}" defer></script>' for x in scripts]
    out += ['</head><body class="fc-site fc-life-story">', (DATA/'navigation.html.template').read_text(encoding='utf-8'), '<main>']
    for index, unit in enumerate(story['units']):
        out += [f'<section id="{unit["id"]}" aria-labelledby="heading-{unit["id"]}">']
        if index == 0:
            out += [figure(unit, ready[unit['id']], True), '<div class="fc-life-reading fc-life-opening">', '<p class="fc-eyebrow"><a href="../church-history.html#faithful-lives">Church History</a></p>', f'<h1>{esc(story["title"])}</h1>', f'<div class="fc-actions"><a class="fc-button fc-button--primary" href="#heading-{unit["id"]}">Begin the story</a></div>', '<details class="fc-life-directory"><summary>Explore this story</summary><ol>']
            out += [f'<li><a href="#{"heading-" if i == 0 else ""}{u["id"]}">{esc(u["title"])}</a></li>' for i, u in enumerate(story['units'])]
            out += ['<li><a href="#official-film">Watch the official film</a></li><li><a href="#reflect">Pause and reflect</a></li></ol></details></div><div class="fc-life-reading fc-life-body-start">', f'<h2 id="heading-{unit["id"]}">{esc(unit["title"])}</h2>']
        else:
            out += ['<div class="fc-life-reading">', figure(unit, ready[unit['id']]), f'<h2 id="heading-{unit["id"]}">{esc(unit["title"])}</h2>']
        out += [f'<p>{prose(p, unit["sources"])}</p>' for p in unit['paragraphs']]
        out += ['</div></section>']
    out += ['<section class="fc-life-reading" id="official-film" aria-labelledby="film-heading"><h2 id="film-heading">Watch the story</h2><div class="fc-resource-grid">', story['film_html'], '</div></section>', '<section class="fc-life-reading" id="reflect" aria-labelledby="reflect-heading"><h2 id="reflect-heading">Pause and reflect</h2><div class="fc-life-reflections">']
    out += [f'<div class="fc-life-reflection"><p>{esc(p)}</p></div>' for p in story['reflection_prompts']]
    out += ['</div><div class="fc-actions" aria-label="Connected scripture study">' + ' '.join(source_link(s) for s in story['scriptures']) + '</div><p><a href="../church-history.html#faithful-lives">Explore more lives in Church History</a></p></section></main>', (DATA/'footer.html.template').read_text(encoding='utf-8'), '</body></html>']
    return '\n'.join(out) + '\n'

def render_hub(stories):
    path = ROOT/'church-history.html'
    source = path.read_text(encoding='utf-8')
    descriptions = {
        'john-tanner': 'Follow John Tanner from his conversion in New York to Kirtland, Nauvoo, and the Salt Lake Valley, through journeys, generous gifts, and a remembered act of forgiveness.',
        'eleazer-miller': 'Meet the missionary whose simple witness reached Brigham Young, and follow his service from the small branches of New York to the journey west.',
        'john-rowe-moyle': 'Travel with the English handcart pioneer, see the work of a skilled stonecutter, and follow his return to the temple site with a handmade wooden leg.'
    }
    out = ['<!-- faithful-lives:start -->', '<section class="fc-section" id="faithful-lives" aria-labelledby="faithful-lives-title"><div class="fc-container--standard"><p class="fc-eyebrow">Lives of faith and service</p><h2 class="fc-section-heading" id="faithful-lives-title">Three lives, told through pictures and records</h2><p>Explore each life through illustrated scenes, the historical accounts, and an official Church film.</p><div class="fc-history-life-grid">']
    for story in stories:
        slug = story['id']
        scene = {'john-tanner': 'tanner-healing-witness', 'eleazer-miller': 'miller-simple-witness', 'john-rowe-moyle': 'moyle-wooden-leg'}[slug]
        ready = json.loads((DATA/'art-ready.json').read_text(encoding='utf-8'))
        art = ready[scene]
        destination = f'history/{slug}.html#picture-{scene}'
        out += [f'<section class="fc-history-life-card" id="{slug}" aria-labelledby="{slug}-entry-title" data-linked-picture-reference="{scene}"><a class="fc-history-life-preview" href="{destination}" aria-label="Explore {esc(story["name"])}’s illustrated story"><img src="{esc(art["thumbnail"])}" width="960" height="640" loading="lazy" decoding="async" alt="{esc(art["alt"])}"></a><div class="fc-history-life-body"><h3 id="{slug}-entry-title">{esc(story["name"])}</h3><p>{esc(descriptions[slug])}</p><a class="fc-button" href="history/{slug}.html">Read {esc(story["name"])}’s story</a></div></section>']
    out += ['</div></div></section>', '<!-- faithful-lives:end -->']
    assert source.count('<!-- faithful-lives:start -->') == source.count('<!-- faithful-lives:end -->') == 1
    return re.sub(r'<!-- faithful-lives:start -->.*?<!-- faithful-lives:end -->', '\n'.join(out), source, flags=re.S)

def build():
    stories = json.loads((DATA/'stories.json').read_text(encoding='utf-8'))['stories']
    ready = json.loads((DATA/'art-ready.json').read_text(encoding='utf-8'))
    ids = [u['id'] for s in stories for u in s['units']]
    assert len(ids) == len(set(ids)) == 24
    preview_only = '--story' in sys.argv
    if preview_only:
        slug = sys.argv[sys.argv.index('--story') + 1]
        stories = [s for s in stories if s['id'] == slug]
        assert len(stories) == 1, 'Unknown story preview'
    for story in stories:
        assert len(story['units']) == {'john-tanner': 7, 'eleazer-miller': 9, 'john-rowe-moyle': 8}[story['id']] and story['hero_unit_id'] == story['units'][0]['id']
        assert [u['id'] for u in story['units']] == story['reviewed_scene_ids']
        for unit in story['units']:
            assert 1 <= len(unit['paragraphs']) <= 2
            art = ready[unit['id']]
            assert art['reviewed'] and art['alt'] and art['caption']
            for key in ['full', 'thumbnail']:
                path = ROOT/art[key]
                assert path.is_file(), path
            assert hashlib.sha256((ROOT/art['full']).read_bytes()).hexdigest() == art['sha256'], unit['id']
            if unit['id'] == story['hero_unit_id']:
                assert art['desktop_reviewed']
                assert hashlib.sha256((ROOT/art['desktop']).read_bytes()).hexdigest() == art['desktop_sha256'], unit['id'] + ' desktop'
    rendered = {ROOT/f'history/{s["id"]}.html': render(s, ready) for s in stories}
    if not preview_only:
        rendered[ROOT/'church-history.html'] = render_hub(stories)
    for path, content in rendered.items():
        if '--check' in sys.argv:
            assert path.read_text(encoding='utf-8') == content, f'Stale story: {path}'
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(content, encoding='utf-8', newline='\n')
    print(f'PASS: {len(stories)} stories, {sum(len(s['units']) for s in stories)} reviewed distinct scene records' + ('; unlinked local preview only' if preview_only else ''))

if __name__ == '__main__':
    build()
