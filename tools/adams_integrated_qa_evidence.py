"""Current integrated viewer/owner-journey evidence; historical report stays historical."""
import json
import math
import hashlib
import re
from adams_source_import_v9 import require, bound

def validate_semantic_successor(result):
    """Current actual report semantics, separate from exact source/evidence pins."""
    semantics = result.get('semantics')
    require(isinstance(semantics, dict), 'QA missing semantic evidence')
    heading = semantics.get('heading')
    links = semantics.get('continuations')
    require(isinstance(heading, dict), 'QA missing H1 evidence')
    require(heading.get('selector') == 'h1.title' and heading.get('tag') == 'H1' and heading.get('text') == 'Adams’ Chart · 1881', 'QA H1 identity')
    require(heading.get('fontWeight') == '700' and isinstance(heading.get('fontFamily'), str) and 'Georgia' in heading['fontFamily'] and heading.get('margins') == ['0px'] * 4, 'QA H1 styling')
    width = result['profile']['width']; height = result['profile']['height']
    expected_font = 22 if width >= 900 else min(23, max(16, width * .048))
    require(isinstance(heading.get('fontSize'), (int, float)) and math.isfinite(heading['fontSize']) and abs(heading['fontSize'] - expected_font) <= .02, 'QA H1 responsive size')
    require(isinstance(links, list) and len(links) == 1 and all(isinstance(n, dict) for n in links), 'QA continuation count')
    expected_links = [('nav[data-focuschrist-header=standard] .nav-logo', '../index.html', 'focusChrist')]
    for node, expected in zip(links, expected_links):
        require((node.get('selector'), node.get('href'), node.get('text')) == expected and node.get('tag') == 'A', 'QA continuation identity')
    initial = next((state for state in result['states'] if state['label'] == 'initial-fit'), None)
    require(initial is not None, 'QA missing initial semantic geometry')
    for node in [heading, *links]:
        require(node.get('visible') is True and node.get('hit') is True, 'QA semantic visibility/hit')
        require(all(isinstance(node.get(k), (int, float)) and not isinstance(node.get(k), bool) and math.isfinite(node[k]) for k in ('x', 'y', 'right', 'bottom', 'width', 'height')), 'QA semantic finite geometry')
        require(node['width'] > 0 and node['height'] > 0 and node['x'] >= -1 and node['y'] >= -1 and node['right'] <= width + 1 and node['bottom'] <= height + 1, 'QA semantic physical bounds')
        require(abs(node['right'] - node['x'] - node['width']) <= 1 and abs(node['bottom'] - node['y'] - node['height']) <= 1, 'QA semantic box consistency')
    require(all(n['bottom'] <= initial['viewport']['y'] + 1 for n in links), 'QA continuations must remain above chart')

    integration = result.get('integration')
    require(isinstance(integration,dict) and integration.get('footerPresent') is True, 'current canonical footer absent')
    require(integration['header']['bottom'] <= heading['y'] + 1, 'shared header overlaps chart title')
    require(integration['main']['height'] > 0, 'nonpositive current chart area')
    require(semantics.get('footerDestinations') == [{'href':'adams-1881-introduction.html','text':'About this chart'}, {'href':'../timeline.html#adams-1881','text':'All timelines'}], 'current footer continuation identity')


