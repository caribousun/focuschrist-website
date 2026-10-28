"""Validate old generated-index receipt context separately from current output.

The immutable pre-selector commit is historical evidence only. Current JSON is
schema-checked here; configured generator --check jobs verify complete freshness.
"""
from functools import lru_cache
import hashlib, subprocess
from pathlib import Path
from artwork_owner_closure import current_index_bytes
HISTORICAL_COMMIT='de5f3c35505fddd4586bb0b51c17dad1389f2bf9'
ALLOWED=frozenset({'art-gallery.json','site-search-index.json'})

def require(condition,message):
 if not condition:raise ValueError('Historical index context: '+message)

@lru_cache(maxsize=4)
def historical_bytes(root,name):
 require(name in ALLOWED,'unsupported evidence path')
 try:
  raw=subprocess.check_output(['git','-C',str(root),'show',HISTORICAL_COMMIT+':'+name],stderr=subprocess.PIPE)
 except (OSError,subprocess.CalledProcessError) as error:
  raise ValueError('Historical index context: immutable source unavailable') from error
 from artwork_display_delivery import inverse
 return inverse(name,raw)

def validate_context(root,row):
 root=Path(root).resolve();name=row.get('path')
 require(name in ALLOWED and isinstance(row.get('sha256'),str),'unsupported evidence row')
 # Validate actual current index before treating the old receipt as historical.
 current_index_bytes(root,name)
 raw=historical_bytes(root,name)
 require(hashlib.sha256(raw).hexdigest()==row['sha256'],'historical receipt mismatch: '+name)
 return True
