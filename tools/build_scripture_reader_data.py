#!/usr/bin/env python3
"""Build local scripture chapters from explicitly linked official English scripture URLs.

No inferred chapters, footnotes, headings, introductions or generated wording enter verse
text. Run again after adding scripture links; --check validates the existing catalog.
Requires Python standard library only. Network concurrency is bounded to six requests.
"""
import argparse, concurrent.futures, datetime, hashlib, html, json, pathlib, re, time, urllib.request
from html.parser import HTMLParser
ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 'https://www.churchofjesuschrist.org/study/scriptures/'
LEDGER = ROOT / 'docs/scripture-source-ledger.json'
PATTERN = re.compile(r'/study/scriptures/([a-z0-9-]+)/([a-z0-9-]+)/([0-9]+)(?=[.?/#\s"\'<>]|$)')
CANON = {'ot', 'nt', 'bofm', 'dc-testament', 'pgp'}
EXCLUDE = {'.git', 'node_modules', 'tools', 'scripture-data'}

class VerseParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.verses = []; self.current = None; self.parts = []; self.skip = 0; self.title = []; self.in_title = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self.in_title = True
        if tag == 'p' and 'verse' in a.get('class', '').split() and re.fullmatch(r'p\d+', a.get('id', '')):
            if self.current is not None: raise ValueError('Nested verse paragraph')
            self.current = int(a['id'][1:]); self.parts = []; self.skip = 0
        if self.current is not None:
            if self.skip: self.skip += 1
            elif tag == 'sup' or 'verse-number' in a.get('class', '').split(): self.skip = 1
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if self.current is not None:
            if self.skip: self.skip -= 1
            elif tag == 'p':
                text = re.sub(r'\s+', ' ', ''.join(self.parts)).strip()
                if not text: raise ValueError('Empty verse')
                self.verses.append({'number': self.current, 'text': text}); self.current = None
    def handle_data(self, data):
        if self.in_title: self.title.append(data)
        if self.current is not None and not self.skip: self.parts.append(data)

def discover():
    refs = {}; skipped = {}
    for p in sorted(ROOT.rglob('*')):
        rel = p.relative_to(ROOT)
        if p.suffix not in {'.html', '.js'} or EXCLUDE.intersection(rel.parts) or p.name.endswith('.test.js') or p.name == 'church-source-index.js': continue
        text = html.unescape(p.read_text(encoding='utf-8', errors='replace')).replace('\\/', '/')
        for m in PATTERN.finditer(text):
            key = '/'.join(m.groups())
            if m[1] in CANON: refs.setdefault(key, set()).add(str(rel))
        for m in re.finditer(r'/study/scriptures/([^\s"\'<>?#]+)', text):
            key = m[1].rstrip('/')
            if re.fullmatch(r'[a-z0-9/-]+', key) and key not in refs and not PATTERN.match('/study/scriptures/' + key): skipped.setdefault(key, set()).add(str(rel))
    return {k: sorted(v) for k,v in sorted(refs.items())}, {k: sorted(v) for k,v in sorted(skipped.items())}

def validate(data):
    nums = [v['number'] for v in data['verses']]
    if not nums or nums != list(range(1, len(nums)+1)): raise ValueError('Missing, duplicated or noncontiguous verse numbers: '+str(nums))
    if any(not v['text'] or re.search(r'<[^>]+>',v['text']) for v in data['verses']): raise ValueError('Invalid verse text')

def fetch(key, files, previous, refresh=False):
    url = BASE + key + '?lang=eng'; target = ROOT / 'scripture-data' / (key + '.json')
    if not refresh and target.exists() and previous and previous.get('status') == 'verified':
        raw = target.read_bytes(); data = json.loads(raw); validate(data)
        if hashlib.sha256(raw).hexdigest() == previous.get('data_sha256') and data['source_url'] == url:
            return dict(previous, linked_from=files)
    error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent':'focusChrist scripture source verification/1.0'})
            with urllib.request.urlopen(request,timeout=25) as response:
                raw = response.read(); status = response.status; final_url = response.url
            if final_url.split('?')[0].rstrip('/') != url.split('?')[0]: raise ValueError('Unexpected source redirect: '+final_url)
            parser = VerseParser(); parser.feed(raw.decode('utf-8'))
            data = {'title':html.unescape(''.join(parser.title)).strip(), 'source_url':url, 'verses':parser.verses, 'verified_on':datetime.date.today().isoformat()}
            validate(data)
            target.parent.mkdir(parents=True,exist_ok=True)
            payload = (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'); target.write_bytes(payload)
            return {'chapter':key,'status':'verified','source_url':url,'http_status':status,'source_html_sha256':hashlib.sha256(raw).hexdigest(),'data_sha256':hashlib.sha256(payload).hexdigest(),'verse_count':len(data['verses']),'verified_on':data['verified_on'],'linked_from':files}
        except Exception as exc:
            error = str(exc)
            if attempt < 2: time.sleep(attempt+1)
    return {'chapter':key,'status':'unavailable','source_url':url,'error':error,'linked_from':files}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--refresh',action='store_true'); args=ap.parse_args()
    refs, skipped = discover()
    prior = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    previous = {v['chapter']:v for v in prior.get('chapters',[])}
    if args.check:
        failures=[]
        for key in refs:
            try:
                p=ROOT/'scripture-data'/(key+'.json'); raw=p.read_bytes(); d=json.loads(raw); validate(d)
                assert d['source_url']==BASE+key+'?lang=eng'
                assert hashlib.sha256(raw).hexdigest()==previous[key]['data_sha256']
            except Exception as exc: failures.append(key+': '+str(exc))
        print(json.dumps({'linked_chapters':len(refs),'failures':failures},indent=2)); return bool(failures)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(fetch,k,v,previous.get(k),args.refresh):k for k,v in refs.items()}
        for f in concurrent.futures.as_completed(futures):
            result=f.result();results.append(result);print(result['status'],result['chapter'],result.get('verse_count',result.get('error')),flush=True)
    ledger={'schema_version':1,'generated_on':datetime.date.today().isoformat(),'extraction':'Official English canonical verse paragraphs only; verse-number spans and superscript footnote markers removed; text-node order and punctuation preserved; whitespace normalized; sequential verse numbers required. No headings, summaries or footnotes.','discovery':'Explicit canonical chapter paths in deployed HTML and runtime JS, including proxy runtime; excludes tests, tools and unused church-source-index.js.','chapters':sorted(results,key=lambda x:x['chapter']),'skipped_nonchapter_links':skipped}
    LEDGER.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
    return any(r['status']!='verified' for r in results)
if __name__=='__main__':raise SystemExit(main())
