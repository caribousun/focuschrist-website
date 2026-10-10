"""Owner correction checks, deliberately separate from visual approval."""
import math
import re
import hashlib
ROUTE = 'joseph-smith-portrait-research.html'
PDF_BROWSER_TOKEN_INVERSES = (
    (b'<link rel="stylesheet" href="site-system.css?v=20261005-mobile-study-rows-1">', b'<link rel="stylesheet" href="site-system.css?v=20260930-study-alignment-1">'),
    (b'<link rel="stylesheet" href="full-image-viewer.css?v=20261007-viewer-controls-1">', b'<link rel="stylesheet" href="full-image-viewer.css?v=20260905-viewport">'),
    (b'<script src="topic-artwork-details.js?v=20261009-settled-continue-2" defer></script>', b'<script src="topic-artwork-details.js?v=20261004-joseph-journeys-1" defer></script>'),
    (b'<script src="site-common.js?v=20261008-section-top-2" defer></script>', b'<script src="site-common.js?v=20261006-balanced-opening-1" defer></script>'),
)

PDF_CURRENT_BROWSER_SOURCE_SHA256 = '0126b33a1ca77902fc38aa478148261e975557a790c5cca535a8f7ca9c34b36f'
PDF_CURRENT_BROWSER_TOKEN_INVERSES = (
    (b'<link rel="stylesheet" href="connected-study.css?v=20261008-promotion-spacing-1">', b'<link rel="stylesheet" href="connected-study.css?v=20260927-anchor-alignment-1">'),
    (b'<link rel="stylesheet" href="joseph-smith-likeness.css?v=20261009-mobile-shared-height-1">', b'<link rel="stylesheet" href="joseph-smith-likeness.css?v=20261004-joseph-heroes-1">'),
    (b'<script src="full-image-viewer.js?v=20261009-titled-downloads-1" defer></script>', b'<script src="full-image-viewer.js?v=20260914-reopen-1" defer></script>'),
)

def check_pdf_source_binding(source, reviewed_hash):
    """Reconstruct exact frozen PDF source through four browser-only tokens."""
    if hashlib.sha256(source).hexdigest() == reviewed_hash:
        return
    inverse = source
    if hashlib.sha256(source).hexdigest() == PDF_CURRENT_BROWSER_SOURCE_SHA256:
        for current, reviewed in PDF_CURRENT_BROWSER_TOKEN_INVERSES:
            assert inverse.count(current) == 1 and reviewed not in inverse
            inverse = inverse.replace(current, reviewed, 1)
    for current, reviewed in PDF_BROWSER_TOKEN_INVERSES[1:]:
        assert inverse.count(current) == 1 and reviewed not in inverse, 'PDF source requires each exact single current browser dependency'
        inverse = inverse.replace(current, reviewed, 1)
    if hashlib.sha256(inverse).hexdigest() == reviewed_hash:
        return
    current, reviewed = PDF_BROWSER_TOKEN_INVERSES[0]
    assert inverse.count(current) == 1 and reviewed not in inverse, 'Exact prior shared-style token required'
    inverse = inverse.replace(current, reviewed, 1)
    assert hashlib.sha256(inverse).hexdigest() == reviewed_hash, 'Research content changed beyond exact reviewed browser tokens'

REJECTED_ARTWORK_BADGES = ('New artistic interpretation', 'New artwork · historical interpretation',
                         'New artwork · explanatory interpretation', 'New artwork · feature study')
ARTWORK_FOOTER_DISCLOSURE = ('Artwork on focusChrist includes AI-generated artistic interpretations. '
    'Illustrative and reconstructed details are not photographs or eyewitness records of the people or events shown.')
