"""Evidence-preserving reader narrative gates; semantic review remains mandatory."""
import hashlib,json,re
from bs4 import BeautifulSoup
BASELINE_SHA256='23724949768c40951657d0a6233cf9e281930047fa9c03d5449d7fbe4bd0343b'
SECTION_ORDER=[1,2,4,5,6,7,8,9,11,12,3,10,13,14,15]
CHAPTER_GROUPS=[[1,2],[4,5],[6,7,8,9],[11,12],[3,10,13,14,15]]
REJECTED_EDITORIAL=('portrait remains unchanged','Keep him as he stands','no compulsory recoloring','our assessment','approved pixels','research verdict')

def check_canonical_narrative(root, canonical):
    """Reverse only the reviewed browser opening; retain exact manuscript equality."""
    current = '<p class="fc-page-intro-copy">What did Joseph Smith look like to the people who knew him? Explore portraits, casts and written accounts. Meet the artists, read remembered encounters, compare the features, and follow the choices behind our portrait.</p>'
    previous = '<p class="fc-page-intro-copy">Explore the portraits, casts and personal recollections that help us picture Joseph Smith. Meet the artists, compare the features, and follow the story of how our portrait took shape.</p>'
    actual = str(root)
    assert canonical is not None, 'Canonical research missing'
    openings = root.select(':scope > header.research-opening')
    assert len(openings) == 1, 'Exactly one research opening required'
    paragraphs = openings[0].select(':scope > p.fc-page-intro-copy')
    assert len(paragraphs) == 1 and str(paragraphs[0]) == current, 'Exact reviewed browser introduction required'
    assert actual.count(current) == 1 and previous not in actual, 'Mixed or duplicate research introduction'
    assert str(canonical).count(previous) == 1, 'Canonical introduction changed'
    assert actual.replace(current, previous, 1) == str(canonical), 'Generated research differs from canonical narrative input beyond the reviewed introduction'
def text(value):
    return re.sub(r'\s+',' ',BeautifulSoup(value,'html.parser').get_text(' ',strip=True)).strip()
def evidence_items(data):
    items=[]
    for section in data['sections']:
        for bi,block in enumerate(section['blocks']):
            if section['id']=='section-2' and block['kind']!='box':continue
            kind=block['kind'];values={}
            if kind=='paragraph':
                if block['style']=='title' or block['html'].startswith('Prepared for Wyatt. Use the navigation bar'):continue
                values={'html':block['html']}
            elif kind=='box':values={k:block[k] for k in ('title','html')}
            elif kind=='trait':values={k:block[k] for k in ('title','observed','evidence','verdict')}
            elif kind=='table':values={**{f'headers/{i}':x for i,x in enumerate(block['headers'])},**{f'rows/{i}/{j}':x for i,row in enumerate(block['rows']) for j,x in enumerate(row)}}
            elif kind=='image' and block.get('caption'):values={'caption':block['caption']}
            for field,value in values.items():
                items.append(dict(id=f'{section["id"]}/blocks/{bi}/{field}',original=value,original_sha256=hashlib.sha256(value.encode()).hexdigest(),kind=kind,field=field,feature_id='research-feature-'+block['title'].split()[0] if kind=='trait' else None))
    return items

def check_coverage(root,items,coverage):
    records=coverage['records'];expected={x['id']:x for x in items}
    assert len(records)==len(expected) and len({r['id'] for r in records})==len(records), 'Missing or duplicated evidence coverage record'
    assert {r['id'] for r in records}==set(expected), 'Evidence coverage IDs differ from preserved baseline'
    for record in records:
        original=expected[record['id']]
        assert record['original_sha256']==original['original_sha256'],'Original evidence changed inside coverage map'
        disposition=record['disposition']
        assert disposition in {'preserved','paraphrased','consolidated','presentation-retired'}, 'Unreviewed evidence disposition'
        assert len(record.get('reason','').split())>=5, 'Coverage needs a specific semantic rationale'
        targets=record.get('targets',[])
        if disposition=='presentation-retired':
            assert not targets, 'Retired presentation cannot pretend to map substantive evidence'
        else:
            assert targets, 'Substantive evidence needs actual narrative targets'
            for target in targets:
                node=root.find(id=target['id'])
                assert node is not None,'Coverage points outside actual narrative'
                excerpt=text(target['excerpt']);assert excerpt and excerpt in text(str(node)), 'Mapped evidence excerpt missing or changed'
            if original['feature_id'] and original['field']!='title':
                nodes=[root.find(id=t['id']) for t in targets]
                assert any(n.get('id')==original['feature_id'] or n.find_parent(id=original['feature_id']) for n in nodes), 'Feature-specific evidence moved away from its explanation'
            if disposition=='preserved':
                assert text(original['original']) in ' '.join(text(t['excerpt']) for t in targets), 'Preserved evidence is not actually preserved verbatim'
    return len(records)

