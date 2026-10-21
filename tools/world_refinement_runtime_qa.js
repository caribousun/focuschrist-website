/* Actual UI regression for alphabetical groups, reading links and playback. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require(process.env.QA_PLAYWRIGHT_MODULE||'playwright'),root=path.resolve(__dirname,'..');
(async()=>{
 const out=path.join(root,'.qa-artifacts/continue-motion/world-refinement');fs.mkdirSync(out,{recursive:true});const results=[];
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.webp':'image/webp','.pdf':'application/pdf','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})[path.extname(file)]||'application/octet-stream'}).end(b));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{
  browser=await chromium.launch({headless:true,...(process.env.QA_CHROME_CHANNEL?{channel:process.env.QA_CHROME_CHANNEL}:{})});
  for(const width of [1366,390]){
   const page=await browser.newPage({viewport:{width,height:900}});
   await page.goto('http://127.0.0.1:'+server.address().port+'/timelines/world-and-scripture-timeline.html');
   await page.locator('#study-companions>summary').click();assert.equal(await page.locator('#study-companions article').count(),4);
   const links=await page.locator('#study-companions a[href]').evaluateAll(a=>a.map(n=>({href:n.getAttribute('href'),target:n.target,rel:n.rel,download:n.hasAttribute('download')})));
   assert.equal(links.filter(n=>n.download).length,3);assert(links.every(n=>n.download?!n.target:n.target==='_blank'&&n.rel.split(/\s+/).includes('noopener')));
   const parent=page.url(),popupPromise=page.waitForEvent('popup');await page.locator('#study-companions a').first().click();const popup=await popupPromise;await popup.waitForLoadState();assert(await popup.evaluate(()=>opener===null));assert.equal(page.url(),parent);await popup.close();
   await page.locator('#study-companions>summary').click();await page.locator('#modeMap').click();
   for(const year of [-600,-3900,33]){
    await page.locator('#yearInput').fill(String(year));await page.locator('#yearInput').dispatchEvent('change');
    const groups=await page.locator('#momentList>h4').evaluateAll(a=>a.map(h=>[...h.nextElementSibling.querySelectorAll('button[data-i]')].map(n=>n.textContent)));
    assert(groups.length);for(const names of groups)assert.deepEqual(names,[...names].sort((a,b)=>a.localeCompare(b,'en',{sensitivity:'base'})));
   }
   assert.deepEqual(await page.locator('#playSpeed option').evaluateAll(a=>a.map(n=>n.value)),['0.25','0.5','1','2','5','10']);
   await page.locator('#yearInput').fill('-3900');await page.locator('#yearInput').dispatchEvent('change');await page.locator('#playSpeed').selectOption('0.25');await page.locator('#playBtn').click();
   await page.waitForFunction(()=>mapState.year!==-3900,{},{timeout:7000});const first=await page.evaluate(()=>mapState.year);assert(first>-3900&&first<=-3890);
   await page.locator('#playBtn').click();const paused=await page.evaluate(()=>mapState.year);await page.waitForTimeout(4300);assert.equal(await page.evaluate(()=>mapState.year),paused);
   await page.locator('#yearInput').fill('-610');await page.locator('#yearInput').dispatchEvent('change');await page.locator('#playSpeed').selectOption('10');
   await page.evaluate(()=>{window.playbackWrites=[];let value=mapState.year;Object.defineProperty(mapState,'year',{configurable:true,get:()=>value,set(next){playbackWrites.push({from:value,to:next,time:performance.now()});value=next;}});});
   await page.locator('#playBtn').click();await page.waitForFunction(()=>playbackWrites.filter(r=>r.to!==r.from).length>=5);await page.locator('#playBtn').click();
   // Rendering may reassign the same clamped year; only changed values advance.
   const transitions=await page.evaluate(()=>playbackWrites.filter(r=>r.to!==r.from).map(r=>({...r,skipped:PLAYKEYS.some(k=>k>r.from&&k<r.to)})));
   fs.writeFileSync(path.join(out,'transitions-'+width+'.json'),JSON.stringify(transitions,null,2));assert(transitions.length>=5);assert(transitions.every(r=>r.to>r.from&&r.to-r.from<=10&&!r.skipped));
   await page.locator('#yearInput').fill('1697');await page.locator('#yearInput').dispatchEvent('change');await page.locator('#playBtn').click();await page.waitForFunction(()=>mapState.year===1700&&!mapState.playing);
   assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)));
   results.push({width,groupsSorted:true,newTabReader:true,links,slowPauseMs:4300,transitions,terminal:1700});await page.close();
  }
  console.log('WORLD REFINEMENT BROWSER PASS: desktop/phone alphabetical groups, new-tab reader, slow cancellation, fast event-preserving steps and terminal stop');
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));}
})().catch(e=>{console.error(e);process.exitCode=1});
