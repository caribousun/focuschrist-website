"""Add the authorized journey while preserving existing parent study and artwork."""
import argparse,json,re
from pathlib import Path
from build_jesus_journey import ROOT,render,E
page=json.loads((ROOT/'docs/jesus-journey/main-content.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser();parser.add_argument('--strict',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
art=json.loads((ROOT/'docs/jesus-journey/artworks.json').read_text(encoding='utf-8'))
# Missing planned records remain explicit drafts, never fake pictures.
for sec in page['sections']:
    for block in sec.get('blocks',[]):
        if isinstance(block,dict) and 'art' in block and block['art'] not in art:art[block['art']]={}
generated=render(page,art,args.strict)
body=re.search(r'<main class="jj-wrap jj-main" id="main-content">(.*?)<nav class="jj-actions jj-return fc-actions"',generated,re.S).group(1)
target=ROOT/'answers/jesus-christ-latter-day-saint-beliefs.html'
text=target.read_text(encoding='utf-8')
previous=text
text=re.sub(r'<!-- JESUS JOURNEY BEGIN -->.*?<!-- JESUS JOURNEY END -->','',text,flags=re.S)
marker='<section class="fc-deep-study fc-foundation-route"'
pos=text.index(marker)
text=text[:pos]+'<!-- JESUS JOURNEY BEGIN --><div class="jj-main">'+body+'</div><!-- JESUS JOURNEY END -->'+text[pos:]
if 'jesus-journey.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="../jesus-journey.css?v=20260923-1">\n</head>')
text=re.sub(r'jesus-journey.js\?v=[^"\s]+','jesus-journey.js?v=20260923-pictured-chapters-1',text)
text=re.sub(r'jesus-journey.css\?v=[^"\s]+','jesus-journey.css?v=20260923-chapters-2',text)
text=re.sub(r'topic-artwork-details.js\?v=[^"\s]+','topic-artwork-details.js?v=20260923-next-study-1',text)
if 'src="../jesus-journey.js' not in text:text=text.replace('</body>','<script src="../jesus-journey.js?v=20260923-pictured-chapters-1" defer></script></body>')
text=re.sub(r'<title>.*?</title>','<title>Jesus Christ: Come to Know the Living Savior | focusChrist</title>',text,count=1)
for attribute,name,value in [('name','robots','index,follow,max-image-preview:large' if args.strict else 'noindex,nofollow'),('name','description',page['description']),('property','og:title',page['title']),('property','og:description',page['description']),('name','twitter:title',page['title']),('name','twitter:description',page['description'])]:
    tag=f'<meta {attribute}="{name}" content="{E(value)}">'
    pattern=r'<meta '+attribute+'="'+re.escape(name)+r'"[^>]*>'
    if re.search(pattern,text):text=re.sub(pattern,lambda m:tag,text,count=1)
    else:text=text.replace('</head>',tag+'\n</head>')
def structured(match):
    data=json.loads(match.group(1))
    if data.get('@type')=='Article':data['headline']=page['title'];data['description']=page['description']
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',structured,text,flags=re.S)
if args.check:
    if previous!=text:raise ValueError('Parent journey output is stale')
else:target.write_text(text,encoding='utf-8',newline='\n')
print('Parent journey updated; original hero and study retained. strict='+str(args.strict)+'. Publication and complete destination verification are separate.')
