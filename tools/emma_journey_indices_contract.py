"""Current Emma index delta: run on independently validated, full-tree outputs.

This checks source-oriented public indexing, not source review, asset provenance,
rendering, owner acceptance, or release. Prior generated-index evidence is not
rewritten or used as a current index. It MUST be called with real full-tree
baseline and fresh producer outputs from the reviewed exact candidate.
"""
from urllib.parse import urlsplit
HUB='/history/emma-hale-smith.html';OLD='/history/emma-elect-lady.html';HYMN='/history/emma-hymns.html'
NEW=['emma-journey-origin']+['emma-journey-%02d'%i for i in range(3,13)]
RETAINED=['emma-h1','emma-h3','emma-h4','emma-h5']+['emma-story1-ride','emma-story2-hymnal','emma-story3-quincy','emma-story4-hospitality','emma-story5-testimony']
REMOVED=['emma-c1','emma-c3','emma-c4','emma-c5']
SECTIONS=['heading-emma-beginnings','heading-emma-pen-family','heading-emma-songs-separation','heading-emma-relief-questions','heading-emma-household','heading-emma-remaining-years']
def req(v,m):
 if not v:raise AssertionError(m)
def items(g):
 a=g.get('artworks');req(isinstance(a,list),'gallery artworks absent');ids=[x.get('id') for x in a];req(len(ids)==len(set(ids)),'duplicate gallery IDs');return a
def exact_urls(search):
 rows=search.get('records');req(isinstance(rows,list),'search records absent');urls=[x.get('url') for x in rows];req(len(urls)==len(set(urls)),'duplicate search destinations');return {x['url']:x for x in rows}
def check(before,after):
 """Inputs contain gallery, search, and panel JSON, not paths or fake output."""
 oldg,newg=before['gallery'],after['gallery'];olds,news=before['search'],after['search'];oldp,newp=before['panel'],after['panel']
 for label,prev,curr in [('gallery',oldg['pages'],newg['pages']),('search',olds['pages'],news['pages'])]:
  req(len(prev)==len(set(prev)) and len(curr)==len(set(curr)),label+' duplicate pages')
  req(set(curr)==set(prev)-{OLD},label+' unrelated canonical page drift')
  req(HUB in curr and OLD not in curr,label+' route retirement')
 op=oldp['canonical_pages'];np=newp['canonical_pages'];req(len(op)==len(set(op)) and len(np)==len(set(np)),'duplicate panel canonical routes')
 prev=set(op);curr=set(np);req(curr==prev-{'history/emma-elect-lady.html'},'panel canonical routes drift')
 rr=newp.get('candidate_classes',{}).get('fc-life-scripture-reflection',{})
 req(not rr or rr.get('count',0)==0,'retired reflection class returned')
 arts=items(newg);expected_ids=[]
 for key in NEW:
  full='/assets/page-art/emma-journey/'+key+'-1536.webp';thumb='/assets/page-art/emma-journey/'+key+'-960.webp'
  matches=[x for x in arts if x.get('fullImage')==full];req(len(matches)==1,key+' artwork missing or duplicate')
  x=matches[0];req(x.get('thumbnail')==thumb,key+' thumbnail changed');occ=x.get('occurrences',[])
  req(len(occ)==1 and occ[0].get('page')==HUB,key+' not exclusively owned by hub');expected_ids.append(x['id'])
 for key in RETAINED:
  full='/assets/page-art/emma-life/'+key+'-review-1536.webp';matches=[x for x in arts if x.get('fullImage')==full];prior=[x for x in items(oldg) if x.get('fullImage')==full]
  req(len(matches)==len(prior)==1,key+' retained gallery artwork missing or duplicate')
  prior_hub=[o for o in prior[0].get('occurrences',[]) if o.get('page')==HUB];current_hub=[o for o in matches[0].get('occurrences',[]) if o.get('page')==HUB]
  req(len(prior_hub)==len(current_hub)==1 and prior_hub==current_hub,key+' retained gallery hub occurrence changed')
  req({k:v for k,v in prior[0].items() if k!='occurrences'}=={k:v for k,v in matches[0].items() if k!='occurrences'},key+' retained gallery metadata changed')
 for key in REMOVED:
  needle='/assets/page-art/emma-life/'+key+'-review-1536.webp'
  req(not any(x.get('fullImage')==needle and any(o.get('page')==HUB for o in x.get('occurrences',[])) for x in arts),key+' removed pairing returned')
 for x in arts:
  req(not any(o.get('page')==OLD for o in x.get('occurrences',[])),'retired route still gallery owner')
 # Every unaffected gallery occurrence remains byte-for-byte equal, and no
 # unrelated new occurrence is silently introduced. Art metadata can change
 # for an Emma-owned shared artwork, so compare occurrences independently.
 def unaffected_occurrences(g):
  return sorted((x['id'],str(sorted(o.items()))) for x in items(g) for o in x.get('occurrences',[]) if o.get('page') not in {HUB,OLD,HYMN})
 req(unaffected_occurrences(oldg)==unaffected_occurrences(newg),'unrelated gallery occurrence drift')
 # For artworks wholly outside the changed pages, preserve every metadata field
 # as well as occurrence membership; altered thumbnails/titles cannot slip by.
 def untouched_artworks(g):
  return {x['id']:x for x in items(g) if all(o.get('page') not in {HUB,OLD,HYMN} for o in x.get('occurrences',[]))}
 req(untouched_artworks(oldg)==untouched_artworks(newg),'unrelated gallery artwork metadata drift')
 # The inventory aggregates counts, but it also carries exact page membership.
 # Preserve unrelated owners for every known classification and selector.
 changed_pages={HUB.lstrip('/'),OLD.lstrip('/'),HYMN.lstrip('/')}
 for family in ('candidate_classes','styled_surface_candidates','surface_selectors'):
  oldrows=oldp.get(family,{});newrows=newp.get(family,{})
  for key in set(oldrows)|set(newrows):
   old_pages=set(oldrows.get(key,{}).get('pages',[]))-changed_pages
   new_pages=set(newrows.get(key,{}).get('pages',[]))-changed_pages
   req(old_pages==new_pages,'unrelated panel membership drift: '+family+' '+key)
 before_rows=exact_urls(olds);after_rows=exact_urls(news)
 req(HUB in after_rows and not any(urlsplit(url).path==OLD for url in after_rows),'search canonical route retirement')
 for s in SECTIONS:req(HUB+'#'+s in after_rows,'missing story destination '+s)
 for key in expected_ids:req('/art-gallery.html?picture='+key in after_rows,'new artwork absent from search')
 all_gallery_ids={x['id'] for x in arts}
 for key in all_gallery_ids:req('/art-gallery.html?picture='+key in after_rows,'gallery artwork absent from search')
 actual_art_keys={u.split('?picture=',1)[1] for u in after_rows if u.startswith('/art-gallery.html?picture=')}
 req(actual_art_keys==all_gallery_ids,'extra or missing indexed gallery picture')
 unaffected_ids={x['id'] for x in items(oldg) if any(o.get('page') not in {HUB,OLD,HYMN} for o in x.get('occurrences',[]))}
 for key in unaffected_ids:
  url='/art-gallery.html?picture='+key
  req(url in before_rows and before_rows[url]==after_rows.get(url),'unrelated gallery search record drift')
 def untouched(rows):
  return {url:record for url,record in rows.items() if urlsplit(url).path not in {HUB,OLD,HYMN,'/art-gallery.html'}}
 req(untouched(before_rows)==untouched(after_rows),'unrelated search record drift')
 return {'new_emma_images':10,'additional_person_free_origins':1,'retained_emma_images':9,'limits':'Index semantics only; no owner, image, interaction, or rendered approval.'}

