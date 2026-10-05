"""Mutation tests for inventory/provenance/markup contracts, not pixel review."""
from pathlib import Path
import sys, json, hashlib, html, tempfile

HERE = Path(__file__).resolve().parent
import os
SITE = Path(os.environ.get('FOCUS_QA_SITE_ROOT', str(HERE.parent)))
sys.path.insert(0, str(SITE / 'tools'))
sys.path.insert(0, str(HERE))
import first_topic_completion_qa as qa

fixture_directory = tempfile.TemporaryDirectory(prefix='focus-first-topic-qa-')
root = Path(fixture_directory.name)
def write(path, value):
    p = root/path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')
def save(path, obj): write(path, json.dumps(obj))
def sha(value): return hashlib.sha256(value.encode()).hexdigest()
records=[]; figures={qa.PRAYER:[],qa.FAMILIES:[]}; registry={qa.PRAYER:[],qa.FAMILIES:[]}
for key,route in qa.EXPECTED.items():
    asset=qa.PREFIX+key+'-full.webp'; responsive=qa.PREFIX+key+'-960.webp'
    write(asset,'fixture full '+key);write(responsive,'fixture responsive '+key)
    r=dict(key=key,route=route,asset=asset,responsive=responsive,sha256=sha('fixture full '+key),
           responsive_sha256=sha('fixture responsive '+key),source_sha256=sha('fixture raw '+key),
           source_urls=['https://www.churchofjesuschrist.org/study/scriptures/nt/john/6?lang=eng&id=p9-p11#p9'],
           source_label='John 6:9-11',title='Title '+key,caption='Caption '+key,alt='Alt '+key,
           christ=key!='prayer-04',width=1536,height=1024,reviewed=True)
    r.update(study=qa.STUDIES[key][0],study_label=qa.STUDIES[key][1])
    records.append(r);registry[route].append(dict(asset=asset,sha256=r['sha256'],reviewed=True))
    e=lambda x:html.escape(x,quote=True)
    figures[route].append(f'''<figure class="fc-study-visual" data-exclusive-artwork="first-{key}" data-enriched-study-art="first-{key}"><a href="../{asset}" data-topic-study="{e(r['study'])}" data-topic-study-label="{e(r['study_label'])}" data-full-image-viewer aria-haspopup="dialog" aria-label="Explore artwork: {e(r['title'])}" data-full-image-alt="{e(r['alt'])}"><img src="../{responsive}" srcset="../{responsive} 960w, ../{asset} 1536w" width="1536" height="1024" alt="{e(r['alt'])}"></a><figcaption><p class="fc-study-visual-label">Explore and study</p><h3>{e(r['title'])}</h3><p>{e(r['caption'])}</p><p class="fc-study-visual-sources"><a class="fc-inline-scripture" href="{e(r['source_urls'][0])}">{e(r['source_label'])}</a></p></figcaption></figure>''')
for route,fs in figures.items():
    write(route,'<html><head><script defer src="../topic-artwork-details.js"></script><link href="../topic-artwork-details.css"></head><body><main>'+''.join(fs)+'</main></body></html>')
for study,label in qa.STUDIES.values():
    if not (root/'answers'/study).exists(): write('answers/'+study,'<html><main><h1>'+label+'</h1></main></html>')
write('general-conference.html','<html><main></main></html>')
write('sitemap.xml','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://example.invalid/'+r+'</loc></url>' for r in figures)+'</urlset>')
save('docs/art-study-image-review.json',{'pages':registry})
manifest={'artworks':records,'review_receipts':{}}
for reviewer in ['Fermi','Newton']:
    path='docs/first-topic-completion/'+reviewer.lower()+'.json'
    save(path,{'reviewer':reviewer,'records':[{k:r[k] for k in ['sha256','responsive_sha256','source_sha256']} for r in records]})
    manifest['review_receipts'][reviewer]=[{'path':path,'sha256':qa.digest(root/path)}]
