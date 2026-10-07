#!/usr/bin/env python3
"""Exact, reversible review of existing-target anchor spacing; no artwork waiver."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / 'docs/anchor-alignment.json').read_text(encoding='utf-8'))
FILES = {item['path']: item for item in CONTRACT['files']}
VALUE = 'var(--fc-anchor-offset, 16px)'
PATTERN = re.compile(r'(scroll-margin-top\s*:\s*)([^;}]+)')

# Owner-authorized link audit: one continuous mouse/touch target for wrapped
# search titles. Strip only this exact declaration; the historical contract
# below must still reconstruct its original reviewed bytes.
SEARCH_HITBOX = b'.fc-search-result h2 a {display:inline-block;'
SEARCH_PRIOR = b'.fc-search-result h2 a {'
SEARCH_VERSION = '20260929-result-hitbox-1'
ART_STUDY_NAV_VERSION = '20261006-caption-prose-gap-1'
ART_CAPTION_GAP_SHA256 = 'b6d58dbb0c04984177a330db8686f0f5be03dff468b6ec2496ef5931b1da91d3'
ART_CAPTION_GAP_BLOCK = b'/* Keep following prose clear of the artwork caption without changing its frame. */\n.fc-art-study-page .fc-deep-study .fc-art-story + p {\n    margin-top: 20px;\n}\n\n'


def before_art_caption_gap(data):
    """Invert only the exact independently reviewed caption/prose buffer."""
    if hashlib.sha256(data).hexdigest() == ART_CAPTION_GAP_SHA256 and data.count(ART_CAPTION_GAP_BLOCK) == 1:
        prior = data.replace(ART_CAPTION_GAP_BLOCK, b'', 1)
        if hashlib.sha256(prior).hexdigest() == FILES['art-study-enrichment.css']['after_sha256']:
            return prior
    return data

TOPIC_DESKTOP_APPENDIX = b'\n/* Owner-requested desktop parity with Home; approved phone opening rules stay intact. */\n@media(min-width:701px){\n body.fc-site.fc-topic-page .fc-topic-opening{min-height:0;grid-template-rows:auto auto;align-content:start}\n body.fc-site.fc-topic-page .fc-topic-opening .fc-visual-hero{height:auto!important;min-height:0!important;max-height:none!important;aspect-ratio:2048/684}\n}\n'
TOPIC_DESKTOP_VERSION = "20260929-home-height-1"

STUDY_CENTER_APPENDIX = b'\n/* Owner-requested centered study choices; chapter picker keeps its own layout. */\nbody.fc-site .fc-study-nav:not(.jj-local-nav) { justify-content: center; }\n'
STUDY_CENTER_SHA256 = '17d2b86bc2afc65b8133b6cc2831028b02590fe6874a13098345f5f5a1ec35fc'
STUDY_CENTER_VERSION = "20261004-source-control-rows-2"

# Owner-authorized Joseph family study appendix. Full bytes and original prefix
# are pinned; no existing artwork or anchor geometry is exempted.
JOSEPH_LIFE_SHA256 = 'f0d485eafec25578228e1f69222c6ecc04b06ae5a4de33be50489c819b53c6a9'
JOSEPH_LIFE_APPENDIX = b'.joseph-life-nav{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}\n.joseph-life-nav a{border:1px solid var(--fc-line);border-radius:var(--fc-radius);padding:10px 14px;color:var(--fc-gold-light);text-decoration:none}\n.joseph-life-nav a:hover,.joseph-life-nav a:focus-visible{background:rgba(255,255,255,.06);text-decoration:underline}\n.joseph-life-scene,.joseph-life-closing{padding:32px 0;border-top:1px solid var(--fc-line);scroll-margin-top:120px}\n.joseph-life-scene>h3,.joseph-life-closing>h3{color:var(--fc-gold-light);font-size:clamp(1.35rem,3vw,1.85rem)}\n.joseph-life-enrichment p{line-height:1.7}\n.joseph-life-reflection{border-left:3px solid var(--fc-gold-light);padding:12px 18px;margin:24px 0}\n.joseph-life-source-note{font-size:.94rem}\n.joseph-life-scene .likeness-art img{width:100%;height:auto;object-fit:contain}\n@media(max-width:580px){.joseph-life-nav a{width:100%;box-sizing:border-box}.joseph-life-scene,.joseph-life-closing{padding:24px 0}}\n\n.joseph-life-caption-title{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}\n'

JOSEPH_LIFE_APPENDIX += b'\n/* The former illustrated opening is now a compact two-journey entrance. */\nbody.fc-likeness-page .joseph-bridge-intro{max-width:var(--fc-standard);margin:32px auto 24px;padding:0 var(--fc-body-gutter);text-align:center}\nbody.fc-likeness-page .joseph-bridge-intro h1{font-family:var(--fc-font-display);font-size:clamp(2rem,5vw,3.2rem);line-height:1.16;color:var(--fc-gold-light);margin:12px 0 18px}\nbody.fc-likeness-page .joseph-bridge-intro p{max-width:760px;margin:12px auto;line-height:1.65}\nbody.fc-likeness-page #joseph-study-entrance{margin-top:24px}\n@media(max-width:600px){body.fc-likeness-page .joseph-bridge-intro{margin:24px auto}body.fc-likeness-page #joseph-study-entrance h2{font-size:1.5rem}}\n'

# Exact owner-directed two-hero appendix; prior historical bytes still reconstruct.
JOSEPH_LIFE_APPENDIX += b'\n/* Distinct Joseph leading pictures retain the panorama on desktop and a reviewed central phone composition. */\nbody.fc-site .joseph-leading-hero{display:block;width:100%;height:auto!important;min-height:0!important;max-height:none!important;aspect-ratio:2170/725}\nbody.fc-site .joseph-leading-hero>img{object-fit:contain!important;object-position:center!important}\nbody.fc-site .joseph-leading-hero::before,body.fc-site .joseph-leading-hero::after{display:none}\nbody.fc-site .joseph-bridge-intro[data-unified-opening]{margin-block:0}\n@media(max-width:700px){body.fc-site .joseph-leading-hero{height:300px!important;min-height:300px!important;aspect-ratio:auto}body.fc-site .joseph-leading-hero>img{object-fit:cover!important;object-position:45% 50%!important}}\n'

# Exact owner-requested chapter-label correction; preserve prior anchor/artwork bytes.
JOURNEY_PICKER_VERSION = '20261007-chapter-pair-1'
JOURNEY_PICKER_SHA256 = 'f2b19be6fff3b5940bde22ab758e9547938c8154f6f63b6a280c95e1344c54a9'
JOURNEY_PICKER_PREVIOUS_SHA256 = '79979a47c68eb512854d98fbc4399411a5b88fb02262fff4e903c4adc9af6a2e'
JOURNEY_PAIR_APPENDIX = b'\n/* Paired chapter controls share content-driven rows, including enlarged text. */\n.jj-chapter-controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-items:stretch}\n.jj-chapter-position,.jj-reading-guide{grid-column:1/-1}\n.jj-chapter-controls .jj-chapter-picker{min-width:0;border-radius:10px}\n.jj-chapter-controls .jj-chapter-picker>summary{display:flex;align-items:center;justify-content:center;height:100%;min-height:44px;line-height:1.5}\n.jj-chapter-controls .jj-mode{box-sizing:border-box;min-width:0;font-size:1rem;text-align:center}\n.jj-chapter-controls .jj-chapter-picker[open]{grid-column:1/-1}\n.jj-chapter-controls .jj-chapter-picker[open]>summary{height:auto}\n@media(max-width:360px){.jj-chapter-controls{grid-template-columns:minmax(0,1fr)}}\n'
JOURNEY_PICKER_PRIOR = b'.jj-chapter-picker{flex:1 1 200px;border:1px solid #829a91!important;border-radius:12px;padding:0!important;min-width:0;background:#102c36}\n.jj-chapter-picker>summary{padding:10px 16px;font-size:1rem!important;margin:0!important}\n'
JOURNEY_PICKER_CURRENT = b".jj-chapter-picker{flex:1 1 200px;border:1px solid #829a91!important;border-radius:12px;padding:0!important;min-width:min(100%,14ch);box-sizing:border-box;background:#102c36}\n.jj-chapter-picker>summary{display:block;position:relative;box-sizing:border-box;padding:10px 38px;font-size:1rem!important;margin:0!important;list-style:none;text-align:center;overflow-wrap:anywhere}\n.jj-chapter-picker>summary::-webkit-details-marker{display:none}\n.jj-chapter-picker>summary::before{content:'';position:absolute;left:16px;top:50%;width:0;height:0;border-top:5px solid transparent;border-bottom:5px solid transparent;border-left:7px solid currentColor;transform:translateY(-50%)}\n.jj-chapter-picker[open]>summary::before{transform:translateY(-50%) rotate(90deg)}\n"

def before_journey_picker(data):
    if hashlib.sha256(data).hexdigest() == JOURNEY_PICKER_SHA256 and data.endswith(JOURNEY_PAIR_APPENDIX):
        data = data[:-len(JOURNEY_PAIR_APPENDIX)]
    if hashlib.sha256(data).hexdigest() == JOURNEY_PICKER_PREVIOUS_SHA256 and data.count(JOURNEY_PICKER_CURRENT) == 1:
        prior = data.replace(JOURNEY_PICKER_CURRENT, JOURNEY_PICKER_PRIOR, 1)
        if hashlib.sha256(prior).hexdigest() == FILES['jesus-journey.css']['after_sha256']:
            return prior
    return data


def before_joseph_life(data):
    if hashlib.sha256(data).hexdigest() == JOSEPH_LIFE_SHA256 and data.endswith(JOSEPH_LIFE_APPENDIX):
        prior = data[:-len(JOSEPH_LIFE_APPENDIX)]
        if hashlib.sha256(prior).hexdigest() == FILES['joseph-smith-likeness.css']['after_sha256']:
            return prior
    return data


SOURCE_ROWS_APPENDIX = b'\n/* Related source controls share each row instead of forming ragged steps.\n   Keep single citations compact and preserve the CFM reading-link treatment. */\nbody.fc-site :is(.fc-study-visual-sources, .pioneer-source-links) > a[hidden] {\n    display: none !important;\n}\nbody.fc-site:not(.cfm-page) :is(.fc-study-visual-sources, .pioneer-source-links) {\n    align-items: stretch;\n}\nbody.fc-site:not(.cfm-page) :is(.fc-study-visual-sources, .pioneer-source-links) > a:not(.fc-button--primary):not([hidden]) {\n    flex: 1 1 16rem;\n    margin: 0;\n}\nbody.fc-site:not(.cfm-page) :is(.fc-study-visual-sources, .pioneer-source-links) > a:not(.fc-button--primary):not([hidden]):only-child {\n    flex: 0 1 auto;\n}\n@media (max-width: 600px) {\n    body.fc-site:not(.cfm-page) :is(.fc-study-visual-sources, .pioneer-source-links) > a:not(.fc-button--primary):not([hidden]) {\n        flex-basis: 100%;\n        width: 100%;\n    }\n}\n'
SOURCE_ROWS_SHA256 = '52fa1665567cb5e7b7583a6ba8130e303737464da4a325f0b96be50ea026cc71'


# Exact owner-directed mobile navigation appendix; historical checks unchanged.
MOBILE_NAV_SHA256 = '180472aa7aaa2009115976caec3d5838c76275d4c25f63523901224255859e55'
MOBILE_NAV_VERSION = '20261005-mobile-study-rows-1'
MOBILE_NAV_APPENDIX = b'\n/* Mobile study menus use aligned rows; numbered chapter pickers retain their\n   own layouts. Rem-based tracks reflow with enlarged text. */\n@media (max-width: 700px) {\n    body.fc-site :is(.fc-study-nav:not(.jj-local-nav), .cfm-jump, .gc-jumps, .watch-theme-tabs, .cta-row, .journal-collections, .filters, .era-pills, .controls-row) {\n        display: grid;\n        width: 100%;\n        grid-template-columns: repeat(auto-fit, minmax(min(100%, max(10rem, 45%)), 1fr));\n        align-items: stretch;\n        gap: var(--fc-study-control-gap) !important;\n    }\n    body.fc-site :is(.fc-study-nav:not(.jj-local-nav), .cfm-jump, .gc-jumps, .watch-theme-tabs, .cta-row, .journal-collections, .filters, .era-pills, .controls-row) > :is(a, button) {\n        width: 100%;\n        margin: 0;\n        min-height: max(44px, 3.5rem) !important;\n        align-self: stretch;\n    }\n    body.fc-site :is(.fc-study-nav:not(.jj-local-nav), .cfm-jump, .gc-jumps, .watch-theme-tabs, .cta-row, .journal-collections, .filters, .era-pills, .controls-row, .atonement-path) > :is(a, button):last-child:nth-of-type(odd) {\n        grid-column: 1 / -1;\n    }\n    body.fc-site .era-pills {\n        grid-template-columns: minmax(0, 1fr) !important;\n    }\n    body.fc-site .controls-row > .lbl {\n        grid-column: 1 / -1;\n    }\n    /* The unified opening owns placement; its retained descriptions stay visible. */\n    body.fc-site :is([data-unified-opening], .fc-unified-opening-continuation) .fc-opening-explanation {\n        display: block !important;\n        flex: 0 0 auto;\n        width: 100%; max-width: 38ch; box-sizing: border-box;\n        margin: 0; padding: 0;\n        color: var(--fc-muted); font-size: .9rem; line-height: 1.45;\n        font-weight: 400; text-align: center;\n    }\n}\n'

def before_mobile_nav(data):
    if hashlib.sha256(data).hexdigest() == MOBILE_NAV_SHA256 and data.endswith(MOBILE_NAV_APPENDIX):
        prior = data[:-len(MOBILE_NAV_APPENDIX)]
        if hashlib.sha256(prior).hexdigest() == SOURCE_ROWS_SHA256:
            return prior
    return data

def before_source_rows(data):
    if hashlib.sha256(data).hexdigest() == SOURCE_ROWS_SHA256 and data.endswith(SOURCE_ROWS_APPENDIX):
        prior = data[:-len(SOURCE_ROWS_APPENDIX)]
        if hashlib.sha256(prior).hexdigest() == STUDY_CENTER_SHA256:
            return prior
    return data

def before_study_center(data):
    if hashlib.sha256(data).hexdigest() == STUDY_CENTER_SHA256 and data.endswith(STUDY_CENTER_APPENDIX):
        return data[:-len(STUDY_CENTER_APPENDIX)]
    return data


def before_topic_desktop(data):
    if data.endswith(TOPIC_DESKTOP_APPENDIX):
        prior = data[:-len(TOPIC_DESKTOP_APPENDIX)]
        if hashlib.sha256(prior).hexdigest() == FILES["topic-study-pages.css"]["after_sha256"]:
            return prior
    return data


def before_search_hitbox(data):
    if data.count(SEARCH_HITBOX) == 1:
        prior = data.replace(SEARCH_HITBOX, SEARCH_PRIOR, 1)
        if hashlib.sha256(prior).hexdigest() == FILES['site-search.css']['after_sha256']:
            return prior
    return data


CONFERENCE_VERSION = '20261007-conference-centered-controls-3'
CONFERENCE_CENTER_APPENDIX = b'\n/* Center the complete conference control row and existing artwork compositions. */\n#general-conference .gc-jumps { justify-content: center; }\n#general-conference .gc-heading:has(> .fc-study-visual) { margin-inline: auto; }\n\n/* Keep the Session chevron comfortably inside its existing native control. */\n#conference-session {\n    appearance: none;\n    padding-right: 36px;\n    background-image: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'10\' height=\'6\' viewBox=\'0 0 10 6\'%3E%3Cpath d=\'m1 1 4 4 4-4\' fill=\'none\' stroke=\'%23fff2dc\' stroke-width=\'1.5\'/%3E%3C/svg%3E");\n    background-repeat: no-repeat;\n    background-position: right 12px center;\n    background-size: 10px 6px;\n}\n'
CONFERENCE_ROWS_SHA256 = '7c0f15564c90ea0fa066041e54938e52c661a0c7f3c188f20a1ad4739eab2bcc'
CONFERENCE_ROWS_APPENDIX = b'\n/* Balance the visible search results, excluding cards hidden by the filters. */\n@media (min-width:701px) and (max-width:1000px) {\n    #conference-results .fc-talk-list > :not([hidden]) { grid-column: auto; }\n    #conference-results .fc-talk-list > :nth-last-child(1 of :not([hidden])):nth-child(odd of :not([hidden])) { grid-column: 1 / -1; }\n}\n@media (min-width:1001px) {\n    #conference-results .fc-talk-list > :not([hidden]) { grid-column: span 2; }\n    #conference-results .fc-talk-list > :not([hidden]) > a { display: flex; }\n    #conference-results .fc-talk-list > :nth-last-child(1 of :not([hidden])):nth-child(3n+1 of :not([hidden])) { grid-column: 1 / -1; }\n    #conference-results .fc-talk-list > :nth-last-child(2 of :not([hidden])):nth-child(3n+1 of :not([hidden])),\n    #conference-results .fc-talk-list > :nth-last-child(1 of :not([hidden])):nth-child(3n+2 of :not([hidden])) { grid-column: span 3; }\n    #conference-results .fc-talk-list > :nth-last-child(1 of :not([hidden])):nth-child(3n+1 of :not([hidden])) > a { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); align-items: center; }\n}\n'
CONFERENCE_ARCHIVE_SHA256 = '2f5903f9d75b2da757aea4a448f0593ab9eb1a8eafe7c9a454bbca0603e4503f'
CONFERENCE_CURRENT = b'.fc-conference-sessions details[open]>summary'
CONFERENCE_PRIOR = b'.fc-conference-sessions details[open] summary'


def before_conference_centering(data):
    if data.count(CONFERENCE_CENTER_APPENDIX) == 1 and data.endswith(CONFERENCE_CENTER_APPENDIX):
        prior = data[:-len(CONFERENCE_CENTER_APPENDIX)]
        if hashlib.sha256(prior).hexdigest() == CONFERENCE_ROWS_SHA256:
            return prior
    return data


def before_conference_archive(data):
    """Invert only the exact visible-row appendix and two archive selectors."""
    data = before_conference_centering(data)
    if data.count(CONFERENCE_ROWS_APPENDIX) != 1 or not data.endswith(CONFERENCE_ROWS_APPENDIX):
        return data
    archive = data[:-len(CONFERENCE_ROWS_APPENDIX)]
    if hashlib.sha256(archive).hexdigest() != CONFERENCE_ARCHIVE_SHA256:
        return data
    if archive.count(CONFERENCE_CURRENT) == 2 and CONFERENCE_PRIOR not in archive:
        prior = archive.replace(CONFERENCE_CURRENT, CONFERENCE_PRIOR)
        if hashlib.sha256(prior).hexdigest() == FILES['general-conference-section.css']['after_sha256']:
            return prior
    return data


def historical_style_bytes(data):
    """Recover exact prior bytes only from an exact registered current file.

    Existing artwork geometry/prefix checks continue to inspect their original
    reviewed bytes. The mandatory current-file checks separately reject stale
    files and any mutation to the approved anchor-only transformation.
    """
    data = before_conference_archive(data)
    data = before_art_caption_gap(data)
    data = before_mobile_nav(data)
    data = before_source_rows(data)
    data = before_journey_picker(before_joseph_life(before_study_center(before_topic_desktop(before_search_hitbox(data)))))
    digest = hashlib.sha256(data).hexdigest()
    record = next((r for r in FILES.values() if r['after_sha256'] == digest), None)
    if not record:
        return data
    text = data.decode('utf-8')
    if record['path'] == 'art-study-enrichment.css':
        current = r'(\.fc-art-study-page \.fc-study-nav \{\r?\n    position: )static;(\r?\n    top: )auto;(\r?\n    z-index: )auto;'
        previous = r'\g<1>sticky;\g<2>74px;\g<3>8;'
        text, count = re.subn(current, previous, text)
        if count != 1:
            return data
    if record['path'] == 'site-system.css':
        appendix = CONTRACT['shared_appendix']
        if not text.endswith(appendix):
            return data
        text = text[:-len(appendix)]
        # Only the unindented global rule changed. Preserve the separate
        # reduced-motion rules and prove the exact pre-review file afterward.
        current = '\nhtml { scroll-behavior: auto; }\n'
        previous_rule = '\nhtml { scroll-behavior: smooth; }\n'
        if text.count(current) != 1:
            return data
        text = text.replace(current, previous_rule, 1)
    found = list(PATTERN.finditer(text))
    if len(found) != len(record['old_values']) or any(m[2] != VALUE for m in found):
        return data
    previous = iter(record['old_values'])
    restored = PATTERN.sub(lambda m: m[1] + next(previous), text).encode('utf-8')
    return restored if hashlib.sha256(restored).hexdigest() == record['before_sha256'] else data


def reviewed_anchor_style(name, data):
    record = FILES.get(name)
    if name == 'general-conference-section.css':
        if before_conference_centering(data) == data: return False
        prior = before_conference_archive(data)
        if prior == data: return False
        data = prior
    if name == 'art-study-enrichment.css':
        if hashlib.sha256(data).hexdigest() != ART_CAPTION_GAP_SHA256: return False
        data = before_art_caption_gap(data)
    if name == 'jesus-journey.css':
        if hashlib.sha256(data).hexdigest() != JOURNEY_PICKER_SHA256: return False
        data = before_journey_picker(data)
    if name == 'joseph-smith-likeness.css':
        if hashlib.sha256(data).hexdigest() != JOSEPH_LIFE_SHA256: return False
        data = before_joseph_life(data)
    if name == 'site-system.css':
        if hashlib.sha256(data).hexdigest() != MOBILE_NAV_SHA256: return False
        data = before_mobile_nav(data)
        if hashlib.sha256(data).hexdigest() != SOURCE_ROWS_SHA256: return False
        data = before_source_rows(data)
        if hashlib.sha256(data).hexdigest() != STUDY_CENTER_SHA256: return False
        data = before_study_center(data)
    if name == "topic-study-pages.css":
        if not data.endswith(TOPIC_DESKTOP_APPENDIX):
            return False
        data = before_topic_desktop(data)
    if name == 'site-search.css':
        if data.count(SEARCH_HITBOX) != 1:
            return False
        data = before_search_hitbox(data)
    return bool(record and hashlib.sha256(data).hexdigest() == record['after_sha256']
                and hashlib.sha256(historical_style_bytes(data)).hexdigest() == record['before_sha256'])


def conference_cache_errors(pages):
    expected = 'general-conference-section.css?v=' + CONFERENCE_VERSION
    consumers = {}
    for name, source in pages.items():
        refs = re.findall(r'(?:href|src)=["\']([^"\']*general-conference-section\.css[^"\']*)["\']', source)
        if refs:
            consumers[name] = refs
    return [] if consumers == {'answers.html': [expected], 'general-conference.html': [expected]} else ['Conference stylesheet consumers must be exactly Answers and General Conference, one current reference each']


def check():
    errors = []
    if len(FILES) != 22 or sum(len(r['old_values']) for r in FILES.values()) != 37:
        errors.append('Expected 22 anchor-only stylesheets and 37 existing target declarations; CFM has its separate exact composition contract')
    for name in FILES:
        if not reviewed_anchor_style(name, (ROOT / name).read_bytes()):
            errors.append('Anchor-only stylesheet contract changed: ' + name)
    # Verify header geometry remains the source of the desktop offset.
    header = (ROOT / 'site-header.css').read_text(encoding='utf-8')
    compact = re.sub(r'\s+', '', header)
    if 'height:max(52px,3.25rem)!important' not in compact or '@media(max-width:1020px)' not in compact:
        errors.append('Header geometry changed; re-review anchor spacing')
    conference_pages = {}
    for path in ROOT.rglob('*.html'):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(('tools/', 'work/', 'node_modules/', '.git/')):
            continue
        conference_pages[rel] = path.read_text(encoding='utf-8')
        for filename, version in re.findall(r'([\w-]+\.css)\?v=([\w.-]+)', conference_pages[rel]):
            expected = ART_STUDY_NAV_VERSION if filename == 'art-study-enrichment.css' else '20261004-joseph-heroes-1' if filename == 'joseph-smith-likeness.css' and rel in {'joseph-smith-likeness.html','joseph-smith-portrait-research.html'} else JOURNEY_PICKER_VERSION if filename == 'jesus-journey.css' else MOBILE_NAV_VERSION if filename == 'site-system.css' else SEARCH_VERSION if filename == 'site-search.css' else TOPIC_DESKTOP_VERSION if filename == 'topic-study-pages.css' else CONTRACT['version']
            if filename == 'general-conference-section.css':
                expected = CONFERENCE_VERSION
            if filename in FILES and version != expected:
                errors.append('Stale anchor stylesheet: ' + rel + ': ' + filename)
    errors.extend(conference_cache_errors(conference_pages))
    return errors


def self_test():
    conference = (ROOT / 'general-conference-section.css').read_bytes()
    for mutation in (conference.replace(CONFERENCE_CURRENT, CONFERENCE_PRIOR),
                     conference.replace(CONFERENCE_CURRENT, CONFERENCE_PRIOR, 1),
                     conference.replace(CONFERENCE_CURRENT, b'.fc-conference-sessions details[open]~summary', 1),
                     conference + b'\nbody{color:red}'):
        assert mutation != conference
        assert not reviewed_anchor_style('general-conference-section.css', mutation)
    for mutation in (conference[:-len(CONFERENCE_ROWS_APPENDIX)], conference + CONFERENCE_ROWS_APPENDIX,
                     conference.replace(b' of :not([hidden])', b'', 1),
                     conference.replace(b'#conference-results', b'.fc-conference-section', 1),
                     conference.replace(b'grid-column: span 3;', b'grid-column: span 2;', 1)):
        assert mutation != conference
        assert not reviewed_anchor_style('general-conference-section.css', mutation)
    for mutation in (before_conference_centering(conference), conference + CONFERENCE_CENTER_APPENDIX,
                     conference.replace(CONFERENCE_CENTER_APPENDIX, CONFERENCE_CENTER_APPENDIX.replace(b'justify-content: center; }', b'justify-content: start; }', 1), 1),
                     conference.replace(CONFERENCE_CENTER_APPENDIX, CONFERENCE_CENTER_APPENDIX.replace(b'margin-inline: auto; }', b'margin-inline: 0; }', 1), 1),
                     conference.replace(CONFERENCE_CENTER_APPENDIX, CONFERENCE_CENTER_APPENDIX.replace(b'right 12px center', b'right 0px center', 1), 1),
                     conference.replace(CONFERENCE_CENTER_APPENDIX, CONFERENCE_CENTER_APPENDIX.replace(b'padding-right: 36px', b'padding-right: 12px', 1), 1)):
        assert mutation != conference
        assert not reviewed_anchor_style('general-conference-section.css', mutation)
    link = '<link href="general-conference-section.css?v=' + CONFERENCE_VERSION + '">'
    pages = {'answers.html': link, 'general-conference.html': link}
    assert not conference_cache_errors(pages)
    for altered in ({'answers.html': link}, {**pages, 'other.html': link},
                    {**pages, 'answers.html': link + link},
                    {**pages, 'answers.html': link + link.replace(CONFERENCE_VERSION, 'unknown')},
                    {**pages, 'answers.html': link.replace(CONFERENCE_VERSION, '20261007-october-archive-1')},
                    {**pages, 'answers.html': link.replace(CONFERENCE_VERSION, '20261007-october-visible-rows-2')},
                    {**pages, 'answers.html': link.replace(CONFERENCE_VERSION, 'unknown')}):
        assert conference_cache_errors(altered)
    for name in FILES:
        data = (ROOT / name).read_bytes()
        assert reviewed_anchor_style(name, data), name
        assert not reviewed_anchor_style(name, data + b'\nbody{height:1px}'), name
        assert not reviewed_anchor_style(name, data.replace(VALUE.encode(), b'100px', 1)), name
        assert not reviewed_anchor_style(name, b'/* extra */' + data), name
        assert not reviewed_anchor_style('unregistered.css', data), name
        assert not reviewed_anchor_style(name, historical_style_bytes(data)), name
    art = (ROOT / 'art-study-enrichment.css').read_bytes()
    prior_art = before_art_caption_gap(art)
    assert hashlib.sha256(prior_art).hexdigest() == FILES['art-study-enrichment.css']['after_sha256']
    assert hashlib.sha256(historical_style_bytes(art)).hexdigest() == FILES['art-study-enrichment.css']['before_sha256']
    assert not reviewed_anchor_style('art-study-enrichment.css', prior_art)
    for mutation in (
        art + ART_CAPTION_GAP_BLOCK,
        art.replace(b'margin-top: 20px;', b'margin-top: 21px;', 1),
        art.replace(b'.fc-art-story + p {', b'.fc-art-story ~ p {', 1),
        art.replace(b'.fc-art-story img {', b'.fc-art-story video {', 1),
        art + b'\nbody{color:red}',
    ):
        assert mutation != art
        assert before_art_caption_gap(mutation) == mutation
        assert not reviewed_anchor_style('art-study-enrichment.css', mutation)
    journey = (ROOT / 'jesus-journey.css').read_bytes()
    assert not reviewed_anchor_style('jesus-journey.css', before_journey_picker(journey))
    assert not reviewed_anchor_style('jesus-journey.css', journey.replace(b'min-width:min(100%,14ch);', b'min-width:0;', 1))
    for old, new in [(b'text-align:center;', b'text-align:left;'), (b'padding:10px 38px;', b'padding:10px 38px 10px 16px;'), (b'rotate(90deg)', b'rotate(0deg)'), (b'::-webkit-details-marker{display:none}', b'::-webkit-details-marker{display:block}')]:
        changed = JOURNEY_PICKER_CURRENT.replace(old, new, 1)
        assert changed != JOURNEY_PICKER_CURRENT
        assert not reviewed_anchor_style('jesus-journey.css', journey.replace(JOURNEY_PICKER_CURRENT, changed, 1))
    for mutation in (journey + JOURNEY_PAIR_APPENDIX, journey[:-len(JOURNEY_PAIR_APPENDIX)], journey.replace(b'align-items:stretch}\n.jj-chapter-position', b'align-items:center}\n.jj-chapter-position'), journey.replace(b'@media(max-width:360px)', b'@media(max-width:300px)')):
        assert mutation != journey
        assert not reviewed_anchor_style('jesus-journey.css', mutation)
    shared = (ROOT / 'site-system.css').read_bytes()
    assert not reviewed_anchor_style('site-system.css', before_mobile_nav(shared))
    assert before_mobile_nav(shared) == shared[:-len(MOBILE_NAV_APPENDIX)]
    assert not reviewed_anchor_style('site-system.css', shared[:-1] + bytes([shared[-1] ^ 1]))
    search = (ROOT / 'site-search.css').read_bytes()
    assert not reviewed_anchor_style('site-search.css', search.replace(SEARCH_HITBOX, SEARCH_PRIOR, 1))
    assert not reviewed_anchor_style('site-search.css', search.replace(b'display:inline-block;', b'display:inline;', 1))
    assert not reviewed_anchor_style('site-system.css', shared.replace(
        b'\nhtml { scroll-behavior: auto; }\n', b'\nhtml { scroll-behavior: smooth; }\n', 1))
    assert not reviewed_anchor_style('site-system.css', shared.replace(
        b'    html { scroll-behavior: auto; }', b'    html { scroll-behavior: smooth; }', 1))
    for old, new in [(b'1021px', b'1000px'), (b'3.25rem', b'52px'), (b'+ 16px', b'+ 100px')]:
        # Change the exact appendix, not an unrelated earlier occurrence.
        changed_appendix = CONTRACT['shared_appendix'].replace(old.decode(), new.decode()).encode()
        assert not reviewed_anchor_style('site-system.css', shared[:-len(CONTRACT['shared_appendix'].encode())] + changed_appendix)
    print('PASS: exact anchor transform, stale offsets, unrelated edits, unknown files, breakpoint, enlarged-text, root smooth-scroll and reduced-motion fixtures')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    errors = check()
    print(json.dumps({'stylesheets': len(FILES), 'existing_targets': 37, 'errors': errors}, indent=2))
    raise SystemExit(bool(errors))
