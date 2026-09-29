#!/usr/bin/env python3
"""Static release gate for the sitewide hero review. Does not grant visual/owner approval."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
import argparse, hashlib, json, re, subprocess, sys, xml.etree.ElementTree as ET
from cfm_composition_qa import check as composition_check, self_test as composition_self_test
from anchor_alignment_qa import FILES as ANCHOR_STYLES, historical_style_bytes, reviewed_anchor_style, self_test as anchor_self_test
ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXT = {'.png','.webp','.jpg','.jpeg','.avif','.gif','.svg'}
BIBLE_STYLE = 'bible-together.css'
BIBLE_STYLE_SHA256 = '128b2a54bf1a285497ea11d6c8e9040c55baa996ec75aa376b29463f854a9121'
BIBLE_STYLE_OWNER = 'answers/bible-and-book-of-mormon-together.html'
MISSION_ENRICHMENT_STYLE = 'missionary-enrichment.css'
MISSION_ENRICHMENT_STYLE_SHA256 = 'e40315cfc4994ba862cd7bf3c1d4f0fa77db5bd1ba59d8ca0eedfd8cdd8b875c'
WATCH_SHORTS_STYLE = 'watch-shorts.css'
# Owner-requested three-Short disclosure; centered 310px cards and controls,
# independently checked on desktop and enlarged phone text. Exact Watch-only bytes.
WATCH_SHORTS_STYLE_SHA256 = '1feb6892f74ca30d8ec52af3f76e8da197d2bac2cc61716838cf87fe6efd24b6'
HOME_STYLE = 'home-presentation.css'
HOME_STYLE_SHA256 = 'a3a6331971ae7a289b5cad3c3e5c16e947a0dfada2c0325f1e6b9abc87466282'
HOME_STYLE_OWNER = 'index.html'
JOURNEY_STYLE = 'jesus-journey.css'
JOURNEY_STYLE_SHA256 = '165bea932d4ca288c9ade8327e5d5999798be4c41f17c4627bf1bdd8c74790c0'
ANSWERS_FEATURED_STYLE_SHA256 = '3f3ab5babea5aadf5ddd79655922bd29b7f4c8b1aa74742b1146eccfca7caa87'
# Owner-requested featured and foundational study links. Only the listed rules in
# the exact reviewed stylesheet qualify; the 700px stack is pinned by its hash.
ANSWERS_FEATURED_RULES = {
    '.fc-answers-jumps .fc-settle-directory-intro': {'display:grid;grid-template-columns:minmax(0,1fr);gap:20px;'},
    '.fc-answers-jumps .fc-answers-jump-links': {'grid-template-columns:minmax(0,1fr);', 'grid-template-columns:repeat(2,minmax(0,1fr));', 'grid-template-columns:repeat(12,minmax(0,1fr));'},
    '.fc-answers-jumps .fc-answers-jump-links > a': {'grid-column:span3;', 'grid-column:auto;'},
    '.fc-answers-jumps .fc-answers-jump-links > a:last-child:nth-child(odd)': {'grid-column:1/-1;'},
    '.fc-answers-jump-panel > .fc-resource-next': {'display:grid;gap:14px;margin:0;padding-top:20px;border-top:1pxsolidrgba(240,195,106,.25);text-align:center;'},
    '.fc-answers-jump-panel [data-foundational-study-actions]': {'grid-template-columns:minmax(0,1fr);', 'display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:0;width:100%;'},
    '.fc-answers-jump-panel [data-foundational-study-actions] > a': {'width:100%;text-align:center;'},
    '.fc-answers-jumps .fc-answers-featured-pair': {
        'display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;flex:1136rem;min-width:0;',
        'grid-template-columns:minmax(0,1fr);',
        'grid-template-columns:repeat(2,minmax(0,1fr));',
    },
    '.fc-answers-jumps .fc-answers-featured-pair > a': {
        'width:100%;max-width:none;min-width:0;box-sizing:border-box;white-space:normal;overflow-wrap:anywhere;height:auto;line-height:1.5;',
    },
}

def reviewed_answers_featured(selector, body, data):
    data = historical_style_bytes(data)
    return (re.sub(r'\s+', '', body) in ANSWERS_FEATURED_RULES.get(selector.strip(), set())
            and hashlib.sha256(data).hexdigest() == ANSWERS_FEATURED_STYLE_SHA256)

def reviewed_art_reflection(selector, body, data):
    data = historical_style_bytes(data)
    return selector.strip() == '.fc-art-study-page .fc-reflection-prompts > .fc-art-story' and re.sub(r'\s+', '', body) == 'max-width:none!important;' and hashlib.sha256(data).hexdigest() == '557ff4b1825bdf655751cbc6491d0133db294f022b90fcda270039ff849053a3'

def reviewed_wrap_consumers(consumers, expected, version):
    return (set(consumers) == set(expected) | {'answers/holy-ghost.html', 'answers/plan-of-salvation.html'} and len(consumers) == 122
            and all(parse_qs(urlsplit(ref).query).get('v') == [version] for refs in consumers.values() for ref in refs))


def reviewed_system_panel_style(data):
    data = historical_style_bytes(data)
    # Owner-directed surface appendix only. Existing hero/mobile rules retain
    # their exact reviewed prefix; both the prefix and full file are pinned.
    return (hashlib.sha256(data).hexdigest() == '6bcb9b6bd26ee85d8afa47ff1f1631430f191fdd3c3e6414937909858fec480b'
            and hashlib.sha256(data[:58704]).hexdigest() == '7b7ba6dd6b273f0fd4fb0302049ce304bf87dac133a2dd852fe4d548ad293984')

def reviewed_mission_enrichment_style(data):
    data = historical_style_bytes(data)
    return hashlib.sha256(data).hexdigest() == MISSION_ENRICHMENT_STYLE_SHA256

def mission_enrichment_style_reference_allowed(relative, text):
    return relative == "missionary.html" or MISSION_ENRICHMENT_STYLE not in text

def reviewed_watch_shorts_style(data):
    data = historical_style_bytes(data)
    return hashlib.sha256(data).hexdigest() == WATCH_SHORTS_STYLE_SHA256

def watch_shorts_style_reference_allowed(relative, text):
    return relative == "watch.html" or WATCH_SHORTS_STYLE not in text

def reviewed_home_style(data):
    data = historical_style_bytes(data)
    return hashlib.sha256(data).hexdigest() == HOME_STYLE_SHA256

def home_style_reference_allowed(relative, text):
    return relative == HOME_STYLE_OWNER or HOME_STYLE not in text

def reviewed_bible_style(data):
    data = historical_style_bytes(data)
    return hashlib.sha256(data).hexdigest() == BIBLE_STYLE_SHA256

def bible_style_reference_allowed(relative, text):
    return relative == BIBLE_STYLE_OWNER or BIBLE_STYLE not in text

def reviewed_journey_style(data):
    data = historical_style_bytes(data)
    return hashlib.sha256(data).hexdigest() == JOURNEY_STYLE_SHA256

def journey_style_reference_allowed(relative, text, owners):
    return relative in owners or JOURNEY_STYLE not in text

BOUNDARY_WRAP_STYLES = {'.fc-history-page main': ('church-history.css', '5b7e4c13945dcae80da5c278192b2d846e1d03f31aa4eeb4de133fa697613937'), '.fc-missionary-page main': ('missionary.css', '1fc685047557e7d077b8c25c833731dca799335add20d3b139cf626f72357e21')}

def reviewed_boundary_wrap(selector, body, data):
    data = historical_style_bytes(data)
    entry = BOUNDARY_WRAP_STYLES.get(selector.strip())
    return bool(entry and re.sub(r"\s+", "", body) == "overflow-wrap:anywhere;" and hashlib.sha256(data).hexdigest() == entry[1])

MISSION_PURPOSE_RULES = {
    '.fc-missionary-purpose .fc-missionary-visual figcaption': 'position:static;padding:16px24px;background:transparent;',
    '.fc-missionary-purpose .fc-missionary-copy > .fc-section-heading': 'max-width:none;',
}

def reviewed_mission_purpose(selector, body, data):
    data = historical_style_bytes(data)
    return (selector.strip() in MISSION_PURPOSE_RULES
            and re.sub(r'\s+', '', body) == MISSION_PURPOSE_RULES[selector.strip()]
            and hashlib.sha256(data).hexdigest() == BOUNDARY_WRAP_STYLES['.fc-missionary-page main'][1])

class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.feed(text)
    def handle_starttag(self, tag, attrs): self.tags.append((tag,dict(attrs)))

# Exact narrow title/mini-card appendices. Search base additionally includes the
# independently reviewed intrinsic trigger width, nowrap label and fixed-size icon;
# M063 removes only the mobile title/second-row rules, retaining the first-row grid.
# Full-file and updated base-prefix pins both apply.
NARROW_READING_STYLES = {'site-search.css': {'base_bytes': 4716, 'base_sha256': '13550e00846fb8c2a81204d71fb3e131c71e3e9f74f0fa94791bbc1e8a5e0492', 'sha256': 'ca09d2ce90471be8c404efc4c8a27aeb756fdc1d30276aa3d112705595ffa32e'}, 'watch-experience.css': {'base_bytes': 12132, 'base_sha256': '3dfc3ac65f176f0c3c3f8c21dbb5c504f4d9dee1302074f6c396790982446a53', 'sha256': 'ec9e99bdb5c0e39daa0b59c65866b1cbd09ed6b451ffafc15f76b60778846f3e'}}
def reviewed_narrow_reading_style(name, data):
    data = historical_style_bytes(data)
    entry=NARROW_READING_STYLES.get(name)
    return bool(entry and hashlib.sha256(data).hexdigest()==entry["sha256"]
                and hashlib.sha256(data[:entry["base_bytes"]]).hexdigest()==entry["base_sha256"])

# Owner-authorized toolbar readability; exact bytes do not exempt future style edits.
TOOLBAR_STYLE_SHA256 = {'site-header.css': 'a915de3ba44c8e14f127e25ec51498960fb1f108990a837d1cc366f8841d1b9f', 'study-navigation.css': '316f49fbd8a3d7f1cedcdf48389c738749ab5904ffd5723c0a68759adb080972'}

# Owner-requested growing Ask composer and opt-in Holy Ghost player, independently
# reviewed in source and rendered by Albert. Exact full bytes and single owners.
SCOPED_INTERFACE_STYLES = {
    'plan-of-salvation.css': ('214c7c4c54c67b58c986d311e2bcb69a02bda9ab19427ba26f6bef433c8105bc', 'answers/plan-of-salvation.html'),
    'come-follow-me.css': ('4ac596b6c1d0c165636f0e965794a9939a34c8333501b5bad64fad103b1bd7be', 'come-follow-me.html'),
    'cfm-study-controls.css': ('35c8939f4fc950d241ecb6a62ac58c1be6e02a59f64bee9b19fd2704011b58fb', 'come-follow-me.html'),
    'ask-experience.css': ('62b8578e09c01fc8bd6eb4b46de4337a39aaa33280c8ba6b51606f57481d6df6', 'ask.html'),
    'holy-ghost-video.css': ('1fd7cb06db86e03a95cdc1a0420535d73fab5ddda5e2533e06b61613a5efae50', 'answers/holy-ghost.html'),
}
# Wyatt requested these exact desktop repairs and the Temple chronology.
# Albert independently reviewed rendered composition; byte/consumer changes fail closed.
OWNER_20260929_STYLES = {
    'desktop-hero-repairs.css': ('26af1b820ab62722ad60ab124f16ccf5784304edafa375a854f0ea7f076e9e96', ['answers/abrahamic-covenant.html', 'answers/look-unto-me-doctrine-and-covenants-6-36.html', 'answers/plan-of-salvation.html', 'book-of-mormon-evidences.html', 'general-conference.html']),
    'temples-history.css': ('55e75a39ef5e01699307df18932ac7dd83771216cd144fb59c119b4b1e9da030', ['answers/why-latter-day-saints-build-temples.html']),
}
def reviewed_owner_20260929_style(name, data):
    return name in OWNER_20260929_STYLES and hashlib.sha256(data).hexdigest() == OWNER_20260929_STYLES[name][0]

# Exact owner-requested picture-source pill correction; removing only this
# declaration/comment must recover the prior stylesheet bytes. No global waiver.
PICTURE_PILL_ADDITION = b"    /* Picture-panel sources share the standard pill radius, including wrapped labels. */\n    --fc-study-control-radius: 999px;\n"
def reviewed_picture_pill_style(data):
    return (hashlib.sha256(data).hexdigest() == '7b0c502eef4f5e5c2db7b984ce76334a1ce02cda34a861bb6a3a99075b497678'
            and data.count(PICTURE_PILL_ADDITION) == 1
            and hashlib.sha256(data.replace(PICTURE_PILL_ADDITION, b'', 1)).hexdigest() == '094e3c7c814476bc17653435b36de4fff53ed970fd25e3635f887717961b5714')

def reviewed_scoped_interface_style(name, data):
    data = historical_style_bytes(data)
    return name in SCOPED_INTERFACE_STYLES and hashlib.sha256(data).hexdigest()==SCOPED_INTERFACE_STYLES[name][0]
def scoped_interface_reference_allowed(name, relative, text):
    return relative==SCOPED_INTERFACE_STYLES[name][1] or name not in text

def reviewed_toolbar_style(name, data):
    data = historical_style_bytes(data)
    return name in TOOLBAR_STYLE_SHA256 and hashlib.sha256(data).hexdigest() == TOOLBAR_STYLE_SHA256[name]

def sha(path): return hashlib.sha256(historical_style_bytes(path.read_bytes())).hexdigest()
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
    composition_check()
    if args.self_test:
        anchor_self_test()
        answers_css = (ROOT/'answers-hero.css').read_bytes()
        for selector, bodies in ANSWERS_FEATURED_RULES.items():
            for body in bodies:
                assert reviewed_answers_featured(selector, body, answers_css)
                assert not reviewed_answers_featured('.unknown-selector', body, answers_css)
                assert not reviewed_answers_featured(selector, body, answers_css + b'\n.fc-answers-jumps .fc-answers-jump-links > a:nth-last-child(-n+3){grid-column:span 4;}')
                assert not reviewed_answers_featured(selector, body + 'height:9px;', answers_css)
                assert not reviewed_answers_featured(selector, body, answers_css.replace(b'max-width: 700px', b'max-width: 900px'))
                assert not reviewed_answers_featured(selector, body, answers_css + b'\n.fc-visual-hero{height:9px}')
        good=[{'key':'a','source_sha256':'1'*64,'sha256':'2'*64},{'key':'b','source_sha256':'3'*64,'sha256':'4'*64}]
        assert not unique_reviewed(good,set())
        duplicate=[good[0],dict(good[1],source_sha256='1'*64)]
        assert any('duplicate source_sha256' in e for e in unique_reviewed(duplicate,set()))
        assert any('rejected sha256' in e for e in unique_reviewed(good,{'2'*64}))
        for name in TOOLBAR_STYLE_SHA256:
            toolbar_css = (ROOT/name).read_bytes()
            assert reviewed_toolbar_style(name, toolbar_css)
            assert not reviewed_toolbar_style(name, toolbar_css + b'\n.fc-visual-hero{height:9px}')
            assert not reviewed_toolbar_style('unreviewed.css', toolbar_css)
        wrap_expected = [f'page-{i}.html' for i in range(120)]
        panel_style = (ROOT/'site-system.css').read_bytes()
        assert reviewed_system_panel_style(panel_style)
        assert not reviewed_system_panel_style(panel_style + b'\n.fc-visual-hero{height:9px}')
        assert not reviewed_system_panel_style(panel_style.replace(b'--fc-panel-fill:', b'--fc-panel-broken:', 1))
        assert not reviewed_system_panel_style(panel_style.replace(b'--fc-opening-hero-height:', b'--fc-opening-broken-height:', 1))
        wrap_good = {name: ['site-system.css?v=current'] for name in [*wrap_expected, 'answers/holy-ghost.html', 'answers/plan-of-salvation.html']}
        assert reviewed_wrap_consumers(wrap_good, wrap_expected, 'current')
        assert not reviewed_wrap_consumers(dict(list(wrap_good.items())[1:]), wrap_expected, 'current')
        assert not reviewed_wrap_consumers(dict(wrap_good, **{'other.html': ['site-system.css?v=current']}), wrap_expected, 'current')
        assert not reviewed_wrap_consumers(dict(wrap_good, **{'page-0.html': ['site-system.css?v=stale']}), wrap_expected, 'current')
        assert not reviewed_wrap_consumers(dict(wrap_good, **{'page-0.html': ['site-system.css?v=current-extra']}), wrap_expected, 'current')
        art_css = (ROOT/'art-study-enrichment.css').read_bytes()
        art_selector = '.fc-art-study-page .fc-reflection-prompts > .fc-art-story'
        assert reviewed_art_reflection(art_selector, 'max-width:none !important;', art_css)
        assert not reviewed_art_reflection(art_selector, 'max-width:none !important; height:9px;', art_css)
        assert not reviewed_art_reflection('.fc-visual-hero', 'max-width:none !important;', art_css)
        assert not reviewed_art_reflection(art_selector, 'max-width:none !important;', art_css + b' ')
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
        assert b'flex: 0 1 310px' in shorts_css
        assert not reviewed_watch_shorts_style(shorts_css.replace(b'flex: 0 1 310px', b'flex: 1 1 100%'))
        assert b'justify-content: center' in shorts_css
        assert not reviewed_watch_shorts_style(shorts_css.replace(b'justify-content: center', b'justify-content: flex-start'))
        assert watch_shorts_style_reference_allowed('watch.html', WATCH_SHORTS_STYLE)
        assert not watch_shorts_style_reference_allowed('index.html', WATCH_SHORTS_STYLE)
        assert not watch_shorts_style_reference_allowed('shared.css', '@import "' + WATCH_SHORTS_STYLE + '";')
        assert not watch_shorts_style_reference_allowed('shared.js', WATCH_SHORTS_STYLE)
        home_css = (ROOT/HOME_STYLE).read_bytes()
        assert reviewed_home_style(home_css)
        assert not reviewed_home_style(home_css.replace(b'position:static;padding:16px 17px', b'position:absolute;padding:16px 17px'))
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
        composition_self_test()
        for name in NARROW_READING_STYLES:
            data=(ROOT/name).read_bytes()
            assert reviewed_narrow_reading_style(name,data)
            assert not reviewed_narrow_reading_style(name,data+b"body{display:none}")
            assert not reviewed_narrow_reading_style(name,b"X"+data[1:])
        cfm_controls=(ROOT/'cfm-study-controls.css').read_bytes()
        assert not reviewed_scoped_interface_style('cfm-study-controls.css', cfm_controls.replace(b'text-transform:none', b'text-transform:uppercase'))
        assert not reviewed_scoped_interface_style('cfm-study-controls.css', cfm_controls.replace(b'--fc-study-control-radius:6px', b'--fc-study-control-radius:999px'))
        ask_css=(ROOT/'ask-experience.css').read_bytes()
        assert not reviewed_scoped_interface_style('ask-experience.css', ask_css.replace(b'position:static;padding:16px 17px', b'position:absolute;padding:16px 17px'))
        for name in OWNER_20260929_STYLES:
            data = (ROOT/name).read_bytes()
            assert reviewed_owner_20260929_style(name, data)
            assert not reviewed_owner_20260929_style(name, data+b'\n.x{height:1px}')
            assert not reviewed_owner_20260929_style('unrelated.css', data)
            assert 'unrelated.html' not in OWNER_20260929_STYLES[name][1]
        for name, (_, owner) in SCOPED_INTERFACE_STYLES.items():
            data=(ROOT/name).read_bytes()
            assert reviewed_scoped_interface_style(name,data)
            assert not reviewed_scoped_interface_style(name,data+b'\n.x{height:1px}')
            assert scoped_interface_reference_allowed(name,owner,name)
            assert not scoped_interface_reference_allowed(name,'unrelated.html',name)
        search_css = (ROOT/"site-search.css").read_bytes()
        assert b"width:max-content;white-space:nowrap;" in search_css
        assert not reviewed_narrow_reading_style("site-search.css", search_css.replace(b"white-space:nowrap;", b"", 1))
        assert not reviewed_narrow_reading_style("site-search.css", search_css.replace(b'> .nav-links {display:none!important;}', b'> .nav-links {display:block!important;}', 1))
        journey_css = (ROOT/JOURNEY_STYLE).read_bytes()
        owners = {'answers/jesus-christ-latter-day-saint-beliefs.html','jesus-christ/before-bethlehem.html','birth-of-christ.html','answers/abrahamic-covenant.html'}
        assert reviewed_journey_style(journey_css)
        assert not reviewed_journey_style(journey_css + b'\n.fc-topic-unique-hero{height:999px}\n')
        assert journey_style_reference_allowed('jesus-christ/before-bethlehem.html', JOURNEY_STYLE, owners)
        assert journey_style_reference_allowed('answers/jesus-christ-latter-day-saint-beliefs.html', JOURNEY_STYLE, owners)
        assert journey_style_reference_allowed('birth-of-christ.html', JOURNEY_STYLE, owners)
        assert journey_style_reference_allowed('answers/abrahamic-covenant.html', JOURNEY_STYLE, owners)
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
    journey_owners.update({'answers/jesus-christ-latter-day-saint-beliefs.html','birth-of-christ.html','answers/abrahamic-covenant.html','answers/holy-ghost.html','answers/plan-of-salvation.html','answers/god-our-heavenly-father.html'})
    check(len(journey_owners)==82, 'Journey stylesheet must have exactly82 reviewed consumers')
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
    wrap_review = json.loads((ROOT/'docs/large-text-wrap-independent-review-20260923.json').read_text(encoding='utf-8'))
    wrap_consumers = {}
    for path in ROOT.rglob('*.html'):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(('tools/', '.git/', 'node_modules/', 'focuschrist-repo/')): continue
        refs = re.findall(r'<link\b[^>]*href=[\"\']([^\"\']*site-system\.css[^\"\']*)', path.read_text(encoding='utf-8'))
        if refs: wrap_consumers[relative] = refs
    panel_contract = json.loads((ROOT/'docs/section-panel-surfaces.json').read_text(encoding='utf-8'))
    check(set(panel_contract['site_system_consumers']) == set(wrap_review['siteSystemConsumers']), 'Panel update changed protected shared stylesheet coverage')
    check(reviewed_wrap_consumers(wrap_consumers, panel_contract['site_system_consumers'], panel_contract['version']), 'Shared panel stylesheet consumer list or cache versions changed')
    art_owners = {'art-study/the-good-shepherd.html', 'art-study/the-living-christ.html', 'art-study/suffer-the-little-children.html', 'art-study/be-still.html'}
    art_consumers = {str(p.relative_to(ROOT)).replace('\\','/'): re.findall(r'art-study-enrichment\.css\?v=([^\"\\s>]+)', p.read_text(encoding='utf8')) for p in ROOT.rglob('*.html') if 'art-study-enrichment.css' in p.read_text(encoding='utf8')}
    check(set(art_consumers) == art_owners and all(v == ['20260927-anchor-alignment-1'] for v in art_consumers.values()), 'Art reflection stylesheet consumers/version differ')
    # Owner-directed mobile framing and menu-wrap repair; exact reviewed bytes only.
    check(reviewed_system_panel_style((ROOT/'site-system.css').read_bytes()), 'Reviewed base or exact owner-directed panel appendix changed: site-system.css')
    check(reviewed_toolbar_style('site-header.css', (ROOT/'site-header.css').read_bytes()), 'Reviewed mobile polish stylesheet changed: site-header.css')
    check(reviewed_toolbar_style('study-navigation.css', (ROOT/'study-navigation.css').read_bytes()), 'Study navigation differs from exact reviewed toolbar bytes')
    check(reviewed_home_style((ROOT/HOME_STYLE).read_bytes()), 'Home presentation stylesheet differs from exact reviewed bytes')
    check(sha(ROOT/'missionary.css') == BOUNDARY_WRAP_STYLES['.fc-missionary-page main'][1],
          'Mission purpose stylesheet differs from exact reviewed bytes')
    check(reviewed_watch_shorts_style((ROOT/WATCH_SHORTS_STYLE).read_bytes()), 'Watch Shorts stylesheet differs from exact reviewed bytes')
    check(reviewed_mission_enrichment_style((ROOT/MISSION_ENRICHMENT_STYLE).read_bytes()), 'Mission enrichment stylesheet differs from exact reviewed bytes')
    for name in SCOPED_INTERFACE_STYLES:
        check(reviewed_scoped_interface_style(name, (ROOT/name).read_bytes()), 'Scoped interface stylesheet bytes changed: '+name)
        for page in ROOT.rglob('*.html'):
            relative=page.relative_to(ROOT).as_posix()
            if relative.startswith(('tools/', '.git/', 'node_modules/', 'focuschrist-repo/')): continue
            check(scoped_interface_reference_allowed(name, relative, page.read_text(encoding='utf-8')), 'Scoped interface stylesheet consumed outside owner: '+relative)
    for name, (_, owners) in OWNER_20260929_STYLES.items():
        check(reviewed_owner_20260929_style(name, (ROOT/name).read_bytes()), 'Owner-reviewed stylesheet bytes changed: '+name)
        consumers = set()
        for page in ROOT.rglob('*.html'):
            relative = page.relative_to(ROOT).as_posix()
            if relative.startswith(('tools/', '.git/', 'node_modules/', 'focuschrist-repo/')): continue
            if name in page.read_text(encoding='utf-8'): consumers.add(relative)
        check(consumers == set(owners), 'Owner-reviewed stylesheet consumer set changed: '+name)
    for name in ANCHOR_STYLES:
        check(reviewed_anchor_style(name, (ROOT/name).read_bytes()), 'Anchor-only transformation differs from exact reviewed bytes: '+name)
    excluded_styles={MISSION_ENRICHMENT_STYLE,WATCH_SHORTS_STYLE,'missionary.css',HOME_STYLE,'focused-answers.css',tool_style,bom_style,pioneer_style,pioneer_ask_style,settle_style,row_style,BIBLE_STYLE,JOURNEY_STYLE,'site-system.css','site-header.css','study-navigation.css'}
    picture_pill_bytes = (ROOT/'artwork-actions.css').read_bytes()
    check(reviewed_picture_pill_style(picture_pill_bytes), 'Picture source pills differ from exact scoped reviewed change')
    check(not reviewed_picture_pill_style(picture_pill_bytes.replace(b'999px;', b'10px;', 1)), 'Picture pill radius mutation escaped')
    check(not reviewed_picture_pill_style(picture_pill_bytes+b'\n.x{height:1px}'), 'Unrelated picture stylesheet mutation escaped')
    excluded_styles.add('artwork-actions.css')
    excluded_styles.update(SCOPED_INTERFACE_STYLES)
    excluded_styles.update(OWNER_20260929_STYLES)
    # These files have just passed the exact full-byte AND reconstructed baseline
    # checks; no later geometry or non-margin changes can enter this exclusion.
    excluded_styles.update(ANCHOR_STYLES)
    diff=subprocess.check_output(['git','diff',baseline,'--','*.css',*[':(exclude)'+name for name in sorted(excluded_styles)]],cwd=ROOT,text=True)
    added_lines=[]; added_file=None
    for line in diff.splitlines():
        if line.startswith('+++ b/'):
            added_file=line[len('+++ b/'):]; continue
        if not line.startswith('+') or line.startswith('+++'): continue
        rule=line[1:]
        matches=re.findall(r'([^{}]+)\{([^{}]*)\}',rule)
        if added_file=='answers-hero.css' and len(matches)==1 and matches[0][0].strip() in ANSWERS_FEATURED_RULES:
            check(reviewed_answers_featured(*matches[0], (ROOT/'answers-hero.css').read_bytes()),
                  'Answers featured pair differs from exact reviewed selectors/properties/stylesheet bytes')
            continue
        if added_file in NARROW_READING_STYLES:
            check(reviewed_narrow_reading_style(added_file,(ROOT/added_file).read_bytes()), "Narrow reading CSS differs from exact reviewed appendix/prefix: "+added_file)
            continue
        added_lines.append(rule)
    additions='\n'.join(added_lines)
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
        if selector.strip() == '.fc-history-predictions button':
            check(re.sub(r'\s+', '', body) == 'flex:11 180px;min-width:0;white-space:normal;overflow-wrap:anywhere;'.replace(' ', '') and sha(ROOT/'church-history.css') == '5b7e4c13945dcae80da5c278192b2d846e1d03f31aa4eeb4de133fa697613937', 'History choice rows differ from exact reviewed properties/bytes')
            continue
        if selector.strip() in BOUNDARY_WRAP_STYLES:
            filename, _ = BOUNDARY_WRAP_STYLES[selector.strip()]
            check(reviewed_boundary_wrap(selector, body, (ROOT/filename).read_bytes()),
                  'Boundary text wrapping differs from exact reviewed selector/property/stylesheet bytes')
            continue
        if selector.strip() == '.fc-art-study-page .fc-reflection-prompts > .fc-art-story':
            check(reviewed_art_reflection(selector, body, (ROOT/'art-study-enrichment.css').read_bytes()), 'Art reflection width differs from exact reviewed rule/bytes')
            continue
        diagram_rules = {'.fc-bom-evidences .bom-visual-guide > a,\n.fc-bom-evidences .bom-visual-guide picture': 'display:block;', '.fc-bom-evidences .bom-visual-guide img': 'display:block;width:100%;height:auto;object-fit:contain;'}
        if selector.strip() in diagram_rules:
            check(re.sub(r'\s+', '', body) == diagram_rules[selector.strip()] and sha(ROOT/'bom-evidences.css') == '19b54d55057adeaa0373631a572482e3fdbe0acbcb053755c3b87d6bbda5046b', 'Evidences diagram CSS differs from exact reviewed rule/bytes')
            continue
        if selector.strip() == 'body.fc-site .cfm-paths > figure.cfm-path.fc-study-visual':
            check(re.sub(r'\s+', '', body) == 'display:flex;flex-direction:column;flex-wrap:nowrap' and sha(ROOT/'come-follow-me.css') == '97a1bb9d5d27a22126ce9f01c8140c53855b4ffae78f6327aa421792643099d3', 'CFM study card differs from exact reviewed vertical-flow rule/bytes')
            continue
        if selector.strip() == 'body.fc-site .cfm-paths > figure.cfm-path.fc-study-visual > :is(a,figcaption)':
            check(re.sub(r'\s+', '', body) == 'flex:01auto;min-width:0;width:100%' and sha(ROOT/'come-follow-me.css') == '97a1bb9d5d27a22126ce9f01c8140c53855b4ffae78f6327aa421792643099d3', 'CFM study card children differ from exact reviewed intrinsic-flow rule/bytes')
            continue
        if selector.strip() == 'body.cfm-page .cfm-toolkit__grid':
            check(re.sub(r'\s+', '', body) == 'grid-template-columns:1fr;' and sha(ROOT/'come-follow-me.css') == '97a1bb9d5d27a22126ce9f01c8140c53855b4ffae78f6327aa421792643099d3', 'CFM phone toolkit differs from exact reviewed rule/bytes')
            continue
        # Separate owner-authorized mobile opening and Conference banner review.
        # Exact file hashes prevent this scoped acceptance from admitting later edits.
        if selector.strip()=='body.fc-site.cfm-page .cfm-hero::before' and body.strip()=='background-position:center 25%':
            check(sha(ROOT/'come-follow-me.css')=='97a1bb9d5d27a22126ce9f01c8140c53855b4ffae78f6327aa421792643099d3',
                  'Come Follow Me mobile focal point differs from reviewed bytes')
            continue
        if selector.strip().startswith('.gc-page .gc-page-opening'):
            check(sha(ROOT/'general-conference-section.css')=='83b30800abdb31ff894314897030e7d7f8d469136267c00eea275dbed53cabe3',
                  'Conference opening CSS differs from reviewed bytes')
            continue
        if selector.strip()=='body.fc-site' and body.strip()=='--fc-opening-hero-height: clamp(320px, 44svh, 420px);':
            check(reviewed_system_panel_style((ROOT/'site-system.css').read_bytes()),
                  'Mobile opening CSS differs from reviewed bytes')
            continue
        dropdown_selectors = {
            '.nav[data-focuschrist-header="standard"] .hamburger-menu a:focus-visible',
            '.nav[data-focuschrist-header="standard"] .hamburger-menu a[aria-current="page"]',
            '.nav[data-focuschrist-header="standard"] .hamburger-menu a.active',
        }
        if all(part.strip() in dropdown_selectors for part in selector.split(',')):
            check(reviewed_toolbar_style('site-header.css', (ROOT/'site-header.css').read_bytes()),
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