def validate_qa_report(spec, report, identity, captures):
    """Semantic checks after exact evidence byte binding; also unit-testable data."""
    require(report['sourceSHA256'] == spec['page']['sha256'] and report['landingSHA256'] == spec['landing']['sha256'], 'QA source identity')
    require(report['assetCount'] == 331 and report['assetBytes'] == 119541095, 'QA asset totals')
    rows = spec['assets']
    digest_input = ''.join(f"{r['path']}\0{r['bytes']}\0{r['sha256']}\n" for r in sorted(rows, key=lambda r: r['path']))
    require(report['assetSetSHA256'] == hashlib.sha256(digest_input.encode()).hexdigest(), 'QA asset digest')
    results = report['results']
    require(report['timedOut'] is False and len(results) == 4, 'QA timeout or profile count')
    require([r['profile'] for r in results] == spec['qa']['profiles'], 'QA profiles')
    require(all(r['pass'] is True and not r.get('error') and not r.get('issues') for r in results), 'QA failed profile')
    require(sum(len(r['states']) for r in results) == spec['qa']['states'] == 101, 'QA state count')
    require(all(r['initialFitOverlayOverlap'] == [] for r in results), 'QA initial chart obstruction')
    required = {'initial-fit', 'one-to-one', 'right-tap', 'left-tap', 'down-tap', 'up-tap', 'next-section', 'start', 'end', 'reset-fit', 'zoom-in', 'zoom-out', 'full-view', 'exit-full-view', 'fill-screen', 'exit-fill-screen', 'restore-map', 'map-navigation', 'final-reset', 'history-back-viewer', 'reload-viewer', 'home-history-back-viewer'}
    for result in results:
        validate_semantic_successor(result)
        labels = [s['label'] for s in result['states']]
        require(len(labels) == len(set(labels)) and required <= set(labels), 'QA missing or duplicate journey')
        if result['profile']['width'] <= 899 and result['profile']['height'] <= 700:
            require({'restore-arrows', 'compact-clear-fit'} <= set(labels), 'QA compact restore/close')
        for state in result['states']:
            tile = state['firstTile']; inline = tile['inline']; rect = tile['rect']; vp = state['viewport']
            require(abs(vp['y'] - state['toolbar']['bottom']) <= 1, 'QA toolbar overlap')
            require(abs(rect['width'] - inline['width']) <= 1 and abs(rect['height'] - inline['height']) <= 1 and abs(rect['x'] - vp['x'] - inline['left']) <= 1 and abs(rect['y'] - vp['y'] - inline['top']) <= 1, 'QA rendered geometry')
    shots = [shot for result in results for shot in result['screenshots']]
    require(len(shots) == report['screenshots'] == spec['qa']['screenshot_count'] == 24, 'QA screenshot count')
    require(len({s['file'] for s in shots}) == 24, 'QA duplicate screenshot')
    require(all(0 < s['bytes'] <= 1024 * 1024 and re.fullmatch(r'[a-z0-9-]+\.jpg', s['file']) for s in shots), 'QA screenshot limits')
    require(sum(s['bytes'] for s in shots) == report['screenshotBytes'] <= 23 * 1024 * 1024, 'QA screenshot bytes')
    require(captures['capture_count'] == 24 and sorted(captures['captures'], key=lambda r: r['file']) == sorted(shots, key=lambda r: r['file']), 'capture manifest mismatch')
    require(captures['raw_report_sha256'] == spec['qa']['report']['sha256'], 'capture report identity')
    expected = spec['qa']['producer']
    require(identity == expected, 'exact actual producer identity')
    require(identity['run_id'] == captures['run_id'] and identity['artifact_id'] == captures['artifact_id'], 'run/artifact identity')
    require(identity['artifact_bytes'] == captures['artifact_bytes'] and identity['artifact_sha256'] == captures['artifact_sha256'], 'artifact byte identity')
    require(identity['timeline_conclusion'] == 'success' and identity['release_claim'] is False, 'actual successful bounded job required')
    require(identity['repository'] == 'caribousun/focuschrist-website' and identity['event'] == 'pull_request', 'expected producer repository/event')
    require(report.get('integratedSources') == spec['context'], 'current integrated source set')
    assets = {'/' + r['path']: r for r in rows}; profiles = {r['profile']['name'] for r in results}
    require(0 < len(report['network']) <= report['requestCount'] <= 2000, 'QA request bound')
    for response in report['network']:
        expected = assets.get(response['path'])
        require(expected is not None and response['profile'] in profiles and response['status'] == 200 and response['bytes'] == expected['bytes'] and response['sha256'] == expected['sha256'], 'QA tile response')
    require(sum(r['bytes'] for r in report['network']) == report['tileResponseBytes'] <= 256 * 1024 * 1024, 'QA response byte bound')


