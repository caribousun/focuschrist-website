"""Build the research page from its shared, reviewed reader manuscript.

The manuscript is the canonical narrative for the webpage and PDF. Historical
JSON registries remain source/provenance records; they do not overwrite prose.
The tracked route supplies the existing site shell, scripts, and exact footer.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / 'docs/joseph-research-manuscript.html.inc'
OUTPUT = ROOT / 'joseph-smith-portrait-research.html'
MAIN = re.compile(r'<main\b[^>]*\bid="main-content"[^>]*>[\s\S]*?</main>')


def build(check=False):
    manuscript = MANUSCRIPT.read_text(encoding='utf-8').strip()
    page = OUTPUT.read_text(encoding='utf-8')
    if len(MAIN.findall(page)) != 1 or not MAIN.fullmatch(manuscript):
        raise ValueError('Expected one complete canonical research main element')
    ids = re.findall(r'<section\b[^>]*\bid="(portrait-section-\d+)"', manuscript)
    expected = [f'portrait-section-{n}' for n in [1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 3, 10, 13, 14, 15]]
    if ids != expected:
        raise ValueError('Research narrative section order differs from reviewed reading journey')
    result = MAIN.sub(lambda _: manuscript, page, count=1)
    if check:
        if result != page:
            raise SystemExit('Research page is stale; rebuild from the canonical manuscript')
    else:
        OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print(json.dumps({'output': OUTPUT.name, 'canonical_source': str(MANUSCRIPT.relative_to(ROOT)),
                      'sections': len(ids), 'manuscript_sha256': hashlib.sha256(MANUSCRIPT.read_bytes()).hexdigest(),
                      'status': 'current' if check else 'built'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
