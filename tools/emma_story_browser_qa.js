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
 try{
  // Page-level checks at all three widths for the hub and the five stories.
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:900});
   await page.goto(origin+'/'+HUB);await noOverflow();
   await page.screenshot({path:path.join(out,`emma-hub-${width}.png`),fullPage:false});
   for(const s of STORIES){
    await page.goto(origin+'/'+s.page);await noOverflow();
    const img=page.locator(`img[src*="${s.base}-960.webp"]`);
    assert.equal(await img.count(),1,`${s.page}: story artwork image missing`);
    assert.equal(await img.getAttribute('alt'),s.alt,`${s.page}: alt text changed`);
    // Bring lazy-loaded story artwork into view before requiring decoded pixels.
    await img.scrollIntoViewIfNeeded();
    await page.waitForFunction(base=>{const n=document.querySelector('img[src*="'+base+'-960.webp"]');return n&&n.complete&&n.naturalWidth>0;},s.base,{timeout:10000});
    assert(await img.evaluate(n=>n.complete&&n.naturalWidth>0),`${s.page}: artwork image did not load`);
    await page.locator(`#${s.section}`).screenshot({path:path.join(out,`${s.base}-${width}.png`)});
   }
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
   await page.screenshot({path:path.join(out,`${s.base}-dialog-390.png`)});
   // Full-size viewer layer, then back to the dialog.
   await dialog.locator('a[data-full-image-viewer]').click();
   const viewer=page.locator('dialog.fc-full-image-viewer[open]');
   await viewer.waitFor({state:'visible'});
   assert((await viewer.locator('img').first().getAttribute('src')).includes(`${s.base}-1536.webp`),`${s.page}: full-size viewer image`);
   await viewer.locator('.fc-full-image-close').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-full-image-viewer[open]'));
   assert.equal(await page.locator('dialog.fc-artwork-detail-dialog[open]').count(),1,`${s.page}: study dialog lost after full-size close`);
   // Close returns focus to the artwork trigger.
   await dialog.locator('button[data-artwork-detail-close]').click();
   await page.waitForFunction(()=>!document.querySelector('dialog.fc-artwork-detail-dialog[open]'));
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
  results.push({page:HUB,journey:'hub-dialog-open-close',width:1280});
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({results,pass:true},null,2));
  console.log(`EMMA STORY PASS: 6 pages x 3 widths, 5 dialog/full-size/focus journeys, Continue Lesson, Escape, 5 hub link-and-back journeys`);
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
