"""Bounded current Timeline index semantics; generator --check remains separate."""
import json
from pathlib import Path
from timeline_selector_semantics import validate, DESCRIPTIONS
from timeline_selector_check import DESTINATIONS
ROOT=Path(__file__).resolve().parents[1]
def validate_current(root=ROOT):
 root=Path(root)
 validate((root/'timeline.html').read_bytes())
 search=json.loads((root/'site-search-index.json').read_bytes());gallery=json.loads((root/'art-gallery.json').read_bytes())
 assert search.get('version')==1 and isinstance(search.get('pages'),list) and isinstance(search.get('records'),list)
 assert gallery.get('version')==1 and isinstance(gallery.get('pages'),list) and isinstance(gallery.get('artworks'),list)
 urls=[r['url'] for r in search['records']];assert len(urls)==len(set(urls)),'Duplicate search destinations'
 assert '/timeline.html' in search['pages'] and '/timeline.html' in gallery['pages']
 records={r['url']:r for r in search['records']}
 for name in ('/timeline.html','/timeline.html#choose-timeline','/timeline.html#adams-1881'):assert name in records,'Missing Timeline search destination'
 choice=records['/timeline.html#choose-timeline']['text']
 for (name,_,_),description in zip(DESTINATIONS,DESCRIPTIONS):assert name in choice and description in choice,'Stale Timeline search text'
 assert records['/timeline.html#adams-1881']['title']=="Adams' 1881 Chart of History"
 return {'status':'CURRENT_TIMELINE_INDEX_SEMANTICS_PASS','files':['art-gallery.json','site-search-index.json','timeline.html'],'limits':'Selected Timeline semantics only; source-to-index equivalence is independently checked by the configured generators.'}
