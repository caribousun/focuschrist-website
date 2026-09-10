#!/usr/bin/env python3
"""Verify the conference hub's source identities, progressive UI and local routes."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


class Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children, self.parts = tag, attrs or {}, [], []

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def text(self):
        return ' '.join(self.parts + [child.text() for child in self.children])


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        self.stack[-1].parts.append(text)


def require(condition, message):
    if not condition:
        raise SystemExit('GENERAL CONFERENCE QA FAIL: ' + message)


source = (ROOT / 'general-conference.html').read_text(encoding='utf-8')
doc = Document(source)
all_nodes = list(doc.root.walk())
hub = next((n for n in all_nodes if n.attrs.get('id') == 'general-conference'), None)
require(hub is not None, 'conference study root must remain on the standalone page')
require(any(n.tag == 'link' and n.attrs.get('rel') == 'canonical' and n.attrs.get('href') == 'https://focuschrist.com/general-conference.html' for n in all_nodes), 'standalone page needs its canonical URL')
require(sum(n.tag == 'h1' for n in all_nodes) == 1, 'standalone page needs one primary heading')
active_links = [n for n in all_nodes if n.tag == 'a' and n.attrs.get('aria-current') == 'page']
require(len(active_links) == 2 and all(urlsplit(n.attrs.get('href', '')).path == 'general-conference.html' and 'active' in n.attrs.get('class', '').split() for n in active_links), 'desktop and mobile menus must mark only General Conference active')
answers_doc = Document((ROOT / 'answers.html').read_text(encoding='utf-8'))
answers_nodes = list(answers_doc.root.walk())
# Answers retains a curated conference study surface while the standalone hub
# remains the canonical complete collection and direct destination.
require(any(n.attrs.get('id') == 'general-conference' for n in answers_nodes), 'legacy Answers fragment needs a useful migration destination')
require(any(n.tag == 'a' and urlsplit(n.attrs.get('href', '')).path == 'general-conference.html' for n in answers_nodes), 'Answers needs a direct standalone conference route')
nodes = list(hub.walk())
require(sum('data-full-image-viewer' in n.attrs for n in nodes) == 6, 'conference must retain its opening viewer and five manifested body artwork viewers')
ids = Counter(n.attrs['id'] for n in all_nodes if 'id' in n.attrs)
require(all(count == 1 for count in ids.values()), 'conference page IDs must remain unique')
cards = [n for n in nodes if 'data-conference-talk' in n.attrs]
groups = [n for n in nodes if 'data-conference-session' in n.attrs]
require(len(cards) == 37, 'all 37 April 2026 messages and proceedings must be available statically')
require(len(groups) == 4, 'April 2026 has four sessions')
group_values = {n.attrs['data-conference-session'] for n in groups}
require(len(group_values) == 4, 'sessions must have distinct filter values')
session_select = next((n for n in nodes if n.attrs.get('id') == 'conference-session'), None)
require(session_select is not None, 'session selector is missing')
require({n.attrs.get('value') for n in session_select.walk() if n.tag == 'option'} == group_values | {'all'}, 'session options must match actual groups')
require(all(n.tag == 'details' for n in groups), 'sessions must remain native disclosures')
require(not any('hidden' in n.attrs for n in cards + groups), 'no-JavaScript visitors must retain every message')
for required_id in ['conference-search', 'conference-session']:
    require(any(n.attrs.get('id') == required_id for n in nodes), 'missing filter ' + required_id)
    require(any(n.tag == 'label' and n.attrs.get('for') == required_id for n in nodes), 'filter needs a visible label: ' + required_id)
for attr in ['data-conference-reset', 'data-conference-status', 'data-conference-empty', 'data-conference-controls']:
    require(any(attr in n.attrs for n in nodes), 'missing progressive interface element ' + attr)
status = next(n for n in nodes if 'data-conference-status' in n.attrs)
require(status.attrs.get('aria-live') == 'polite' or status.attrs.get('role') == 'status', 'results count must be announced')
controls = next(n for n in nodes if 'data-conference-controls' in n.attrs)
require('hidden' in controls.attrs, 'inactive search controls must stay hidden without JavaScript')
require(any(n.tag == 'script' and urlsplit(n.attrs.get('src', '')).path == 'general-conference.js' for n in all_nodes), 'filter script missing')
for card in cards:
    require(bool(card.attrs.get('data-conference-search')), 'every message needs searchable title and speaker text')
    require(any(n.tag == 'img' for n in card.walk()), 'every message needs its source preview')

for n in nodes:
    if n.tag == 'img':
        image = ROOT / unquote(urlsplit(n.attrs.get('src', '')).path)
        require(image.is_file(), 'thumbnail missing: ' + str(image))
        require('alt' in n.attrs and n.attrs.get('width') and n.attrs.get('height'), 'thumbnail needs alt and layout dimensions')
    if n.tag == 'a':
        u = urlsplit(n.attrs.get('href', ''))
        if u.scheme or u.netloc:
            if n.attrs.get('target') == '_blank':
                require('noopener' in n.attrs.get('rel', '').split(), 'external tab needs noopener')
            continue
        target = ROOT / unquote(u.path or 'general-conference.html')
        require(target.is_file(), 'local study route missing: ' + str(target))
        if u.fragment and target.suffix == '.html' and u.fragment != 'ask-question':
            target_doc = Document(target.read_text(encoding='utf-8'))
            require(any(x.attrs.get('id') == unquote(u.fragment) for x in target_doc.root.walk()), 'study fragment missing: ' + n.attrs['href'])

ledger_path = ROOT / 'docs/general-conference-source-ledger.json'
require(ledger_path.is_file(), 'reviewed conference source ledger missing')
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
records = ledger['items']
april = [r for r in records if '/2026/04/' in r['url']]
require(len(april) == 37 and len({r['url'] for r in april}) == 37, 'ledger must identify each current message once')
for record in april:
    matches = [card for card in cards if any(n.tag == 'a' and n.attrs.get('href') == record['url'] for n in card.walk())]
    require(len(matches) == 1, 'message must appear in exactly one session: ' + record['id'])
    card = matches[0]
    normalized_text = ' '.join(card.text().split())
    speaker = record['speaker'].removeprefix('By ').removeprefix('Presented by ')
    require(record['title'] in normalized_text and speaker in normalized_text, 'published title/speaker differs from official source: ' + record['id'])
    require(record['title'] in card.attrs['data-conference-search'] and speaker in card.attrs['data-conference-search'], 'title/speaker omitted from search: ' + record['id'])
    require(any(n.tag == 'img' and n.attrs.get('src') == record['local_thumbnail'] for n in card.walk()), 'preview/source mismatch: ' + record['id'])
    image = ROOT / record['local_thumbnail']
    require(hashlib.sha256(image.read_bytes()).hexdigest() == record['sha256'], 'source preview bytes changed: ' + record['id'])
for record in ledger.get('enduring_sources', []):
    require(any(n.tag == 'a' and n.attrs.get('href') == record['url'] for n in nodes), 'enduring source route missing: ' + record['id'])
    image = ROOT / record['local_thumbnail']
    require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == record['sha256'], 'enduring source preview changed: ' + record['id'])
print('GENERAL CONFERENCE QA PASS: 37 source-matched messages, four native sessions, progressive filters, accessible controls, thumbnails, and connected routes.')
