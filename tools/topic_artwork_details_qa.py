#!/usr/bin/env python3
"""Verify every body-artwork entry can reach the shared contextual detail adapter."""
from pathlib import Path
import json
import hashlib
from urllib.parse import urlsplit
from answer_study_qa import Document
from study_gap_art_qa import sitewide_entries
from build_jesus_journey import validate_artwork_review
ROOT=Path(__file__).resolve().parents[1]
from first_topic_completion_qa import check as check_first_topic_completion
first_topic_review=check_first_topic_completion(ROOT)
first_topic_assets=[]

# Only these three reviewed additions are outside the unchanged 99/3 baseline.
REVIEWED_READING_ART = {'assets/page-art/stand-forever-journey/stand-john6-remain-full.webp': {'owner': 'answers/stand-forever.html', 'key': 'stand-john6-remain', 'figure_sha256': 'dfe7b41ca2795f1ab6e53348a32d7087c0578524a00268aef4543517d11523d8', 'assets': {'assets/page-art/stand-forever-journey/stand-john6-remain-full.webp': 'f9bc997a86d7f85695eeb32cabf1ae9e76e88122ff6a6efba8a247a408bd78a6', 'assets/page-art/stand-forever-journey/stand-john6-remain-960.webp': 'bcbfa7bb0face64659185fe097bf8ae213e100b14b3de8765a549b15dc113aab', 'assets/page-art/stand-forever-journey/stand-john6-remain-original.png': '3384d4a1a3599ab7c789ab1f1a712c66519f01851f9e46d23bd1e1d51eda709b'}}, 'assets/page-art/stand-forever-journey/stand-john7-do-his-will-full.webp': {'owner': 'answers/stand-forever.html', 'key': 'stand-john7-do-his-will', 'figure_sha256': 'b56130f6cef10260bc1a9e8cd4105ab91e4c51bcdb33f270fb318ca5cb587a17', 'assets': {'assets/page-art/stand-forever-journey/stand-john7-do-his-will-full.webp': 'fb9cd7f0a0c4f1612f428375729bcd3685046427da82b3cdbda13a91be0f9029', 'assets/page-art/stand-forever-journey/stand-john7-do-his-will-960.webp': '43be5dbb873b53460c987d8cfc06a6342a1c5f2c208da6e3fa3cb8d2828f31b8', 'assets/page-art/stand-forever-journey/stand-john7-do-his-will-original.png': 'd04caa98a349c66f1112930b89869196bf1dce9e3590f8445c48fc0f71c86072'}}, 'assets/page-art/visual-rhythm-journey/temple-tribute-full.webp': {'owner': 'answers/why-latter-day-saints-build-temples.html', 'key': 'temple-tribute', 'figure_sha256': '56ff33e46e3326db3c459f13f09917f96e687c7e18460bcf83892a31150b1c49', 'assets': {'assets/page-art/visual-rhythm-journey/temple-tribute-full.webp': 'de729b17b7a72a14b6f667c9a23a4f064c4d7883dab1d5d1d430f80e7f1820bf', 'assets/page-art/visual-rhythm-journey/temple-tribute-960.webp': 'fc1dff1127af137bdf0cf20d3da8833b6b6180940aa7dd019106bb022f5e050a', 'assets/page-art/visual-rhythm-journey/temple-tribute-original.png': 'e1cbd9cf09065630f8af52791c9832cf93e1c0be0f75893b138e1f4cede47195'}}}

def check_reading_art(route, source, verify_assets=True):
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(source, 'html.parser')
 for full, row in REVIEWED_READING_ART.items():
  # Match asset references as well as keys so a renamed marker cannot evade ownership.
  candidates=[f for f in soup.find_all('figure') if f.get('data-topic-art')==row['key'] or any(Path(a).name in str(f) for a in row['assets'])]
  expected=1 if row['owner']==route else 0
  assert len(candidates)==expected, route+': missing, duplicate or wrong-owner reviewed artwork'
  if not expected:continue
  figure=candidates[0]
  assert hashlib.sha256(str(figure).encode()).hexdigest()==row['figure_sha256'], route+': reviewed figure markup changed'
  if verify_assets:
   for asset,digest in row['assets'].items():
    assert hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()==digest, asset+': reviewed image bytes changed'

def reading_art_self_test():
 from bs4 import BeautifulSoup
 for full,row in REVIEWED_READING_ART.items():
  route=row['owner']; source=(ROOT/route).read_text(encoding='utf-8')
  figure=str(BeautifulSoup(source, 'html.parser').select_one('figure[data-topic-art="'+row['key']+'"]'))
  for kind in ('missing','duplicate','markup','asset','wrong-owner'):
   soup=BeautifulSoup(source,'html.parser'); current=soup.select_one('figure[data-topic-art="'+row['key']+'"]')
   if kind=='missing':current.decompose()
   elif kind=='duplicate':soup.append(BeautifulSoup(figure,'html.parser'))
   elif kind=='markup':current['data-topic-art']='unreviewed'
   elif kind=='asset':current.find('img')['src']='unreviewed.webp'
   try:check_reading_art('answers/unreviewed.html' if kind=='wrong-owner' else route,str(soup),False)
   except AssertionError:pass
   else:raise AssertionError('Reviewed artwork mutation escaped: '+kind)

