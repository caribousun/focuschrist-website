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
APPROVED_SPEC = '51fcc28a25bba1c9711371b204728df5fa7e4090191a75735b7725aec42600fe'
APPROVED_REVIEWS = '30b5f43bc98a28b677a281780912b8097e62c09b98bfe3183e813104a1e90ee3'
PREFIX = 'assets/world-scripture/'

# Exact compatibility hooks only; original display review evidence pins are retained.
REVIEWED_CODE_INVERSES = {'tools/artwork_display_delivery.py': {'current': '9d045de3c77661d77b3d932a8c108e68d250f21c5f4a22ae303e33964e2925f8', 'previous': 'ecce82fcd932502d3f5aedb5382432a151791e69ec9f3108c94dc8eedfe0e66f', 'spans': [(5615, 5848, ''), (12024, 12093, ''), (12105, 12141, ''), (12166, 12167, '')]}, 'tools/test_display_delivery.py': {'current': '57a795b8c57f943e74af4a253af9526c4f7db97c43f2142ca2566d4f86c3c6c8', 'previous': '387fea58b6096a09b4f939058b88b5dbf496f89b91a16b782d7ed0c93c69df47', 'spans': [(1470, 1607, ''), (1612, 1627, ''), (1670, 1797, '')]}}

NEW_SNIPPET = "        from artwork_display_delivery import inverse\\n        # Display-only Home sizes do not replace the gallery's full original.\\n        name = page.lstrip('/')\\n        if name == 'missionary.html':\\n            # The commission hand successor is a reviewed content delivery\\n            # change, not a presentation layer: the gallery records the\\n            # renditions the page actually serves, so parse it as served.\\n            doc.feed((ROOT / name).read_bytes().decode('utf-8'))\\n        else:\\n            doc.feed(inverse(name, (ROOT / name).read_bytes()).decode('utf-8'))"
OLD_SNIPPET = "        from artwork_display_delivery import inverse\\n        # Display-only Home sizes do not replace the gallery's full original.\\n        name = page.lstrip('/')\\n        doc.feed(inverse(name, (ROOT / name).read_bytes()).decode('utf-8'))"


def before_motion_code_evidence(name, data):
    if name == 'tools/artwork_display_delivery.py' and hashlib.sha256(data).hexdigest() == 'ae5f73d6f8f54e92257c7ae10df855c995c672496e49db24af3a9ef41e2ef6d8':
        # Undo only the exact gallery-builder inverse update registered with
        # the commission hand successor, then the motion strips below apply.
        text=data.decode('utf-8')
        require(text.count('4489874fcbe0aeac68eab1de36b9cd0739fec65ca3981edbb961ce236baa78a1') == 1, 'gallery builder inverse drift')
        text=text.replace('4489874fcbe0aeac68eab1de36b9cd0739fec65ca3981edbb961ce236baa78a1','1b0fdf7b8c97d949dea025e99cdf57a1f06c58fa69f53a61587ae9818b1228d5',1)
        require(text.count(NEW_SNIPPET) == 1, 'gallery builder snippet drift')
        text=text.replace(NEW_SNIPPET, OLD_SNIPPET, 1)
        text=text.replace('    from continue_motion_binding import restore as before_motion\n','',1).replace('require(sha(before_motion(name,(root / name).read_bytes())) == expected','require(sha((root / name).read_bytes()) == expected',1)
        data=text.encode('utf-8')
        require(hashlib.sha256(data).hexdigest() == '9d045de3c77661d77b3d932a8c108e68d250f21c5f4a22ae303e33964e2925f8', 'motion code predecessor drift')
    if name == 'tools/artwork_display_delivery.py' and hashlib.sha256(data).hexdigest() == '12c6ab0536a8f7992e707cf8bfb4feff2d391182912f9f5460b553e1a8ef1007':
        text=data.decode('utf-8')
        text=text.replace('    from continue_motion_binding import restore as before_motion\n','',1).replace('require(sha(before_motion(name,(root / name).read_bytes())) == expected','require(sha((root / name).read_bytes()) == expected',1)
        data=text.encode('utf-8')
        require(hashlib.sha256(data).hexdigest() == '9d045de3c77661d77b3d932a8c108e68d250f21c5f4a22ae303e33964e2925f8', 'motion code predecessor drift')
    return data

def restore_code_evidence(name, data):
    from continue_motion_binding import restore as before_motion
    data=before_motion(name,data)
    data=before_motion_code_evidence(name,data)
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

