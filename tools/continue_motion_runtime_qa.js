/* Real browser motion regression: sampled movement, not just behavior arguments. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require(process.env.QA_PLAYWRIGHT_MODULE||'playwright'),root=path.resolve(__dirname,'..');
const out=path.join(root,'.qa-artifacts/continue-motion');
(async()=>{
 const server=http.createServer((req,res)=>{
  const url=new URL(req.url,'http://localhost'),file=path.resolve(root,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));
  if(!file.startsWith(root+path.sep))return res.writeHead(403).end();
  fs.readFile(file,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'application/octet-stream'}).end(b));
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const origin='http://127.0.0.1:'+server.address().port;let browser;const results=[];
 fs.mkdirSync(out,{recursive:true});
 try{
  browser=await chromium.launch({headless:true,...(process.env.QA_CHROME_CHANNEL?{channel:process.env.QA_CHROME_CHANNEL}:{})});
  for(const width of [1536,390]){
   const context=await browser.newContext({viewport:{width,height:width===390?844:807}}),page=await context.newPage();
   const errors=[];page.on('pageerror',e=>errors.push(String(e)));
   for(const route of ['index.html','ask.html','atonement.html','timelines/world-and-scripture-timeline.html','timelines/willie-and-martin-handcart-map.html']){
    await page.goto(origin+'/'+route);await page.waitForFunction(()=>!!window.FocusContinueScroll);
    await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(200);
    const cue=page.locator('a.fc-unified-continue:visible,a.fc-scroll-cue:visible,a.fc-mobile-scroll-cue:visible,a.timeline-opening-continue:visible,a.scrollcue:visible').first();
    assert(await cue.count(),route+': real visible Continue cue required');
    await cue.scrollIntoViewIfNeeded();
    const href=await cue.getAttribute('href'),initial=await page.evaluate(()=>scrollY);
    await page.evaluate(()=>{window.qaMotion=[];const start=performance.now();function tick(){qaMotion.push([performance.now()-start,scrollY]);if(performance.now()-start<1000)requestAnimationFrame(tick)}requestAnimationFrame(tick)});
    await cue.click();await page.waitForTimeout(1050);
    const samples=await page.evaluate(()=>qaMotion),positions=new Set(samples.map(x=>Math.round(x[1])));
    assert(positions.size>4,route+': actual intermediate Continue positions required');
    assert(Math.abs(samples.at(-1)[1]-samples.at(-5)[1])<=1,route+': no late snap-back');
    assert.equal(await cue.getAttribute('href'),href);
    assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)));
    results.push({route,width,kind:'Continue',initial,positions:positions.size,final:samples.at(-1)[1]});
    // The exact same control honors a changed accessibility preference.
    await page.emulateMedia({reducedMotion:'reduce'});await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
    await cue.scrollIntoViewIfNeeded();await cue.click();await page.waitForTimeout(80);
    const reduced=await page.evaluate(()=>scrollY);await page.waitForTimeout(650);
    assert(Math.abs(reduced-await page.evaluate(()=>scrollY))<=1,route+': reduced motion must already be settled');
    results.push({route,width,kind:'reduced',final:reduced});await page.emulateMedia({reducedMotion:'no-preference'});
   }
   // A real ordinary Atonement chapter link continues to jump immediately.
   await page.goto(origin+'/atonement.html');await page.waitForFunction(()=>!!window.FocusContinueScroll);
   const href='#healing',native=page.locator('a[href="#healing"]:visible').first();
   assert(await native.count(),'Real ordinary chapter link required');
   await native.scrollIntoViewIfNeeded();await native.click();await page.waitForTimeout(100);
   const landed=await page.evaluate(()=>scrollY);await page.waitForTimeout(650);
   assert(Math.abs(landed-await page.evaluate(()=>scrollY))<=1,'Ordinary link must not animate or recapture');
   results.push({width,kind:'ordinary',href,final:landed});assert.deepEqual(errors,[]);
   await page.screenshot({path:path.join(out,'ordinary-'+width+'.png')});await context.close();
  }
  console.log('CONTINUE MOTION BROWSER PASS: '+results.length+' actual desktop/phone animation, reduced-motion and ordinary-link cases');
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));}
})().catch(e=>{console.error(e);process.exitCode=1});