reading_art_self_test()
reading_art_assets=[]


# The approved Winter scene is the only seasonal addition on an Answer page.
# Its exact family remains separate from the unchanged legacy 99/3 baseline.
WINTER_OWNER='answers/why-families-are-important.html'
WINTER_KEY='christ-winter-laughter'
WINTER_FULL='assets/page-art/christ-world/christ-winter-laughter-full.webp'
WINTER_FIGURE_SHA='99227e589a6095a88ae67fd84309aafbb386b66f4b7c65849c38eb9cc337a8bf'
WINTER_ASSETS={
 'assets/page-art/christ-world/christ-winter-laughter-640.webp':'0357025d0b8b4772e16a7df7ca7f8c6171826114e1187954be9e631759f0a108',
 'assets/page-art/christ-world/christ-winter-laughter-960.webp':'2c3e9b8067d4fcdf2b283981ca48e06e48395e8b75d7a3ebb7b82ecbc5e39fe9',
 WINTER_FULL:'c88c3ff2656c7fd1a0e44e462b073b4ab3643978085f43249a742f7ce5b59d04',
 'assets/page-art/christ-world/masters/christ-winter-laughter.png':'9d4bc85cd2f4b6977926688a2e4c5385c96284874c937ffd46bed54bed5b63a5'
}
def check_winter_art(route,source,verify_assets=True):
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(source,'html.parser')
 candidates=[f for f in soup.find_all('figure') if f.get('data-exclusive-artwork')==WINTER_KEY or any(Path(a).name in str(f) for a in WINTER_ASSETS)]
 assert len(candidates)==(1 if route==WINTER_OWNER else 0),route+': missing, duplicate or wrong-owner Winter artwork'
 if route!=WINTER_OWNER:return
 figure=candidates[0];anchor=figure.find('a')
 assert anchor and anchor.get('aria-haspopup')=='dialog' and not anchor.has_attr('data-full-image-viewer'),'Winter must open shared study details first'
 assert anchor.get('data-topic-study')=='#hope-reflection','Winter surrounding study destination changed'
 assert hashlib.sha256(str(figure).encode()).hexdigest()==WINTER_FIGURE_SHA,'Winter reviewed figure changed'
 if verify_assets:
  for asset,digest in WINTER_ASSETS.items():
   assert hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()==digest,asset+': Winter reviewed bytes changed'

def winter_art_self_test():
 from bs4 import BeautifulSoup
 source=(ROOT/WINTER_OWNER).read_text(encoding='utf-8')
 figure=str(BeautifulSoup(source,'html.parser').select_one('figure[data-exclusive-artwork="'+WINTER_KEY+'"]'))
 for kind in ('missing','duplicate','markup','asset','wrong-owner','dialog','direct-viewer','study-target'):
  soup=BeautifulSoup(source,'html.parser');current=soup.select_one('figure[data-exclusive-artwork="'+WINTER_KEY+'"]')
  if kind=='missing':current.decompose()
  elif kind=='duplicate':soup.append(BeautifulSoup(figure,'html.parser'))
  elif kind=='markup':current['data-exclusive-artwork']='unreviewed'
  elif kind=='asset':current.find('img')['src']='unreviewed.webp'
  elif kind=='dialog':current.find('a')['aria-haspopup']='false'
  elif kind=='direct-viewer':current.find('a')['data-full-image-viewer']=''
  elif kind=='study-target':current.find('a')['data-topic-study']='#unreviewed'
  try:check_winter_art('answers/unreviewed.html' if kind=='wrong-owner' else WINTER_OWNER,str(soup),False)
  except AssertionError:pass
  else:raise AssertionError('Winter artwork mutation escaped: '+kind)
winter_art_self_test()
winter_art_assets=[]

