"""Bind the covenant study to its reviewed sources, pictures and chapter contract.

Structural checks complement recorded human source and pixel review.
"""
import hashlib, json
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs
from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'answers/abrahamic-covenant.html'
CHAPTERS = ['a-promise-to-live-by', 'abraham-and-sarah', 'every-family', 'god-remembers',
            'jacob-at-bethel', 'jacob-becomes-israel', 'christ-at-the-heart', 'risen-lord', 'our-day', 'nearer-to-him']

def document(path):
    d=Document();d.feed(path.read_text(encoding='utf-8'));return list(d.root.walk())

def check():
    ns=document(ROOT/PAGE); ids={n.attrs['id']:n for n in ns if 'id' in n.attrs}
    manifest=json.loads((ROOT/'docs/abrahamic-covenant/art-review.json').read_text(encoding='utf-8'))
    arts=manifest['artworks']
    assert len(arts)==12 and sum(a['includes_christ'] for a in arts.values())==6
    figures=[n for n in ns if n.tag=='figure' and 'data-exclusive-artwork' in n.attrs]
    assert len(figures)==12 and {n.attrs['data-exclusive-artwork'] for n in figures}==set(arts)
    decoded=set()
    for f in figures:
        key=f.attrs['data-exclusive-artwork'];a=arts[key]
        assert a['owner']=='/'+PAGE and a['review_status']=='pass' and a['owner_approved'] is False
        assert a['independent_review']['review_status']=='pass'
        assert a['independent_review']['sha256']==a['original_sha256']
        link=next(n for n in f.children if n.tag=='a');img=next(n for n in link.walk() if n.tag=='img')
        assert urlsplit(link.attrs['href']).path=='/'+a['asset']
        assert urlsplit(img.attrs['src']).path=='/'+a['thumbnail']
        assert link.attrs.get('aria-haspopup')=='dialog'
        for field in ('asset','thumbnail'):
            p=ROOT/a[field];assert hashlib.sha256(p.read_bytes()).hexdigest()==a[field+'_sha256'],key
            with Image.open(p) as im:assert abs(im.width/im.height-1.5)<.001
        with Image.open(ROOT/a['asset']) as im:
            digest=hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
        assert digest not in decoded,'Duplicate original pixels';decoded.add(digest)
        cap=next(n for n in f.children if n.tag=='figcaption')
        assert any(n.tag=='a' and 'churchofjesuschrist.org' in n.attrs.get('href','') for n in cap.walk())
    nav=next(n for n in ns if n.has('jj-local-nav'))
    assert nav.has('fc-study-nav')
    assert [n.attrs['href'][1:] for n in nav.walk() if n.tag=='a']==CHAPTERS
    for chapter in CHAPTERS:
        section=ids[chapter];assert section.parent is nav.parent
        run=0;visuals=0
        for n in section.children:
            if n.has('jj-reading'):
                run+=1;assert run<=3,chapter+': too many paragraphs without a picture'
            if n.tag=='figure' or 'data-linked-picture-reference' in n.attrs:
                run=0;visuals+=1
        assert visuals>=1,chapter+': picture missing'
        assert any(n.tag=='details' for n in section.walk()),chapter+': reflection missing'
    refs=[n for n in ns if 'data-linked-picture-reference' in n.attrs]
    assert len(refs)==1 and refs[0].attrs['data-linked-picture-reference']=='life-after-death-nephi-bread'
    assert next(n for n in refs[0].walk() if n.tag=='a').attrs['href']=='/answers/what-happens-after-death.html#christ-in-third-nephi'
    canon=set()
    for n in ns:
        if n.tag!='a':continue
        u=urlsplit(n.attrs.get('href',''))
        if '/study/scriptures/' in u.path:
            assert u.hostname=='www.churchofjesuschrist.org' and parse_qs(u.query).get('id') and u.fragment.startswith('p')
            canon.add(u.path.split('/study/scriptures/')[1].split('/')[0])
    assert {'ot','nt','bofm','dc-testament','pgp'}<=canon
    assert 'continue-study' in ids
    ask=next(n for n in ids['continue-study'].walk() if n.tag=='a' and '/ask.html?' in n.attrs.get('href',''))
    query=parse_qs(urlsplit(ask.attrs['href']).query)
    assert query['study']==['Abrahamic Covenant'] and query['return']==['/'+PAGE+'#a-promise-to-live-by']
    directory=document(ROOT/'answers.html')
    grid=next(n for n in directory if n.has('fc-answers-jump-links'))
    routes=[n.attrs['href'] for n in grid.walk() if n.tag=='a']
    assert len(routes)==len(set(routes))==28 and PAGE in routes
    assert 'answers/jesus-christ-latter-day-saint-beliefs.html' not in routes
    pair=next(n for n in directory if n.has('fc-answers-featured-pair'))
    assert [n.attrs['href'] for n in pair.walk() if n.tag=='a']==['atonement.html','answers/jesus-christ-latter-day-saint-beliefs.html']
    print('COVENANT QA PASS: 12 reviewed originals, 6 Christ, 10 pictured chapters, 2–3 paragraph rhythm, five scripture divisions, exact Ask return and 28 topic slots.')

if __name__=='__main__':check()
