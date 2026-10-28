#!/usr/bin/env python3
"""Current semantic mutations and separate historical fixture fidelity."""
import argparse, shutil, tempfile
from pathlib import Path
from timeline_selector_semantics import validate
from owner_integration_contract import validate_file, historical_bytes
from owner_integration_successor import restore, advance

def reject(raw):
 try: validate(raw)
 except AssertionError: return
 raise AssertionError('semantic drift accepted')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--prior-manifest',type=Path,help='Optionally test immutable historical reconstruction');a=p.parse_args();new=(a.root/'timeline.html').read_bytes();validate(new)
 benign=new.replace(b'fc-timeline-choice__body',b'fc-timeline-choice__body layout-v2');assert benign!=new;validate(benign)
 wrapped=new.replace(b'<article class="fc-timeline-choice">',b'<div class="layout-wrap"><article class="fc-timeline-choice">',1).replace(b'</article>',b'</article></div>',1);assert wrapped!=new;validate(wrapped)
 mutations=[(b'Explore the story of the Restoration.',b'Changed visible copy.'),(b'latter-day-saint-church-history-timeline.html',b'other.html'),(b'church-history-grove.webp',b'other.webp'),(b'Church History Timeline',b'Altered History Timeline'),(b'id="adams-1881"',b'id="other"'),(b'<article class="fc-timeline-choice">',b'<article class="fc-timeline-choice" hidden>',1),(b'</main>',b'<p>Unapproved content</p></main>')]
 # Inventory mutations must also fail rather than silently hide or duplicate a choice.
 start=new.index(b'<article class="fc-timeline-choice">'); stop=new.index(b'</article>',start)+len(b'</article>'); card=new[start:stop]
 reject(new[:start]+new[stop:]); reject(new[:stop]+card+new[stop:])
 for pair in mutations:
  old,newpart,*count=pair;assert old in new;reject(new.replace(old,newpart,count[0] if count else 1))
 if a.prior_manifest:
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'docs/timeline-selector').mkdir(parents=True);(root/'docs/owner-integration-contract').mkdir(parents=True)
   shutil.copyfile(a.root/'docs/timeline-selector/historical-c910.txt',root/'docs/timeline-selector/historical-c910.txt')
   (root/'timeline.html').write_bytes(benign)
   shutil.copyfile(a.prior_manifest,root/'docs/owner-integration-contract/source-manifest.json')
   validate_file('timeline.html',new,root);validate_file('timeline.html',benign,root)
   history=historical_bytes('timeline.html',benign,root);assert restore('timeline.html',benign,root)==history;validate(advance('timeline.html',history,root))
   fixture=root/'docs/timeline-selector/historical-c910.txt';fixture.write_bytes(fixture.read_bytes()+b' ')
   try: historical_bytes('timeline.html',new,root)
   except AssertionError:pass
   else:raise AssertionError('tampered historical fixture accepted')
 print('PASS current content/navigation/asset mutations rejected; class and wrapper variations accepted' + ('; historical fixture tampering rejected' if a.prior_manifest else '; historical checks not run'))
if __name__=='__main__':main()