REJECTED_SCENE_BOILERPLATE = (
    'The artwork offers reverent, imaginative scenes; the linked scriptures provide the accounts we study.',
    'Let the quiet of this imagined landscape lead you to the scriptures',
    'Jesus does not specify the merchandise or the particular transactions',
    "this scene illustrates the story's action without claiming to show the devil's physical appearance",
    'without claiming a particular family dispute or its outcome',
    'without claiming to display everything he owned',
    'This is an illustration of His parable.',
    'This cloth-market exchange is an illustration of that activity, not merchandise specified in the parable.',
    'The father watching at the gate is an artistic detail that gives the departure a personal setting.',
    'their clothing, setting and gesture are not a record of the wedding',
    'its appearance, the handoff and the couple’s clothing are interpreted',
    'The clothing and session are interpreted',
    'this reflective scene imagines the room, book and pose',
    'her clothing, gestures and the room are interpreted',
    'The source does not record their exact pose, furnishings or garments',
    'Emma’s reading moment, expression, clothing and surroundings are imagined',
    'this particular task moment, wagon, clothing and path are interpreted',
    'the wagon, clothing, route and weather are interpreted',
    'their posture, clothing and room are interpreted',
    'the room, pose and furnishings here are an artistic interpretation',
    'The newly imagined side view is not a measured reconstruction',
    'New explanatory artwork', 'newly made interpretive Joseph artwork',
    'This new scene interprets that temporary appearance',
    'A new expression study is contemporary explanatory art, not an eyewitness record',
    'The hymn’s publication is distinct from an undocumented scene of its composition',
    'in a reconstruction of the later family account',
    'the pictured transaction is reconstructed', 'the exact home and arrangement are imagined',
    'the pictured conversation is imagined', 'the room and moment are imagined',
    'their exact arrangement is not recorded', 'the scene is reconstructed',
    'The campsite and task are reconstructed', 'An imagined aftermath of the cow’s kick',
    'the fittings are reconstructed', 'in a reconstruction of his family’s later account',
    'the pictured panel is not an exact facsimile',
    'the exact appearance of the ancient camp remains uncertain',
    'An artistic interpretation guided by Nephi’s account',
    'the gentle rise pictured here is an interpretation, not a known location',
    'A historical artistic reconstruction informed by portraits from her lifetime',
    'This historical artistic reconstruction draws on portraits of Emma',
    'The opening illustration is an artistic interpretation of a pioneer family',
    'This is an illustrative landscape, not a verified biblical location',
    'The artwork offers reverent interpretations of scripture, historical accounts, and study',
    'in this interpretation of a camp discussion',
    'This illustrative landscape is not a named scriptural location',
    'This youthful interpretation recalls that difficult journey',
    'Historical portrait interpretation of Elijah Able',
    'Historical interpretation of young adult Elijah Able',
    'Historical artistic interpretation of Elijah Able',
    'Historical interpretation of young Jane Manning James',
    'Historical portrait interpretation of Jane Manning James',
    'Historical artistic interpretation: Green Flake on the westward trail',
    'Historical artistic interpretation: A life of work in Union',
    'Historical artistic interpretation: Remembering Green Flake',
    'Historical artistic interpretation of President Spencer W. Kimball',
    'Artistic portrait based on Elijah Able’s surviving likeness',
    'Artistic portrait based on Jane Manning James’s surviving likeness',
    'This interpretive study scene accompanies the Church’s account of prayer and revelation',
    'The artist imagines the scene; the passage tells us what was recorded',
)

def check_no_repeated_artwork_disclosure(text):
    # Normalize extraction whitespace/punctuation without rejecting meaningful
    # source-specific historical limits or artwork descriptions.
    normalize = lambda value: ''.join(c for c in value.casefold() if c.isalnum())
    actual = normalize(text)
    assert not any(normalize(label) in actual for label in REJECTED_ARTWORK_BADGES), 'Owner-rejected generic artwork badge returned'
    assert not any(normalize(phrase) in actual for phrase in REJECTED_SCENE_BOILERPLATE), 'Owner-rejected per-scene disclaimer boilerplate returned'

def check_artwork_disclosure_text(text):
    check_no_repeated_artwork_disclosure(text)
    normalize = lambda value: ''.join(c for c in value.casefold() if c.isalnum())
    actual = normalize(text)
    assert normalize(ARTWORK_FOOTER_DISCLOSURE) in actual, 'Artwork disclosure must remain visible in footer/edition closing'

def check_caption_evidence_metacommentary(text):
    rejected = ('His care is documented', 'His hired labor is documented', 'The comb purchase is recorded',
                'Their move to Harmony is documented', 'The reading is recorded in Doctrine and Covenants 135',
                'The minutes record her urging', 'His later history records the women praying',
                'Joseph’s November 1838 letter survives')
    normalize = lambda value: ''.join(c for c in value.casefold() if c.isalnum())
    assert not any(normalize(x) in normalize(text) for x in rejected), 'Owner-rejected caption evidence-status commentary returned'

