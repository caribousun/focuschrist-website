"""Exact four-scene current equivalence; no historical preflight claim or generic exemption."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from PIL import Image

SCENES={'christ-moving-day': 'answers/divorce-and-faith.html', 'christ-food-pantry': 'answers/are-latter-day-saints-christian.html', 'christ-homecoming-celebration': 'answers/faith-in-jesus-christ-during-trials.html', 'christ-children-colorful-day': 'art-study/suffer-the-little-children.html'}
NODES={'scene15': ('4d8ed6462589a7b2c0574ad60a804e0e2027b654858fbb7b6aed92072e8db198', '6782b740aef0ee64b40610640fbaf32b5620ec43a1875073dfba33556020588d', ['approved-home']), 'scene26-original': ('bdc586300dcacf4967c3181bf433853792b94867d6cac17566cb29c95eca968b', '9a0fd33f12ed16a7495f820d8245aea98dec0757f5c53f3fc85fca1f84330a65', ['approved-home']), 'scene26-final': ('d835e757765039247138af12a5fae27cf5655692757254be009dc61576093920', 'f9d6ca4752715e3d9e78529751326253c66f339a5ec4c999396a1a8744ed902f', ['scene26-original']), 'scene27-final': ('c1c592570b8fbc6083d7e39e344eb2a64b609b026f3da44449976e12f3969322', '8a2774b7cf69f3ae93bff4fb6e7341666e1b908fe5c3702669a9af48b84205b9', ['approved-home']), 'scene18-final': ('f405305ea6ddd8a78848fced8a1d04d0cfbf78ebbd6abe29c33060ca84a078ff', 'c071373277023b58bfd11da14ab16186097b479c812c90d07635f3db97c4f840', ['approved-home'])}
IDENTITY='4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b'
def require(ok,message):
    if not ok: raise ValueError('Four-scene delivery: '+message)
def canonical(value):
    return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def local(root,name):
    p=(root/name).resolve()
    require(isinstance(name,str) and not Path(name).is_absolute() and '\\' not in name and ':' not in name and p.is_relative_to(root.resolve()),'unsafe local path')
    require(p.is_file(),'missing local file '+name)
    return p
def digest(p):
    from continue_motion_binding import reviewed_bytes
    return hashlib.sha256(reviewed_bytes(p)).hexdigest()
def time(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00'))

def validate(root,record,approved_binding,added,covered,rejected,pixel_hash,page_dependencies):
    require(record.get('schema')==1 and canonical(record)==approved_binding,'unreviewed exact family record')
    spec=record['spec'];binding=canonical(spec)
    require(spec['classification']=='symbolic-christ-contemporary' and spec['owner_final_image_acceptance']=='not-claimed','identity/owner classification drift')
    require({s['id']:s['route'] for s in spec['scenes']}==SCENES and len(spec['scenes'])==4,'only exact four scenes permitted')
    identity=spec['identity_reference'];require(identity=={'path':'assets/heroes/home-christ-signature-approved-20260907.png','sha256':IDENTITY},'approved identity changed')
    require(digest(local(root,identity['path']))==IDENTITY,'actual identity changed')
    nodes={n['id']:n for n in spec['generation_graph']}
    require(len(nodes)==5 and len(spec['generation_graph'])==5 and set(nodes)==set(NODES),'generation graph drift')
    for node in nodes.values():
        require(node['source_sha256'] not in rejected,'forbidden generation ancestor')
        require(time(node['prompt_load']['timestamp'])<=time(node['dispatch']['timestamp'])<time(node['completion']['timestamp']),'generation chronology reversed')
        require(node['actual_load_outputs'],'missing actual prompt load evidence')
        for proof in [node['prompt_load'],node['dispatch'],node['completion'],*node['actual_load_outputs']]:
            require(len(proof['event_sha256'])==64 and all(ch in '0123456789abcdef' for ch in proof['event_sha256']),'invalid native event digest')
        for proof in node['actual_load_outputs']:
            require(time(node['prompt_load']['timestamp'])<=time(proof['timestamp'])<=time(node['dispatch']['timestamp']),'actual prompt load output chronology reversed')
        for key in ['stored_prompt_sha256','dispatched_prompt_sha256']:
            require(len(node[key])==64,'invalid prompt digest')
        require(node['stored_prompt_sha256']==node['dispatched_prompt_sha256'],'stored/dispatched prompt mismatch')
        for parent in node['references']:
            require(parent=='approved-home' or parent in nodes,'unresolved predecessor')
            if parent!='approved-home':require(time(nodes[parent]['completion']['timestamp'])<time(node['dispatch']['timestamp']),'reference did not yet exist')
    require(spec['registration_class']=='CURRENT_EQUIVALENCE' and spec['historical_preparation_audit_status']=='NOT_ESTABLISHED_BY_BOUNDED_AUDIT','historical approval invented')
    audit=spec['historical_preparation_audit'];rows={r['id']:r for r in audit['rows']}
    require(audit['reviewer']=='Newton' and len(audit['rows'])==5 and set(rows)==set(nodes) and audit['limitations'],'historical audit scope drift')
    for nid,node in nodes.items():
        require((node['source_sha256'],node['stored_prompt_sha256'],node['references'])==NODES[nid],'exact approved source/prompt/reference graph changed')
        row=rows[nid]
        require(row['source_sha256']==node['source_sha256'] and row['prompt_sha256']==node['stored_prompt_sha256'],'audit node mismatch')
        require(row['historical_three_role_preflight']=='NOT_ESTABLISHED_BY_BOUNDED_AUDIT' and row['historical_gate_preparation']=='NOT_CLAIMED' and row['current_equivalence_required'] is True,'historical classification drift')
        require(row['generation_lineage']=='VERIFIED_NATIVE_LOAD_DISPATCH_COMPLETION','unverified lineage')
        if 'earlier_newton_read_event' in row:
            proof=row['earlier_newton_read_event']
            require(time(proof['timestamp'])<time(node['dispatch']['timestamp']) and proof['evidence_class']=='Exact specification read before dispatch; not substituted for explicit concurrence','earlier read falsely classified')
    require('final_preparation' not in spec,'invented historical preparation')
    assets=set();hashes=set();pixels=set();latest=max(time(s['final_generated_at']) for s in spec['scenes'])
    for scene in spec['scenes']:
        sid=scene['id'];expected={f'assets/page-art/christ-world/masters/{sid}.png',*[f'assets/page-art/christ-world/{sid}-{size}.webp' for size in ['480','960','full']]}
        require({a['path'] for a in scene['assets']}==expected and len(scene['assets'])==4,'asset family expansion or omission')
        require(not scene['historical_claim'] and scene['owning_section']==sid,'false historical claim/ownership')
        master=next(a for a in scene['assets'] if a['kind']=='original')
        final_node=nodes[scene['generation_ids'][-1]]
        require(final_node['delivery_status']=='final-reviewed-source' and final_node['source_sha256']==master['sha256'] and final_node['completion']['timestamp']==scene['final_generated_at'],'wrong final master')
        im=Image.open(local(root,master['path'])).convert('RGB')
        for a in scene['assets']:
            p=local(root,a['path']);require(digest(p)==a['sha256'] and a['sha256'] not in rejected,'asset bytes changed/rejected')
            require(pixel_hash(p)==a['pixel_sha256'],'asset pixel digest changed')
            with Image.open(p) as delivered:
                require(delivered.size==(a['width'],a['height']) and getattr(delivered,'n_frames',1)==1,'wrong size/animated delivery')
                target=im if a['width']==im.width else im.resize((a['width'],round(im.height*a['width']/im.width)),Image.Resampling.LANCZOS)
                require(delivered.convert('RGB').tobytes()==target.tobytes() and delivered.size==target.size,'lossless pixel equivalence failed')
            assets.add(a['path']);hashes.add(a['sha256']);pixels.add(a['pixel_sha256'])
        context={c['path']:c['sha256'] for c in scene['context']}
        require(len(context)==len(scene['context']),'duplicate rendered context')
        if sid=='christ-children-colorful-day':require('four-scene-artwork.css' in context,'missing scoped background CSS')
        require(page_dependencies(root,scene['route'])<=set(context),'missing page/CSS context')
        require('four-scene-artwork.js' in context,'missing navigation helper binding')
        for name,value in context.items():require(digest(local(root,name))==value,'rendered context drift '+name)
        page=local(root,scene['route']).read_text(encoding='utf8')
        require(page.count('id="'+sid+'"')==1 and page.count('data-exclusive-artwork="'+sid+'"')==1,'owning placement missing or repeated')
    require(len(assets)==16 and assets<=added and not assets&covered,'coverage must be sixteen new separate assets')
    reviews={}
    for pointer in record['reviews']:
        p=local(root,pointer['path']);require(digest(p)==pointer['sha256'],'review bytes changed')
        receipt=json.loads(p.read_text(encoding='utf8'));who=receipt['reviewer']
        require(who in {'Fermi','Newton','Albert'} and who not in reviews,'unexpected/duplicate reviewer')
        require(receipt['decision']=='CONCUR' and receipt['spec_sha256']==binding,'missing exact concurrence')
        require(time(receipt['reviewed_at'])>=latest and time(receipt['reviewed_at'])>=time(record['normalized_at']),'backdated equivalence review')
        require(receipt['no_individual_owner_acceptance_claim'] is True,'false owner vote')
        if who in {'Fermi','Newton'}:
            require(receipt['private_source_and_event_verification'] is True and receipt['derivative_pixel_review'] is True and receipt['assembled_context_review'] is True,'missing independent equivalence/finished review')
        else:
            require(receipt['desktop_phone_direct_browser_review'] is True,'missing root direct assembled proof')
        require(receipt['evidence'] and receipt['limits'],'missing evidence scope/limits')
        reviews[who]=receipt
    require(set(reviews)=={'Fermi','Newton','Albert'},'three actual current reviews required')
    return assets,hashes,pixels
