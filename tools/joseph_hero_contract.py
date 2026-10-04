"""Exact two Joseph hero contracts; pixel and rendering approval remain separate."""
import hashlib,json
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from bs4 import BeautifulSoup
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
HEROES={
 'joseph-smith-likeness.html':('joseph-gateway-20261004','064817c39cdd0b59782a2b5d70d2250798c786a08022115534f9fabb62b7b059'),
 'joseph-smith-portrait-research.html':('joseph-research-20261004','a0843f406e0b8d991739d8e3a80922bcdd42042a352642f24729dc55aa52573a'),
}
def check_hero(route,doc=None):
 doc=doc or BeautifulSoup((ROOT/route).read_text(encoding='utf-8'),'html.parser')
 key,digest=HEROES[route];asset='assets/heroes/'+key+'.png'
 heroes=doc.select('.fc-visual-hero');assert len(heroes)==1,route+': exactly one hero required'
 hero=heroes[0];assert hero.name=='a' and hero.has_attr('data-hero-viewer') and hero.get('aria-haspopup')=='dialog',route+': native hero detail action required'
 assert hero.get('data-hero-record')==key and hero.get('href')==asset,route+': exact distinct owner asset/record required'
 assert not hero.has_attr('data-full-image-viewer'),route+': study must precede full-size'
 assert hero.find_parent('main') is None,route+': hero shell must not duplicate body artwork'
 assert hero.get('data-exclusive-artwork')==key and hero.get('data-full-image-alt'),route+': ownership/accessibility required'
 ask=parse_qs(urlsplit(hero.get('data-hero-ask','')).query);assert ask.get('topic') and ask.get('return')==['/'+route+'?hero=1'],route+': contextual Ask return required'
 assert hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()==digest,route+': reviewed original changed'
 imgs=hero.select('img');assert len(imgs)==1
 img=imgs[0];assert img.get('alt') and img.get('data-source-original')==asset and img.get('fetchpriority')=='high'
 assert (int(img['width']),int(img['height']))==(2170,725),route+': original proportions changed'
 assert img.get('srcset') and img.get('sizes')=='(max-width: 700px) 900px, 100vw',route+': proportional responsive delivery required'
 for variant in img['srcset'].split(','):
  src,width=variant.strip().split();width=int(width.rstrip('w'))
  with Image.open(ROOT/src) as image:assert image.width==width and abs(image.width/image.height-2170/725)<.01
 assert len(doc.select('[data-exclusive-artwork="'+key+'"]'))==1,route+': duplicated owning hero'
 return True

def check_grouping(doc):
 for suffix,title,art in [('2','A profile sitting in Nauvoo','profile-sitting-1842-retry'),('3','A face painted from life','painted-likeness-1842')]:
  block=doc.find(id='research-block-section-4-'+suffix)
  assert block and 'research-reading-block--cohesive' in block.get('class',[]),'Distinct cohesive sitting unit required'
  heading=block.find('h3',recursive=False);assert heading and heading.get_text(strip=True)==title
  figures=block.find_all('figure',recursive=False);assert len(figures)==1 and figures[0].get('data-research-art')==art,'Sitting heading must own its corresponding primary image'
  copy=block.select_one('.research-reading-copy');assert copy and copy.select_one('p') and copy.select_one('a[href^="#portrait-source-"]')
  assert figures[0].find_previous_sibling()==heading and copy.find_previous_sibling()==figures[0],'Heading/image/caption/history must remain one direct ordered unit'
 assert len(doc.select('#portrait-research figure'))==81,'Body figure corpus must remain81'
