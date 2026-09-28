"""Exact CFM composition review; immutable hero, sources, images and weekly controller."""
from pathlib import Path
import hashlib,json,sys
from collections import Counter
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=json.loads((ROOT/'docs/cfm-composition.json').read_text(encoding='utf-8'))
def digest(v):return hashlib.sha256(v if isinstance(v,bytes) else v.encode()).hexdigest()
def check(html=None,css=None,controls=None):
 html=(ROOT/'come-follow-me.html').read_text(encoding='utf-8') if html is None else html
 css=(ROOT/'come-follow-me.css').read_text(encoding='utf-8') if css is None else css
 controls=(ROOT/'cfm-study-controls.css').read_text(encoding='utf-8') if controls is None else controls
 assert digest(css)==CONTRACT['css_sha256']['come-follow-me.css'],'Unreviewed composition CSS'
 assert digest(controls)==CONTRACT['css_sha256']['cfm-study-controls.css'],'Unreviewed controls CSS'
 assert digest(css.split('/* One page composition',1)[0])==CONTRACT['hero_css_sha256'],'Hero rules changed'
 s=BeautifulSoup(html,'html.parser');assert str(s.select_one('header.cfm-hero'))==CONTRACT['hero_html'],'Hero markup changed'
 assert str(s.select_one('nav.nav'))==CONTRACT['nav_html'],'Header navigation changed'
 assert sorted(json.dumps(dict(x.attrs),sort_keys=True) for x in s.select('img'))==CONTRACT['images'],'Image identity/count/attributes changed'
 expected=Counter(CONTRACT['hrefs']);expected[CONTRACT['removed_duplicate_href']]-=1
 assert Counter(x['href'] for x in s.select('a[href]'))==+expected,'Destination changed beyond approved duplicate removal'
 expected_text=Counter(CONTRACT['prior_main_text']);expected_text.subtract(CONTRACT['removed_text']);expected_text.update(CONTRACT['added_text'])
 assert Counter(t.strip() for t in s.select_one('main').stripped_strings)==+expected_text,'Study prose changed beyond approved labels'
 assert sorted(n['id'] for n in s.select('[id]'))==CONTRACT['prior_ids'],'Study target changed'
 assert sorted([n.name,k,str(v)] for n in s.select('*') for k,v in n.attrs.items() if k.startswith('data-cfm-') or k=='data-week-move')==CONTRACT['prior_hooks'],'Weekly hook changed'
 assert digest((ROOT/'come-follow-me.js').read_bytes())==CONTRACT['script_sha256'],'Weekly controller changed'
 assert len(s.select('.cfm-signature'))==1 and len(s.select('.cfm-library>.cfm-library-card'))==8,'One moved preview and eight library cards required'
 assert s.select_one('.cfm-week__grid>.cfm-signature'),'Signature belongs beside weekly introduction'
 assert s.select_one('.cfm-week__intro .cfm-week-reading') and not s.select('.cfm-reading--assignment'),'Unboxed weekly reading required'
 assert s.select_one('.cfm-resources #official-toolkit') and len(s.select('.cfm-resources .cfm-tool'))==4,'Four resources in own section'
 assert len(s.select('.cfm-focus li'))==3 and len(s.select('[data-guided-reflection]'))==3,'All study invitations retained'
 figure=s.select_one('figure.cfm-reflection-picture.fc-study-visual--panel[data-linked-picture-reference=modern-prayer]');assert figure and figure.select_one('figcaption .fc-study-visual-sources') and figure.select_one('figcaption .fc-actions'),'Prayer preview needs one semantic framed study card'
 assert 'flex-wrap:nowrap' in css and 'flex:0 1 auto;min-width:0;width:100%' in css,'Study captions need intrinsic column layout'
 assert 'font:400 clamp(1.8rem' in css and '.cfm-library{display:grid;grid-template-columns:repeat(4' in css,'Shared typography and complete rows required'
 return True
def self_test():
 h=(ROOT/'come-follow-me.html').read_text(encoding='utf-8');c=(ROOT/'come-follow-me.css').read_text(encoding='utf-8');k=(ROOT/'cfm-study-controls.css').read_text(encoding='utf-8');check(h,c,k)
 mutations=[(h,c+'body{display:none}',k),(h,c.replace('flex-wrap:nowrap','flex-wrap:wrap'),k),(h,c.replace('height:auto','height:99px',1),k),(h,c,k.replace('border-radius:999px','border-radius:2px')),(h.replace('cfm-signature','removed-signature'),c,k),(h.replace('id="official-toolkit"','id="missing-toolkit"'),c,k),(h.replace('cfm-reflection-picture','missing-reflection'),c,k),(h.replace('personal-study-2026.webp','wrong.webp'),c,k),(h.replace('why-families-are-important.html','what-is-eternal-marriage.html'),c,k)]
 mutations.extend([(h.replace('data-cfm-current-title','data-cfm-missing-title'),c,k),(h.replace('id="guided-reflections"','id="lost-reflections"'),c,k),(h.replace('A man pauses to pray before the day begins.',''),c,k)])
 mutations.append((h.replace('data-week-move="-1"','data-week-move="1"'),c,k))
 for args in mutations:
  try:check(*args)
  except AssertionError:pass
  else:raise AssertionError('Composition mutation escaped')
 print('CFM composition self-test PASS:13 image/layout/source/prose/hook/target rejection fixtures')
if __name__=='__main__':
 check()
 if '--self-test' in sys.argv:self_test()
 print('CFM composition PASS: exact hero/nav/19images/destinations/controller; one moved preview,8library,4resources,3reflections')
