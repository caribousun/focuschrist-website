"""Preserve originals and derive delivery variants with explicit reviewed revision chains."""
from pathlib import Path
import json,hashlib,shutil,re
from PIL import Image
from build_jesus_journey import validate_artwork_review
ROOT=Path(__file__).resolve().parents[1]

def batch_order(path):
    match=re.fullmatch(r'art-batch-(\d+)\.json',path.name)
    if not match:raise ValueError('Batch needs numeric sequence: '+path.name)
    return int(match[1])

def merge_batches(registry,batches,data_dir):
    chains={}
    for batch in sorted(batches,key=batch_order):
        for key,record in json.loads(batch.read_text(encoding='utf-8')).items():
            previous=chains.get(key)
            if previous and previous.get('generated_path')!=record.get('generated_path'):
                old_sha=previous.get('original_sha256') or hashlib.sha256(Path(previous['generated_path']).read_bytes()).hexdigest()
                new_sha=record.get('original_sha256')
                if record.get('supersedes_sha256')!=old_sha or new_sha==old_sha:
                    raise ValueError('Unlinked revision '+key)
                if not record.get('reviewed'):raise ValueError('Unreviewed revision '+key)
                validate_artwork_review(key,record,data_dir,check_corrections=False)
                for field in ('original','asset','thumbnail'):
                    if record.get(field)==previous.get(field):raise ValueError('Revision would overwrite archive '+key)
            chains[key]={**(previous or {}),**record}
            if record.get('supersedes_sha256'):
                for field in ('asset_sha256','thumbnail_sha256'):
                    if field not in record:chains[key].pop(field,None)
    result={k:dict(v) for k,v in registry.items()}
    for key,record in chains.items():
        existing=registry.get(key,{})
        # Registry may already contain the chain tip; do not replay it backwards.
        if existing.get('generated_path') and existing.get('generated_path')!=record.get('generated_path'):
            if record.get('supersedes_sha256')!=existing.get('original_sha256'):
                # Multiple new linked revisions can be imported before preparation.
                hashes=[r.get('original_sha256') for b in sorted(batches,key=batch_order) for k,r in json.loads(b.read_text(encoding='utf-8')).items() if k==key]
                if existing.get('original_sha256') not in hashes:raise ValueError('Registry outside revision chain '+key)
        if record.get('supersedes_sha256'):validate_artwork_review(key,record,data_dir)
        result[key]={**existing,**record}
        if record.get('supersedes_sha256'):
            for field in ('asset_sha256','thumbnail_sha256'):
                if field not in record:result[key].pop(field,None)
    return result

def main():
    folder=ROOT/'docs/jesus-journey';manifest=folder/'artworks.json'
    data=merge_batches(json.loads(manifest.read_text(encoding='utf-8')),list(folder.glob('art-batch-*.json')),folder)
    # Imported batches preserve image-review history. Explicit current paragraph
    # placement is editorial metadata and must not revert when replaying them.
    for entry in json.loads((folder/'parable-art-plan.json').read_text(encoding='utf-8'))['entries']:
        if 'afterParagraph' in entry:
            data[entry['key']]['section']=entry['sectionId']
    originals=ROOT.parent/'originals';originals.mkdir(exist_ok=True)
    for key,a in data.items():
        if not a.get('generated_path'):continue
        src=Path(a['generated_path']);dst=originals/a['original']
        digest=hashlib.sha256(src.read_bytes()).hexdigest()
        if a.get('original_sha256') and digest!=a['original_sha256']:raise ValueError('Changed source original '+key)
        if not dst.exists():shutil.copy2(src,dst)
        if dst.read_bytes()!=src.read_bytes():raise ValueError('Original collision '+key)
        a['original_sha256']=digest
        im=Image.open(dst).convert('RGB');a['width'],a['height']=im.size
        for field,width in [('asset',im.width),('thumbnail',960)]:
            target=ROOT/a[field];target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():
                out=im.copy();out.thumbnail((width,round(width*im.height/im.width)),Image.Resampling.LANCZOS)
                out.save(target,'WEBP',quality=93,method=6)
            actual=hashlib.sha256(target.read_bytes()).hexdigest()
            if a.get(field+'_sha256') and actual!=a[field+'_sha256']:raise ValueError('Changed existing derivative '+key)
            a[field+'_sha256']=actual
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Preserved and prepared',sum(bool(a.get('generated_path')) for a in data.values()),'originals;',len(data),'total planned artworks')

if __name__=='__main__':main()
