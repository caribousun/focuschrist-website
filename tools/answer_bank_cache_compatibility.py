"""Validate current bank cache references before isolated historical checks.

Only the cache query in the two exact historical HTML pages may differ. This
checks cache coherence, NOT the bank's content quality, approval, or publication.
An optional diagnostic also validates the bounded current Watch source and
projects its exact historical predecessor. No historical receipts, validators,
or current site files are modified.
"""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_COMMIT='4fb9e51deda2997d6974e80a5dce86a65167841c'
HISTORICAL_HTML={
 'ask.html':'3595a295f5df683c2cc842f3ae51705eed08963face03b90bd85a8fe9246ad1f',
 'pioneers.html':'ebd9444e89b0acff74bf0b761460a42c30f04a149ff8d9de9ce49f127188b3aa',
}
OLD_TAG=b'<script src="answer-bank-data.js?v=20261023-answer-bank-1" defer></script>'
CURRENT_TAG=re.compile(rb'<script src="answer-bank-data\.js\?v=([0-9]{8})-answer-bank-([0-9a-f]{8})" defer></script>')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(root,name):
 p=root/name
 if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
  raise ValueError('Missing or unsafe cache-coherence input: '+name)
 return p.read_bytes()

def validate_current(root=ROOT):
 root=Path(root).resolve();bank=read(root,'answer-bank-data.js');bank_sha=sha(bank);result={}
 for name,pin in HISTORICAL_HTML.items():
  raw=read(root,name);matches=list(CURRENT_TAG.finditer(raw))
  if len(matches)!=1:
   raise ValueError('Exactly one canonical current bank loader required: '+name)
  match=matches[0]
  if match.group(2).decode()!=bank_sha[:8]:
   raise ValueError('Bank cache token does not match actual bank SHA: '+name)
  historical=raw[:match.start()]+OLD_TAG+raw[match.end():]
  if sha(historical)!=pin:
   raise ValueError('Non-cache HTML drift is not covered: '+name)
  result[name]={'actual_sha256':sha(raw),'historical_sha256':pin,'historical_bytes':historical}
 return {'bank_sha256':bank_sha,'pages':result}

@contextmanager
def historical_check_view(root=ROOT, include_watch=False):
 """Keep actual-source validation separate from unchanged legacy assertions."""
 root=Path(root).resolve();record=validate_current(root)
 watch_before=None
 if include_watch:
  import subprocess
  from watch_current_source_qa import check
  record['watch']=check(root)
  watch_before=subprocess.check_output(['git','-C',str(root),'show',HISTORICAL_COMMIT+':watch.html'])
  record['watch']['historical_sha256']=sha(watch_before)
  if sha(watch_before)!='af5c40051f3bf9378f89e2c692192b0fff78cf1162ee903d2a7583ef8045ac82':
   raise ValueError('Historical Watch fixture changed')
 with tempfile.TemporaryDirectory(prefix='validated-bank-cache-') as folder:
  view=Path(folder)/'site'
  def copy(source,target):
   if Path(source).is_symlink():raise ValueError('Symlink in validation input')
   return shutil.copy2(source,target)
  for parent,dirs,files in os.walk(root,followlinks=False):
   dirs[:]=[d for d in dirs if d not in {'.git','.qa-artifacts','__pycache__','.pytest_cache'}]
   if any((Path(parent)/d).is_symlink() for d in dirs):raise ValueError('Symlink directory in validation input')
  shutil.copytree(root,view,copy_function=copy,ignore=shutil.ignore_patterns('.git','.qa-artifacts','__pycache__','.pytest_cache'))
  if sha(read(view,'answer-bank-data.js'))!=record['bank_sha256']:
   raise ValueError('Bank changed during validation snapshot')
  for name,item in record['pages'].items():
   if sha(read(view,name))!=item['actual_sha256']:raise ValueError('HTML changed during validation snapshot')
   (view/name).write_bytes(item['historical_bytes'])
  if watch_before is not None:
   from watch_current_source_qa import check_sources
   check_sources(view)
   (view/'watch.html').write_bytes(watch_before)
  yield view,record

if __name__=='__main__':
 import json
 import continue_motion_binding
 with historical_check_view(include_watch=True) as (view,record):
  result=continue_motion_binding.check(view)
  print(json.dumps({'cache_coherence':{'bank_sha256':record['bank_sha256'],'pages':{n:{k:v for k,v in p.items() if k!='historical_bytes'} for n,p in record['pages'].items()}},'watch_source':record.get('watch'),'scope':'Projected historical diagnostic; not current behavior acceptance','historical_motion':result},sort_keys=True))
