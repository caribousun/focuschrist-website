/* Hosted rendered checks for the requested Timeline controls. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
module.exports=async function(page,origin,out){
 assert.equal(process.env.CI,'true','Hosted CI only');
 const results=[];
 for(const profile of [{name:'desktop',width:1366,height:900},{name:'phone',width:390,height:844}]){
  await page.setViewportSize({width:profile.width,height:profile.height});
  await page.goto(origin+'/timelines/world-and-scripture-timeline.html#viewer',{waitUntil:'load'});
  assert(await page.locator('#mapview').isVisible(),'Moment & Map opens first');
  assert(await page.locator('#modeMap').evaluate(n=>n.classList.contains('on')));
  const counts=()=>page.evaluate(()=>{
   const svg=document.querySelectorAll('#worldmap .ghostpath,#worldmap .routepath,#worldmap .party,#worldmap .routelabel').length;
   let leaflet=0;if(typeof leafLayerGroup!=='undefined'&&leafLayerGroup)leafLayerGroup.eachLayer(n=>{if(['routefaint','routetraveled','party'].includes(n.__kind))leaflet++;});
   return {svg,leaflet};
  });
  const initial=await counts();assert(initial.svg+initial.leaflet>0,'Scenario routes initially present');
  const filterSummary=page.locator('#workspaceFilterState');
  const filterDisclosure=filterSummary.locator('xpath=parent::details');
  assert.equal(await filterDisclosure.count(),1,'Filter summary belongs to one disclosure');
  assert(!(await filterDisclosure.evaluate(n=>n.open)),'Filter starts closed');
  await filterSummary.click();assert(await filterDisclosure.evaluate(n=>n.open),'Filter opens through its summary');
  await page.locator('#catChips [data-cat="bible"]').click();await page.locator('#catChips [data-cat="bom"]').click();
  assert.deepEqual(await counts(),{svg:0,leaflet:0},'World-only removes scenario routes and party markers');
  assert(await page.locator('#routeLegend').evaluate(n=>n.hidden));
  for(const c of ['bible','bom','dual'])assert(await page.locator('[data-legend-category="'+c+'"]').evaluate(n=>n.hidden));
  assert(!await page.locator('[data-legend-category="world"]').evaluate(n=>n.hidden));
  assert(!/both journey paths are drawn|Book of Mormon promised-land pins/i.test(await page.locator('#mapNote').innerText()));
  // Capture the actual World-only state before restoring Book of Mormon.
  // The map and the legend may be far apart on a phone, so retain each as
  // a separate actual browser capture instead of composing or resizing them.
  await filterSummary.click();assert(!(await filterDisclosure.evaluate(n=>n.open)),'Filter closes for World-only evidence');
  const map=page.locator('.mapwrap');await map.scrollIntoViewIfNeeded();
  await map.screenshot({path:path.join(out,'requested-world-only-map-'+profile.name+'.png'),animations:'disabled'});
  const legend=page.locator('.legend-disclosure');await legend.locator('summary').click();assert(await legend.evaluate(n=>n.open));
  await legend.scrollIntoViewIfNeeded();await legend.screenshot({path:path.join(out,'requested-world-only-legend-'+profile.name+'.png'),animations:'disabled'});
  await legend.locator('summary').click();assert(!(await legend.evaluate(n=>n.open)));
  await filterSummary.click();assert(await filterDisclosure.evaluate(n=>n.open));
  await page.locator('#catChips [data-cat="bom"]').click();const restored=await counts();assert(restored.svg+restored.leaflet>0,'Book of Mormon restores scenario routes');
  await filterSummary.click();assert(!(await filterDisclosure.evaluate(n=>n.open)),'Filter closes through its summary');
  const settings=page.locator('.mapsettings');await settings.locator('summary').click();assert(await settings.evaluate(n=>n.open),'Map settings opens after closing the filter');
  const buttons=page.locator('#modelSeg button');assert.equal(await buttons.count(),4);
  const layouts=await buttons.evaluateAll(nodes=>nodes.map(n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n);return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,border:s.borderTopWidth,style:s.borderTopStyle};}));
  for(const x of layouts)assert(parseFloat(x.border)>0&&x.style!=='none','Each setting has a visible border');
  for(let i=0;i<layouts.length;i++)for(let j=i+1;j<layouts.length;j++)assert(layouts[i].right<layouts[j].left||layouts[j].right<layouts[i].left||layouts[i].bottom<layouts[j].top||layouts[j].bottom<layouts[i].top,'Settings have visible spacing');
  for(const model of ['anchored','meso','na','both']){await page.locator('#modelSeg [data-model="'+model+'"]').click();assert.equal(await page.locator('#modelSeg [data-model="'+model+'"]').getAttribute('aria-pressed'),'true');}
  await settings.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'requested-world-settings-'+profile.name+'.png'),animations:'disabled'});
  await page.locator('#mapSettingsClose').click();assert(!(await settings.evaluate(n=>n.open)),'Map settings closes through its control');await page.locator('#modeChart').click();assert(await page.locator('#river').isVisible(),'Explicit Timeline remains available');
  await page.locator('#modeMap').click();assert(await page.locator('#mapview').isVisible(),'Explicit return to map remains available');
  await page.goto(origin+'/timelines/adams-1881-chart.html',{waitUntil:'load'});
  assert(await page.locator('#progress').evaluate(n=>n.hidden),'Tile diagnostics hidden');assert(await page.locator('#mini').isVisible(),'Minimap retained');
  assert(await page.locator('#viewport').isVisible());assert(await page.locator('#zoom100').count());
  await page.screenshot({path:path.join(out,'requested-adams-'+profile.name+'.png'),animations:'disabled'});
  // Force a rejected fullscreen request so that genuine failure feedback is
  // still tested while normal tile diagnostics stay hidden.
  await page.evaluate(()=>{document.documentElement.requestFullscreen=()=>Promise.reject(new Error('test fullscreen rejection'));});
  await page.locator('#full').click();
  await page.waitForFunction(()=>!document.getElementById('progress').hidden);
  assert.equal(await page.locator('#progress').innerText(),'Fullscreen unavailable in this browser');
  results.push({profile:profile.name,initial,restored,settings:layouts,providerTiles:'not verified; external requests blocked'});
 }
 // The image coverage suite checks image/link attributes, but does not click
 // those links. Activate each corrected link and verify its actual landing.
 const catalog=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../art-gallery.json'),'utf8'));
 const destinations=[
  ['life','life-of-christ-journey-map.html','LifeTimeline',5,'/answers/jesus-christ-latter-day-saint-beliefs.html#nazareth-childhood'],
  ['life','life-of-christ-journey-map.html','LifeTimeline',7,'/art-gallery.html?picture=art-4f5759d8edad'],
  ['life','life-of-christ-journey-map.html','LifeTimeline',10,'/art-gallery.html?picture=art-3b1016debbad'],
  ['life','life-of-christ-journey-map.html','LifeTimeline',14,'/art-gallery.html?picture=art-838305f993f7'],
  ['history','latter-day-saint-church-history-timeline.html','HistoryTimeline',4,'/art-gallery.html?picture=art-6e45c602be15'],
  ['history','latter-day-saint-church-history-timeline.html','HistoryTimeline',42,'/jesus-christ/restoration-and-today.html#living-christ']
 ];
 const landings=[];await page.setViewportSize({width:1366,height:900});
 for(const [kind,route,api,index,target] of destinations){
  await page.goto(origin+'/timelines/'+route,{waitUntil:'load'});
  await page.waitForFunction(api=>window[api]&&window.TimelineImages,api);
  await page.evaluate(({api,index})=>window[api].select(index),{api,index});
  const figure=page.locator('[data-timeline-image="'+index+'"]');await figure.waitFor({state:'visible'});
  const link=figure.locator('a').first();assert.equal(await link.getAttribute('href'),target);
  await Promise.all([page.waitForURL(origin+target),link.click()]);
  if(target.startsWith('/art-gallery.html?')){
   const id=new URL(origin+target).searchParams.get('picture'),art=catalog.artworks.find(a=>a.id===id);assert(art&&art.occurrences.length);
   await page.waitForFunction(()=>document.getElementById('artGalleryDialog').open,{},{timeout:20000});
   const frame=page.locator('#artGalleryFrame');const actual=new URL(await frame.getAttribute('src'),origin);
   assert.equal(actual.pathname,art.occurrences[0].page);assert.equal(actual.searchParams.get('gallery-art'),art.occurrences[0].id);
   assert(await frame.isVisible(),'Gallery opened its owning study panel');
  }else{
   const anchor=new URL(origin+target).hash.slice(1);assert(await page.locator('#'+anchor).isVisible(),'Expected event section is visible');
  }
  const screenshot='requested-destination-'+kind+'-'+(index+1)+'.png';await page.screenshot({path:path.join(out,screenshot),animations:'disabled'});
  landings.push({kind,event:index+1,target,screenshot});
 }
 results.push({scope:'corrected_link_landings',landings});
 fs.writeFileSync(path.join(out,'requested-controls-report.json'),JSON.stringify(results,null,2)+'\n');return results;
};
