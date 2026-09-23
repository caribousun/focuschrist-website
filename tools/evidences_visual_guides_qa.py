"""Typed analytical SVG checks; never treat vectors as decoded photographic pixels."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/evidences-visual-guides-review-20260923.json'
ALLOWED = {'svg', 'title', 'desc', 'rect', 'circle', 'path', 'text', 'tspan'}

def records():
    return json.loads(MANIFEST.read_text(encoding='utf-8'))['records']

def svg_errors(data, entry, verify_hash=True):
    errors = []
    if verify_hash and hashlib.sha256(data).hexdigest() != entry['sha256']:
        errors.append('SVG differs from reviewed source bytes')
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        return errors + ['SVG must not declare external entities']
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return errors + ['Malformed SVG']
    if root.tag != '{http://www.w3.org/2000/svg}svg': errors.append('Wrong SVG root')
    if root.get('viewBox') != f"0 0 {entry['width']} {entry['height']}": errors.append('Wrong SVG viewBox')
    if (root.get('width'), root.get('height')) != (str(entry['width']), str(entry['height'])): errors.append('Wrong SVG dimensions')
    for node in root.iter():
        if node.tag.removeprefix('{http://www.w3.org/2000/svg}') not in ALLOWED:
            errors.append('SVG has unreviewed element')
        for name, value in node.attrib.items():
            if name.lower().startswith('on') or name.endswith('href') or 'url(' in value.lower():
                errors.append('SVG has active or externally embedded content')
    titles = root.findall('{http://www.w3.org/2000/svg}title')
    descs = root.findall('{http://www.w3.org/2000/svg}desc')
    if len(titles) != 1 or titles[0].text != entry['title']: errors.append('SVG title differs')
    if len(descs) != 1 or descs[0].text != entry['alt']: errors.append('SVG accessible description differs')
    return errors

def check():
    errors = []
    entries = records()
    if len({e['asset'] for e in entries}) != len(entries): errors.append('Repeated diagram asset')
    expected = {e[field] for e in entries for field in ('asset', 'desktop_asset')}
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/'assets/page-art/bom-evidences/visual-guides-20260923').glob('*.svg')}
    if actual != expected: errors.append('SVG variant inventory differs from reviewed set')
    for e in entries:
        if e.get('type') != 'analytical-svg' or e.get('counts_as_photographic_artwork') is not False:
            errors.append('Diagrams must remain separately typed')
        path = (ROOT / e['asset']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file(): errors.append('Missing diagram'); continue
        errors.extend(e['key'] + ': ' + x for x in svg_errors(path.read_bytes(), e))
        desktop = dict(e, width=e['desktop_width'], height=e['desktop_height'], sha256=e['desktop_sha256'])
        errors.extend(e['key'] + ' desktop: ' + x for x in svg_errors((ROOT / e['desktop_asset']).read_bytes(), desktop))
    return errors

if __name__ == '__main__':
    errors = check()
    first = records()[0]
    data = (ROOT / first['asset']).read_bytes()
    assert not svg_errors(data, first)
    assert svg_errors(data + b' ', first)
    assert svg_errors(data.replace(b'</svg>', b'<script>alert(1)</script></svg>'), first, False)
    assert svg_errors(data.replace(b'<rect ', b'<rect onclick="alert(1)" ', 1), first, False)
    assert svg_errors(data.replace(b'<rect ', b'<rect filter="url(https://example.com/x)" ', 1), first, False)
    assert svg_errors(data.replace(b'viewBox="0 0 ', b'viewBox="1 0 ', 1), first, False)
    if errors: raise SystemExit('\n'.join(errors))
    print(f'Analytical SVG QA PASS: {len(records())} exact source hashes, dimensions, accessible descriptions and inactive vector markup; negative fixtures passed')
