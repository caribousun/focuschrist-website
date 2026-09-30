"""Integrate the researched temple chronology only after every artwork passes review.

Research lives in docs/temples/chapters.json; root reviewer supplies art-ready.json.
This script deliberately rejects missing/unreviewed assets instead of publishing placeholders.
"""
from pathlib import Path
import html
import hashlib
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'answers/why-latter-day-saints-build-temples.html'
BEGIN = '<!-- temple-history:start -->'
END = '<!-- temple-history:end -->'

def esc(value):
    return html.escape(str(value), quote=True)

def linked_prose(value):
    text = esc(value)
    for label, chapter in {'Moses 5': 'pgp/moses/5', 'Doctrine and Covenants 110': 'dc-testament/dc/110', 'Official Declaration 2': 'dc-testament/od/2'}.items():
        text = text.replace(label, '<a class="fc-inline-scripture" href="https://www.churchofjesuschrist.org/study/scriptures/' + chapter + '?lang=eng" target="_blank" rel="noopener noreferrer">' + label + '</a>')
    return text

def source_link(source):
    css = 'fc-inline-scripture' if '/study/scriptures/' in source['url'] else ''
    return f'<a class="{css}" href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(source["label"])}</a>'

def build():
    raw = json.loads((ROOT / 'docs/temples/chapters.json').read_text(encoding='utf-8-sig'))
    chapters = raw if isinstance(raw, list) else raw['chapters']
    ready = json.loads((ROOT / 'docs/temples/art-ready.json').read_text(encoding='utf-8-sig'))
    master_review = json.loads((ROOT / 'docs/art-study-image-review.json').read_text(encoding='utf-8'))
    registered = {r['asset']: r for r in master_review['pages'].get('answers/why-latter-day-saints-build-temples.html', []) if r.get('reviewed') is True}
    assert len(chapters) >= 15
    assert len({c['art_id'] for c in chapters}) == len(chapters)
    # Check the whole inventory before modifying the public page.
    pictures = [picture for chapter in chapters for picture in [chapter, *chapter.get('companions', [])]]
    for chapter in pictures:
        art = ready[chapter['art_id']]
        assert art.get('reviewed') is True, f'{chapter["art_id"]}: direct visual review required'
        assert art['full'] in registered, f'{chapter["art_id"]}: required master artwork review entry missing'
        assert hashlib.sha256((ROOT / art['full']).read_bytes()).hexdigest() == registered[art['full']]['sha256'], f'{chapter["art_id"]}: changed bytes require a new visual review'
        for key in ['full', 'thumbnail']:
            file = ROOT / art[key]
            assert file.is_file(), str(file)
        with Image.open(ROOT / art['full']) as image:
            assert image.size == (art['width'], art['height']), chapter['art_id']
        assert chapter['sources']
    assert all(len(chapter['paragraphs']) >= 2 for chapter in chapters)
    output = [BEGIN, '<section class="fc-deep-study fc-temple-history" id="temple-history" aria-labelledby="temple-history-title">',
      '<p class="fc-eyebrow">A journey through scripture and history</p>',
      '<h2 id="temple-history-title">The temple story: from the beginning to today</h2>',
      '<p>Follow the story of sacred places, covenant worship, and Jesus Christ across scripture and the history of the Church. The linked passages let you read each account in its own setting.</p>',
      '<nav class="fc-temple-history__directory" aria-label="Temple history eras">',
      '<p>Choose an era to explore its sections, or begin with the first story.</p>']
    eras = [('Scriptural beginnings', 0, 6), ('Jesus Christ and temple worship', 6, 13), ('Restoration and pioneer temples', 13, 18), ('Temples throughout the world', 18, 20)]
    for label, start, end in eras:
        output.append(f'<details class="fc-temple-history__era-menu"><summary><span>{esc(label)}</span><span class="fc-temple-history__range">Sections {start + 1}–{end}</span></summary><ol start="{start + 1}">')
        for chapter in chapters[start:end]:
            output.append(f'<li><a href="#temple-{esc(chapter["id"])}">{esc(chapter["title"])}</a></li>')
        output.append('</ol></details>')
    output.append('<div class="fc-actions"><a class="fc-button fc-button--primary" href="#temple-beginnings-eden">Begin temple story</a></div></nav>')
    for i, chapter in enumerate(chapters, 1):
        art = ready[chapter['art_id']]
        title = esc(chapter['title'])
        output.extend([
          f'<section class="fc-temple-history__chapter" id="temple-{esc(chapter["id"])}" aria-labelledby="temple-heading-{esc(chapter["id"])}">',
          f'<p class="fc-temple-history__era">{i:02d} · {esc(chapter["era"])}</p>',
          f'<h3 id="temple-heading-{esc(chapter["id"])}">{title}</h3>'])
        output.append(f'<p>{linked_prose(chapter["paragraphs"][0])}</p>')
        output.extend([
          f'<figure class="fc-study-visual" id="picture-{esc(chapter["art_id"])}" data-exclusive-artwork="{esc(chapter["art_id"])}" data-topic-art="{esc(chapter["art_id"])}">',
          f'<a href="../{esc(art["full"])}" aria-label="Explore artwork: {title}" aria-haspopup="dialog" data-full-image-alt="{esc(chapter["alt"])}">',
          f'<img src="../{esc(art["thumbnail"])}" srcset="../{esc(art["thumbnail"])} 960w, ../{esc(art["full"])} {art["width"]}w" sizes="(max-width: 700px) calc(100vw - 36px), 640px" width="{art["width"]}" height="{art["height"]}" loading="lazy" decoding="async" alt="{esc(chapter["alt"])}"></a>',
          f'<figcaption><p class="fc-study-visual-label">Explore and study</p><h3>{title}</h3><p>{linked_prose(chapter["caption"])}</p>',
          '<p class="fc-study-visual-sources">' + ' '.join(source_link(s) for s in chapter['sources'][:3]) + '</p></figcaption></figure>'])
        output.extend(f'<p>{linked_prose(paragraph)}</p>' for paragraph in chapter['paragraphs'][1:])
        for companion in chapter.get('companions', []):
            extra = ready[companion['art_id']]
            output.append(f'<figure class="fc-study-visual" id="picture-{esc(companion["art_id"])}" data-exclusive-artwork="{esc(companion["art_id"])}" data-topic-art="{esc(companion["art_id"])}" data-temple-companion="{esc(chapter["id"])}"><a href="../{esc(extra["full"])}" aria-label="Explore artwork: {esc(companion["title"])}" aria-haspopup="dialog" data-full-image-alt="{esc(companion["alt"])}"><img src="../{esc(extra["thumbnail"])}" srcset="../{esc(extra["thumbnail"])} 960w, ../{esc(extra["full"])} {extra["width"]}w" sizes="(max-width: 700px) calc(100vw - 36px), 640px" width="{extra["width"]}" height="{extra["height"]}" loading="lazy" decoding="async" alt="{esc(companion["alt"])}"></a><figcaption><p class="fc-study-visual-label">A companion view</p><h3>{esc(companion["title"])}</h3><p>{esc(companion["caption"])}</p><p class="fc-study-visual-sources">' + ' '.join(source_link(s) for s in companion['sources']) + '</p></figcaption></figure>')
        if len(chapter['sources']) > 3:
            output.append('<p class="fc-study-visual-sources">' + ' '.join(source_link(s) for s in chapter['sources'][3:]) + '</p>')
        if chapter.get('context_detail'):
            detail = chapter['context_detail']
            output.append('<details><summary>' + esc(detail['summary']) + '</summary><p>' + esc(detail['text']) + '</p>')
            if detail.get('sources'):
                output.append('<p class="fc-study-visual-sources">' + ' '.join(source_link(s) for s in detail['sources']) + '</p>')
            output.append('</details>')
        if chapter.get('reflection'):
            output.append('<details><summary>Pause and reflect</summary><p>' + esc(chapter['reflection']) + '</p></details>')
        if chapter.get('related_study'):
            related = chapter['related_study']
            output.append('<p>' + esc(related['introduction']) + ' <a class="fc-temple-history__related-link" href="' + esc(related['url']) + '">' + esc(related['label']) + '</a></p>')
        if i in (6, 13, 18, 20):
            output.append('<p><a class="fc-temple-history__era-return" href="#temple-history">Back to temple eras</a></p>')
        output.append('</section>')
    output.extend(['</section>', END])
    content = PAGE.read_text(encoding='utf-8')
    block = '\n'.join(output)
    if BEGIN in content:
        content = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda _: block, content, flags=re.S)
    else:
        anchor = '<section class="fc-deep-study" id="scripture-study"'
        assert anchor in content
        content = content.replace(anchor, block + '\n' + anchor, 1)
        content = content.replace('<a href="#watch-study">Watch and study</a>', '<a href="#temple-history">Temples through time</a><a href="#watch-study">Watch and study</a>', 1)
    style = '<link rel="stylesheet" href="../temples-history.css?v=20260929-related-hitbox-1">'
    if re.search(r'<link rel="stylesheet" href="\.\./temples-history\.css\?v=[^"]+">', content):
        content = re.sub(r'<link rel="stylesheet" href="\.\./temples-history\.css\?v=[^"]+">', style, content)
    elif style not in content:
        content = content.replace('</head>', style + '\n</head>', 1)
    content = re.sub(r'topic-artwork-details\.js\?v=[A-Za-z0-9-]+', 'topic-artwork-details.js?v=20260929-history-sources-2', content)
    PAGE.write_text(content, encoding='utf-8', newline='\n')
    print(f'Integrated {len(chapters)} reviewed original temple-history picture studies.')

if __name__ == '__main__':
    build()