def check_artwork_badges_and_footer(doc):
    accessible_text = ' '.join(str(node.get(attr,'')) for node in doc.find_all(True) for attr in ('alt','title','aria-label','data-full-image-alt'))
    check_artwork_disclosure_text(doc.get_text(' ',strip=True)+' '+accessible_text)
    for caption in doc.select('figcaption'): check_caption_evidence_metacommentary(caption.get_text(' ',strip=True))
    footer = doc.select_one('footer [data-focuschrist-artwork-disclosure="footer"]')
    assert footer and footer.get_text(' ',strip=True) == ARTWORK_FOOTER_DISCLOSURE, 'Exact shared footer artwork disclosure required'
    assert not footer.has_attr('hidden') and footer.get('aria-hidden') != 'true', 'Footer disclosure must remain visible'
REJECTED_GENERIC_SCENES={
    'research-record-date-comparison','research-custody-gap','research-viewpoint-demonstration',
    'research-photogrammetry-method','research-source-independence'
}
REJECTED_GENERIC_HASHES={
    '2e1fceb1acdc83d0cac23164635c3c4268a529f8bace14c8e55408dff535a1d7',
    '31060009b9c24b415b4fb917a85178c98193d3ab9fc0ad8517271902a4ca1245',
    '64969c7fa606de986b0b6af7286af917f458a34f66b89bd42bffb03492117639',
    '9246c40f79fecd6b097c0e1243aa9846e21b43f0afccbd4bcff69c1f14a0e56e',
    '84c152a2ce978289c0ec5bd05f5e1fcb2154c7d36cc47395b7a27715f368f2eb'
}

def section_label(p):
    """Only the numbered direct-child chapter eyebrow is navigation metadata."""
    parent=p.parent
    if not (parent and 'research-part' in parent.get('class',[]) and 'fc-eyebrow' in p.get('class',[])):return False
    from joseph_research_narrative_qa import SECTION_ORDER
    try:number=int(parent['id'].rsplit('-',1)[1]);position=SECTION_ORDER.index(number)+1
    except (KeyError,ValueError):return False
    return p.get_text(' ',strip=True)==f'Chapter {position:02d}'

def bibliography_paragraph(p):
    section=p.find_parent(class_='research-part')
    source_index=p.find_parent('details',class_='research-source-index')
    return bool(section and section.get('id') in {'portrait-section-13','portrait-section-14','portrait-section-15'} and source_index and {'research-source','research-source-note'} & set(p.get('class',[])))

def check_entry_and_brevity(main):
    assert not main.select('.research-part, .research-trait, .research-table-wrap, .research-source'), 'Complete research must not be appended to main study'
    bridge=main.select_one('#joseph-study-entrance')
    if bridge:
        assert not main.select('main figure, main img'),'Concise bridge cannot duplicate artwork ownership'
        pills={a.get('href') for a in bridge.select('.fc-actions a.fc-button')}
        assert {ROUTE,'answers/who-was-joseph-smith.html#joseph-family-life'}<=pills,'Bridge needs both complete reader journeys'
        assert len(bridge.get_text(' ',strip=True).split())<=500,'Bridge must remain a concise entry'
        assert bridge.select_one('#our-portrait a[href="'+ROUTE+'#portrait-section-11"]'),'Legacy portrait anchor must reach portrait-making chapter'
        assert bridge.select_one('#portrait-research a[href="'+ROUTE+'"]'),'Legacy research anchor must reach complete journey'
        return
    entry=main.select_one('#our-portrait')
    assert entry is not None, 'Missing portrait entry section'
    assert any(a.get('href','').split('#')[0]==ROUTE and 'fc-button' in a.get('class',[]) and 'research' in a.get_text().lower() for a in entry.select('a[href]')), 'Main portrait section needs a clear research pill to the separate route'
    legacy=main.select_one('#portrait-research')
    if legacy:
        assert len(legacy.get_text(' ',strip=True).split())<=120, 'Legacy research landing must stay brief'
        assert len(legacy.select('p'))<=2, 'Legacy research landing is not a short entry'
        assert any(a.get('href','').split('#')[0]==ROUTE for a in legacy.select('a[href]')), 'Legacy research anchor must lead to separate page'

