"""Exact current hub wrapper/inverse controls; not browser or release approval."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
import emma_hub_citation_successor as c
import emma_story_successor as historical

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.data=[]; self.anchors=[]; self.depth=0
    def handle_data(self,data): self.data.append(data)
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            assert self.depth==0, 'Nested anchor'
            self.depth+=1; self.anchors.append(dict(attrs))
    def handle_endtag(self,tag):
        if tag=='a': self.depth-=1

class HubCitationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.raw=(c.ROOT/c.NAME).read_bytes()
        self.manifest=(c.ROOT/c.MANIFEST).read_bytes()
        self.write(c.NAME,self.raw);self.write(c.MANIFEST,self.manifest)
    def write(self,name,data):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    def test_exact_round_trip(self):
        self.assertEqual(c.sha(self.raw),c.AFTER)
        old=c.restore(c.NAME,self.raw,self.root)
        self.assertEqual(c.sha(old),c.BEFORE)
        self.assertEqual(c.advance(c.NAME,old,self.root),self.raw)
        self.assertEqual(c.check(self.root)['files'],1)
    def test_wrong_owner_identity(self):
        self.assertEqual(c.restore('unknown.html',self.raw,self.root),self.raw)
        old=c.restore(c.NAME,self.raw,self.root)
        self.assertEqual(c.advance('unknown.html',old,self.root),old)
    def test_unknown_current_identity_and_gate_rejection(self):
        bad=self.raw+b' ';self.write(c.NAME,bad)
        self.assertEqual(c.restore(c.NAME,bad,self.root),bad)
        with self.assertRaises(ValueError): c.check(self.root)
    def test_unknown_predecessor_identity(self):
        old=c.restore(c.NAME,self.raw,self.root)+b' '
        self.assertEqual(c.advance(c.NAME,old,self.root),old)
    def test_changed_inside_anchor_rejected(self):
        bad=self.raw.replace(b'id=p12-p16#p12',b'id=p12-p15#p12',1)
        self.assertNotEqual(bad,self.raw);self.write(c.NAME,bad)
        with self.assertRaises(ValueError): c.check(self.root)
    def test_changed_outside_anchor_rejected(self):
        bad=bytes([self.raw[0]^1])+self.raw[1:];self.write(c.NAME,bad)
        with self.assertRaises(ValueError): c.check(self.root)
    def test_omitted_wrapper_rejected(self):
        row=json.loads(self.manifest)['pairs'][0]
        self.write(c.NAME,self.raw.replace(row['after'].encode(),row['before'].encode(),1))
        with self.assertRaises(ValueError): c.check(self.root)
    def test_duplicate_wrapper_rejected(self):
        row=json.loads(self.manifest)['pairs'][0]
        self.write(c.NAME,self.raw+row['after'].encode())
        with self.assertRaises(ValueError): c.check(self.root)
    def test_manifest_tamper_rejected(self):
        value=json.loads(self.manifest);value['pairs'][0]['before']+=' '
        self.write(c.MANIFEST,json.dumps(value).encode())
        with self.assertRaises(ValueError): c.check(self.root)
    def test_missing_inputs_rejected(self):
        for name in [c.NAME,c.MANIFEST]:
            p=self.root/name;data=p.read_bytes();p.unlink()
            with self.assertRaises((ValueError,OSError)): c.check(self.root)
            p.write_bytes(data)
    def test_visible_data_and_crlf_unchanged(self):
        old=c.restore(c.NAME,self.raw,self.root);a=Text();b=Text()
        a.feed(old.decode());b.feed(self.raw.decode())
        self.assertEqual(''.join(a.data),''.join(b.data))
        self.assertEqual(old.count(b'\r\n'),self.raw.count(b'\r\n'))
    def test_exact_safe_anchor_markup(self):
        rows=json.loads(self.manifest)['pairs']
        self.assertEqual([r['label'] for r in rows],['Luke 6:12–16','John 4:31–34'])
        expected=['https://www.churchofjesuschrist.org/study/scriptures/nt/luke/6?lang=eng&id=p12-p16#p12','https://www.churchofjesuschrist.org/study/scriptures/nt/john/4?lang=eng&id=p31-p34#p31']
        for row,href in zip(rows,expected):
            p=Text();p.feed(row['after']);self.assertEqual(len(p.anchors),1)
            a=p.anchors[0];self.assertEqual(a['href'],href);self.assertEqual(a['class'],'fc-inline-scripture')
            self.assertEqual(a['target'],'_blank');self.assertEqual(a['rel'],'noopener noreferrer')
    def test_unchanged_historical_layer(self):
        self.write('docs/emma-story-successor/manifest.json',(c.ROOT/'docs/emma-story-successor/manifest.json').read_bytes())
        with c.predecessor_view(self.root) as view:
            self.assertEqual(historical.check(view)['status'],'EMMA_STORY_SUCCESSOR_EVIDENCE_PASS')
            self.assertEqual((view/c.NAME).read_bytes(),c.restore(c.NAME,self.raw,self.root))

if __name__=='__main__': unittest.main()
