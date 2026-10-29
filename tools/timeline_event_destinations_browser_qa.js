/* Verify actual image-link landings in the hosted Timeline browser. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
module.exports=async function(page,origin,out){
 assert.equal(process.env.CI,'true','Hosted CI only');
 const bindings=require('./timeline_51_destination_bindings').read(fs.readFileSync(path.join(__dirname,'../docs/reviews/timeline-51-destination-bindings.json')));
 const routes={life:['life-of-christ-journey-map.html','LifeTimeline'],handcart:['willie-and-martin-handcart-map.html','HandcartTimeline'],history:['latter-day-saint-church-history-timeline.html','HistoryTimeline']};
 const targets=bindings.filter(b=>b.target),records=[];assert.equal(targets.length,50);
 const evidenceDir=path.join(out,'event-destinations');fs.mkdirSync(evidenceDir,{recursive:true});
 for(const profile of [{name:'desktop',width:1366,height:900},{name:'phone',width:390,height:844}]){
  await page.setViewportSize({width:profile.width,height:profile.height});
  for(const b of targets){
   const [route,api]=routes[b.timeline];
   await page.goto(origin+'/timelines/'+route,{waitUntil:'load'});
   await page.waitForFunction(api=>window[api]&&window.TimelineImages,api);
   await page.evaluate(({api,index})=>window[api].select(index),{api,index:b.index});
   const figure=page.locator('[data-timeline-image="'+b.index+'"]');await figure.waitFor({state:'visible'});
   const title=page.locator(b.timeline==='life'?'#dTitle':b.timeline==='handcart'?'#detail-title':'#history-event-'+b.index+' h3');assert.equal((await title.innerText()).trim(),b.event,'Actual selected event matches binding');
   await figure.scrollIntoViewIfNeeded();await page.waitForFunction(index=>{const img=document.querySelector('[data-timeline-image="'+index+'"] img');return img&&img.complete&&img.naturalWidth>0;},b.index,{timeout:15000});await figure.locator('img').evaluate(img=>img.decode());
   const link=figure.locator('a').first();assert.equal(await link.getAttribute('href'),b.target);
   const credit=figure.locator('figcaption a');assert.equal(await credit.getAttribute('href'),b.original_source);
   await Promise.all([page.waitForURL(origin+b.target),link.click()]);
   const anchor=new URL(origin+b.target).hash.slice(1),section=page.locator('[id="'+anchor+'"]');
   assert.equal(await section.count(),1);assert(await section.isVisible(),'Event section must be visible');assert.equal((await section.locator('h2,h3').first().innerText()).trim(),b.heading,'Landed heading matches the bound event');
   const heading=section.locator('h2,h3').first(),naturalLanding=profile.name==='desktop'&&b.timeline==='handcart'&&b.index===30;
   if(naturalLanding){
    // The shared fragment controller performs a final alignment 800ms after
    // load. Do not center this heading or capture an intermediate layout.
    await page.waitForLoadState('load');await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(1000);
    await page.waitForFunction(()=>{const h=document.querySelector('#timeline-handcart-31 h3'),nav=document.querySelector('[data-focuschrist-header="standard"]');if(!h||!nav)return false;const a=h.getBoundingClientRect(),n=nav.getBoundingClientRect(),s=getComputedStyle(nav);return s.position==='fixed'&&Math.abs(n.top)<=1&&a.top>=n.bottom&&a.top-n.bottom<=120&&a.bottom<=innerHeight;},{},{timeout:5000});
    const stable=await page.evaluate(async()=>{let previous=null;for(let i=0;i<8;i++){await new Promise(r=>requestAnimationFrame(r));const h=document.querySelector('#timeline-handcart-31 h3').getBoundingClientRect(),n=document.querySelector('[data-focuschrist-header="standard"]').getBoundingClientRect(),now=[scrollY,document.documentElement.scrollHeight,h.top,n.top,n.bottom];if(previous&&now.some((v,j)=>Math.abs(v-previous[j])>1))return false;previous=now;}return true;});
    assert(stable,'Big Mountain native landing geometry is stable before capture');
   }else await heading.evaluate(n=>n.scrollIntoView({block:'center',inline:'nearest'}));
   await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   assert(await heading.evaluate(n=>{const r=n.getBoundingClientRect(),header=document.querySelector('[data-focuschrist-header="standard"]'),style=header&&getComputedStyle(header),box=header&&header.getBoundingClientRect(),bottom=header&&['fixed','sticky'].includes(style.position)&&box.top<=0?Math.max(0,box.bottom):0;return r.width>0&&r.height>0&&r.top>=bottom&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth;}),'Landed event heading is in the viewport below the fixed header');
   const screenshot=profile.name+'-'+b.timeline+'-'+String(b.index+1).padStart(2,'0')+'.png';
   await page.screenshot({path:path.join(evidenceDir,screenshot),animations:'disabled'});
   records.push({profile:profile.name,timeline:b.timeline,event:b.index+1,target:b.target,heading:await section.locator('h2,h3').first().innerText(),screenshot:'event-destinations/'+screenshot,capture_method:naturalLanding?'settled_native_fragment':'centered_heading'});
  }
 }
 assert.equal(records.length,100);fs.writeFileSync(path.join(out,'event-destination-landings.json'),JSON.stringify({records,unresolved:bindings.filter(b=>!b.target)},null,2)+'\n');return records;
};
