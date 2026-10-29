"""DRAFT partition adapter for four retained Emma stories, not release review.
Actual current story source validation must happen before historical projection.
"""
import hashlib

SOURCE_HASH={
 'history/emma-hymns.html':'55ee8b1a9b57154ca074282f2b6f44c19d77d15a63abd5adcde3286174625087',
 'history/emma-winter-crossing.html':'a2c6003789eaaf4458bb3f431943c2d4602908b19324054ef8ca9f0aab30a417',
 'history/emma-relief-society.html':'e90e7b25239973e2488f32e57482fd5cfbdabb6a7f3f1746599aded9cd546ebb',
 'history/emma-last-testimony.html':'ff608df4a3bb994d29834e253daac97b1721ecf2b3209a621e284f16ca91eb70',
}
CURRENT=frozenset({'history/emma-hymns.html','history/emma-winter-crossing.html','history/emma-relief-society.html','history/emma-last-testimony.html'})
RETIRED='history/emma-elect-lady.html'

def current_consumers(consumers,expected):
    if not isinstance(consumers,dict) or RETIRED in consumers:return None
    if any(consumers.get(route)!=expected for route in CURRENT):return None
    return {key:value for key,value in consumers.items() if key not in CURRENT}

def reviewed_wrap_additions(consumers,expected,version,historical_check):
    from emma_story_consumers import SYSTEM_REF
    if version!=SYSTEM_REF.split('?v=')[1]:return False
    historical=current_consumers(consumers,[SYSTEM_REF])
    return historical is not None and historical_check(historical,expected,version)

def reviewed_viewer_additions(bindings,historical_check):
    from emma_story_consumers import VIEWER_REFS
    historical=current_consumers(bindings,VIEWER_REFS)
    return historical is not None and historical_check(historical)

historical_consumers = current_consumers

def historical_routes(pages):
    assert len(pages)==len(set(pages)),'duplicate canonical route'
    assert RETIRED not in pages,'retired compatibility route cannot be canonical'
    assert CURRENT<=set(pages),'missing current Emma owner'
    return set(pages)-CURRENT

def assert_story_opening(route,text,doc,source_raw,previous):
    assert route in CURRENT,'unknown or retired current owner'
    assert isinstance(source_raw,bytes) and hashlib.sha256(source_raw).hexdigest()==SOURCE_HASH[route],'current story source drift'
    previous(route,text,doc)