save(qa.MANIFEST,manifest)
baseline={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
require=qa.require
require(len(qa.check(root))==10,'valid synthetic control must pass')
def alter(path,old,new):
    p=root/path;t=p.read_text();assert old in t;p.write_text(t.replace(old,new,1),encoding='utf8')
def manifest_mutate(fn):
    d=json.loads((root/qa.MANIFEST).read_text());fn(d);save(qa.MANIFEST,d)
tests=[
 ('missing onward study',lambda:alter(qa.PRAYER,'data-topic-study="'+records[0]['study']+'"','')),
 ('changed onward destination',lambda:alter(qa.PRAYER,'data-topic-study="'+records[0]['study']+'"','data-topic-study="holy-ghost.html"')),
 ('changed onward label',lambda:alter(qa.PRAYER,'data-topic-study-label="'+records[0]['study_label']+'"','data-topic-study-label="Wrong label"')),
 ('coordinated wrong manifest study',lambda:manifest_mutate(lambda d:d['artworks'][0].update(study='holy-ghost.html'))),
 ('missing onward destination file',lambda:(root/'answers'/records[0]['study']).unlink()),
 ('duplicate manifest key',lambda:manifest_mutate(lambda d:d['artworks'][1].update(key=d['artworks'][0]['key']))),
 ('changed full bytes',lambda:write(records[0]['asset'],'changed')),
 ('changed caption',lambda:alter(qa.PRAYER,'Caption prayer-01','Wrong caption')),
 ('changed alt',lambda:alter(qa.PRAYER,'alt="Alt prayer-01"','alt="wrong"')),
 ('changed source',lambda:alter(qa.PRAYER,'john/6?lang','john/7?lang')),
 ('missing fallback',lambda:alter(qa.PRAYER,' data-full-image-viewer','')),
 ('adapter bypass',lambda:alter(qa.PRAYER,' aria-haspopup="dialog"',' data-artwork-detail aria-haspopup="dialog"')),
 ('wrong responsive source',lambda:alter(qa.PRAYER,'src="../'+records[0]['responsive']+'"','src="../'+records[1]['responsive']+'"')),
 ('unregistered first marker',lambda:alter(qa.PRAYER,'</main>','<figure data-exclusive-artwork="first-rogue"></figure></main>')),
 ('unregistered family occurrence',lambda:alter(qa.PRAYER,'</main>','<img src="../'+records[0]['responsive']+'"></main>')),
 ('missing figure',lambda:alter(qa.PRAYER,figures[qa.PRAYER][0],'')),
 ('duplicate figure',lambda:alter(qa.PRAYER,'</main>',figures[qa.PRAYER][0]+'</main>')),
 ('wrong owning route',lambda:manifest_mutate(lambda d:d['artworks'][0].update(route=qa.FAMILIES))),
 ('stale receipt bytes',lambda:write('docs/first-topic-completion/fermi.json','{}')),
 ('unreviewed record',lambda:manifest_mutate(lambda d:d['artworks'][0].update(reviewed=False))),
 ('receipt lacks source hash',lambda:manifest_mutate(lambda d:d['artworks'][0].update(source_sha256='0'*64))),
 ('shared registry mismatch',lambda:alter('docs/art-study-image-review.json',records[0]['sha256'],'0'*64)),
]
results=[]
for name,mutation in tests:
    mutation()
    try:qa.check(root)
    except AssertionError as error:results.append({'mutation':name,'rejected':True,'reason':str(error)})
    else:raise AssertionError('Mutation escaped: '+name)
    for path,content in baseline.items():(root/path).write_bytes(content)
require(len(qa.check(root))==10,'restored positive control must pass')
receipt={'scope':'Synthetic inventory/markup/provenance contract mutation tests; fixture bytes are not images and do not test pixel quality or production candidate.','fixture':str(root),'positive_control':True,'restored_control':True,'mutations':results,'count':len(results)}
report = Path(os.environ.get('FOCUS_QA_REPORT', str(SITE/'.qa-artifacts'/'first-topic-qa-mutations.json')))
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
fixture_directory.cleanup()
print(json.dumps({'positive':True,'rejected_mutations':len(results),'restored':True,'receipt':str(report)}))