# The baseline data must be explicitly materialized from the pinned git commit,
# not from a stale local build. Git blob IDs verify its exact bytes. The current
# data must be the exact fresh full-checkout producer outputs; read/owner review
# and release acceptance remain separate.
BASE_BLOBS={'art-gallery.json':'d7a9e628341f264d86227ac729d8db7ab8ef4584',
            'site-search-index.json':'cba61442fcbed4fd1e62d61b0d90134d8237d086',
            'docs/section-panel-inventory.json':'5a2db892aaad7e51e545e92604a8cd80b9becdc4'}
def git_blob(raw):
 import hashlib
 return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def validate_full_tree(root,baseline):
 import json
 from pathlib import Path
 import build_art_gallery,build_site_search,section_panel_surface_qa
 root=Path(root).resolve();baseline=Path(baseline).resolve()
 req(root==build_art_gallery.ROOT.resolve()==build_site_search.ROOT.resolve()==section_panel_surface_qa.ROOT.resolve(),'producer root mismatch')
 def read_verified(path):
  raw=(baseline/path).read_bytes();req(git_blob(raw)==BASE_BLOBS[path],'baseline blob drift: '+path);return json.loads(raw)
 before={'gallery':read_verified('art-gallery.json'),'search':read_verified('site-search-index.json'),'panel':read_verified('docs/section-panel-inventory.json')}
 after={'gallery':json.loads((root/'art-gallery.json').read_bytes()),'search':json.loads((root/'site-search-index.json').read_bytes()),'panel':json.loads((root/'docs/section-panel-inventory.json').read_bytes())}
 # Do not bless hand-edited generated output or stale gallery inputs.
 req(build_art_gallery.build()==after['gallery'],'gallery differs from full-tree producer')
 req(build_site_search.build()==after['search'],'search differs from full-tree producer')
 cfg=json.loads((root/'docs/section-panel-surfaces.json').read_bytes())
 live_panel=section_panel_surface_qa.inventory(cfg);section_panel_surface_qa.check(cfg,live_panel)
 req(live_panel==after['panel'],'panel inventory differs from full-tree producer')
 # A separately bound Timeline change modifies three non-Emma search rows.
 # Keep the original no-drift comparison unchanged: validate the full current
 # producer output first, then compare the exact reconstructed historical
 # index to the Emma baseline. This is not current review or release approval.
 from timeline_search_index_successor import AFTER as TIMELINE_SEARCH, restore as restore_timeline_search, sha
 raw=(root/'site-search-index.json').read_bytes()
 from timeline_51_search_successor import AFTER as EVENT_SEARCH, restore as restore_event_search
 if sha(raw)==EVENT_SEARCH:
  raw=restore_event_search(raw,root)  # Exact historical projection; actual producer already checked above.
 if sha(raw)==TIMELINE_SEARCH:
  historical=dict(after,search=json.loads(restore_timeline_search(raw,root)))
  result=check(before,historical)
  result['timeline_search_successor']='exact mechanical projection; current review remains separate'
  return result
 return check(before,after)
if __name__=='__main__':
 import argparse,json
 from pathlib import Path
 parser=argparse.ArgumentParser(description='Full-tree Emma current index delta only, not release approval')
 parser.add_argument('--root',type=Path,required=True);parser.add_argument('--baseline',type=Path,required=True);args=parser.parse_args()
 try:print(json.dumps(validate_full_tree(args.root,args.baseline),sort_keys=True))
 except (AssertionError,OSError,KeyError,ValueError) as error:raise SystemExit('Emma index successor BLOCKED: '+str(error))
