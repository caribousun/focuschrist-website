"""Draft Emma-only current closure: NOT independent review or owner acceptance.

Do not repin historic closure receipts. The old 73-asset census still applies;
H2/C2 retirement remains explicit. Eleven new scene families are separately
covered by the artwork-creation gate, not added silently to the old census.
Fresh full-tree panel/gallery/search outputs and an independently reviewed,
owner-accepted current closure record are prerequisites. Absent evidence is a
hard failure. The 63fafd baseline blobs below are historical comparison inputs,
never substituted for current source or runtime outputs.
"""
from collections import Counter
from pathlib import Path
import hashlib,json,subprocess,tempfile
from datetime import datetime

HUB='history/emma-hale-smith.html'
CURRENT_HUB_SHA256='7511f2d034d6117cb9e4d0da896c3ff778c1f0a2165c0425361b47c1d6fb3573'
OLD_REGISTRY='docs/exclusive-artwork-ownership.json'
REVIEW_RECORD='docs/emma-journey-owner-closure/current-review.json'
# Fill only after real exact finished-source, asset, generated-output and owner
# review; this is deliberately PENDING, not a fabricated acceptance.
APPROVED_REVIEW_SHA256='58cb5d0f09fc8d146e832ca5f42a620f9586c6fbfff9f7c4d15e3776e5d0bc6c'
LEGACY_OWNER_COMMITMENT='f190d2ae997ec531a16e422d424eb756af1249ff4b88f5f29ab191b59fd6397a'
BASELINE_BLOBS={'art-gallery.json':'d7a9e628341f264d86227ac729d8db7ab8ef4584',
                'site-search-index.json':'cba61442fcbed4fd1e62d61b0d90134d8237d086',
                'docs/section-panel-inventory.json':'5a2db892aaad7e51e545e92604a8cd80b9becdc4'}

def require(ok,message):
    if not ok:raise ValueError('Emma journey current closure: '+message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def local(root,name):
    require(isinstance(name,str) and name,'missing evidence path')
    root=Path(root).resolve();p=(root/name).resolve()
    require(not Path(name).is_absolute() and '..' not in Path(name).parts and p.is_relative_to(root) and p.is_file(),'missing/unsafe '+str(name))
    require(not any((root.joinpath(*Path(name).parts[:i])).is_symlink() for i in range(1,len(Path(name).parts)+1)),'symlink evidence path '+name)
    return p

def validated_baseline(root, target):
    """Extract exact pinned repository blobs without network or altering the tree."""
    from emma_journey_indices_contract import git_blob
    root=Path(root).resolve();target=Path(target)
    for name,expected in BASELINE_BLOBS.items():
        try:raw=subprocess.check_output(['git','cat-file','blob',expected],cwd=root,timeout=30)
        except (OSError,subprocess.SubprocessError) as e:raise ValueError('Emma journey current closure: baseline blob unavailable '+name) from e
        require(git_blob(raw)==expected,'historical baseline blob drift '+name)
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)

