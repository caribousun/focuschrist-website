"""Discover all complete-row consumers; rendered geometry is tested separately."""
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from answer_study_qa import Document

ROOT = Path(__file__).resolve().parents[1]
CLASSES = {'fc-resource-grid', 'fc-study-grid', 'ask-continue-grid', 'fc-voice-grid', 'gc-pathways', 'fc-talk-list'}
VERSION = '20260920-1'


def inventory():
    pages = sorted({urlsplit(n.text).path.lstrip('/') or 'index.html' for n in ET.parse(ROOT / 'sitemap.xml').getroot().findall('{*}url/{*}loc')})
    consumers = []
    for path in pages:
        doc = Document()
        doc.feed((ROOT / path).read_text(encoding='utf-8'))
        nodes = list(doc.root.walk())
        grids = [n for n in nodes if CLASSES.intersection(n.attrs.get('class', '').split())]
        links = [n.attrs.get('href', '') for n in nodes if n.tag == 'link' and 'complete-card-rows.css' in n.attrs.get('href', '')]
        if grids:
            expected = '../' * path.count('/') + 'complete-card-rows.css?v=' + VERSION
            assert links == [expected], f'{path}: missing, duplicate or stale complete-row stylesheet'
            consumers.append(path)
        else:
            assert not links, f'{path}: stylesheet added without a covered grid'
    return consumers


if __name__ == '__main__':
    pages = inventory()
    assert 'answers/settle-this-in-your-hearts.html' in pages
    assert 'answers/stand-forever.html' in pages
    print(f'PASS: discovered {len(pages)} complete-row consumers; rendered QA must also pass')