# Exact three additional modern Answer figures; historical99/3 remains unchanged.
FOUR_SCENE_ANSWER_ART={'assets/page-art/christ-world/christ-moving-day-full.webp': {'owner': 'answers/divorce-and-faith.html', 'key': 'christ-moving-day', 'destination': '#scripture-study', 'figure_sha256': '9dd542a7e977e0ac0e7bfd93f18ed3556f02bbf10d547042d24185dc34c6f5ab', 'assets': {'assets/page-art/christ-world/masters/christ-moving-day.png': '4d8ed6462589a7b2c0574ad60a804e0e2027b654858fbb7b6aed92072e8db198', 'assets/page-art/christ-world/christ-moving-day-480.webp': '362b688d836d3f5a00c9e815654ce8a8262626680e7fba6218c53a21a7706508', 'assets/page-art/christ-world/christ-moving-day-960.webp': '59ab7e8ef417acb7e81d379294707d2edbadafd66ff7882c62630d75e712733d', 'assets/page-art/christ-world/christ-moving-day-full.webp': 'a44edacbd9727be973217e10a45f661d57e805103b77728e065f1b7a3e43406d'}}, 'assets/page-art/christ-world/christ-food-pantry-full.webp': {'owner': 'answers/are-latter-day-saints-christian.html', 'key': 'christ-food-pantry', 'destination': '#guided-practice', 'figure_sha256': '4445bfee207d0dc34baa6ff73d6219e322e66a621567ed3def8374aa8e00a8cc', 'assets': {'assets/page-art/christ-world/masters/christ-food-pantry.png': 'f405305ea6ddd8a78848fced8a1d04d0cfbf78ebbd6abe29c33060ca84a078ff', 'assets/page-art/christ-world/christ-food-pantry-480.webp': '8e14fad5a0435fb1f9e9d684a791957f149ecbd4f2d83335a91948a98ac5c48c', 'assets/page-art/christ-world/christ-food-pantry-960.webp': 'fdaa35344a331368562bcd3fe49476cd51a6124313693245c3fac6f1b1081013', 'assets/page-art/christ-world/christ-food-pantry-full.webp': 'a443d2bfa5f6a703463e5228d7387b83288f9b5166e43780546b319cd57da85c'}}, 'assets/page-art/christ-world/christ-homecoming-celebration-full.webp': {'owner': 'answers/faith-in-jesus-christ-during-trials.html', 'key': 'christ-homecoming-celebration', 'destination': '#continue-study', 'figure_sha256': '12a4bdebc759297678b1aabfb1cc229dc93e84f027f5c5a5369b5b79618d124d', 'assets': {'assets/page-art/christ-world/masters/christ-homecoming-celebration.png': 'd835e757765039247138af12a5fae27cf5655692757254be009dc61576093920', 'assets/page-art/christ-world/christ-homecoming-celebration-480.webp': '68641bc39651fb610b78a485205d556287729f816de6f9b1d309088f1f004753', 'assets/page-art/christ-world/christ-homecoming-celebration-960.webp': 'dc3013031c5490e2e1bb173e92a672c59be31b8caa24f60e73d9cae03d8fd659', 'assets/page-art/christ-world/christ-homecoming-celebration-full.webp': 'fd968aac0a69a982f8301aa775291bd86f2f6e4067fa040cca03b43de54f38f6'}}}

def check_four_scene_answer(route,source,verify_assets=True):
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(source,'html.parser')
 for full,row in FOUR_SCENE_ANSWER_ART.items():
  candidates=[f for f in soup.find_all('figure') if f.get('data-exclusive-artwork')==row['key'] or any(Path(a).name in str(f) for a in row['assets'])]
  assert len(candidates)==(1 if route==row['owner'] else 0),route+': missing, duplicate or wrong-owner modern artwork'
  if route!=row['owner']:continue
  figure=candidates[0];anchor=figure.find('a')
  assert anchor and anchor.get('aria-haspopup')=='dialog' and not anchor.has_attr('data-full-image-viewer'),'Modern artwork must open study details first'
  assert anchor.get('data-topic-study')==row['destination'],'Modern surrounding-study destination changed'
  assert hashlib.sha256(str(figure).encode()).hexdigest()==row['figure_sha256'],'Modern reviewed figure changed'
  if verify_assets:
   for asset,digest in row['assets'].items():assert hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()==digest,asset+': modern reviewed bytes changed'

def four_scene_answer_self_test():
 from bs4 import BeautifulSoup
 for row in FOUR_SCENE_ANSWER_ART.values():
  source=(ROOT/row['owner']).read_text(encoding='utf8')
  for kind in ('missing','duplicate','markup','asset','wrong-owner','dialog','direct-viewer','study-target'):
   soup=BeautifulSoup(source,'html.parser');current=soup.select_one('figure[data-exclusive-artwork="'+row['key']+'"]')
   if kind=='missing':current.decompose()
   elif kind=='duplicate':soup.append(BeautifulSoup(str(current),'html.parser'))
   elif kind=='markup':current['data-exclusive-artwork']='unreviewed'
   elif kind=='asset':current.find('img')['src']='unreviewed.webp'
   elif kind=='dialog':current.find('a')['aria-haspopup']='false'
   elif kind=='direct-viewer':current.find('a')['data-full-image-viewer']=''
   elif kind=='study-target':current.find('a')['data-topic-study']='#unreviewed'
   try:check_four_scene_answer('answers/unreviewed.html' if kind=='wrong-owner' else row['owner'],str(soup),False)
   except AssertionError:pass
   else:raise AssertionError('Modern artwork mutation escaped: '+kind)
four_scene_answer_self_test()
four_scene_answer_assets=[]

def local_asset(page,href):
 u=urlsplit(href)
 assert not u.scheme and not u.netloc, 'Body artwork must be local'
 target=(ROOT/u.path.lstrip('/') if u.path.startswith('/') else page.parent/u.path).resolve()
 assert target.is_relative_to(ROOT), 'Artwork escapes site root'
 return target
def parents(n):
 while n.parent:
  n=n.parent;yield n
