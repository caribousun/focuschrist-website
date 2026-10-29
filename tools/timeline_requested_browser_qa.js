/* Hosted rendered checks for the requested Timeline controls. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
module.exports=async function(page,origin,out){
 assert.equal(process.env.CI,'true','Hosted CI only');
 const results=[];let desktopReference;
 const geometry=target=>target.evaluate(()=>{
  const bounds=(selector,parent)=>{const n=document.querySelector(selector),r=n.getBoundingClientRect(),p=document.querySelector(parent).getBoundingClientRect(),s=getComputedStyle(n);return {x:r.x-p.x,y:r.y-p.y,width:r.width,height:r.height,appearance:[s.display,s.color,s.backgroundColor,s.backgroundImage,s.borderTopColor,s.borderTopWidth,s.borderTopStyle,s.borderRadius,s.fontFamily,s.fontSize,s.fontWeight,s.lineHeight,s.padding]};};
  return Object.fromEntries([['view','.view-switch','.workspace-toolbar'],['search','#q','.workspace-toolbar'],['filters','#workspaceFilterState','.workspace-toolbar'],['playback','.mapplayback','.maptoolband'],['play','#playBtn','.maptoolband'],['year','#yearInput','.maptoolband'],['time','#timeSeg','.maptoolband'],['speed','#speedSeg','.maptoolband'],['options','.map-options-row','.maptoolband']].map(([name,node,parent])=>[name,bounds(node,parent)]));
 });
 const compareGeometry=(actual,expected,label)=>{
  for(const key of Object.keys(expected)){
   for(const metric of ['x','y','width','height'])assert(Math.abs(actual[key][metric]-expected[key][metric])<1,label+': '+key+' '+metric);
   assert.deepEqual(actual[key].appearance,expected[key].appearance,label+': '+key+' appearance');
  }
 };
 // Render the exact Git predecessor in a temporary isolated copy. Its shared
 // local JS/CSS must also match the predecessor before comparing appearance.
 const base='4fb9e51deda2997d6974e80a5dce86a65167841c',route='timelines/world-and-scripture-timeline.html';
 const repo=path.resolve(__dirname,'..');
 assert.equal(execFileSync('git',['rev-parse',base],{cwd:repo,encoding:'utf8'}).trim(),base,'Exact predecessor commit is available');
 const baseHtml=execFileSync('git',['show',base+':'+route],{cwd:repo,maxBuffer:8*1024*1024});
 assert.equal(crypto.createHash('sha256').update(baseHtml).digest('hex'),'016e9896db70ff0a8a142503f289f2e0cbd2f4d96b73d667247dbb2a2370ceef','Exact predecessor World page');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'focus-world-predecessor-')),copy=path.join(dir,'world.html'),predecessor=await page.context().newPage();
 fs.writeFileSync(copy,baseHtml);
 try{
  await predecessor.setViewportSize({width:1366,height:900});
  await predecessor.route('**/timelines/world-and-scripture-timeline.html',route=>route.fulfill({path:copy,contentType:'text/html; charset=utf-8'}));
  await predecessor.goto(origin+'/'+route+'#viewer',{waitUntil:'load'});await predecessor.evaluate(()=>document.fonts.ready);
  const assets=await predecessor.evaluate(()=>[...document.querySelectorAll('script[src],link[rel="stylesheet"][href]')].map(n=>new URL(n.getAttribute('src')||n.getAttribute('href'),location.href)).filter(u=>u.origin===location.origin).map(u=>decodeURIComponent(u.pathname).replace(/^\//,'')));
  assert.deepEqual([...new Set(assets)].sort(),['header-scroll.js','site-search.css','site-search.js']);
  const dependencyHashes={};
  for(const asset of assets){const old=execFileSync('git',['show',base+':'+asset],{cwd:repo,maxBuffer:8*1024*1024});assert.deepEqual(fs.readFileSync(path.join(repo,asset)),old,'Predecessor shared asset drift: '+asset);dependencyHashes[asset]=crypto.createHash('sha256').update(old).digest('hex');}
  await predecessor.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  assert(await predecessor.locator('#mapview').isVisible());const predecessorGeometry=await geometry(predecessor);
  await predecessor.locator('.workspace-toolbar').scrollIntoViewIfNeeded();await predecessor.screenshot({path:path.join(out,'mobile-collapse-predecessor-desktop-toolbar-viewport.png'),fullPage:false,animations:'disabled'});
  await predecessor.locator('.maptoolband').scrollIntoViewIfNeeded();await predecessor.screenshot({path:path.join(out,'mobile-collapse-predecessor-desktop-playback-viewport.png'),fullPage:false,animations:'disabled'});
  desktopReference={predecessorGeometry,dependencyHashes};
 }finally{await predecessor.close();fs.rmSync(dir,{recursive:true,force:true});}
 for(const profile of [{name:'desktop',width:1366,height:900},{name:'phone',width:390,height:844}]){
  await page.setViewportSize({width:profile.width,height:profile.height});
  await page.goto(origin+'/timelines/world-and-scripture-timeline.html#viewer',{waitUntil:'load'});
  assert(await page.locator('#mapview').isVisible(),'Moment & Map opens first');
  assert(await page.locator('#modeMap').evaluate(n=>n.classList.contains('on')));
  const viewToggle=page.locator('#mobileViewToggle'),playToggle=page.locator('#mobilePlaybackToggle');
  const viewPanel=page.locator('#mobileViewControls'),playPanel=page.locator('#mobilePlaybackControls');
  if(profile.width<=900){
   assert(await viewToggle.isVisible()&&await playToggle.isVisible(),'Both mobile disclosure controls are visible');
   assert.equal(await viewToggle.getAttribute('aria-controls'),'mobileViewControls');assert.equal(await playToggle.getAttribute('aria-controls'),'mobilePlaybackControls');
   assert.equal(await viewToggle.getAttribute('aria-expanded'),'false');assert.equal(await playToggle.getAttribute('aria-expanded'),'false');
   assert(!(await viewPanel.isVisible())&&!(await playPanel.isVisible()),'Both mobile panels start compact');
   assert.match(await viewToggle.innerText(),/Moment & Map/);assert.match(await playToggle.innerText(),/Playback.*\d/);
   assert(await page.locator('.map-options-row').isVisible(),'Geography and map settings remain outside playback');
   await page.evaluate(()=>{if(document.activeElement instanceof HTMLElement)document.activeElement.blur();});
   let reachedView=false;
   for(let i=0;i<120;i++){await page.keyboard.press('Tab');if(await viewToggle.evaluate(n=>document.activeElement===n)){reachedView=true;break;}}
   assert(reachedView,'View disclosure is reachable by Tab');
   await page.keyboard.press('Tab');assert(await playToggle.evaluate(n=>document.activeElement===n),'Tab reaches playback after the collapsed view panel');
   await page.keyboard.press('Tab');assert(await page.locator('#frameBtn').evaluate(n=>document.activeElement===n),'Tab continues to map options');
   await page.locator('.workspace-toolbar').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'mobile-collapse-phone-closed-viewport.png'),fullPage:false,animations:'disabled'});
   await page.locator('.workspace-toolbar').screenshot({path:path.join(out,'mobile-collapse-view-closed.png'),animations:'disabled'});
   await page.locator('.maptoolband').scrollIntoViewIfNeeded();await page.locator('.maptoolband').screenshot({path:path.join(out,'mobile-collapse-playback-closed.png'),animations:'disabled'});
   await viewToggle.focus();await page.keyboard.press('Enter');assert.equal(await viewToggle.getAttribute('aria-expanded'),'true');assert(await viewPanel.isVisible());
   await page.locator('.workspace-toolbar').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'mobile-collapse-phone-view-open-viewport.png'),fullPage:false,animations:'disabled'});
   await viewToggle.focus();await page.keyboard.press('Space');assert(!(await viewPanel.isVisible()));
   await playToggle.focus();await page.keyboard.press('Enter');assert(await playPanel.isVisible());
   await page.locator('.maptoolband').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'mobile-collapse-phone-playback-open-viewport.png'),fullPage:false,animations:'disabled'});
   await playToggle.focus();await page.keyboard.press('Space');assert(!(await playPanel.isVisible()));
   await viewToggle.focus();await page.keyboard.press('Enter');assert(await viewPanel.isVisible());
   await page.locator('#q').fill('Egypt');await page.locator('#modeOverview').click();assert(await page.locator('#gwrap').isVisible());
   const mobileFilter=page.locator('#workspaceFilterState');await mobileFilter.click();await page.locator('#catChips [data-cat="bible"]').click();await mobileFilter.click();
   assert.equal(await page.locator('#catChips [data-cat="bible"]').getAttribute('aria-pressed'),'false');
   for(let i=0;i<2;i++){
    await viewToggle.focus();await page.keyboard.press('Space');assert(!(await viewPanel.isVisible()));assert(await viewToggle.evaluate(n=>document.activeElement===n));
    await viewToggle.focus();await page.keyboard.press('Enter');assert(await viewPanel.isVisible());
    assert(!(await playPanel.isVisible()),'View toggles leave playback collapsed');
    assert.equal(await page.locator('#q').inputValue(),'Egypt');assert(await page.locator('#modeOverview').evaluate(n=>n.classList.contains('on')));
    assert.equal(await page.locator('#catChips [data-cat="bible"]').getAttribute('aria-pressed'),'false');
   }
   await page.locator('#modeMap').click();assert(await page.locator('#mapview').isVisible());
   await playToggle.focus();await page.keyboard.press('Enter');assert.equal(await playToggle.getAttribute('aria-expanded'),'true');assert(await playPanel.isVisible());
   const originalYear=await page.locator('#yearInput').inputValue(),originalSpeed=await page.locator('#playSpeed').inputValue();
   const changedYear=originalYear==='-610'?'-620':'-610';assert.notEqual(changedYear,originalYear);
   await page.locator('#yearInput').fill(changedYear);await page.locator('#yearInput').dispatchEvent('change');await page.locator('#playSpeed').selectOption('2');
   for(let i=0;i<2;i++){
    await playToggle.focus();await page.keyboard.press('Space');assert(!(await playPanel.isVisible()));assert(await playToggle.evaluate(n=>document.activeElement===n));
    assert(await viewPanel.isVisible(),'Playback collapse leaves the view panel open');
    await playToggle.focus();await page.keyboard.press('Enter');assert(await playPanel.isVisible());
    assert.equal(await page.locator('#yearInput').inputValue(),changedYear);assert.equal(await page.locator('#playSpeed').inputValue(),'2');
    assert.equal(await page.locator('#q').inputValue(),'Egypt');assert.equal(await page.locator('#catChips [data-cat="bible"]').getAttribute('aria-pressed'),'false');assert(await page.locator('#modeMap').evaluate(n=>n.classList.contains('on')));
   }
   await viewToggle.focus();await page.keyboard.press('Space');assert(!(await viewPanel.isVisible())&&await playPanel.isVisible());
   await viewToggle.focus();await page.keyboard.press('Enter');assert(await viewPanel.isVisible()&&await playPanel.isVisible());
   assert.equal(await page.locator('#yearInput').inputValue(),changedYear);assert.equal(await page.locator('#q').inputValue(),'Egypt');assert.equal(await page.locator('#catChips [data-cat="bible"]').getAttribute('aria-pressed'),'false');assert(await page.locator('#modeMap').evaluate(n=>n.classList.contains('on')));
   await page.locator('#yearInput').fill(originalYear);await page.locator('#yearInput').dispatchEvent('change');await page.locator('#playSpeed').selectOption(originalSpeed);
   await page.locator('#q').fill('');await mobileFilter.click();await page.locator('#catChips [data-cat="bible"]').click();await mobileFilter.click();
   await page.locator('.workspace-toolbar').scrollIntoViewIfNeeded();await page.locator('.workspace-toolbar').screenshot({path:path.join(out,'mobile-collapse-view-open.png'),animations:'disabled'});
   await page.locator('.maptoolband').scrollIntoViewIfNeeded();await page.locator('.maptoolband').screenshot({path:path.join(out,'mobile-collapse-playback-open.png'),animations:'disabled'});
  }else{
   assert(!(await viewToggle.isVisible())&&!(await playToggle.isVisible()),'Desktop has no mobile toggles');
   assert(await viewPanel.isVisible()&&await playPanel.isVisible(),'Desktop controls remain visible');
   await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   const candidateGeometry=await geometry(page);compareGeometry(candidateGeometry,desktopReference.predecessorGeometry,'Predecessor versus candidate desktop');desktopReference.candidateGeometry=candidateGeometry;
   await page.locator('.workspace-toolbar').screenshot({path:path.join(out,'mobile-collapse-desktop-view-before.png'),animations:'disabled'});
   await page.locator('.workspace-toolbar').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'mobile-collapse-candidate-desktop-toolbar-viewport.png'),fullPage:false,animations:'disabled'});
   await page.locator('.maptoolband').scrollIntoViewIfNeeded();await page.locator('.maptoolband').screenshot({path:path.join(out,'mobile-collapse-desktop-playback-before.png'),animations:'disabled'});
   await page.screenshot({path:path.join(out,'mobile-collapse-candidate-desktop-playback-viewport.png'),fullPage:false,animations:'disabled'});
  }
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
  if(profile.width<=900){
   await filterSummary.click();await page.locator('#catChips [data-cat="bible"]').click();await filterSummary.click();
   await page.waitForFunction(()=>document.getElementById('workspaceFilterState').textContent.trim()==='All records · All regions');
   await viewToggle.click();assert(!(await viewPanel.isVisible()));
   await page.setViewportSize({width:1366,height:900});assert(await viewPanel.isVisible()&&!(await viewToggle.isVisible()),'Desktop resize restores controls');
   await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   const resized=await geometry(page);assert(desktopReference.candidateGeometry,'Desktop reference was captured');
   compareGeometry(resized,desktopReference.candidateGeometry,'Desktop after resize');
   fs.writeFileSync(path.join(out,'mobile-collapse-desktop-parity.json'),JSON.stringify({predecessor:base,predecessorSourceSha256:'016e9896db70ff0a8a142503f289f2e0cbd2f4d96b73d667247dbb2a2370ceef',dependencyHashes:desktopReference.dependencyHashes,predecessorGeometry:desktopReference.predecessorGeometry,candidateGeometry:desktopReference.candidateGeometry,candidateAfterResize:resized,limitations:['External map providers blocked; no owner acceptance.']},null,2)+'\n');
   await page.locator('.workspace-toolbar').screenshot({path:path.join(out,'mobile-collapse-desktop-view-after.png'),animations:'disabled'});
   await page.locator('.maptoolband').scrollIntoViewIfNeeded();await page.locator('.maptoolband').screenshot({path:path.join(out,'mobile-collapse-desktop-playback-after.png'),animations:'disabled'});
   await page.locator('#q').focus();await page.setViewportSize({width:profile.width,height:profile.height});
   await page.waitForFunction(()=>document.activeElement===document.getElementById('mobileViewToggle'));
   assert(!(await viewPanel.isVisible()),'Returning to mobile restores collapsed state');
  }
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
   const handle=await frame.elementHandle(),embedded=handle&&await handle.contentFrame(),source=art.occurrences[0];assert(embedded,'Owning study frame exists');
   await embedded.waitForFunction(id=>document.documentElement.dataset.galleryArtworkReady===id||!!document.documentElement.dataset.galleryArtworkError,source.id,{timeout:18000});
   const error=await embedded.evaluate(()=>document.documentElement.dataset.galleryArtworkError);assert(!error,'Owning artwork bridge reported an error: '+error);
   await embedded.evaluate(()=>document.fonts.ready);
   const selectors={hero:'#heroDetailDialog',artwork:'#artworkDetailDialog',topic:'#topicArtworkDetailDialog',missionary:'#missionaryDetailDialog',legacy:'#imageModal',full:'.fc-full-image-viewer'};
   const selector=selectors[source.kind];assert(selector,'Known native panel type');
   if(source.kind==='legacy'){
    const drawer=embedded.locator('[data-focuschrist-art-study-drawer]');
    if(!await drawer.evaluate(n=>n.classList.contains('open')))await embedded.locator('[data-focuschrist-art-study-button]').click();
   }
   const panel=embedded.locator(selector),picture=panel.locator('img').first();
   assert(await panel.isVisible(),'Owning panel is rendered');
   assert(await panel.evaluate(n=>n.open||n.classList.contains('active')),'Owning panel is open');
   await embedded.waitForFunction(selector=>{const img=document.querySelector(selector)?.querySelector('img');return !!(img&&img.complete&&img.naturalWidth>0);},selector,{timeout:18000});
   await picture.evaluate(img=>img.decode());
   assert(await picture.isVisible(),'Owning panel image is rendered');
   assert(await picture.evaluate(img=>{const r=img.getBoundingClientRect(),s=getComputedStyle(img);return s.visibility==='visible'&&s.display!=='none'&&Number(s.opacity)>0&&r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.left<innerWidth&&r.top<innerHeight;}),'Owning panel image intersects the frame viewport');
   assert.equal(new URL(await picture.getAttribute('src'),origin).pathname,art.fullImage,'Owning panel shows the requested artwork');
   await embedded.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  }else{
   const anchor=new URL(origin+target).hash.slice(1);assert(await page.locator('#'+anchor).isVisible(),'Expected event section is visible');
   await page.locator('#'+anchor).scrollIntoViewIfNeeded();await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   assert(await page.locator('#'+anchor).evaluate(n=>{const r=n.getBoundingClientRect();return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.left<innerWidth&&r.top<innerHeight;}),'Expected section intersects the viewport');
  }
  const screenshot='requested-destination-'+kind+'-'+(index+1)+'.png';await page.screenshot({path:path.join(out,screenshot),animations:'disabled'});
  landings.push({kind,event:index+1,target,screenshot});
 }
 results.push({scope:'corrected_link_landings',landings});
 fs.writeFileSync(path.join(out,'requested-controls-report.json'),JSON.stringify(results,null,2)+'\n');return results;
};
