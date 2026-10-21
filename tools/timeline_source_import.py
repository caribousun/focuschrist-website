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
APPROVED_SPEC = '873cefc4d5de61071db6186ff325c17e2fd7b4c16735f5054f0f9d30a075db32'
APPROVED_REVIEWS = '34ba7eca7a13d034016cfbdaedcfc6bd16faa9bc679697df6f0c805f58b6f898'
PREFIX = 'assets/world-scripture/'

# Exact compatibility hooks only; original display review evidence pins are retained.
REVIEWED_CODE_INVERSES = {'tools/artwork_display_delivery.py': {'current': '9d045de3c77661d77b3d932a8c108e68d250f21c5f4a22ae303e33964e2925f8', 'previous': 'ecce82fcd932502d3f5aedb5382432a151791e69ec9f3108c94dc8eedfe0e66f', 'spans': [(5615, 5848, ''), (12024, 12093, ''), (12105, 12141, ''), (12166, 12167, '')]}, 'tools/test_display_delivery.py': {'current': '57a795b8c57f943e74af4a253af9526c4f7db97c43f2142ca2566d4f86c3c6c8', 'previous': '387fea58b6096a09b4f939058b88b5dbf496f89b91a16b782d7ed0c93c69df47', 'spans': [(1470, 1607, ''), (1612, 1627, ''), (1670, 1797, '')]}}

def restore_code_evidence(name, data):
    binding = REVIEWED_CODE_INVERSES.get(name)
    if not binding or hashlib.sha256(data).hexdigest() != binding['current']:
        return data
    text = data.decode('utf-8')
    for start, end, previous in reversed(binding['spans']):
        text = text[:start] + previous + text[end:]
    restored = text.encode('utf-8')
    require(hashlib.sha256(restored).hexdigest() == binding['previous'], 'historical code evidence drift: '+name)
    return restored

# Exact previously reviewed introduction corrections; historical pins stay immutable.
REVIEWED_CONSUMER_INVERSES = {'timeline-experiences.css': {'current': 'ea1726660d8b9fb9e7f679c05fee370748df99408876ab559eda2fda5d15253a', 'previous': '4ae767e376478f2cdb16c3085ffa519a7a458314ed81aad2c662ec281ab82e5c', 'edits': [['body.fc-timeline-experience .timeline-life-intro{box-sizing:border-box;min-height:max(0px,calc(100dvh - 52px - 33.3984375vw + 8px));padding:clamp(8px,1.25dvh,14px) 0 24px;background:#10252d}', 'body.fc-timeline-experience .timeline-life-intro{box-sizing:border-box;min-height:max(0px,calc(100dvh - 52px - 33.3984375vw + 8px));padding:clamp(8px,1.25dvh,14px) 0 24px;background:transparent}'], ['body.fc-timeline-experience .timeline-life-intro .kicker{color:#f0c36a;background:#10252d;line-height:1.5}', 'body.fc-timeline-experience .timeline-life-intro .kicker{color:#f0c36a;background:transparent;line-height:1.5}'], ['body.fc-timeline-experience .timeline-history-opening-copy{background:#10252d;border-radius:14px;padding:24px; margin-block:24px;max-width:1080px}', 'body.fc-timeline-experience .timeline-history-opening-copy{background:transparent;border-radius:14px;padding:24px; margin-block:24px;max-width:1080px}'], ['body.fc-timeline-experience .timeline-history-opening-copy .kicker{color:#f0c36a;background:#10252d;line-height:1.5}', 'body.fc-timeline-experience .timeline-history-opening-copy .kicker{color:#f0c36a;background:transparent;line-height:1.5}']]}, 'timelines/latter-day-saint-church-history-timeline.html': {'current': '647c75794179cfaaf4b586011fe2a2e1e51c66563c470f7d8e930b136fcc4de8', 'previous': 'e5ed96eb0d69768241a55ccadc693c5066bc09953ced618ecc3c7e5113f3b72e', 'edits': [['Continue below <span aria-hidden="true">&#8595;</span>', 'Continue <span aria-hidden="true">&#8595;</span>'], ['../timeline-experiences.css?v=20261007-timeline-panels-1', '../timeline-experiences.css?v=20261020-intro-canvas-1']]}, 'timelines/life-of-christ-journey-map.html': {'current': 'ce1f2fb1e17b1d333ff3f1340c3140abb6490357157c40c81c6ebdd22370fb5e', 'previous': '7a003eb4ed27d65f08e3983650473aadb5d09800c3991d60c6d5cd8dfc40910f', 'edits': [['Continue below <span aria-hidden="true">&#8595;</span>', 'Continue <span aria-hidden="true">&#8595;</span>'], ['../timeline-experiences.css?v=20261007-timeline-panels-1', '../timeline-experiences.css?v=20261020-intro-canvas-1']]}, 'timelines/willie-and-martin-handcart-map.html': {'current': '1ed6267e763ffbeecd1f897463688469546a97f31b29d78bff89fef5f45d2e0c', 'previous': 'fe8e1610154b47e2d92c85c5fe7627e4a8655db252d105efed1bffbcd94b7269', 'edits': [['Continue below <span aria-hidden="true">&#8595;</span>', 'Continue <span aria-hidden="true">&#8595;</span>'], ['../timeline-experiences.css?v=20261007-timeline-panels-1', '../timeline-experiences.css?v=20261020-intro-canvas-1']]}}

