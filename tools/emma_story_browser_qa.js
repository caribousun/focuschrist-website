const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/emma-story');
// Narrowly scoped rendered verification for the Emma story finisher (A-009):
// the five new story pages and their hub at desktop, phone and narrow phone,
// including the composed artwork-dialog, full-size-viewer and back-navigation
// journeys. Expected titles, alt text and sources are the Hannah-reviewed
// strings carried on the pages; they are asserted as literals here so a page
// regression cannot silently rewrite its own expectations.
const STORIES=[
 {page:'history/emma-elect-lady.html',base:'emma-story1-ride-review',section:'elect-lady-right-person',title:'A ride to warn Joseph',
  alt:'Emma Smith at twenty three, wearing a long blue dress, rides sidesaddle at a gallop on a brown horse up a leaf covered slope in autumn, leaning forward with both hands on the reins and her eyes on the path ahead.',
  sourceLabel:'Emma Protected Scripture',sourceHref:'https://www.churchofjesuschrist.org/study/liahona/2021/03/emma-protected-scripture?lang=eng'},
 {page:'history/emma-hymns.html',base:'emma-story2-hymnal-review',section:'hymns-book',title:'The finished hymnbook',
  alt:'Emma Smith at thirty one, wearing a brown dress, stands by a window holding a small bound book in both hands and looking down at it.',
  sourceLabel:'Collection of Sacred Hymns, 1835',sourceHref:'https://www.josephsmithpapers.org/paper-summary/collection-of-sacred-hymns-1835/1'},
 {page:'history/emma-winter-crossing.html',base:'emma-story3-quincy-review',section:'crossing-words',title:'Emma in Quincy',
  alt:'Emma Smith at thirty four, wearing a gray dress, sits by a window with her hands folded in her lap and her gaze lowered.',
  sourceLabel:'Letter from Emma Smith, 7 March 1839',sourceHref:'https://www.josephsmithpapers.org/paper-summary/letter-from-emma-smith-7-march-1839/1'},
 {page:'history/emma-relief-society.html',base:'emma-story4-hospitality-review',section:'relief-relieved',title:'An open door',
  alt:'Emma Smith at thirty eight, wearing a dark green dress, stands in the open doorway of her home with one hand resting on the door.',
  sourceLabel:'Female Relief Society of Nauvoo',sourceHref:'https://www.churchofjesuschrist.org/study/history/topics/female-relief-society-of-nauvoo?lang=eng'},
 {page:'history/emma-last-testimony.html',base:'emma-story5-testimony-review',section:'testimony-kept',title:'Her testimony',
  alt:'Emma Smith at seventy four, wearing a dark gray dress, sits speaking, one hand raised in conversation, her gaze toward the one she is speaking with.',
  sourceLabel:'My Great-Great-Grandmother Emma Hale Smith',sourceHref:'https://www.churchofjesuschrist.org/study/ensign/1992/08/my-great-great-grandmother-emma-hale-smith?lang=eng'}];
