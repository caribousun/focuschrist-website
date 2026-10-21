"""Strict successor evidence for the two owner-selected existing-art references.

Historical import evidence stays unchanged. This module never grants approval;
the reviewed successor manifest pin must be supplied after actual reviews.
"""
import hashlib
import json
import re
from pathlib import Path

BASELINE = 'docs/world-scripture-import/pr494-baseline.txt'
BASELINE_SHA = '79e8766bb3fd2b4493bf9679644654ad91a17090bb1f70373e88ae7e7b12d972'
PAGE = 'timelines/world-and-scripture-timeline.html'
MANIFEST = 'docs/world-scripture-import/artwork-reuse.json'
APPROVED_REUSE = '07f319f74d3b839359c3209aba997585c8cccaa76eb408ff8cce2d6f4426f924'  # Exact completed source/pixel reviews; owner publication approval remains separate.
ASSET = '/assets/page-art/atonement/first-hope.webp'
ASSET_SHA = 'fecacbeca9d2c885707a1feadb25d8b4e502fe3c308aefe15b68a61fdd02e495'
OWNER = 'https://focuschrist.com/atonement.html'
RETIRED = frozenset({
    '/assets/world-scripture/ba562fe56fbeb6bd97a5e6ecb753c5555b50dc5fba63fa398bcba989bcf32cbd.jpg',
    '/assets/world-scripture/2e7a94b04030b1dc99ae1d6921bacecd2a602f2e8be09867f123c0d140afa53d.jpg',
})

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

def require(ok, message):
    if not ok:
        raise ValueError(message)

def declaration(text, name):
    hits=list(re.finditer(r'\bconst\s+'+re.escape(name)+r'\s*=\s*', text))
    require(len(hits)==1, 'Missing or ambiguous '+name)
    return json.JSONDecoder().raw_decode(text[hits[0].end():])[0]

def validate_delta(before, after):
    old=declaration(before, 'DATA'); new=declaration(after, 'DATA')
    require(len(old)==len(new)==730, 'Changed record inventory')
    require({old[i]['img'] for i in (25,28)}==RETIRED, 'Changed original artwork records')
    for index,(a,b) in enumerate(zip(old,new)):
        if index not in (25,28):
            require(a==b, 'Unrelated DATA change: '+str(index)); continue
        require(b.get('img')==ASSET and b.get('imgpage')==OWNER, 'Incorrect artwork or owner')
        require(b.get('credit')=='Artwork: focuschrist.com', 'Missing site artwork credit')
        require({k:v for k,v in a.items() if k not in ('img','imgpage','credit')}==
                {k:v for k,v in b.items() if k not in ('img','imgpage','credit')}, 'Changed historical entry fields')
    oldcredits=declaration(before,'PHOTO_CREDITS'); active=declaration(after,'PHOTO_CREDITS')
    require(len(oldcredits)==193 and set(oldcredits)>=RETIRED, 'Unexpected historical rights inventory')
    require(active=={k:v for k,v in oldcredits.items() if k not in RETIRED}, 'Changed active rights inventory')
    require(not any(path in after for path in RETIRED), 'Retired photo remains a live reference')
    return {'records':730,'active_photos':191,'retired_photos':2,'reused_site_artworks':1}

def local(root, name):
    root=Path(root).resolve(); path=(root/name).resolve()
    require(path.is_relative_to(root) and path.is_file(), 'Missing/outside evidence: '+name)
    return path

def validate(root, current, expected=None):
    from continue_motion_binding import restore as before_motion
    current=before_motion(PAGE,current)
    expected=APPROVED_REUSE if expected is None else expected
    require(isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected), 'Artwork reuse pending finished review pin')
    record=json.loads(local(root,MANIFEST).read_text(encoding='utf-8'))
    require(canonical(record)==expected, 'Unreviewed artwork reuse manifest')
    require(record.get('schema')==1 and record.get('status')=='REVIEWED_EXISTING_ARTWORK_REUSE', 'Unfinished reuse evidence')
    require(record.get('page_sha256')==sha(current), 'Changed final page')
    baseline=local(root,BASELINE).read_bytes()
    require(sha(baseline)==BASELINE_SHA, 'Changed historical page baseline')
    require(sha(local(root,ASSET.lstrip('/')).read_bytes())==ASSET_SHA, 'Changed existing artwork bytes')
    require(record.get('baseline_sha256')==BASELINE_SHA and record.get('asset_sha256')==ASSET_SHA, 'Wrong provenance binding')
    require(record.get('owner_page')==OWNER and set(record.get('retired',[]))==RETIRED, 'Wrong ownership or retirement set')
    validate_delta(baseline.decode('utf-8'), current.decode('utf-8'))
    reviews=record.get('reviews',[])
    require(len(reviews)==3 and {r.get('reviewer') for r in reviews}=={'Albert','Fermi','Newton'}, 'Missing finished reviewers')
    for r in reviews:
        require(r.get('decision')=='CONCUR' and r.get('finished_pixels') is True and r.get('source_rights_checked') is True, 'Unperformed review')
        require(r.get('page_sha256')==sha(current), 'Review bound to another page')
        require(sha(local(root,r['evidence']['path']).read_bytes())==r['evidence']['sha256'], 'Changed review evidence')
    return baseline