def check_public_reviews(root, record, reviewers, root_review):
    """Validate bounded projections of the actual current review records.

    Private reviewer identity and source documents must be independently
    authenticated before the enclosing closure record is pinned. This does not
    turn their bounded Emma-index review into a whole-site review.
    """
    from emma_public_commitments import SUBJECT, SUBJECT_SHA256, read_pinned
    subject=read_pinned(root,SUBJECT,SUBJECT_SHA256)
    def evidence(name):
        item=record.get(name);require(isinstance(item,dict) and set(item)=={'path','sha256'},'missing '+name)
        expected_paths={'index_review_evidence':'docs/emma-journey-public/index-review-commitments.json','current_confirmation_evidence':'docs/emma-journey-public/closure-confirmations.json'}
        require(item['path']==expected_paths[name],'unexpected public review evidence path')
        raw=local(root,item['path']).read_bytes();require(sha(raw)==item['sha256'],'changed '+name)
        return json.loads(raw)
    index=evidence('index_review_evidence');confirm=evidence('current_confirmation_evidence')
    require(index.get('schema')=='emma-index-review-commitments-v1' and index.get('subject_sha256')==SUBJECT_SHA256 and index.get('scope')=='bounded_current_emma_indices_not_whole_site_review','index review subject mismatch')
    outputs={key:record[key] for key in ('panel','gallery','search')}
    require(index.get('hub_sha256')==CURRENT_HUB_SHA256 and index.get('outputs')==outputs,'index review outputs changed')
    require(confirm.get('schema')=='emma-current-closure-confirmations-v1' and confirm.get('subject_sha256')==SUBJECT_SHA256 and confirm.get('index_review_sha256')==record['index_review_evidence']['sha256'] and confirm.get('scope')=='bounded_current_emma_indices_not_whole_site_review','current confirmations mismatch')
    actors={x['role']:x['actor_commitment'] for x in subject['reviews']}
    require(record['assets_manifest']['sha256']==subject['source_manifest_sha256'] and subject['bindings']['delivery_spec_sha256']==subject['private_spec_sha256'],'asset manifest subject mismatch')
    expected={'Fermi':('23ad527d8d5b2a17682cb129a24be656bea072bb71ec22bebc8795cf285554cc','PASS_BOUNDED_EMMA_SCOPE','NOT_RECORDED'),
              'Newton':('9986e43705061849930f0c8f4fd48526f87484111ea7448c23566a3f5571350e','CONCUR_WITHIN_BOUNDED_SCOPE','NOT_WITHDRAWN')}
    entries=index.get('reviews');require(isinstance(entries,list) and len(entries)==2 and {x.get('role') for x in entries}==set(expected),'index reviewers missing')
    for entry in entries:
        role=entry['role'];row=next(x for x in reviewers if x['reviewer']==role)
        require((entry.get('source_receipt_sha256'),entry.get('verdict'),entry.get('withdrawn_status'))==expected[role],'index review receipt or status mismatch')
        require(entry.get('actor_commitment')==actors[role] and row.get('actual_actor')=='commitment:'+actors[role] and row.get('reviewed_at')==entry.get('reviewed_at') and row.get('evidence')==record['index_review_evidence'],'index reviewer association or time mismatch')
        require(row.get('assets_manifest_binding')=='separately_reviewed_current_source_subject','index reviewer manifest scope misstated')
    f=confirm.get('fermi');require(isinstance(f,dict) and f.get('source_receipt_sha256')=='52a3bb070acaa92899d3d9fd983b6b8bdd634c103a61b09baf6dcb7da9b6729a' and f.get('actor_commitment')==actors['Fermi'] and f.get('withdrawn') is False,'Fermi current non-withdrawal confirmation missing')
    old=next(x for x in entries if x['role']=='Fermi');require(f.get('index_reviewed_at')==old['reviewed_at'] and datetime.fromisoformat(f['confirmed_at'].replace('Z','+00:00'))>=datetime.fromisoformat(old['reviewed_at'].replace('Z','+00:00')),'Fermi confirmation time mismatch')
    require(next(x for x in reviewers if x['reviewer']=='Fermi').get('withdrawn_confirmed_at')==f['confirmed_at'],'Fermi withdrawal status time missing')
    a=confirm.get('albert');require(isinstance(a,dict) and a.get('source_receipt_sha256')=='f777c0e38bbf78d1f321246ee88f4672577669ba005bdbd69634274c9c448a7a' and a.get('actor_commitment')==actors['Albert'] and a.get('verdict')=='PASS_BOUNDED_EMMA_SCOPE' and a.get('withdrawn') is False and a.get('hub_sha256')==CURRENT_HUB_SHA256 and a.get('outputs')==outputs and a.get('reviewed_at')==root_review.get('reviewed_at'),'Albert current index review mismatch')
    require(root_review.get('assets_manifest_binding')=='separately_reviewed_current_source_subject','Albert manifest scope misstated')
    mandate=local(root,'docs/section-panel-design-mandate.md').read_bytes()
    require(a.get('section_panel_mandate_personally_read') is True and a.get('section_panel_mandate_sha256')==sha(mandate)=='26a8028ec7c7393d070e6f8006662861e1651643dbf925092b19d364ace797fc','Albert section-panel mandate read missing')
    for view in ('desktop','phone'):
        rendered=subject['bindings']['rendered'][view]['image']
        require(root_review[view+'_evidence']=={'path':rendered['path'],'sha256':rendered['sha256']},'Albert rendered evidence mismatch')

