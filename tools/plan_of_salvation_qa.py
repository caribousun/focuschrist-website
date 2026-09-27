"""Bind the Plan study to reviewed curriculum, sources, navigation and original art."""
import copy, hashlib, json, sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PAGE='answers/plan-of-salvation.html'
DATA=ROOT/'docs/plan-of-salvation'
CHAPTERS=['before-birth','creation','fall-agency','mortal-life','redeemer','covenants','spirit-world','resurrection-judgment','eternal-life','today']
BODY={'belong','purpose','earth','tend','labor','choose','care','return','bore','burdens','small-voices','between','redemption-dead','life-with-god','long-view','begin'}
def check_structure(text):
 s=BeautifulSoup(text,'html.parser'); d=json.loads((DATA/'content.json').read_text(encoding='utf-8'))
 assert [n.get('id') for n in s.select('section.jj-chapter')]==CHAPTERS, 'Exact ten ordered chapters required'
 assert [a.get('href') for a in s.select('.jj-local-nav a')]==['#'+x for x in CHAPTERS], 'Chapter navigation mismatch'
 assert len(s.select('main .pos-study-unit'))==20, 'Twenty substantive study units required'
 assert len({x.get('id') for x in s.select('[id]')})==len(s.select('[id]')), 'Duplicate IDs'
 sources={x['id']:x for x in d['sources']}
 for chapter in d['chapters']:
  for unit in chapter['units']:
   node=s.select_one('#study-'+unit['id']); assert node, unit['id']
   assert [p.get_text() for p in node.select('.jj-reading > p')]==unit['paragraphs'], unit['id']+': reviewed prose changed'
   hrefs={a.get('href') for a in node.select('a')}
   assert all(sources[k]['url'] in hrefs for k in unit['source_ids']), unit['id']+': exact reviewed source selection missing'
 figures=s.select('main figure[data-exclusive-artwork]')
 assert {f['data-exclusive-artwork'] for f in figures}=={'pos-'+x for x in BODY} and len(figures)==16, 'Sixteen new body originals required'
 for f in figures:
  assert f.select_one('a[data-full-image-viewer][aria-haspopup="dialog"]') and f.select_one('figcaption .fc-study-visual-sources a'), 'Picture study controls missing'
 references=s.select('.pos-owned-reference');assert len(references)==3, 'Three references to existing owning studies required'
 for ref in references:
  assert not ref.select('[data-exclusive-artwork]') and ref.name!='figure', 'Existing art must not be counted as a new original'
  urls={a['href'] for a in ref.select('a[href]')};assert len(urls)==1
  url=urlsplit(next(iter(urls)));assert not url.netloc and url.path.endswith('.html') and url.path!='/'+PAGE
  target=ROOT/url.path.lstrip('/');assert target.is_file()
  owner=BeautifulSoup(target.read_text(encoding='utf-8'),'html.parser');anchor=owner.find(id=url.fragment)
  assert url.fragment and anchor, 'Reference must reach owning artwork'
  own_figure=anchor if anchor.name=='figure' else anchor.find('figure')
  assert own_figure and own_figure.find('img'), 'Reference destination must contain owning artwork'
  def asset_path(page,value):
   raw=urlsplit(value).path
   return (ROOT/raw.lstrip('/') if raw.startswith('/') else page.parent/raw).resolve()
  assert len(ref.select('img'))==1 and asset_path(ROOT/PAGE,ref.select_one('img')['src'])==asset_path(target,own_figure.find('img')['src']), 'Reference thumbnail must be the exact owning image'
  assert 'fc-resource-card__play' not in ref.get('class',[]) and not ref.select('.fc-resource-card__play, [data-full-image-viewer], [data-hero-viewer]'), 'Reference must not copy an artwork or video player'

 hero=s.select_one('.fc-topic-opening a[data-hero-record="plan-of-salvation"]');assert hero and hero.get('href')=='/assets/heroes/plan-of-salvation-hero-full.webp'
 assert 'plan-of-salvation-hero-mobile.webp' in hero.get('style','') and s.select_one('.fc-scroll-cue[href="#main-content"]'), 'Standard responsive opening missing'
 cards=s.select('.fc-resource-card[data-resource-key]');resources=json.loads((DATA/'resources.json').read_text(encoding='utf-8'))['resources']
 assert len(cards)==len(resources)==6 and all(c.parent is cards[0].parent for c in cards) and 'fc-resource-grid' in cards[0].parent.get('class',[]), 'Six talks need one bounded grid'
 for card,record in zip(cards,resources):
  im=card.select_one('img');assert im and im['src']==record['thumbnail']['url'] and [int(im['width']),int(im['height'])]==[record['thumbnail']['width'],record['thumbnail']['height']] and int(im['width'])>=900, 'Talk thumbnail source/resolution changed'
  assert any(a.get('href')==record['url'] for a in card.select('a')), 'Talk destination mismatch'
 assert s.select_one('link[href*="complete-card-rows.css"]') and s.select_one('script[src*="topic-artwork-details.js"]') and s.select_one('script[src*="jesus-journey.js"]')
 asks=[a for a in s.select('a[href]') if urlsplit(a['href']).path=='/ask.html'];assert asks
 assert all(parse_qs(urlsplit(a['href']).query).get('return',[''])[0].startswith('/'+PAGE+'#') for a in asks), 'Ask return context missing'
 return s

