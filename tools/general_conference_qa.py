#!/usr/bin/env python3
"""Verify the conference hub's source identities, progressive UI and local routes."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib
import json
import sys

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
style_bytes = (ROOT / 'general-conference-section.css').read_bytes()
style = style_bytes.decode('utf-8')
require(style.count('.fc-conference-sessions details[open]>summary') == 2 and '.fc-conference-sessions details[open] summary' not in style, 'nested archive state must style only the opened details own summary')
from anchor_alignment_qa import reviewed_anchor_style, CONFERENCE_ROWS_APPENDIX, CONFERENCE_VERSION
require(reviewed_anchor_style('general-conference-section.css', style_bytes), 'only exact archive, visible-result rows, centered-controls and accessible mobile archive-count corrections may change')
conference_styles = [n.attrs.get('href') for n in all_nodes if n.tag == 'link' and 'general-conference-section.css' in n.attrs.get('href', '')]
require(conference_styles == ['general-conference-section.css?v=' + CONFERENCE_VERSION], 'conference stylesheet requires exactly one current reference')
corbridge_visuals = [n for n in all_nodes if n.tag == 'a'
                    and 'gc-voice-visual' in n.attrs.get('class', '').split()
                    and n.attrs.get('href') == 'answers/stand-forever.html']
require(len(corbridge_visuals) == 1, 'Corbridge enduring-voice card needs its linked visual')
corbridge_images = [n for n in corbridge_visuals[0].walk() if n.tag == 'img']
require(len(corbridge_images) == 1
        and corbridge_images[0].attrs.get('src') == 'assets/resources/corbridge-stand-forever-byu.jpg'
        and corbridge_images[0].attrs.get('width') == '1280'
        and corbridge_images[0].attrs.get('height') == '720'
        and (ROOT / corbridge_images[0].attrs['src']).is_file(),
        'Corbridge card must retain its official BYU thumbnail with reserved 16:9 dimensions')
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
require(sum('data-full-image-viewer' in n.attrs for n in nodes) == 5, 'conference must retain all five manifested body artwork viewers')
opening = [n for n in all_nodes if n.attrs.get('data-exclusive-artwork') == 'conference-listening']
require(len(opening) == 1, 'conference needs exactly one exclusive opening study picture')
opening_header = next(n for n in all_nodes if 'gc-page-opening' in n.attrs.get('class', '').split())
require(opening[0] in list(opening_header.walk()), 'conference picture must remain in its opening header')
require(any(n.attrs.get('srcset') == 'assets/heroes/conference-desktop-exact-20260929.webp' and n.attrs.get('media') == '(min-width:701px)' for n in opening[0].walk()), 'conference desktop must use its reviewed wide rendition while retaining the original mobile image')
opening_links = [n for n in opening[0].walk() if n.tag == 'a' and any(c.tag == 'img' for c in n.walk())]
require(len(opening_links) == 1, 'conference opening needs one picture trigger')
opening_trigger = opening_links[0]
require(opening_trigger.attrs.get('href') == 'assets/heroes/topics/conference-listening-full.webp' and opening_trigger.attrs.get('aria-haspopup') == 'dialog' and 'data-full-image-viewer' not in opening_trigger.attrs, 'conference opening must preserve its own picture and open study details first')
require(opening_trigger.attrs.get('data-topic-study') == 'general-conference.html#conference-messages', 'conference opening must continue to its own messages')
require(any(n.tag == 'a' and n.attrs.get('href') == 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/1?lang=eng&id=p37-p38#p37' for n in opening[0].walk()), 'conference opening must retain its exact scripture source')
require(sum(n.tag == 'script' and 'topic-artwork-details.js' in n.attrs.get('src', '') for n in all_nodes) == 1, 'conference opening requires the shared study adapter once')
ids = Counter(n.attrs['id'] for n in all_nodes if 'id' in n.attrs)
require(all(count == 1 for count in ids.values()), 'conference page IDs must remain unique')
cards = [n for n in nodes if 'data-conference-talk' in n.attrs]
groups = [n for n in nodes if 'data-conference-session' in n.attrs]
require(len(cards) == 38, 'all 38 October 2026 messages and proceedings must be available statically')
require(len(groups) == 4, 'October 2026 has four sessions')
require([sum('data-conference-talk' in n.attrs for n in g.walk()) for g in groups] == [9, 10, 9, 10], 'October official session order/counts must be preserved')
archive = next((n for n in nodes if n.attrs.get('id') == 'conference-april-2026'), None)
require(archive is not None and archive.tag == 'details' and 'open' not in archive.attrs, 'April must remain in a clearly collapsed native archive')
archive_summaries = [n for n in archive.children if n.tag == 'summary']
require(len(archive_summaries) == 1, 'archive needs one direct native summary')
archive_summary = archive_summaries[0]
archive_counts = [n for n in archive_summary.children if 'gc-session-count' in n.attrs.get('class', '').split()]
require(len(archive_counts) == 1 and archive_counts[0].text().strip() == '37 messages · 4 sessions', 'archive count must remain as accessible summary text')
require(all('hidden' not in n.attrs and n.attrs.get('aria-hidden', '').lower() != 'true'
            and 'style' not in n.attrs for n in archive_summary.walk()),
        'archive summary/count must not be hidden from assistive technology or restyled inline')
require('April 2026 archive' in ' '.join(archive_summary.parts), 'archive title remains directly visible in its summary')
archive_nodes = list(archive.walk())
archive_cards = [n for n in archive_nodes if 'data-archive-talk' in n.attrs]
archive_groups = [n for n in archive_nodes if 'data-archive-session' in n.attrs]
require(len(archive_cards) == 37 and len(archive_groups) == 4, 'all April messages and four sessions must remain in the archive')
require(not any(k.startswith('data-conference-') for n in archive_nodes for k in n.attrs), 'October filtering must never alter archived April cards')
require(not any('hidden' in n.attrs for n in archive_cards + archive_groups), 'April remains available without JavaScript')
require(not any('data-exclusive-artwork' in n.attrs or 'data-full-image-viewer' in n.attrs for n in archive_nodes), 'archive must not duplicate owned artwork')
require('October 2026' in opening_header.text() and '38 messages' in opening_header.text() and 'April 2026' not in opening_header.text(), 'opening must identify the current October collection')
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
october_ids = '11christofferson 12gong 13runia 14causse 15sikahema 16hathaway 17soares 18douglas 19christofferson 21renlund 22farnes 23chigbundu 24giuffra 25morgan 26fale 27kearon 28dunn 29eyring 210rasband 41eyring 42chibota 43andersen 44fantone 45dube 46cook 47kyungu 48schmeil 49oaks 51uchtdorf 52munoz-spannaus 53villanueva 54bednar 55lebethoa 56sinclair 57stevenson 58reid 59gilbert 510oaks'.split()
require(ledger['official_collection'] == 'https://www.churchofjesuschrist.org/study/general-conference/2026/10?lang=eng' and ledger['item_count'] == 38, 'current ledger must identify October')
require([r['id'] for r in records] == october_ids, 'ledger must preserve exact official October order and identities')
require([c.attrs['data-conference-talk'] for c in cards] == october_ids, 'page must preserve exact official October order and identities')
sustaining_images = [n for n in cards[0].walk() if n.tag == 'img']
require(len(sustaining_images) == 1 and sustaining_images[0].attrs.get('width') == '768' and sustaining_images[0].attrs.get('height') == '512' and 'object-fit:contain' in sustaining_images[0].attrs.get('style', '').replace(' ', ''), 'native 3:2 sustaining preview must fit without cropping')
archive_records = ledger['archive']['items']
require(ledger['archive']['item_count'] == len(archive_records) == 37 and len({r['url'] for r in archive_records}) == 37, 'April archive ledger requires exactly 37 unique records')
april_ids = '11oaks 12christofferson 13kearon 14yee 15gilbert 16bednar 17teh 18becerra 19eyring 21christofferson 22larson 23stevenson 24ortega 25wu 26wunderli 27causse 28holmes 29matswagothata 210soares 41uchtdorf 42freeman 43larreal 44rowe 45rasband 46renlund 47mutombo 48walker 49oaks 51christofferson 52wong 53hall 54porter 55andersen 56cook 57wakolo 58gong 59oaks'.split()
require([r['id'] for r in archive_records] == april_ids and [c.attrs['data-archive-talk'] for c in archive_cards] == april_ids, 'exact ordered April archive identities must remain preserved')
require(ledger['archive']['official_collection'] == 'https://www.churchofjesuschrist.org/study/general-conference/2026/04?lang=eng', 'April archive collection URL must remain exact')
for record, period, collection in [(r, '10', cards) for r in records] + [(r, '04', archive_cards) for r in archive_records]:
    require('/2026/' + period + '/' in record['url'], 'message is filed under wrong conference: ' + record['id'])
    matches = [card for card in collection if any(n.tag == 'a' and n.attrs.get('href') == record['url'] for n in card.walk())]
    require(len(matches) == 1, 'message must appear in exactly one session: ' + record['id'])
    card = matches[0]
    period_groups = groups if period == '10' else archive_groups
    owners = [g for g in period_groups if card in list(g.walk())]
    require(len(owners) == 1 and record['session'].removesuffix(' Session') in owners[0].text(), 'message appears in wrong official session: ' + record['id'])
    normalized_text = ' '.join(card.text().split())
    speaker = record['speaker'].removeprefix('By ').removeprefix('Presented by ')
    require(record['title'] in normalized_text and speaker in normalized_text, 'published title/speaker differs from official source: ' + record['id'])
    search_key = 'data-conference-search' if period == '10' else 'data-archive-search'
    require(record['title'] in card.attrs[search_key] and speaker in card.attrs[search_key], 'title/speaker omitted from search: ' + record['id'])
    require(any(n.tag == 'img' and n.attrs.get('src') == record['local_thumbnail'] for n in card.walk()), 'preview/source mismatch: ' + record['id'])
    image = ROOT / record['local_thumbnail']
    require(hashlib.sha256(image.read_bytes()).hexdigest() == record['sha256'], 'source preview bytes changed: ' + record['id'])
for record in ledger.get('enduring_sources', []):
    require(any(n.tag == 'a' and n.attrs.get('href') == record['url'] for n in nodes), 'enduring source route missing: ' + record['id'])
    image = ROOT / record['local_thumbnail']
    require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == record['sha256'], 'enduring source preview changed: ' + record['id'])
print('GENERAL CONFERENCE QA PASS: 38 October messages, 37 preserved April archive records, exact source bindings, native sessions, isolated progressive filters, thumbnails and connected routes.')

if '--self-test' in sys.argv:
    # Exercise the real contract against isolated HTML values; never mutate the page.
    code = Path(__file__).read_text(encoding='utf-8').split("if '--self-test' in sys.argv:")[0]
    code = code.replace("source = (ROOT / 'general-conference.html').read_text(encoding='utf-8')", 'source = CANDIDATE')
    mutants = {
        'stale opening': source.replace('Explore the complete October 2026', 'Explore the complete April 2026', 1),
        'wrong current month': source.replace('/2026/10/11christofferson?', '/2026/04/11christofferson?', 1),
        'wrong current thumbnail': source.replace(records[0]['local_thumbnail'], archive_records[0]['local_thumbnail'], 1),
        'missing current record': source.replace('data-conference-talk="11christofferson"', 'data-missing-talk="11christofferson"', 1),
        'missing archived record': source.replace('data-archive-talk="11oaks"', 'data-missing-talk="11oaks"', 1),
        'archive leaks into search': source.replace('data-archive-talk="11oaks"', 'data-conference-talk="11oaks"', 1),
        'wrong archived month': source.replace('/2026/04/11oaks?', '/2026/10/11oaks?', 1),
        'archive opened initially': source.replace('id="conference-april-2026"', 'id="conference-april-2026" open', 1),
        'archive count aria-hidden': source.replace('<span class="gc-session-count">37 messages', '<span class="gc-session-count" aria-hidden="true">37 messages', 1),
        'archive count hidden': source.replace('<span class="gc-session-count">37 messages', '<span class="gc-session-count" hidden>37 messages', 1),
        'archive count removed': source.replace('<span class="gc-session-count">37 messages · 4 sessions</span>', '', 1),
        'archive count changed': source.replace('37 messages · 4 sessions', '36 messages · 4 sessions', 1),
        'cropped sustaining image': source.replace('object-fit:contain', 'object-fit:cover', 1),
        'stale conference CSS': source.replace('general-conference-section.css?v=' + CONFERENCE_VERSION, 'general-conference-section.css?v=20260927-anchor-alignment-1', 1),
    }
    for label, candidate in mutants.items():
        require(candidate != source, 'inactive negative fixture: ' + label)
        try:
            exec(compile(code, __file__, 'exec'), {'__file__': __file__, 'CANDIDATE': candidate})
        except SystemExit:
            continue
        raise SystemExit('GENERAL CONFERENCE QA FAIL: negative fixture accepted: ' + label)
    for mutation in (style_bytes[:-len(CONFERENCE_ROWS_APPENDIX)], style_bytes + CONFERENCE_ROWS_APPENDIX,
                     style_bytes.replace(b' of :not([hidden])', b'', 1),
                     style_bytes.replace(b'grid-column: span 3;', b'grid-column: span 2;', 1),
                     style_bytes.replace(b'#conference-results', b'.fc-conference-section', 1)):
        require(mutation != style_bytes, 'inactive filtered-row negative fixture')
        require(not reviewed_anchor_style('general-conference-section.css', mutation), 'filtered-row regression accepted')
    print('GENERAL CONFERENCE ROW SELF-TEST PASS: missing/duplicate correction, hidden-child counting, stranded pair and archive scope regressions rejected.')
    print(f'GENERAL CONFERENCE SELF-TEST PASS: {len(mutants)} stale/current/archive negative cases.')
