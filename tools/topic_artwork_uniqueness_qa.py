#!/usr/bin/env python3
"""Require five contextual body artworks per study page, exclusive across public HTML.

Responsive sizes/formats, exact bytes and decoded RGBA pixels share an identity. Source-review
records also join differently named published derivatives of one original.
This gate does not grant visual approval to an unreviewed or altered image.
"""
import hashlib,json,re,sys
from pathlib import Path
from PIL import Image, ImageOps
from urllib.parse import urlsplit,unquote
from answer_study_qa import Document
from topic_body_picture_qa import ancestors
ROOT=Path(__file__).resolve().parents[1]
EXT={'.jpg','.jpeg','.png','.webp','.avif','.gif','.svg'}

def family_name(path):
    p=Path(path)
    stem=re.sub(r'-(?:desktop|mobile|tablet)(?:-v\d+)?$','',p.stem)
    stem=re.sub(r'-\d{3,4}(?:w)?$','',stem)
    return (p.parent/stem).as_posix().lower()

def public_pages(root=ROOT):
    excluded={'.git','.github','node_modules','.venv','venv','work','outputs','tools','tests'}
    return sorted(p for p in root.rglob('*.html') if not (set(p.relative_to(root).parts)&excluded))

def local_asset(page,value,root=ROOT):
    u=urlsplit(value)
    if u.netloc and u.netloc not in {'focuschrist.com','www.focuschrist.com'}:return None
    if u.scheme and u.scheme not in {'http','https'}:return None
    path=unquote(u.path)
    if Path(path).suffix.lower() not in EXT:return None
    candidate=(root/path.lstrip('/') if path.startswith('/') or u.netloc else page.parent/path).resolve()
    try:return candidate.relative_to(root.resolve()).as_posix()
    except ValueError:return None

