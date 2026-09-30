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
    results.push({file,width,height,...evidence});
    assert(evidence.visible&&!evidence.clipped&&!evidence.overflow&&evidence.top>=0&&evidence.bottom<=height-8&&evidence.height>=43.5&&evidence.left>=0&&evidence.right<=width+1,JSON.stringify(results.at(-1)));
    const completeOpening=await page.locator('.'+record.kind).evaluate(opening=>{
     const controls=[...opening.querySelectorAll('a,button,summary')].filter(el=>!el.matches('[data-hero-viewer]')&&!el.closest('.fc-visual-hero')).flatMap(el=>{
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
  console.log(`ANSWER OPENING BROWSER PASS: ${results.length} desktop cases; complete opening and all visible controls,44px Continue,8px cue clearance,no clipping/overflow,and same-page navigation`);
 }finally{
  fs.mkdirSync(path.join(root,'.qa-artifacts'),{recursive:true});fs.writeFileSync(path.join(root,'.qa-artifacts/answer-openings.json'),JSON.stringify(results,null,2));
  if(browser)await browser.close();await new Promise(r=>server.close(r));
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
