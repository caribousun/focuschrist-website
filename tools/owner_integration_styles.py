"""Exact added Adams shared-style consumers, not a generic CSS exception."""
from pathlib import Path
from owner_integration_contract import CHART, INTRO, LANDING, Document, validate_file

ROOT=Path(__file__).resolve().parents[1]
CSS='adams-integration.css'
OWNERS=frozenset((CHART,INTRO,LANDING))
TIMELINE_REF='../timeline-experiences.css?v=20261020-navigation-polish-1'

def refs(text, name):
    return [n.attrs.get('href','') for n in Document(text).root.walk()
            if n.tag=='link' and n.attrs.get('rel')=='stylesheet' and name in n.attrs.get('href','')]

def timeline_binding(page, tags):
    assert page==INTRO
    found=[a.get('href','') for t,a in tags if t=='link' and a.get('rel')=='stylesheet' and 'timeline-experiences.css' in a.get('href','')]
    return found==[TIMELINE_REF]

def timeline_consumers(sources, historical_owners, root=ROOT):
    if set(sources)!=set(historical_owners)|{INTRO}:
        return False
    raw=(root/INTRO).read_bytes();validate_file(INTRO,raw,root)
    return sources[INTRO]==raw.decode() and refs(sources[INTRO],'timeline-experiences.css')==[TIMELINE_REF] and sources[INTRO].count('timeline-experiences.css')==1

def validate_scoped_style(sources, root=ROOT):
    validate_file(CSS,(root/CSS).read_bytes(),root)
    actual={p for p,text in sources.items() if p!=CSS and CSS in text}
    assert actual==OWNERS, 'Exact three integrated stylesheet owners only'
    for route in OWNERS:
        raw=(root/route).read_bytes();validate_file(route,raw,root)
        assert sources[route]==raw.decode(), 'Current stylesheet consumer source drift'
        expected=('../' if '/' in route else '')+CSS+'?v=20261027-integrated-1'
        assert refs(sources[route],CSS)==[expected] and sources[route].count(CSS)==1, 'Exact integration stylesheet reference'
    return True