def scan(root=ROOT):
    pages=public_pages(root);parsed={};references=[];asset_paths=set();asset_issues={}
    def add_reference(page, value, key, tag, attr):
        asset=local_asset(page,value,root)
        if asset:
            asset_paths.add(asset);references.append({'page':key,'asset':asset,'tag':tag,'attribute':attr})
    def script_refs(text, page, key):
        # Literal image URLs used by DOM image/detail setters resolve against the document.
        # Computed template paths require the separate browser interaction gate.
        for value in re.findall(r"[\"'`]([^\"'`\n]+\.(?:png|jpe?g|webp|avif|gif|svg)(?:[?#][^\"'`\n]*)?)[\"'`]",text,re.I):
            if '${' not in value:add_reference(page,value,key,'script','literal-image-url')
    def css_refs(file, key, seen):
        if file in seen or not file.is_file():return
        seen.add(file)
        text=file.read_text(encoding='utf-8')
        for value in re.findall(r'url\([\s\"\']*([^\)\"\']+)',text):
            add_reference(file,value,key,'stylesheet','css-url')
        for value in re.findall(r'@import\s+(?:url\()?\s*[\"\']([^\"\']+)',text):
            child=local_file(file,value,{'.css'})
            if child:css_refs(child,key,seen)
    def local_file(page,value,extensions):
        u=urlsplit(value)
        if u.netloc and u.netloc not in {'focuschrist.com','www.focuschrist.com'}:return None
        if u.scheme and u.scheme not in {'http','https'}:return None
        path=unquote(u.path)
        if Path(path).suffix.lower() not in extensions:return None
        candidate=(root/path.lstrip('/') if path.startswith('/') or u.netloc else page.parent/path).resolve()
        if candidate.is_relative_to(root.resolve()):return candidate
    for page in pages:
        d=Document();d.feed(page.read_text(encoding='utf-8'));nodes=list(d.root.walk());key=page.relative_to(root).as_posix();parsed[key]=nodes
        for n in nodes:
            if n.tag=='link' and 'stylesheet' in n.attrs.get('rel','').split():
                css=local_file(page,n.attrs.get('href',''),{'.css'})
                if css:css_refs(css,key,set())
            if n.tag=='script':
                js=local_file(page,n.attrs.get('src',''),{'.js'})
                script_refs(js.read_text(encoding='utf-8') if js and js.is_file() else n.text(),page,key)
            if n.tag=='style':
                for value in re.findall(r'url\([\s\"\']*([^\)\"\']+)',n.text()):
                    asset=local_asset(page,value,root)
                    if asset:
                        asset_paths.add(asset);references.append({'page':key,'asset':asset,'tag':'style','attribute':'css-url'})
            for attr,value in n.attrs.items():
                values=[]
                if attr=='style':values=re.findall(r'url\([\s\"\']*([^\)\"\']+)',value)
                elif isinstance(value,str):
                    # Includes hidden artwork detail records and future image attrs.
                    values=[v.strip().split()[0] for v in value.split(',') if v.strip()] if 'srcset'in attr else [value]
                for value in values:
                    asset=local_asset(page,value,root)
                    if asset:
                        asset_paths.add(asset);references.append({'page':key,'asset':asset,'tag':n.tag,'attribute':attr})
    parent={a:a for a in asset_paths}
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    def union(a,b):
        if a in parent and b in parent:parent[find(b)]=find(a)
    names={};digests={};pixels={};lineages={};file_hashes={};pixel_hashes={}
    for asset in sorted(asset_paths):
        file=root/asset
        if not file.is_file():
            asset_issues[asset]='Missing public image asset';continue
        sha=hashlib.sha256(file.read_bytes()).hexdigest();file_hashes[asset]=sha
        if sha in digests:union(asset,digests[sha])
        digests[sha]=asset
        try:
            if file.suffix.lower()!='.svg':
                with Image.open(file) as image:
                    rgb=ImageOps.exif_transpose(image).convert('RGBA')
                    pixel=hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
                    pixel_hashes[asset]=pixel
                    if pixel in pixels:union(asset,pixels[pixel])
                    pixels[pixel]=asset
                    # Numeric endings are aliases only when they encode actual image width.
                    match=re.search(r'-(\d{3,4})w?$',file.stem)
                    if match and int(match[1])!=rgb.width:continue
            name=family_name(asset)
            if name in names:union(asset,names[name])
            names[name]=asset
        except (OSError,ValueError) as exc:
            asset_issues[asset]='Undecodable public image asset: '+str(exc)
    # These explicit schemas describe one reviewed original per record. Never
    # union a document's unrelated top-level assets collection.
    schemas={'exclusive-artwork-review.json':'assets','exclusive-artwork-ownership.json':'replacements',
             'five-picture-image-review.json':'approved','topic-artwork-review.json':'assets'}
    for filename,collection in schemas.items():
        doc=root/'docs'/filename
        if not doc.is_file():continue
        try:records=json.loads(doc.read_text(encoding='utf-8'))[collection]
        except (ValueError,KeyError,TypeError) as exc:
            asset_issues['docs/'+filename]='Invalid identity manifest: '+str(exc);continue
        if not isinstance(records,list):
            asset_issues['docs/'+filename]='Invalid identity manifest record collection';continue
        for record in records:
            if not isinstance(record,dict):
                asset_issues['docs/'+filename]='Invalid identity manifest record';continue
            entries=record.get('published_assets',record.get('assets',[]))
            paths=[]
            for entry in entries:
                if not isinstance(entry,dict):
                    asset_issues['docs/'+filename]='Invalid identity manifest asset entry';continue
                path=entry.get('path')
                if path not in parent:continue
                if entry.get('sha256')!=file_hashes.get(path):
                    asset_issues[path]='Identity manifest asset SHA-256 mismatch';continue
                if record.get('status','approved')!='approved':
                    asset_issues[path]='Public reference to artwork not approved in review manifest'
                paths.append(path)
            for path in paths[1:]:union(paths[0],path)
            for field in ['source_sha256','source_decoded_rgb_sha256']:
                value=record.get(field,'')
                if paths and re.fullmatch(r'[0-9a-f]{64}',value):
                    lineage=field+':'+value
                    if lineage in lineages:union(paths[0],lineages[lineage])
                    lineages[lineage]=paths[0]
    groups={}
    for asset in sorted(asset_paths):groups.setdefault(find(asset),[]).append(asset)
    identities={};identity_labels=set()
    for members in groups.values():
        label=min(family_name(p) for p in members)
        if label in identity_labels:label=min(members)
        identity_labels.add(label)
        for asset in members:identities[asset]=label
    usages={}
    for ref in references:
        ref['family']=identities[ref['asset']];usages.setdefault(ref['family'],[]).append(ref)
    results=[]
    for page in [*sorted((root/'answers').glob('*.html')),root/'general-conference.html']:
        key=page.relative_to(root).as_posix();records=[]
        if key not in parsed:
            results.append({'page':key,'bodyPictureCount':0,'exclusiveCount':0,'minimumNewIfOtherUsagesRemain':5,'figures':[],'issues':['Missing required study page']});continue
        for n in parsed[key]:
            if n.tag!='img':continue
            chain=list(ancestors(n))
            if not any(a.tag=='main' for a in chain) or any(a.has('fc-resource-card') or a.has('fc-topic-opening') or a.has('gc-intro') or a.tag=='dialog' for a in chain):continue
            figure=next((a for a in chain if a.tag=='figure' or a.has('fc-marriage-era')),None)
            if not figure or not figure.text().strip():continue
            src=n.attrs.get('src','');asset=local_asset(page,src,root)
            if not asset:continue
            family=identities[asset];cap=next((c for c in figure.walk() if c.tag=='figcaption'),figure)
            heading=next((c for c in cap.walk() if c.tag in {'h2','h3','h4'}),None)
            ps=[c.text().strip() for c in cap.walk() if c.tag=='p' and not c.has('fc-study-visual-label') and not c.has('fc-study-visual-sources') and not c.has('fc-study-visual-actions')]
            sources=[c.attrs['href'] for c in cap.walk() if c.tag=='a' and c.attrs.get('href','').startswith('http')]
            image_link=next((a for a in ancestors(n) if a.tag=='a'),None)
            context=next((a for a in chain if a.tag=='section' and a.attrs.get('id')),None)
            container=context or figure.parent
            context_text=[]
            for c in container.walk():
                if c.tag not in {'h2','h3','p'}:continue
                if any(a is figure or a.has('fc-resource-card') for a in ancestors(c)):continue
                if c.text().strip():context_text.append(c.text().strip())
            owners=sorted({ref['page'] for ref in usages[family]})
            records.append({'title':heading.text().strip() if heading else cap.text().strip()[:100],'description':' '.join(ps),'alt':n.attrs.get('alt',''),'sources':sources,'src':src,'asset':asset,'fullsrc':image_link.attrs.get('href') if image_link else None,'family':family,'figureAttributes':figure.attrs,'imageAttributes':n.attrs,'nearestContext':{'section':context.attrs.get('id') if context else None,'text':context_text[:5]},'usedOnPages':owners,'exclusive':owners==[key] and asset not in asset_issues})
        exclusive={x['family'] for x in records if x['exclusive']};issues=[message+': '+asset for asset,message in asset_issues.items() if any(r['page']==key and r['asset']==asset for r in references)]
        if len(exclusive)<5:issues.append(f'Needs five globally exclusive body pictures; found {len(exclusive)}')
        for family in sorted({x['family'] for x in records if x['usedOnPages']!=[key]}):
            other=sorted({ref['page'] for ref in usages[family]}-{key})
            issues.append('Body artwork is reused on another page: '+family+' -> '+', '.join(other))
        results.append({'page':key,'bodyPictureCount':len({x['family'] for x in records}),'exclusiveCount':len(exclusive),'minimumNewIfOtherUsagesRemain':max(0,5-len(exclusive)),'figures':records,'issues':issues})
    return {'assetIssues':asset_issues,'decodedPixelHashCount':len(pixel_hashes),'publicHtmlCount':len(pages),'pages':results,'familyUsages':{family:{'assets':sorted({x['asset'] for x in refs}),'pages':sorted({x['page'] for x in refs}),'references':refs} for family,refs in usages.items()}}

if __name__=='__main__':
    data=scan()
    for page in data['pages']:
        print(f"{page['page']}: {page['exclusiveCount']} globally exclusive / {page['bodyPictureCount']} body artwork families")
        for issue in page['issues']:print('  FAIL: '+issue)
    for asset,issue in data['assetIssues'].items():print('  FAIL: '+issue+': '+asset)
    sys.exit(bool(data['assetIssues']) or any(p['issues'] for p in data['pages']))
