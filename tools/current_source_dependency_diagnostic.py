#!/usr/bin/env python3
"""Read-only, bounded current-source diagnostic; not a release verdict.

Run named validators independently so one failure does not hide later results.
Writes only diagnostic logs under .qa-artifacts; no deployment or source edits.
"""
import json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.qa-artifacts/current-source-dependency'
COMMANDS={
 'retirement-census':['python','-m','unittest','discover','-s','tools','-p','test_artwork_owner_closure.py'],
 'current-mixed':['python','tools/run_current_mixed_regressions.py'],
 'current-display':['python','tools/run_current_mixed_regressions.py','--display-only'],
 'historical-index-context':['python','-m','unittest','discover','-s','tools','-p','test_historical_generated_index_context.py'],
 'selection-guards':['python','tools/test_run_current_mixed_regressions.py'],
 'normalizer-safety':['python','tools/test_current_normalizer_fail_closed.py'],
 'current-content-tests':['python','-m','unittest','discover','-s','tools','-p','test_current_integration_content_audit.py'],
 'current-index-tests':['python','-m','unittest','discover','-s','tools','-p','test_actual_current_index_composition.py'],
 'adams-search-consumer':['python','-m','unittest','discover','-s','tools','-p','test_adams_search_consumer.py'],
 'site-search-behavior':['python','tools/site_search_qa.py'],
 'current-gallery-integration':['python','-m','unittest','discover','-s','tools','-p','test_gallery_current_integration.py'],
 'sitewide-artwork-review':['python','tools/sitewide_artwork_review_qa.py'],
 'adams-context':['python','-m','unittest','discover','-s','tools','-p','test_adams_integrated_context.py'],
 'adams-header-evidence':['python','-m','unittest','discover','-s','tools','-p','test_adams_header_evidence_successor.py'],
 'current-content-audit':['python','tools/static_content_audit.py'],
 'search-generator-check':['python','tools/build_site_search.py','--check'],
 'gallery-generator-check':['python','tools/build_art_gallery.py','--check'],
 'artwork-release-check':['python','tools/artwork_creation_gate.py','release'],
}
PATTERN=re.compile(r'site-search-index\.json|art-gallery\.json|a9933a9ec749aec4|5744d3b23308c419|038391c9f469c4c7|2712123eff786e68',re.I)
def inventory():
 rows=[]
 for path in sorted((ROOT/'tools').rglob('*')):
  if not path.is_file() or path.suffix not in {'.py','.js','.cjs','.mjs'}:continue
  for number,line in enumerate(path.read_text(encoding='utf8').splitlines(),1):
   if PATTERN.search(line):rows.append({'path':str(path.relative_to(ROOT)),'line':number,'text':line[:500]})
 return rows
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 expected=os.environ.get('GITHUB_SHA')
 if os.environ.get('GITHUB_ACTIONS') == 'true' and (not expected or head != expected):
  raise RuntimeError('Checkout SHA does not match the requested immutable workflow revision')
 (OUT/'checkout.txt').write_text(head+'\n')
 (OUT/'index-callsite-inventory.json').write_text(json.dumps({'scope':'Targeted literal search in tools Python and JavaScript files; dynamic references and other paths may be missed.','checkout':head,'matches':inventory()},indent=2)+'\n')
 if '--inventory-only' in sys.argv:
  print('Inventory written; validators not run.');return 0
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');results={}
 for name,cmd in COMMANDS.items():
  timeout=180 if name == 'artwork-release-check' else 90
  try:
   done=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
   status={'status':'pass' if done.returncode==0 else 'fail','returncode':done.returncode};output=done.stdout
  except subprocess.TimeoutExpired as error:
   status={'status':'timeout','returncode':None};output=error.stdout or ''
   if isinstance(output,bytes):output=output.decode('utf8','replace')
  status['timeout_seconds']=timeout
  (OUT/(name+'.log')).write_text(output,encoding='utf8');results[name]=status
  print(name,status['status'],flush=True)
 (OUT/'summary.json').write_text(json.dumps({'scope':'Independent bounded source diagnostics, not release acceptance','checkout':head,'results':results},indent=2)+'\n')
 return 0 if all(row['status']=='pass' for row in results.values()) else 1
if __name__=='__main__':sys.exit(main())
