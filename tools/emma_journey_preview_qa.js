'use strict';
// Hosted diagnostic only. It does not approve artwork, source copy, geometry,
// predecessor contracts or release. Run with a complete exact checkout.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {inspect:inspectPixels}=require('./emma_capture_pixel_guard');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/emma-journey');
const ids=['emma-story1-ride','emma-story2-hymnal','emma-story3-quincy','emma-story4-hospitality','emma-story5-testimony','emma-h1','emma-h3','emma-h4','emma-h5','emma-journey-origin',...Array.from({length:10},(_,i)=>'emma-journey-'+String(i+3).padStart(2,'0'))];
const mime={'.html':'text/html','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.xml':'application/xml','.ico':'image/x-icon','.json':'application/json','.woff2':'font/woff2','.pdf':'application/pdf'};
(async()=>{
 assert.equal(process.env.CI,'true','Run this diagnostic only in hosted CI');
 const server=http.createServer((req,res)=>{try{const u=new URL(req.url,'http://localhost'),urlpath=decodeURIComponent(u.pathname);if(urlpath.split('/').some(x=>x.startsWith('.')))return res.writeHead(403).end();const file=path.resolve(root,'.'+urlpath);if(!file.startsWith(root+path.sep)||!mime[path.extname(file)])return res.writeHead(403).end();fs.realpath(file,(e,real)=>{if(e||!real.startsWith(root+path.sep))return res.writeHead(404).end();const parts=path.relative(root,real).split(path.sep);if(parts.some(x=>x.startsWith('.'))||!mime[path.extname(real)])return res.writeHead(403).end();fs.readFile(real,(err,b)=>err?res.writeHead(404).end():res.writeHead(200,{'Content-Type':mime[path.extname(real)]||'application/octet-stream'}).end(b));});}catch(_){res.writeHead(400).end()}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`;
 await new Promise((resolve,reject)=>http.get(origin+'/.git/config',r=>{r.resume();r.statusCode===403?resolve():reject(new Error('hidden path not denied'))}).on('error',reject));
 fs.mkdirSync(out,{recursive:true});const testSecret=path.join(out,'server-fixture.js'),testLink=path.join(root,'__emma-preview-hidden-'+process.pid+'.js');fs.writeFileSync(testSecret,'synthetic fixture');fs.symlinkSync(testSecret,testLink);try{await new Promise((resolve,reject)=>http.get(origin+'/'+path.basename(testLink),r=>{r.resume();r.statusCode===403?resolve():reject(new Error('hidden symlink target not denied'))}).on('error',reject));}finally{fs.unlinkSync(testLink);fs.unlinkSync(testSecret)}const browser=await chromium.launch({headless:true});const report={scope:'diagnostic only; no release or owner acceptance',profiles:[],captures:[],errors:[],prior_blank_capture:{run:40766330050,artifact:12851145697,file:'desktop-emma-journey-origin.jpg'}};
 async function snap(page,name){const b=await page.screenshot({type:'jpeg',quality:75,fullPage:false});assert(b.length<1024*1024,'screenshot size limit');fs.writeFileSync(path.join(out,name),b,{flag:'wx'});}
 async function captureFigure(page,id,name){
  const locator=page.locator('#picture-'+id+' img');
  await locator.evaluate(async im=>{await im.decode();assertImage();const src=im.currentSrc;for(let n=0;n<3;n++)await new Promise(r=>requestAnimationFrame(r));assertImage();if(im.currentSrc!==src)throw Error('Image source changed after decoding');function assertImage(){if(!im.complete||!im.naturalWidth||!im.naturalHeight)throw Error('Image not decoded')}});
  const bytes=await page.screenshot({type:'jpeg',quality:75,fullPage:false});assert(bytes.length<1024*1024,'screenshot size limit');
  // Persist the unmodified viewport capture even when the pixel check fails.
  fs.writeFileSync(path.join(out,name),bytes,{flag:'wx'});
  const samples=await page.evaluate(async({id,jpeg})=>{
   const im=document.querySelector('#picture-'+id+' img'),r=im.getBoundingClientRect(),style=getComputedStyle(im);
   if(devicePixelRatio!==1||style.filter!=='none'||Number(style.opacity)!==1)throw Error('Unsupported screenshot image rendering state');
   if(Math.abs(r.width/r.height-im.naturalWidth/im.naturalHeight)>.02)throw Error('Unsupported image aspect ratio');
   const actual=new Image();actual.src='data:image/jpeg;base64,'+jpeg;await actual.decode();
   if(actual.naturalWidth!==innerWidth||actual.naturalHeight!==innerHeight)throw Error('Screenshot viewport size mismatch');
   const ac=document.createElement('canvas');ac.width=innerWidth;ac.height=innerHeight;const ax=ac.getContext('2d',{willReadFrequently:true});ax.drawImage(actual,0,0);
   const ec=document.createElement('canvas');ec.width=Math.ceil(r.width);ec.height=Math.ceil(r.height);const ex=ec.getContext('2d',{willReadFrequently:true});ex.drawImage(im,0,0,ec.width,ec.height);
   const left=Math.max(0,r.left)+3,right=Math.min(innerWidth,r.right)-3,top=Math.max(0,r.top)+3,bottom=Math.min(innerHeight,r.bottom)-3,out=[];
   if(right<=left||bottom<=top)throw Error('No visible image area');
   for(let y=0;y<12;y++)for(let x=0;x<12;x++){
    const sx=Math.floor(left+(right-left)*(x+.5)/12),sy=Math.floor(top+(bottom-top)*(y+.5)/12),hit=document.elementFromPoint(sx,sy);
    if(hit!==im&&hit!==im.parentElement)continue;
    const observed=ax.getImageData(sx,sy,1,1).data, expected=ex.getImageData(Math.max(0,Math.min(ec.width-1,Math.floor(sx-r.left))),Math.max(0,Math.min(ec.height-1,Math.floor(sy-r.top))),1,1).data;
    out.push([expected[0],expected[1],expected[2],observed[0],observed[1],observed[2]]);
   }
   return out;
  },{id,jpeg:bytes.toString('base64')});
  const result=inspectPixels(samples);report.captures.push({id,file:name,...result});
 }
 async function geometry(page,url){await page.goto(origin+url,{waitUntil:'load'});await page.waitForSelector('.fc-unified-continue');await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))});return page.evaluate(()=>{let a=document.querySelector('.fc-life-hero').getBoundingClientRect(),b=document.querySelector('.fc-unified-continue').getBoundingClientRect();return{hero:{x:a.x,y:a.y,width:a.width,height:a.height},continue:{x:b.x,y:b.y,width:b.width,height:b.height}}})}
 try {
  for(const [name,width,height] of [['desktop',1440,900],['phone',390,844],['narrow',320,740]]){
   const ctx=await browser.newContext({viewport:{width,height},serviceWorkers:'block'});await ctx.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());const page=await ctx.newPage();const baseline=await geometry(page,'/history/__emma-baseline-for-qa.html');const actual=await geometry(page,'/history/emma-hale-smith.html');
   for(const area of ['hero','continue'])for(const v of ['x','y','width','height'])assert(Math.abs(baseline[area][v]-actual[area][v])<=1,`${name}: ${area}.${v} changed`);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),name+': horizontal overflow');
   await snap(page,name+'-opening.jpg');
   for(const id of ids){
    const figure=page.locator('#picture-'+id), trigger=figure.locator(':scope > a');assert.equal(await figure.count(),1,id+' owner');
    await figure.scrollIntoViewIfNeeded();await figure.locator('img').waitFor({state:'visible'});await page.waitForFunction(k=>{const i=document.querySelector('#picture-'+k+' img');return i&&i.complete&&i.naturalWidth>0},id,{timeout:8000});
    await captureFigure(page,id,name+'-'+id+'.jpg');
    const source=await figure.locator('figcaption .fc-study-visual-sources a').first().getAttribute('href');assert(source,id+' source missing');
    await trigger.click();const dialog=page.locator('#topicArtworkDetailDialog[open]');await dialog.waitFor({state:'visible'});
    assert(await dialog.locator('a').evaluateAll((links,src)=>links.some(a=>a.getAttribute('href')===src),source),id+' expected source not visible in detail panel');
    if(id==='emma-journey-03'||id==='emma-story1-ride'){
     await dialog.locator('[data-full-image-viewer]').click();const full=page.locator('dialog.fc-full-image-viewer[open]');await full.waitFor({state:'visible'});await page.keyboard.press('Escape');await full.waitFor({state:'hidden'});
    }
    if(await dialog.isVisible())await page.keyboard.press('Escape');await dialog.waitFor({state:'hidden'});
   }
   for(const id of ['heading-emma-beginnings','emma-pen-family','emma-songs-separation','emma-relief-questions','emma-household','emma-remaining-years','print-emma'])assert.equal(await page.locator('#'+id).count(),1,id+' missing');
   report.profiles.push({name,width,height,baseline,actual,figures:ids.length});await ctx.close();
  }
  const ctx=await browser.newContext({serviceWorkers:'block'});await ctx.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());const p=await ctx.newPage();
  for(const [from,to] of [['sources','heading-elect-lady-called'],['sources-heading','heading-elect-lady-called'],['more-stories','emma-more-stories-heading'],['more-stories-heading','emma-more-stories-heading'],['elect-lady-pen','elect-lady-pen'],['picture-emma-story1-ride','picture-emma-story1-ride'],['reflect','reflect']]){
   await p.goto(origin+'/history/emma-elect-lady.html?q=legacy#'+from);await p.waitForURL('**/history/emma-hale-smith.html?q=legacy#'+to);assert.equal(await p.locator('#'+to).count(),1,'legacy target '+to);
  }
  const context=await browser.newContext({javaScriptEnabled:false,serviceWorkers:'block'});await context.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());const nojs=await context.newPage();await nojs.goto(origin+'/history/emma-elect-lady.html#elect-lady-pen');assert.equal(await nojs.locator('a[href="emma-hale-smith.html"]').count(),1,'no-JS manual link');await context.close();await ctx.close();
 } catch(error){report.errors.push(String(error.stack||error));throw error}
 finally {fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));await browser.close();await new Promise(r=>server.close(r))}
})().catch(e=>{console.error(e);process.exitCode=1});
