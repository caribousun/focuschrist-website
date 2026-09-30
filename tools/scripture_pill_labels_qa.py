"""Keep rendered scripture link/pill verse ranges typographic, not spoken."""
import re
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
spoken=re.compile(r'\b\d+:\d+\s+(?:to|through)\s+\d+\b',re.I)
failures=[];count=0
for p in ROOT.rglob('*.html'):
 if any(x in p.relative_to(ROOT).parts for x in ['.git','.qa-artifacts','node_modules','work']):continue
 soup=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
 for a in soup.select('a[href*="/scriptures/"], [data-detail-source*="/scriptures/"]'):
  label=a.get('data-detail-source-label') or a.get_text(' ',strip=True)
  count+=1
  if spoken.search(label):failures.append((str(p.relative_to(ROOT)),label))
assert spoken.search('Read John 10:11 to 16')
assert not spoken.search('Read John 10:11–16')
assert not failures, failures
assert count>100, 'No meaningful scripture-label coverage'
print(f'SCRIPTURE PILL LABELS PASS: {count} scripture links and artwork source labels')