def check_review(root):
    """Review data must be authentic independently authored receipts, not a flag.

    An exact record hash binds all current page/index/artwork and reviewer
    evidence. It is intentionally unset until independent review and direct
    owner acceptance exist. This structural check cannot authenticate people.
    """
    require(APPROVED_REVIEW_SHA256 is not None,'PENDING actual current closure and owner review')
    raw=local(root,REVIEW_RECORD).read_bytes();require(sha(raw)==APPROVED_REVIEW_SHA256,'unreviewed current closure record')
    try:r=json.loads(raw)
    except (ValueError,UnicodeError) as e:raise ValueError('Emma journey current closure: malformed review record') from e
    require(r.get('schema')==1 and r.get('status')=='owner_accepted','current closure not owner accepted')
    require(r.get('current_hub_sha256')==CURRENT_HUB_SHA256,'current source review mismatch')
    assets=r.get('assets_manifest');require(isinstance(assets,dict),'missing asset evidence')
    for name in ('assets_manifest','gallery','search','panel','owner_acceptance'):
        entry=r.get(name);require(isinstance(entry,dict) and set(entry)=={'path','sha256'},'missing review binding '+name)
        current=local(root,entry['path']).read_bytes()
        if name=='search' and sha(current)!=entry['sha256']:
            from timeline_current_index_closure import prepare
            current=prepare(root)['historical_search']
        require(sha(current)==entry['sha256'],'stale review binding '+name)
    require(r['gallery']['path']=='art-gallery.json' and r['search']['path']=='site-search-index.json' and r['panel']['path']=='docs/section-panel-inventory.json','wrong generated output bindings')
    mandates={'AGENTS.md':'8517aa734f89b5fb1d6cb62fa1c870ec2f5959c8','docs/historical-character-identity.md':'a2af09fc97c9205139ed0621075fb5d189cf93c5','docs/section-panel-design-mandate.md':'dd0db449995f1f636abd0b84b0da4820630c87c8'}
    reviews=r.get('reviewers');require(isinstance(reviews,list) and len(reviews)==2 and {x.get('reviewer') for x in reviews}=={'Fermi','Newton'},'two independent reviewers required')
    require(len({x.get('actual_actor') for x in reviews})==2 and all(x.get('actual_actor') and x.get('decision')=='CONCUR' and x.get('withdrawn') is False for x in reviews),'missing/negative reviewer')
    for x in reviews:
        require(x.get('page_sha256')==CURRENT_HUB_SHA256 and all(x.get(k+'_sha256')==r[k]['sha256'] for k in ('gallery','search','panel','assets_manifest')),'reviewer evidence binding mismatch')
        require(x.get('mandate_blobs')==mandates and isinstance(x.get('observations'),str) and x['observations'].strip(),'reviewer mandate read/observations missing')
        ev=x.get('evidence');require(isinstance(ev,dict) and set(ev)=={'path','sha256'} and sha(local(root,ev['path']).read_bytes())==ev['sha256'],'reviewer evidence missing')
    public=r.get('review_mode')=='bounded_public_commitments_v1'
    owner=json.loads(local(root,r['owner_acceptance']['path']).read_bytes())
    if public:
        require(owner.get('kind')=='conditional_owner_commitment' and owner.get('actor_role')=='owner' and owner.get('decision')=='ACCEPT' and owner.get('withdrawn') is False and 'actual_actor' not in owner and 'reviewed_at' not in owner,'conditional owner commitment missing')
    else:
        actor=owner.get('actual_actor');require(owner.get('kind')=='direct_owner_acceptance' and isinstance(actor,str) and sha(actor.encode('utf-8'))==LEGACY_OWNER_COMMITMENT and owner.get('decision')=='ACCEPT' and owner.get('withdrawn') is False,'direct owner acceptance missing')
    require(owner.get('page_sha256')==CURRENT_HUB_SHA256 and (public or all(owner.get(k+'_sha256')==r[k]['sha256'] for k in ('gallery','search','panel','assets_manifest'))),'owner acceptance subject mismatch')
    require(isinstance(owner.get('source_evidence'),dict) and set(owner['source_evidence'])=={'path','sha256'} and sha(local(root,owner['source_evidence']['path']).read_bytes())==owner['source_evidence']['sha256'],'owner source evidence missing')
    root_review=r.get('root_review')
    require(isinstance(root_review,dict) and root_review.get('reviewer')=='Albert' and root_review.get('decision')=='CONCUR' and root_review.get('withdrawn') is False,'assembled root review missing')
    require(root_review.get('page_sha256')==CURRENT_HUB_SHA256 and all(root_review.get(k+'_sha256')==r[k]['sha256'] for k in ('gallery','search','panel','assets_manifest')),'root review subject mismatch')
    require(root_review.get('desktop_inspected') is True and root_review.get('phone_inspected') is True,'root desktop/phone review missing')
    require(root_review.get('mandate_blobs')==mandates and isinstance(root_review.get('observations'),str) and root_review['observations'].strip(),'root mandate read/observations missing')
    for view in ('desktop_evidence','phone_evidence'):
        ev=root_review.get(view);require(isinstance(ev,dict) and set(ev)=={'path','sha256'} and sha(local(root,ev['path']).read_bytes())==ev['sha256'],'root rendered evidence missing '+view)
    if public:
        from emma_public_commitments import OWNER_METADATA, OWNER_READBACK, OWNER_TIME_COMMITMENT
        require(r.get('owner_acceptance_mode')=='conditional_on_remaining_checks' and owner.get('acceptance_mode')=='conditional_on_remaining_checks' and owner.get('accepted_at_commitment')==OWNER_TIME_COMMITMENT and owner.get('metadata_commitment')==OWNER_METADATA and owner.get('private_readback_commitment')==OWNER_READBACK and owner.get('binding_basis')=='engineering_bindings_not_owner_claim_of_hash_review' and not any(k+'_sha256' in owner for k in ('gallery','search','panel','assets_manifest')),'conditional owner evidence misstated')
        check_public_reviews(root,r,reviews,root_review)
        from emma_public_commitments import validate_release
        validate_release(root)
    for subject in reviews+[root_review]+([] if public else [owner]):
        try:dt=datetime.fromisoformat(subject['reviewed_at'].replace('Z','+00:00'))
        except (KeyError,TypeError,ValueError) as e:raise ValueError('Emma journey current closure: invalid review time') from e
        require(dt.tzinfo is not None,'review time needs timezone')
    return r

