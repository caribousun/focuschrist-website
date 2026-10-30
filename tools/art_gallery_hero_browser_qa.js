/* Bounded hosted gallery-opening evidence. This is not release acceptance. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts','gallery-hero');
const predecessor='c131e8254ec1b0a022bc8ab8cea834f8110e3f03';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function predecessorBytes(name){
 try{return execFileSync('git',['show',predecessor+':'+name],{cwd:root,maxBuffer:16*1024*1024});}
 catch(_){throw Error('Unable to read bounded predecessor file: '+name);}
}
const publicFiles=['art-gallery.html','art-gallery.css','art-gallery.js','art-gallery.json','art.html','answers/what-happens-after-death.html','site-header.css','site-system.css','site-common.js','site-search.css','site-search.js','study-navigation.css','footer-navigation.css','study-journey.js','unified-opening.css','unified-opening.js','art-gallery-bridge.js','scripture-library.js','scripture-reader.js','scripture-reader.css','header-scroll.js','answer-styles.css','connected-study.css','full-image-viewer.css','full-image-viewer.js','artwork-details.css','hero-details.css','hero-image-source.js','hero-details.js','artwork-actions.css','resource-cards.css','answer-navigation.css','topic-study-pages.css','topic-art.css','topic-artwork-details.css','topic-artwork-details.js','topic-heroes.css','complete-card-rows.css','answer-opening.css','assets/heroes/art.webp','assets/heroes/mobile-scene/art-20260920.webp','assets/page-art/life-after-death/nephi-children-1536.webp'];
const shared=publicFiles.filter(name=>!['art-gallery.html','art-gallery.css'].includes(name));
const allowed=new Set(publicFiles.map(name=>'/'+name));
function safeReadAt(base,permitted,name){
 const parts=name.split('/'),file=path.resolve(base,name);
 if(!permitted.has('/'+name)||!file.startsWith(base+path.sep)||parts.some(part=>!part||part.startsWith('.')||part==='..'))throw Error('Disallowed diagnostic file');
 let current=base;for(const part of parts){current=path.join(current,part);if(fs.lstatSync(current).isSymbolicLink())throw Error('Symlink in diagnostic file');}
 if(!fs.realpathSync(file).startsWith(base+path.sep))throw Error('Diagnostic file outside checkout');
 return fs.readFileSync(file);
}
function safeRead(name){return safeReadAt(root,allowed,name);}
function assertHosted(env){
 assert.equal(env.GITHUB_ACTIONS,'true','GitHub Actions diagnostic only');assert.equal(env.GITHUB_EVENT_NAME,'pull_request');assert.equal(env.GITHUB_HEAD_REF,'albert/art-gallery-hero-20261030');assert(/^\d+$/.test(env.GITHUB_RUN_ID||''));
}
const catalog=JSON.parse(safeRead('art-gallery.json'));
for(const art of catalog.artworks){
 const p=art.thumbnail;
 if(typeof p==='string'&&/^\/(?:assets|art)\/[a-zA-Z0-9_./% -]+\.(?:webp|png|jpe?g)$/i.test(p)&&!p.split('/').some(part=>part==='..'||part.startsWith('.')))allowed.add(decodeURIComponent(p));
}
assert.equal(catalog.artworks[0].id,'art-993a9d736f42');assert.equal(catalog.artworks[0].occurrences[0].page,'/answers/what-happens-after-death.html');
const old={};
for(const [name,expected] of [['art-gallery.html','67e419a67ab8062e5a4ae2bfb397608a495e6ff94af02bdd4d9fd5e6a8d622a2'],['art-gallery.css','f9bebefb1b4a70a73efdbef6344b40973394521caa5682660a472256530d151a']]){
 const bytes=predecessorBytes(name);assert.equal(sha(bytes),expected,'Exact predecessor bytes required');old['/'+name]=bytes;
}
for(const name of shared){
 const bytes=predecessorBytes(name);assert.equal(sha(safeRead(name)),sha(bytes),'Shared predecessor dependency changed: '+name);
}
function server(baseline){
 return http.createServer((req,res)=>{
  try{
   const u=new URL(req.url,'http://localhost'),pathname=decodeURIComponent(u.pathname),parts=pathname.split('/').filter(Boolean),file=path.resolve(root,'.'+pathname);
   if(!['GET','HEAD'].includes(req.method)||!allowed.has(pathname)||!file.startsWith(root+path.sep)||parts.some(part=>part.startsWith('.')||part==='..'))return res.writeHead(403).end();
   const respond=(e,data)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'application/octet-stream'}).end(data);
   if(baseline&&old[u.pathname])return respond(null,old[u.pathname]);
   return respond(null,safeRead(pathname.slice(1)));
  }catch(_){res.writeHead(400).end();}
 });
}
async function listen(s){await new Promise(resolve=>s.listen(0,'127.0.0.1',resolve));return 'http://127.0.0.1:'+s.address().port;}
async function layout(page){
 return page.evaluate(()=>{
  const rect=el=>{if(!el)return null;const r=el.getBoundingClientRect(),s=getComputedStyle(el);if(!r.width||!r.height||s.display==='none'||s.visibility==='hidden')return null;return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom};};
  const cue=[...document.querySelectorAll('.fc-mobile-scroll-cue,.fc-unified-continue,.fc-scroll-cue,.fc-gallery-desktop-continue')].find(el=>rect(el));
  const hero=document.querySelector('.fc-gallery-hero');
  return {intro:rect(document.querySelector('.fc-gallery-intro')),title:rect(document.querySelector('.fc-gallery-intro h1')),cue:rect(cue),cueHref:cue?.getAttribute('href')||null,hero:rect(hero),heroImage:hero?getComputedStyle(hero).backgroundImage:null,clientWidth:document.documentElement.clientWidth,overflow:document.documentElement.scrollWidth>innerWidth+1};
 });
}
async function run(){
 assertHosted(process.env);fs.mkdirSync(out,{recursive:true});
 const report={scope:'Diagnostic only; not visual or release approval. Enlarged text uses CSS root font size, not native browser zoom. Ordinary cross-origin requests and WebSockets are blocked.',predecessor,checkout:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),htmlSha256:sha(safeRead('art-gallery.html')),cssSha256:sha(safeRead('art-gallery.css')),profiles:[],errors:[]};
 try{assert.equal(report.htmlSha256,'7af78f9aceb3cf9fe8de572336bf8fae3c826ce798bc2b8b5b3bc1aacbf4a586');assert.equal(report.cssSha256,'71e37a6611ec000184632a0536984bfa617a08b3cef61e6f6baa52a6d658f808');}
 catch(error){report.errors.push('Candidate source hash differs');fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');throw error;}
 const oldServer=server(true),currentServer=server(false);let browser,baseline,candidate;
 try{
  baseline=await listen(oldServer);candidate=await listen(currentServer);
  browser=await chromium.launch({headless:true});
  for(const profile of [{name:'desktop',width:1366,height:900,scale:100},{name:'phone',width:390,height:844,scale:100},{name:'narrow',width:320,height:740,scale:100},{name:'phone-enlarged',width:390,height:844,scale:200}]){
   const context=await browser.newContext({viewport:{width:profile.width,height:profile.height},reducedMotion:'reduce',serviceWorkers:'block'});
   await context.route('**/*',route=>{const u=new URL(route.request().url());return (u.origin===baseline||u.origin===candidate)?route.continue():route.abort('blockedbyclient');});
   await context.routeWebSocket('**/*',socket=>socket.close());
   const before=await context.newPage(),after=await context.newPage(),pageErrors=[];after.on('pageerror',e=>pageErrors.push(String(e)));
   try{
    for(const [page,origin] of [[before,baseline],[after,candidate]]){
     await page.goto(origin+'/art-gallery.html',{waitUntil:'domcontentloaded'});
     await page.evaluate(scale=>{document.documentElement.style.fontSize=scale+'%';},profile.scale);
     await page.evaluate(()=>document.fonts.ready);await page.waitForSelector('[data-gallery-card]');
     if(profile.width<=700)await page.waitForSelector('.fc-mobile-scroll-cue',{state:'visible'});
     await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    }
    const original=await layout(before),current=await layout(after);const problems=[];
    if(profile.width<=700){
     for(const field of ['x','y','width','height'])if(Math.abs(original.intro[field]-current.intro[field])>1)problems.push('Phone intro geometry changed: '+field);
     if(!original.cue||!current.cue)problems.push('Phone baseline or candidate Continue missing');
     else {for(const field of ['x','y','width','height'])if(Math.abs(original.cue[field]-current.cue[field])>1)problems.push('Phone Continue geometry changed: '+field);if(original.cueHref!==current.cueHref)problems.push('Phone Continue target changed');}
    }else{
     if(!current.cue||current.cueHref!=='#fc-opening-next')problems.push('Desktop Continue missing or target changed');
     else {
      if(Math.abs(current.cue.bottom-(profile.height-20))>1)problems.push('Desktop Continue vertical baseline differs');
      if(Math.abs(current.cue.x+current.cue.width/2-current.clientWidth/2)>1)problems.push('Desktop Continue horizontal center differs');
     }
     if(!current.hero||!current.title||Math.abs(current.hero.height-current.hero.width*724/2172)>1||current.title.y<current.hero.bottom-1)problems.push('Desktop image-first composition differs');
    }
    if(current.overflow)problems.push('Horizontal overflow');
    if(!current.hero||!current.heroImage?.includes(profile.width<=700?'mobile-scene/art-20260920.webp':'assets/heroes/art.webp'))problems.push('Expected hero artwork missing');
    const imagePath=profile.width<=700?'/assets/heroes/mobile-scene/art-20260920.webp':'/assets/heroes/art.webp';
    await after.evaluate(async src=>{const image=new Image();image.src=src;await image.decode();if(!image.naturalWidth)throw Error('Artwork not decoded');},imagePath);
    const beforeImages=await before.evaluate(async()=>{
     const intro=document.querySelector('.fc-gallery-intro');
     if(getComputedStyle(intro).backgroundImage!=='none'||getComputedStyle(intro,'::before').backgroundImage!=='none')throw Error('Baseline intro has an unbound background image');
     const visible=[...document.images].filter(img=>{const r=img.getBoundingClientRect();return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.left<innerWidth&&r.top<innerHeight;});
     await Promise.all(visible.map(img=>img.decode()));
     return [...new Set(visible.map(img=>new URL(img.currentSrc||img.src).pathname))];
    });
    for(const urlPath of beforeImages){const name=decodeURIComponent(urlPath).replace(/^\//,'');const current=safeRead(name),prior=predecessorBytes(name);assert.equal(sha(current),sha(prior),'Visible baseline image changed: '+name);}
    await before.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    await after.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    await before.screenshot({path:path.join(out,profile.name+'-before.png'),animations:'disabled'});
    await after.screenshot({path:path.join(out,profile.name+'-candidate.png'),animations:'disabled'});
    const cue=after.locator(profile.width<=700?'.fc-mobile-scroll-cue':'.fc-gallery-desktop-continue');await cue.click();
    await after.waitForFunction(()=>{const el=document.getElementById('fc-opening-next'),r=el.getBoundingClientRect(),nav=document.querySelector('.nav').getBoundingClientRect();return location.hash==='#fc-opening-next'&&document.activeElement===el&&r.top>=nav.bottom-1&&r.top<innerHeight-1&&r.bottom>nav.bottom;});
    const navigation=await after.evaluate(async()=>{const el=document.getElementById('fc-opening-next'),first=el.getBoundingClientRect().top;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const target=el.getBoundingClientRect(),nav=document.querySelector('.nav').getBoundingClientRect();return {targetTop:target.top,headerBottom:nav.bottom,scrollY:scrollY,settled:Math.abs(first-target.top)<=1,hash:location.hash,focused:document.activeElement===el};});
    if(!navigation.settled||navigation.hash!=='#fc-opening-next'||!navigation.focused||navigation.targetTop<navigation.headerBottom-1||navigation.targetTop>=profile.height-1)problems.push('Continue target did not settle visibly below the header');
    await after.screenshot({path:path.join(out,profile.name+'-continue.png'),animations:'disabled'});
    // Start the keyboard traversal in a fresh document; Continue intentionally
    // focused a later element and the gallery contains hundreds of links.
    await after.goto(candidate+'/art-gallery.html',{waitUntil:'domcontentloaded'});
    await after.evaluate(scale=>{document.documentElement.style.fontSize=scale+'%';},profile.scale);
    await after.waitForSelector('[data-gallery-card]');await after.evaluate(()=>document.fonts.ready);
    await after.evaluate(async src=>{const image=new Image();image.src=src;await image.decode();},imagePath);
    await after.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    const hero=after.locator('.fc-gallery-hero');
    let focused=false;for(let i=0;i<80&&!focused;i++){await after.keyboard.press('Tab');focused=await hero.evaluate(el=>document.activeElement===el);}
    if(!focused)throw Error('Hero not reachable by keyboard Tab sequence');
    if(!await hero.evaluate(el=>el.matches(':focus-visible')))problems.push('Hero keyboard focus outline state missing');
    await after.screenshot({path:path.join(out,profile.name+'-focus.png'),animations:'disabled'});
    await after.keyboard.press('Enter');await after.waitForURL('**/art.html');
    await after.goto(candidate+'/art-gallery.html',{waitUntil:'domcontentloaded'});await after.waitForSelector('[data-gallery-card]');
    const search=after.locator('#artGallerySearch'),all=await after.locator('[data-gallery-card]:visible').count();await search.fill('Jesus');
    await after.waitForFunction(()=>{const cards=[...document.querySelectorAll('[data-gallery-card]')],shown=cards.filter(c=>!c.hidden);return shown.length>0&&shown.length<cards.length&&shown.every(c=>c.dataset.search.includes('jesus'));});
    const filtered=await after.locator('[data-gallery-card]:visible').count();if(!(filtered>0&&filtered<all))problems.push('Search did not filter cards');
    await after.locator('#artGalleryReset').click();if(await search.inputValue()!==''||await after.locator('[data-gallery-card]:visible').count()!==all)problems.push('Filter reset failed');
    await after.locator('[data-gallery-card] .fc-gallery-picture').first().click();
    await after.locator('#artGalleryDialog[open]').waitFor({timeout:18000});
    if(!await after.locator('#artGalleryDialog').evaluate(el=>el.open))problems.push('Artwork viewer did not open');
    const frame=await after.locator('#artGalleryFrame').elementHandle().then(el=>el.contentFrame());
    if(!frame)problems.push('Artwork viewer frame unavailable');
    else {await frame.waitForFunction(()=>document.documentElement.dataset.galleryArtworkReady==='source-bbc2a6bdfa53',null,{timeout:18000});await frame.waitForFunction(()=>{const image=document.querySelector('#topicArtworkDetailDialog img');return !!(image&&image.complete&&image.naturalWidth>0);},null,{timeout:18000});}
    if(pageErrors.length)problems.push('Uncaught page errors');
    report.profiles.push({profile,original,current,navigation,pageErrors,problems});report.errors.push(...problems.map(message=>profile.name+': '+message));
   }catch(error){report.errors.push(profile.name+': '+String(error));try{await before.screenshot({path:path.join(out,profile.name+'-before-failure.png')});await after.screenshot({path:path.join(out,profile.name+'-failure.png')});}catch(_){}}
   finally{await context.close();}
  }
 }finally{
  if(browser)await browser.close();await Promise.all([oldServer,currentServer].filter(s=>s.listening).map(s=>new Promise(r=>s.close(r))));
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
 }
 console.log(JSON.stringify({profiles:report.profiles.length,errors:report.errors}));if(report.errors.length)process.exitCode=1;
}
module.exports={safeReadAt,assertHosted};
if(require.main===module)run().catch(e=>{console.error(e);process.exitCode=1;});
