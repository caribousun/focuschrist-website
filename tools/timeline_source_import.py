"""Exact reviewed import of existing timeline media, not generated-art preflight.

This separate coverage retains every existing creation/baseline gate. Source
photographs, an owner-selected existing hero and vendor decoding probes have
different provenance; none is presented as a newly generated scene.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

MANIFEST = 'docs/world-scripture-import/delivery.json'
PAGE = 'timelines/world-and-scripture-timeline.html'
APPROVED_SPEC = '2338edd6dd216dd370670d9698a074c811a04680453962350d3f37b4ea4c401c'
APPROVED_REVIEWS = '8efc67e6a14aef3595ddefeedcb19c6b46a4383b9a311a90aee8082854374925'
PREFIX = 'assets/world-scripture/'

def require(ok, message):
    if not ok:
        raise ValueError('Timeline source import: ' + message)

def canonical(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def local(root, name):
    require(isinstance(name,str) and '\\' not in name and not name.startswith('/') and '..' not in Path(name).parts, 'unsafe path')
    p=root/name
    require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), 'missing or unsafe file: '+name)
    return p

def bound_file(root, item):
    p=local(root,item['path']);raw=p.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==item['sha256'], 'changed bytes: '+item['path'])
    return raw

def validate(root, added, covered, rejected, expected=APPROVED_SPEC, expected_reviews=APPROVED_REVIEWS):
    record=json.loads(local(root,MANIFEST).read_text(encoding='utf-8'))
    require(record.get('schema')==1 and record.get('status')=='REVIEWED_EXACT_SOURCE_IMPORT', 'unfinished record')
    spec=record['spec']
    require(canonical(spec)==expected, 'unreviewed exact specification')
    require(spec.get('precreation_claim') is False and spec.get('kind')=='EXISTING_TIMELINE_MEDIA', 'misclassified creation')
    require(spec['page']['path']==PAGE, 'wrong owning page')
    page=bound_file(root,spec['page']).decode('utf-8')
    credits=json.loads(bound_file(root,spec['credits']).decode('utf-8'))
    require(spec['credits']['path']=='docs/world-scripture-import/photo-credits.json' and len(credits)==193, 'wrong credit inventory')
    require(spec['archive_sha256']=='034a982736431a818956851a00b0dcd568c84707f435b826cc7065e43690bc1b', 'changed source archive')
    bound_file(root,spec['lineage'])
    assets=spec['assets'];paths={a['path'] for a in assets}
    require(len(assets)==len(paths)==197, 'missing or duplicate asset')
    require(Counter(a['role'] for a in assets)=={'source-photo':193,'existing-hero':1,'vendor-probe':3}, 'incorrect provenance roles')
    require(paths<=added and not paths&covered, 'overlapping or absent coverage')
    from PIL import Image
    for a in assets:
        require(re.fullmatch(r'assets/world-scripture/[0-9a-f]{64}\.(jpg|png|webp|gif)',a['path']) is not None, 'noncanonical asset path')
        raw=bound_file(root,a)
        require(a['sha256'] not in rejected and Path(a['path']).stem==a['sha256'] and len(raw)==a['bytes'], 'rejected or renamed bytes')
        with Image.open(local(root,a['path'])) as image:
            require(list(image.size)==a['dimensions'], 'changed dimensions')
            image.verify()
        require('/'+a['path'] in page, 'unconsumed asset')
        if a['role']=='source-photo':
            require('/'+a['path'] in credits, 'missing photo attribution')
            c=credits['/'+a['path']]
            require(all(c.get(k) for k in ['title','author','license','source','original','notice']), 'incomplete attribution')
            require(bool(c.get('license_url')) or c['license']=='Public domain', 'missing license URL without reviewed public-domain status')
            require(c['source'].startswith('https://commons.wikimedia.org/wiki/File:'), 'missing original file page')
            require(canonical(c)==a['credit_sha256'], 'unreviewed attribution')
    # The actual browser tests cover the card and image-dialog consumers. These
    # exact source checks prevent their accidental removal from this delivery.
    require('const PHOTO_CREDITS = ' in page and 'photoCreditMarkup(e)' in page and 'id="photo-credits"' in page, 'missing visitor credits')
    require(len(spec['licenses'])==3, 'missing bundled license')
    for item in spec['licenses']:
        bound_file(root,item)
        require('/'+item['path'] in page, 'license not reachable')
    reviews=record['reviews']
    require(canonical(reviews)==expected_reviews, 'unreviewed finished receipts')
    require(len(reviews)==3 and {r['reviewer'] for r in reviews}=={'Albert','Fermi','Newton'}, 'missing independent finished review')
    for review in reviews:
        require(review.get('decision')=='CONCUR' and review.get('spec_sha256')==expected, 'stale or negative review')
        require(review.get('finished_pixels') is True and review.get('source_rights_checked') is True, 'unperformed review')
        bound_file(root,review['evidence'])
    return paths
