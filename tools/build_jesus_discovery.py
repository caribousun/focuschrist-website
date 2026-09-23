"""Regenerate nested journey discovery; draft discovery is not publication approval.

Run after rebuilding the journey HTML as artwork grows. Existing sitemap entries
are retained; only journey descendants are reconciled with the content manifest.
Release QA separately requires strict, indexable, complete reviewed pages.
"""
import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from build_art_gallery import build as gallery
from build_site_search import build as search

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://focuschrist.com'

def sitemap(text,pages):
    urls=[p['url'] for p in pages]
    if len(urls)!=76 or len(set(urls))!=76 or any(not re.fullmatch(r'/jesus-christ/[a-z0-9/-]+\.html',u) for u in urls):
        raise ValueError('Expected 76 unique nested journey destinations')
    expected={ORIGIN+u for u in urls}
    def keep(match):
        loc=re.search(r'<loc>(.*?)</loc>',match[0]).group(1)
        return '' if loc.startswith(ORIGIN+'/jesus-christ/') and loc not in expected else match[0]
    text=re.sub(r'\s*<url>.*?</url>',keep,text,flags=re.S)
    existing=[n.text for n in ET.fromstring(text).findall('{*}url/{*}loc')]
    if len(existing)!=len(set(existing)):raise ValueError('Duplicate existing sitemap destinations')
    additions=''.join('\n  <url><loc>'+u+'</loc></url>' for u in sorted(expected-set(existing)))
    return text.replace('</urlset>',additions+'\n</urlset>') if additions else text

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    pages=json.loads((ROOT/'docs/jesus-journey/pages.json').read_text(encoding='utf-8'))
    target=ROOT/'sitemap.xml';current=target.read_text(encoding='utf-8');expected=sitemap(current,pages)
    if args.check and expected!=current:raise SystemExit('Journey sitemap is stale')
    if not args.check:target.write_text(expected,encoding='utf-8',newline='\n')
    for name,value in [('art-gallery.json',gallery) ,('site-search-index.json',search)]:
        result=value()
        output=json.dumps(result,ensure_ascii=False,indent=2)+'\n' if name=='art-gallery.json' else json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n'
        target=ROOT/name
        if args.check:
            if target.read_text(encoding='utf-8')!=output:raise SystemExit('Stale discovery file '+name)
        else:target.write_text(output,encoding='utf-8',newline='\n')
    print('Journey discovery current: 76 nested destinations; accepted rendered artwork only. Draft release checks remain required.')

if __name__=='__main__':main()
