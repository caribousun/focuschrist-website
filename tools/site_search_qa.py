"""Search coverage, index safety and source visibility checks."""
import json
import sys
from urllib.parse import urlsplit, unquote, parse_qs
sys.dont_write_bytecode=True
from build_site_search import ROOT, build, visible
from answer_study_qa import Document

data=build()
actual=json.loads((ROOT/'site-search-index.json').read_text(encoding='utf-8'))
assert data==actual, 'Search index stale'
art_ids={x['id'] for x in json.loads((ROOT/'art-gallery.json').read_text(encoding='utf-8'))['artworks']}
cache={}
for record in data['records']:
    u=urlsplit(record['url']); assert not u.scheme and not u.netloc and u.path.startswith('/') and '..' not in u.path
    path=ROOT/u.path.lstrip('/'); assert path.is_file(),record['url']
    if u.path not in cache:
        d=Document();d.feed(path.read_text(encoding='utf-8'));cache[u.path]=d
    if u.fragment: assert unquote(u.fragment) in {n.attrs.get('id') for n in cache[u.path].root.walk()},record['url']
    if u.query: assert u.path=='/art-gallery.html' and parse_qs(u.query)['picture'][0] in art_ids
    if record.get('thumbnail'): assert (ROOT/record['thumbnail'].lstrip('/')).is_file()
for path in data['pages']+['/search.html','/404.html']:
    d=Document();d.feed((ROOT/path.lstrip('/')).read_text(encoding='utf-8'));nodes=list(d.root.walk())
    links=[n for n in nodes if 'data-site-search-trigger' in n.attrs]
    assert len(links)==1,path
    assert links[0].attrs.get('aria-label')=='Search focusChrist'
    assert any(n.tag=='script' and n.attrs.get('src','').endswith('site-search.js?v=20260919-focused-answers-1') for n in nodes),path
    assert any(n.tag=='link' and n.attrs.get('href','').endswith('site-search.css?v=20260924-narrow-reading-1') for n in nodes),path
assert '/search.html' not in data['pages']
fixture=Document();fixture.feed('<main><p>Visible teaching</p><nav>SECRET NAV</nav><dialog>SECRET DIALOG</dialog><div hidden>SECRET HIDDEN</div><script>SECRET SCRIPT</script><footer>SECRET FOOTER</footer><div aria-hidden="true">SECRET ARIA</div><div style="display:none">SECRET STYLE</div></main>')
assert 'SECRET' not in visible(fixture.root)
assert 'Visible teaching' in visible(fixture.root)
print(f'SEARCH QA PASS: {len(data["pages"])} public pages, {len(data["records"])} valid destinations; hidden/internal content excluded')
