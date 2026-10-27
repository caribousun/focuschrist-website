/* Focused owner-acceptance journeys. Hosted CI only; no local browser release. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'.qa-artifacts/owner-integration');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const PROFILES=[{name:'desktop',width:1280,height:900,touch:false},{name:'phone',width:390,height:844,touch:true},{name:'narrow',width:320,height:568,touch:true},{name:'landscape',width:844,height:390,touch:true}];
const TYPES={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.ico':'image/x-icon','.xml':'application/xml'};
const LIMIT={milliseconds:420000,requests:2500,servedBytes:384*1024*1024,shots:72,fileBytes:8*1024*1024,shotBytes:1024*1024,allShots:23*1024*1024,reportBytes:1024*1024};

function readContract(){
 const raw=fs.readFileSync(path.join(__dirname,'owner_integration_qa_contract.json'));
 const c=JSON.parse(raw);assert.equal(c.version,1);assert.equal(c.ready,true,'Exact reviewed source contract required');
 assert.equal(c.emma.route,'/history/emma-hale-smith.html');assert.equal(c.emma.stories.length,5);
 assert.deepEqual(c.emma.stories.map(s=>s.base),['emma-story1-ride-review','emma-story2-hymnal-review','emma-story3-quincy-review','emma-story4-hospitality-review','emma-story5-testimony-review']);
 assert.equal(c.adams.timeline,'/timeline.html');assert.equal(c.adams.intro,'/timelines/adams-1881-introduction.html');assert.equal(c.adams.chart,'/timelines/adams-1881-chart.html');
 assert.equal(c.adams.reference,'/timelines/latter-day-saint-church-history-timeline.html');
 assert.equal(c.emma.stories.filter(s=>s.reader).length,1,'One bounded owning-caption reader');
 const plannedShots=PROFILES.reduce((n,p)=>n+12+(['desktop','phone'].includes(p.name)?7:0)+(p.name==='phone'?4:0),0);assert.equal(plannedShots,66);assert(plannedShots<=LIMIT.shots);
 const checked=[];
 for(const r of [...c.sources,...c.assets]){
  assert(/^[a-zA-Z0-9_./-]+$/.test(r.path)&&!r.path.split('/').includes('..')&&!r.path.startsWith('/'));
  assert(!r.path.split('/').some(x=>x.startsWith('.')));const p=path.join(ROOT,r.path),s=fs.lstatSync(p);assert(s.isFile()&&!s.isSymbolicLink());
  const b=fs.readFileSync(p);assert.equal(b.length,r.bytes,r.path+' bytes');assert.equal(sha(b),r.sha256,r.path+' exact source');checked.push(r);
 }
 return {c,checked,contractSHA256:sha(raw)};
}

async function stable(page,selector){
 await page.waitForFunction(async selector=>{
  if(document.fonts)await document.fonts.ready;
  return new Promise(resolve=>{let last='',same=0;const until=performance.now()+4500;
   function frame(){const n=document.querySelector(selector);if(!n){resolve(false);return;}const r=n.getBoundingClientRect(),key=JSON.stringify([r.x,r.y,r.width,r.height,scrollX,scrollY]);same=key===last?same+1:0;last=key;
    if(same>=3){resolve(true);return;}if(performance.now()>=until){resolve(false);return;}requestAnimationFrame(frame);
   }requestAnimationFrame(frame);
  });
 },selector,{timeout:5000});
}
async function noOverflow(page,label){
 const r=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth}));
 assert(r.documentWidth<=r.width+1&&r.bodyWidth<=r.width+1,label+' horizontal overflow '+JSON.stringify(r));return r;
}
async function decoded(locator){
 await locator.scrollIntoViewIfNeeded();await locator.evaluate(n=>n.decode());
 assert(await locator.evaluate(n=>n.complete&&n.naturalWidth>0&&n.naturalHeight>0),'Decoded visible image required');
}
async function imageFlow(img){
 return img.evaluate(n=>{const r=n.getBoundingClientRect();let a=n,hidden=[];
  while(a){const c=getComputedStyle(a);if(a.hidden||c.display==='none'||c.visibility==='hidden'||c.visibility==='collapse'||Number(c.opacity)===0||(a.tagName==='DETAILS'&&!a.open))hidden.push(a.tagName+(a.id?'#'+a.id:''));a=a.parentElement;}
  const c=getComputedStyle(n),f=n.closest('figure');return {src:new URL(n.currentSrc).pathname,alt:n.alt,naturalWidth:n.naturalWidth,naturalHeight:n.naturalHeight,rect:{x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height},documentTop:r.top+scrollY,scrollY,viewport:{width:innerWidth,height:innerHeight},position:c.position,hiddenAncestors:hidden,inMain:!!n.closest('main'),figure:f?.id||'',dialog:!!n.closest('dialog'),centerHit:(()=>{const x=Math.max(0,Math.min(innerWidth-1,r.x+r.width/2)),y=Math.max(0,Math.min(innerHeight-1,r.y+r.height/2)),hit=document.elementFromPoint(x,y);return hit===n||!!hit&&n.contains(hit);})()};
 });
}
function checkFlow(r,label){
 assert.deepEqual(r.hiddenAncestors,[],label+' hidden/collapsed ancestor');assert(r.inMain&&!r.dialog,label+' must be an in-page main figure');assert(!['fixed','absolute'].includes(r.position),label+' image must remain in document flow');
 assert(r.rect.width>0&&r.rect.height>0&&r.rect.x>=-1&&r.rect.right<=r.viewport.width+1,label+' image bounds');
 assert(r.rect.bottom>0&&r.rect.y<r.viewport.height&&r.centerHit,label+' actual viewport image visibility');
}
async function chartSnapshot(page){
 return page.evaluate(()=>{const t=document.querySelector('#tiles img.tile');return t?{left:t.style.left,top:t.style.top,width:t.style.width,height:t.style.height,fit:document.querySelector('#fit')?.getAttribute('aria-pressed')}:null;});
}

async function headerJourney(page,record,profile,capture,label,chart){
 await stable(page,'nav[data-focuschrist-header="standard"]');
 const nav=page.locator('nav.nav[data-focuschrist-header="standard"]');assert.equal(await nav.count(),1,label+' canonical header');
 const m=await nav.evaluate(n=>{const r=n.getBoundingClientRect(),c=getComputedStyle(n);return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,display:c.display,position:c.position,background:c.backgroundColor,logo:n.querySelector('.nav-logo')?.textContent,controls:['.nav-logo','.fc-search-trigger[data-site-search-trigger]','.hamburger'].map(sel=>{const a=n.querySelector(sel),q=a.getBoundingClientRect(),cs=getComputedStyle(a),hit=document.elementFromPoint(q.x+q.width/2,q.y+q.height/2);return {selector:sel,x:q.x,y:q.y,right:q.right,bottom:q.bottom,width:q.width,height:q.height,visible:cs.display!=='none'&&cs.visibility==='visible',hit:!!hit&&(a===hit||a.contains(hit))};})};});
 assert(['flex','grid'].includes(m.display)&&m.height>=52&&m.x>=-1&&m.right<=profile.width+1,label+' styled header bounds');
 for(const r of m.controls)assert(r.width>0&&r.height>0&&r.visible&&r.hit&&r.x>=-1&&r.y>=-1&&r.right<=profile.width+1&&r.bottom<=profile.height+1,label+' reachable header control '+r.selector);
 const before=chart?await chartSnapshot(page):null,h=nav.locator('.hamburger'),menu=nav.locator('#hamburgerMenu');
 if(profile.touch){
  await h.click();await menu.waitFor({state:'visible',timeout:5000});assert.equal(await h.getAttribute('aria-expanded'),'true');await h.focus();await page.keyboard.press('ArrowRight');
  if(chart)assert.deepEqual(await chartSnapshot(page),before,'Menu keys must not pan the chart');
  const box=await menu.boundingBox();assert(box&&box.x>=-1&&box.y>=-1&&box.x+box.width<=profile.width+1&&box.y+box.height<=profile.height+1,'Menu fits visible viewport');
  if(profile.name==='phone'&&(label==='emma-hub'||label==='adams-chart'))await capture(label+'-menu');
  await page.keyboard.press('Escape');await page.waitForFunction(()=>{const h=document.querySelector('.hamburger'),m=document.getElementById('hamburgerMenu');return h?.getAttribute('aria-expanded')==='false'&&getComputedStyle(m).display==='none'&&document.activeElement===h;},null,{timeout:5000});
 }
 const search=nav.locator('[data-site-search-trigger]');await search.click();const dialog=page.locator('#fc-search-dialog[open]');await dialog.waitFor({state:'visible',timeout:5000});
 const input=dialog.locator('#fc-header-search');await input.fill('Emma');await page.keyboard.press('ArrowRight');
 if(chart)assert.deepEqual(await chartSnapshot(page),before,'Search keys must not pan the chart');
 if(profile.name==='phone'&&(label==='emma-hub'||label==='adams-chart'))await capture(label+'-search');
 await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.getElementById('fc-search-dialog')?.open&&document.activeElement===document.querySelector('[data-site-search-trigger]'),null,{timeout:5000});
 if(chart)assert.deepEqual(await chartSnapshot(page),before,'Search close must not change chart view');
 record.headers.push({label,...m,menuTested:profile.touch,searchTested:true,searchSubmitted:false,chartKeyboardGuard:!!chart});
}

async function scriptureJourney(page,trigger,expected,record,capture,label,artOpen){
 assert.equal(await trigger.count(),1,label+' citation identity');const href=await trigger.getAttribute('href');assert.equal(href,expected.href);
 await trigger.scrollIntoViewIfNeeded();await trigger.focus();await page.keyboard.press('Enter');const reader=page.locator('#fc-scripture-reader[open]');await reader.waitFor({state:'visible',timeout:8000});
 await page.waitForFunction(()=>document.querySelector('#fc-scripture-reader .fc-scripture-verses')?.children.length>0,null,{timeout:8000});
 assert.equal(await reader.locator('#fc-scripture-title').textContent(),expected.title);assert.equal(await reader.locator('.fc-scripture-source').getAttribute('href'),href);
 assert.deepEqual(await reader.locator('.fc-scripture-number').allTextContents(),expected.numbers.map(String));
 const chapter=JSON.parse(fs.readFileSync(path.join(ROOT,expected.data),'utf8'));
 const expectedText=chapter.verses.filter(v=>expected.numbers.includes(v.number)).map(v=>(v.number+' '+v.text).replace(/\s+/g,' ').trim());
 assert.deepEqual((await reader.locator('.fc-scripture-verse').allTextContents()).map(t=>t.replace(/\s+/g,' ').trim()),expectedText);
 await noOverflow(page,label);await capture(label);await page.keyboard.press('Escape');
 await page.waitForFunction(n=>!document.getElementById('fc-scripture-reader')?.open&&!document.body.classList.contains('fc-scripture-open')&&document.activeElement===n,await trigger.elementHandle(),{timeout:5000});
 assert.equal(await page.locator('dialog.fc-artwork-detail-dialog[open]').count(),artOpen?1:0);
 record.journeys.push({label,href,numbers:expected.numbers,exactText:true,focusReturned:true,artworkRemainedOpen:artOpen});
}

async function emmaJourney(page,origin,c,record,profile,capture){
 const response=await page.goto(origin+c.emma.route,{waitUntil:'load'});assert.equal(response.status(),200);await noOverflow(page,'Emma hub opening');
 await headerJourney(page,record,profile,capture,'emma-hub',false);await page.mouse.move(profile.width-2,profile.height-2);await capture('emma-hub-opening');
 let previous=-1;
 for(const s of c.emma.stories){
  const figure=page.locator(s.figure);assert.equal(await figure.count(),1,'One actual hub owner '+s.base);
  assert.equal(await figure.getAttribute('data-topic-art'),s.key);const img=figure.locator('img');assert.equal(await img.count(),1);assert.equal(await img.getAttribute('alt'),s.alt);
  await decoded(img);await stable(page,s.figure);const m=await imageFlow(img);checkFlow(m,s.base);assert(m.documentTop>previous,'Five artworks occur in chronological scroll flow');previous=m.documentTop;
  assert([640,960,1536].some(w=>m.src===`/assets/page-art/emma-life/${s.base}-${w}.webp`),'Approved source derivative '+m.src);
  const section=page.locator(s.section);assert.equal(await section.count(),1);assert((await section.innerText()).replace(/\s+/g,' ').includes(s.requiredText),'Substantive integrated story text '+s.base);
  await noOverflow(page,s.base);record.images.push({base:s.base,...m});await capture('emma-hub-'+s.base);
 }
 // Preserve the reviewed Christ reflection as a distinct, plainly identified
 // scripture reflection, not a substitute for an Emma historical artwork.
 assert.deepEqual(await page.locator('figure[data-topic-art]').evaluateAll(a=>a.map(n=>n.getAttribute('data-topic-art'))),c.emma.owners,'Exact current sole hub owners');
 assert.equal(await page.locator('#reflection-c2, #picture-emma-c2').count(),0,'Weak-fit Christ scene removed by owner decision');
 assert(await page.locator('#reflection-c5').evaluate(n=>n.previousElementSibling?.textContent.includes('killed at Carthage')),'Grief reflection follows actual Carthage loss');
 for(const r of c.emma.reflections){const n=page.locator(r.selector);assert.equal(await n.count(),1);assert((await n.innerText()).replace(/\s+/g,' ').trim().includes(r.text));}
 if(profile.name==='desktop'||profile.name==='phone'){
  for(const s of c.emma.stories){
   const trigger=page.locator(s.figure+' > a');await trigger.scrollIntoViewIfNeeded();await trigger.click();const detail=page.locator('dialog.fc-artwork-detail-dialog[open]');await detail.waitFor({state:'visible',timeout:8000});
   assert((await detail.innerText()).includes(s.title));assert.equal(await detail.locator('a[href="'+s.sourceHref+'"]').count(),1,'Owning dialog source preserved');
   const img=detail.locator('img').first();await decoded(img);assert(new URL(await img.getAttribute('src'),origin).pathname.endsWith(s.base+'-1536.webp'));
   await capture('emma-hub-'+s.base+'-dialog');
   if(s.reader){await scriptureJourney(page,detail.locator(s.reader.selector),s.reader,record,capture,'emma-hub-'+s.base+'-reader',true);}
   const fullTrigger=detail.locator('a[data-full-image-viewer]');await fullTrigger.click();const full=page.locator('dialog.fc-full-image-viewer[open]');await full.waitFor({state:'visible',timeout:8000});const fullImg=full.locator('img').first();await decoded(fullImg);assert(new URL(await fullImg.getAttribute('src'),origin).pathname.endsWith(s.base+'-1536.webp'));
   await full.locator('.fc-full-image-close').click();await page.waitForFunction(()=>!document.querySelector('dialog.fc-full-image-viewer[open]')&&!document.body.classList.contains('fc-full-image-open')&&document.activeElement?.matches('dialog.fc-artwork-detail-dialog[open] a[data-full-image-viewer]'),null,{timeout:5000});
   await detail.locator('button[data-artwork-detail-close]').click();await page.waitForFunction(n=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]')&&!document.body.classList.contains('fc-dialog-open')&&document.activeElement===n,await trigger.elementHandle(),{timeout:5000});
   record.journeys.push({label:s.base+'-hub-details-fullsize-close',source:s.sourceHref,exactFocusReturned:true});
  }
  const r=c.emma.reader;await scriptureJourney(page,page.locator(r.selector),r,record,capture,'emma-hub-scripture-reflection',false);
 }
 // The separate pages are honest references, not competing artwork owners.
 for(const s of c.emma.stories){
  await page.goto(origin+s.referenceRoute,{waitUntil:'load'});const ref=page.locator(s.referenceSelector);assert.equal(await ref.count(),1);assert.equal(await ref.getAttribute('href'),s.referenceHref);
  assert.equal(await page.locator('figure[data-topic-art="'+s.key+'"]').count(),0,'Separate page must not retain independent artwork ownership');
  await ref.scrollIntoViewIfNeeded();await ref.click();await page.waitForURL(origin+c.emma.route+s.fragment,{timeout:12000});await decoded(page.locator(s.figure+' img'));assert.equal(await page.locator('dialog.fc-artwork-detail-dialog[open]').count(),0,'Reference navigation is not a second lightbox');await noOverflow(page,'Reference return');
  record.journeys.push({label:s.base+'-reference-to-hub',from:s.referenceRoute,to:c.emma.route+s.fragment});
 }
}

async function openingMetrics(page){
 await stable(page,'.timeline-opening-continue');return page.evaluate(()=>{const rect=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom,centerX:r.x+r.width/2,centerY:r.y+r.height/2};};const hero=document.querySelector('.timeline-life-hero'),intro=document.querySelector('.timeline-life-intro'),cue=document.querySelector('.timeline-opening-continue'),cs=getComputedStyle(cue),range=document.createRange();range.selectNodeContents(cue);const text=range.getBoundingClientRect();const keys=['display','fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','textTransform','color','backgroundColor','borderTopWidth','borderTopStyle','borderTopColor','borderRadius','paddingTop','paddingRight','paddingBottom','paddingLeft','minHeight','justifyContent','alignItems'];return {hero:rect(hero),intro:rect(intro),cue:rect(cue),textBottom:text.bottom,style:Object.fromEntries(keys.map(k=>[k,cs[k]])),heroObjectFit:getComputedStyle(hero.querySelector('img')).objectFit};});
}
function compareOpening(reference,current){
 // Same browser, viewport, fonts and shared rule set: compare exactly. A
 // wrapped-copy baseline difference is evidence for review, not a waived pass.
 for(const key of ['x','y','width','height'])assert.equal(current.hero[key],reference.hero[key],'Reference hero '+key);
 assert.deepEqual(current.style,reference.style,'Reference Continue style');assert.equal(current.heroObjectFit,reference.heroObjectFit,'Reference hero object-fit');
 for(const key of ['width','height','centerX','y','bottom'])assert.equal(current.cue[key],reference.cue[key],'Reference Continue '+key);
 assert.equal(current.textBottom,reference.textBottom,'Reference Continue text baseline box');
}

async function adamsJourney(page,origin,c,record,profile,capture){
 await page.goto(origin+c.adams.reference,{waitUntil:'load'});await page.locator('.timeline-life-hero img').evaluate(n=>n.decode());await stable(page,'.timeline-life-hero');await page.mouse.move(profile.width-2,profile.height-2);const reference=await openingMetrics(page);await capture('church-reference-opening');
 await page.goto(origin+c.adams.timeline,{waitUntil:'load'});await noOverflow(page,'Timeline');await headerJourney(page,record,profile,capture,'timeline',false);
 const section=page.locator('#adams-1881');assert.equal(await section.count(),1);const overview=section.locator('img');assert.equal(await overview.count(),1);await decoded(overview);await capture('adams-timeline-section');
 const pill=page.locator('#choose-timeline .fc-timeline-choices a[href="timelines/adams-1881-introduction.html"]');assert.equal(await pill.count(),1,'Existing choice enters introduction');
 assert.equal(await overview.locator('..').getAttribute('href'),'timelines/adams-1881-introduction.html','Overview image also enters introduction');
 const entry=section.locator('.fc-button--primary[href="timelines/adams-1881-introduction.html"]');assert.equal(await entry.count(),1);await entry.click();await page.waitForURL(origin+c.adams.intro,{timeout:12000});await headerJourney(page,record,profile,capture,'adams-intro',false);await page.mouse.move(profile.width-2,profile.height-2);await stable(page,'.timeline-life-hero');
 const hero=page.locator('.fc-adams-intro-hero img');assert.equal(await hero.count(),1);await hero.evaluate(n=>n.decode());assert(await hero.evaluate(n=>n.complete&&n.naturalWidth>0));assert.equal(await page.locator('h1').count(),1);await noOverflow(page,'Adams introduction');
 const current=await openingMetrics(page);record.openingComparison={reference,current};await capture('adams-intro-opening');try{compareOpening(reference,current);}catch(e){record.acceptanceErrors.push(String(e));}
 // Preserve the failed comparison while continuing the independent viewer journey.
 const cue=page.locator('.timeline-opening-continue');assert.equal(await cue.getAttribute('href'),'#adams-overview');await cue.click();
 await page.waitForFunction(()=>{const n=document.getElementById('adams-overview'),r=n.getBoundingClientRect();return r.top>=-1&&r.top<=240;},null,{timeout:5000});await stable(page,'#adams-overview');await capture('adams-intro-overview');
 const open=page.locator('#adams-open-chart');assert.equal(await open.getAttribute('href'),'adams-1881-chart.html');await open.click();await page.waitForURL(origin+c.adams.chart,{timeout:12000});
 await page.waitForFunction(()=>{const a=[...document.querySelectorAll('#tiles img.tile')];return a.length>0&&a.every(n=>n.complete&&n.naturalWidth>0);},null,{timeout:10000});await stable(page,'#toolbar');await stable(page,'#tiles img.tile');await headerJourney(page,record,profile,capture,'adams-chart',true);
 assert.equal(await page.locator('main#adams-chart-main').count(),1);assert.equal(await page.locator('.fc-adams-strip').count(),0,'Rejected pre-heading wall removed');assert.equal(await page.locator('footer[data-focuschrist-footer="standard"] .fc-adams-credit').count(),1);
 const layout=await page.evaluate(()=>{const box=n=>{const r=n.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height};};return {nav:box(document.querySelector('nav[data-focuschrist-header="standard"]')),heading:box(document.querySelector('#toolbar h1')),toolbar:box(document.getElementById('toolbar')),viewport:box(document.getElementById('viewport')),main:box(document.getElementById('adams-chart-main'))};});
 assert(layout.heading.top>=layout.nav.bottom-1,'Canonical header above chart heading');assert(Math.abs(layout.viewport.top-layout.toolbar.bottom)<=1,'Chart viewport below actual toolbar');assert(layout.viewport.height>0,'Chart remains usable below header');record.chartLayout=layout;
 await noOverflow(page,'Adams chart');await capture('adams-chart-opening');
 const footer=page.locator('footer[data-focuschrist-footer="standard"]');await footer.scrollIntoViewIfNeeded();assert((await footer.innerText()).includes(c.adams.credit));const fm=await footer.boundingBox();assert(fm&&fm.y<profile.height&&fm.y+fm.height>0,'Footer is scroll-reachable');record.footer={...fm,scrollY:await page.evaluate(()=>scrollY)};await noOverflow(page,'Chart footer');await capture('adams-chart-footer');
 await footer.locator('a[href="adams-1881-introduction.html"]').click();await page.waitForURL(origin+c.adams.intro,{timeout:12000});await page.goBack({waitUntil:'load'});await page.waitForURL(origin+c.adams.chart,{timeout:12000});
 record.journeys.push({label:'timeline-illustrated-intro-continue-chart-footer-back',referenceCompared:true});
}

async function main(){
 assert.equal(process.env.CI,'true','Hosted CI only; no local browser launch');assert.equal(process.argv.length,2,'No custom server/origin or options');
 const {c,checked,contractSHA256}=readContract();fs.mkdirSync(path.dirname(OUT),{recursive:true});fs.mkdirSync(OUT,{recursive:false});
 const report={scope:'Focused actual owner-integration journeys; broad CI remains required',producer:{sha:process.env.GITHUB_SHA||null,run:process.env.GITHUB_RUN_ID||null,event:process.env.GITHUB_EVENT_NAME||null},contractSHA256,checked,profiles:[],screenshots:[],network:[],blocked:[],errors:[],timedOut:false,pass:false};
 let server,browser,timer,requests=0,servedBytes=0,shotBytes=0;const pending=[];
 try{
  server=http.createServer((req,res)=>{
   if(!['GET','HEAD'].includes(req.method))return res.writeHead(405).end();let decodedPath;try{decodedPath=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);}catch{return res.writeHead(400).end();}
   if(decodedPath==='/' )decodedPath='/index.html';const parts=decodedPath.split('/').filter(Boolean),ext=path.extname(decodedPath).toLowerCase();
   if(parts.some(x=>x.startsWith('.'))||!TYPES[ext]||parts.length>1&&!['assets','history','timelines','scripture-data'].includes(parts[0]))return res.writeHead(403).end();
   const file=path.resolve(ROOT,'.'+decodedPath);if(!file.startsWith(ROOT+path.sep))return res.writeHead(403).end();
   try{const stat=fs.lstatSync(file);if(!stat.isFile()||stat.isSymbolicLink()||fs.realpathSync(file)!==file)return res.writeHead(403).end();if(stat.size>LIMIT.fileBytes)return res.writeHead(413).end();}catch{return res.writeHead(404).end();}
   fs.readFile(file,(e,b)=>{if(e)return res.writeHead(404).end();servedBytes+=b.length;if(servedBytes>LIMIT.servedBytes){report.errors.push('Served byte bound exceeded');return res.writeHead(413).end();}res.writeHead(200,{'Content-Type':TYPES[ext]});res.end(req.method==='HEAD'?undefined:b);});
  });await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});const origin='http://127.0.0.1:'+server.address().port;
  browser=await chromium.launch({headless:true});timer=setTimeout(()=>{report.timedOut=true;browser.close().catch(()=>{});server.closeAllConnections?.();},LIMIT.milliseconds);
  const assets=new Map(c.assets.map(r=>['/'+r.path,r]));
  for(const profile of PROFILES){
   if(report.timedOut)break;const record={profile,pass:false,images:[],headers:[],journeys:[],acceptanceErrors:[]};report.profiles.push(record);let context;
   try{
    context=await browser.newContext({viewport:{width:profile.width,height:profile.height},isMobile:profile.touch,hasTouch:profile.touch,deviceScaleFactor:1,reducedMotion:'reduce',serviceWorkers:'block'});
    await context.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin!==origin){if(report.blocked.length<100)report.blocked.push({profile:profile.name,url:u.origin+u.pathname});return route.abort();}if(++requests>LIMIT.requests){report.errors.push('Request bound exceeded');return route.abort();}return route.continue();});
    const page=await context.newPage();page.setDefaultTimeout(8000);page.setDefaultNavigationTimeout(12000);page.on('pageerror',e=>report.errors.push(String(e).slice(0,1000)));
    page.on('response',response=>{const u=new URL(response.url());if(u.origin!==origin)return;if(response.status()>=400)report.errors.push('HTTP '+response.status()+' '+u.pathname);const a=assets.get(u.pathname);if(!a)return;pending.push((async()=>{const b=await response.body();assert.equal(response.status(),200);assert.equal(b.length,a.bytes);assert.equal(sha(b),a.sha256);report.network.push({profile:profile.name,path:u.pathname,status:response.status(),bytes:b.length,sha256:a.sha256});})().catch(e=>report.errors.push(String(e).slice(0,1000))));});
    const capture=async label=>{assert(report.screenshots.length<LIMIT.shots,'Capture count');const b=await page.screenshot({type:'jpeg',quality:80,fullPage:false,animations:'disabled',timeout:8000});assert(b.length<=LIMIT.shotBytes&&shotBytes+b.length<=LIMIT.allShots,'Capture byte bound');const name=profile.name+'-'+label+'.jpg';fs.writeFileSync(path.join(OUT,name),b,{flag:'wx'});shotBytes+=b.length;report.screenshots.push({file:name,bytes:b.length,sha256:sha(b),viewport:{width:profile.width,height:profile.height}});};
    await emmaJourney(page,origin,c,record,profile,capture);await adamsJourney(page,origin,c,record,profile,capture);await Promise.all(pending);assert.deepEqual(report.errors,[],'Runtime/network errors');assert.deepEqual(record.acceptanceErrors,[],'Exact owner geometry comparisons');record.pass=true;
   }catch(e){record.error=String(e.stack||e).slice(0,5000);}finally{if(context)await context.close();}
  }
  await Promise.all(pending);report.pass=!report.timedOut&&report.profiles.length===4&&report.profiles.every(r=>r.pass)&&report.errors.length===0;
 }catch(e){report.errors.push(String(e.stack||e).slice(0,5000));}
 finally{
  clearTimeout(timer);if(browser)await browser.close().catch(e=>report.errors.push(String(e)));if(server){server.closeAllConnections?.();await new Promise(resolve=>server.close(resolve));}
  report.requests=requests;report.servedBytes=servedBytes;report.screenshotBytes=shotBytes;report.pass=report.pass&&report.errors.length===0;
  report.limits=['Hosted Chromium emulation, not physical-device or deployed acceptance.','No native pinch/drag, external source navigation, search submission or model calls.','Exact opening comparison failures remain failures; no layout/style injection or tolerance waiver.'];
  const b=Buffer.from(JSON.stringify(report,null,2)+'\n');assert(b.length<=LIMIT.reportBytes,'Report byte bound');fs.writeFileSync(path.join(OUT,'report.json'),b,{flag:'wx'});
 }
 console.log(JSON.stringify({pass:report.pass,profiles:report.profiles.map(r=>({name:r.profile.name,pass:r.pass,error:r.error})),shots:report.screenshots.length,report:'.qa-artifacts/owner-integration/report.json'}));if(!report.pass)process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1;});
