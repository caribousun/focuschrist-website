"""Bind four reviewed body-art additions without relaxing legacy viewer inventories."""
from pathlib import Path
import hashlib
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OWNERS = {
    'church-history.html': 'history-friendship',
    'pioneers.html': 'pioneers-traveler',
    'answers/why-latter-day-saints-build-temples.html': 'temple-tribute',
    'timelines/willie-and-martin-handcart-map.html': 'handcart-supplies',
}

def records():
    rows = json.loads((ROOT/'docs/visual-rhythm-artwork-inventory.json').read_text(encoding='utf-8'))['figures']
    assert len(rows) == 4 and {r['page']: r['key'] for r in rows} == OWNERS
    return {r['page']: r for r in rows}

def without_reviewed_figure(route, text, record):
    """Remove exactly the bound figure only; any changed/duplicate figure fails."""
    found = []
    for match in re.finditer(r'<figure\b[^>]*>[\s\S]*?</figure>', text):
        figure = BeautifulSoup(match[0], 'html.parser').find('figure')
        if figure.get('data-topic-art') == record['key']:
            found.append((match, figure))
    assert route == record['page'] and OWNERS.get(route) == record['key']
    assert len(found) == 1, route + ': missing or duplicate new artwork'
    match, figure = found[0]
    assert hashlib.sha256(str(figure).encode()).hexdigest() == record['figure_sha256'], route + ': new figure differs from exact reviewed inventory'
    return text[:match.start()] + text[match.end():]

def check_sources(sources, rows):
    for route, row in rows.items():
        assert route in sources
        without_reviewed_figure(route, sources[route], row)
        expected = {f'assets/page-art/visual-rhythm-journey/{row["key"]}-{suffix}' for suffix in ('original.png', 'full.webp', '960.webp')}
        assert len(row['assets']) == 3 and {a['path'] for a in row['assets']} == expected
        for asset in row['assets']:
            assert hashlib.sha256((ROOT/asset['path']).read_bytes()).hexdigest() == asset['sha256'], asset['path'] + ': changed bytes'
    for route, text in sources.items():
        soup = BeautifulSoup(text, 'html.parser')
        for key in OWNERS.values():
            if soup.select(f'figure[data-topic-art="{key}"]'):
                assert OWNERS.get(route) == key, route + ': new figure on unreviewed route'
        for match in re.finditer(r'assets/page-art/visual-rhythm-journey/([^\s"<>]+)', text):
            assert route in OWNERS and match[1] in {OWNERS[route] + '-960.webp', OWNERS[route] + '-full.webp'}, route + ': unexpected new artwork reference'

def check():
    rows = records()
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html') if not set(p.relative_to(ROOT).parts) & {'.git', '.qa-artifacts', 'tools', 'node_modules', 'work', 'outputs'}}
    check_sources(sources, rows)
    return rows

def self_test():
    rows = records()
    for route, row in rows.items():
        text = (ROOT/route).read_text(encoding='utf-8')
        clean = without_reviewed_figure(route, text, row)
        figure = next(m[0] for m in re.finditer(r'<figure\b[^>]*>[\s\S]*?</figure>', text) if f'data-topic-art="{row["key"]}"' in m[0])
        for changed in (clean, text + figure, text.replace(row['key']+'-full.webp', 'wrong-full.webp'), text.replace(row['key']+'-960.webp', 'wrong-960.webp'), text.replace('data-topic-art="'+row['key']+'"', 'data-topic-art="unknown"')):
            try:
                without_reviewed_figure(route, changed, row)
            except AssertionError:
                pass
            else:
                raise AssertionError('Artwork mutation escaped: ' + route)
    sources = {r:(ROOT/r).read_text(encoding='utf-8') for r in rows}
    try:
        check_sources(dict(sources, **{'unexpected.html': sources['church-history.html']}), rows)
    except AssertionError:
        pass
    else:
        raise AssertionError('Unreviewed artwork owner escaped')

if __name__ == '__main__':
    self_test()
    check()
    print('PASS: four exact visual-rhythm figures, twelve assets, owners and mutation fixtures')