REVIEWED_CONSUMER_INVERSES['art-gallery.json'] = {'current': '0417ab54dfa01b62d925cc6d32f10acd5600f5cefc16d6b90708662a052a2824', 'previous': '5fb9f428a7e4bbf63cd9b5721ca7e576b14bbfa8334c073343f84e49efb8fcb1', 'edits': [['', '    "/timelines/world-and-scripture-timeline.html",\n'], ['/assets/missionary/christ-teaches-apostles-home-likeness-20260914-1100.webp', '/assets/missionary/christ-teaches-apostles-home-likeness-20260914-hand-repair-v2-1100.webp'], ['/assets/missionary/christ-teaches-apostles-home-likeness-20260914-full.webp', '/assets/missionary/christ-teaches-apostles-home-likeness-20260914-hand-repair-v2-full.webp'], ['art-3559c7c6b5f8', 'art-5e9eaab4f27d']]}

# Exact owner-requested navigation correction; compose before historical pins.
POLISH_CONSUMER_INVERSES = {'timeline-experiences.css': {'current': '4d76e920b978b14ffd360fc8007c848f7f39ca327408f50385b37a1ff7d3349b', 'previous': 'ea1726660d8b9fb9e7f679c05fee370748df99408876ab559eda2fda5d15253a', 'spans': [[11173, 11625, '']]}, 'timelines/willie-and-martin-handcart-map.html': {'current': '117057276965a37d668a2879b46e0810066fb94813436eb55253b647dd550de0', 'previous': '1ed6267e763ffbeecd1f897463688469546a97f31b29d78bff89fef5f45d2e0c', 'spans': [[108759, 108849, '<link rel="stylesheet" href="../timeline-experiences.css?v=20261020-intro-canvas-1">\n'], [163683, 163860, '']]}, 'timelines/life-of-christ-journey-map.html': {'current': '9d22d5bcc74289ed60b2000bceb53af8b89ea2afb2165fac39dc6b5be0968acf', 'previous': 'ce1f2fb1e17b1d333ff3f1340c3140abb6490357157c40c81c6ebdd22370fb5e', 'spans': [[10295, 10385, '<link rel="stylesheet" href="../timeline-experiences.css?v=20261020-intro-canvas-1">\n']]}, 'timelines/latter-day-saint-church-history-timeline.html': {'current': '6d3b5a98c83512547000f83e140c89d6db8baec9755337c7600d583cd02f1ac6', 'previous': '647c75794179cfaaf4b586011fe2a2e1e51c66563c470f7d8e930b136fcc4de8', 'spans': [[12698, 12789, '<link rel="stylesheet" href="../timeline-experiences.css?v=20261020-intro-canvas-1">\r\n']]}}

HANDCART_VIEWPORT_INVERSE = {'current': '98e10999411e9c9a6c610207013b3a10c810b249175fbdeb57aaf36234828cdb', 'previous': '117057276965a37d668a2879b46e0810066fb94813436eb55253b647dd550de0', 'spans': [[163206, 164446, 'window.HandcartTimeline={\r\n    select:function(index){\r\n      if(!Number.isInteger(index)||!STOPS[index])return;\r\n      if(!currentRows.some(function(r){return r.index===index;})){\r\n        filterGeneration++;currentFilter=\'all\';chips.forEach(function(c){c.setAttribute(\'aria-pressed\',String(c.getAttribute(\'data-filter\')===\'all\'));});rows=buildRows();mount(rows);\r\n      }\r\n      var row=currentRows.find(function(r){return r.index===index;});selectStop(index,row.el,false);\r\n      if(window.matchMedia("(min-width:901px)").matches){if(window.TimelineWorkspace)window.TimelineWorkspace.scrollRow(row.el);else row.el.scrollIntoView({block:"nearest"});}']]}

def before_handcart_viewport(name, data):
    from continue_motion_binding import restore as before_motion
    data=before_motion(name,data)
    binding=HANDCART_VIEWPORT_INVERSE
    if name != "timelines/willie-and-martin-handcart-map.html" or hashlib.sha256(data).hexdigest()!=binding["current"]:
        return data
    text=data.decode("utf-8")
    for start,end,previous in reversed(binding["spans"]):
        text=text[:start]+previous+text[end:]
    prior=text.encode("utf-8")
    require(hashlib.sha256(prior).hexdigest()==binding["previous"], "Handcart viewport predecessor drift")
    return prior

