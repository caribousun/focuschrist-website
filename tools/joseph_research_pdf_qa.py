"""Independently compare the illustrated PDF with the current research page."""
from pathlib import Path
import copy, hashlib, json, re, sys, unicodedata
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import fitz
from joseph_research_acceptance import check_artwork_disclosure_text

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'joseph-smith-portrait-research.html'
PDF = ROOT / 'assets/research/focuschrist-joseph-evidence.pdf'
BASE = 'https://focuschrist.com/joseph-smith-portrait-research.html'

def norm(value):
    value = unicodedata.normalize('NFKD', value).casefold()
    return ''.join(c for c in value if c.isalnum())

def navigation_checks(document):
    """Inspect actual PDF annotations and painted labels, not builder receipts."""
    titles = {norm(row[1]): row[2]-1 for row in document.get_toc()}
    destinations = [('Cover', 0), ('Contents', titles.get(norm('Contents'))),
        ('Evidence', titles.get(norm('Masks and life-derived art'))),
        ('Facial Features', titles.get(norm('Trait audit: facial structure'))),
        ('Creation', titles.get(norm('How our portrait was created'))),
        ('Sources', titles.get(norm('Sources: original records and art')))]
    failures, cue_failures, panel_failures = [], [], []
    checked_buttons = checked_source_links = 0
    for number, page in enumerate(document, 1):
        links = page.get_links()
        header = [x for x in links if x['from'].y0 < 60 and x['from'].y1 > 30]
        if len(header) != 6:
            failures.append({'page':number,'error':'expected six header annotations','actual':len(header)})
        header.sort(key=lambda x:x['from'].x0)
        for i, (label, target) in enumerate(destinations):
            if i >= len(header): continue
            link = header[i]; box = link['from']
            expected = fitz.Rect(49+i*86.5, 36, 49+i*86.5+81.5, 53)
            if any(abs(a-b)>1 for a,b in zip(box,expected)):
                failures.append({'page':number,'button':label,'error':'incorrect or overlapping hit rectangle'})
            painted = page.get_textbox(box + (-2,-2,2,2)).strip()
            if norm(painted) != norm(label):
                failures.append({'page':number,'button':label,'error':'missing painted label','actual':painted})
            if target is None or link.get('kind') != fitz.LINK_GOTO or link.get('page') != target:
                failures.append({'page':number,'button':label,'error':'wrong internal destination','expected_page':target})
            checked_buttons += 1
        # Running title sits above the controls; actual body starts at76pt.
        # Leave tolerance for ascenders while rejecting text painted in the gap.
        gap_words=[w[4] for w in page.get_text('words') if w[1] >= 54 and w[1] < 67]
        if gap_words: failures.append({'page':number,'error':'body/header overlap','words':gap_words})
        body_words = [w for w in page.get_text('words') if 67 <= w[1] < 750]
        for word in body_words:
            if word[1] < 88 or word[3] > 733 or word[0] < 45 or word[2] > 567:
                panel_failures.append({'page':number,'word':word[4],'bbox':list(word[:4]),'error':'body text lacks panel inset'})
        spans=[span for b in page.get_text('dict')['blocks'] if 'lines' in b
               for line in b['lines'] for span in line['spans']]
        # A wrapped URL may create several rectangles; inspect them as one
        # semantic link. Image-only links need no text arrow; the front key
        # explicitly explains that an image opens the complete source.
        uri_groups={}
        for link in links:
            if link.get('uri'): uri_groups.setdefault(link['uri'],[]).append(link['from'])
        for uri, boxes in uri_groups.items():
            painted=[span for span in spans if any(fitz.Rect(span['bbox']).intersects(box) for box in boxes)]
            if not painted: continue
            checked_source_links += 1
            if not any('↗' in span['text'] for span in painted):
                cue_failures.append({'page':number,'uri':uri,'error':'external text link lacks visible arrow'})
    front='\n'.join(p.get_text() for p in list(document)[:3]).casefold()
    if not all(word in front for word in ('buttons','arrow','link','source')):
        cue_failures.append({'error':'front navigation/link key missing'})
    return {'header_buttons_checked':checked_buttons,'header_navigation_errors':failures,
            'external_text_links_checked':checked_source_links,'link_cue_errors':cue_failures,
            'panel_clearance_errors':panel_failures}

def navigation_self_test():
    """Mutate extracted data from real PDF pages; never alter the artifact."""
    document = fitz.open(PDF)
    probe_pages = list(document)[:3]
    probe_pages.append(next(p for p in document if '↗' in p.get_text() and any(x.get('uri') for x in p.get_links())))
    class PageProbe:
        def __init__(self, page, fault): self.page, self.fault = page, fault
        def get_links(self):
            links = copy.deepcopy(self.page.get_links())
            if self.fault == 'missing': links.pop(0)
            if self.fault == 'destination': links[0]['page'] = -1
            if self.fault == 'rectangle': links[0]['from'] = fitz.Rect(0,36,81.5,53)
            return links
        def get_textbox(self, box): return self.page.get_textbox(box)
        def get_text(self, kind='text'):
            value = self.page.get_text(kind)
            if kind == 'words' and self.fault == 'inset':
                value.append((49,74,90,84,'Overlap',0,0,0))
            if kind == 'dict' and self.fault == 'cue':
                for block in value['blocks']:
                    for line in block.get('lines',[]):
                        for span in line['spans']: span['text'] = span['text'].replace('↗','')
            return value
    class DocumentProbe:
        def __init__(self, fault): self.fault = fault
        def get_toc(self): return document.get_toc()
        def __iter__(self): return (PageProbe(p,self.fault) for p in probe_pages)
    baseline = navigation_checks(DocumentProbe(None))
    assert not any(baseline[k] for k in ('header_navigation_errors','link_cue_errors','panel_clearance_errors')), baseline
    for fault, key in [('missing','header_navigation_errors'),('destination','header_navigation_errors'),
                       ('rectangle','header_navigation_errors'),('inset','panel_clearance_errors'),('cue','link_cue_errors')]:
        assert navigation_checks(DocumentProbe(fault))[key], f'Undetected navigation fault: {fault}'
    print('PASS: valid navigation plus five missing/destination/rectangle/inset/cue negative fixtures')

