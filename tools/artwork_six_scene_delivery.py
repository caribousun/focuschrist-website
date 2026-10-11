"""Exact six-scene current equivalence; no historical preflight claim or generic exemption."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from PIL import Image

SCENES={'christ-under-countless-stars': 'art-study/the-living-christ.html', 'christ-earthquake-community': 'missionary.html', 'christ-hospital-corridor': 'jesus-christ/miracles-and-compassion.html', 'christ-caregiver-night': 'art-study/be-still.html', 'christ-last-bus': 'art-study/the-good-shepherd.html', 'christ-responder-rest': 'jesus-christ/parables/good-samaritan.html'}
NODES={'scene01': ('3d181461d7af5fd6b77d50dc4d5d0cc835ba1eb7150706187d148617e6452959', '7210f3bb82baf835b6e0f5a3b0b18e6753d1369e831773a25844c3ef3952c335', ['approved-home']), 'scene06': ('f114110e592096fc5b6557c95ccde558d026fbf06e92f101cef9e5520873d85c', '2b6bdf9415baa5076f224846f98dee29e8f93d6e4d3fd12bc8d3d547823b3cb0', ['approved-home']), 'scene08-original': ('b610a743bd00cac48ad9c1683e7dc70b6e03cc80bacc0a6cd179461abbb4fe13', '0043822062989ce87945af34d132c6361a2570c22012aa54bc63f09c80cf7fd3', ['approved-home']), 'scene08-final': ('ad524748880db2a57e8cff34120376d2ff4bd816154f122789fd49d9320aceb1', '0765c1c8532b16d4c604dd07ce812b40b87ef7248c340ae420c0198e7024cb6d', ['scene08-original', 'approved-home']), 'scene09': ('fc8cbb81addf78056a72e3f08980a484948f2e4156092d587191e2f64ec252f9', '565fda26a883e906d6e21dd3fe7d17221f7feb4373468244f05860e82d7ac896', ['approved-home']), 'scene11-original': ('9c5f7e8c634f2315f5f8ba0c932b31955582e62be838eff915979568da217bf0', '50091cf0aff88f71eaf1524d13aff75768e33a8a36a593a06b8e8df1ac9d764b', ['approved-home']), 'scene11-final': ('ce9d0696224460d0c9e86df8bd6b602b48b09a9558b85bb1d7db781d530db225', '815f466c3fad7a88ab0ff00794918d00e496edd38cca75dd515498dac8405104', ['approved-home', 'scene11-original']), 'scene13': ('b44746658c0e92b53a248995b9bdcdca71c34fcdb635d1059576967d4f35c1c3', 'cfa5cf97db53768b44cc2f6bfa48523c59933f3799d4f5f322bcdb99584d5118', ['approved-home'])}
IDENTITY='4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b'
def require(ok,message):
    if not ok: raise ValueError('Six-scene delivery: '+message)
def canonical(value):
    return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def local(root,name):
    p=(root/name).resolve()
    require(isinstance(name,str) and not Path(name).is_absolute() and '\\' not in name and ':' not in name and p.is_relative_to(root.resolve()),'unsafe local path')
    require(p.is_file(),'missing local file '+name)
    return p
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def time(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00'))

def validate(root,record,approved_binding,added,covered,rejected,pixel_hash,page_dependencies):
    require(record.get('schema')==1 and canonical(record)==approved_binding,'unreviewed exact family record')
    spec=record['spec'];binding=canonical(spec)
    require(spec['classification']=='symbolic-christ-contemporary' and spec['owner_final_image_acceptance']=='not-claimed','identity/owner classification drift')
    require({s['id']:s['route'] for s in spec['scenes']}==SCENES and len(spec['scenes'])==6,'only exact six scenes permitted')
    require(digest(local(root,'six-scene-artwork.css'))=='658c22fa104b970fe652961c5c13a860cc593e125b2b3102a591a826510ce311','exact six-scene stylesheet changed')
    consumers={p.relative_to(root).as_posix() for p in root.rglob('*.html') if 'six-scene-artwork.css' in p.read_text(encoding='utf8')}
    require(consumers==set(SCENES.values()),'six-scene stylesheet consumer drift')
    identity=spec['identity_reference'];require(identity=={'path':'assets/heroes/home-christ-signature-approved-20260907.png','sha256':IDENTITY},'approved identity changed')
    require(digest(local(root,identity['path']))==IDENTITY,'actual identity changed')
    nodes={n['id']:n for n in spec['generation_graph']}
    require(len(nodes)==8 and len(spec['generation_graph'])==8 and set(nodes)==set(NODES),'generation graph drift')
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
    require(audit['reviewer']=='Newton' and len(audit['rows'])==8 and set(rows)==set(nodes) and audit['limitations'],'historical audit scope drift')
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
        require(page_dependencies(root,scene['route'])<=set(context),'missing page/CSS context')
        require('six-scene-artwork.js' in context and 'six-scene-artwork.css' in context,'missing navigation/style binding')
        for name,value in context.items():require(digest(local(root,name))==value,'rendered context drift '+name)
        page=local(root,scene['route']).read_text(encoding='utf8')
        require(page.count('id="'+sid+'"')==1 and page.count('data-exclusive-artwork="'+sid+'"')==1,'owning placement missing or repeated')
    require(len(assets)==24 and assets<=added and not assets&covered,'coverage must be twenty-four new separate assets')
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
