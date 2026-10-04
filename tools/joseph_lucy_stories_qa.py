"""Protect all ten Lucy stories, exact reviewed pixels, and unique biography ownership."""
import hashlib,json,sys
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(allow_partial=False):
 data=json.loads((ROOT/'docs/joseph-lucy-family-stories.json').read_text(encoding='utf-8'))
 art=json.loads((ROOT/'docs/joseph-lucy-art-review.json').read_text(encoding='utf-8'))
 assert len(data['stories'])==10 and len({s['id'] for s in data['stories']})==10
 assert art['required_story_ids']==[s['id'] for s in data['stories']]
 accepted=[s for s in data['stories'] if s.get('image_status')=='accepted']
 if not allow_partial:assert len(accepted)==10,'Release requires all ten illustrated Lucy stories; '+str(len(accepted))+' are ready'
 page=BeautifulSoup((ROOT/art['owning_page']).read_text(encoding='utf-8'),'html.parser')
 assert len(page.select('#lucy-family-stories article'))==len(accepted)
 for s in data['stories']:
  node=page.find(id=s['id'])
  if s not in accepted:assert node is None,'No unfinished public story slots';continue
  record=next(x for x in art['items'] if x['id']==s['id']);asset=ROOT/record['asset']
  assert digest(asset)==record['sha256'] and Image.open(asset).size==(record['width'],record['height'])
  assert {r['reviewer'] for r in record['reviews']}=={'fermi','newton'}
  for r in record['reviews']:
   receipt=ROOT/r['receipt'];assert digest(receipt)==r['sha256'];review=next(x for x in json.loads(receipt.read_text(encoding='utf-8')) if x['id']==s['id']);assert review['concur'] and review['sha256']==record['sha256']
  assert node and node.find('h3').get_text()==s['heading']
  for text in s['paragraphs']+[s['visitor_caption']]:assert text in node.get_text()
  for source in s['sources']:assert node.select_one('a[href="'+source['url']+'"]')
  assert node.select_one('a[href="../'+record['asset']+'"]')
  image=node.find('img');assert image['width']==str(record['width']) and image['height']==str(record['height'])
  delivery=record['delivery']
  assert delivery['default'] in {v['asset'] for v in delivery['variants']},'Default derivative is hash-verified'
  assert s['delivery']==delivery,'Visitor delivery metadata matches reviewed manifest'
  assert image.get('src')=='../'+delivery['default'],'Displayed default is the reviewed derivative'
  expected_srcset=', '.join('../'+v['asset']+' '+str(v['width'])+'w' for v in delivery['variants'])
  assert image.get('srcset')==expected_srcset,'Every responsive candidate is reviewed and correctly sized'
  assert image.get('data-source-original')=='../'+record['asset'],'Original-pixel provenance remains explicit'
  for variant in delivery['variants']:
   p=ROOT/variant['asset'];assert digest(p)==variant['sha256'];assert Image.open(p).size==(variant['width'],variant['height']);assert abs(variant['width']/variant['height']-record['width']/record['height'])<.003
  assert len(page.select('[data-exclusive-artwork="'+s['id']+'"]'))==1
  assets={record['asset'],*(v['asset'] for v in delivery['variants'])}
  for other in ROOT.rglob('*.html'):
   relative=other.relative_to(ROOT)
   if relative.as_posix()==art['owning_page'] or any(part in {'docs','tools','work','node_modules','.git'} for part in relative.parts):continue
   other_page=BeautifulSoup(other.read_text(encoding='utf-8'),'html.parser')
   for img in other_page.select('img'):
    references=' '.join(str(img.get(attr,'')) for attr in ['src','srcset','data-source-original'])
    assert not any(asset in references for asset in assets),'Story artwork duplicated on '+relative.as_posix()

 print('LUCY STORY QA PASS:',len(accepted),'of 10 complete; '+('integration-only, release blocked until ten' if allow_partial else 'all ten required stories illustrated'))
if __name__=='__main__':check('--allow-partial' in sys.argv)
