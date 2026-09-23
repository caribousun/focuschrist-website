#!/usr/bin/env python3
"""Static release gate for the sitewide hero review. Does not grant visual/owner approval."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
import argparse, hashlib, json, re, subprocess, sys, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXT = {'.png','.webp','.jpg','.jpeg','.avif','.gif','.svg'}
BIBLE_STYLE = 'bible-together.css'
BIBLE_STYLE_SHA256 = '128b2a54bf1a285497ea11d6c8e9040c55baa996ec75aa376b29463f854a9121'
BIBLE_STYLE_OWNER = 'answers/bible-and-book-of-mormon-together.html'
MISSION_ENRICHMENT_STYLE = 'missionary-enrichment.css'
MISSION_ENRICHMENT_STYLE_SHA256 = 'e40315cfc4994ba862cd7bf3c1d4f0fa77db5bd1ba59d8ca0eedfd8cdd8b875c'
WATCH_SHORTS_STYLE = 'watch-shorts.css'
WATCH_SHORTS_STYLE_SHA256 = '3d5c271067dc106524f103fb3af67d6423a77f1a338fc5691c2af02d7723bd85'
HOME_STYLE = 'home-presentation.css'
HOME_STYLE_SHA256 = '435c9f72296fd8ded6d19d09a3963b5ef291cae22faa9ce562292f4f2d62a5b8'
HOME_STYLE_OWNER = 'index.html'
JOURNEY_STYLE = 'jesus-journey.css'
JOURNEY_STYLE_SHA256 = '68f2abf3d0fa65b2e87c6a8bd3798dd8dfb1a1e522e7f3d5b14dc810d1f90978'

def reviewed_mission_enrichment_style(data):
    return hashlib.sha256(data).hexdigest() == MISSION_ENRICHMENT_STYLE_SHA256

def mission_enrichment_style_reference_allowed(relative, text):
    return relative == "missionary.html" or MISSION_ENRICHMENT_STYLE not in text

def reviewed_watch_shorts_style(data):
    return hashlib.sha256(data).hexdigest() == WATCH_SHORTS_STYLE_SHA256

def watch_shorts_style_reference_allowed(relative, text):
    return relative == "watch.html" or WATCH_SHORTS_STYLE not in text

def reviewed_home_style(data):
    return hashlib.sha256(data).hexdigest() == HOME_STYLE_SHA256

def home_style_reference_allowed(relative, text):
    return relative == HOME_STYLE_OWNER or HOME_STYLE not in text

def reviewed_bible_style(data):
    return hashlib.sha256(data).hexdigest() == BIBLE_STYLE_SHA256

def bible_style_reference_allowed(relative, text):
    return relative == BIBLE_STYLE_OWNER or BIBLE_STYLE not in text

def reviewed_journey_style(data):
    return hashlib.sha256(data).hexdigest() == JOURNEY_STYLE_SHA256

def journey_style_reference_allowed(relative, text, owners):
    return relative in owners or JOURNEY_STYLE not in text

BOUNDARY_WRAP_STYLES = {'.fc-history-page main': ('church-history.css', '26991016b8be1b6a3dc8854d41e07a1b6d12cdbefaf7ac260ba4b1736ec74b1a'), '.fc-missionary-page main': ('missionary.css', '1fc685047557e7d077b8c25c833731dca799335add20d3b139cf626f72357e21')}

def reviewed_boundary_wrap(selector, body, data):
    entry = BOUNDARY_WRAP_STYLES.get(selector.strip())
    return bool(entry and re.sub(r"\s+", "", body) == "overflow-wrap:anywhere;" and hashlib.sha256(data).hexdigest() == entry[1])

MISSION_PURPOSE_RULES = {
    '.fc-missionary-purpose .fc-missionary-visual figcaption': 'position:static;padding:16px24px;background:transparent;',
    '.fc-missionary-purpose .fc-missionary-copy > .fc-section-heading': 'max-width:none;',
}

def reviewed_mission_purpose(selector, body, data):
    return (selector.strip() in MISSION_PURPOSE_RULES
            and re.sub(r'\s+', '', body) == MISSION_PURPOSE_RULES[selector.strip()]
            and hashlib.sha256(data).hexdigest() == BOUNDARY_WRAP_STYLES['.fc-missionary-page main'][1])

class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.feed(text)
    def handle_starttag(self, tag, attrs): self.tags.append((tag,dict(attrs)))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unique_reviewed(heroes, rejected):
    errors=[]; seen={}
    for h in heroes:
        for field in ('source_sha256','sha256'):
            value=h.get(field)
            if not value or not re.fullmatch(r'[0-9a-f]{64}',value): errors.append(f"{h.get('key')}: missing valid {field}"); continue
            if value in rejected: errors.append(f"{h.get('key')}: rejected {field}")
            identity=(field,value)
            if identity in seen: errors.append(f"{h.get('key')}: duplicate {field} with {seen[identity]}")
            seen[identity]=h.get('key')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--baseline-report');args=ap.parse_args()
    if args.self_test:
        good=[{'key':'a','source_sha256':'1'*64,'sha256':'2'*64},{'key':'b','source_sha256':'3'*64,'sha256':'4'*64}]
        assert not unique_reviewed(good,set())
        duplicate=[good[0],dict(good[1],source_sha256='1'*64)]
        assert any('duplicate source_sha256' in e for e in unique_reviewed(duplicate,set()))
        assert any('rejected sha256' in e for e in unique_reviewed(good,{'2'*64}))
        mission_css = (ROOT/MISSION_ENRICHMENT_STYLE).read_bytes()
        assert reviewed_mission_enrichment_style(mission_css)
        assert not reviewed_mission_enrichment_style(mission_css + b'\n.fc-visual-hero{height:9px}')
        assert mission_enrichment_style_reference_allowed('missionary.html', MISSION_ENRICHMENT_STYLE)
        assert not mission_enrichment_style_reference_allowed('index.html', MISSION_ENRICHMENT_STYLE)
        assert not mission_enrichment_style_reference_allowed('shared.css', '@import "' + MISSION_ENRICHMENT_STYLE + '";')
        assert not mission_enrichment_style_reference_allowed('shared.js', MISSION_ENRICHMENT_STYLE)
        shorts_css = (ROOT/WATCH_SHORTS_STYLE).read_bytes()
        assert reviewed_watch_shorts_style(shorts_css)
        assert not reviewed_watch_shorts_style(shorts_css + b'\n.fc-visual-hero{height:9px}')
        assert watch_shorts_style_reference_allowed('watch.html', WATCH_SHORTS_STYLE)
        assert not watch_shorts_style_reference_allowed('index.html', WATCH_SHORTS_STYLE)
        assert not watch_shorts_style_reference_allowed('shared.css', '@import "' + WATCH_SHORTS_STYLE + '";')
        assert not watch_shorts_style_reference_allowed('shared.js', WATCH_SHORTS_STYLE)
        home_css = (ROOT/HOME_STYLE).read_bytes()
        assert reviewed_home_style(home_css)
        assert not reviewed_home_style(home_css + b'\nbody.fc-home-presentation{height:999px}')
        assert home_style_reference_allowed('index.html', HOME_STYLE)
        assert not home_style_reference_allowed('about.html', HOME_STYLE)
        assert not home_style_reference_allowed('shared.css', '@import "' + HOME_STYLE + '";')
        assert not home_style_reference_allowed('shared.js', HOME_STYLE)
        reviewed_css = (ROOT/BIBLE_STYLE).read_bytes()
        assert reviewed_bible_style(reviewed_css)
        assert not reviewed_bible_style(reviewed_css + b'\n.fc-topic-unique-hero{height:999px}\n')
        assert bible_style_reference_allowed(BIBLE_STYLE_OWNER, BIBLE_STYLE)
        assert not bible_style_reference_allowed('answers/another-page.html', BIBLE_STYLE)
        assert not bible_style_reference_allowed('shared.css', '@import "'+BIBLE_STYLE+'";')
        journey_css = (ROOT/JOURNEY_STYLE).read_bytes()
        owners = {'answers/jesus-christ-latter-day-saint-beliefs.html','jesus-christ/before-bethlehem.html','birth-of-christ.html'}
        assert reviewed_journey_style(journey_css)
        assert not reviewed_journey_style(journey_css + b'\n.fc-topic-unique-hero{height:999px}\n')
        assert journey_style_reference_allowed('jesus-christ/before-bethlehem.html', JOURNEY_STYLE, owners)
        assert journey_style_reference_allowed('answers/jesus-christ-latter-day-saint-beliefs.html', JOURNEY_STYLE, owners)
        assert journey_style_reference_allowed('birth-of-christ.html', JOURNEY_STYLE, owners)
        assert not journey_style_reference_allowed('index.html', JOURNEY_STYLE, owners)
        assert not journey_style_reference_allowed('answers/another-page.html', JOURNEY_STYLE, owners)
        assert not journey_style_reference_allowed('shared.css', '@import "'+JOURNEY_STYLE+'";', owners)
        for selector, (filename, _) in BOUNDARY_WRAP_STYLES.items():
            data = (ROOT/filename).read_bytes()
            assert reviewed_boundary_wrap(selector, 'overflow-wrap: anywhere;', data)
            assert not reviewed_boundary_wrap(selector, 'overflow-wrap: anywhere; height: 9px;', data)
            assert not reviewed_boundary_wrap('.wrong-page main', 'overflow-wrap: anywhere;', data)
            assert not reviewed_boundary_wrap(selector, 'overflow-wrap: anywhere;', data + b'\nmain{height:9px}')
        mission_css = (ROOT/'missionary.css').read_bytes()
        for selector, body in MISSION_PURPOSE_RULES.items():
            assert reviewed_mission_purpose(selector, body, mission_css)
            assert not reviewed_mission_purpose(selector, body + 'height:9px;', mission_css)
            assert not reviewed_mission_purpose('.wrong-page main', body, mission_css)
            assert not reviewed_mission_purpose(selector, body, mission_css + b'\nmain{height:9px}')
        print('PASS regression fixtures: duplicate/rejected images, modified Bible/journey CSS and out-of-scope stylesheet references are rejected'); return 0
    errors=[]
    def check(ok,msg):
        if not ok: errors.append(msg)
    plan=json.loads((ROOT/'docs/sitewide-hero-production-plan.json').read_text(encoding='utf8'))
    baseline=plan['baseline']; tree=subprocess.check_output(['git','ls-tree','-r','-z',baseline],cwd=ROOT)
    preserved=[]
    for entry in tree.split(b'\0'):
        if not entry: continue
        meta,name=entry.split(b'\t',1); name=name.decode('utf8'); path=ROOT/name
        if path.suffix.lower() not in IMAGE_EXT: continue
        old=meta.decode().split()[2]
        if not path.is_file():errors.append('Protected image missing: '+name);continue
        data=path.read_bytes(); current=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        check(current==old,'Protected image bytes changed: '+name)
        preserved.append({'asset':name,'baseline_blob':old,'sha256':hashlib.sha256(data).hexdigest(),'unchanged':current==old})
    if args.baseline_report:Path(args.baseline_report).write_text(json.dumps({'baseline':baseline,'images':preserved},indent=2),encoding='utf8')
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    pages=[urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(ROOT/'sitemap.xml').findall('s:url/s:loc',ns)]
    expected_pages={p.relative_to(ROOT).as_posix() for p in [*ROOT.glob('*.html'),*ROOT.glob('answers/*.html'),*ROOT.glob('art-study/*.html'),*ROOT.glob('jesus-christ/**/*.html')] if p.name not in {'404.html','google3fa84a4b37862f36.html'}}
    check(len(pages)==len(set(pages)) and set(pages)==expected_pages,'Sitemap must expose every canonical destination exactly once')
    parsed={}
    for page in pages:
        check((ROOT/page).is_file(),'Missing canonical page '+page)
        if not (ROOT/page).is_file():continue
        parsed[page]=Tags((ROOT/page).read_text(encoding='utf8'))
        check(any(t=='link' and a.get('rel')=='canonical' for t,a in parsed[page].tags),'Missing canonical link '+page)
    manifest_path=ROOT/'docs/sitewide-artwork-review.json'
    if not manifest_path.exists(): errors.append('Reviewed image manifest missing; incomplete review cannot pass'); heroes=[]
    else:
        manifest=json.loads(manifest_path.read_text(encoding='utf8'));heroes=manifest.get('heroes',[])
        check(manifest.get('baseline')==baseline,'Manifest baseline mismatch')
        errors.extend(unique_reviewed(heroes,set(manifest.get('rejected_sha256',[]))))
    check(len(heroes)==19,'Require all 19 reviewed replacement heroes')
    expected={p['page'] for p in plan['plans']}; check(len(expected)==19,'Production plan must contain 19 destinations')
    check({h['page'] for h in heroes}==expected,'Reviewed heroes do not cover production plan')
    check(len({h['key'] for h in heroes})==len(heroes),'Hero keys must be unique')
    decoded_seen={}
    rejected=set(manifest.get('rejected_sha256',[])) if manifest_path.exists() else set()
    for h in heroes:
        page=h['page']; key=h['key']; tags=parsed.get(page);check(tags is not None,key+': not canonical')
        if tags is None:continue
        anchors=[a for t,a in tags.tags if t=='a' and 'data-hero-viewer' in a]
        check(len(anchors)==1,key+': require one hero trigger')
        if not anchors:continue
        a=anchors[0];check(a.get('data-hero-record')=='topic-'+key,key+': mismatched hero record')
        check('fc-topic-unique-hero' in a.get('class','').split(),key+': missing scoped hero class')
        resolved=(ROOT/page).parent/unquote(urlsplit(a.get('href','')).path)
        check(resolved.resolve()==(ROOT/h['asset']).resolve(),key+': hero does not use reviewed full asset')
        check(h.get('technical_review_passed') is True,key+': technical visual review incomplete')
        for field in ('identity','realism','gaze','anatomy','history','responsive'):
            check(bool(h.get('review',{}).get(field)),key+': missing '+field+' review evidence')
        for field,hashfield in [('asset','sha256'),('desktop','desktop_sha256'),('mobile','mobile_sha256')]:
            path=ROOT/h[field];check(path.is_file(),key+': missing '+field)
            if path.is_file():
                digest=sha(path);check(digest==h.get(hashfield),key+': '+field+' bytes differ from reviewed hash')
                check(digest not in rejected,key+': rejected '+field+' hash')
                if field=='asset':
                    from PIL import Image
                    with Image.open(path) as image:
                        pixels=image.convert('RGBA');pixelhash=hashlib.sha256(str(pixels.size).encode()+pixels.tobytes()).hexdigest()
                    check(pixelhash not in decoded_seen,key+': decoded pixels duplicate '+decoded_seen.get(pixelhash,''))
                    decoded_seen[pixelhash]=key
        original=Path(h.get('source_file',''))
        if not original.is_absolute(): original=ROOT/original
        check(original.is_file(),key+': original source file missing for provenance check')
        if original.is_file():check(sha(original)==h.get('source_sha256'),key+': original source hash mismatch')
        study=urlsplit(h['study']);check(study.path.lstrip('/')==page and bool(study.fragment),key+': study must target own page anchor')
        check(any(a.get('id')==study.fragment for t,a in tags.tags),key+': missing study anchor')
        ask=urlsplit(h['ask']);query=parse_qs(ask.query)
        check(ask.path.rstrip('/').endswith('ask.html') and ask.fragment=='ask-question',key+': invalid contextual Ask route')
        check(bool(query.get('topic')),key+': missing Ask topic')
        check(urlsplit(query.get('return',[''])[0]).path.lstrip('/')==page,key+': Ask return does not target own page')
        style=a.get('style','')
        for variable,asset in [('--topic-hero-desktop',h['desktop']),('--topic-hero-mobile',h['mobile'])]:
            match=re.search(re.escape(variable)+r"\s*:\s*url\(['\"]?([^)'\"]+)",style)
            check(bool(match),key+': missing '+variable)
            if match:check(((ROOT/page).parent/match.group(1)).resolve()==(ROOT/asset).resolve(),key+': wrong '+variable)
    # Added CSS must be scoped and must not alter width/height/frame geometry.
    # The focused-study additions have a separate, closed visual-review baseline.
    # Exempt only the exact reviewed bytes, never arbitrary later edits to this file.
    focused=json.loads((ROOT/'tools/focused_answers_baseline.json').read_text(encoding='utf8'))
    reviewed=focused['reviewed_stylesheets']
    check(set(reviewed)=={'focused-answers.css'}, 'Unexpected focused stylesheet exemption')
    for name,digest in reviewed.items():
        check(sha(ROOT/name)==digest, 'Focused stylesheet differs from reviewed bytes: '+name)
    # The separately reviewed Book of Mormon directory owns this exact stylesheet.
    # Keep the hero geometry gate closed to every other file and later CSS edit.
    bom_style = 'bom-story-journey.css'
    pioneer_style = 'pioneer-story.css'
    pioneer_ask_style = 'pioneer-experience.css'
    # Independently reviewed study-body and Answers-directory styles, no hero rules.
    settle_style = 'settle-heart-study.css'
    row_style = 'complete-card-rows.css'
    # Independently reviewed Bible study-body layout only; no hero-rule exemption
    # survives a byte change or consumption outside its single owning page.
    check(reviewed_bible_style((ROOT/BIBLE_STYLE).read_bytes()),
          'Bible study stylesheet differs from reviewed bytes')
    # The complete journey has its own independently reviewed reading layout.
    # Bind this exception to exact bytes and the parent, Birth, and76 planned descendants.
    check(reviewed_journey_style((ROOT/JOURNEY_STYLE).read_bytes()),
          'Jesus journey stylesheet differs from reviewed bytes')
    journey_pages=json.loads((ROOT/'docs/jesus-journey/pages.json').read_text(encoding='utf8'))
    journey_owners={p['url'].lstrip('/') for p in journey_pages}
    check(len(journey_owners)==76 and all(p.startswith('jesus-christ/') and p.endswith('.html') for p in journey_owners),
          'Journey stylesheet ownership differs from76 nested study pages')
    journey_owners.update({'answers/jesus-christ-latter-day-saint-beliefs.html','birth-of-christ.html'})
    check(len(journey_owners)==78, 'Journey stylesheet must have exactly78 reviewed consumers')
    check(sha(ROOT/row_style)=='7f72f430deae755a59e9f0cdf60c3d6b68c214b8421feac28e548c8f07a32941',
          'Reviewed complete card row stylesheet changed')
    check(sha(ROOT/settle_style)=='ef58ca8c056db359667b85bf697ece78cc54a496e082b9a44f7a283e0d0fc5a2',
          'Settle study stylesheet differs from reviewed bytes')
    # Owner-requested two-column topics and Ask presentation were reviewed
    # separately from hero artwork. Permit these exact bytes, not later CSS edits.
    check(sha(ROOT/pioneer_ask_style)=='7f67cd77c23157019cd4cb609f2ff0b7151b9a503e143dd692337f41aed919d8',
          'Pioneer Ask stylesheet differs from reviewed bytes')
    check(sha(ROOT/pioneer_style)=='1255d1628391a932385df5d5667242abf48cff108ebd62938670606829168ad3',
          'Pioneer stylesheet differs from reviewed bytes')
    check(sha(ROOT/bom_style)=='9c1963e6981ec14114ee08da6230c26048ea491177936599d1e8050da4f6be9f',
          'Book of Mormon stylesheet differs from reviewed bytes')
    # The standalone review desk has its own document; its stylesheet must never
    # be loaded by visitor pages or imported by a site stylesheet.
    tool_style = 'tools/anatomy-review/style.css'
    for path in [*ROOT.rglob('*.html'), *ROOT.rglob('*.css'), *ROOT.rglob('*.js')]:
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(('tools/', '.git/', 'node_modules/', 'focuschrist-repo/')):
            continue
        check('anatomy-review' not in path.read_text(encoding='utf8'),
              'Visitor asset references standalone anatomy review tool: '+relative)
        if relative != 'missionary.html':
            check('missionary.css' not in path.read_text(encoding='utf8'),
                  'Mission stylesheet referenced outside its owning page: '+relative)
        check(mission_enrichment_style_reference_allowed(relative, path.read_text(encoding='utf8')),
              'Mission enrichment stylesheet referenced outside its single owning page: '+relative)
        check(watch_shorts_style_reference_allowed(relative, path.read_text(encoding='utf8')),
              'Watch Shorts stylesheet referenced outside its single owning page: '+relative)
        check(home_style_reference_allowed(relative, path.read_text(encoding='utf8')),
              'Home presentation stylesheet referenced outside its single owning page: '+relative)
        check(bible_style_reference_allowed(relative, path.read_text(encoding='utf8')),
              'Bible study stylesheet referenced outside its owning page: '+relative)
        check(journey_style_reference_allowed(relative, path.read_text(encoding='utf8'), journey_owners),
              'Journey stylesheet referenced outside its owning pages: '+relative)
        if relative != 'answers/what-is-the-book-of-mormon.html':
            check(bom_style not in path.read_text(encoding='utf8'),
                  'Book of Mormon stylesheet referenced outside its owning page: '+relative)
        if relative not in {'answers.html', 'answers/settle-this-in-your-hearts.html', settle_style}:
            check(settle_style not in path.read_text(encoding='utf8'),
                  'Settle stylesheet referenced outside reviewed destinations: '+relative)
        if relative != 'pioneers.html':
            check(pioneer_style not in path.read_text(encoding='utf8'),
                  'Pioneer stylesheet referenced outside its owning page: '+relative)
    # Owner-directed mobile framing and menu-wrap repair; exact reviewed bytes only.
    check(sha(ROOT/'site-system.css')=='b1dcd1c1bc1ab585f0803af31ad8d56789a4f2e07202c4bfb59ab0849656a0e1', 'Reviewed mobile polish stylesheet changed: site-system.css')
    check(sha(ROOT/'site-header.css')=='4684f655bae604a41d00fdf45f67d1f6d24ae02ac4e5760987f42691b0ee4d24', 'Reviewed mobile polish stylesheet changed: site-header.css')
    check(reviewed_home_style((ROOT/HOME_STYLE).read_bytes()), 'Home presentation stylesheet differs from exact reviewed bytes')
    check(sha(ROOT/'missionary.css') == BOUNDARY_WRAP_STYLES['.fc-missionary-page main'][1],
          'Mission purpose stylesheet differs from exact reviewed bytes')
    check(reviewed_watch_shorts_style((ROOT/WATCH_SHORTS_STYLE).read_bytes()), 'Watch Shorts stylesheet differs from exact reviewed bytes')
    check(reviewed_mission_enrichment_style((ROOT/MISSION_ENRICHMENT_STYLE).read_bytes()), 'Mission enrichment stylesheet differs from exact reviewed bytes')
    excluded_styles={MISSION_ENRICHMENT_STYLE,WATCH_SHORTS_STYLE,'missionary.css',HOME_STYLE,'focused-answers.css',tool_style,bom_style,pioneer_style,pioneer_ask_style,settle_style,row_style,BIBLE_STYLE,JOURNEY_STYLE,'site-system.css','site-header.css'}
    diff=subprocess.check_output(['git','diff',baseline,'--','*.css',*[':(exclude)'+name for name in sorted(excluded_styles)]],cwd=ROOT,text=True)
    additions='\n'.join(line[1:] for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++'))
    # Include newly created CSS before staging, too.
    for name in subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','*.css'],cwd=ROOT,text=True).splitlines():
        if name not in excluded_styles:
            additions += '\n' + (ROOT/name).read_text(encoding='utf-8')
    for selector,body in re.findall(r'([^{}]+)\{([^{}]*)\}',re.sub(r'/\*.*?\*/','',additions,flags=re.S)):
        if selector.strip().startswith('@'):continue
        if selector.strip() in MISSION_PURPOSE_RULES:
            check(reviewed_mission_purpose(selector, body, (ROOT/'missionary.css').read_bytes()),
                  'Mission purpose rule differs from exact reviewed properties/stylesheet bytes')
            continue
        if selector.strip() in BOUNDARY_WRAP_STYLES:
            filename, _ = BOUNDARY_WRAP_STYLES[selector.strip()]
            check(reviewed_boundary_wrap(selector, body, (ROOT/filename).read_bytes()),
                  'Boundary text wrapping differs from exact reviewed selector/property/stylesheet bytes')
            continue
        # Separate owner-authorized mobile opening and Conference banner review.
        # Exact file hashes prevent this scoped acceptance from admitting later edits.
        if selector.strip()=='body.fc-site.cfm-page .cfm-hero::before' and body.strip()=='background-position:center 25%':
            check(sha(ROOT/'come-follow-me.css')=='d550f16a7f3708e638522d46acd65dfbce8ae74fcb516b28ac0bf2c639822984',
                  'Come Follow Me mobile focal point differs from reviewed bytes')
            continue
        if selector.strip().startswith('.gc-page .gc-page-opening'):
            check(sha(ROOT/'general-conference-section.css')=='83b30800abdb31ff894314897030e7d7f8d469136267c00eea275dbed53cabe3',
                  'Conference opening CSS differs from reviewed bytes')
            continue
        if selector.strip()=='body.fc-site' and body.strip()=='--fc-opening-hero-height: clamp(320px, 44svh, 420px);':
            check(sha(ROOT/'site-system.css')=='b1dcd1c1bc1ab585f0803af31ad8d56789a4f2e07202c4bfb59ab0849656a0e1',
                  'Mobile opening CSS differs from reviewed bytes')
            continue
        dropdown_selectors = {
            '.nav[data-focuschrist-header="standard"] .hamburger-menu a:focus-visible',
            '.nav[data-focuschrist-header="standard"] .hamburger-menu a[aria-current="page"]',
            '.nav[data-focuschrist-header="standard"] .hamburger-menu a.active',
        }
        if all(part.strip() in dropdown_selectors for part in selector.split(',')):
            check(sha(ROOT/'site-header.css')=='4684f655bae604a41d00fdf45f67d1f6d24ae02ac4e5760987f42691b0ee4d24',
                  'Dropdown stylesheet differs from reviewed gold-menu bytes')
            check(all(prop in {'outline-offset','border-radius','box-shadow','font-weight'}
                      for prop in re.findall(r'([a-z-]+)\s*:',body)),
                  'Dropdown focus/current rule changes unexpected properties')
            continue
        navigation_fallback = all('.nav[data-focuschrist-header="standard"].fc-nav-compact' in part and '.nav-links' in part or '.nav[data-focuschrist-header="standard"].fc-nav-compact .fc-nav-side' in part for part in selector.split(','))
        if navigation_fallback:
            # The separately reviewed collision fix affects navigation only.
            allowed_nav = {'display', 'max-width', 'min-width', 'white-space', 'text-align'}
            properties = re.findall(r'([a-z-]+)\s*:', body)
            check(all(prop in allowed_nav for prop in properties), 'Navigation fallback changes unexpected properties')
            check('fc-visual-hero' not in selector, 'Navigation fallback must not target a hero')
            continue
        check(all('.fc-topic-unique-hero' in s for s in selector.split(',')),'Added CSS escapes scoped hero class: '+selector.strip())
        image_layer = all(part.strip().endswith('::before') for part in selector.split(','))
        dimensions = re.findall(r'(?<![\w-])(height|min-height|max-height|width|min-width|max-width|aspect-ratio|padding|margin)\s*:\s*([^;]+)', body)
        allowed_image_dimensions = {'width': '100%', 'height': '100%', 'max-width': 'none'}
        check(all(image_layer and allowed_image_dimensions.get(prop) == value.strip() for prop,value in dimensions),'Added hero CSS changes frame geometry')
    print(json.dumps({'canonical_pages':len(pages),'reviewed_heroes':len(heroes),'protected_images_checked':len(preserved),'errors':errors},indent=2))
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
