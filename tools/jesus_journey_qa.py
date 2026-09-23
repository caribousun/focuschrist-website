"""Release gate for the complete, reviewed and interconnected Jesus Christ journey."""
from collections import Counter
import hashlib,json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
from build_jesus_journey import ROOT,DATA,render,scripture,validate_artwork_review

def read(name):return json.loads((DATA/name).read_text(encoding='utf-8'))

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.hrefs=[];self.art=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if a.get('href'):self.hrefs.append(a['href'])
        if a.get('data-journey-art'):self.art.append(a['data-journey-art'])

def verify(pages,registry):
    errors=[];owners={};missing=[];hashes={}
    urls=[p['url'] for p in pages]
    if len(pages)!=76 or len(set(urls))!=76:errors.append('Expected exactly 76 distinct descendants: seven journeys, six collections, 63 individual studies')
    collection_urls={p['url'] for p in read('parable-collections-reviewed.json')}
    branch_urls={p['url'] for p in read('branch-content-reviewed.json')}
    if len(collection_urls)!=6 or len(branch_urls)!=7:errors.append('Changed major journey or collection inventory')
    all_pages=pages+[read('main-content.json')]
    cache={}
    for p in all_pages:
        path=ROOT/p['url'].lstrip('/')
        if not path.is_file():errors.append('Missing page '+p['url']);continue
        parsed=Page(path.read_text(encoding='utf-8'));cache[path.resolve()]=parsed
        if len(parsed.ids)!=len(set(parsed.ids)):errors.append('Duplicate section IDs '+p['url'])
        keys=[b['art'] for s in p['sections'] for b in s.get('blocks',[]) if isinstance(b,dict) and 'art' in b]
        if len(keys)!=len(set(keys)):errors.append('Repeated same-page original '+p['url'])
        if p['url'] in collection_urls|branch_urls and len(keys)<8:errors.append('Fewer than eight original scenes '+p['url'])
        for key in keys:
            if key in owners:errors.append('Multiple original owners '+key)
            owners[key]=p['url'].lstrip('/')
            a=registry.get(key,{})
            if a.get('owner')!=owners[key]:errors.append('Wrong original owner '+key)
            if not a.get('reviewed') or not all((ROOT/a.get(f,'__missing__')).is_file() for f in ('asset','thumbnail')):missing.append(key);continue
            try:validate_artwork_review(key,a)
            except ValueError as exc:errors.append(str(exc))
            old=hashes.setdefault(a.get('original_sha256'),key)
            if old!=key:errors.append('Duplicate original pixels '+old+' / '+key)
            if not a.get('alt') or not a.get('caption') or not a.get('refs'):errors.append('Incomplete study copy '+key)
            for ref in a.get('refs',[]):scripture(ref)
            for field in ('asset','thumbnail'):
                actual=hashlib.sha256((ROOT/a[field]).read_bytes()).hexdigest()
                if actual!=a.get(field+'_sha256'):errors.append('Changed artwork derivative '+key+' '+field)
        if Counter(parsed.art)!=Counter(keys):errors.append('Rendered scene inventory incomplete '+p['url'])
        if p['url'] in urls:
            try:
                if path.read_text(encoding='utf-8')!=render(p,registry,True):errors.append('Non-strict or stale output '+p['url'])
            except ValueError as exc:errors.append(str(exc))
    if set(owners)!=set(registry):errors.append('Orphaned or unplanned registry entries')
    if missing:errors.append(f'{len(missing)} planned originals are not ready: '+', '.join(missing[:12]))
    main=read('main-content.json')['url'].lstrip('/')
    main_art=[a for a in registry.values() if a['owner']==main]
    if sum(bool(a.get('depicts_christ')) for a in main_art)<9 or sum(not a.get('depicts_christ') for a in main_art)<6:errors.append('Parent requires nine new Christ stories plus six modern application scenes beside six preserved originals')
    for path,parsed in list(cache.items()):
        for href in parsed.hrefs:
            u=urlsplit(href)
            if u.scheme or u.netloc:continue
            target=(ROOT/u.path.lstrip('/') if u.path.startswith('/') else path.parent/u.path).resolve() if u.path else path
            if not target.is_file():errors.append('Broken local destination '+href+' from '+str(path.relative_to(ROOT)));continue
            if u.fragment and target.suffix=='.html':
                if target not in cache:cache[target]=Page(target.read_text(encoding='utf-8'))
                if unquote(u.fragment) not in cache[target].ids:errors.append('Broken fragment '+href)
    sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
    if any('https://focuschrist.com'+u not in sitemap for u in urls):errors.append('Descendant sitemap integration incomplete')
    if 'About this portrayal' in (ROOT/'answers/bible-and-book-of-mormon-together.html').read_text(encoding='utf-8'):errors.append('Removed portrayal pills returned')
    return errors

if __name__=='__main__':
    errors=verify(read('pages.json'),read('artworks.json'))
    if errors:raise SystemExit('\n'.join(errors))
    print('Jesus journey release gate passed: all planned scenes, reviewed derivatives, one owner per original, complete descendant navigation and sitemap.')
