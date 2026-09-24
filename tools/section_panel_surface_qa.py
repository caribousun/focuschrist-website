"""Inventory named panel surfaces; reject accidental geometry/image/control styling."""
import collections, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import xml.etree.ElementTree as ET
from answer_study_qa import Document
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'docs/section-panel-surfaces.json'
INVENTORY=ROOT/'docs/section-panel-inventory.json'
PATTERN=re.compile(r'card|panel|callout|reflection|note|tile|pathway')

def canonical():
    return sorted({urlsplit(e.text).path.lstrip('/') or 'index.html'
                   for e in ET.parse(ROOT/'sitemap.xml').getroot().iter() if e.tag.endswith('loc')})

def match_atom(node, atom):
    if atom.startswith('.'):return atom[1:] in node.attrs.get('class','').split()
    return node.tag==atom

def matches(node, selector):
    atoms=selector.split()
    if not match_atom(node, atoms[-1]):return False
    current=node.parent
    for atom in reversed(atoms[:-1]):
        while current and not match_atom(current,atom):current=current.parent
        if current is None:return False
        current=current.parent
    return True

def inventory(config):
    candidates=collections.defaultdict(lambda:dict(count=0,pages=set(),tags=set()))
    surfaces={s:dict(count=0,pages=set(),tags=set()) for s in config['surface_selectors']}
    nodes_by_page={}
    for page in canonical():
        d=Document();d.feed((ROOT/page).read_text(encoding='utf-8'))
        nodes=list(d.root.walk());nodes_by_page[page]=nodes
        for n in nodes:
            for c in n.attrs.get('class','').split():
                if PATTERN.search(c):
                    a=candidates[c];a['count']+=1;a['pages'].add(page);a['tags'].add(n.tag)
            for selector in surfaces:
                if matches(n,selector):
                    a=surfaces[selector];a['count']+=1;a['pages'].add(page);a['tags'].add(n.tag)
    direct={s.split()[-1][1:] for s in surfaces if s.split()[-1].startswith('.')}
    for c,a in candidates.items():
        if c in direct:status='shared_surface'
        elif c in config['unchanged_reference_classes']:status='approved_reference_unchanged'
        elif c in config['delegated_classes']:status='coordinated_stylesheet_owner'
        elif c in config['excluded_classes']:status='excluded_with_reason'
        else:raise AssertionError('Unclassified panel-like class: '+c)
        a['disposition']=status
        a['reason']=config['excluded_classes'].get(c) or config['delegated_classes'].get(c) or config['unchanged_reference_classes'].get(c) or 'Named existing section panel; shared Home-derived surface only.'
    # A component's name need not contain card/panel. Also discover actual
    # rounded, bordered, filled CSS surfaces that have canonical HTML users.
    class_pages=collections.defaultdict(set)
    for page,nodes in nodes_by_page.items():
        for n in nodes:
            if n.tag in ('div','section','article','aside','details','a'):
                for c in n.attrs.get('class','').split():class_pages[c].add(page)
    styled=collections.defaultdict(lambda:dict(stylesheets=set(),pages=set()))
    for file in ROOT.glob('*.css'):
        css=re.sub(r'/\*.*?\*/','',file.read_text(encoding='utf-8'),flags=re.S)
        for selectors,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
            if not all(re.search(p,body) for p in (r'background\s*:',r'border-radius\s*:',r'border\s*:')):continue
            for selector in selectors.split(','):
                if ':is(' in selector or ':where(' in selector:continue
                found=re.search(r'\.([\w-]+)$',selector.strip())
                if not found or found[1] not in class_pages:continue
                c=found[1];styled[c]['stylesheets'].add(file.name);styled[c]['pages'].update(class_pages[c])
    for c,a in styled.items():
        if c in direct:a['disposition']='shared_surface'
        elif c in config['unchanged_reference_classes']:a['disposition']='approved_reference_unchanged'
        elif c in config['delegated_classes']:a['disposition']='coordinated_stylesheet_owner'
        elif c in config['excluded_classes']:a['disposition']='excluded_with_reason'
        elif c in config.get('styled_surface_exclusions',{}):
            a['disposition']='excluded_with_reason';a['reason']=config['styled_surface_exclusions'][c]
        else:raise AssertionError('Unclassified rounded/bordered/filled surface: '+c)
    def clean(items):
        return {k:{field:sorted(value) if isinstance(value,set) else value for field,value in v.items()} for k,v in sorted(items.items())}
    return {'canonical_pages':canonical(),'candidate_classes':clean(candidates),'styled_surface_candidates':clean(styled),'surface_selectors':clean(surfaces),
            'limitations':'Static inventory and CSS scope checks are not rendered visual approval. Exclusions preserve bare reading wrappers, artwork and controls; delegated classes need their own runtime/visual checks.'}

