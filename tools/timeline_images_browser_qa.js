/* Exhaustive assembled phone-image review evidence. Run only from the hosted Timeline runner. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
module.exports=async function(page,origin,out){
 const dir=path.join(out,'image-coverage');fs.mkdirSync(dir,{recursive:true});const records=[];
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 for(const [kind,route,total,api] of [['life','life-of-christ-journey-map.html',38,'LifeTimeline'],['handcart','willie-and-martin-handcart-map.html',33,'HandcartTimeline'],['history','latter-day-saint-church-history-timeline.html',51,'HistoryTimeline']]){
  await page.setViewportSize({width:390,height:844});await page.goto(origin+'/timelines/'+route,{waitUntil:'load'});await page.waitForFunction(api=>window[api]&&window.TimelineImages&&window.TimelineWorkspace,api);await page.evaluate(()=>document.fonts.ready);
  const coverage=await page.evaluate(kind=>Object.keys(window.TimelineImages.registry[kind]).map(Number),kind);assert.deepEqual(coverage,Array.from({length:total},(_,i)=>i),'Complete exact registry '+kind);
  for(let index=0;index<total;index++){
   const record={kind,index,number:index+1,route,status:'pending'};
   try{
    // Public controller selection changes the real narrative and emits the normal image event.
    await page.evaluate(({api,index})=>window[api].select(index),{api,index});
    const figure=page.locator('[data-timeline-image="'+index+'"]');assert.equal(await figure.count(),1,'Exactly one current entry figure');await figure.waitFor({state:'visible'});
    // Lazy pictures are activated by actual viewport entry, before decoding is requested.
    await figure.scrollIntoViewIfNeeded();await page.waitForFunction(index=>{const img=document.querySelector('[data-timeline-image="'+index+'"] img');return img&&img.complete&&img.naturalWidth>0;},index,{timeout:15000});await figure.locator('img').evaluate(img=>img.decode());
    record.evidence=await figure.evaluate((f,{kind,index,api})=>{const img=f.querySelector('img'),entry=window.TimelineImages.registry[kind][index],reader=kind==='history'?document.querySelector('#history-event-'+index):document.querySelector('[data-timeline-pane="detail"]'),r=img.getBoundingClientRect();return{entry,src:img.getAttribute('src'),currentSrc:img.currentSrc,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,width:r.width,height:r.height,caption:f.querySelector('figcaption').textContent,href:f.querySelector('a').getAttribute('href'),current:kind==='history'?window[api].selectedIndex:window[api].current,title:reader.querySelector('h2,h3,.detail-title')?.textContent||reader.textContent.trim().slice(0,160),container:kind==='history'?f.closest('article')?.id:f.parentElement.getAttribute('data-timeline-pane'),readerOverflow:getComputedStyle(reader).overflowY,documentWidth:document.documentElement.scrollWidth,viewport:innerWidth};},{kind,index,api});
    const e=record.evidence;assert.equal(e.current,index);assert.equal(e.src,e.entry.src);assert.equal(e.href,e.entry.href);assert(e.naturalWidth>0&&e.naturalHeight>0,'Image decoded');assert.equal(e.naturalWidth,e.entry.width);assert.equal(e.naturalHeight,e.entry.height);assert(e.caption.includes(e.entry.caption));if(e.entry.credit)assert(e.caption.includes(e.entry.credit));assert.equal(e.container,kind==='history'?'history-event-'+index:'detail');assert(e.documentWidth<=e.viewport+3,'Image adds no horizontal document overflow');assert(e.width>150&&e.height>30,'Readable image frame');if(!e.entry.frame)assert(Math.abs(e.width/e.height-e.naturalWidth/e.naturalHeight)<.02,'Natural image aspect ratio');
    await figure.scrollIntoViewIfNeeded();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));const file=kind+'-'+String(index+1).padStart(2,'0')+'.png';await figure.screenshot({path:path.join(dir,file),animations:'disabled'});record.screenshot='image-coverage/'+file;record.status='passed';
   }catch(error){record.status='failed';record.error=error.stack||String(error);await page.screenshot({path:path.join(dir,kind+'-'+(index+1)+'-failure.png'),fullPage:false,animations:'disabled'}).catch(()=>{});}
   records.push(record);
  }
 }
 fs.writeFileSync(path.join(out,'image-coverage-report.json'),JSON.stringify({expected:122,records},null,2));
 fs.writeFileSync(path.join(out,'image-coverage-contact-sheet.html'),'<!doctype html><meta charset="utf-8"><title>122 assembled timeline pictures</title><style>body{margin:20px;background:#07191d;color:#f3ead6;font:16px Georgia}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}article{min-width:0;border:1px solid #8a733f;padding:12px}img{width:100%;height:auto}a{color:#ead49b}</style><h1>122 assembled phone story pictures</h1><p>Actual rendered figures, original source links and captions; provider behavior and owner phone acceptance remain separate evidence.</p><main>'+records.map(r=>'<article><h2>'+escape(r.kind+' '+r.number)+'</h2><p>'+escape(r.evidence?.title||r.error)+'</p>'+(r.screenshot?'<img loading="lazy" src="'+escape(r.screenshot)+'">':'')+'<p>'+escape(r.status)+'</p></article>').join('')+'</main>');
 assert.equal(records.length,122);assert(records.every(r=>r.status==='passed'),'All122 assembled pictures must pass; see image-coverage-report.json');return records;
};