def main():
    soup = BeautifulSoup(HTML.read_text(encoding='utf-8'), 'html.parser')
    roots = soup.select('section.research-part, section.research-study-onward')
    assert len(soup.select('section.research-part')) == 15
    assert len(soup.select('.research-feature-study')) == 16
    document = fitz.open(PDF)
    navigation = navigation_checks(document)
    heading_texts = {norm(x.get_text(' ',strip=True)) for root in roots for x in root.select('h2,h3,h4')}
    heading_texts.add(norm('What this can and cannot tell us'))
    orphan_headings = []
    for number, page in enumerate(document,1):
        lines = [line for block in page.get_text('dict')['blocks'] for line in block.get('lines',[])
                 if 67 <= line['bbox'][1] < 750]
        lines = [line for line in lines if not re.fullmatch(r'\d+theresearch|lookcloselyfollowtheevidence',
                 norm(''.join(span['text'] for span in line['spans'])))]
        if lines:
            last = max(lines,key=lambda line:line['bbox'][3])
            value = ''.join(span['text'] for span in last['spans'])
            if norm(value) in heading_texts:
                orphan_headings.append({'page':number,'heading':value})
    text = '\n'.join(page.get_text() for page in document)
    check_artwork_disclosure_text(text)
    normalized = norm(text)
    missing = []
    checked = 0
    for root in roots:
        for element in root.select('h2,h3,h4,p,td,th,li,dt,dd'):
            # Repeated web section/feature eyebrows are replaced by book running
            # heads and section numbers; they carry no research content.
            if element.find_parent('nav') or 'fc-eyebrow' in element.get('class', []):
                continue
            value = element.get_text(' ', strip=True)
            if len(norm(value)) < 4:
                continue
            checked += 1
            if norm(value) not in normalized:
                missing.append(value)
    links = [link for page in document for link in page.get_links()]
    actual_uris = {link.get('uri') for link in links if link.get('uri')}
    expected_uris = {urljoin(BASE, a['href']) for root in roots for a in root.select('a[href]')
                     if not a['href'].startswith('#') and not a.find('img') and not a.find_parent('nav')}
    missing_uris = sorted(expected_uris - actual_uris)
    original_uris = {urljoin(BASE, figure.select_one('a:has(img)')['href'])
                     for figure in soup.select('figure[data-research-art]')}
    missing_original_uris = sorted(original_uris - actual_uris)
    image_placements = sum(len(p.get_image_info()) for p in document)
    expected_image_placements = len(soup.select('figure')) + 1  # Cover portrait.
    bookmarks = document.get_toc()
    expected_bookmarks = 1 + len(soup.select('section.research-part')) + len(soup.select('.research-feature-study')) + 1
    bad_internal = [x for x in links if x.get('kind') == fitz.LINK_GOTO and not 0 <= x.get('page', -1) < len(document)]
    empty_pages = [i+1 for i,p in enumerate(document) if len(norm(p.get_text())) < 15 and not p.get_images()]
    out_of_bounds = []
    for i,page in enumerate(document):
        for word in page.get_text('words'):
            if word[0] < -1 or word[1] < -1 or word[2] > page.rect.width+1 or word[3] > page.rect.height+1:
                out_of_bounds.append({'page':i+1,'word':word[4]})
    report = {'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
              'html_sha256':hashlib.sha256(HTML.read_bytes()).hexdigest(),
              'pages':len(document),'substantive_text_blocks_checked':checked,
              'missing_text':missing,'expected_external_links':len(expected_uris),
              'missing_external_links':missing_uris,'link_annotations':len(links),
              'bad_internal_links':bad_internal,'empty_pages':empty_pages,
              'out_of_page_text':out_of_bounds,'bookmarks':len(bookmarks),
              'expected_bookmarks':expected_bookmarks,
              'image_placements':image_placements,'expected_image_placements':expected_image_placements,
              'original_image_links':len(original_uris),'missing_original_image_links':missing_original_uris,
              'limits':'Text/link/geometry checks do not replace independent rendered-page visual review.'}
    report['pass'] = not (missing or missing_uris or missing_original_uris or bad_internal or empty_pages or out_of_bounds) and image_placements == expected_image_placements and len(bookmarks) == expected_bookmarks and len(original_uris) == 10
    report.update(navigation)
    report['orphan_headings'] = orphan_headings
    report['pass'] = report['pass'] and not (navigation['header_navigation_errors'] or navigation['link_cue_errors'] or navigation['panel_clearance_errors'] or orphan_headings)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    assert report['pass'], 'PDF is incomplete or has invalid links/page geometry'

if __name__ == '__main__':
    navigation_self_test() if '--self-test' in sys.argv else main()