REVIEWED_CONSUMER_INVERSES['art-gallery.json'] = {'current': '2fc81791182ae590d34b9d926d63aa4b794b0bba5b1f30691f1f4660b0251be9', 'previous': '5fb9f428a7e4bbf63cd9b5721ca7e576b14bbfa8334c073343f84e49efb8fcb1', 'edits': [['', '    "/timelines/world-and-scripture-timeline.html",\n']]}

def restore_consumers(name, data):
    """Reconstruct historical evidence only for a complete reviewed byte binding."""
    binding = REVIEWED_CONSUMER_INVERSES.get(name)
    if not binding or hashlib.sha256(data).hexdigest() != binding['current']:
        return data
    text = data.decode('utf-8')
    for previous, current in reversed(binding['edits']):
        require(text.count(current) == 1, 'ambiguous reviewed consumer inverse: '+name)
        text = text.replace(current, previous, 1)
    restored = text.encode('utf-8')
    require(hashlib.sha256(restored).hexdigest() == binding['previous'], 'historical consumer predecessor drift: '+name)
    return restored

def restore_search(data):
    """Undo only the exact generated search record for this new route."""
    if hashlib.sha256(data).hexdigest() != 'e7dcd184298a1fcc256e5733cb6a1080d1529f0119fb3e21e279b92c804a6f44':
        return data
    index = json.loads(data)
    route = '/timelines/world-and-scripture-timeline.html'
    require(index['pages'].count(route) == 1, 'ambiguous search page')
    require(sum(row.get('url') == route for row in index['records']) == 1, 'ambiguous search record')
    index['pages'].remove(route)
    index['records'] = [row for row in index['records'] if row.get('url') != route]
    handcart = [row for row in index['records'] if row.get('url') == '/timelines/willie-and-martin-handcart-map.html']
    phrase = 'dates. Continue Two companies'
    require(len(handcart) == 1 and handcart[0]['text'].count(phrase) == 1, 'ambiguous handcart search wording')
    handcart[0]['text'] = handcart[0]['text'].replace(phrase, 'dates. Continue below Two companies', 1)
    restored = (json.dumps(index, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
    require(hashlib.sha256(restored).hexdigest() == '038391c9f469c4c7a24894c629b915851ec097d305e880bdfe12e6f24b3c9e0d', 'search predecessor drift')
    return restored

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
        with Image.open(local(root,a['path'])) as image:
            image.load()
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
