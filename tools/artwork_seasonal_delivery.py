"""Exact reviewed two-scene delivery family; no generic preflight exemption."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from PIL import Image

SCENES={'christ-winter-laughter':'answers/why-families-are-important.html','christ-christmas-light':'birth-of-christ.html'}
IDENTITY='4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b'
def require(ok,message):
    if not ok: raise ValueError('Seasonal delivery: '+message)
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
    require({s['id']:s['route'] for s in spec['scenes']}==SCENES and len(spec['scenes'])==2,'only exact two scenes permitted')
    identity=spec['identity_reference'];require(identity=={'path':'assets/heroes/home-christ-signature-approved-20260907.png','sha256':IDENTITY},'approved identity changed')
    require(digest(local(root,identity['path']))==IDENTITY,'actual identity changed')
    nodes={n['id']:n for n in spec['generation_graph']}
    require(len(nodes)==9 and len(spec['generation_graph'])==9,'generation graph drift')
    for node in nodes.values():
        require(node['source_sha256'] not in rejected,'forbidden generation ancestor')
        require(time(node['prompt_load']['timestamp'])<=time(node['dispatch']['timestamp'])<time(node['completion']['timestamp']),'generation chronology reversed')
        require(node['actual_load_outputs'],'missing actual prompt load evidence')
        for key in ['stored_prompt_sha256','dispatched_prompt_sha256']:
            require(len(node[key])==64,'invalid prompt digest')
        require(node['stored_prompt_sha256']==node['dispatched_prompt_sha256'],'stored/dispatched prompt mismatch')
        for parent in node['references']:
            require(parent=='approved-home' or parent in nodes,'unresolved predecessor')
            if parent!='approved-home':require(time(nodes[parent]['completion']['timestamp'])<time(node['dispatch']['timestamp']),'reference did not yet exist')
    require(len(spec['final_preparation'])==2 and {f['scene'] for f in spec['final_preparation']}=={22,23},'exact two final preparation records required')
    for final in spec['final_preparation']:
        last=nodes['winter-final-wrists' if final['scene']==22 else 'christmas-final-wrist']
        require(final['dispatch']==last['dispatch'] and final['completion']==last['completion'] and final['prompt_sha256']==last['dispatched_prompt_sha256'],'final preparation/node mismatch')
        require(time(final['dispatch']['timestamp'])<time(final['completion']['timestamp']),'final chronology invalid')
        require(set(final['prospective_evidence'])=={'Newton_spec_authorship_execution','Newton_plaintext_before_generation','Fermi_plaintext_prospective_concurrence'},'missing genuine prospective evidence')
        for proof in final['prospective_evidence'].values():require(time(proof['timestamp'])<time(final['dispatch']['timestamp']),'prospective evidence follows generation')
    assets=set();hashes=set();pixels=set();latest=max(time(s['final_generated_at']) for s in spec['scenes'])
    for scene in spec['scenes']:
        sid=scene['id'];expected={f'assets/page-art/christ-world/masters/{sid}.png',*[f'assets/page-art/christ-world/{sid}-{size}.webp' for size in ['640','960','full']]}
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
        require(page_dependencies(root,scene['route'])<=set(context),'missing page/CSS context')
        require('seasonal-artwork.js' in context,'missing navigation helper binding')
        for name,value in context.items():require(digest(local(root,name))==value,'rendered context drift '+name)
        page=local(root,scene['route']).read_text(encoding='utf8')
        require(page.count('id="'+sid+'"')==1 and page.count('data-exclusive-artwork="'+sid+'"')==1,'owning placement missing or repeated')
    require(len(assets)==8 and assets<=added and not assets&covered,'coverage must be eight new separate assets')
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
