"""Protect centerpiece coverage, unique reviewed pictures and study interactions."""
import hashlib,json
from pathlib import Path
from urllib.parse import urlsplit
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
page=ROOT/'atonement.html';text=page.read_text(encoding='utf-8');d=Document();d.feed(text);nodes=list(d.root.walk())
def require(condition,message):
    if not condition: raise AssertionError(message)
required={'before-the-world','need-a-savior','promise','sacrifice','resurrection','book-of-mormon','living-voice','repentance','grace','healing','remember','continue-study','main-content'}
ids=[n.attrs['id'] for n in nodes if n.attrs.get('id')]
require(required<=set(ids),'Every connected chapter and onward destination must exist')
require(len(ids)==len(set(ids)),'IDs must be unique')
figures=[n for n in nodes if n.tag=='figure' and 'data-enriched-study-art' in n.attrs]
require(len(figures)>=25,'Centerpiece requires at least25 reviewed supporting pictures plus hero')
records={r['asset']:r for r in json.loads((ROOT/'docs/art-study-image-review.json').read_text())['pages']['atonement.html']}
heroes=[n for n in nodes if n.tag=='a' and n.attrs.get('data-hero-record')=='atonement']
require(len(heroes)==1,'One dedicated Atonement hero is required')
hero_asset=heroes[0].attrs['href']
require(hero_asset in records and records[hero_asset]['reviewed'] and records[hero_asset]['sha256']==hashlib.sha256((ROOT/hero_asset).read_bytes()).hexdigest(),'Hero must match its reviewed bytes')
assets=[];hashes=[]
for fig in figures:
    a=next(n for n in fig.walk() if n.tag=='a');asset=a.attrs['href'];assets.append(asset)
    digest=hashlib.sha256((ROOT/asset).read_bytes()).hexdigest();hashes.append(digest)
    require(asset in records and records[asset]['reviewed'] and records[asset]['sha256']==digest,'Artwork must match the reviewed bytes: '+asset)
    require(a.attrs.get('aria-haspopup')=='dialog' and 'data-full-image-viewer' not in a.attrs,'Supporting art must open study panel first')
    require(a.attrs.get('data-topic-study','').startswith('atonement.html#'),'Artwork must return to its own study')
    require(any(n.tag=='a' and '/study/scriptures/' in n.attrs.get('href','') for n in fig.walk()),'Every picture needs its own scripture')
require(len(set(assets))==len(assets) and len(set(hashes))==len(hashes),'Responsive aliases must not inflate artwork count')
for other in ROOT.rglob('*.html'):
    if other==page or '.git' in other.parts:continue
    require(not any(asset in other.read_text(encoding='utf-8') for asset in assets),'Supporting art must be page-exclusive')
for canon in ['pgp','ot','nt','bofm','dc-testament']:
    require('/study/scriptures/'+canon+'/' in text,'Missing standard-work witness: '+canon)
for passage in ['pgp/a-of-f/1','dc-testament/dc/138','bofm/moro/4','bofm/moro/5','nt/john/19','nt/john/20']:
    require(passage in text,'Missing essential source: '+passage)
require('Eternal life with God is a distinct gift' in text,'Resurrection must not be conflated with eternal life')
require('it is not your fault' in text and 'professional help' in text,'Healing guidance must retain safety and support')
require(sum(n.tag=='details' for n in nodes)>=8,'Guided reflection must remain substantive')
require(sum(n.tag=='article' and 'data-resource-key' in n.attrs for n in nodes)>=11,'Official visual resource coverage reduced')
for dependency in ['topic-artwork-details.js','hero-details.js','site-search.js']:
    require(text.count('src="'+dependency)==1,'Missing or duplicate shared interaction: '+dependency)
for forbidden in ['cross-v4','cross-v6','cross-v8','cross-v9','cross-v10','-original.png','<base','Local editorial review']:
    require(forbidden not in text,'Rejected/preview artifact in published page: '+forbidden)
require('href="atonement.html"' in (ROOT/'answers.html').read_text(encoding='utf-8'),'Topic discovery missing')
require('<div class="atonement-reading"><p></p></div>' not in text,'Empty reading blocks create artificial gaps')
for n in nodes:
    if n.has('fc-actions'):require(n.has('atonement-chapter-actions'),'Study actions must share centered spacing')
print('ATONEMENT QA PASS: chapters,26distinct reviewed visuals,all standard works,reflection,safety and shared study hooks')
