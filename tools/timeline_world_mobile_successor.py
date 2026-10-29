"""Exact mobile-controls source projection; mechanical only, not review or release."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGE='timelines/world-and-scripture-timeline.html'
CONTROLLER='timeline-mobile-collapse.js'
MANIFEST='docs/timeline-mobile-collapse/world-source-delta.json'
MANIFEST_SHA='4a5078da187cb1a4845e4bcd048dce70b07bbc663ca79e9b0bae9f5d274be1ed'
BEFORE='016e9896db70ff0a8a142503f289f2e0cbd2f4d96b73d667247dbb2a2370ceef'
AFTER='e6331171d55a522bd411bd27b58ebe23335d04313cab0426bee9b1c64f0d2805'
CONTROLLER_SHA='d1738fa1b95e3c2f2e6690175050e95f3183c9f334b8fe57e9af8a7f20170049'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def source(root,name):
 root=Path(root).resolve();parts=Path(name).parts;p=root.joinpath(*parts)
 assert not Path(name).is_absolute() and '..' not in parts
 assert all(not root.joinpath(*parts[:i]).is_symlink() for i in range(1,len(parts)+1))
 assert p.is_file() and p.resolve().is_relative_to(root),'Missing or unsafe mobile source'
 return p.read_bytes()
def restore(raw,root=ROOT):
 manifest=source(root,MANIFEST);assert sha(manifest)==MANIFEST_SHA,'Mobile source manifest changed'
 row=json.loads(manifest);assert set(row)=={'schema','path','before_sha256','after_sha256','controller_path','controller_sha256','changes'}
 assert row['schema']==1 and row['path']==PAGE and row['before_sha256']==BEFORE and row['after_sha256']==AFTER
 assert row['controller_path']==CONTROLLER and row['controller_sha256']==CONTROLLER_SHA
 assert sha(source(root,CONTROLLER))==CONTROLLER_SHA,'Mobile controller changed'
 assert sha(raw)==AFTER,'Unreviewed mobile controls source'
 assert isinstance(row['changes'],list) and len(row['changes'])==5
 for item in reversed(row['changes']):
  assert set(item)=={'before_b64','after_b64'}
  before=base64.b64decode(item['before_b64'],validate=True);after=base64.b64decode(item['after_b64'],validate=True)
  assert before!=after and after and raw.count(after)==1,'Mobile successor context changed'
  raw=raw.replace(after,before,1)
 assert sha(raw)==BEFORE,'Mobile predecessor mismatch'
 return raw