def validate_owner_report(spec, report):
    require(report.get('pass') is True and report.get('timedOut') is False and report.get('errors') == [], 'owner journey not successful')
    require(report.get('contractSHA256') == spec['qa']['owner_contract']['sha256'], 'owner contract mismatch')
    profiles = report.get('profiles')
    require(isinstance(profiles,list) and [r['profile'] for r in profiles] == spec['qa']['owner_profiles'], 'owner profiles incomplete')
    for row in profiles:
        require(row.get('pass') is True and not row.get('error') and row.get('acceptanceErrors') == [], 'owner profile failed')
        pair = row['openingComparison']; ref=pair['reference']; cur=pair['current']
        require(all(cur['hero'][k] == ref['hero'][k] for k in ('x','y','width','height')), 'actual shared hero geometry differs')
        require(cur['style'] == ref['style'] and cur['heroObjectFit'] == ref['heroObjectFit'], 'Continue appearance or image framing differs')
        require(all(cur['cue'][k] == ref['cue'][k] for k in ('width','height','centerX','y','bottom')) and cur['textBottom'] == ref['textBottom'], 'actual Continue geometry/baseline differs')
        headers = {h['label']:h for h in row['headers']}
        for name in ('timeline','adams-intro','adams-chart'):
            h=headers[name]
            require(h.get('searchTested') is True and h.get('searchSubmitted') is False, 'shared Search not actually checked')
            require(h.get('menuTested') == row['profile']['touch'], 'actual menu coverage missing')
            require(all(h.get(k) is True for k in ('searchEscapeCleared','searchEmptyEscapeClosed','searchExplicitClose')), 'actual native Search transitions incomplete')
            states = [x for x in row['searchStates'] if x['label'] == name]
            require(len(states) == 5 and len({x['phase'] for x in states}) == 5, 'Search state inventory')
            phases = {x['phase']:x for x in states}
            require(phases['typed-query']['dialogOpen'] is True and phases['typed-query']['inputValue'] == 'Emma', 'typed Search state')
            require(phases['first-escape']['dialogOpen'] is True and phases['first-escape']['inputValue'] == '' and phases['first-escape']['activeId'] == 'fc-header-search', 'first Escape must clear native Search')
            for phase in ('empty-field-escape','explicit-close'):
                require(phases[phase]['dialogOpen'] is False and phases[phase]['focusOnTrigger'] is True, 'Search close/focus state')
        require(headers['adams-chart'].get('chartKeyboardGuard') is True, 'header/chart key conflict not checked')
        labels=[j['label'] for j in row['journeys']]
        require(labels.count('timeline-illustrated-intro-continue-chart-footer-back') == 1, 'owner journey missing/duplicate')
        layout=row['chartLayout']
        require(layout['heading']['top'] >= layout['nav']['bottom']-1 and abs(layout['viewport']['top']-layout['toolbar']['bottom']) <= 1 and layout['viewport']['height'] > 0, 'current chart geometry')
        footer=row['footer'];require(footer['height'] > 0 and footer['y'] < row['profile']['height'] and footer['y']+footer['height'] > 0, 'footer not reachable')
    shots=report['screenshots']
    require(len(shots) == 74 and len({s['file'] for s in shots}) == 74, 'owner capture inventory')
    require(all(0 < s['bytes'] <= 1024*1024 and re.fullmatch(r'[a-z0-9-]+\.jpg',s['file']) for s in shots), 'owner capture bounds')
    require(sum(s['bytes'] for s in shots) == report['screenshotBytes'] <= 23*1024*1024, 'owner capture total')
    require(report['requests'] <= 2500 and report['servedBytes'] <= 384*1024*1024, 'owner request/byte bounds')

def validate_qa(root, spec, helper_reader=bound):
    qa=spec['qa']
    for key in ('helper','owner_helper','owner_contract'):helper_reader(root,qa[key])
    report=json.loads(bound(root,qa['report']))
    identity=json.loads(bound(root,qa['run_identity']))
    captures=json.loads(bound(root,qa['capture_manifest']))
    validate_qa_report(spec,report,identity,captures)
    owner=json.loads(bound(root,qa['owner_report']))
    validate_owner_report(spec,owner)
    owner_captures=json.loads(bound(root,qa['owner_capture_manifest']))
    require(owner_captures['raw_report_sha256'] == qa['owner_report']['sha256'] and owner_captures['captures'] == owner['screenshots'], 'owner capture/report binding')
