/* Mission caption must stay beneath its unchanged picture and the directory label must center. */
const assert=require('node:assert/strict');
module.exports=async function(page,origin){
 const records=[];
 for(const [width,enlarged] of [[320,false],[390,false],[1040,false],[1536,false],[390,true],[1536,true]]){
  await page.setViewportSize({width,height:1000});
  await page.goto(origin+'/missionary.html',{waitUntil:'load'});
  await page.locator('.fc-unified-continue').waitFor({state:'visible'});
  if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const measure=()=>page.evaluate(()=>{
   const figure=document.querySelector('.fc-missionary-commission-artwork'),img=figure.querySelector('img'),caption=figure.querySelector('figcaption'),label=document.querySelector('.fc-mission-directory-label');
   const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom};};
   const range=document.createRange();range.selectNodeContents(label);const r=range.getBoundingClientRect(),l=label.getBoundingClientRect();
   const other=document.querySelector('.fc-missionary-visual--purpose');
   return {image:rect(img),caption:rect(caption),captionPosition:getComputedStyle(caption).position,link:img.closest('a').getAttribute('href'),source:img.getAttribute('src'),labelCenterError:Math.abs(r.x+r.width/2-l.x-l.width/2),labelAlign:getComputedStyle(label).textAlign,purposeClearance:other.querySelector('figcaption').getBoundingClientRect().top-other.querySelector('img').getBoundingClientRect().bottom,overflow:document.documentElement.scrollWidth-innerWidth};
  });
  const actual=await measure();
  const noOverlay=x=>x.captionPosition==='static'&&x.caption.y>=x.image.bottom-.5;
  assert(noOverlay(actual),`Commission caption overlays artwork at ${width}/${enlarged}`);
  assert(actual.purposeClearance>=-.5,'Existing purpose caption must remain below picture');
  assert.equal(actual.labelAlign,'center');assert(actual.labelCenterError<=1,'Directory text must center in its actual rail');
  assert(actual.overflow<=1,'No horizontal overflow');assert(actual.link&&actual.source,'Preserve image and artwork link');
  const defect=await page.addStyleTag({content:'.fc-missionary-page .fc-missionary-commission-artwork > figcaption {position:absolute!important;bottom:0!important;}'});
  const legacy=await measure();assert(!noOverlay(legacy),'Negative overlay fixture must be detected');
  for(const key of ['x','y','width','height'])assert(Math.abs(actual.image[key]-legacy.image[key])<.5,'Caption repair must preserve image geometry '+key);
  assert.equal(actual.link,legacy.link);assert.equal(actual.source,legacy.source);
  await defect.evaluate(e=>e.remove());
  records.push({width,enlarged,...actual,status:'PASS',negativeOverlayDetected:true});
 }
 const supporting=[];
 for(const [width,enlarged] of [[320,false],[390,false],[1040,false],[1536,false],[390,true],[1536,true]]){
  await page.setViewportSize({width,height:1000});
  for(const [route,selector,count] of [['answers.html','.fc-answers-family-art',1],['ask.html','.ask-emmaus-art',1],['index.html','.fc-home-featured-art,.fc-home-purpose-art',3]]){
   await page.goto(origin+'/'+route,{waitUntil:'load'});
   if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   const measure=()=>page.locator(selector).evaluateAll(figures=>figures.map(f=>{const img=f.querySelector('img'),cap=f.querySelector('figcaption'),i=img.getBoundingClientRect(),c=cap.getBoundingClientRect();return {source:img.getAttribute('src'),link:img.closest('a').getAttribute('href'),image:[i.x,i.y,i.width,i.height],clearance:c.top-i.bottom,position:getComputedStyle(cap).position};}));
   const actual=await measure();assert.equal(actual.length,count);
   assert(actual.every(c=>c.clearance>=-.5&&c.position==='static'),'Supporting caption overlaps '+route+'/'+width);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Supporting page overflow');
   const defect=await page.addStyleTag({content:selector.split(',').map(x=>x+' > figcaption').join(',')+'{position:absolute!important;bottom:0!important;}'});
   const old=await measure();assert(old.every(c=>c.clearance<0),'Old supporting overlay fixture must fail');
   actual.forEach((c,i)=>{assert.equal(c.source,old[i].source);assert.equal(c.link,old[i].link);assert(Math.abs(c.image[2]-old[i].image[2])<.5&&Math.abs(c.image[3]-old[i].image[3])<.5,'Original supporting image dimensions preserved');});
   await defect.evaluate(e=>e.remove());supporting.push({route,width,enlarged,captions:actual,status:'PASS'});
  }
 }
 records.push({supportingCaptionProfiles:supporting});
 console.log('PASS:6 Mission profiles plus18 supporting-page profiles covering five captions; negative overlays and unchanged image dimensions/links');
 return records;
};
