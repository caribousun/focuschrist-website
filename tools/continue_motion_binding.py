"""Exact historical reconstruction plus a separate fail-closed motion gate.

Predecessor recovery never grants approval for changed behavior. The CLI requires
actual separately authored finished review evidence pinned by the integrator.
"""
import base64
import hashlib
import json
from pathlib import Path
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[1]
MAP='docs/continue-motion/predecessors.json'
REVIEWS='docs/continue-motion/reviews.json'
MAP_SHA='010f24f44c70beaab3dbfe2b92832cdc28adbb79343dcb34c144191154f4312a'
APPROVED_REVIEWS='4dddbcc19a585f93627a3d3bace52419ed588952aaaef2adf6c22f2353cea615'  # Actual finite finished reviews; publication is separate.

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def require(value,message):
    if not value:raise ValueError(message)

@lru_cache(maxsize=2)
def _mapping(raw,expected):
    data=json.loads(raw)
    require(expected is not None and canonical(data)==expected,'Unknown motion predecessor map')
    require(data.get('schema')==1 and data.get('version')=='20261021-continue-motion-1','Wrong motion predecessor schema')
    return data

def mapping(root=ROOT):
    return _mapping((root/MAP).read_bytes(),MAP_SHA)

def reviewed_bytes(path):
    """Preserve exact historical context for enumerated repository consumers."""
    raw=path.read_bytes()
    try:name=path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:return raw
    return restore(name,raw)

def restore(name,data,root=ROOT):
    from timeline_51_source_successor import project_exact
    data=project_exact(name,data,root)
    # Project only exact, separately bound later sources for historical checks.
    if name == 'answers/jesus-christ-latter-day-saint-beliefs.html':
        from timeline_nazareth_successor import AFTER as NAZARETH_AFTER, restore as restore_nazareth
        if sha(data)==NAZARETH_AFTER: data=restore_nazareth(data)
    elif name == 'timelines/world-and-scripture-timeline.html':
        from timeline_world_controls_successor import AFTER as WORLD_AFTER, restore as restore_world_controls
        from timeline_world_mobile_successor import AFTER as MOBILE_AFTER
        from timeline_world_tooltip_visual_successor import PAGE_AFTER as TOOLTIP_AFTER
        if sha(data) in (WORLD_AFTER, MOBILE_AFTER, TOOLTIP_AFTER): data=restore_world_controls(data,root)
    from owner_integration_successor import restore as restore_owner
    data=restore_owner(name,data,root)
    from emma_hub_citation_successor import restore as restore_hub_citations
    data=restore_hub_citations(name,data,root)
    from adams_delivery_successor import restore as restore_adams_delivery
    data=restore_adams_delivery(name,data,root)
    from emma_generated_indices_successor import restore as restore_emma_indices
    data=restore_emma_indices(name,data,root)
    from missionary_close_successor import restore as restore_close
    from commission_hand_successor import restore as restore_hand
    from world_companion_successor import restore as restore_world
    from settings_successor import restore as restore_settings
    from answer_bank_successor import restore as restore_bank
    from display_gate_successor import restore as restore_gate
    from evaluator_corrections_successor import restore as restore_eval
    from citation_rendering_successor import restore as restore_citation
    from legacy_answer_repairs_successor import restore as restore_legacy
    from bank_serve_decoupling_successor import restore as restore_decoupling
    from entry_scroll_successor import restore as restore_scroll
    from pioneer_entry_scroll_successor import restore as restore_pioneer_scroll
    from bank_context_bypass_successor import restore as restore_bypass
    from emma_story_successor import restore as restore_emma
    data=restore_world(name,restore_settings(name,restore_close(name,restore_hand(name,restore_bank(name,restore_gate(name,restore_eval(name,restore_citation(name,restore_legacy(name,restore_decoupling(name,restore_scroll(name,restore_pioneer_scroll(name,restore_bypass(name,restore_emma(name,data,root),root),root),root),root),root),root),root),root),root),root),root),root),root)
    record=mapping(root)['files'].get(name)
    if not record or sha(data)!=record['after_sha256']:return data
    restored=data
    last=len(data)
    for span in reversed(record['spans']):
        start,end=span['start'],span['end']
        require(isinstance(start,int) and isinstance(end,int) and 0<=start<=end<=last,'Overlapping motion inverse spans')
        require(data[start:end]==base64.b64decode(span['current_b64'],validate=True),'Motion inverse byte mismatch')
        restored=restored[:start]+base64.b64decode(span['previous_b64'],validate=True)+restored[end:]
        last=start
    require(sha(restored)==record['before_sha256'],'Motion predecessor reconstruction drift')
    return restored