def check_feature_studies(root, features, traits):
    """Check the complete evidence-to-choice units, not just sixteen headings."""
    expected={f'{i:02d}' for i in range(1,17)}
    assert set(features)==expected and set(traits)==expected, 'All sixteen feature specifications and trait records are required'
    articles=root.select('.research-feature-study[data-research-feature]')
    assert len(articles)==16 and {a['data-research-feature'] for a in articles}==expected, 'All sixteen distinct feature studies must be present'
    assert not root.select('.research-trait'), 'Old trait blocks must not duplicate new feature studies'
    def text(value):
        from bs4 import BeautifulSoup
        value=BeautifulSoup(value,'html.parser').get_text(' ',strip=True)
        value=re.sub(r'\[\s*[0-9]+(?:\s*[-,]\s*[0-9]+)*\s*\]','',value)
        return re.sub(r'\s+',' ',value).strip()
    for article in articles:
        key=article['data-research-feature']; spec=features[key]; trait=traits[key]
        assert article.get('id')=='research-feature-'+key, 'Feature deep-link identity differs'
        assert 1<=len(spec['explanation'])<=2 and spec.get('limits'), 'Each feature needs bounded explanation and explicit limits'
        actual=text(str(article))
        for value in [trait['title'],trait['observed'],trait['evidence'],trait['verdict'],*spec['explanation'],spec['limits']]:
            assert text(value) in actual, 'Feature-local evidence or reasoning missing: '+key
        figures=article.select('figure')
        assert len(figures)==len(spec['visuals'])>=2, 'Each feature needs its actual reviewed visual set'
        assert any(v['src']=='assets/identities/joseph-smith-owner-approved-20260914.png' for v in spec['visuals']), 'Feature lacks unchanged adopted detail'
        assert any(v.get('sources') for v in spec['visuals']), 'Feature lacks direct historical-source access'
        for figure, visual in zip(figures,spec['visuals']):
            image=figure.select_one('img')
            assert image and image.get('data-source-original',image.get('src'))==visual['src'], 'Feature visual missing or replaced by distant link'
            assert text(visual['caption']) in text(str(figure)), 'Feature visual context changed'
            destinations={a.get('href') for a in figure.select('a[href]')}
            assert visual['src'] in destinations and visual['owner'] in destinations, 'Feature full-size/return action missing'
            assert all(s['url'] in destinations for s in visual.get('sources',[])), 'Feature historical-source action missing'
    return expected

def check_reading_cadence(root, exceptions=(), verified_features=()):
    blocks=root.select('[data-research-reading-block]')
    assert blocks, 'Reading must be divided into image-supported blocks'
    allowed = {e['slot']:e for e in exceptions}
    assert len(allowed)==len(exceptions), 'Duplicate cadence exception'
    seen=set()
    for block in blocks:
        slot=block.get('data-research-reading-block')
        paragraphs=[p for p in block.select('p') if not p.find_parent('figure') and 'research-return' not in p.get('class',[]) and not bibliography_paragraph(p)]
        units=block.select('.research-trait, table')
        if units:
            assert len(units)<=2 and (len(units)==1 or all(u.name!='table' for u in units)), 'A visual must not cover a long stack of traits/tables'
            assert all(any(u in p.parents for u in units) for p in paragraphs), 'Trait/table block includes extra unsupported prose'
        else:
            assert len(paragraphs)<=2, 'More than two narrative paragraphs without an adjacent image'
        if slot in allowed:
            item=allowed[slot]
            assert item.get('purpose') in {'source-key','unavailable-source-table','short-synthesis','proposed-work','research-limits'}, 'Unreviewed cadence exception purpose'
            assert len(item.get('reason','').split())>=5, 'Cadence exception needs a specific source-grounded rationale'
            copy=block.select_one('.research-reading-copy')
            assert copy, 'Cadence exception needs an explicit reading-copy boundary'
            content=re.sub(r'\s+',' ',copy.get_text(' ',strip=True)).strip()
            assert hashlib.sha256(content.encode('utf-8')).hexdigest()==item.get('content_sha256'), 'Cadence exception text changed; independent review must be renewed'
            assert not block.select('.research-trait'), 'Trait audits need actual feature imagery'
            assert len(paragraphs)<=2 and len(units)<=1, 'Cadence exception cannot hide a long prose or table stack'
            if units:
                assert item['purpose']=='unavailable-source-table' and len(units[0].select('tbody tr'))<=3, 'Only one bounded contemporary-record table may omit unavailable manuscript images'
            assert not block.select_one('figure img'), 'Image-supported block no longer needs an exception'
            seen.add(slot)
        else:
            assert block.select_one('figure img'), 'Reading block needs a relevant image or exact reviewed cadence rationale: '+str(slot)
    assert seen==set(allowed), 'Unused or stale cadence exception'
    for p in root.select('.research-part p'):
        if p.find_parent('figure') or 'research-return' in p.get('class',[]) or bibliography_paragraph(p) or section_label(p):continue
        feature=p.find_parent(class_='research-feature-study')
        if feature and feature.get('data-research-feature') in verified_features:continue
        assert p.find_parent(attrs={'data-research-reading-block':True}), 'Narrative paragraph escaped image-cadence accounting'
    return len(blocks)