def before_navigation_polish(name, data):
    data=before_handcart_viewport(name, data)
    binding=POLISH_CONSUMER_INVERSES.get(name)
    if not binding or hashlib.sha256(data).hexdigest()!=binding['current']:
        return data
    text=data.decode('utf-8')
    for start,end,previous in reversed(binding['spans']):
        text=text[:start]+previous+text[end:]
    prior=text.encode('utf-8')
    require(hashlib.sha256(prior).hexdigest()==binding['previous'], 'navigation predecessor drift: '+name)
    return prior

# Only the exact reviewed current-source gallery builder can reconstruct its
# predecessor for historical delivery evidence. Unknown bytes are never normalized.
def before_current_gallery_builder(name, data):
    if name != 'tools/build_art_gallery.py' or hashlib.sha256(data).hexdigest() != 'c6a0354d6967ab85bf2a395a81cdb3bfdb5bb5e120b0acb72d03d7faebc74195':
        return data
    block = b'def gallery_source(name, raw, root=ROOT):\n    """Index actual reviewed Emma owners; historical projections stay historical."""\n    from owner_integration_contract import HUB, STORIES, CHART, INTRO, LANDING, validate_file\n    if name in {HUB, CHART, INTRO, LANDING, *STORIES}:\n        validate_file(name, raw, root)\n        return raw\n    from artwork_display_delivery import inverse\n    return inverse(name, raw)\n\n\n'
    current = b"doc.feed(gallery_source(name, (ROOT / name).read_bytes()).decode('utf-8'))"
    previous = b"doc.feed(inverse(name, (ROOT / name).read_bytes()).decode('utf-8'))"
    require(data.count(block) == data.count(current) == 1, 'gallery builder successor spans drift')
    prior = data.replace(block, b'', 1).replace(current, previous, 1)
    require(hashlib.sha256(prior).hexdigest() == '4489874fcbe0aeac68eab1de36b9cd0739fec65ca3981edbb961ce236baa78a1', 'gallery builder predecessor drift')
    return prior


def restore_consumers(name, data):
    """Reconstruct historical evidence only for a complete reviewed byte binding."""
    data = before_current_gallery_builder(name, data)
    from continue_motion_binding import restore as before_motion
    data = before_motion(name,data)
    data = before_navigation_polish(name, data)
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
    from adams_delivery_successor import restore as restore_adams_delivery
    data = restore_adams_delivery('site-search-index.json', data)
    from emma_generated_indices_successor import restore as restore_emma_indices
    data = restore_emma_indices('site-search-index.json', data)
    if hashlib.sha256(data).hexdigest() == '85c5c413d2a293b9e61bc569a63663d959472c1f085e9f9f86e35839eb4fc970':
        # Undo only the exact gallery picture id delta from the commission
        # hand successor, then the frozen route inverse below applies.
        require(data.count(b'art-5e9eaab4f27d') == 1, 'ambiguous gallery search inverse')
        require(data.count(b'christ-teaches-apostles-home-likeness-20260914-hand-repair-v2-1100.webp') == 1, 'ambiguous gallery search thumbnail inverse')
        data = data.replace(b'art-5e9eaab4f27d', b'art-3559c7c6b5f8', 1)
        data = data.replace(b'christ-teaches-apostles-home-likeness-20260914-hand-repair-v2-1100.webp', b'christ-teaches-apostles-home-likeness-20260914-1100.webp', 1)
        require(hashlib.sha256(data).hexdigest() == 'e7dcd184298a1fcc256e5733cb6a1080d1529f0119fb3e21e279b92c804a6f44', 'gallery search inverse failed binding')
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
    current=local(root,spec['page']['path']).read_bytes()
    from continue_motion_binding import restore as before_motion
    current=before_motion(spec['page']['path'],current)
    if hashlib.sha256(current).hexdigest()==spec['page']['sha256']:
        page=current.decode('utf-8')
    else:
        # A successor cannot rewrite historical import approval. Its separately
        # pinned finished evidence validates live reuse; old coverage still uses
        # the exact original page, including the two retained archival photos.
        from timeline_artwork_reuse import validate as validate_reuse
        try:
            prior=validate_reuse(root,current)
        except (ValueError, OSError, KeyError, TypeError) as error:
            raise ValueError('changed bytes: '+spec['page']['path']+'; successor evidence rejected: '+str(error)) from error
        require(hashlib.sha256(prior).hexdigest()==spec['page']['sha256'], 'wrong historical import baseline')
        page=prior.decode('utf-8')
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
