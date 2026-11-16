"""Exact reviewed-bank search source projection for historical diagnostics only.

Current behavior is exercised separately by existing search QA/runtime tests.
This projection does not replace those tests or grant publication approval.
"""
import hashlib
import re
from pathlib import Path

HISTORICAL_SHA = 'ab87a8629e8e341de08f194dbac8628a81c24730413ce705f08884a2b6bd2dd2'
DEPENDENCIES = {
 'site-search.js':'d98c242ff4866ae1c04ae0e0aa47c5cec4e6acaab7ead94d6200308586f4beeb',
 'answer-bank-matcher.js':'818d3f9d60d8ecef96643ab0c57a5b08ca363be475d9ff25401387043f6a4b39',
 'answer-bank-guards.js':'a80ffc54b1609ccce36bd93567f25c80a96c64151ab62f8d2113088b67975604',
}
OLD = b'<script src="site-search.js?v=20260919-focused-answers-1" defer></script>'
CURRENT = re.compile(rb'<script src="answer-bank-data\.js\?v=[0-9]{8}-answer-bank-([0-9a-f]{8})" data-answer-bank-search defer></script><script src="answer-bank-matcher\.js\?v=20261023-answer-bank-1" defer></script><script src="answer-bank-guards\.js\?v=20261023-answer-bank-1" defer></script><script src="site-search\.js\?v=20261112-reviewed-answer-search-1" defer></script>')

def checked_bytes(root, name):
 root=Path(root).resolve();p=root
 for part in Path(name).parts:
  p=p/part
  if p.is_symlink():raise ValueError('Unsafe search source: '+name)
 if not p.is_file() or not p.resolve().is_relative_to(root):raise ValueError('Missing search source: '+name)
 return p.read_bytes()

def project(root):
 for name,pin in DEPENDENCIES.items():
  if hashlib.sha256(checked_bytes(root,name)).hexdigest()!=pin:raise ValueError('Unaccounted search dependency drift: '+name)
 raw=checked_bytes(root,'search.html');matches=list(CURRENT.finditer(raw))
 if len(matches)!=1:raise ValueError('Expected exactly one reviewed search dependency block')
 match=matches[0];banksha=hashlib.sha256(checked_bytes(root,'answer-bank-data.js')).hexdigest()
 if match.group(1).decode()!=banksha[:8]:raise ValueError('Search bank cache mismatch')
 old=raw[:match.start()]+OLD+raw[match.end():]
 if hashlib.sha256(old).hexdigest()!=HISTORICAL_SHA:raise ValueError('Unrelated search HTML drift')
 return old
