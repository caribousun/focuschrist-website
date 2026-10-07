/* Focused opening evidence; actual artwork composition still requires independent pixel review. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
module.exports=async function(page,origin,out){
 const records=[];
 for(const [width,height,scale] of [[1366,768,1],[1920,900,1],[1366,500,1],[390,844,1],[320,740,1],[320,900,2]])for(const kind of ['history','life','handcart']){
  const r={kind,width,height,scale};try{
   await page.setViewportSize({width,height});await page.goto(origin+'/timelines/'+({life:'life-of-christ-journey-map',history:'latter-day-saint-church-history-timeline',handcart:'willie-and-martin-handcart-map'}[kind])+'.html',{waitUntil:'load'});
   await page.evaluate(()=>document.fonts.ready);if(scale!==1)await page.evaluate(scale=>{const nodes=[...document.body.querySelectorAll('*')],sizes=nodes.map(n=>parseFloat(getComputedStyle(n).fontSize));nodes.forEach((n,i)=>n.style.fontSize=sizes[i]*scale+'px');},scale);await page.evaluate(()=>window.dispatchEvent(new Event('resize')));await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await page.evaluate(()=>scrollTo(0,0));
   r.header=await require('./timeline_header_geometry_qa')(page);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+3),'Opening has no horizontal overflow');
   {
    const hero=page.locator('.fc-visual-hero');assert.equal(await hero.count(),1,'Each corrected page has one real shared image hero');const img=hero.locator('img');await img.evaluate(i=>i.decode());r.image=await img.evaluate(i=>({src:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,alt:i.alt}));assert(r.image.width>500&&r.image.height>200&&r.image.alt.length>20,'Actual described artwork loaded');if(kind==='life'){assert(r.image.src.endsWith(width<=700?'assets/heroes/topics/jesus-mobile.webp':'assets/heroes/topics/jesus-desktop.webp'),'Approved existing Life artwork rendition');}
    if(kind==='handcart'){assert(r.image.src.endsWith('assets/heroes/pioneers.webp'));}
    const reference=await page.context().newPage();try{await reference.setViewportSize({width,height});await reference.goto(origin+'/birth-of-christ.html',{waitUntil:'load'});await reference.evaluate(()=>document.fonts.ready);await reference.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));const expected=await reference.locator('.fc-visual-hero').boundingBox(),actual=await hero.boundingBox();r.frame={expected,actual};assert(Math.abs(expected.width-actual.width)<=1&&Math.abs(expected.height-actual.height)<=1,'Corrected page uses approved Birth shared hero frame');if(width===390)await reference.screenshot({path:path.join(out,'opening-reference-birth-390.png'),animations:'disabled'});}finally{await reference.close();}
    const clearance=await hero.evaluate(n=>({top:n.getBoundingClientRect().top,headerBottom:document.querySelector('[data-focuschrist-header="standard"]').getBoundingClientRect().bottom}));assert(clearance.top>=clearance.headerBottom-1,'Header cannot cover opening artwork');r.clearance=clearance;
   }
   if(kind==='history'){
    assert(r.image.src.endsWith('assets/timelines/church-history-grove.webp'));
    r.kicker=await page.locator('.fc-page-intro .kicker').evaluate(n=>{const c=getComputedStyle(n);return {color:c.color,background:c.backgroundColor,text:n.textContent};});const rgb=s=>s.match(/[\d.]+/g).map(Number),fg=rgb(r.kicker.color),bg=rgb(r.kicker.background);assert(bg.length===3||bg[3]===1,'Kicker uses explicit opaque contrast surface');const lum=c=>c.slice(0,3).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0);r.contrast=(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);assert(r.contrast>=4.5,'History kicker has readable normal-text contrast');
   }
   {
    const hero=page.locator('.fc-visual-hero'),study={life:'../answers/jesus-christ-latter-day-saint-beliefs.html#nested-page-title',history:'../church-history.html#history-first-vision-title',handcart:'../pioneers.html#pioneer-page-title'}[kind],fallback={life:'../assets/heroes/topics/jesus-full.webp',history:'../assets/timelines/church-history-grove.webp',handcart:'../assets/heroes/pioneers.webp'}[kind];
    assert.equal(await hero.getAttribute('data-hero-record'),'timeline-'+kind);
    assert.equal(await hero.getAttribute('data-hero-study'),study,'Exact owning study retained as metadata');
    assert.equal(await hero.getAttribute('href'),fallback,'Exact image fallback retained');
    const before=page.url();await hero.click();const panel=page.locator('#heroDetailDialog');await panel.waitFor({state:'visible'});
    assert.equal(page.url(),before,'Hero opens a panel without navigating');
    assert.equal(await panel.locator('[data-hero-study-link]').getAttribute('href'),new URL(study,before).href,'Actual panel pill reaches the exact owning study');
    assert((await panel.locator('[data-hero-study-link]').innerText()).trim().length>8,'Related study pill has a human label');
    assert(await panel.locator('[data-hero-source-link]').isVisible());assert(await panel.locator('[data-hero-ask-link]').isVisible());assert(await panel.locator('[data-full-image-viewer]').isVisible());
    r.panel={study:await panel.locator('[data-hero-study-link]').getAttribute('href'),image:await panel.locator('.fc-artwork-detail-media img').getAttribute('src')};
    assert.equal(r.panel.image,new URL(kind==='life'&&width<=700?'../assets/heroes/topics/jesus-mobile.webp':fallback,before).href,'Panel uses exact selected artwork');
    // Compare computed pill tokens with the existing standard, not class names alone.
    if(scale===1&&(width===390||width===1366)&&height!==500){
     const reference=await page.context().newPage();try{
      await reference.setViewportSize({width,height});await reference.goto(origin+'/answers/jesus-christ-latter-day-saint-beliefs.html',{waitUntil:'load'});await reference.evaluate(()=>document.fonts.ready);await reference.locator('a.fc-visual-hero[data-hero-viewer]').click();await reference.locator('#heroDetailDialog').waitFor({state:'visible'});
      const tokens=n=>{const c=getComputedStyle(n);return Object.fromEntries(['fontFamily','fontSize','fontWeight','lineHeight','minHeight','paddingTop','paddingRight','paddingBottom','paddingLeft','borderRadius','borderTopWidth','borderTopStyle','borderTopColor','color','backgroundColor','backgroundImage','display','alignItems','justifyContent','textAlign'].map(k=>[k,c[k]]));};
      r.pillParity=[];
      for(const selector of ['[data-hero-source-link]','[data-hero-study-link]','[data-hero-ask-link]','[data-full-image-viewer]','button[data-hero-close]']){
       const target=panel.locator('.fc-artwork-detail-actions '+selector),standard=reference.locator('#heroDetailDialog .fc-artwork-detail-actions '+selector),actual=await target.evaluate(tokens),expected=await standard.evaluate(tokens);assert.deepEqual(actual,expected,'Timeline picture pill matches standard computed size/style: '+selector);assert((await target.boundingBox()).height>=48,'Standard 48px picture pill target');r.pillParity.push({selector,actual,expected});
      }
      await panel.locator('[data-full-image-viewer]').click();await reference.locator('#heroDetailDialog [data-full-image-viewer]').click();await page.locator('.fc-full-image-viewer').waitFor({state:'visible'});await reference.locator('.fc-full-image-viewer').waitFor({state:'visible'});
      for(const selector of ['.fc-full-image-close','.fc-full-image-download',...(kind==='life'?['.fc-full-image-version select']:[])]){const actual=await page.locator('.fc-full-image-viewer '+selector).evaluate(tokens),expected=await reference.locator('.fc-full-image-viewer '+selector).evaluate(tokens);assert.deepEqual(actual,expected,'Timeline full-size control matches standard: '+selector);r.pillParity.push({selector,actual,expected});}
      await page.keyboard.press('Escape');assert(await panel.isVisible(),'Full-size Escape returns to picture panel');
     }finally{await reference.close();}
    }
    await page.keyboard.press('Escape');assert(!(await panel.isVisible()),'Escape closes panel');assert(await hero.evaluate(n=>document.activeElement===n),'Focus returns to hero');await page.evaluate(()=>scrollTo(0,0));
   }
   const cue=page.locator('.fc-page-intro .timeline-opening-continue');
   assert.equal(await cue.count(),1,'Exactly one authored Continue invitation exists');
   assert(await cue.isVisible(),'Authored Continue remains visible');
   assert.equal(await page.locator('.fc-page-intro .timeline-navigation').count(),0,'Timeline navigation is truly moved out of the opening DOM');
   const overviewId={history:'history-journey-overview',life:'life-journey-overview',handcart:'handcart-journey-overview'}[kind];
   const target=await cue.getAttribute('href');
   assert.equal(target,'#'+overviewId,'Continue retains its exact overview destination');
   const overview=page.locator('#'+overviewId+'.timeline-life-overview');
   assert.equal(await overview.count(),1,'Continue reaches the existing overview section');
   const nav=overview.locator(':scope > nav.timeline-navigation[aria-label="Timeline navigation"]');
   assert.equal(await page.locator('.timeline-navigation').count(),1,'No duplicate timeline navigation remains');
   assert.equal(await nav.count(),1,'The real navigation is a direct child of its overview');
   const links=nav.locator('a.timeline-return');
   assert.equal(await nav.locator('a').count(),2,'Overview contains exactly two navigation links');
   assert.equal(await links.count(),2,'Both existing pill controls are retained');
   r.navigation=await links.evaluateAll(nodes=>nodes.map(n=>({label:n.textContent.trim().replace(/\s+/g,' '),href:n.getAttribute('href')})));
   assert.deepEqual(r.navigation,[{label:'All timelines',href:'../timeline.html'},{label:kind==='history'?'Explore timeline':'Explore journey',href:kind==='history'?'#historyWorkspace':'#journeyWorkspace'}],'Navigation labels and destinations remain exact');
   assert.equal(await page.locator(r.navigation[1].href).count(),1,'Explore destination remains present');
   r.controls=await page.locator('.hero a,.fc-page-intro a').evaluateAll(nodes=>nodes.filter(n=>n.getClientRects().length).map(n=>{const b=n.getBoundingClientRect();return {label:n.textContent.trim().replace(/\s+/g,' '),authored:n.classList.contains('timeline-opening-continue'),top:b.top,bottom:b.bottom,height:b.height,width:b.width,scroll:n.scrollHeight,client:n.clientHeight,left:b.left,right:b.right};}));
   assert.equal(r.controls.length,1,'Continue is the only visible opening control');
   assert(r.controls[0].authored,'The visible opening control is the original authored cue');
   assert(r.controls.every(c=>c.height>=44&&c.scroll<=c.client+1&&c.left>=-1&&c.right<=width+1),'Opening Continue has a complete label,44px height and no overflow');
   r.continueTarget=target;
   if(scale===1&&height!==500){
    assert(r.controls.every(c=>c.top>=0&&c.bottom<=height-8),'Normal opening Continue stays within the first viewport');
    const bounds=await overview.boundingBox();assert(bounds&&bounds.y>=height-1,'Following overview begins after normal opening viewport');r.overviewTop=bounds.y;
   }
   await page.screenshot({path:path.join(out,'opening-'+kind+'-'+width+'x'+height+'-scale'+scale+'.png'),animations:'disabled'});
   await nav.scrollIntoViewIfNeeded();
   r.navigationGeometry=await links.evaluateAll(nodes=>nodes.map(n=>{const b=n.getBoundingClientRect(),range=document.createRange();range.selectNodeContents(n);const text=range.getBoundingClientRect();return {label:n.textContent.trim(),height:b.height,left:b.left,right:b.right,scrollWidth:n.scrollWidth,clientWidth:n.clientWidth,scrollHeight:n.scrollHeight,clientHeight:n.clientHeight,textContained:text.left>=b.left-1&&text.right<=b.right+1&&text.top>=b.top-1&&text.bottom<=b.bottom+1,tabIndex:n.tabIndex};}));
   assert(r.navigationGeometry.every(c=>c.height>=44&&c.left>=-1&&c.right<=width+1&&c.scrollWidth<=c.clientWidth+1&&c.scrollHeight<=c.clientHeight+1&&c.textContained&&c.tabIndex>=0),'Relocated pills retain44px height, complete labels, keyboard access and no overflow at every profile');
   r.navigationFocus=[];
   for(let i=0;i<2;i++){
    await links.nth(i).focus();
    const focus=await links.nth(i).evaluate(n=>{const c=getComputedStyle(n);return {active:document.activeElement===n,outlineStyle:c.outlineStyle,outlineWidth:parseFloat(c.outlineWidth)};});
    assert(focus.active&&focus.outlineStyle!=='none'&&focus.outlineWidth>=2,'Each relocated pill receives visible keyboard focus');r.navigationFocus.push(focus);
   }
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+3),'Relocated navigation adds no horizontal overflow');
   await nav.screenshot({path:path.join(out,'navigation-'+kind+'-'+width+'x'+height+'-scale'+scale+'.png'),animations:'disabled'});
   if(kind==='history'){const sources=page.locator('section.sources');await sources.scrollIntoViewIfNeeded();r.sources=await sources.evaluate(n=>{const c=getComputedStyle(n);return {background:c.backgroundColor,gradient:c.backgroundImage,border:c.borderTopColor,text:[...n.querySelectorAll('h2,p,li,a')].map(e=>({tag:e.tagName,color:getComputedStyle(e).color,text:e.textContent})),scroll:n.scrollWidth,client:n.clientWidth};});assert(r.sources.gradient!=='none','Sources uses shared green/teal panel gradient');const rgb=s=>s.match(/[\d.]+/g).map(Number),lum=c=>c.slice(0,3).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0),colors=r.sources.gradient.slice(r.sources.gradient.lastIndexOf('linear-gradient(')).match(/rgba?\([^)]+\)/g)||[];assert(colors.length>=2);for(const text of r.sources.text)for(const color of colors){const a=lum(rgb(text.color)),b=lum(rgb(color));assert((Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5,'Readable sources text/links against each panel gradient endpoint');}assert(r.sources.scroll<=r.sources.client+1,'Sources content stays within panel');await sources.screenshot({path:path.join(out,'sources-history-'+width+'x'+height+'-scale'+scale+'.png'),animations:'disabled'});}
   r.status='PASS';
  }catch(e){r.error=String(e);r.stack=e.stack;await page.screenshot({path:path.join(out,'opening-'+kind+'-'+width+'x'+height+'-failure.png'),animations:'disabled'}).catch(()=>{});}records.push(r);
 }
 fs.writeFileSync(path.join(out,'timeline-openings.json'),JSON.stringify(records,null,2));assert.equal(records.length,18);assert.deepEqual(records.filter(r=>r.error),[],'All changed opening profiles must pass');return records;
};
