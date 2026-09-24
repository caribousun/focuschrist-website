#!/usr/bin/env python3
"""Gate dedicated topic destinations, complete openings, study content and migration."""
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote, parse_qs
from answer_study_qa import Document
from focused_answers_qa import opening as validated_opening
from abrahamic_covenant_qa import check as check_covenant, CHAPTERS as COVENANT_CHAPTERS
ROOT=Path(__file__).resolve().parents[1]
COVENANT='answers/abrahamic-covenant.html'
FEATURED_JESUS='answers/jesus-christ-latter-day-saint-beliefs.html'
def read(p):
 d=Document();d.feed(p.read_text(encoding="utf-8"));return list(d.root.walk())
errors=[]
nodes=read(ROOT/'answers.html')
pills=next(n for n in nodes if n.has('fc-answers-jump-links'))
links=[n for n in pills.walk() if n.tag=='a']
foundational={
 'answers/god-our-heavenly-father.html',
 'answers/restored-church-of-jesus-christ.html',
}
answer_paths=sorted((ROOT/'answers').glob('*.html'))
for answer_path in answer_paths:
 answer_nodes=read(answer_path)
 body_class='fc-jesus-journey' if answer_path.relative_to(ROOT).as_posix()==COVENANT else 'fc-topic-page'
 assert any(n.tag=='body' and n.has(body_class) for n in answer_nodes),answer_path.name+': shared responsive topic-page contract'
study_destinations={
 'birth-of-christ.html',
 'general-conference.html', 'book-of-mormon-evidences.html',
 'joseph-smith-likeness.html', 'church-history.html', 'pioneers.html',
 'come-follow-me.html',
}
expected=({p.relative_to(ROOT).as_posix() for p in answer_paths}-{FEATURED_JESUS})|study_destinations
assert len(links)==28, 'Keep the owner-requested seven by four topic grid'
featured=[n for n in nodes if n.has('fc-settle-featured')]
assert [(n.attrs.get('href'),n.text().strip()) for n in featured]==[('atonement.html','The Atonement of Jesus Christ'),(FEATURED_JESUS,'Jesus Christ')], 'Exact Atonement and Jesus featured destinations required'
assert featured[0].parent is featured[1].parent and featured[0].parent.has('fc-answers-featured-pair'), 'Featured destinations must remain paired'
assert len(links)==len(expected), 'topic directory must not duplicate destinations'
assert {n.attrs['href'] for n in links}==expected, 'topic grid must cover every Answer and enriched study destination'
for link in links:
 href=link.attrs['href'];u=urlsplit(href)
 assert not u.scheme and not u.netloc, 'Every topic opens an existing local study'
 p=ROOT/u.path;ns=read(p)
 headings=[n for n in ns if n.tag=='h1']
 assert len(headings)==1, href+': one page heading'
 if u.fragment:
  target=next((n for n in ns if n.attrs.get('id')==unquote(u.fragment)),None)
  assert target is not None and any(n.tag in ('h2','h3') for n in target.walk()),href+': named study section exists'
 if p.parent!=ROOT/'answers':continue
 heading_label={'answers/god-our-heavenly-father.html':'God',
                COVENANT:'The Abrahamic Covenant',
                'answers/restored-church-of-jesus-christ.html':'The restored Church',
                'answers/settle-this-in-your-hearts.html':'Settle This in Your Hearts'}.get(href,link.text().strip())
 assert headings[0].text().strip()==heading_label,href+': heading matches topic destination'
 if href==COVENANT:
  opening_nodes=[n for n in ns if n.has('jj-opening')]
  assert len(opening_nodes)==1 and headings[0] in list(opening_nodes[0].walk()), 'Covenant requires its single journey title opening'
  assert [n.attrs.get('id') for n in ns if n.has('jj-chapter')]==COVENANT_CHAPTERS, 'Covenant requires its exact ten reading chapters'
  validated_opening(p,ns)
  check_covenant()  # Exact twelve reviewed originals, hashes, owners, sources and study paths.
  continue
 opening=next(n for n in ns if n.has('fc-topic-opening'))
 assert any(n.has('fc-visual-hero') for n in opening.walk()),href+': image in first screen'
 assert any(n.has('fc-page-intro') for n in opening.walk()),href+': title in first screen'
 assert any(n.has('fc-scroll-cue') and n.attrs.get('href')=='#main-content' for n in opening.walk()),href+': continue action'
 assert sum('topic-study-pages.css?' in n.attrs.get('href','') for n in ns)==1
 main=next(n for n in ns if n.tag=='main')
 assert main.order>opening.order and len(main.text().split())>200,href+': substantive study after opening'
 hero=next(n for n in ns if 'data-hero-viewer' in n.attrs)
 return_path=parse_qs(urlsplit(hero.attrs['data-hero-ask']).query)['return'][0]
 assert urlsplit(return_path).path=='/'+href,href+': art study returns to same page'
