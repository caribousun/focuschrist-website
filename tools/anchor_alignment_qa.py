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

TOPIC_DESKTOP_APPENDIX = b'\n/* Owner-requested desktop parity with Home; approved phone opening rules stay intact. */\n@media(min-width:701px){\n body.fc-site.fc-topic-page .fc-topic-opening{min-height:0;grid-template-rows:auto auto;align-content:start}\n body.fc-site.fc-topic-page .fc-topic-opening .fc-visual-hero{height:auto!important;min-height:0!important;max-height:none!important;aspect-ratio:2048/684}\n}\n'
TOPIC_DESKTOP_VERSION = "20260929-home-height-1"

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


def historical_style_bytes(data):
    """Recover exact prior bytes only from an exact registered current file.

    Existing artwork geometry/prefix checks continue to inspect their original
    reviewed bytes. The mandatory current-file checks separately reject stale
    files and any mutation to the approved anchor-only transformation.
    """
    data = before_topic_desktop(before_search_hitbox(data))
    digest = hashlib.sha256(data).hexdigest()
    record = next((r for r in FILES.values() if r['after_sha256'] == digest), None)
    if not record:
        return data
    text = data.decode('utf-8')
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
    for path in ROOT.rglob('*.html'):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(('tools/', 'work/', 'node_modules/', '.git/')):
            continue
        for filename, version in re.findall(r'([\w-]+\.css)\?v=([\w.-]+)', path.read_text(encoding='utf-8')):
            expected = SEARCH_VERSION if filename == 'site-search.css' else TOPIC_DESKTOP_VERSION if filename == 'topic-study-pages.css' else CONTRACT['version']
            if filename in FILES and version != expected:
                errors.append('Stale anchor stylesheet: ' + rel + ': ' + filename)
    return errors


def self_test():
    for name in FILES:
        data = (ROOT / name).read_bytes()
        assert reviewed_anchor_style(name, data), name
        assert not reviewed_anchor_style(name, data + b'\nbody{height:1px}'), name
        assert not reviewed_anchor_style(name, data.replace(VALUE.encode(), b'100px', 1)), name
        assert not reviewed_anchor_style(name, b'/* extra */' + data), name
        assert not reviewed_anchor_style('unregistered.css', data), name
        assert not reviewed_anchor_style(name, historical_style_bytes(data)), name
    shared = (ROOT / 'site-system.css').read_bytes()
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