def current_census(root,scope,assets,origin,expected):
    from artwork_owner_closure import (CURRENT_CONSUMER_SCOPE,CURRENT_SCOPE_PINS,H2_REMOVED,references)
    from owner_journey_successor import validate_hub,validate_canonical
    from emma_journey_indices_contract import validate_full_tree
    root=Path(root).resolve();names=[x['path'] for x in scope]
    require(len(names)==len(set(names)) and set(names)==CURRENT_CONSUMER_SCOPE,'consumer scope drift')
    require(len(assets)==73 and origin=='https://focuschrist.com','prior asset scope/origin drift')
    page=local(root,HUB).read_bytes();require(sha(page)==CURRENT_HUB_SHA256,'current hub bytes drift')
    validate_hub(page,root);validate_canonical(local(root,'sitemap.xml').read_bytes())
    require(sha(local(root,OLD_REGISTRY).read_bytes())==CURRENT_SCOPE_PINS[OLD_REGISTRY],'historical ownership registry changed')
    registry=json.loads(local(root,OLD_REGISTRY).read_bytes());retired=set()
    for name in ('emma-h2','emma-c2'):
        rows=[x for x in registry['replacements'] if x.get('name')==name]
        require(len(rows)==1 and rows[0].get('placement_status')=='retired' and rows[0].get('current_placement') is None,'historical retirement changed '+name)
        retired.update(x['path'] for x in rows[0]['assets'])
    require(all(expected[pair]==count for pair,count in H2_REMOVED.items()),'historical H2 census changed')
    # Never compare a previous index to itself: validate actual fresh producers
    # against separately recovered exact baseline blobs before the census.
    with tempfile.TemporaryDirectory(prefix='emma-closure-baseline-') as temp:
        validated_baseline(root,temp)
        result=validate_full_tree(root,Path(temp))
    require(result.get('new_emma_images')==10 and result.get('additional_person_free_origins')==1 and result.get('retained_emma_images')==9,'current index completeness missing')
    check_review(root)
    current_expected=Counter(expected)
    for pair in H2_REMOVED:del current_expected[pair]
    # Exactly one replacement in the reviewed scope: bind the actual current
    # hub bytes, keep every other source pin unchanged. This does not alter the
    # immutable historical closure contract or its prior review subject.
    revised=[dict(x,sha256=CURRENT_HUB_SHA256) if x['path']==HUB else dict(x) for x in scope]
    actual=references(root,revised,assets|retired,origin,current_emma=True)
    require(actual==current_expected,'actual retained-asset consumer census changed')
    return current_expected