def check_original_manifest(records, require_half_christ=True):
    """Metadata is checked here; reviewers must still inspect actual pixels."""
    assert len(records)>=10, 'At least ten unique originals are required'
    assert not any(r['id'] in REJECTED_GENERIC_SCENES or r['sha256'] in REJECTED_GENERIC_HASHES for r in records), 'Owner-rejected generic method scenes cannot be used'
    assert all(r['kind']=='original_scene' for r in records), 'Reference images/diagrams cannot count as originals'
    assert len({r['id'] for r in records})==len(records), 'Duplicate original identity'
    assert len({r['sha256'] for r in records})==len(records), 'Renamed/repeated bytes do not create originals'
    assert all(r['owning_page']==ROUTE and r.get('owning_section') for r in records), 'Every original requires this sole page and section'
    assert all(type(r['depicts_christ']) is bool for r in records), 'Christ classification must be explicit'
    if require_half_christ:
        assert sum(r['depicts_christ'] for r in records)>=math.ceil(len(records)/2), 'Christ must appear in at least half, rounded up'

def check_evidence_inventory(placements, references, route):
    """Exact Joseph evidence-study scope; never count references as new art.

    The later owner instruction requires actual masks, portrait evidence and
    documented creation. General artwork rules remain in check_original_manifest.
    This path permits only byte-identified references, not generated substitutes.
    """
    assert route == ROUTE, 'Evidence-study scope is limited to the Joseph research route'
    assert placements and references, 'Evidence study requires actual source imagery'
    assert len({r['asset'] for r in references}) == len(references), 'Ambiguous reference asset'
    inventory = {r['asset']: r for r in references}
    used = set()
    for placed in placements:
        assert placed['src'] in inventory, 'Unclassified evidence image: '+placed['src']
        reference = inventory[placed['src']]
        assert reference['kind'] in {'historical_document', 'existing_reference'}, 'Generated art cannot enter as source evidence'
        assert placed['sha256'] == reference['sha256'], 'Evidence image bytes differ from source record'
        assert re.fullmatch(r'[0-9a-f]{64}', reference['sha256']), 'Evidence requires exact SHA256'
        assert reference['sha256'] not in REJECTED_GENERIC_HASHES, 'Rejected generic image cannot be renamed as evidence'
        assert reference.get('source_url') or reference.get('owning_study'), 'Evidence requires source or owning-study provenance'
        if reference['kind'] == 'historical_document':
            assert reference.get('rights_basis') and reference.get('processing') and reference.get('publication_year'), 'Historical scan needs rights, processing and date provenance'
        used.add(reference['asset'])
    return {'unique_reference_assets': len(used), 'reference_placements': len(placements), 'new_original_artworks': 0}

def check_reference_scope(record):
    if record.get('reference_sha256'):
        refs=record['reference_sha256']
        refs=refs if isinstance(refs,list) else [refs]
        assert all(isinstance(v,str) and re.fullmatch(r'[0-9a-f]{64}',v) for v in refs), 'Identity references require actual SHA256 values'
        if record['depicts_christ']:
            assert '4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b' in refs, 'Christ scene must use the current approved Home identity'
        return
    assert record.get('identity_scope')=='unnamed_contemporary_only' and record['depicts_christ'] is False, 'Historical/Christ identity reference cannot be waived'
    assert record.get('reference_sha256')==[] and record.get('reference_not_applicable_reason','').strip(), 'Anonymous modern scene requires explicit empty reference list and reason'

def check_exact_review(record, receipt, finished=False):
    candidates=receipt.get('scenes',[receipt])
    matches=[r for r in candidates if r.get('id')==record['id']]
    assert len(matches)==1, 'Review must identify exactly this scene'
    review=matches[0]
    assert review.get('concur') is True, 'Explicit concurrence is missing or withheld'
    assert review.get('prompt_sha256')==record['preflight_prompt_sha256'], 'Review covers another prompt'
    if finished:
        assert review.get('sha256')==record['sha256'], 'Finished review covers other asset bytes'


def check_original_page_exclusivity(records, rendered_images):
    """Rendered-image hashes catch renamed clones; source citations are allowed."""
    owners={r['sha256']:r['owning_page'] for r in records}
    for page, hashes in rendered_images.items():
        for digest in hashes:
            if digest in owners:
                assert page==owners[digest], 'Original artwork cloned onto another page: '+page
