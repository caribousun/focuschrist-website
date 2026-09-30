/* Hosted vertical-fit regression; owner composition acceptance is separate. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const inventory=JSON.parse(fs.readFileSync(path.join(root,'docs/answer-opening-baseline.json'),'utf8')).pages;
const results=[];
(async()=>{
 const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
  const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};
  fs.readFile(file,(e,data)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'}).end(data));
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{
  browser=await chromium.launch({headless:true});const context=await browser.newContext();
  await context.route('https://**',r=>r.abort());const page=await context.newPage();
  for(const [width,height] of [[1918,991],[1536,792],[1366,768],[1920,900]]){
   await page.setViewportSize({width,height});
   for(const [file,record] of Object.entries(inventory)){
    await page.goto(`http://127.0.0.1:${server.address().port}/${file}`,{waitUntil:'domcontentloaded'});
    await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(100);
    const selector=record.kind==='fc-topic-opening'?'.fc-topic-opening .fc-scroll-cue':record.kind==='jj-opening'?'.jj-opening .fc-covenant-continue':'.fc-source-opening a[href="#begin-study"]';
    const evidence=await page.locator(selector).evaluate(el=>{
     const r=el.getBoundingClientRect(),s=getComputedStyle(el);let clipped=false;
     for(let p=el.parentElement;p;p=p.parentElement){const ps=getComputedStyle(p),b=p.getBoundingClientRect();if(/hidden|clip/.test(ps.overflowY)&&(r.bottom>b.bottom+1||r.top<b.top-1))clipped=true;}
     return {top:r.top,bottom:r.bottom,height:r.height,left:r.left,right:r.right,visible:s.display!=='none'&&s.visibility!=='hidden',clipped,href:el.getAttribute('href'),overflow:document.documentElement.scrollWidth>innerWidth+1};
    });
    const {height:controlHeight,...controlEvidence}=evidence;
    results.push({file,viewportWidth:width,viewportHeight:height,controlHeight,...controlEvidence});
    assert(evidence.visible&&!evidence.clipped&&!evidence.overflow&&evidence.top>=0&&evidence.bottom<=height-8&&evidence.height>=43.5&&evidence.left>=0&&evidence.right<=width+1,JSON.stringify(results.at(-1)));
    if(record.kind==='jj-opening'){
     const alignment=await page.locator('.jj-opening').evaluate(opening=>{
      const title=opening.querySelector('h1'),cue=opening.querySelector('.fc-covenant-continue'),r=cue.getBoundingClientRect(),s=getComputedStyle(title);
      return {titleAlign:s.textAlign,titleFont:s.fontFamily,titleWeight:s.fontWeight,cueCenter:(r.left+r.right)/2,viewportCenter:innerWidth/2,breadcrumb:!!opening.querySelector('a[href="/answers.html"]')};
     });
     Object.assign(results.at(-1),{alignment});
     assert(alignment.titleAlign==='center'&&alignment.titleFont.includes('Georgia')&&alignment.titleWeight==='400'&&Math.abs(alignment.cueCenter-alignment.viewportCenter)<=8&&!alignment.breadcrumb,file+': owner-requested centered shared Answer opening '+JSON.stringify(alignment));
    }
    const completeOpening=await page.locator('.'+record.kind).evaluate(opening=>{
     const controls=[...opening.querySelectorAll('a,button,summary')].filter(el=>!el.matches('[data-hero-viewer]')&&!el.closest('.fc-visual-hero')).flatMap(el=>{
      // Closed disclosure contents may retain layout rects without being painted.
      // Only the direct summary remains visible; test every closed ancestor.
      for(let p=el.parentElement;p&&p!==opening.parentElement;p=p.parentElement){
       if(p.tagName==='DETAILS'&&!p.open){const summary=[...p.children].find(c=>c.tagName==='SUMMARY');if(!summary||!summary.contains(el))return [];}
      }
      const r=el.getBoundingClientRect(),s=getComputedStyle(el);
      if(!r.width||!r.height||s.display==='none'||s.visibility==='hidden')return [];
      let clipped=false;for(let p=el.parentElement;p;p=p.parentElement){const ps=getComputedStyle(p),b=p.getBoundingClientRect();if(/hidden|clip/.test(ps.overflowY)&&(r.bottom>b.bottom+1||r.top<b.top-1))clipped=true;}
      return [{text:el.textContent.trim(),top:r.top,bottom:r.bottom,left:r.left,right:r.right,clipped}];
     });
     return {bottom:opening.getBoundingClientRect().bottom,controls};
    });
    Object.assign(results.at(-1),{completeOpening});
    assert(completeOpening.bottom<=height+16,file+': complete opening extends beyond viewport '+JSON.stringify(completeOpening));
    assert(completeOpening.controls.every(c=>!c.clipped&&c.top>=0&&c.bottom<=height&&c.left>=0&&c.right<=width+1),file+': clipped secondary opening control '+JSON.stringify(completeOpening));
    await page.locator(selector).click();
    assert.equal(new URL(page.url()).hash,evidence.href,file+': same-page Continue target');
   }
  }
  // Focused owner regressions retain the full 100-case Answer matrix above.
  for(const file of ['art.html','answers/abrahamic-covenant.html']){
   for(const [width,height] of [[1918,991],[1536,792],[1366,768],[1920,900],[320,740],[390,844],[432,936]]){
    await page.setViewportSize({width,height});
    await page.goto(`http://127.0.0.1:${server.address().port}/${file}`,{waitUntil:'domcontentloaded'});
    await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(100);
    const evidence=await page.evaluate(({file,width})=>{
     const art=file==='art.html',opening=document.querySelector(art?'.fc-page-intro':'.jj-opening');
     const visible=el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width&&r.height&&s.display!=='none'&&s.visibility!=='hidden';};
     const cues=[...opening.querySelectorAll('.fc-art-continue,.fc-covenant-continue,.fc-mobile-scroll-cue')].filter(visible);
     const controls=cues.map(el=>{const r=el.getBoundingClientRect();let clipped=false;for(let p=el.parentElement;p;p=p.parentElement){const s=getComputedStyle(p),b=p.getBoundingClientRect();if(/hidden|clip/.test(s.overflowY)&&(r.bottom>b.bottom+1||r.top<b.top-1))clipped=true;}return {href:el.getAttribute('href'),top:r.top,bottom:r.bottom,left:r.left,right:r.right,height:r.height,clipped};});
     const title=getComputedStyle(opening.querySelector('h1')),href=controls[0]?.href,target=href&&document.querySelector(href);
     return {file,kind:'focused-owner-opening',viewportWidth:width,viewportHeight:innerHeight,controls,openingBottom:opening.getBoundingClientRect().bottom,overflow:document.documentElement.scrollWidth>innerWidth+1,oldArtCue:!!document.querySelector('.art-scroll-cue'),breadcrumb:!!opening.querySelector('a[href="/answers.html"]'),titleAlign:title.textAlign,titleFont:title.fontFamily,titleWeight:title.fontWeight,targetExists:!!target,phoneHint:!!target?.querySelector('.fc-art-study-hint'),targetText:target?.textContent.trim().slice(0,200)};
    },{file,width});
    results.push(evidence);
    assert.equal(evidence.controls.length,1,JSON.stringify(evidence));
    const cue=evidence.controls[0];
    assert(!cue.clipped&&!evidence.overflow&&cue.top>=0&&cue.bottom<=height-8&&cue.height>=43.5&&cue.left>=0&&cue.right<=width+1&&evidence.openingBottom<=height+16&&evidence.targetExists,JSON.stringify(evidence));
    if(file==='art.html'){
     assert(!evidence.oldArtCue,JSON.stringify(evidence));
     if(width>700)assert(cue.href==='#art-gallery'&&Math.abs((cue.left+cue.right)/2-width/2)<=8,JSON.stringify(evidence));
     else assert(evidence.phoneHint,JSON.stringify(evidence));
    }else{
     assert(!evidence.breadcrumb&&evidence.titleAlign==='center'&&evidence.titleFont.includes('Georgia')&&evidence.titleWeight==='400'&&Math.abs((cue.left+cue.right)/2-width/2)<=8&&cue.href==='#a-promise-to-live-by',JSON.stringify(evidence));
    }
    await page.locator(file==='art.html'?(width>700?'.fc-art-continue':'.fc-mobile-scroll-cue'):'.fc-covenant-continue:visible').click();
    assert.equal(new URL(page.url()).hash,cue.href,file+': focused same-page Continue target');
   }
  }
  console.log(`ANSWER OPENING BROWSER PASS: ${results.length} cases; full100 Answer desktop matrix plus14 Art/Covenant desktop/phone cases; complete opening,44px Continue,8px clearance,preserved targets and centered owner openings`);
 }finally{
  fs.mkdirSync(path.join(root,'.qa-artifacts'),{recursive:true});fs.writeFileSync(path.join(root,'.qa-artifacts/answer-openings.json'),JSON.stringify(results,null,2));
  if(browser)await browser.close();await new Promise(r=>server.close(r));
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