def check_narrative(root,site):
    raw=(site/'docs/joseph-portrait-research-content.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASELINE_SHA256,'Historical evidence baseline changed; independent source review required'
    items=evidence_items(json.loads(raw));assert len(items)==164,'Original164evidence fields must remain accounted for'
    manuscript=(site/'docs/joseph-research-manuscript.html.inc').read_bytes()
    coverage=json.loads((site/'docs/joseph-research-narrative-coverage.json').read_text(encoding='utf-8'))
    assert coverage['baseline_sha256']==BASELINE_SHA256,'Coverage bound to different evidence baseline'
    digest=hashlib.sha256(manuscript).hexdigest()
    assert coverage['manuscript_sha256']==digest,'Narrative changed after semantic coverage review'
    canonical=BeautifulSoup(manuscript,'html.parser').select_one('#portrait-research')
    check_canonical_narrative(root, canonical)
    assert [int(s['id'].rsplit('-',1)[1]) for s in root.select('.research-part')]==SECTION_ORDER,'Unreviewed narrative order'
    assert [json.loads(a['data-research-sections']) for a in root.select('.research-chapters > a')]==CHAPTER_GROUPS,'Unreviewed chapter group coverage'
    for card,group in zip(root.select('.research-chapters > a'),CHAPTER_GROUPS):
        assert card.get('href')=='#portrait-section-'+str(group[0]) and card.select_one('strong').get_text(strip=True),'Chapter start/label missing'
    visible=BeautifulSoup(str(root),'html.parser')
    for node in visible.select('blockquote,q,[data-source-quotation]'):node.decompose()
    flat=text(str(visible)).casefold()
    for phrase in REJECTED_EDITORIAL:assert phrase.casefold() not in flat,'Owner-rejected editorial wording: '+phrase
    checked=check_coverage(root,items,coverage)
    records_digest=hashlib.sha256(json.dumps(coverage['records'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    for name in ('Fermi','Newton'):
        record=coverage['reviewers'][name];assert record['concur'] is True,'Independent semantic concurrence required'
        receipt_bytes=(site/record['receipt']).read_bytes();assert hashlib.sha256(receipt_bytes).hexdigest()==record['receipt_sha256'],'Coverage review receipt changed'
        receipt=json.loads(receipt_bytes)
        assert receipt['concur'] is True and receipt['manuscript_sha256']==digest and receipt['baseline_sha256']==BASELINE_SHA256 and receipt['coverage_records_sha256']==records_digest,'Semantic concurrence belongs to different evidence or narrative'
    return checked,coverage

def check_narrative_features(root,features,coverage):
    articles=root.select('.research-feature-study[data-research-feature]');expected={f'{i:02d}' for i in range(1,17)}
    assert len(articles)==16 and {a['data-research-feature'] for a in articles}==expected==set(features),'All16 distinct feature studies required'
    assert not root.select('.research-trait'),'Obsolete audit blocks cannot duplicate feature narrative'
    for article in articles:
        key=article['data-research-feature'];spec=features[key]
        assert article.get('id')=='research-feature-'+key,'Stable feature destination changed'
        assert article.select('p') and len(article.get_text(' ',strip=True).split())>=40,'Feature cannot be a heading-only coverage placeholder'
        figures=[f for f in article.select('figure') if not f.get('data-research-art','').startswith('likeness-')];assert len(figures)==len(spec['visuals'])>=2,'Feature reviewed visual set missing'
        assert any(v['src']=='assets/identities/joseph-smith-owner-approved-20260914.png' for v in spec['visuals']),'Feature adopted detail missing'
        for figure,visual in zip(figures,spec['visuals']):
            img=figure.select_one('img');assert img and img.get('data-source-original',img.get('src'))==visual['src'],'Feature image replaced'
            links={a.get('href') for a in figure.select('a[href]')}
            assert visual['src'] in links,'Feature full-original link missing'
            assert all(s['url'] in links for s in visual.get('sources',[])),'Feature historical source link missing'
            assert figure.select_one('figcaption'),'Feature image context missing'
    return expected


def check_art_migration(root, site):
    """Retain the published75, plus exactly four reviewed artworks and two references."""
    from collections import Counter
    migration=json.loads((site/'docs/joseph-journey-art-migration.json').read_text(encoding='utf-8'))
    def signature(figure):
        img=figure.select_one('img');anchor=figure.select_one('a:has(img)');src=img['src']
        return dict(src=src,sha256=hashlib.sha256((site/src).read_bytes()).hexdigest(),original_id=figure.get('data-research-art'),image_style=img.get('style',''),window_style=anchor.get('style',''),full_asset=anchor['href'])
    def key(record):return json.dumps(record,sort_keys=True)
    moves=migration['moves'];assert len(moves)==4 and len(migration['reference_moves'])==2,'Exactly six reviewed migrations required'
    baseline=migration['baseline_research_figures'];assert hashlib.sha256(json.dumps(baseline,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='47fa4873b19c48f3a0b76dbced6ea3a289bd8c80105925e5912a005fff28ed67','Published figure baseline altered'
    assert len(baseline)==75,'Published75 figure baseline incomplete'
    expected=list(baseline)
    review=json.loads((site/'docs/art-study-image-review.json').read_text(encoding='utf-8'))
    legacy=review['pages']['joseph-smith-likeness.html'] if 'pages' in review else review['routes']['joseph-smith-likeness.html']
    for move in moves:
        figures=root.select('figure[data-research-art="'+move['id']+'"]');assert len(figures)==1,'Migrated original must appear exactly once'
        figure=figures[0];target=move['to'].split('#')[1]
        assert figure.find_parent(id=target),'Migrated original outside reviewed reading destination'
        old=dict(move['baseline']);old['original_id']=move['id'];assert signature(figure)==old,'Migrated original pixels/crop/link changed'
        approved=next(r for r in legacy if r['slot']==move['legacy_slot'])
        assert approved['reviewed'] is True and approved['asset']==old['full_asset'],'Missing prior reviewed-original provenance'
        assert hashlib.sha256((site/approved['asset']).read_bytes()).hexdigest()==approved['sha256'],'Legacy reviewed original bytes changed'
        expected.append(old)
    for reference in migration['reference_moves']:
        target=root.find(id=reference['target']);assert target is not None,'Migrated reference destination missing'
        assert any(signature(f)==reference['baseline'] for f in target.select('figure')),'Migrated reference outside reviewed reading destination'
    expected.extend(r['baseline'] for r in migration['reference_moves'])
    assert Counter(map(key,expected))==Counter(key(signature(f)) for f in root.select('figure')),'Published figure set or exact migration changed'
    return migration