errors=[];count=0;preserved=0;panels=0;life_assets=[];gap_assets=[];sitewide_assets=[]
joseph_family=json.loads((ROOT/'docs/joseph-life-enrichment.json').read_text(encoding='utf-8'))['scenes']
joseph_lucy=json.loads((ROOT/'docs/joseph-lucy-family-stories.json').read_text(encoding='utf-8'))['stories']
joseph_archive=json.loads((ROOT/'docs/joseph-family-archival-art.json').read_text(encoding='utf-8'))['items']
joseph_review={s['image']['src'] for s in joseph_family+joseph_lucy} | {s['asset'] for s in joseph_archive}
assert len(joseph_family)==11 and len(joseph_lucy)==10 and len(joseph_archive)==5 and len(joseph_review)==26, 'Exact reviewed Joseph family additions required'
joseph_assets=[]
temple_records=json.loads((ROOT/'docs/temples/art-ready.json').read_text(encoding='utf-8'))
temple_review={v['full']:(k,v) for k,v in temple_records.items()}
temple_assets=[]
journey_review=json.loads((ROOT/'docs/jesus-journey/artworks.json').read_text(encoding='utf-8'))
journey_assets=[]
new_review = {e['asset']: e for e in sitewide_entries() if not e['talk'] and (e['page'].startswith('answers/') or e['page']=='general-conference.html')}
focused_review = {e['asset']: e for e in json.loads((ROOT/'docs/focused-answers-art-review.json').read_text(encoding='utf-8'))['images'] if e['role'] == 'body'}
assert len(focused_review) == 4, 'Exact four new supporting photographs required'
opening_review = {e['asset']: e for e in json.loads((ROOT/'docs/focused-answers-art-review.json').read_text(encoding='utf-8'))['images'] if e['role'] == 'opening'}
assert len(opening_review) == 1 and {e['id'] for e in opening_review.values()} == {'conference-listening'}, 'Exact reviewed Conference opening required'
bom_manifest = json.loads((ROOT/'docs/book-of-mormon-art-review.json').read_text(encoding='utf-8'))
assert bom_manifest.get('page') == 'answers/what-is-the-book-of-mormon.html', 'Book of Mormon review ownership mismatch'
bom_entries = bom_manifest.get('artworks', [])
bom_review = {entry['asset']: entry for entry in bom_entries}
assert bom_entries and len(bom_review) == len(bom_entries), 'Book of Mormon review requires unique original assets'
settle_manifest=json.loads((ROOT/'docs/settle-heart-art-review.json').read_text(encoding='utf-8'))
assert settle_manifest['page']=='answers/settle-this-in-your-hearts.html'
settle_review={e['asset']:e for e in settle_manifest['artworks'][1:]}
assert len(settle_review)==14, 'Settled faith requires fourteen supporting originals plus its distinct hero'
bible_manifest=json.loads((ROOT/'docs/bible-together-art-review.json').read_text(encoding='utf-8'))
assert bible_manifest.get('page')=='answers/bible-and-book-of-mormon-together.html', 'Bible together review ownership mismatch'
bible_entries=bible_manifest.get('artworks',[])
bible_review={e['asset']:e for e in bible_entries}
assert len(bible_entries)==len(bible_review)==13 and len({e['key'] for e in bible_entries})==13, 'Bible together requires thirteen distinct reviewed supporting originals'
bible_assets=[]
covenant_manifest=json.loads((ROOT/'docs/abrahamic-covenant/art-review.json').read_text(encoding='utf-8'))
covenant_entries=covenant_manifest['artworks']
covenant_review={record['asset']:(key,record) for key,record in covenant_entries.items()}
assert len(covenant_entries)==len(covenant_review)==12, 'Covenant requires exactly twelve distinct reviewed originals'
assert all(key.startswith('ac-') and record['owner']=='/answers/abrahamic-covenant.html' for key,record in covenant_entries.items()), 'Covenant review ownership mismatch'
covenant_assets=[]
from holy_ghost_qa import check as check_holy_ghost
check_holy_ghost()
hg_review={v['asset']:(k,v) for k,v in json.loads((ROOT/'docs/holy-ghost/art-review.json').read_text(encoding='utf-8'))['artworks'].items()}
hg_assets=[]
from plan_of_salvation_qa import check as check_plan
check_plan()
plan_review={v['asset']:(k,v) for k,v in json.loads((ROOT/'docs/plan-of-salvation/art-review.json').read_text(encoding='utf-8'))['artworks'].items()}
plan_assets=[]
from heavenly_father_qa import check_structure as check_father_structure, check_art as check_father_art
check_father_art(check_father_structure((ROOT/'answers/god-our-heavenly-father.html').read_text(encoding='utf-8')))
father_review={next(x['path'] for x in a['derivatives'] if x['path'].endswith('-full.webp')):a for a in json.loads((ROOT/'docs/heavenly-father/art-review.json').read_text(encoding='utf-8'))['items']}
assert len(father_review)==5
father_assets=[]
settle_assets=[]
bom_assets=[]
opening_assets=[]
focused_assets=[]; relocated_assets=[]
relocated_names={'aaronic-priesthood','joseph-baptizes-oliver','oliver-baptizes-joseph','melchizedek-priesthood','apostles-ordain-joseph','apostles-ordain-oliver'}
for page in [*sorted((ROOT/'answers').glob('*.html')),ROOT/'general-conference.html']:
 source=page.read_text(encoding='utf-8')
 check_reading_art(page.relative_to(ROOT).as_posix(),source)
 check_winter_art(page.relative_to(ROOT).as_posix(),source)
 check_four_scene_answer(page.relative_to(ROOT).as_posix(),source)
 d=Document();d.feed(source);ns=list(d.root.walk())
 if page.relative_to(ROOT).as_posix()=='answers/race-priesthood-and-temple-blessings.html':
  # Official source media open their Church destinations; they are not original
  # artwork requiring the site's picture-detail adapter. No other page is exempt.
  cards=[n for n in ns if n.has('fc-resource-card')]
  assert len(cards)==6 and len({n.attrs.get('data-resource-key') for n in cards})==6
  assert not any('data-exclusive-artwork' in n.attrs or 'data-hero-viewer' in n.attrs or 'data-topic-art' in n.attrs for n in ns)
  for card in cards:
   anchors=[n for n in card.walk() if n.tag=='a']
   assert len(anchors)==2 and all(urlsplit(n.attrs.get('href','')).hostname=='www.churchofjesuschrist.org' for n in anchors)
   assert not any('data-full-image-viewer' in n.attrs or n.attrs.get('aria-haspopup')=='dialog' for n in anchors)
  continue
 for asset,tag,attr in [('topic-artwork-details.js','script','src'),('topic-artwork-details.css','link','href')]:
  if sum(n.tag==tag and asset in n.attrs.get(attr,'') for n in ns)!=1:errors.append(f'{page.name}: missing or duplicate {asset}')
 for panel in [n for n in ns if n.has('fc-study-feature') and any(c.has('fc-study-visual') for c in n.walk())]:
  panels+=1
  if not panel.has('fc-study-feature--illustrated'):errors.append(page.name+': body artwork still nested in split study panel')
  for f in [n for n in panel.walk() if n.has('fc-study-visual')]:
   if f.parent is not panel:errors.append(page.name+': artwork not lifted out of narrow study/media column')
 for a in [n for n in ns if n.tag=='a' and 'href' in n.attrs and (n.parent.tag=='figure' or n.has('fc-marriage-era__art') or n.has('fc-foundation-card__image'))]:
  if not any(n.tag=='img' for n in a.walk()) or not any(n.tag=='main' for n in parents(a)):continue
  if any(n.has('fc-resource-card') or n.tag=='dialog' for n in parents(a)):continue
  if 'data-artwork-detail' in a.attrs:
   preserved+=1;continue
  count+=1;container=a.parent
  cap=next((n for n in container.walk() if n.tag=='figcaption' or n.has('fc-marriage-era__copy') or n.has('fc-foundation-card-copy')),None)
  if cap is None or not cap.text().strip():errors.append(page.name+': missing approved body caption')
  sources=[n for n in cap.walk() if n.tag=='a' and urlsplit(n.attrs.get('href','')).hostname in ('www.churchofjesuschrist.org','newsroom.churchofjesuschrist.org')] if cap else []
  if not sources and 'data-topic-study' not in a.attrs and page.name not in ('grief-and-faith.html','general-conference.html'):errors.append(page.name+': body source unavailable without unrelated page fallback')
  relative_asset=local_asset(page,a.attrs['href']).relative_to(ROOT).as_posix()
  if relative_asset in REVIEWED_READING_ART:
   assert page.relative_to(ROOT).as_posix()==REVIEWED_READING_ART[relative_asset]['owner'], 'Reading artwork owner mismatch'
   reading_art_assets.append(relative_asset)
  elif relative_asset==WINTER_FULL:
   assert page.relative_to(ROOT).as_posix()==WINTER_OWNER and container.attrs.get('data-exclusive-artwork')==WINTER_KEY, 'Winter exact owner/key mismatch'
   assert a.attrs.get('aria-haspopup')=='dialog' and 'data-full-image-viewer' not in a.attrs and a.attrs.get('data-topic-study')=='#hope-reflection', 'Winter study-first adapter mismatch'
   winter_art_assets.append(relative_asset)
  elif relative_asset in FOUR_SCENE_ANSWER_ART:
   record=FOUR_SCENE_ANSWER_ART[relative_asset]
   assert page.relative_to(ROOT).as_posix()==record['owner'] and container.attrs.get('data-exclusive-artwork')==record['key'], 'Modern exact owner/key mismatch'
   assert a.attrs.get('aria-haspopup')=='dialog' and 'data-full-image-viewer' not in a.attrs and a.attrs.get('data-topic-study')==record['destination'], 'Modern study-first adapter mismatch'
   four_scene_answer_assets.append(relative_asset)
  elif relative_asset in first_topic_review:
   record=first_topic_review[relative_asset]
   assert page.relative_to(ROOT).as_posix()==record['route'], 'FIRST topic owner mismatch'
   first_topic_assets.append(relative_asset)
  elif relative_asset.startswith('assets/page-art/temples/'):
   assert relative_asset in temple_review and page.name=='why-latter-day-saints-build-temples.html', 'Temple artwork owner/review mismatch'
   key,record=temple_review[relative_asset]
   assert record['reviewed'] and hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['sha256'], 'Temple artwork changed after visual review'
   assert container.attrs.get('data-exclusive-artwork')==key and a.attrs.get('aria-haspopup')=='dialog', 'Temple picture adapter binding mismatch'
   temple_assets.append(relative_asset)
  elif relative_asset in covenant_review or (page.name=='abrahamic-covenant.html' and 'data-exclusive-artwork' in container.attrs):
   assert relative_asset in covenant_review, 'Covenant picture missing from its exact review manifest'
   key,record=covenant_review[relative_asset]
   assert '/'+page.relative_to(ROOT).as_posix()==record['owner']=='/answers/abrahamic-covenant.html', 'Covenant artwork on wrong page'
   assert record['review_status']=='pass' and record['owner_approved'] is False, 'Covenant technical review must remain separate from owner approval'
   assert record['independent_review']['review_status']=='pass' and record['independent_review']['sha256']==record['original_sha256'], 'Covenant independent original review mismatch'
   assert container.attrs.get('data-exclusive-artwork')==key, 'Covenant figure key differs from review'
   assert hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['asset_sha256'], 'Covenant artwork changed since review'
   images=[n for n in a.walk() if n.tag=='img']
   assert len(images)==1 and local_asset(page,images[0].attrs['src']).relative_to(ROOT).as_posix()==record['thumbnail'], 'Covenant thumbnail differs from review'
   assert hashlib.sha256((ROOT/record['thumbnail']).read_bytes()).hexdigest()==record['thumbnail_sha256'], 'Covenant thumbnail changed since review'
   assert a.attrs.get('aria-haspopup')=='dialog', 'Covenant picture must bind the shared study adapter'
   assert {s['url'] for s in record['sources']} <= {n.attrs.get('href') for n in sources}, 'Covenant exact picture sources missing'
   covenant_assets.append(relative_asset)
  elif relative_asset in hg_review or page.name=='holy-ghost.html':
   assert relative_asset in hg_review, 'Holy Ghost picture missing from exact review'
   key,record=hg_review[relative_asset]
   assert '/'+page.relative_to(ROOT).as_posix()==record['owner']=='/answers/holy-ghost.html'
   assert container.attrs.get('data-exclusive-artwork')==key and a.attrs.get('aria-haspopup')=='dialog'
   hg_assets.append(relative_asset)
  elif relative_asset in plan_review or page.name=='plan-of-salvation.html':
   assert relative_asset in plan_review, 'Plan picture missing from exact reviewed manifest'
   key,record=plan_review[relative_asset]
   assert '/'+page.relative_to(ROOT).as_posix()==record['owner']=='/answers/plan-of-salvation.html'
   assert container.attrs.get('data-exclusive-artwork')==key and a.attrs.get('aria-haspopup')=='dialog'
   assert hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['asset_sha256'], 'Plan picture changed after review'
   plan_assets.append(relative_asset)
  elif relative_asset in father_review or container.attrs.get('data-exclusive-artwork','').startswith('hf-'):
   assert relative_asset in father_review and page.relative_to(ROOT).as_posix()=='answers/god-our-heavenly-father.html', 'Father picture outside exact owner/review'
   assert container.attrs.get('data-exclusive-artwork')=='hf-'+father_review[relative_asset]['id'] and a.attrs.get('aria-haspopup')=='dialog', 'Father shared study adapter binding mismatch'
   father_assets.append(relative_asset)
  elif 'data-journey-art' in container.attrs:
   key=container.attrs['data-journey-art'];record=journey_review[key]
   assert record['owner']==page.relative_to(ROOT).as_posix(), 'Journey artwork ownership mismatch'
   assert record['reviewed'] and record['asset']==relative_asset, 'Journey artwork registry mismatch'
   validate_artwork_review(key,record,ROOT/'docs/jesus-journey')
   assert hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['asset_sha256'], 'Journey artwork changed since review'
   assert a.attrs.get('aria-haspopup')=='dialog', 'Journey picture must bind the shared study adapter'
   journey_assets.append(key)
  elif relative_asset in focused_review or (relative_asset.startswith('assets/page-art/church-history/') and Path(relative_asset).stem in relocated_names):
   if relative_asset in focused_review:
    record=focused_review[relative_asset]
    assert record['page']==page.relative_to(ROOT).as_posix(), 'Focused artwork ownership mismatch'
    assert record['reviewed'] and hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['sha256'], 'Focused artwork changed since review'
    focused_assets.append(relative_asset)
   else: relocated_assets.append(relative_asset)
   if 'data-full-image-viewer' in a.attrs or a.attrs.get('aria-haspopup')!='dialog': errors.append(page.name+': focused picture must open study details first')
  elif relative_asset in opening_review:
   record=opening_review[relative_asset]
   assert record['page']==page.relative_to(ROOT).as_posix()=='general-conference.html', 'Conference opening ownership mismatch'
   assert record['reviewed'] and hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['sha256'], 'Conference opening changed since review'
   if 'data-full-image-viewer' in a.attrs or a.attrs.get('aria-haspopup')!='dialog': errors.append(page.name+': opening picture must show study details first')
   assert a.attrs.get('data-topic-study')=='general-conference.html#conference-messages', 'Conference opening study target changed'
   opening_assets.append(relative_asset)
  elif relative_asset in settle_review:
   record=settle_review[relative_asset]
   assert page.relative_to(ROOT).as_posix()==settle_manifest['page'], 'Settled faith artwork ownership mismatch'
   assert record['reviewed'] and record['technical_review_passed'] and hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['sha256'], 'Settled faith artwork changed since review'
   assert container.attrs.get('data-topic-art')=='settle-'+record['key'], 'Settled faith adapter key mismatch'
   assert a.attrs.get('aria-haspopup')=='dialog' and 'data-full-image-viewer' not in a.attrs, 'Settled faith picture must open study first'
   assert any(n.attrs.get('href')==record['source_url'] for n in sources), 'Settled faith exact scripture missing'
   settle_assets.append(relative_asset)
  elif relative_asset in bible_review or 'data-bible-original' in container.attrs:
   assert relative_asset in bible_review, 'Bible together picture is missing from its review manifest'
   record=bible_review[relative_asset]
   assert page.relative_to(ROOT).as_posix()==bible_manifest['page'], 'Bible together artwork ownership mismatch'
   assert record.get('reviewed') is True and record.get('technical_review_passed') is True, 'Bible together artwork lacks technical review'
   assert hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record['sha256'], 'Bible together artwork changed since review'
   assert container.attrs.get('data-bible-original')==record['key'], 'Bible together figure key differs from review'
   assert a.attrs.get('aria-haspopup')=='dialog' and 'data-full-image-viewer' not in a.attrs, 'Bible together picture must open study first'
   assert any(n.attrs.get('href')==record['source_url'] for n in sources), 'Bible together exact scripture missing'
   bible_assets.append(relative_asset)
  elif relative_asset in bom_review:
   record=bom_review[relative_asset]
   assert page.relative_to(ROOT).as_posix()==bom_manifest['page'], 'Book of Mormon artwork is on the wrong page'
   assert record.get('reviewed') is True and hashlib.sha256((ROOT/relative_asset).read_bytes()).hexdigest()==record.get('sha256'), 'Book of Mormon artwork changed since review'
   assert container.attrs.get('data-bom-story-art')==record['key'], 'Book of Mormon figure key differs from review'
   # Like the preserved topic pictures, this page retains a native fallback marker.
   # The required shared adapter removes it and installs the study action first.
   if a.attrs.get('aria-haspopup')!='dialog' or container.attrs.get('data-topic-art')!='bom-'+record['key']:errors.append(page.name+': Book of Mormon picture must bind the shared study adapter')
   bom_assets.append(relative_asset)
  elif relative_asset in new_review:
   record=new_review[relative_asset]
   if record['page']!=page.relative_to(ROOT).as_posix():errors.append(page.name+': sitewide artwork is on the wrong page')
   if 'data-full-image-viewer' in a.attrs or a.attrs.get('aria-haspopup')!='dialog':errors.append(page.name+': sitewide picture must open study details first')
   sitewide_assets.append(relative_asset)
  elif 'data-life-after-death-art' in container.attrs or 'data-study-gap-art' in container.attrs:
   # The anchor href is the native fallback. New figures intentionally let the
   # study adapter install the first action rather than the bare-image viewer.
   if 'data-full-image-viewer' in a.attrs:errors.append(page.name+': new picture must open study options first')
   if a.attrs.get('aria-haspopup')!='dialog':errors.append(page.name+': new picture dialog semantics missing')
   (life_assets if 'data-life-after-death-art' in container.attrs else gap_assets).append(relative_asset)
  elif relative_asset in joseph_review:
   assert page.relative_to(ROOT).as_posix()=='answers/who-was-joseph-smith.html', 'Joseph family artwork ownership mismatch'
   assert a.attrs.get('aria-haspopup')=='dialog' and a.attrs.get('data-topic-study'), 'Joseph family contextual study adapter missing'
   joseph_assets.append(relative_asset)
  elif 'data-full-image-viewer' not in a.attrs:errors.append(page.name+': native image fallback missing')
  if not local_asset(page,a.attrs['href']).is_file():errors.append(page.name+': full image missing')