def check_art(s, review=None):
 if review is None:review=json.loads((DATA/'art-review.json').read_text(encoding='utf-8'))
 arts=review['artworks'];assert set(arts)=={'pos-'+x for x in BODY}
 seen=set()
 for f in s.select('main figure[data-exclusive-artwork]'):
  key=f['data-exclusive-artwork'];a=arts[key]
  assert a['owner']=='/'+PAGE and a['review_status']=='pass' and a['owner_approved'] is False
  assert a['independent_review']['review_status']=='pass' and a['independent_review']['sha256']==a['original_sha256'], key+': independent review must bind exact original'
  im=f.select_one('img');link=f.select_one('a')
  assert link['href']=='/'+a['asset'] and im['src']=='/'+a['thumbnail'] and im['alt']==a['alt']
  for field in ('asset','thumbnail','original'):
   path=ROOT/a[field];assert path.resolve().is_relative_to(ROOT.resolve()) and path.is_file(),key+': missing '+field
   assert hashlib.sha256(path.read_bytes()).hexdigest()==a[field+'_sha256'],key+': changed '+field
  with Image.open(ROOT/a['asset']) as image:digest=hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
  assert digest not in seen, 'Distinct original pixels required';seen.add(digest)
 hero=review['hero'];assert hero['owner']=='/'+PAGE and hero['includes_christ'] is True and hero['owner_approved'] is False
 assert hero['identity_reference']=='assets/heroes/home-christ-signature-approved-20260907.png'
 for path,expected in [(hero['original'],hero['original_sha256']),(hero['identity_reference'],hero['identity_reference_sha256'])]:assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected, 'Hero original/identity changed'
 independent=json.loads((ROOT/hero['independent_review']).read_text(encoding='utf-8'))
 assert independent['sha256']==hero['original_sha256'] and independent['asset']==hero['original'], 'Hero independent review mismatch'
 assert set(hero['deliveries'])=={'full','1600','mobile'}
 for name,record in hero['deliveries'].items():
  assert record['asset']=='assets/heroes/plan-of-salvation-hero-'+name+'.webp'
  assert hashlib.sha256((ROOT/record['asset']).read_bytes()).hexdigest()==record['sha256'], 'Hero delivery changed'


def selftest(text):
 mutants=[text.replace('id="before-birth"','id="missing"',1),text.replace('data-exclusive-artwork="pos-belong"','data-exclusive-artwork="pos-purpose"',1),text.replace('plan-of-salvation-hero-mobile.webp','missing-mobile.webp',1),text.replace('class="fc-resource-grid"','class="unbounded"',1),text.replace('id=p22-p26','id=p22-p25')]
 ref=check_structure(text).select_one('.pos-owned-reference');image=ref.select_one('img')['src']
 mutants.extend([text.replace(image,'/assets/heroes/home.webp',1),text.replace('class="fc-resource-card pos-owned-reference"','class="fc-resource-card pos-owned-reference fc-resource-card__play"',1)])
 for i,mutant in enumerate(mutants):
  assert mutant!=text, 'Fixture did not mutate'
  try:check_structure(mutant)
  except AssertionError:continue
  raise AssertionError('Negative fixture accepted '+str(i))
 if '--structure-only' not in sys.argv:
  reviewed=json.loads((DATA/'art-review.json').read_text(encoding='utf-8'));soup=check_structure(text)
  mutations=[(('artworks','pos-belong','owner_approved'),True),(('artworks','pos-belong','asset_sha256'),'0'*64),(('artworks','pos-belong','independent_review','sha256'),'0'*64),(('hero','deliveries','mobile','sha256'),'0'*64),(('hero','identity_reference_sha256'),'0'*64)]
  for path,value in mutations:
   changed=copy.deepcopy(reviewed);node=changed
   for key in path[:-1]:node=node[key]
   node[path[-1]]=value
   try:check_art(soup,changed)
   except AssertionError:continue
   raise AssertionError('Artwork mutation accepted '+str(path))
 print('PLAN QA SELFTEST PASS: seven structure/source/reference and five artwork/identity mutations rejected' if '--structure-only' not in sys.argv else 'PLAN structure mutation tests PASS; artwork mutations not run')

def check():
 text=(ROOT/PAGE).read_text(encoding='utf-8');s=check_structure(text)
 if '--selftest' in sys.argv:selftest(text)
 if '--structure-only' not in sys.argv:check_art(s)
 print('PLAN QA PASS: ten chapters, twenty teaching units, sixteen body originals, three owning-study previews, six source-matched talks'+(' (structure only; art readiness not attested)' if '--structure-only' in sys.argv else '; exact independently reviewed art hashes'))
if __name__=='__main__':check()
