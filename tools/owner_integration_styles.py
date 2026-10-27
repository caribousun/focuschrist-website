"""Exact added Adams shared-style consumers, not a generic CSS exception."""
from pathlib import Path
from owner_integration_contract import CHART, INTRO, LANDING, Document, validate_file

ROOT=Path(__file__).resolve().parents[1]
CSS='adams-integration.css'
OWNERS=frozenset((CHART,INTRO,LANDING))
TIMELINE_REF='../timeline-experiences.css?v=20261020-navigation-polish-1'
TIMELINE_MOBILE_REF='../timeline-mobile-study.css?v=20261004-terrain-recovery-1'

def refs(text, name):
    return [n.attrs.get('href','') for n in Document(text).root.walk()
            if n.tag=='link' and n.attrs.get('rel')=='stylesheet' and name in n.attrs.get('href','')]

def timeline_binding(page, tags):
    assert page==INTRO
    found=[a.get('href','') for t,a in tags if t=='link' and a.get('rel')=='stylesheet' and 'timeline-experiences.css' in a.get('href','')]
    return found==[TIMELINE_REF]

def _timeline_consumers(sources, historical_owners, name, expected, root):
    if set(sources)!=set(historical_owners)|{INTRO}:
        return False
    raw=(root/INTRO).read_bytes();validate_file(INTRO,raw,root)
    return sources[INTRO]==raw.decode() and refs(sources[INTRO],name)==[expected] and sources[INTRO].count(name)==1

def timeline_consumers(sources, historical_owners, root=ROOT):
    return _timeline_consumers(sources, historical_owners, 'timeline-experiences.css', TIMELINE_REF, root)

def timeline_mobile_consumers(sources, historical_owners, root=ROOT):
    return _timeline_consumers(sources, historical_owners, 'timeline-mobile-study.css', TIMELINE_MOBILE_REF, root)

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
