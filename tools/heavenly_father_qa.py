"""Verify the enriched Father study, preserved artwork and exact owning-study reference."""
import hashlib,json,sys,copy
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from bs4 import BeautifulSoup,NavigableString
ROOT=Path(__file__).resolve().parents[1]
PAGE='answers/god-our-heavenly-father.html'
DATA=ROOT/'docs/heavenly-father'
CHAPTERS=['begin-study','abraham-inherited-records','teach-along-the-way','inherited-words-personal-prayer','the-son-shows-the-father','restoration-witness','seek-god','divine-purpose','nourish-faith','watch-and-study']
ART={'adam-eve-teach','kept-record','abraham-records','teach-on-the-way','kirtland-readers'}
def check_reference(text):
 s=BeautifulSoup(text,'html.parser');refs=s.select('.hf-owned-reference')
 assert len(refs)==1,'Exactly one Enos owning-study reference'
 ref=refs[0];dest='/answers/what-is-the-book-of-mormon.html#keepers-of-the-record';asset='/assets/page-art/book-of-mormon-stories/05-enos-prayer-960.webp'
 assert ref.get('data-linked-picture-reference')=='enos-prayer' and ref.name=='article'
 assert len(ref.select('img'))==1 and ref.select_one('img')['src']==asset,'Exact existing Enos thumbnail'
 assert len(ref.select('a[href]'))==2 and all(a['href']==dest for a in ref.select('a[href]')),'Exact owning Enos destination'
 assert not any(ref.has_attr(k) for k in ('data-exclusive-artwork','data-full-image-viewer','data-hero-viewer')) and not ref.select('[data-exclusive-artwork],[data-full-image-viewer],[data-hero-viewer],.fc-resource-card__play'),'Reference cannot duplicate viewer or original'
 owner=BeautifulSoup((ROOT/'answers/what-is-the-book-of-mormon.html').read_text(encoding='utf-8'),'html.parser')
 assert any(urlsplit(im['src']).path.endswith(asset.lstrip('/')) for im in owner.select('#keepers-of-the-record img')),'Owning artwork must remain at destination'
 return s

def check_structure(text):
 s=check_reference(text);old=BeautifulSoup((DATA/'original-page.txt').read_text(encoding='utf-8'),'html.parser')
 sections=s.select('main>section');assert [x['id'] for x in sections if not x.get('data-chapter-group')]==CHAPTERS,'Ten ordered chapter leaders'
 assert all(s.find(id=x['id']) for x in old.select('[id]')),'Existing bookmarks preserved'
 assert len(s.select('[id]'))==len({x['id'] for x in s.select('[id]')}),'Duplicate IDs'
 for im in old.select('img'):
  # Nelson is the sole explicitly reviewed native thumbnail upgrade.
  if im.find_parent(attrs={'data-resource-key':'god-overcome-world'}):continue
  # Wyatt removed this repeated preview; preserve its exact owning study instead.
  if im.find_parent(attrs={'data-linked-picture-reference':'modern-scripture'}):
   assert im.get('src')=='/assets/page-art/jesus-journey/modern-scripture-960.webp'
   refs=s.select('[data-linked-study-reference="modern-scripture"]')
   assert len(refs)==1 and not refs[0].select('img'),'Removed preview must remain text-only'
   dest='/answers/jesus-christ-latter-day-saint-beliefs.html#picture-modern-scripture'
   assert refs[0].select_one('.fc-actions.fc-actions--content > a.fc-button[href="'+dest+'"]'),'Exact scripture owning-study path preserved'
   owner=BeautifulSoup((ROOT/'answers/jesus-christ-latter-day-saint-beliefs.html').read_text(encoding='utf-8'),'html.parser')
   assert owner.select_one('#picture-modern-scripture img[src="'+im['src']+'"]'),'Original picture retained on owner'
   continue
  assert any(n.get('src')==im.get('src') for n in s.select('img')),'Existing image source changed'
 guide=s.select('.fc-topic-opening p.fc-father-opening-guide');assert len(guide)==1 and guide[0].get_text()=='Explore scripture about our Heavenly Father, His love, and our relationship with Him. Follow the passages and questions throughout the study.' and guide[0].get('class')==['fc-topic-subtitle','fc-father-opening-guide'] and not guide[0].has_attr('hidden'),'Exact permanent owner-requested opening guide'
 opening=copy.deepcopy(s.select_one('.fc-topic-opening'));opening.select_one('.fc-father-opening-guide').decompose()
 assert str(opening)==str(old.select_one('.fc-topic-opening')),'Only the exact authored guide may change the protected opening'
 d=json.loads((DATA/'content-plan.json').read_text(encoding='utf-8'))
 for unit in d['chapters']:
  node=s.find(id='study-hf-'+unit['id']);assert node,'Missing new teaching unit'
  prose=node.get_text(' ',strip=True)
  for paragraph in unit['paragraphs']:assert ' '.join(paragraph.split()) in ' '.join(prose.split()),'Reviewed paragraph changed'
  for source in unit['sources']:assert node.select_one('a[href="'+source['url']+'"]'),'Source omitted'
 assert {x['data-exclusive-artwork'] for x in s.select('[data-exclusive-artwork^="hf-"]')}=={'hf-'+x for x in ART}
 for x in s.select('.fc-study-visual-sources'):assert not any(isinstance(y,NavigableString) and '\u00b7' in str(y) for y in x.children),'No separator dots'
 assert s.select_one('#continue-study a[href="holy-ghost.html"]'),'Holy Ghost onward path'
 asks=[a for a in s.select('a[href]') if urlsplit(a['href']).path=='/ask.html'];assert len(asks)==10
 for a in asks:assert parse_qs(urlsplit(a['href']).query).get('return',[''])[0].startswith('/'+PAGE+'#'),'Ask return context'
 return s

