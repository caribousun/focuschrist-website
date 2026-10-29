"""Destination-specific picture links must retain their reviewed scene and target."""
from pathlib import Path
from urllib.parse import urlsplit
import json, re, posixpath, hashlib
from emma_story_consumers import EMMA_STORY_ROUTES, historical_consumers
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
CONTROLLER_REF = '../topic-artwork-details.js?v=20261021-continue-motion-1'
HISTORICAL_CONTROLLER_SHA256 = '9a683d6ce80dd982fb01418843f78f1df7462d636914804f5894fb4d055fff2a'


def controller_bindings_from_registry(registry, rows):
    historical = historical_consumers(registry, [CONTROLLER_REF])
    assert historical is not None, 'Exact five current Emma controller registry bindings required'
    assert len(historical) == 120
    assert hashlib.sha256(json.dumps(historical, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == HISTORICAL_CONTROLLER_SHA256, 'Historical120 registry bindings changed'
    assert all(len(refs)==1 and refs[0].endswith('topic-artwork-details.js?v=20261009-settled-continue-2') for refs in historical.values())
    assert set(historical)<=set(rows)
    expected = {route:[ref.replace('20261009-settled-continue-2','20261021-continue-motion-1') for ref in refs] for route,refs in historical.items()}
    return dict(expected, **{route: [CONTROLLER_REF] for route in EMMA_STORY_ROUTES})


def current_controller_bindings():
    from continue_motion_binding import mapping
    registry=json.loads((ROOT/'docs/topic-artwork-controller-bindings.json').read_text(encoding='utf8'))
    return controller_bindings_from_registry(registry, mapping()['files'])


def assert_controller_bindings(actual):
    # Preserve the old 125-owner registry and all 120 historical assertions,
    # then validate the exact retired compatibility source before removing its
    # one obsolete consumer from the ACTUAL current expected set.
    expected = current_controller_bindings()
    historical = historical_consumers(expected, [CONTROLLER_REF])
    assert historical is not None and len(historical) == 120
    assert len(expected) == 125
    assert all(len(refs) == 1 and refs[0].endswith('topic-artwork-details.js?v=20261021-continue-motion-1') for refs in expected.values())
    retired = 'history/emma-elect-lady.html'
    assert hashlib.sha256((ROOT/retired).read_bytes()).hexdigest() == '6de7bd0b21f0561913ba251163e552588a3fe065df83fd6cd1ccb9b6365ccbba', 'retired compatibility source drift'
    assert expected.pop(retired) == [CONTROLLER_REF]
    assert len(expected) == 124
    assert actual == expected, 'Exact120 historical plus four live Emma topic-controller owners required'

def controller_binding_self_test():
    expected = current_controller_bindings()
    del expected['history/emma-elect-lady.html']
    assert_controller_bindings(expected)
    owner = 'pioneers.html'; ref = expected[owner][0]
    mutations = [dict(expected, **{owner: []}), dict(expected, **{owner: [ref, ref]}),
                 dict(expected, **{owner: [ref, ref.replace('20261021-continue-motion-1','20260930-history-records-1')]}),
                 dict(expected, **{owner: [ref.replace('20261021-continue-motion-1','unknown')]}),
                 dict(expected, **{'unreviewed.html': [ref]})]
    missing = dict(expected); del missing[owner]; mutations.append(missing)
    mission_ref = expected['missionary.html'][0]
    mutations.extend([dict(expected, **{'missionary.html': []}),
                      dict(expected, **{'missionary.html': [mission_ref, mission_ref]}),
                      dict(expected, **{'missionary.html': ['/topic-artwork-details.js']}),
                      dict(expected, **{'missionary.html': [mission_ref.replace('20261021-continue-motion-1', 'unknown')]})])
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
    controller_version = '20261021-continue-motion-1'
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
        builder=(ROOT/'tools'/name).read_text(encoding='utf8')
        if name in {'build_jesus_journey.py','build_jesus_parent.py'}:
            assert 'topic-artwork-details.js?v=20261009-settled-continue-2' in builder and 'advance(' in builder, name
        else:
            assert 'topic-artwork-details.js?v='+controller_version in builder, name
    print(f'PICTURE CACHE PASS: {consumers} consumers and three authoritative builders use {controller_version}.')
    print('ILLUSTRATED NAVIGATION PASS: 92 specific labels plus two explicitly retired Joseph references, exact destination titles/fragments, no generic CTA recurrence.')
if __name__ == '__main__': check()