stand=read(ROOT/'answers/stand-forever.html');look=read(ROOT/'answers/look-unto-me-doctrine-and-covenants-6-36.html')
# Each primary question has an image-first detail link plus an explicit study link.
foundation=next(n for n in stand if n.has('fc-primary-grid') and n.has('fc-foundation-grid'))
cards=[n for n in foundation.children if n.tag=='article']
assert len(cards)==4
routes=[]
for card in cards:
 anchors=[n for n in card.walk() if n.tag=='a']
 assert len(anchors)==2, 'foundation card has a detail-first image link and one direct study link'
 image_link=next(n for n in anchors if 'data-full-image-viewer' in n.attrs)
 study_link=next(n for n in anchors if n.has('fc-foundation-card-action'))
 assert any(n.tag=='img' for n in image_link.walk())
 href=study_link.attrs['href'];routes.append(href)
 assert image_link.attrs.get('data-topic-study')==href, 'image panel and direct action lead to the same study'
 assert image_link.attrs.get('aria-haspopup')=='dialog'
 assert study_link.attrs.get('aria-label','').startswith('Study ')
 assert any(n.tag=='h4' for n in card.walk())
 target=ROOT/'answers'/href;ns=read(target)
 assert sum(n.tag=='h1' for n in ns)==1
 assert len(next(n for n in ns if n.tag=='main').text().split())>800
 assert any(urlsplit(n.attrs.get('href','')).path=='stand-forever.html' for n in ns)
 assert any('data-full-image-viewer' in n.attrs for n in ns) or href=='restored-church-of-jesus-christ.html'
assert set(routes)=={'god-our-heavenly-father.html','jesus-christ-latter-day-saint-beliefs.html','who-was-joseph-smith.html','restored-church-of-jesus-christ.html'}
for file in ['god-our-heavenly-father.html','restored-church-of-jesus-christ.html']:
 ns=read(ROOT/'answers'/file);hero=next(n for n in ns if 'data-hero-viewer' in n.attrs)
 assert urlsplit(parse_qs(urlsplit(hero.attrs['data-hero-ask']).query)['return'][0]).path=='/answers/'+file
 assert any(n.has('fc-topic-opening') for n in ns)
 assert any(n.attrs.get('href')=='#main-content' and n.has('fc-scroll-cue') for n in ns)
keys={'stand-lord-i-believe','stand-faith-choice','stand-spiritual-momentum'}
assert keys <= {n.attrs.get('data-resource-key') for n in stand}
assert not keys & {n.attrs.get('data-resource-key') for n in look},'Stand Forever videos moved, not duplicated'
assert any(n.attrs.get('href')=='stand-forever.html' for n in look),'original page preserves a study pathway'
series=next(n for n in stand if n.attrs.get('id')=='video-series')
series_nodes=list(series.walk())
series_review=next(r for r in __import__('json').loads((ROOT/'docs/topic-study-source-review.json').read_text(encoding='utf-8'))['pages'] if r['path']=='answers/stand-forever.html')['series']
playlist=series_review['playlist_id']
series_links=[n.attrs['href'] for n in series_nodes if n.tag=='a']
assert series_review['playlist_url'] in series_links, 'publisher playlist must remain directly accessible'
for vid in [series_review['trailer_video_id'],series_review['episode_one_video_id']]:
 assert any(parse_qs(urlsplit(href).query).get('v')==[vid] and parse_qs(urlsplit(href).query).get('list')==[playlist] for href in series_links), 'series videos preserve publisher playlist context'
preview=next(n for n in series_nodes if n.tag=='img')
assert preview.attrs['src']==series_review['remote_thumbnail']
assert '/'+series_review['trailer_video_id']+'/' in preview.attrs['src'], 'native preview must match trailer'
assert preview.attrs.get('loading')=='lazy' and preview.attrs.get('alt')
assert all(preview.attrs.get(k)==str(series_review[k]) for k in ['width','height'])
assert series.order<next(n.order for n in stand if n.attrs.get('id')=='stand-forever'), 'series is discoverable before original devotional study'
assert any(n.attrs.get('href')=='#video-series' for n in stand), 'study navigation reaches video series'
assert not any(n.tag=='iframe' for n in series_nodes), 'direct publisher links work without an embedded player'

grief=read(ROOT/'answers/grief-and-faith.html')
for slug in ['nt/john/11','bofm/alma/7','bofm/mosiah/18']:
 assert any('churchofjesuschrist.org/study/scriptures/'+slug in n.attrs.get('href','') for n in grief)
assert any('data-full-image-viewer' in n.attrs for n in grief),'approved grief artwork remains viewable'
assert not any('/media/video/' in n.attrs.get('href','') for n in grief),'reading-only grief study has no duplicate video'
# Explicit references in enriched study prose and headings open the scripture reader.
reference=re.compile(r'\b(?:Doctrine and Covenants|D&C|3 Nephi|John|Luke|Matthew|Acts|Moses|Alma|Ephesians|Mosiah)\s+\d+(?::\d+(?:[–-]\d+)?)?')
for file in ['stand-forever','god-our-heavenly-father','jesus-christ-latter-day-saint-beliefs','who-was-joseph-smith','restored-church-of-jesus-christ']:
 ns=read(ROOT/'answers'/(file+'.html'));main=next(n for n in ns if n.tag=='main')
 for n in main.walk():
  ancestor=n;inside_link=False
  while ancestor:
   inside_link=inside_link or ancestor.tag=='a';ancestor=ancestor.parent
  if not inside_link:assert not reference.search(' '.join(n.words)),file+': unlinked explicit scripture reference'
  if n.tag=='a':assert not any(child.tag=='a' for child in n.walk() if child is not n),'nested anchor'
  if n.has('fc-inline-scripture'):
   assert n.attrs['href'].startswith('https://www.churchofjesuschrist.org/study/scriptures/')
   assert n.attrs.get('target')=='_blank' and 'noopener' in n.attrs.get('rel','')
print(f'TOPIC STUDY PAGES QA PASS: {len(links)} distinct pill destinations; complete openings, same-page hero return, and source-preserving migrations')