def check_art(s,review=None):
 review=review or json.loads((DATA/'art-review.json').read_text(encoding='utf-8'))
 independent=json.loads((DATA/'independent-art-review.json').read_text(encoding='utf-8'))['assets']
 assert {a['id'] for a in review['items']}==ART
 for a in review['items']:
  assert a['source_checked_before_generation'] is True
  assert hashlib.sha256((ROOT/a['original']).read_bytes()).hexdigest()==a['original_sha256'],'Original hash changed'
  assert any(x['sha256']==a['original_sha256'] and x['status']=='pass_candidate' for x in independent),'Independent exact image review missing'
  if a['identity_reference']:assert hashlib.sha256((ROOT/a['identity_reference']).read_bytes()).hexdigest()==a['reference_sha256'],'Identity reference changed'
  f=s.find(id='picture-hf-'+a['id']);assert f
  for x in a['derivatives']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],'Derivative changed'
  thumb=next(x['path'] for x in a['derivatives'] if x['width']==800);full=next(x['path'] for x in a['derivatives'] if x['path'].endswith('-full.webp'))
  assert f.select_one('img')['src']=='/'+thumb and f.select_one('a')['href']=='/'+full,'Reviewed delivery mismatch'

def selftest(text):
 mutations=[('enos-prayer-960.webp','wrong.webp'),('#keepers-of-the-record','#wrong'),('class="hf-owned-reference','data-full-image-viewer class="hf-owned-reference'),('id="abraham-inherited-records"','id="bad"'),('hf-adam-eve-teach','hf-wrong'),('kept-record-v2-800.webp','kept-record-800.webp'),('href="holy-ghost.html"','href="wrong.html"'),('#picture-modern-scripture','#wrong-scripture-owner'),('data-linked-study-reference="modern-scripture">','data-linked-study-reference="modern-scripture"><img src="/assets/page-art/jesus-journey/modern-scripture-960.webp">')]
 for old,new in mutations:
  assert old in text,old
  try:check_art(check_structure(text.replace(old,new,1)))
  except AssertionError:pass
  else:raise AssertionError('Mutation escaped: '+old)
 review=json.loads((DATA/'art-review.json').read_text(encoding='utf-8'));review['items'][0]['original_sha256']='0'*64
 try:check_art(check_structure(text),review)
 except AssertionError:pass
 else:raise AssertionError('Hash mutation escaped')
 print('PASS 10 Father mutation fixtures')
if __name__=='__main__':
 text=(ROOT/PAGE).read_text(encoding='utf-8');check_art(check_structure(text))
 if '--selftest' in sys.argv:selftest(text)
 print('PASS Father chapters, original bookmarks/art, five reviewed new pictures and owning Enos reference')
