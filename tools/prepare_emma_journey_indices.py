"""Generate and validate actual Emma indices in a full checkout, not approve release.

The baseline must exist in git history. On failure each producer is reported
independently, search is skipped unless gallery succeeds, and no stale output is
presented as generated evidence. This deliberately does not bind new hashes to
historical inverse maps: those need separately reviewed, exact outputs.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

BASE = '63fafd9594949160f912b3c1ca0e39b52432df34'
BASE_BLOBS = {'art-gallery.json':'d7a9e628341f264d86227ac729d8db7ab8ef4584',
              'site-search-index.json':'cba61442fcbed4fd1e62d61b0d90134d8237d086',
              'docs/section-panel-inventory.json':'5a2db892aaad7e51e545e92604a8cd80b9becdc4'}

def blob_id(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def run(root, command):
    result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    return result.returncode, result.stdout

def execute(root, artifact, invoke=run):
    root=Path(root).resolve(); artifact=Path(artifact).resolve()
    artifact.mkdir(parents=True, exist_ok=True)
    names=['art-gallery.json','site-search-index.json','section-panel-inventory.json','index-generation.log','index-generation-status.json']
    if any((artifact/name).exists() or (artifact/name).is_symlink() for name in names):
        raise ValueError('artifact destination already contains index evidence; use a fresh directory')
    results={}; logs=[]
    def step(label, commands):
        for command in commands:
            code, output=invoke(root, command)
            logs.append('$ '+ ' '.join(command)+'\n'+output.decode('utf-8','replace')+'\nexit '+str(code)+'\n')
            if code != 0:
                results[label]='failed'; return False
        results[label]='success'; return True
    # A missing/incorrect baseline blocks the semantic comparison, but does not
    # hide independent producer results. Never silently accept unpinned bytes.
    with tempfile.TemporaryDirectory(prefix='emma-index-baseline-') as td:
        baseline=Path(td); baseline_ok=True
        for name, expected in BASE_BLOBS.items():
            code, raw=invoke(root, ['git','show',BASE+':'+name])
            if code or blob_id(raw)!=expected:
                baseline_ok=False; logs.append('baseline blob failed: '+name+'\n'); continue
            p=baseline/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        results['baseline']='success' if baseline_ok else 'failed'
        panel=step('panel', [['python','tools/section_panel_surface_qa.py','--write-inventory'],
                             ['python','tools/section_panel_surface_qa.py']])
        gallery=step('gallery', [['python','tools/build_art_gallery.py'],['python','tools/build_art_gallery.py','--check']])
        search=step('search', [['python','tools/build_site_search.py'],['python','tools/build_site_search.py','--check'],
                               ['python','tools/site_search_qa.py']]) if gallery else False
        if not gallery: results['search']='skipped (gallery failed)'
        for label, name, ok in [('panel','docs/section-panel-inventory.json',panel),('gallery','art-gallery.json',gallery),('search','site-search-index.json',search)]:
            if ok:
                data=(root/name).read_bytes(); out=artifact/Path(name).name; out.write_bytes(data)
                results[label+'_sha256']=hashlib.sha256(data).hexdigest()
        if baseline_ok and panel and gallery and search:
            step('semantic_delta', [['python','tools/emma_journey_indices_contract.py','--root',str(root),'--baseline',str(baseline)]])
        else: results['semantic_delta']='skipped (baseline or producer failed)'
    (artifact/'index-generation.log').write_text(''.join(logs),encoding='utf-8')
    (artifact/'index-generation-status.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return results

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--artifacts',type=Path,required=True);a=p.parse_args()
    try:r=execute(a.root,a.artifacts)
    except (OSError,ValueError) as exc:raise SystemExit('Index generation BLOCKED: '+str(exc))
    print(json.dumps(r,sort_keys=True));return 0 if all(r.get(k)=='success' for k in ('baseline','panel','gallery','search','semantic_delta')) else 1
if __name__=='__main__':raise SystemExit(main())
