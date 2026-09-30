"""Owner-authorized duplicate-card repairs: exact art, one placement, original references."""
from pathlib import Path
import hashlib,json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def check(overrides=None):
 overrides=overrides or {}
 def html(name):return overrides.get(name) if name in overrides else (ROOT/name).read_text(encoding="utf8")
 records=json.loads((ROOT/'docs/artwork-uniqueness-audit-20260929/new-art-review.json').read_text(encoding='utf8'))
 assert len(records)==11 and len({r['source_sha256'] for r in records})==11,'Eleven distinct source originals required'
 stand=BeautifulSoup(html('answers/stand-forever.html'),'html.parser')
 cfm=BeautifulSoup(html('come-follow-me.html'),'html.parser')
 art=BeautifulSoup(html('art.html'),'html.parser')
 assert len(art.select('.gallery > *'))==39,'Balanced Art rows require review when artwork count changes'
 assert '--fc-gallery: 1440px;' in html('site-system.css'),'Gallery maximum width changed'
 assert hashlib.sha256(html('art-experience.css').encode('utf-8')).hexdigest()=='ef21dea3b87e8b3e59454aba32726210a783d87d556928201ef375a3627b1c74','Reviewed Art row thresholds or offset styling changed'
 assert art.select_one('link[href="art-experience.css?v=20260929-balanced-gallery-1"]'),'Gallery cache key not propagated'
 for r in records:
  assert r['independent_review'] is True,r['id']+' lacks independent review'
  for field in ['full','thumbnail']:
   assert hashlib.sha256((ROOT/r[field]).read_bytes()).hexdigest()==r[field+'_sha256'],r['id']+' asset changed'
  page=stand if r['id'].startswith('stand-') else art if r['id'].startswith('art-') else cfm
  nodes=[n for n in page.select('img') if n.get('src','').lstrip('./')==r['thumbnail']]
  assert len(nodes)==1,r['id']+' needs one placement'
  if page is stand:assert nodes[0].find_parent('a',class_='fc-foundation-card__image'),r['id']+' misplaced'
  elif page is cfm:
   assert nodes[0].find_parent('figure',class_='cfm-tool'),r['id']+' misplaced'
   assert nodes[0].parent.name=='a' and nodes[0].parent.get('href')==r['full']
   assert nodes[0].find_parent('figure').select_one('figcaption a.cfm-tool-resource[href^="https://www.churchofjesuschrist.org/"]')
  else:assert nodes[0].find_parent('a').has_attr('data-artwork-detail'),r['id']+' misplaced'
 for asset in ['stand-prayerful-question','stand-record-context','stand-faithful-service']:
  assert len(stand.select('figure img[src*="'+asset+'"]'))==1,'Retain original owning figure '+asset
  assert len(stand.select('img[src*="'+asset+'"]'))==1,'Repeated original family '+asset
 for asset in ['personal-study-2026','family-study-2026','old-testament-journey-2026']:
  assert len(cfm.select('figure.cfm-path img[src*="'+asset+'"]'))==1,'Retain original CFM study '+asset
  assert len(cfm.select('img[src*="'+asset+'"]'))==1,'Repeated CFM original family '+asset
 answers=BeautifulSoup(html('answers.html'),'html.parser')
 art=BeautifulSoup(html('art.html'),'html.parser')
 gc=BeautifulSoup(html('general-conference.html'),'html.parser')
 owner_labels = {'ask.html': 'Ask', 'answers.html': 'Answers Library', 'watch.html': 'Watch and Study', 'art.html': 'Art', 'missionary.html': 'Mission', 'church-history.html': 'Church History', 'pioneers.html': 'Pioneers', 'general-conference.html': 'General Conference', 'come-follow-me.html': 'Come, Follow Me', 'answers/look-unto-me-doctrine-and-covenants-6-36.html': 'Look unto Me'}
 for nodes in [cfm.select('.cfm-library-card'),gc.select('.gc-pathway')]:
  assert len(nodes)==9
  for node in nodes:
   link=node if node.name=='a' else node.select_one('a[href]')
   destination=link['href'].split('#')[0]
   assert 'Picture from '+owner_labels[destination] in node.get_text(),'Wrong artwork owner label: '+destination
 assert gc.select_one('.gc-pathway[href="answers/look-unto-me-doctrine-and-covenants-6-36.html"] img[src="assets/heroes/home-christ-signature-approved-20260907.png"]')
 assert answers.select_one('[data-linked-picture-reference="cfm-personal-study"] a[href="come-follow-me.html#personal-study-art"]')
 assert cfm.select_one('#personal-study-art img[src*="personal-study-2026"]')
 assert cfm.select_one('[data-linked-picture-reference="conference-listening"] a[href="general-conference.html#conference-listening-art"] img[src*="conference-listening-960"]')
 assert gc.select_one('#conference-listening-art img[src*="conference-listening-960"]')
 assert art.select_one('.gallery-original-reference a[href="answers.html#answers-christ-portrait"]')
 assert answers.select_one('#answers-christ-portrait img[src="assets/answers-christ-portrait.png"]')
 for asset in ['The-Living-Christ','The-Good-Shephard','Suffer-the-Little-Children','Be-Still']:
  assert len(art.select('img[src*="'+asset+'"]'))==1,'Repeated original gallery family '+asset
 for slug in ['be-still','the-good-shepherd','suffer-the-little-children']:
  study=BeautifulSoup(html('art-study/'+slug+'.html'),'html.parser')
  assert study.select_one('a[href="../art.html#gallery-original-'+slug+'"]') and art.select_one('#gallery-original-'+slug)
 print('ARTWORK REPAIR QA PASS: eleven exact reviewed originals, eleven sole card placements, preserved owning pictures, three explicit original references.')
def self_test():
 stand=(ROOT/'answers/stand-forever.html').read_text(encoding='utf8')
 answers=(ROOT/'answers.html').read_text(encoding='utf8')
 changed=stand.replace('../assets/page-art/uniqueness-repairs/stand-creation-inquiry-960.webp','../assets/page-art/exclusive/stand-prayerful-question-800.webp')
 duplicated=stand.replace('<div class="fc-primary-grid fc-foundation-grid">','<div class="fc-primary-grid fc-foundation-grid"><img src="../assets/page-art/exclusive/stand-prayerful-question-1536.webp" alt="Restored duplicate">',1)
 wrong=answers.replace('come-follow-me.html#personal-study-art','general-conference.html#conference-listening-art')
 gallery=(ROOT/'art.html').read_text(encoding='utf8')
 css=(ROOT/'art-experience.css').read_text(encoding='utf8')
 for case in [{'art.html':gallery.replace('<div class="gallery" id="art-gallery">','<div class="gallery" id="art-gallery"><div class="unexpected-card"></div>',1)},{'art-experience.css':css.replace('/ 10)', '/ 9)')},{'site-system.css':(ROOT/'site-system.css').read_text(encoding='utf8').replace('--fc-gallery: 1440px;', '--fc-gallery: 1600px;')},{'answers/stand-forever.html':changed},{'answers/stand-forever.html':duplicated},{'answers.html':wrong}]:
  try:check(case)
  except AssertionError:pass
  else:raise AssertionError('Duplicate or wrong-owner mutation escaped')
 print('ARTWORK REPAIR negative fixtures PASS: gallery count/offset/maximum-width drift, restored old card, original size duplicate, wrong owner rejected.')
if __name__=='__main__':
 check()
 self_test()
