"""Fail closed before pip when a QA consumer job lacks the shared pinned setup.

Standard library only: this check must run before third-party dependencies exist.
It checks each workflow job independently, not package installation in another job.
"""
import argparse
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={'pillow':'12.2.0','beautifulsoup4':'4.15.0'}
INSTALL='python -m pip install -r tools/qa-requirements.txt'
CONTRACT='python tools/qa_dependency_contract.py --self-test'
CONSUMER=re.compile(r'\bpython(?:3)?\s+tools/(?:unified_experience_qa|sitewide_artwork_review_qa|plan_of_salvation_qa)\.py\b')


def errors(workflows, requirements):
 issues=[];pins={}
 for raw in requirements.splitlines():
  line=raw.strip()
  if not line or line.startswith('#'):continue
  match=re.fullmatch(r'([A-Za-z0-9_-]+)==([0-9]+(?:\.[0-9]+)*)',line)
  if not match:issues.append('Dependency must use an exact version pin: '+line);continue
  package=match[1].lower().replace('_','-')
  if package in pins:issues.append('Duplicate dependency: '+package)
  pins[package]=match[2]
 if pins!=REQUIRED:issues.append('Shared requirements must contain exactly the reviewed Pillow and BeautifulSoup pins')
 consumer_jobs=0
 for name,text in workflows.items():
  # GitHub workflow jobs are two-space mapping keys beneath jobs. Step names are deeper.
  section=re.search(r'^jobs:\s*$',text,re.M)
  if not section:
   if CONSUMER.search(text):issues.append(name+': consumer present but jobs mapping is unrecognized')
   continue
  body=text[section.end():];headers=list(re.finditer(r'^  ([A-Za-z0-9_-]+):\s*$',body,re.M))
  for index,header in enumerate(headers):
   job=body[header.end():headers[index+1].start() if index+1<len(headers) else len(body)]
   # Full-line comments are not executable commands and cannot satisfy setup.
   job='\n'.join(line for line in job.splitlines() if not line.lstrip().startswith('#'))
   consumers=list(CONSUMER.finditer(job))
   if not consumers:continue
   consumer_jobs+=1;label=name+':'+header[1]
   installs=[m.start() for m in re.finditer(re.escape(INSTALL)+r'(?=\s*(?:$|\n))',job,re.M)]
   contracts=[m.start() for m in re.finditer(re.escape(CONTRACT)+r'(?=\s*(?:$|\n))',job,re.M)]
   if len(installs)!=1:issues.append(label+': requires one shared requirements install');continue
   if installs[0]>=consumers[0].start():issues.append(label+': install occurs after a dependency consumer')
   if len(contracts)!=1 or contracts[0]>=installs[0]:issues.append(label+': requires contract before pip install')
 if consumer_jobs<2:issues.append('Expected both Site QA and Pages deployment consumer jobs')
 return issues


def self_test(workflows,requirements):
 assert not errors(workflows,requirements), 'Positive workflow contract must pass before mutation tests'
 name=next(n for n in workflows if 'deploy-pages' in n);original=workflows[name]
 variants=[('missing install',original.replace(INSTALL,'python -m pip install Pillow==12.2.0')),
 ('wrong requirements',original.replace(' -r tools/qa-requirements.txt',' -r tools/other-requirements.txt')),
 ('missing contract',original.replace(CONTRACT,'echo contract omitted')),
 ('contract after pip',original.replace(CONTRACT,'SWAP').replace(INSTALL,CONTRACT).replace('SWAP',INSTALL)),
 ('install after consumer',original.replace(INSTALL,'echo install delayed')+'\n          '+INSTALL+'\n'),
 ('commented install',original.replace('run: '+INSTALL,'# run: '+INSTALL))]
 count=0
 for label,changed in variants:
  assert changed!=original,label
  candidate=dict(workflows);candidate[name]=changed
  assert errors(candidate,requirements),label+' escaped';count+=1
 for label,changed in [('missing BeautifulSoup',requirements.replace('beautifulsoup4==4.15.0\n','')),('missing Pillow',requirements.replace('Pillow==12.2.0\n','')),('unpinned package',requirements.replace('beautifulsoup4==4.15.0','beautifulsoup4')),('wrong version',requirements.replace('4.15.0','4.14.0'))]:
  assert errors(workflows,changed),label+' escaped';count+=1
 candidate=dict(workflows);candidate['new-consumer.yml']='jobs:\n  new:\n    steps:\n      - run: python tools/unified_experience_qa.py\n'
 assert errors(candidate,requirements),'New workflow without setup escaped';count+=1
 candidate=dict(workflows);candidate[name]=original.replace(INSTALL,'echo installed elsewhere')+'\n  unrelated:\n    steps:\n      - run: '+CONTRACT+'\n      - run: '+INSTALL+'\n'
 assert errors(candidate,requirements),'Install in sibling job escaped';count+=1
 print('QA DEPENDENCY CONTRACT SELFTEST PASS: '+str(count)+' setup/pin/order/job-scope mutations rejected')


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 workflows={p.name:p.read_text(encoding='utf-8') for p in sorted((ROOT/'.github/workflows').glob('*.y*ml'))}
 requirements=(ROOT/'tools/qa-requirements.txt').read_text(encoding='utf-8')
 issues=errors(workflows,requirements)
 if issues:raise SystemExit('QA DEPENDENCY CONTRACT FAIL\n- '+'\n- '.join(issues))
 if args.self_test:self_test(workflows,requirements)
 print('QA DEPENDENCY CONTRACT PASS: every dependent workflow job runs the standard-library guard and shared pinned install before its consumers')
if __name__=='__main__':main()
