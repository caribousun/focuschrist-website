"""Guard the explicit scripture action without changing ordinary study cards."""
from answer_study_qa import Document
from build_jesus_journey import card, scripture
DEST='/jesus-christ/parables/laborers-vineyard.html'
TITLE='The Laborers in the Vineyard'
REF=['nt/matt/19','Matthew 19:27–30','27-30']
HREF='https://www.churchofjesuschrist.org/study/scriptures/nt/matt/19?lang=eng&id=p27-p30#p27'

def check(text):
    doc=Document();doc.feed(text);nodes=list(doc.root.walk())
    headings=[n for n in nodes if n.tag=='h3' and n.text()==TITLE]
    if len(headings)!=1:return ['Expected exactly one Laborers study card']
    parent=headings[0].parent
    while parent and not parent.has('jj-card'):parent=parent.parent
    if not parent:return ['Missing Laborers card container']
    errors=[];ns=list(parent.walk())
    refs=[n for n in ns if n.tag=='a' and n.text()==REF[1]]
    if len(refs)!=1 or refs[0].attrs.get('href')!=HREF or not refs[0].has('fc-inline-scripture'):
        errors.append('Laborers card must link Matthew 19:27–30 at its reference')
    elif refs[0].parent.tag!='p':errors.append('Laborers source must remain in description')
    if not any(n.tag=='a' and n.attrs.get('href')==DEST and n.has('jj-card-action') for n in ns):
        errors.append('Laborers onward study action missing')
    for n in ns:
        if n.tag!='a':continue
        p=n.parent
        while p:
            if p.tag=='a':errors.append('Nested card anchors are invalid');break
            p=p.parent
    return errors

def self_test():
    item=[DEST,TITLE,'Read {0} in its setting.',{'refs':[REF]}]
    actual=card(item)
    assert not check(actual)
    source=scripture(REF)
    assert check(actual.replace(source,REF[1],1))
    assert check(actual.replace('id=p27-p30','id=p27',1))
    assert check('<a href="/wrong">'+actual+'</a>')
    assert check(actual.replace('class="jj-card-action"','class="removed"',1))
    old=['/example.html','Example','Ordinary description.']
    expected='<a class="jj-card" href="/example.html"><h3>Example</h3><p>Ordinary description.</p><span class="jj-card-action">Open study →</span></a>'
    assert card(old)==expected
    preview={'thumbnail':'example.webp','width':100,'height':50,'alt':'Example scene.'}
    image='<img class="jj-card-preview" src="/example.webp" width="100" height="50" loading="lazy" decoding="async" alt="Example scene.">'
    assert card(old,preview)==expected.replace('<h3>',image+'<h3>',1)

if __name__=='__main__':
    from build_jesus_journey import ROOT
    self_test();errors=check((ROOT/'jesus-christ/parables/stewardship.html').read_text(encoding='utf8'))
    print({'errors':errors});raise SystemExit(bool(errors))
