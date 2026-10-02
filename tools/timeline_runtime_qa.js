/* Focused hosted-browser checks. Provider tiles and owner phone approval remain separate evidence. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/timeline');
(async()=>{
 assert.equal(process.env.CI,'true','Run rendered QA in hosted CI only');
 const {chromium}=require('playwright');
 const server=http.createServer((req,res)=>{const url=new URL(req.url,'http://localhost'),file=path.resolve(root,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.json':'application/json'})[path.extname(file)]||'application/octet-stream'}).end(b));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port;
 let browser;const results=[];fs.mkdirSync(out,{recursive:true});
 try{
 browser=await chromium.launch({headless:true});
 for(const profile of [{name:'desktop',width:1366,height:900,scale:1},{name:'phone',width:390,height:844,scale:1},{name:'narrow-large-text',width:320,height:900,scale:2}]){
  const context=await browser.newContext({viewport:{width:profile.width,height:profile.height}}),page=await context.newPage();
  await context.route('https://**',r=>r.abort()); // Deliberately tests usable stories if map/font providers are unavailable.
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const scaleText=async()=>page.evaluate(scale=>{if(scale===1)return;const nodes=[...document.body.querySelectorAll('*')];nodes.forEach(n=>{if(n.dataset.qaTextScaled==='true')n.style.fontSize=n.dataset.qaOriginalFontSize;});const sizes=nodes.map(n=>parseFloat(getComputedStyle(n).fontSize));nodes.forEach((n,i)=>{if(n.dataset.qaTextScaled!=='true')n.dataset.qaOriginalFontSize=n.style.fontSize;n.style.fontSize=sizes[i]*scale+'px';n.dataset.qaTextScaled='true';});},profile.scale);
  const visit=async route=>{const response=await page.goto(origin+'/'+route,{waitUntil:'load'});assert.equal(response.status(),200);await scaleText();};
  const measure=async label=>{await scaleText();assert(await page.locator('h1').first().isVisible(),label+' visible h1');assert.equal(await page.locator('iframe').count(),0,label+' not embedded');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+3),label+' horizontal overflow');await page.screenshot({path:path.join(out,profile.name+'-'+label+'.png'),fullPage:false});};
  await visit('timeline.html');
  for(const target of ['latter-day-saint-church-history-timeline.html','willie-and-martin-handcart-map.html'])assert(await page.locator('a[href$="'+target+'"]').count(),target+' accessible from hub');
  assert.equal(await page.locator('a[href*="life-of-christ"]').count(),0,'Life of Christ remains held');
  await measure('hub');
  if(profile.name==='desktop'){await page.setViewportSize({width:1920,height:1080});
  assert.equal(await page.locator('.fc-nav-side--before a').count(),5,'Five links before central Atonement');assert.equal(await page.locator('.fc-nav-side--after a').count(),5,'Five links after central Atonement');
  assert.deepEqual(await page.locator('.fc-nav-side--after a').evaluateAll(nodes=>nodes.map(n=>n.textContent.trim())),['History','Pioneers','Watch','Timeline','About']);
  const center=await page.locator('.fc-nav-atonement').boundingBox();assert(center&&Math.abs(center.x+center.width/2-(await page.evaluate(()=>document.documentElement.clientWidth))/2)<4,'Atonement centered at wide desktop');
  assert(await page.locator('#hamburgerMenu a').evaluateAll(nodes=>{const labels=nodes.map(n=>n.textContent.trim());return labels.indexOf('Timeline')+1===labels.indexOf('About');}),'Menu Timeline immediately before About');
  await page.setViewportSize({width:profile.width,height:profile.height});}
  const choice=page.locator('.fc-timeline-choices a').first();await choice.focus();assert(await choice.evaluate(n=>n===document.activeElement),'Timeline pill keyboard focus');await choice.press('Enter');assert(page.url().endsWith('/timelines/latter-day-saint-church-history-timeline.html'),'Keyboard opens standalone experience');
  await visit('timelines/latter-day-saint-church-history-timeline.html');
  assert.equal(await page.locator('.event').count(),51);assert.equal(await page.locator('#prophetGrid .prophet').count(),18);
  const story=page.locator('.card-top').first();await story.click();assert.equal(await story.getAttribute('aria-expanded'),'true');assert(await page.locator('[data-card].open .detail').first().isVisible());await measure('history-open');await story.press('Enter');assert.equal(await story.getAttribute('aria-expanded'),'false');
  await page.locator('[data-era="nauvoo"]').click();assert.equal(await page.locator('.era-block').count(),1);assert.equal(await page.locator('.era-block').getAttribute('id'),'era-nauvoo');
  await page.locator('[data-era="all"]').click();await page.locator('#search').fill('nonexistentxyz');assert.equal(await page.locator('.event').count(),0);assert(await page.locator('#noResults').isVisible());await page.locator('#search').fill('temple');assert((await page.locator('.event').count())>0);assert((await page.locator('.event').count())<51);await page.locator('#search').fill('');assert.equal(await page.locator('.event').count(),51);
  await page.locator('#prophetGrid').scrollIntoViewIfNeeded();await measure('presidents');
  await visit('timelines/willie-and-martin-handcart-map.html');
  assert.equal(await page.locator('.stop-card').count(),33);const stop=page.locator('.stop-card').first();await stop.click();assert(await page.locator('#detail-panel.is-open').isVisible());assert(!(await page.locator('#detail-title').textContent()).includes('Choose a stop'));assert((await page.locator('#detail-body').innerText()).length>100);await measure('handcart-open');
  if(profile.width<=700){assert.equal(await page.locator('#detail-panel').evaluate(el=>getComputedStyle(el).position),'fixed');assert((await page.locator('#detail-close').boundingBox()).height>=44,'Phone close touch target at least44px');await page.locator('#detail-close').click();assert.equal(await page.locator('#detail-panel.is-open').count(),0);}
  await page.locator('[data-filter="willie"]').click();const count=await page.locator('.stop-card').count();assert(count>0&&count<33);await page.locator('[data-filter="all"]').click();assert.equal(await page.locator('.stop-card').count(),33);
  assert.deepEqual(errors,[],profile.name+' uncaught errors');results.push({profile:profile.name,events:51,presidents:18,stops:33,filters:true,search:true,keyboardStory:true,providerUnavailableFallback:true});await context.close();
 }
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({results,limitations:['Hosted Chromium does not establish owner phone approval.','Remote map tiles intentionally blocked; provider-backed map needs separate live inspection.']},null,2)+'\n');}
 assert.equal(results.length,3);console.log('PASS: Timeline hub and standalone interactions across desktop, phone and enlarged text; remote-provider fallback verified.');
})().catch(e=>{console.error(e);process.exitCode=1;});
