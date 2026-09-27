"""Bind Holy Ghost study structure and reviewed art to exact source/asset contracts.

Technical coverage does not substitute for historical, pixel or owner review.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from PIL import Image
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
PAGE = 'answers/holy-ghost.html'
CHAPTERS = ['who-is-the-holy-ghost', 'old-testament', 'jesus-teaches', 'comforter',
            'hear-and-understand', 'book-of-mormon', 'mind-heart-covenant', 'holy-ghost-or-me']
SCENES = {'baptism':'nt/matt/3', 'nazareth':'nt/luke/4', 'sent-twelve':'nt/matt/10',
          'nicodemus':'nt/john/3', 'comforter':'nt/john/14', 'risen-commission':'nt/john/20',
          'nephite-prayer':'bofm/3-ne/19', 'nephite-disciples':'bofm/3-ne/18',
          'elijah':'ot/1-kgs/19', 'bezalel':'ot/ex/31', 'pentecost':'nt/acts/2',
          'philip':'nt/acts/8', 'nephi':'bofm/1-ne/2', 'mind-heart':'dc-testament/dc/8',
          'adam':'pgp/moses/6', 'confirmation':'dc-testament/dc/20'}
CHRIST = {'baptism','nazareth','sent-twelve','nicodemus','comforter','risen-commission','nephite-prayer','nephite-disciples'}

def nodes(path):
    d=Document(); d.feed(path.read_text(encoding='utf-8')); return list(d.root.walk())

def check_structure(ns):
    assert [n.attrs.get('id') for n in ns if n.tag=='section' and n.has('jj-chapter')]==CHAPTERS, 'Holy Ghost requires all eight ordered chapters'
    nav=next(n for n in ns if n.has('jj-local-nav'))
    assert nav.has('fc-study-nav') and [n.attrs.get('href') for n in nav.walk() if n.tag=='a']==['#'+c for c in CHAPTERS]
    assert len([n for n in ns if n.tag=='link' and 'jesus-journey.css?' in n.attrs.get('href','')])==1
    opening=next(n for n in ns if n.has('fc-topic-opening'))
    hero=[n for n in opening.walk() if n.has('fc-visual-hero')]
    assert len(hero)==1 and hero[0].attrs.get('data-hero-record')=='holy-ghost'
    assert 'data-hero-viewer' in hero[0].attrs and hero[0].attrs.get('aria-haspopup')=='dialog'
    assert urlsplit(hero[0].attrs['href']).path.endswith('/assets/heroes/holy-ghost-hero-full.webp')
    style=hero[0].attrs.get('style','')
    assert 'holy-ghost-hero-1600.webp' in style and 'holy-ghost-hero-mobile.webp' in style
    assert any(n.has('fc-page-intro') for n in opening.walk())
    assert any(n.has('fc-scroll-cue') and n.attrs.get('href')=='#main-content' for n in opening.walk())
    assert any(n.tag=='script' and n.attrs.get('src','').endswith('hero-details.js?v=20260927-human-media-voice-1') for n in ns)
    main=next(n for n in ns if n.tag=='main')
    figures=[n for n in main.walk() if n.tag=='figure']
    assert len(figures)==16 and all(n.has('jj-art') and n.has('fc-study-visual') for n in figures)
    assert {n.attrs.get('data-exclusive-artwork') for n in figures}=={'hg-'+s for s in SCENES}
    for f in figures:
        scene=f.attrs['data-exclusive-artwork'][3:]
        cap=next(n for n in f.children if n.tag=='figcaption')
        links=[n for n in cap.walk() if n.tag=='a']
        assert any(urlsplit(n.attrs['href']).netloc=='www.churchofjesuschrist.org' and urlsplit(n.attrs['href']).path=='/study/scriptures/'+SCENES[scene] for n in links), scene+': exact primary source missing'
        assert any(n.tag=='a' and 'data-full-image-viewer' in n.attrs for n in f.walk()), scene+': full image control missing'
    for chapter in [n for n in ns if n.tag=='section' and n.has('jj-chapter')]:
        assert len(chapter.text().split())>=40, chapter.attrs['id']+': substantive teaching missing'
    assert any(n.tag=='details' for n in ns), 'Optional reflection control missing'
    cards=[n for n in ns if n.has('fc-resource-card')]
    assert len(cards)==4 and len({n.attrs.get('data-resource-key') for n in cards})==4
    grid=cards[0].parent
    assert grid.has('fc-resource-grid') and all(card.parent is grid for card in cards), 'All four talks require one bounded resource grid'
    assert grid.parent.attrs.get('id')=='holy-ghost-or-me', 'Talk grid must remain in intended chapter'
    for card in cards:
        assert len([n for n in card.walk() if n.tag=='img' and n.attrs.get('alt')])==1, 'Talk requires a labeled thumbnail'
        review=json.loads((ROOT/'docs/holy-ghost/talk-thumbnail-review.json').read_text(encoding='utf-8'))
        expected=next(r for r in review['thumbnails'] if r['key']==card.attrs['data-resource-key'])
        image=next(n for n in card.walk() if n.tag=='img')
        assert image.attrs['src']==expected['after'], 'Talk thumbnail must preserve reviewed high-resolution source identity'
        assert [int(image.attrs['width']),int(image.attrs['height'])]==expected['decoded_after'], 'Talk thumbnail intrinsic dimensions must match decoded source'
        assert expected['decoded_after'][0]>=900, 'Talk thumbnail must not regress to low resolution'
    video=next(n for n in ns if n.attrs.get('id')=='holy-ghost-video')
    vn=list(video.walk())
    assert video.attrs.get('data-video-id')=='AGS45Fd9nmE', 'Exact featured Bednar video missing'
    assert not any(n.tag=='iframe' for n in vn), 'Video must load only on visitor request'
    preview=next(n for n in vn if 'data-video-preview' in n.attrs)
    assert preview.tag=='button' and preview.attrs.get('type')=='button' and preview.attrs.get('aria-label')
    assert any(n.tag=='img' and n.attrs.get('src')=='https://i.ytimg.com/vi/AGS45Fd9nmE/sddefault.jpg' and n.attrs.get('alt') for n in preview.walk())
    assert any('data-video-stage' in n.attrs and 'hidden' in n.attrs for n in vn)
    assert any(n.tag=='button' and 'data-video-close' in n.attrs and 'hidden' in n.attrs for n in vn)
    assert any('data-video-status' in n.attrs and n.attrs.get('role')=='status' and n.attrs.get('aria-live')=='polite' for n in vn)
    assert any(n.tag=='a' and n.attrs.get('href')=='https://www.youtube.com/watch?v=AGS45Fd9nmE' for n in vn), 'Permanent owner-channel fallback missing'
    assert any(n.tag=='script' and n.attrs.get('src')=='../holy-ghost-video.js?v=20260927-player-1' for n in ns)
    assert any(n.tag=='link' and n.attrs.get('href')=='../holy-ghost-video.css?v=20260927-thumbnail-2' for n in ns)
    onward=next(n for n in ns if n.attrs.get('id')=='continue-study')
    ask=next(n for n in onward.walk() if n.tag=='a' and urlsplit(n.attrs.get('href','')).path=='/ask.html')
    q=parse_qs(urlsplit(ask.attrs['href']).query)
    assert q.get('topic') and q.get('return')==['/'+PAGE+'#holy-ghost-or-me'], 'Exact editable Ask context/return missing'
    return figures

def check():
    ns=nodes(ROOT/PAGE); figures=check_structure(ns)
    manifest=json.loads((ROOT/'docs/holy-ghost/art-review.json').read_text(encoding='utf-8'))
    arts=manifest['artworks']
    assert set(arts)=={'hg-'+s for s in SCENES}, 'Reviewed body artwork inventory mismatch'
    decoded=set()
    for f in figures:
        key=f.attrs['data-exclusive-artwork']; a=arts[key]; scene=key[3:]
        assert a['owner']=='/'+PAGE and a['includes_christ']==(scene in CHRIST)
        assert a['review_status']=='pass' and a['independent_review']['review_status']=='pass'
        assert a['independent_review']['sha256']==a['original_sha256'], key+': review must bind original bytes'
        link=next(n for n in f.children if n.tag=='a'); im=next(n for n in link.walk() if n.tag=='img')
        assert urlsplit(link.attrs['href']).path=='/'+a['asset']
        assert urlsplit(im.attrs['src']).path=='/'+a['thumbnail']
        assert im.attrs.get('alt')==a['alt']
        for field in ('asset','thumbnail'):
            p=ROOT/a[field]; assert p.resolve().is_relative_to(ROOT)
            assert hashlib.sha256(p.read_bytes()).hexdigest()==a[field+'_sha256'], key+': asset changed since review'
        with Image.open(ROOT/a['asset']) as image:
            digest=hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
        assert digest not in decoded, 'Distinct originals required'; decoded.add(digest)
    print('HOLY GHOST QA PASS: 8 chapters, 16 distinct reviewed originals (8 Christ), 4 talk thumbnails, exact scripture and Ask return contracts')

if __name__=='__main__': check()
