/* Hosted Chromium only. Native phone pinch/drag and owner-device acceptance remain separate. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const W=50195,H=5347,TILE=1024;
const EXPECTED_CHART_SHA256='051fecab5376895220a808a722e940b800cb37d145e9098507004cf4ba6011ca';
const EXPECTED_LANDING_SHA256='fa3b12da544899f8935874508b9abe64b84b6fd2af1e5bfec8a368ce6a638578';
const ASSET_SET_SHA256='6092f3c930ebb6cae7c25b3f881fc93ef590642500e419b539124cacd89bca0f';
const CREDIT='Sebastian C. Adams, Synchronological Chart (1881). Chart image from Wikimedia Commons, courtesy of the David Rumsey Map Collection. The image is in the public domain.';
const COMMONS='https://commons.wikimedia.org/wiki/File:Adams_Synchronological_Chart,_1881.jpg';
const CHOICES=['latter-day-saint-church-history-timeline.html','willie-and-martin-handcart-map.html','life-of-christ-journey-map.html','world-and-scripture-timeline.html','adams-1881-chart.html'];
const PROFILES=[{name:'desktop',width:1280,height:900,touch:false},{name:'phone',width:390,height:844,touch:true},{name:'narrow-phone',width:320,height:568,touch:true},{name:'phone-landscape',width:844,height:390,touch:true}];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const near=(a,b,why,t=.08)=>assert(Math.abs(a-b)<=t,`${why}: ${a} != ${b}`);

function inspectAssets(root){
 const html=fs.readFileSync(path.join(root,'timelines/adams-1881-chart.html'),'utf8');
 assert.equal(sha(Buffer.from(html)),EXPECTED_CHART_SHA256,'Exact reviewed metadata-correct chart');
 assert.equal(sha(fs.readFileSync(path.join(root,'timeline.html'))),EXPECTED_LANDING_SHA256,'Exact reviewed Timeline landing');
 const matches=[...html.matchAll(/assets\["([0-9]+):([0-9]+):([0-9]+)"\]="(\/assets\/adams-chart\/[^"\s]+)"/g)];
 assert.equal(matches.length,331,'331 literal chart assets');
 const assets=new Map(),counts={};let total=0;
 for(const m of matches){
  const [level,col,row]=m.slice(1,4).map(Number),url=m[4],expected=`/assets/adams-chart/adams-${level}-${col}-${row}.jpg`;
  assert([1,4,16,64].includes(level));assert.equal(url,expected);assert(!assets.has(url),'duplicate tile');
  const file=path.join(root,url.slice(1)),s=fs.lstatSync(file);assert(s.isFile()&&!s.isSymbolicLink(),'regular tile');
  const bytes=fs.readFileSync(file),record={url,bytes:bytes.length,sha256:sha(bytes),width:Math.min(TILE,Math.ceil(W/level)-col*TILE),height:Math.min(TILE,Math.ceil(H/level)-row*TILE)};
  assert(record.width>0&&record.height>0);assets.set(url,record);counts[level]=(counts[level]||0)+1;total+=bytes.length;
 }
 assert.deepEqual(counts,{1:300,4:26,16:4,64:1});assert.equal(total,119541095);
 // Locale order is deliberately not used for the digest: Python/source manifest uses byte order.
 const ordered=[...assets.values()].sort((a,b)=>a.url<b.url?-1:a.url>b.url?1:0).map(r=>`${r.url.slice(1)}\0${r.bytes}\0${r.sha256}\n`).join('');
 assert.equal(sha(Buffer.from(ordered)),ASSET_SET_SHA256,'all 331 exact owner-supplied JPEG bytes');
 return {assets,sourceSHA256:sha(Buffer.from(html)),landingSHA256:sha(fs.readFileSync(path.join(root,'timeline.html'))),total};
}

// Reads rendered tile coordinates, not the app's internal variables or setter functions.
function readView(){
 const vp=document.getElementById('viewport'),tiles=[...document.querySelectorAll('#tiles img.tile')],first=tiles[0];
 if(!vp||!first)return null;
 const m=new URL(first.src).pathname.match(/adams-(\d+)-(\d+)-(\d+)\.jpg$/);if(!m)return null;
 const [level,col,row]=m.slice(1).map(Number),z=parseFloat(first.style.width)/Math.min(1024*level,50195-col*1024*level);
 const rect=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
 return {z,x:parseFloat(first.style.left)-col*1024*level*z,y:parseFloat(first.style.top)-row*1024*level*z,level,layout:{width:vp.clientWidth,height:vp.clientHeight},viewport:rect(vp),toolbar:rect(document.getElementById('toolbar')),fit:document.getElementById('fit').getAttribute('aria-pressed'),fill:document.getElementById('fillScreen').getAttribute('aria-pressed'),tiles:tiles.map(n=>({url:new URL(n.src).pathname,complete:n.complete,width:n.naturalWidth,height:n.naturalHeight})),documentWidth:document.documentElement.scrollWidth,innerWidth,innerHeight};
}
async function settle(page){
 // Input handlers queue draw(); it may replace an already-loaded old tile set.
 // Observe the current complete set and geometry across three stable frames,
 // after queued draw/layout work. Never mark a new zero-width tile as ready.
 await page.waitForFunction(()=>new Promise(resolve=>{
  const deadline=performance.now()+7500;let previous='',stable=0;
  const sample=()=>{
   const a=[...document.querySelectorAll('#tiles img.tile')],o=document.getElementById('overview'),v=document.getElementById('viewport'),bar=document.getElementById('toolbar');
   const ready=a.length&&a.every(n=>n.complete&&n.naturalWidth>0&&n.naturalHeight>0)&&o&&o.complete&&o.naturalWidth>0;
   const key=ready?JSON.stringify([v.clientWidth,v.clientHeight,v.style.top,bar.getBoundingClientRect().height,...a.map(n=>[n.src,n.style.left,n.style.top,n.style.width,n.style.height,n.naturalWidth,n.naturalHeight])]):'';
   stable=key&&key===previous?stable+1:0;previous=key;
   if(stable>=3){resolve(true);return;}if(performance.now()>=deadline){resolve(false);return;}requestAnimationFrame(sample);
  };requestAnimationFrame(()=>requestAnimationFrame(sample));
 }),null,{timeout:8000});
 return page.evaluate(readView);
}
// Viewer fitCoords/clamp use integer client dimensions; keep the fractional
// bounding rect separately for actual placement, hit targets and screenshots.
function checkFit(s){near(s.z,Math.min(s.layout.width/W,s.layout.height/H),'full-chart contain zoom',1e-8);near(s.x,(s.layout.width-W*s.z)/2,'fit x');near(s.y,(s.layout.height-H*s.z)/2,'fit y');assert.equal(s.fit,'true');}
function sameView(a,b,label){near(a.z,b.z,label+' zoom',1e-8);near(a.x,b.x,label+' x');near(a.y,b.y,label+' y');}

module.exports=async function adamsChartQA(existingPage,origin,parentOut){
 assert.equal(process.env.CI,'true','Hosted CI only; do not launch locally');
 assert(/^http:\/\/127\.0\.0\.1:\d+$/.test(origin),'Reuse only the existing Timeline QA server');
 const root=path.resolve(__dirname,'..'),out=path.join(parentOut,'adams');
 assert(!fs.existsSync(out),'Fresh Adams evidence directory required');fs.mkdirSync(out);
 const fixture=inspectAssets(root),browser=existingPage.context().browser();assert(browser);
 const results=[],network=[],blocked=[],active=new Set();let outputBytes=0,shots=0,tileBytes=0,requestCount=0,timedOut=false;
 const timer=setTimeout(()=>{timedOut=true;for(const c of active)c.close().catch(()=>{});},240000);
 const save=async(page,name)=>{
  assert(shots<24,'Screenshot count bound');
  const data=await page.screenshot({type:'jpeg',quality:80,fullPage:false,animations:'disabled',timeout:8000});
  assert(data.length<=1024*1024,'Single screenshot exceeds 1 MiB');assert(outputBytes+data.length<=23*1024*1024,'Screenshot budget exceeded');
  fs.writeFileSync(path.join(out,name+'.jpg'),data,{flag:'wx'});outputBytes+=data.length;shots++;
  return {file:name+'.jpg',bytes:data.length,sha256:sha(data)};
 };
 try{
  for(const profile of PROFILES){
   if(timedOut)break;
   const record={profile,pass:false,states:[],screenshots:[],limitations:profile.touch?['Chromium mobile/touch emulation; tap controls tested, not native touch drag/pinch or a physical phone.']:[]};
   results.push(record);let context,page;const issues=[],pending=[];
   try{
    context=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.touch,hasTouch:profile.touch,deviceScaleFactor:1,reducedMotion:'reduce',serviceWorkers:'block'});active.add(context);
    await context.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin!==origin){if(blocked.length<200)blocked.push({profile:profile.name,url:u.origin+u.pathname});return route.abort();}if(++requestCount>2000){issues.push('Request bound exceeded');return route.abort();}return route.continue();});
    page=await context.newPage();page.setDefaultTimeout(8000);page.setDefaultNavigationTimeout(12000);
    page.on('pageerror',e=>issues.push(String(e).slice(0,1000)));
    page.on('requestfailed',req=>{if(new URL(req.url()).origin===origin)issues.push(`Local request failed: ${new URL(req.url()).pathname} ${req.failure()?.errorText}`);});
    page.on('response',res=>{
     const url=new URL(res.url());if(url.origin!==origin)return;
     if(res.status()>=400)issues.push(`HTTP ${res.status()} ${url.pathname}`);
     if(!url.pathname.startsWith('/assets/adams-chart/'))return;
     pending.push((async()=>{const expected=fixture.assets.get(url.pathname);assert(expected,'Unexpected chart asset');assert.equal(res.status(),200);assert((res.headers()['content-type']||'').includes('image/jpeg'));
      const bytes=await res.body();tileBytes+=bytes.length;assert(tileBytes<=256*1024*1024,'Tile response byte budget');assert.equal(bytes.length,expected.bytes);assert.equal(sha(bytes),expected.sha256);
      network.push({profile:profile.name,path:url.pathname,status:res.status(),bytes:bytes.length,sha256:expected.sha256});
     })().catch(e=>issues.push(String(e).slice(0,1500))));
    });
    const act=async id=>{const n=page.locator(id);if(profile.touch)await n.tap();else await n.click();};
    const state=async label=>{const s=await settle(page);assert(s,label+' rendered tiles');near(s.viewport.y,s.toolbar.bottom,label+' viewport below toolbar',1);for(const tile of s.tiles){assert(tile.complete,label+' current tile complete');const e=fixture.assets.get(tile.url);assert(e,'Known tile URL');assert.equal(tile.width,e.width);assert.equal(tile.height,e.height);}await Promise.all(pending);assert.deepEqual(issues,[],label+' errors');record.states.push({label,...s});return s;};
    const capture=async label=>record.screenshots.push(await save(page,profile.name+'-'+label));
    const response=await page.goto(origin+'/timeline.html',{waitUntil:'load'});assert.equal(response.status(),200);
    const choices=page.locator('#choose-timeline .fc-timeline-choices a');assert.equal(await choices.count(),5);
    assert.deepEqual(await choices.evaluateAll(a=>a.map(n=>n.getAttribute('href'))),CHOICES.map(n=>'timelines/'+n));
    const doorway=page.locator('#choose-timeline a[href="timelines/adams-1881-chart.html"]');await doorway.scrollIntoViewIfNeeded();await capture('landing');
    if(profile.touch)await doorway.tap();else await doorway.click();await page.waitForURL(origin+'/timelines/adams-1881-chart.html');
    assert.equal(await page.locator('.fc-adams-back').getAttribute('href'),'../timeline.html#choose-timeline');
    assert.equal((await page.locator('.fc-adams-credit').innerText()).replace(/\s+/g,' ').trim(),CREDIT);
    assert.equal(await page.locator('.fc-adams-credit a').getAttribute('href'),COMMONS);
    assert(!/user-scalable\s*=\s*no|maximum-scale\s*=\s*1(?:,|$)/i.test(await page.locator('meta[name="viewport"]').getAttribute('content')),'Browser zoom not locked');
    assert.equal(await page.locator('iframe').count(),0);
    let s=await state('initial-fit');checkFit(s);
    const initialRequests=network.filter(n=>n.profile===profile.name).length;assert(initialRequests<=6,'Initial view must not download all 331 tiles');
    record.initialTileResponses=initialRequests;
    // Check actual control boxes, not only hidden document overflow.
    const geometry=await page.evaluate(()=>{const ids=['fit','fillScreen','full','toggleMini','out','slider','in','hideNav','fastLeft','sectionLeft','left','up','down','right','sectionRight','fastRight','homeBtn','zoom100'];return ids.map(id=>{const n=document.getElementById(id),r=n.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2),cs=getComputedStyle(n);return {id,x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,visible:cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity)!==0,hit:!!hit&&(n===hit||n.contains(hit))};});});
    record.geometry=geometry;await capture('fit');
    const integration=await page.evaluate(()=>{
     const rect=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
     const bar=document.getElementById('toolbar'),cs=getComputedStyle(bar);
     return {strip:rect(bar.querySelector('.fc-adams-strip')),titleRow:rect(bar.querySelector('.toprow')),controls:rect(bar.querySelector('.controls')),innerWidth:bar.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight),overlays:['navDock','mini','progress'].map(id=>{const n=document.getElementById(id);return {id,...rect(n),display:getComputedStyle(n).display};})};
    });record.integration=integration;
    if(profile.width>=900){near(integration.strip.width,integration.innerWidth,'Added strip full-width row',1);assert(integration.strip.bottom<=Math.min(integration.titleRow.y,integration.controls.y)+1,'Added strip must be above original title/controls');}
    const chart={x:s.viewport.x+s.x,y:s.viewport.y+s.y,right:s.viewport.x+s.x+W*s.z,bottom:s.viewport.y+s.y+H*s.z};
    record.initialFitOverlayOverlap=integration.overlays.map(o=>({id:o.id,area:o.display==='none'?0:Math.max(0,Math.min(o.right,chart.right)-Math.max(o.x,chart.x))*Math.max(0,Math.min(o.bottom,chart.bottom)-Math.max(o.y,chart.y))})).filter(o=>o.area>0);
    if(record.initialFitOverlayOverlap.length)record.limitations.push('Initial full-chart fit intersects existing dock/map/status overlays; default-view visual acceptance remains separate. Existing hide controls are tested, not redesigned.');
    assert(s.viewport.height>0&&s.viewport.width===profile.width,'Nonempty viewport at configured width');near(s.viewport.y,s.toolbar.bottom,'Viewport below toolbar',1);
    assert(s.documentWidth<=s.innerWidth+1,'No document horizontal overflow');
    for(const g of geometry)assert(g.visible&&g.width>0&&g.height>0&&g.x>=-1&&g.y>=-1&&g.right<=profile.width+1&&g.bottom<=profile.height+1&&g.hit,`Unreachable/clipped control ${JSON.stringify(g)}`);
    await act('#zoom100');s=await state('one-to-one');near(s.z,1,'1:1 scale',1e-8);await capture('one-to-one');
    let before=s;await act('#right');s=await state('right-tap');assert(s.x<before.x-1,'Right control actually pans');
    before=s;await act('#left');s=await state('left-tap');assert(s.x>before.x+1,'Left control actually pans');
    before=s;await act('#down');s=await state('down-tap');assert(s.y<before.y-1,'Down control actually pans');
    before=s;await act('#up');s=await state('up-tap');assert(s.y>before.y+1,'Up control actually pans');
    before=s;await act('#sectionRight');s=await state('next-section');near(s.x,Math.max(s.layout.width-W*s.z,before.x-s.layout.width*.85),'Section step');
    await act('#fastLeft');s=await state('start');near(s.x,0,'Start endpoint');
    await act('#fastRight');s=await state('end');near(s.x,s.layout.width-W*s.z,'End endpoint');await capture('end');
    await act('#homeBtn');s=await state('reset-fit');checkFit(s);
    before=s;await act('#in');s=await state('zoom-in');near(s.z,before.z*1.6,'Zoom in scale',1e-8);
    await act('#out');s=await state('zoom-out');near(s.z,before.z,'Zoom out inverse',1e-8);
    await act('#zoom100');before=await state('saved-view');await act('#fit');s=await state('full-view');checkFit(s);
    await act('#fit');s=await state('exit-full-view');sameView(s,before,'Full View restore');
    await act('#fillScreen');s=await state('fill-screen');assert.equal(s.fill,'true');near(s.z,Math.max(s.layout.width/W,s.layout.height/H),'Cover zoom',1e-8);
    await act('#fillScreen');s=await state('exit-fill-screen');assert.equal(s.fill,'false');sameView(s,before,'Fill Screen restore');
    if(!profile.touch){
     const box=s.viewport,x=box.x+box.width*.5,y=box.y+box.height*.4;
     await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+80,y+35,{steps:6});await page.mouse.up();s=await state('mouse-drag');near(s.x,before.x+80,'Mouse pan x',1);near(s.y,before.y+35,'Mouse pan y',1);
     before=s;await page.mouse.wheel(0,-120);s=await state('wheel-zoom');assert(s.z>before.z,'Wheel zoom changes scale');
     await page.locator('#viewport').focus();before=s;await page.keyboard.press('ArrowRight');s=await state('keyboard-pan');assert(s.x<before.x-1,'Keyboard pan');
     await page.keyboard.press('f');s=await state('keyboard-full-view');checkFit(s);await page.keyboard.press('Escape');s=await state('keyboard-exit');sameView(s,record.states.at(-3),'Escape restores saved view');
    }
    await act('#hideNav');assert.equal(await page.locator('#navDock').isVisible(),false);assert(await page.locator('#showNav').isVisible());await capture('controls-hidden');
    await act('#showNav');assert(await page.locator('#navDock').isVisible());assert.equal(await page.locator('#showNav').isVisible(),false);
    await act('#toggleMini');assert.equal(await page.locator('#mini').isVisible(),false);await act('#toggleMini');assert(await page.locator('#mini').isVisible());
    await act('#homeBtn');s=await state('final-reset');checkFit(s);
    if(profile.touch&&profile.width>profile.height){
     // Inspect the unchanged owner's existing uncluttered-reading controls on a
     // short landscape screen; do not imply the default overlaid fit is clear.
     await act('#hideNav');await act('#toggleMini');
     assert.equal(await page.locator('#navDock').isVisible(),false);assert.equal(await page.locator('#mini').isVisible(),false);
     s=await state('landscape-clear-fit');checkFit(s);await capture('landscape-clear-fit');
     await act('#toggleMini');await act('#showNav');
     assert(await page.locator('#navDock').isVisible());assert(await page.locator('#mini').isVisible());
    }
    if(profile.touch)await page.locator('.fc-adams-back').tap();else await page.locator('.fc-adams-back').click();
    await page.waitForURL(origin+'/timeline.html#choose-timeline');assert(await page.locator('#choose-timeline').isVisible());
    await page.goBack({waitUntil:'load'});await page.waitForURL(origin+'/timelines/adams-1881-chart.html');checkFit(await state('history-back-viewer'));
    await page.reload({waitUntil:'load'});checkFit(await state('reload-viewer'));
    await Promise.all(pending);assert.deepEqual(issues,[]);record.pass=true;
   }catch(e){record.error=String(e).slice(0,3000);record.issues=issues.slice(0,40);if(page&&!page.isClosed())try{record.screenshots.push(await save(page,profile.name+'-failure'));}catch(c){record.captureError=String(c).slice(0,500);}}
   finally{if(context){await context.close().catch(()=>{});active.delete(context);}await Promise.all(pending);if(issues.length){record.pass=false;record.issues=issues.slice(0,40);record.error=record.error||'Network/page errors during final cleanup';}}
  }
 }finally{
  clearTimeout(timer);for(const c of active)await c.close().catch(()=>{});
  const report={sourceSHA256:fixture.sourceSHA256,landingSHA256:fixture.landingSHA256,assetSetSHA256:ASSET_SET_SHA256,assetCount:331,assetBytes:fixture.total,timedOut,results,network,blocked,requestCount,tileResponseBytes:tileBytes,screenshots:shots,screenshotBytes:outputBytes,limits:['Hosted Chromium emulation, not deployed or physical-device acceptance.','No native touch drag/pinch, browser chrome fullscreen, accessibility certification or enlarged-text result claimed.','No external providers fetched; every observed chart response must be exact same-origin owner-supplied JPEG bytes.']};
  const bytes=Buffer.from(JSON.stringify(report,null,2)+'\n');assert(bytes.length<=1024*1024,'Report exceeds 1 MiB');assert(outputBytes+bytes.length<=24*1024*1024,'Adams evidence exceeds 24 MiB');fs.writeFileSync(path.join(out,'report.json'),bytes,{flag:'wx'});
 }
 assert(!timedOut,'Adams suite exceeded 240-second bound');assert.equal(results.length,4);assert(results.every(r=>r.pass),'Every Adams profile must pass: '+JSON.stringify(results.filter(r=>!r.pass).map(r=>({profile:r.profile.name,error:r.error}))));
 return {profiles:results.map(r=>r.profile.name),assetCount:331,assetSetSHA256:ASSET_SET_SHA256,screenshots:shots,evidence:'adams/report.json',nativePhoneGestures:'not tested'};
};
