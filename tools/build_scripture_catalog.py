"""Compile the complete, source-hashed library index; never silently omit a chapter."""
import hashlib, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]

def build():
    inventory = json.loads((ROOT/'docs/scripture-canon.json').read_text())
    ledger = json.loads((ROOT/'docs/scripture-source-ledger.json').read_text())
    entries = {v['chapter']: v for v in ledger['chapters']}
    books, chapters = [], {}
    extras = {'dc-testament/dc':['D&C','Doctrine & Covenants','DC'], 'pgp/js-m':['JS-M','Joseph Smith-Matthew','Joseph Smith Matthew'], 'pgp/js-h':['JS-H','Joseph Smith-History','Joseph Smith History'], 'pgp/a-of-f':['A of F'], 'ot/ps':['Psalm'], 'ot/song':['Song of Solomon','Song of Songs']}
    for book in inventory['books']:
        key = book['key']
        first = json.loads((ROOT/'scripture-data'/f'{key}/1.json').read_text(encoding='utf-8'))
        name = re.sub(r'\s+1$', '', first['title']).strip()
        if key == 'dc-testament/dc': name = 'Doctrine and Covenants'
        aliases = [key.split('/')[-1].replace('-', ' ')] + extras.get(key, [])
        books.append(dict(book, name=name, aliases=aliases))
        for n in range(1,book['chapters']+1):
            chapter = f'{key}/{n}'; entry = entries[chapter]
            raw = (ROOT/'scripture-data'/f'{chapter}.json').read_bytes()
            data = json.loads(raw)
            assert entry['status'] == 'verified'
            assert hashlib.sha256(raw).hexdigest() == entry['data_sha256']
            assert [v['number'] for v in data['verses']] == list(range(1,entry['verse_count']+1))
            chapters[chapter] = {'verse_count':entry['verse_count'], 'sha256':entry['data_sha256']}
    books.append({'key':'dc-testament/od','chapters':2,'name':'Official Declaration','aliases':['Official Declarations','OD']})
    for n in (1,2):
        key = f'dc-testament/od/{n}'
        raw = (ROOT/'scripture-data'/f'{key}.json').read_bytes(); entry = entries[key]
        assert entry['status'] == 'verified' and hashlib.sha256(raw).hexdigest() == entry['data_sha256']
        chapters[key] = {'verse_count':0,'kind':'document','paragraph_ids':[p['id'] for p in json.loads(raw)['paragraphs']],'sha256':entry['data_sha256']}
    payload = {'schema':1,'edition':inventory['edition'],'books':books,'chapters':chapters}
    payload['version'] = hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:20]
    return json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n'

if __name__ == '__main__':
    import sys
    target = ROOT/'scripture-data/catalog.json'
    result = build()
    if '--check' in sys.argv: assert target.read_text(encoding='utf-8') == result, 'Stale scripture catalog'
    else: target.write_text(result,encoding='utf-8')
    print('Complete scripture catalog verified')
