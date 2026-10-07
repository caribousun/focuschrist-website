"""Destination-specific picture links must retain their reviewed scene and target."""
from pathlib import Path
from urllib.parse import urlsplit
import json, re, posixpath
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
VISIBLE_TOPIC_ROUTES = frozenset({
    'answers/abrahamic-covenant.html',
    'answers/what-is-eternal-marriage.html',
    'general-conference.html',
    'history/eleazer-miller.html',
    'history/john-rowe-moyle.html',
    'history/john-tanner.html',
})
def assert_controller_bindings(actual):
    expected = json.loads((ROOT/'docs/topic-artwork-controller-bindings.json').read_text(encoding='utf8'))
    assert len(expected) == 118
    assert all(len(refs) == 1 and refs[0].endswith('topic-artwork-details.js?v=20261007-scoped-root-1') for refs in expected.values())
    assert actual == expected, 'Exact118 topic controller owners/single references required'

def controller_binding_self_test():
    expected = json.loads((ROOT/'docs/topic-artwork-controller-bindings.json').read_text(encoding='utf8'))
    assert_controller_bindings(expected)
    owner = 'pioneers.html'; ref = expected[owner][0]
    mutations = [dict(expected, **{owner: []}), dict(expected, **{owner: [ref, ref]}),
                 dict(expected, **{owner: [ref, ref.replace('20261007-scoped-root-1','20260930-history-records-1')]}),
                 dict(expected, **{owner: [ref.replace('20261007-scoped-root-1','unknown')]}),
                 dict(expected, **{'unreviewed.html': [ref]})]
    missing = dict(expected); del missing[owner]; mutations.append(missing)
    for mutation in mutations:
        try: assert_controller_bindings(mutation)
        except AssertionError: pass
        else: raise AssertionError('Invalid controller binding escaped')

def check():
    records = json.loads((ROOT/'docs/illustrated-study-navigation-review-20260929.json').read_text(encoding='utf8'))['static_links']
    cache = {}
    def soup(page):
        if page not in cache: cache[page] = BeautifulSoup((ROOT/page).read_text(encoding='utf8'), 'html.parser')
        return cache[page]
    assert len(records) == 92
    for r in records:
        anchors = [a for a in soup(r['page']).select('a[href]') if a['href'] == r['href']]
        assert any(r['new_label'] in (a.get_text(' ', strip=True) + ' ' + a.get('aria-label', '')) for a in anchors), r
        u = urlsplit(r['href'])
        target = u.path.lstrip('/') if u.path.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(r['page']), u.path))
        dest = soup(target or r['page'])
        assert dest.h1 and dest.h1.get_text(' ',strip=True) == r['target_title'], r
        if u.fragment: assert dest.find(id=u.fragment), r
    generic = re.compile(r'(?:open|follow) (?:this|the) illustrated study', re.I)
    controller_version = '20261007-scoped-root-1'
    consumers = 0
    actual_bindings = {}
    for page in ROOT.rglob('*.html'):
        if set(page.relative_to(ROOT).parts) & {'work', '.git', 'node_modules'}: continue
        for script in soup(page.relative_to(ROOT).as_posix()).select('script[src]'):
            if 'topic-artwork-details.js' in script['src']:
                expected_version = controller_version
                assert script['src'].endswith('topic-artwork-details.js?v='+expected_version), ('Stale picture controller', page)
                consumers += 1
                actual_bindings.setdefault(page.relative_to(ROOT).as_posix(), []).append(script['src'])
        for a in soup(page.relative_to(ROOT).as_posix()).select('a'):
            assert not generic.search(a.get_text(' ',strip=True)+' '+a.get('aria-label','')), page
    assert_controller_bindings(actual_bindings)
    controller_binding_self_test()
    for name in ['build_jesus_journey.py', 'build_jesus_parent.py', 'build_temples_history.py']:
        assert 'topic-artwork-details.js?v='+controller_version in (ROOT/'tools'/name).read_text(encoding='utf8'), name
    print(f'PICTURE CACHE PASS: {consumers} consumers and three authoritative builders use {controller_version}.')
    print('ILLUSTRATED NAVIGATION PASS: 92 specific labels plus two explicitly retired Joseph references, exact destination titles/fragments, no generic CTA recurrence.')
if __name__ == '__main__': check()