life_review=json.loads((ROOT/'docs/life-after-death-art-review.json').read_text(encoding='utf-8'))['artworks']
reviewed_life_assets={entry['asset'] for entry in life_review}
assert len(life_assets)==18 and len(set(life_assets))==18 and set(life_assets)==reviewed_life_assets,'Life After Death adapter inventory differs from reviewed art'
gap_review=json.loads((ROOT/'docs/study-gap-art-review.json').read_text(encoding='utf-8'))['artworks']
assert len(gap_assets)==4 and len(set(gap_assets))==4 and set(gap_assets)=={entry['asset'] for entry in gap_review},'Study-gap adapter inventory differs from reviewed art'
assert len(sitewide_assets)==len(new_review) and set(sitewide_assets)==set(new_review),'Sitewide adapter inventory differs from exact reviewed additions'
assert len(bom_assets)==len(bom_review) and set(bom_assets)==set(bom_review), 'Book of Mormon adapter inventory differs from exact reviewed additions'
assert len(opening_assets)==1 and set(opening_assets)==set(opening_review), 'Conference opening must replace its existing slot exactly once'
# The opening replaces an existing picture and remains within the 99-picture baseline.
assert len(focused_assets)==4 and set(focused_assets)==set(focused_review), 'Focused body artwork inventory mismatch'
assert len(relocated_assets)==6 and {Path(a).stem for a in relocated_assets}==relocated_names, 'Preserved historical artwork inventory mismatch'
assert len(settle_assets)==14 and set(settle_assets)==set(settle_review), 'Settled faith exact body inventory mismatch'
assert len(bible_assets)==13 and len(set(bible_assets))==13 and set(bible_assets)==set(bible_review), 'Bible together exact body inventory mismatch'
assert len(covenant_assets)==len(set(covenant_assets))==12 and set(covenant_assets)==set(covenant_review), 'Covenant exact body inventory mismatch'
expected_journey={k for k,v in journey_review.items() if v['owner'].startswith('answers/')}
assert len(journey_assets)==len(set(journey_assets)) and set(journey_assets)==expected_journey, 'Journey parent exact artwork inventory mismatch'
assert len(hg_assets)==len(set(hg_assets))==16 and set(hg_assets)==set(hg_review), 'Holy Ghost exact body inventory mismatch'
assert len(temple_assets)==len(set(temple_assets))==len(temple_review)==21 and set(temple_assets)==set(temple_review), 'Twenty chapter pictures and the owner-requested Nephi companion must reach the shared study adapter'
assert len(joseph_assets)==len(set(joseph_assets))==26 and set(joseph_assets)==joseph_review, 'All reviewed Joseph family pictures must reach study details exactly once'
assert len(first_topic_assets)==len(set(first_topic_assets))==len(first_topic_review) and set(first_topic_assets)==set(first_topic_review), 'Exact additive FIRST topic family required'
assert len(reading_art_assets)==len(set(reading_art_assets))==3 and set(reading_art_assets)==set(REVIEWED_READING_ART), 'Exact Stand two and Temple one inventory required'
assert winter_art_assets==[WINTER_FULL], 'Exactly one reviewed Winter Answer picture required'
print('PASS: exact Winter owner, figure, four rasters and study-first adapter;8 negative mutations; unchanged legacy99/3 baseline')
assert len(four_scene_answer_assets)==3 and set(four_scene_answer_assets)==set(FOUR_SCENE_ANSWER_ART), 'Exactly three modern Answer pictures required'
print('PASS: three exact modern Answer figures, twelve rasters and24 negative mutations; unchanged historical99/3 baseline')
assert (count-len(four_scene_answer_assets)-len(winter_art_assets)-len(reading_art_assets)-len(first_topic_assets)-len(joseph_assets)-len(temple_assets)-len(father_assets)-len(plan_assets)-len(hg_assets)-len(covenant_assets)-len(journey_assets)-len(bible_assets)-len(settle_assets)-len(life_assets)-len(gap_assets)-len(sitewide_assets)-len(focused_assets)-len(relocated_assets)-len(bom_assets),preserved)==(99,3),(count,preserved)
# Life After Death lifted its old illustrated feature panel into full reading
# sections. All twelve remaining panels still undergo the structural checks.
assert set(plan_assets)==set(plan_review) and len(plan_assets)==16, 'All sixteen Plan originals must reach the shared study adapter'
assert len(father_assets)==len(set(father_assets))==5 and set(father_assets)==set(father_review), 'All five Father originals must reach the shared adapter exactly once'
assert panels==12,panels
stand=Document();stand.feed((ROOT/'answers/stand-forever.html').read_text(encoding='utf-8'));stand_nodes=list(stand.root.walk())
foundation_images=[n for n in stand_nodes if n.tag=='a' and n.has('fc-foundation-card__image')]
assert len(foundation_images)==4,len(foundation_images)
for image in foundation_images:
 study=image.attrs.get('data-topic-study','');assert study and (ROOT/'answers'/study).is_file(),study
 card=next(n for n in parents(image) if n.has('fc-foundation-card'))
 direct=next((n for n in card.walk() if n.tag=='a' and n.has('fc-foundation-card-action')),None)
 assert direct is not None and direct.attrs.get('href')==study,(study,direct.attrs.get('href') if direct else None)
 assert 'data-full-image-viewer' in image.attrs and 'data-full-image-alt' in image.attrs
adapter=(ROOT/'topic-artwork-details.js').read_text(encoding='utf-8')
assert "if (!record.study) {" in adapter,'Foundation cards must not inherit unrelated section sources'
assert "if (record.study) pill(record.studyLabel, record.study, true);" in adapter,'Foundation topic action missing from detail panel'
if errors:raise SystemExit('\n'.join(errors))
print(f'TOPIC ARTWORK DETAILS QA PASS: {count} adapter pictures including {len(first_topic_assets)} strictly validated FIRST additions, {preserved} existing detail pictures, {panels} expanded illustration panels, {len(list((ROOT/'answers').glob('*.html')))+1} page dependencies')