def check(config,actual):
    css=(ROOT/'site-system.css').read_text(encoding='utf-8')
    block=css.split('/* BEGIN OWNER SECTION PANEL SURFACES',1)[1].split('/* END OWNER SECTION PANEL SURFACES */',1)[0]
    for s in config['surface_selectors']:
        assert 'body.fc-site '+s in block,'Surface selector missing '+s
        if s in config.get('runtime_selectors', {}):
            entry=config['runtime_selectors'][s]
            assert entry['marker'] in (ROOT/entry['source']).read_text(encoding='utf-8'), 'Runtime panel missing '+s
        else:
            assert actual['surface_selectors'][s]['count']>0,'No canonical consumer '+s
    allowed={'background','border-color','border-radius','box-shadow','--fc-muted'}
    for selector,body in re.findall(r'([^{}]+)\{([^{}]*)\}',block):
        if selector.strip().endswith(':root'):continue
        properties=set(re.findall(r'(?:^|;)\s*([\w-]+)\s*:',body))
        if '--fc-muted' in properties:
            assert re.search(r'--fc-muted:\s*var\(--fc-text\)\s*;',body), 'Panel muted copy must use brighter text token'
            assert 'body.fc-site .fc-card' not in selector, 'Approved Home must remain unchanged'
        assert properties<=allowed,'Geometry/control override in panel block: '+str(properties-allowed)
        assert not re.search(r'(^|[,\s])(?:img|figure|button|section)(?=\s*[,\{]|$)',selector),'Broad image/control/section selector'
    assert '--fc-panel-fill:' in block and 'var(--fc-card-fill)' in block
    assert '--fc-panel-shadow:' in block and 'inset 0 0 0 1px var(--fc-line)' in block
    assert '.fc-card {' not in block and '.fc-card::before' not in block,'Approved reference changed'
    assert not re.search(r'overflow(?:-[xy])?\s*:',block),'Clipping introduced'
    row=css.split('/* BEGIN OWNER MISSION PANEL ROW',1)[1].split('/* END OWNER MISSION PANEL ROW */',1)[0]
    row_rules=re.findall(r'(body[^{}]+)\{([^{}]*)\}',row)
    assert len(row_rules)==1 and row_rules[0][0].strip()=='body.fc-site .fc-missionary-work-grid','Mission row exception expanded'
    row_props=dict((k,re.sub(r'\s+','',v)) for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',row_rules[0][1]))
    assert row_props=={'gap':'18px','border':'0','background':'none'},'Mission row gap/strip contract changed'
    mission=(ROOT/'missionary.css').read_text(encoding='utf-8')
    for columns in ('repeat(4, minmax(0, 1fr))','repeat(2, minmax(0, 1fr))','1fr'):
        assert re.search(r'\.fc-missionary-work-grid\s*\{[^{}]*grid-template-columns:\s*'+re.escape(columns)+r'\s*;',mission),'Mission responsive columns changed'
    for p in actual['canonical_pages']:
        d=Document();d.feed((ROOT/p).read_text(encoding='utf-8'))
        links=[n.attrs.get('href','') for n in d.root.walk() if n.tag=='link' and urlsplit(n.attrs.get('href','')).path.endswith('site-system.css')]
        assert len(links)==1 and parse_qs(urlsplit(links[0]).query).get('v')==[config['version']],p+' missing current shared stylesheet'

def self_test():
    d=Document();d.feed('<section class="fc-deep-study"><div><details><summary>x</summary></details></div></section>')
    nodes=list(d.root.walk());details=next(n for n in nodes if n.tag=='details')
    assert matches(details,'.fc-deep-study details')
    assert not matches(details,'.fc-study-hub details')
    assert not matches(details,'.fc-deep-study img')
    assert PATTERN.search('new-study-panel')
    print('Panel surface self-test PASS: descendant scope and unknown-panel discovery.')

if __name__=='__main__':
    config=json.loads(CONFIG.read_text(encoding='utf-8'))
    if '--self-test' in sys.argv:self_test()
    actual=inventory(config);check(config,actual)
    if '--write-inventory' in sys.argv:INVENTORY.write_text(json.dumps(actual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:assert json.loads(INVENTORY.read_text(encoding='utf-8'))==actual,'Panel inventory drift; classify new panels deliberately.'
    print('SECTION PANEL QA PASS:',len(actual['canonical_pages']),'canonical pages,',len(actual['candidate_classes']),'classified panel-like classes,',len(actual['surface_selectors']),'shared selectors. Rendered QA remains separate.')