def advance(name,data,root=ROOT):
    from timeline_51_source_successor import advance_exact as advance_timeline
    from owner_integration_successor import advance as advance_owner
    from emma_hub_citation_successor import advance as advance_hub_citations
    """Generate only the exact enumerated successor from an exact predecessor."""
    record=mapping(root)['files'].get(name)
    from emma_generated_indices_successor import advance as advance_emma_indices
    from adams_delivery_successor import advance as advance_adams_delivery
    from missionary_close_successor import advance as advance_close
    from commission_hand_successor import advance as advance_hand
    from world_companion_successor import advance as advance_world
    from settings_successor import advance as advance_settings
    from answer_bank_successor import advance as advance_bank
    from display_gate_successor import advance as advance_gate
    from evaluator_corrections_successor import advance as advance_eval
    from citation_rendering_successor import advance as advance_citation
    from legacy_answer_repairs_successor import advance as advance_legacy
    from bank_serve_decoupling_successor import advance as advance_decoupling
    from entry_scroll_successor import advance as advance_scroll
    from pioneer_entry_scroll_successor import advance as advance_pioneer_scroll
    from bank_context_bypass_successor import advance as advance_bypass
    from emma_story_successor import advance as advance_emma
    if not record or sha(data)!=record['before_sha256']:return advance_timeline(name,advance_owner(name,advance_hub_citations(name,advance_adams_delivery(name,advance_emma_indices(name,advance_emma(name,advance_bypass(name,advance_pioneer_scroll(name,advance_scroll(name,advance_decoupling(name,advance_legacy(name,advance_citation(name,advance_eval(name,advance_gate(name,advance_bank(name,advance_hand(name,advance_close(name,advance_settings(name,advance_world(name,data,root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root)
    replacements=[];delta=0
    for span in record['spans']:
        previous=base64.b64decode(span['previous_b64'],validate=True)
        current=base64.b64decode(span['current_b64'],validate=True)
        start=span['start']+delta
        require(data[start:start+len(previous)]==previous,'Motion successor byte mismatch')
        replacements.append((start,start+len(previous),current))
        delta+=len(previous)-len(current)
    result=data
    for start,end,current in reversed(replacements):result=result[:start]+current+result[end:]
    require(sha(result)==record['after_sha256'],'Motion successor reconstruction drift')
    return advance_timeline(name,advance_owner(name,advance_hub_citations(name,advance_adams_delivery(name,advance_emma_indices(name,advance_emma(name,advance_bypass(name,advance_pioneer_scroll(name,advance_scroll(name,advance_decoupling(name,advance_legacy(name,advance_citation(name,advance_eval(name,advance_gate(name,advance_bank(name,advance_hand(name,advance_close(name,advance_settings(name,advance_world(name,result,root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root),root)

def check(root=ROOT):
    from owner_integration_successor import restore as restore_owner, check as check_owner
    check_owner(root)
    from emma_hub_citation_successor import restore as restore_hub_citations, predecessor_view as hub_predecessor_view
    from adams_delivery_successor import predecessor_view as adams_predecessor_view, restore as restore_adams_delivery
    from emma_generated_indices_successor import check as check_emma_indices
    from missionary_close_successor import check as check_close,restore as restore_close
    from commission_hand_successor import check as check_hand,restore as restore_hand
    from world_companion_successor import check as check_world,restore as restore_world
    from settings_successor import restore as restore_settings,check as check_settings
    from answer_bank_successor import check as check_bank,restore as restore_bank
    from display_gate_successor import check as check_gate,restore as restore_gate
    from evaluator_corrections_successor import check as check_eval,restore as restore_eval
    from citation_rendering_successor import check as check_citation,restore as restore_citation
    from legacy_answer_repairs_successor import check as check_legacy,restore as restore_legacy
    from bank_serve_decoupling_successor import check as check_decoupling,restore as restore_decoupling
    from entry_scroll_successor import check as check_scroll,restore as restore_scroll
    from pioneer_entry_scroll_successor import check as check_pioneer_scroll,restore as restore_pioneer_scroll
    from bank_context_bypass_successor import check as check_bypass,restore as restore_bypass
    from emma_story_successor import check as check_emma,restore as restore_emma
    data=mapping(root)
    for name,row in data['files'].items():
        if name == 'timeline.html':
            # Current Timeline content is checked directly; historical fixture
            # reconstruction is a separate optional test, not a styling gate.
            from owner_integration_contract import validate_file
            validate_file(name, (root/name).read_bytes(), root)
            continue
        path=(root/name).resolve()
        require(path.is_relative_to(root.resolve()) and path.is_file(),'Missing/outside motion consumer')
        source=path.read_bytes()
        from timeline_51_source_successor import project_exact
        source=project_exact(name,source,root)
        # Later exact successors are projected only for this historical check;
        # their own current source and review remain separately required.
        if name == 'answers/jesus-christ-latter-day-saint-beliefs.html':
            from timeline_nazareth_successor import restore as restore_nazareth, BEFORE as NAZARETH_BEFORE, AFTER as NAZARETH_AFTER
            if sha(source)==NAZARETH_AFTER: source=restore_nazareth(source)
            else: require(sha(source)==NAZARETH_BEFORE,'Unknown Nazareth successor source')
        elif name == 'timelines/world-and-scripture-timeline.html':
            from timeline_world_controls_successor import restore as restore_world_controls, BEFORE as WORLD_BEFORE, AFTER as WORLD_AFTER
            from timeline_world_mobile_successor import AFTER as MOBILE_AFTER
            from timeline_world_tooltip_visual_successor import PAGE_AFTER as TOOLTIP_AFTER
            if sha(source) in (WORLD_AFTER, MOBILE_AFTER, TOOLTIP_AFTER): source=restore_world_controls(source,root)
            else: require(sha(source)==WORLD_BEFORE,'Unknown World controls source')
        historical_current=restore_hub_citations(name,restore_adams_delivery(name,restore_owner(name,source,root),root),root)
        current=restore_world(name,restore_settings(name,restore_close(name,restore_hand(name,restore_bank(name,restore_gate(name,restore_eval(name,restore_citation(name,restore_legacy(name,restore_decoupling(name,restore_scroll(name,restore_pioneer_scroll(name,restore_bypass(name,restore_emma(name,historical_current,root),root),root),root),root),root),root),root),root),root),root),root),root),root)
        require(sha(current)==row['after_sha256'],'Motion candidate changed: '+name)
        require(sha(restore(name,current,root))==row['before_sha256'],'Motion inverse failed: '+name)
    require(APPROVED_REVIEWS is not None,'Motion finished review PENDING')
    reviews=json.loads((root/REVIEWS).read_text(encoding='utf-8'))
    require(canonical(reviews)==APPROVED_REVIEWS,'Motion review record changed')
    require(reviews.get('map_sha256')==MAP_SHA,'Motion review source mismatch')
    rows=reviews.get('reviews',[])
    require(len(rows)==3 and {r.get('reviewer') for r in rows}=={'Albert','Fermi','Newton'},'Missing actual motion reviewers')
    for row in rows:
        require(row.get('decision')=='CONCUR' and row.get('finished_behavior') is True and row.get('map_sha256')==MAP_SHA,'Motion review incomplete')
        item=row['evidence'];path=(root/item['path']).resolve()
        require(path.is_relative_to(root.resolve()) and path.is_file(),'Missing/outside motion review evidence')
        require(sha(path.read_bytes())==item['sha256'],'Motion review evidence changed')
    check_world(root)
    check_settings(root)
    import shutil,tempfile
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        (view/'missionary.html').write_bytes(restore_hand('missionary.html',(root/'missionary.html').read_bytes(),root))
        shutil.copy2(root/'missionary-details.js',view/'missionary-details.js')
        shutil.copytree(root/'docs/missionary-close-successor',view/'docs/missionary-close-successor')
        check_close(view)
    check_hand(root)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        for bank_name in ('ask.html','pioneers.html','pioneer-experience.js'):
            (view/bank_name).write_bytes(restore_citation(bank_name,restore_legacy(bank_name,restore_decoupling(bank_name,restore_scroll(bank_name,restore_pioneer_scroll(bank_name,project_exact(bank_name,(root/bank_name).read_bytes(),root),root),root),root),root),root))
        shutil.copytree(root/'docs/answer-bank-successor',view/'docs/answer-bank-successor')
        check_bank(view)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        (view/'site-common.js').write_bytes(restore_eval('site-common.js',restore_decoupling('site-common.js',(root/'site-common.js').read_bytes(),root),root))
        shutil.copytree(root/'docs/display-gate-successor',view/'docs/display-gate-successor')
        check_gate(view)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        (view/'ask.html').write_bytes(restore_legacy('ask.html',restore_decoupling('ask.html',restore_scroll('ask.html',(root/'ask.html').read_bytes(),root),root),root))
        shutil.copytree(root/'docs/citation-rendering-successor',view/'docs/citation-rendering-successor')
        check_citation(view)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        (view/'site-common.js').write_bytes(restore_decoupling('site-common.js',(root/'site-common.js').read_bytes(),root))
        shutil.copytree(root/'docs/evaluator-corrections-successor',view/'docs/evaluator-corrections-successor')
        check_eval(view)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        for legacy_name in ('ask.html','pioneers.html'):
            (view/legacy_name).write_bytes(restore_decoupling(legacy_name,restore_scroll(legacy_name,restore_pioneer_scroll(legacy_name,project_exact(legacy_name,(root/legacy_name).read_bytes(),root),root),root),root))
        shutil.copytree(root/'docs/legacy-answer-repairs-successor',view/'docs/legacy-answer-repairs-successor')
        check_legacy(view)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        for decoupling_name in ('ask.html','site-common.js'):
            (view/decoupling_name).write_bytes(restore_scroll(decoupling_name,(root/decoupling_name).read_bytes(),root))
        shutil.copytree(root/'docs/bank-serve-decoupling-successor',view/'docs/bank-serve-decoupling-successor')
        check_decoupling(view)
    check_scroll(root)
    with tempfile.TemporaryDirectory() as td:
        view=Path(td)
        (view/'pioneers.html').write_bytes(project_exact('pioneers.html',(root/'pioneers.html').read_bytes(),root))
        shutil.copy2(root/'pioneer-experience.js',view/'pioneer-experience.js')
        shutil.copytree(root/'docs/pioneer-entry-scroll-successor',view/'docs/pioneer-entry-scroll-successor')
        check_pioneer_scroll(view)
    check_bypass(root)
    with hub_predecessor_view(root) as historical_hub:
        check_emma(historical_hub)
    # The view validates actual Adams bytes first; Emma checks historical bytes only.
    # Previous index producer bytes are historical, not current output.
    # Configured generator --check jobs test full source/output equivalence.
    from timeline_current_indices import validate_current
    validate_current(root)
    return {'status':'EXACT_MOTION_EVIDENCE_PASS','files':len(data['files']),'limits':'Technical evidence binding only; does not authenticate reviewers or grant publication approval.'}

if __name__=='__main__':
    try:print(json.dumps(check(),sort_keys=True))
    except (ValueError,KeyError,TypeError,OSError) as error:raise SystemExit('Continue motion gate BLOCKED: '+str(error))