const HUB='history/emma-hale-smith.html';
const TYPES={'.html':'text/html','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.json':'application/json','.xml':'application/xml','.woff2':'font/woff2','.ico':'image/x-icon'};
(async()=>{
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,d)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':TYPES[path.extname(file)]||'application/octet-stream'}).end(d));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const origin=`http://127.0.0.1:${server.address().port}`;
 const browser=await chromium.launch({headless:true}),page=await browser.newPage(),results=[];
 fs.mkdirSync(out,{recursive:true});
 const noOverflow=async()=>{const m=await page.evaluate(()=>({sw:document.documentElement.scrollWidth,iw:innerWidth}));assert(m.sw<=m.iw+1,`horizontal overflow ${m.sw} > ${m.iw} on ${page.url()}`);};
 // Keep evidence inside the real viewport: tall element clips can include
 // offscreen fixed controls. Never mask, restyle or blur the skip link.
 const skipEvidence=[],headerEvidence=[],footerEvidence=[],shots=[];let screenshotBytes=0;
 const saveEvidence=()=>{const b=Buffer.from(JSON.stringify({skipEvidence,headerEvidence,footerEvidence,shots,screenshotBytes},null,2)+'\n');assert(b.length<=128*1024,'Skip evidence JSON bound');fs.writeFileSync(path.join(out,'skip-link-evidence.json'),b);};
 const capture=async name=>{
  assert(shots.length<75,'Emma screenshot count bound');
  const jpeg=name.endsWith('.jpg'),data=await page.screenshot({type:jpeg?'jpeg':'png',...(jpeg?{quality:80}:{}),fullPage:false,timeout:8000});
  assert(data.length<=1024*1024,'Single Emma screenshot exceeds 1 MiB');
  assert(screenshotBytes+data.length<=23*1024*1024,'Emma screenshot evidence exceeds 23 MiB');
  fs.writeFileSync(path.join(out,name),data,{flag:'wx'});screenshotBytes+=data.length;shots.push({file:name,bytes:data.length,viewport:page.viewportSize()});saveEvidence();
 };
 const readSkip=async label=>{
  const data=await page.evaluate(()=>{
   const a=document.querySelector('[data-focuschrist-skip-link]');if(!a)return {missing:true};
   const r=a.getBoundingClientRect(),c=getComputedStyle(a),active=document.activeElement;
   return {rect:{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom},viewport:{width:innerWidth,height:innerHeight},scroll:{x:scrollX,y:scrollY},focused:active===a,activeElement:{tag:active?.tagName,id:active?.id||'',className:typeof active?.className==='string'?active.className:''},transform:c.transform,position:c.position,display:c.display,visibility:c.visibility,opacity:c.opacity,outline:{style:c.outlineStyle,width:c.outlineWidth},intersects:r.right>0&&r.bottom>0&&r.left<innerWidth&&r.top<innerHeight,href:a.getAttribute('href')};
  });skipEvidence.push({label,page:new URL(page.url()).pathname,...data});saveEvidence();return data;
 };
 const hiddenSkip=async label=>{const s=await readSkip(label);assert(!s.missing,'Expected shared skip link');assert(!s.focused,label+': skip link unexpectedly focused');assert(!s.intersects,label+': unfocused skip link intersects the real viewport');};
 // Canonical selectors and behavior are copied from the existing hub,
 // site-header.css, site-common.js initNavigation and site-search.js initHeader.
 const checkHeader=async(s,width)=>{
  const nav=page.locator('nav.nav[data-focuschrist-header="standard"]');
  assert.equal(await nav.count(),1,`${s.page}: canonical header missing`);
  assert.equal(await page.locator('header.fc-header[data-site-header]').count(),0,'Alternate unstyled header remains');
  // Shared navigation schedules its fit on load and fonts.ready, then rAF.
  // Observe that normal lifecycle before measuring; do not force its classes.
  await page.waitForFunction(async()=>{if(document.fonts)await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));return true;},null,{timeout:5000});
  const measure=await nav.evaluate(n=>{
   const c=getComputedStyle(n),r=n.getBoundingClientRect(),logo=n.querySelector('.nav-logo'),lc=getComputedStyle(logo);
   const controls=['.nav-logo','.fc-search-trigger[data-site-search-trigger]','.hamburger'].map(selector=>{
    const a=n.querySelector(selector),q=a.getBoundingClientRect(),cs=getComputedStyle(a),hit=document.elementFromPoint(q.x+q.width/2,q.y+q.height/2);
    return {selector,x:q.x,y:q.y,right:q.right,bottom:q.bottom,width:q.width,height:q.height,display:cs.display,visibility:cs.visibility,hit:!!hit&&(a===hit||a.contains(hit))};
   });
   return {rect:{x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height},display:c.display,position:c.position,backgroundImage:c.backgroundImage,backgroundColor:c.backgroundColor,logoDecoration:lc.textDecorationLine,logoSpacing:lc.letterSpacing,linksDisplay:getComputedStyle(n.querySelector('.nav-links')).display,controls};
  });headerEvidence.push({page:s.page,width,label:'normal-header',...measure});saveEvidence();
  assert(['flex','grid'].includes(measure.display),'Canonical header layout CSS not applied');
  assert(measure.backgroundImage!=='none'||!['transparent','rgba(0, 0, 0, 0)'].includes(measure.backgroundColor),'Header background missing');
  assert(measure.logoDecoration==='none'&&parseFloat(measure.logoSpacing)>0,'Canonical wordmark styling missing');
  assert(measure.rect.height>=52&&measure.rect.x>=-1&&measure.rect.right<=width+1,'Header geometry');
  assert.equal(measure.position,width<=1020?'relative':'fixed','Shared header positioning contract');
  assert(width<=1020?measure.linksDisplay==='none':measure.linksDisplay!=='none','Responsive navigation visibility');
  for(const c of measure.controls)assert(c.width>0&&c.height>0&&c.x>=-1&&c.y>=-1&&c.right<=width+1&&c.bottom<=900&&c.display!=='none'&&c.visibility==='visible'&&c.hit,`Unreachable header control ${JSON.stringify(c)}`);
  const timeline=nav.locator('a[data-focuschrist-primary-timeline]');assert((await timeline.count())>=2,'Desktop and menu Timeline destinations');
  for(const href of await timeline.evaluateAll(a=>a.map(n=>n.getAttribute('href'))))assert.equal(href,'../timeline.html','Canonical Timeline target');
  assert.equal(await nav.locator('a[href="../timeline/world.html"]').count(),0,'Broken alternate Timeline route remains');
  const hamburger=nav.locator('.hamburger'),menu=nav.locator('#hamburgerMenu'),search=nav.locator('.fc-search-trigger[data-site-search-trigger]');
  assert.equal(await hamburger.getAttribute('aria-expanded'),'false');assert.equal(await menu.isVisible(),false);
  await capture(`${s.base}-header-${width}.jpg`);
  if(width<=1020){
   await hamburger.click();await menu.waitFor({state:'visible',timeout:5000});
   await page.waitForFunction(()=>document.querySelector('.hamburger')?.getAttribute('aria-expanded')==='true',null,{timeout:5000});
   const box=await menu.boundingBox();assert(box&&box.x>=-1&&box.y>=0&&box.x+box.width<=width+1&&box.y+box.height<=900,'Mobile menu must fit viewport');
   if(s.page===STORIES[1].page)await capture(`emma-mobile-menu-${width}.jpg`);
   await page.keyboard.press('Escape');
   await page.waitForFunction(()=>{const h=document.querySelector('.hamburger'),m=document.getElementById('hamburgerMenu');return h?.getAttribute('aria-expanded')==='false'&&getComputedStyle(m).display==='none'&&document.activeElement===h;},null,{timeout:5000});
   // Keyboard opens the same menu, then Search closes it and owns the modal.
   await page.keyboard.press('Enter');await menu.waitFor({state:'visible',timeout:5000});
   await search.click();const dialog=page.locator('#fc-search-dialog[open]');await dialog.waitFor({state:'visible',timeout:5000});
   await page.waitForFunction(()=>document.activeElement===document.getElementById('fc-header-search'),null,{timeout:5000});
   assert.equal(await menu.isVisible(),false);assert.equal(await hamburger.getAttribute('aria-expanded'),'false');
   const form=dialog.locator('form.fc-search-form');assert.equal(await form.getAttribute('method'),'get');
   assert.equal(await form.getAttribute('action'),origin+'/search.html');
   const input=dialog.locator('#fc-header-search');assert.equal(await input.getAttribute('name'),'q');await input.fill('Emma');assert.equal(await input.inputValue(),'Emma');
   if(s.page===STORIES[1].page)await capture(`emma-mobile-search-${width}.jpg`);
   await dialog.locator('.fc-search-close').click();
   await page.waitForFunction(()=>!document.getElementById('fc-search-dialog')?.open&&document.activeElement===document.querySelector('.fc-search-trigger[data-site-search-trigger]'),null,{timeout:5000});
   headerEvidence.push({page:s.page,width,label:'menu-keyboard-search-close',pass:true,searchSubmitted:false});saveEvidence();
  }
  results.push({page:s.page,journey:width<=1020?'canonical-header-menu-search':'canonical-header',width});
 };
 try{
  // Page-level checks at all three widths for the hub and the five stories.
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:900});
   await page.goto(origin+'/'+HUB);await noOverflow();
   await hiddenSkip(`hub-${width}-normal`);
   await capture(`emma-hub-${width}.png`);
   for(const s of STORIES){
    await page.goto(origin+'/'+s.page);await noOverflow();
    await hiddenSkip(`${s.base}-${width}-normal-before-tab`);
    await checkHeader(s,width);
    await page.mouse.move(width-8,450);await page.mouse.wheel(0,240);
    await hiddenSkip(`${s.base}-${width}-pointer-reading`);
    const img=page.locator(`img[src*="${s.base}-960.webp"]`);
    assert.equal(await img.count(),1,`${s.page}: story artwork image missing`);
    assert.equal(await img.getAttribute('alt'),s.alt,`${s.page}: alt text changed`);
    // Bring lazy-loaded story artwork into view before requiring decoded pixels.
    await img.scrollIntoViewIfNeeded();
    await page.waitForFunction(base=>{const n=document.querySelector('img[src*="'+base+'-960.webp"]');return n&&n.complete&&n.naturalWidth>0;},s.base,{timeout:10000});
    assert(await img.evaluate(n=>n.complete&&n.naturalWidth>0),`${s.page}: artwork image did not load`);
    // The artwork-centered viewport is actual reader-visible content, not a
    // stitched whole-section image. Record its box and any viewport clipping.
    const artwork=await img.evaluate(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom,viewportWidth:innerWidth,viewportHeight:innerHeight};});
    skipEvidence.push({label:`${s.base}-${width}-artwork-box`,page:s.page,artwork});
    await hiddenSkip(`${s.base}-${width}-artwork-viewport`);
    await capture(`${s.base}-${width}-viewport.jpg`);
    await hiddenSkip(`${s.base}-${width}-after-capture`);
   }
  }
  // Real keyboard path at each existing width: first Tab reveals the
  // first-in-body skip link; Enter focuses its main landmark and hides it again.
  // Normal pointer/scroll evidence above was recorded before any Tab.
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:900});await page.goto(origin+'/'+STORIES[1].page);
   await hiddenSkip(`keyboard-${width}-before-tab`);
   await page.keyboard.press('Tab');
   await page.waitForFunction(()=>{const a=document.querySelector('[data-focuschrist-skip-link]');if(!a||document.activeElement!==a)return false;const r=a.getBoundingClientRect();return r.top>=0&&r.left>=0&&r.right<=innerWidth&&r.bottom<=innerHeight;},null,{timeout:5000});
   const shown=await readSkip(`keyboard-${width}-focused`);
   assert(shown.focused&&shown.intersects&&shown.visibility==='visible'&&shown.display!=='none'&&Number(shown.opacity)>0,'Keyboard-focused skip link must be visible');
   assert(shown.outline.style!=='none'&&parseFloat(shown.outline.width)>0,'Keyboard-focused skip link must retain its focus indicator');
   await capture(`emma-skip-keyboard-${width}.jpg`);
   await page.keyboard.press('Enter');
   await page.waitForFunction(()=>{const a=document.querySelector('[data-focuschrist-skip-link]'),main=document.querySelector('main');return a&&main&&document.activeElement===main&&a.getBoundingClientRect().bottom<=0;},null,{timeout:5000});
   await hiddenSkip(`keyboard-${width}-after-enter`);
   results.push({page:STORIES[1].page,journey:'skip-link-tab-enter-main',width});
  }
  // Composed journeys at phone width: artwork dialog, full-size viewer,
  // Continue Lesson, Close with focus return, on every story page.
  await page.setViewportSize({width:390,height:900});
  for(const s of STORIES){
   await page.goto(origin+'/'+s.page);
   const trigger=page.locator(`a:has(img[src*="${s.base}-960.webp"])`);
   await trigger.scrollIntoViewIfNeeded();await trigger.click();
   const dialog=page.locator('dialog.fc-artwork-detail-dialog[open]');
   await dialog.waitFor({state:'visible'});
   const dialogTitle=await dialog.evaluate(d=>d.textContent);
   assert(dialogTitle.includes(s.title),`${s.page}: dialog does not carry its title`);
   assert(dialogTitle.includes(s.sourceLabel),`${s.page}: dialog missing source pill ${s.sourceLabel}`);
   const source=dialog.locator(`a[href="${s.sourceHref}"]`);
   assert.equal(await source.count(),1,`${s.page}: dialog source link`);
   const dialogImg=dialog.locator('img');
   assert((await dialogImg.getAttribute('src')).includes(`${s.base}-1536.webp`),`${s.page}: dialog image is not the full-size derivative`);
   await capture(`${s.base}-dialog-390.png`);
   // Full-size viewer layer, then back to the dialog.
   await dialog.locator('a[data-full-image-viewer]').click();
   const viewer=page.locator('dialog.fc-full-image-viewer[open]');
   await viewer.waitFor({state:'visible'});
   assert((await viewer.locator('img').first().getAttribute('src')).includes(`${s.base}-1536.webp`),`${s.page}: full-size viewer image`);
   await viewer.locator('.fc-full-image-close').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-full-image-viewer[open]'));
   await page.waitForFunction(()=>!document.body.classList.contains('fc-full-image-open')&&document.activeElement?.matches('dialog.fc-artwork-detail-dialog[open] a[data-full-image-viewer]'),null,{timeout:5000});
   assert.equal(await page.locator('dialog.fc-artwork-detail-dialog[open]').count(),1,`${s.page}: study dialog lost after full-size close`);
   // Close returns focus to the artwork trigger.
   await dialog.locator('button[data-artwork-detail-close]').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]'));
   // Native close() removes [open] before its queued close event runs.
   // The topic dialog's close listener removes this class and restores focus.
   // Observe that lifecycle completion; do not alter the page or waive the assertions.
   await page.waitForFunction(()=>!document.body.classList.contains('fc-dialog-open'),null,{timeout:5000});
   assert.equal(await page.evaluate(()=>document.body.classList.contains('fc-dialog-open')),false,`${s.page}: dialog-open body class left behind`);
   assert(await trigger.evaluate(n=>document.activeElement===n),`${s.page}: focus did not return to the artwork`);
   results.push({page:s.page,journey:'dialog-fullsize-close-focus',width:390});
  }
  // Continue Lesson closes the dialog and lands on the story section (story 1),
  // and Escape dismisses the dialog (story 2), at phone width.
  {
   const s=STORIES[0];await page.goto(origin+'/'+s.page);
   const trigger=page.locator(`a:has(img[src*="${s.base}-960.webp"])`);
   await trigger.scrollIntoViewIfNeeded();await trigger.click();
   const dialog=page.locator('dialog.fc-artwork-detail-dialog[open]');await dialog.waitFor({state:'visible'});
   await dialog.locator('a[data-topic-art-continue]').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]'));
   // The shipped landing is specific: the close handler focuses the story
   // section's reading-target heading (marked data-topic-reading-target and
   // given tabindex -1) and scrolls it to the header clearance at the top
   // of the viewport. Assert exactly that, not mere section overlap.
   await page.waitForFunction(()=>{const a=document.activeElement;return a&&a.hasAttribute('data-topic-reading-target');});
   // Topic close focuses after two frames, then header-scroll animates Continue
   // for 560 ms. Observe the same exact landing until stable, never force scroll.
   await page.waitForFunction(section=>new Promise(resolve=>{
    const deadline=performance.now()+4500;let anchor=null,stableSince=0;
    const sample=()=>{
     const now=performance.now(),a=document.activeElement,r=a?.getBoundingClientRect(),sec=a?.closest('section');
     const ready=a?.hasAttribute('data-topic-reading-target')&&sec?.id===section&&r.top>=-1&&r.top<=240&&!document.body.classList.contains('fc-dialog-open')&&!document.querySelector('dialog[open]');
     if(ready){
      if(!anchor||anchor.target!==a||Math.abs(anchor.top-r.top)>.1||Math.abs(anchor.scrollY-scrollY)>.1){anchor={target:a,top:r.top,scrollY};stableSince=now;}
      else if(now-stableSince>=150){resolve(true);return;}
     }else{anchor=null;stableSince=0;}
     if(now>=deadline){resolve(false);return;}requestAnimationFrame(sample);
    };requestAnimationFrame(sample);
   }),s.section,{timeout:5000});
   const landing=await page.evaluate(()=>{const a=document.activeElement,r=a.getBoundingClientRect(),sec=a.closest('section');return {section:sec?sec.id:'',top:r.top};});
   assert.equal(landing.section,s.section,'Continue Lesson focus did not land on the story section reading target');
   assert(landing.top>=-1&&landing.top<=240,`Continue Lesson heading sits at ${landing.top}px, not at the reading clearance below the viewport top`);
   results.push({page:s.page,journey:'continue-lesson',width:390});
  }
  {
   const s=STORIES[1];await page.goto(origin+'/'+s.page);
   const trigger=page.locator(`a:has(img[src*="${s.base}-960.webp"])`);
   await trigger.scrollIntoViewIfNeeded();await trigger.click();
   const dialog=page.locator('dialog.fc-artwork-detail-dialog[open]');await dialog.waitFor({state:'visible'});
   await page.keyboard.press('Escape');
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]'));
   await page.waitForFunction(base=>{const a=document.activeElement;return !document.body.classList.contains('fc-dialog-open')&&a?.matches('a')&&a.querySelector('img[src*="'+base+'-960.webp"]');},s.base,{timeout:5000});
   assert(await trigger.evaluate(n=>document.activeElement===n),`${s.page}: Escape focus did not return to the artwork`);
   results.push({page:s.page,journey:'escape-close',width:390});
  }
  // Hub journeys at desktop: the story doorway is the hub's story listing.
  // It must hold exactly the five story cards; each card reaches its page
  // and Back returns to the hub. (The hub also carries inline Continue
  // links to the same pages in body text; those are not the listing and
  // are deliberately not what this journey clicks.)
  await page.setViewportSize({width:1280,height:900});
  await page.goto(origin+'/'+HUB);
  assert.equal(await page.locator('.fc-story-doorway a.fc-life-reflection').count(),5,'hub story doorway must list exactly five story cards');
  for(const s of STORIES){
   await page.goto(origin+'/'+HUB);
   await page.locator(`.fc-story-doorway a.fc-life-reflection[href="${s.page.split('/').pop()}"]`).click();
   await page.waitForURL('**/'+s.page);await noOverflow();
   await page.goBack();await page.waitForURL('**/'+HUB);
   results.push({page:s.page,journey:'hub-doorway-link-and-back',width:1280});
  }
  // The hub's first artwork (emma-c1) must open the study dialog: its
  // figure carries panel copy and a source link, so the shipped topic
  // script claims the trigger and showStudy opens the detail dialog with
  // the 1536 derivative. If the bare full-size viewer opened instead, the
  // claim regressed and this journey must fail, not adapt.
  await page.goto(origin+'/'+HUB);
  const hubTrigger=page.locator('a[data-full-image-alt]').first();
  await hubTrigger.scrollIntoViewIfNeeded();await hubTrigger.click();
  const hubDialog=page.locator('dialog.fc-artwork-detail-dialog[open]');
  await hubDialog.waitFor({state:'visible'});
  assert((await hubDialog.evaluate(d=>d.textContent)).includes('A night given to prayer'),'hub dialog does not carry the emma-c1 title');
  assert((await hubDialog.locator('img').getAttribute('src')).includes('emma-c1-review-1536.webp'),'hub dialog image is not the emma-c1 full derivative');
  await hubDialog.locator('button[data-artwork-detail-close]').click();
  await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]'));
  await page.waitForFunction(()=>!document.body.classList.contains('fc-dialog-open')&&document.activeElement===document.querySelector('a[data-full-image-alt]'),null,{timeout:5000});
  assert(await hubTrigger.evaluate(n=>document.activeElement===n),'Hub close focus did not return to its artwork');
  results.push({page:HUB,journey:'hub-dialog-open-close',width:1280});
  // Additive footer-only observations after every existing journey/capture.
  // Observe actual standard footer layout; do not hide/restyle any page content.
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:900});
   for(const s of STORIES){
    await page.goto(origin+'/'+s.page);await noOverflow();
    const footer=page.locator('footer.fc-footer[data-focuschrist-footer="standard"]');
    assert.equal(await footer.count(),1,'One canonical story footer');
    await footer.scrollIntoViewIfNeeded({timeout:5000});
    await page.waitForFunction(async()=>{if(document.fonts)await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return true;},null,{timeout:5000});
    const observation=await footer.evaluate(f=>{
     const independence=f.querySelector('[data-focuschrist-independence="footer"]'),art=f.querySelector('[data-focuschrist-artwork-disclosure="footer"]');
     const measure=n=>{if(!n)return null;const r=n.getBoundingClientRect(),c=getComputedStyle(n);return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,display:c.display,visibility:c.visibility,opacity:c.opacity};};
     const official=independence?.querySelector('a');
     return {footer:measure(f),independence:measure(independence),artwork:measure(art),independenceCount:f.querySelectorAll('[data-focuschrist-independence="footer"]').length,artworkCount:f.querySelectorAll('[data-focuschrist-artwork-disclosure="footer"]').length,independenceText:independence?.textContent,artworkText:art?.textContent,adjacent:independence?.nextElementSibling===art,official:official?{href:official.getAttribute('href'),target:official.getAttribute('target'),rel:official.getAttribute('rel'),label:official.textContent}:null,viewport:{width:innerWidth,height:innerHeight},scroll:{x:scrollX,y:scrollY}};
    });
    footerEvidence.push({page:s.page,width,...observation});saveEvidence();
    assert.equal(observation.independenceCount,1);assert.equal(observation.artworkCount,1);assert(observation.adjacent,'Canonical notices adjacent');
    assert.equal(observation.independenceText,'focusChrist is an independent faith-based website and is not an official website of, sponsored by, or endorsed by The Church of Jesus Christ of Latter-day Saints. For official Church information, visit ChurchofJesusChrist.org.');
    assert.equal(observation.artworkText,'Artwork on focusChrist includes AI-generated artistic interpretations. Illustrative and reconstructed details are not photographs or eyewitness records of the people or events shown.');
    assert.deepEqual(observation.official,{href:'https://www.churchofjesuschrist.org/',target:'_blank',rel:'noopener noreferrer',label:'ChurchofJesusChrist.org'});
    for(const box of [observation.footer,observation.independence,observation.artwork])assert(box&&box.width>0&&box.height>0&&box.x>=-1&&box.right<=width+1&&box.y>=-1&&box.bottom<=901&&box.display!=='none'&&box.visibility==='visible'&&Number(box.opacity)>0,'Footer notices must be visible within actual viewport');
    await noOverflow();
    await capture(`${s.base}-footer-${width}.jpg`);
    results.push({page:s.page,journey:'canonical-footer-notices',width});
   }
  }
  // Exact new hymns citation journeys; all prior 60 captures/46 results retained.
  const scriptureEvidence=[],scriptureControlEvidence=[];
  const chapter25=JSON.parse(fs.readFileSync(path.join(root,'scripture-data/dc-testament/dc/25.json'),'utf8'));
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:900});
   await page.goto(origin+'/history/emma-hymns.html');
   await page.waitForSelector('#fc-scripture-reader',{state:'attached',timeout:8000});
   const chapter='https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/25?lang=eng';
   const exercise=async(trigger,label,range,artOpen)=>{
    const href=await trigger.getAttribute('href');
    assert.equal(href,chapter+(range?'&id=p11-p12#p11':''));
    assert.equal(await trigger.getAttribute('target'),'_blank');
    assert.equal(await trigger.getAttribute('rel'),'noopener noreferrer');
    await trigger.scrollIntoViewIfNeeded();await trigger.focus();
    assert(await trigger.evaluate(n=>document.activeElement===n));
    await page.keyboard.press('Enter');
    const reader=page.locator('#fc-scripture-reader[open]');await reader.waitFor({state:'visible',timeout:8000});
    await page.waitForFunction(()=>document.querySelector('#fc-scripture-reader .fc-scripture-verses')?.children.length>0,null,{timeout:8000});
    assert.equal(await reader.locator('#fc-scripture-title').textContent(),'Doctrine and Covenants 25'+(range?':11–12':''));
    assert.equal(await reader.locator('.fc-scripture-source').getAttribute('href'),href);
    const numbers=await reader.locator('.fc-scripture-number').allTextContents();
    assert.deepEqual(numbers,range?['11','12']:Array.from({length:16},(_,i)=>String(i+1)));
    const passage=await reader.locator('.fc-scripture-verse').allTextContents();
    assert.deepEqual(passage.map(t=>t.replace(/\s+/g,' ').trim()),chapter25.verses.filter(v=>!range||[11,12].includes(v.number)).map(v=>(String(v.number)+' '+v.text).replace(/\s+/g,' ').trim()));
    await noOverflow();
    if(label!=='body-second')await capture(`emma-hymns-scripture-${label}-${width}.jpg`);
    if(label==='body-first')await page.keyboard.press('Escape');else await reader.locator('.fc-scripture-x').click();
    await page.waitForFunction(n=>!document.getElementById('fc-scripture-reader').open&&document.activeElement===n&&!document.body.classList.contains('fc-scripture-open'),await trigger.elementHandle(),{timeout:5000});
    assert(await trigger.evaluate(n=>document.activeElement===n),'Scripture focus returns to exact citation');
    assert.equal(await page.locator('dialog.fc-artwork-detail-dialog[open]').count(),artOpen?1:0);
    assert.equal(await page.evaluate(()=>document.body.classList.contains('fc-scripture-open')),false);
    scriptureEvidence.push({page:'history/emma-hymns.html',width,label,href,verses:numbers,keyboardEnter:true,close:label==='body-first'?'Escape':'button',exactFocusReturned:true,artworkRemainedOpen:artOpen});
    results.push({page:'history/emma-hymns.html',journey:'scripture-'+label,width});
   };
   const visible=page.locator('main a.fc-inline-scripture:visible');assert.equal(await visible.count(),3);
   await exercise(visible.nth(0),'body-first',false,false);
   await exercise(visible.nth(1),'body-second',false,false);
   await exercise(visible.nth(2),'source-range',true,false);
   const art=page.locator('a:has(img[src*="emma-story2-hymnal-review-960.webp"])');await art.click();
   const detail=page.locator('dialog.fc-artwork-detail-dialog[open]');await detail.waitFor({state:'visible'});
   const caption=detail.locator('.fc-artwork-detail-copy a.fc-inline-scripture[href*="/dc/25?"]');assert.equal(await caption.count(),1);
   await exercise(caption,'caption',false,true);
   const chapterPill=detail.locator('.fc-artwork-detail-actions a[data-topic-art-source][href="'+chapter+'"]');
   assert.equal(await chapterPill.count(),1);await exercise(chapterPill,'source-pill',false,true);
   const jsp=detail.locator('.fc-artwork-detail-actions a[href="https://www.josephsmithpapers.org/paper-summary/collection-of-sacred-hymns-1835/1"]');assert.equal(await jsp.count(),1);
   const controls=detail.locator('.fc-artwork-detail-actions a,button[data-artwork-detail-close]');
   for(const control of await controls.all()){
    await control.scrollIntoViewIfNeeded();const m=await control.evaluate(n=>{const r=n.getBoundingClientRect(),c=getComputedStyle(n),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {x:r.x,right:r.right,y:r.y,bottom:r.bottom,width:r.width,height:r.height,visible:c.display!=='none'&&c.visibility!=='hidden',hit:hit===n||n.contains(hit)};});
    scriptureControlEvidence.push({viewportWidth:width,label:await control.textContent(),...m});
    assert(m.visible&&m.width>0&&m.height>0&&m.x>=-1&&m.right<=width+1&&m.y>=-1&&m.bottom<=901&&m.hit,'Hymns dialog action must be reachable');
   }
   await jsp.scrollIntoViewIfNeeded();await capture(`emma-hymns-artwork-actions-${width}.jpg`);
   await detail.locator('a[data-full-image-viewer]').click();const full=page.locator('dialog.fc-full-image-viewer[open]');await full.waitFor({state:'visible'});
   assert((await full.locator('img').first().getAttribute('src')).includes('emma-story2-hymnal-review-1536.webp'));
   await full.locator('.fc-full-image-close').click();await page.waitForFunction(()=>!document.querySelector('dialog.fc-full-image-viewer[open]')&&document.activeElement?.matches('dialog.fc-artwork-detail-dialog[open] a[data-full-image-viewer]'),null,{timeout:5000});
   await detail.locator('button[data-artwork-detail-close]').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]'));
   await page.waitForFunction(()=>document.activeElement?.querySelector('img[src*="emma-story2-hymnal-review-960.webp"]'),null,{timeout:5000});
   await art.click();await detail.waitFor({state:'visible'});await detail.locator('a[data-topic-art-continue]').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]')&&document.activeElement?.hasAttribute('data-topic-reading-target')&&document.activeElement.closest('section')?.id==='hymns-book'&&!document.body.classList.contains('fc-dialog-open'),null,{timeout:5000});
   results.push({page:'history/emma-hymns.html',journey:'scripture-expanded-artwork-actions-fullsize-close-continue',width});
  }
  assert.equal(scriptureEvidence.length,15);
  const scriptureBytes=Buffer.from(JSON.stringify({scope:'Actual same-page scripture interactions; not full release',scriptureEvidence,scriptureControlEvidence},null,2)+'\n');
  assert(scriptureBytes.length<=32*1024,'Scripture telemetry bound');fs.writeFileSync(path.join(out,'scripture-link-evidence.json'),scriptureBytes);
  assert.equal(footerEvidence.length,15);assert.equal(shots.length,75);assert.equal(results.length,64);
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({results,pass:true},null,2));
  console.log(`EMMA STORY PASS: 6 pages x 3 widths, normal styled headers/menu/search, viewport and 3 skip-link keyboard checks, 5 dialog/full-size/focus journeys, Continue Lesson, Escape, 5 hub link-and-back journeys`);
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
