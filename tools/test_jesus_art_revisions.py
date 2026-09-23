import hashlib,json,tempfile,unittest
from pathlib import Path
from prepare_jesus_art import merge_batches

class RevisionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
  self.records=[]
  for number in (2,10):
   src=self.p/f'{number}.png';src.write_bytes(str(number).encode());sha=hashlib.sha256(src.read_bytes()).hexdigest()
   record={'generated_path':str(src),'original_sha256':sha,'reviewed':True,'review_record':f'review{number}.json','original':f'{number}.png','asset':f'{number}-full.webp','thumbnail':f'{number}-thumb.webp'}
   if self.records:record['supersedes_sha256']=self.records[-1]['original_sha256']
   (self.p/record['review_record']).write_text(json.dumps({'entries':[{'key':'scene','sha256':sha,'status':'pass'}]}))
   self.records.append(record)
  self.save()
 def save(self):
  for number,record in zip((2,10),self.records):(self.p/f'art-batch-{number}.json').write_text(json.dumps({'scene':record}))
 def merge(self,registry):return merge_batches(registry,list(self.p.glob('art-batch-*.json')),self.p)
 def test_numeric_revision_and_latest_registry_rerun(self):
  first=self.merge({'scene':self.records[0]});self.assertEqual(first['scene']['original'],'10.png')
  self.assertEqual(first,self.merge(first))
 def test_unapproved_revision_rejected(self):
  self.records[1]['reviewed']=False;self.save()
  with self.assertRaisesRegex(ValueError,'Unreviewed revision'):self.merge({'scene':self.records[0]})
 def test_unlinked_revision_rejected(self):
  self.records[1]['supersedes_sha256']='b'*64;self.save()
  with self.assertRaisesRegex(ValueError,'Unlinked revision'):self.merge({'scene':self.records[0]})
 def test_archive_overwrite_rejected(self):
  self.records[1]['asset']=self.records[0]['asset'];self.save()
  with self.assertRaisesRegex(ValueError,'overwrite archive'):self.merge({'scene':self.records[0]})

if __name__=='__main__':unittest.main()
