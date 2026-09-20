#!/usr/bin/env python3
"""Deterministic public-content search index. --check blocks stale releases."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, quote
from xml.etree import ElementTree as ET
sys.dont_write_bytecode = True
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'script', 'style', 'nav', 'footer', 'dialog', 'template', 'noscript', 'form', 'button'}

def hidden(n):
    return (n.tag in EXCLUDED or 'hidden' in n.attrs or n.attrs.get('aria-hidden') == 'true'
            or re.search(r'display\s*:\s*none', n.attrs.get('style', ''))
            or any(k in n.attrs for k in ('data-artwork-detail-content', 'data-missionary-detail-content')))

def visible(n):
    if hidden(n): return ''
    return ' '.join(c if isinstance(c, str) else visible(c) for c in n.content)

def clean(s): return re.sub(r'\s+', ' ', s).strip()

def category(path):
    if path.startswith('/answers/'): return 'Answer'
    if path.startswith('/art-study/') or path in {'/art.html', '/art-gallery.html'}: return 'Art'
    if path in {'/church-history.html', '/joseph-smith-likeness.html', '/pioneers.html'}: return 'History'
    if path == '/watch.html': return 'Watch'
    return 'Study'

def build():
    pages = sorted({('/index.html' if urlsplit(x.text).path in {'','/'} else urlsplit(x.text).path) for x in ET.parse(ROOT/'sitemap.xml').getroot().findall('{*}url/{*}loc')})
    pages = [p for p in pages if p != '/search.html']
    records = []
    for path in pages:
        doc = Document(); doc.feed((ROOT/path.lstrip('/')).read_text(encoding='utf-8'))
        nodes = list(doc.root.walk())
        h1 = next((n for n in nodes if n.tag == 'h1'), None)
        title_node = next((n for n in nodes if n.tag == 'title'), h1)
        title = clean(visible(title_node)).split('|')[0].strip() if title_node else path
        meta = next((n.attrs.get('content','') for n in nodes if n.tag == 'meta' and n.attrs.get('name') == 'description'), '')
        body = next((n for n in nodes if n.tag == 'body'), doc.root)
        main = next((n for n in nodes if n.tag == 'main'), body)
        search_keywords = next((n.attrs.get('content', '') for n in nodes if n.tag == 'meta' and n.attrs.get('name') == 'keywords'), '')
        base = {'url':path, 'title':title, 'pageTitle':title, 'category':category(path), 'keywords':clean(Path(path).stem.replace('-',' ') + ' ' + search_keywords)}
        records.append(dict(base, text=clean(visible(main)), excerpt=clean(meta)))
        used = set()
        for heading in nodes:
            if heading.tag not in {'h2','h3'}: continue
            lineage=[]; n=heading
            while n: lineage.append(n); n=n.parent
            if any(hidden(n) for n in lineage): continue
            # An explicit heading ID or the nearest named section is a durable destination.
            target = next((n for n in lineage if n.attrs.get('id') and (n is heading or n.tag in {'section','article'})), None)
            if not target or target.attrs['id'] in used: continue
            used.add(target.attrs['id'])
            # These retained bookmarks now forward to their own complete studies.
            if path == '/church-history.html' and target.attrs['id'] in {
                'aaronic-priesthood-restoration', 'melchizedek-priesthood-restoration'
            }: continue
            if target.tag in {'section','article'}:
                bodytext = clean(visible(target))
            else:
                # A heading directly in main must not borrow the whole page's text.
                following = heading.parent.children[heading.parent.children.index(heading)+1:]
                parts=[]
                for sibling in following:
                    if sibling.tag in {'h1','h2','h3'} and int(sibling.tag[1]) <= int(heading.tag[1]): break
                    parts.append(visible(sibling))
                bodytext=clean(' '.join(parts))
            headingtext = clean(visible(heading))
            if not bodytext or not headingtext: continue
            if bodytext.startswith(headingtext): bodytext=bodytext[len(headingtext):].strip()
            records.append(dict(base, url=path+'#'+quote(target.attrs['id']),title=headingtext,text=bodytext,excerpt='',keywords=target.attrs['id'].replace('-',' ')))
    # Artwork routes use the existing gallery's own stable picture IDs and detail panels.
    gallery=json.loads((ROOT/'art-gallery.json').read_text(encoding='utf-8'))
    for art in gallery['artworks']:
        records.append({'url':'/art-gallery.html?picture='+quote(art['id']), 'title':art['title'],
                        'pageTitle':'Art Gallery','category':'Art','text':art['alt'], 'excerpt':art['alt'],
                        'thumbnail':art['thumbnail']})
    if len({r['url'] for r in records}) != len(records): raise ValueError('Duplicate search destinations')
    return {'version':1, 'pages':pages, 'records':records}

if __name__ == '__main__':
    result=json.dumps(build(),ensure_ascii=False,separators=(',',':'))+'\n'
    target=ROOT/'site-search-index.json'
    if '--check' in sys.argv:
        if not target.exists() or target.read_text(encoding='utf-8') != result:
            raise SystemExit('Search index is stale. Run python tools/build_site_search.py and review the changes.')
        print('SEARCH INDEX PASS: public pages, sections and artwork are current')
    else:
        target.write_text(result,encoding='utf-8'); print('Built site-search-index.json')
