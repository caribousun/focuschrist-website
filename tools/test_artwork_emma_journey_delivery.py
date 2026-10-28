"""Synthetic integrity tests only. Fixtures are not review/owner evidence."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,features,__version__
import artwork_emma_journey_delivery as v

def sha(b):return hashlib.sha256(b).hexdigest()
def pix(p):
 with Image.open(p) as im:
  im=im.convert('RGBA');return hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
class Delivery(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name);root=cls.root
  def write(name,data):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return {'path':name,'bytes':len(data),'sha256':sha(data)}
  def j(name,obj):return write(name,json.dumps(obj,sort_keys=True).encode())
  def arr(name,im):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);im.save(p,format='PNG' if name.endswith('.png') else 'WEBP',quality=92,method=6);raw=p.read_bytes();return {'path':name,'bytes':len(raw),'sha256':sha(raw),'pixel_sha256':pix(p),'dimensions':list(im.size)}
  # Entirely synthetic identities: patch the test-only reference pins to generated
  # fixture hashes. This exercises validation mechanics, not real likeness.
  from io import BytesIO
  def fake_png(color):
   b=BytesIO();Image.new('RGB',(2,2),color).save(b,format='PNG');return b.getvalue()
  master=write('refs/master.png',fake_png('red'));smile=write('refs/smile.png',fake_png('blue'))
  cls.old_pins=(v.ID_MASTER,v.EXPRESSION);v.ID_MASTER=master['sha256'];v.EXPRESSION=smile['sha256']
  common=write('evidence/synthetic.txt',b'Test fixture only: not actual review');mandates=[write(name,('synthetic '+name).encode()) for name in sorted(v.MANDATES)];mandate_map={m['path']:m['sha256'] for m in mandates};page=write(v.ROUTE,b'<html>synthetic</html>');rows=[]
  for i,id in enumerate(v.SCENES):
   origin=id=='origin';prompt=write('prompts/'+id+'.txt',('synthetic '+id).encode());pre={'scene_id':id,'route':v.ROUTE,'source_urls':['https://example.org/source'],'prompt':prompt,'references':[] if origin else [master,smile],'characters':[] if origin else ['Emma Hale Smith'],'chronology':{'kind':v.CHRONOLOGY[id][0],'start':v.CHRONOLOGY[id][1],'end':v.CHRONOLOGY[id][2],'age_range':list(v.CHRONOLOGY[id][3]) if v.CHRONOLOGY[id][3] else None,'basis':'synthetic'},'mandates':mandates,'setting':'synthetic','period_clothing':'synthetic or not applicable','scene_action':'synthetic'}
   y=Image.linear_gradient('L').resize((1536,1024));x=Image.linear_gradient('L').rotate(90,expand=True).resize((1536,1024));im=Image.merge('RGB',(x.point(lambda p:(p+i*19)%256),y.point(lambda p:(p+i*29)%256),x.point(lambda p:(p//2+i*11)%256)))
   src='assets/page-art/emma-journey/originals/emma-journey-'+id+'-source.png';original=arr(src,im);derivs=[]
   for width in (640,960,1536):
    scaled=im if width==1536 else im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
    derivs.append(arr('assets/page-art/emma-journey/emma-journey-'+id+'-'+str(width)+'.webp',scaled))
   ordering=j('sequence/'+id+'.json',{'actor':'Albert','scene_id':id,'prompt_sha256':prompt['sha256'],'output_sha256':original['sha256'],'preflight_receipt_ids':[id+'-Fermi-preflight',id+'-Newton-preflight'],'both_preflights_preceded_generation':True,'evidence':[common]})
   gen={'actor':'Albert','scene_id':id,'prompt_sha256':prompt['sha256'],'output_sha256':original['sha256'],'reference_sha256':[x['sha256'] for x in pre['references']],'edit_target_sha256':None,'provider_model':'UNKNOWN','provider_job_id':'UNKNOWN','call_timestamp_status':'UNKNOWN_NOT_INFERRED','call_timestamp':None,'unknown_timestamp_basis':'synthetic fixture','no_unlisted_inputs':True,'evidence':[common],'preflight_sequence_evidence':ordering}
   row={'id':id,'kind':'PERSON_FREE_CONTEXT' if origin else 'EMMA_CHARACTER','preflight':pre,'original':original,'derivatives':derivs,'generation_lineage':j('generation/'+id+'.json',gen),'derivative_lineage':{'source_sha256':original['sha256'],'pillow_version':__version__,'libwebp_version':features.version('webp'),'resampling':'LANCZOS','quality':92,'method':6,'evidence':[common]}}
   reviews={}
   for phase in ('preflight','finished'):
    binding=v.canonical(pre) if phase=='preflight' else v.canonical(row)
    for who in ('Fermi','Newton'):
     doc={'reviewer':who,'stage':phase,'verdict':'PASS','withdrawn':False,'binding_sha256':binding,'actual_actor':who+' synthetic','observations':'synthetic','reviewed_at':'2026-10-28T12:00:00Z','evidence':[common],'receipt_id':id+'-'+who+'-'+phase,'reviewed_before_generation':True,'mandate_bindings':mandate_map}
     if phase=='finished':doc.update(full_resolution_inspected=True,face_details_inspected=not origin,checks={x:'synthetic' for x in v.CHECKS})
     reviews[who.lower()+'_'+phase]=j('reviews/'+id+'-'+who+'-'+phase+'.json',doc)
   row['reviews']=reviews;rows.append(row)
  spec={'route':v.ROUTE,'page_source':page,'page_context':[],'scenes':rows};binding=v.canonical(spec);assembled=[]
  for who in ('Fermi','Newton','Albert'):
   doc={'reviewer':who,'stage':'assembled','verdict':'PASS','withdrawn':False,'binding_sha256':binding,'actual_actor':who+' synthetic','observations':'synthetic','reviewed_at':'2026-10-28T13:00:00Z','evidence':[common],'full_context_inspected':True,'checks':{x:'synthetic' for x in v.CHECKS},'mandate_bindings':mandate_map}
   if who=='Albert':doc['rendered']={'desktop':common,'phone':common}
   assembled.append(j('reviews/assembled-'+who+'.json',doc))
  owner=j('reviews/owner.json',{'kind':'direct_owner_acceptance','actor':'Wyatt','verdict':'ACCEPT','subject_sha256':binding,'evidence':[common]})
  cls.record={'schema':1,'status':'REVIEWED_EXACT_EMMA_JOURNEY','spec':spec,'assembled_reviews':assembled,'owner_acceptance':owner}
 @classmethod
 def tearDownClass(cls):
  v.ID_MASTER,v.EXPRESSION=cls.old_pins;cls.tmp.cleanup()
 def check(self,record=None,added=None,covered=None):
  r=copy.deepcopy(self.record if record is None else record)
  with patch.object(v,'APPROVED_RECORD_SHA256',v.canonical(r)):
   return v.validate(self.root,r,set(v.ASSETS) if added is None else added,set() if covered is None else covered,set(),pix,lambda root,route:set())
 def test_synthetic_complete_path(self):
  assets,hashes,pixels=self.check();self.assertEqual(len(assets),44);self.assertEqual(len(hashes),44);self.assertEqual(len(pixels),44)
 def test_actual_pin_is_pending(self):
  self.assertIsNone(v.APPROVED_RECORD_SHA256)
  with self.assertRaisesRegex(ValueError,'pending'):v.validate(self.root,self.record,set(v.ASSETS),set(),set(),pix,lambda root,route:set())
 def test_scene_duplicate_missing_and_origin_not_character(self):
  for transform in ('duplicate','missing','origin'):
   r=copy.deepcopy(self.record)
   if transform=='duplicate':r['spec']['scenes'][0]['id']='04'
   if transform=='missing':r['spec']['scenes'].pop()
   if transform=='origin':r['spec']['scenes'][-1]['kind']='EMMA_CHARACTER'
   with self.subTest(transform=transform),self.assertRaises((ValueError,KeyError)):self.check(r)
 def test_missing_extra_and_overlap_coverage(self):
  with self.assertRaises(ValueError):self.check(added=set(v.ASSETS)-{next(iter(v.ASSETS))})
  with self.assertRaises(ValueError):self.check(covered={next(iter(v.ASSETS))})
  self.assertEqual(len(v.ASSETS),44)
 def test_wrong_or_withdrawn_actual_receipt(self):
  for field,value in [('reviewer','Newton'),('verdict','HOLD'),('withdrawn',True),('mandate_bindings',{})]:
   r=copy.deepcopy(self.record);ptr=r['spec']['scenes'][0]['reviews']['fermi_preflight'];doc=json.loads((self.root/ptr['path']).read_bytes());doc[field]=value
   raw=json.dumps(doc,sort_keys=True).encode();name='reviews/mutated-'+field+'.json';f=self.root/name;f.write_bytes(raw);r['spec']['scenes'][0]['reviews']['fermi_preflight']={'path':name,'bytes':len(raw),'sha256':sha(raw)}
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(r)
 def test_different_valid_webp_is_not_a_derivative(self):
  import shutil
  with tempfile.TemporaryDirectory() as d:
   new=Path(d);shutil.copytree(self.root,new,dirs_exist_ok=True);r=copy.deepcopy(self.record);row=r['spec']['scenes'][0];a=row['derivatives'][0];p=new/a['path']
   Image.new('RGB',tuple(a['dimensions']),(240,10,20)).save(p,format='WEBP',quality=92,method=6);raw=p.read_bytes();a.update(bytes=len(raw),sha256=sha(raw),pixel_sha256=pix(p))
   scene_binding=v.canonical({k:value for k,value in row.items() if k!='reviews'})
   for who in ('fermi','newton'):
    pointer=row['reviews'][who+'_finished'];doc=json.loads((new/pointer['path']).read_bytes());doc['binding_sha256']=scene_binding;raw=json.dumps(doc,sort_keys=True).encode();f=new/pointer['path'];f.write_bytes(raw);pointer.update(bytes=len(raw),sha256=sha(raw))
   with patch.object(self,'root',new),self.assertRaisesRegex(ValueError,'deterministically reproduce'):self.check(r)
 def test_scene_chronology_and_mandate_set_cannot_drift(self):
  for change in ('chronology','mandates'):
   r=copy.deepcopy(self.record);pre=r['spec']['scenes'][0]['preflight']
   if change=='chronology':pre['chronology']['age_range']=[40,40]
   else:pre['mandates'].pop()
   with self.subTest(change=change),self.assertRaises(ValueError):self.check(r)
 def test_missing_operator_sequence_evidence_fails(self):
  import shutil
  with tempfile.TemporaryDirectory() as d:
   new=Path(d);shutil.copytree(self.root,new,dirs_exist_ok=True);r=copy.deepcopy(self.record);row=r['spec']['scenes'][0];pointer=row['generation_lineage'];doc=json.loads((new/pointer['path']).read_bytes());doc['preflight_sequence_evidence']={'path':'missing-ordering.json','bytes':0,'sha256':'0'*64};raw=json.dumps(doc,sort_keys=True).encode();(new/pointer['path']).write_bytes(raw);pointer.update(bytes=len(raw),sha256=sha(raw))
   scene_binding=v.canonical({k:value for k,value in row.items() if k!='reviews'})
   for who in ('fermi','newton'):
    ptr=row['reviews'][who+'_finished'];rec=json.loads((new/ptr['path']).read_bytes());rec['binding_sha256']=scene_binding;raw=json.dumps(rec,sort_keys=True).encode();(new/ptr['path']).write_bytes(raw);ptr.update(bytes=len(raw),sha256=sha(raw))
   with patch.object(self,'root',new),self.assertRaises(ValueError):self.check(r)
 def test_owner_or_review_missing(self):
  for change in ('owner','review','wrong-source'):
   r=copy.deepcopy(self.record)
   if change=='owner':r['owner_acceptance']={'path':'missing.json','bytes':0,'sha256':'0'*64}
   if change=='review':del r['spec']['scenes'][0]['reviews']['fermi_finished']
   if change=='wrong-source':r['spec']['page_source']['path']='unknown.html'
   with self.subTest(change=change),self.assertRaises((ValueError,KeyError)):self.check(r)
if __name__=='__main__':unittest.main()
