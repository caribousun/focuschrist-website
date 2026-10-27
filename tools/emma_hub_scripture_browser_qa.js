'use strict';
// Six actual local-hosted browser journeys, not source-art or release acceptance.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/emma-hub-scripture');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const route='history/emma-hale-smith.html';
const cases=[
 {label:'Luke 6:12–16',key:'nt/luke/6',start:12,end:16,sha:'b8ad2f2a8ea945fcef6482351505cb67ef0c6e236a69c01a03946bf790447ccc',mode:'keyboard'},
 {label:'Matthew 26:26–30',linkLabel:'Read Matthew 26:26–30',key:'nt/matt/26',start:26,end:30,sha:'18b5e040e096a7b8a46c7a9a5c3643efe29c3285dec1c4635409c42aea28f8b2',mode:'click'}
];
(async()=>{
 assert.equal(process.env.CI,'true','Hosted CI only');
 const hub=fs.readFileSync(path.join(root,route));assert.equal(sha(hub),'50c334379066722ef6e80e97d70f0f2ca431777b5857eb15b998da65cc1783cf');
 for(const c of cases){const raw=fs.readFileSync(path.join(root,'scripture-data',c.key+'.json'));assert.equal(sha(raw),c.sha);c.chapter=JSON.parse(raw);}
 const report={scope:'Two hub citation interactions only; not artwork or release approval',status:'INCOMPLETE',source_sha256:sha(hub),results:[],captures:[],pageErrors:[]};
 fs.mkdirSync(out,{recursive:true});
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,b)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':({'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'application/octet-stream'}).end(b));});
 let browser,total=0;
 try{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  browser=await chromium.launch({headless:true});
  const page=await browser.newPage();page.setDefaultTimeout(8000);page.setDefaultNavigationTimeout(12000);
  await page.route('https://**',r=>r.abort());page.on('pageerror',e=>report.pageErrors.push(String(e)));
  const capture=async name=>{assert(report.captures.length<12);const b=await page.screenshot({type:'jpeg',quality:80,fullPage:false,timeout:8000});assert(b.length<=1024*1024);total+=b.length;assert(total<=12*1024*1024);fs.writeFileSync(path.join(out,name),b,{flag:'wx'});report.captures.push({file:name,bytes:b.length,sha256:sha(b),viewport:page.viewportSize()});};
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:900});
   await page.goto(`http://127.0.0.1:${server.address().port}/${route}`,{waitUntil:'domcontentloaded'});
   await page.waitForSelector('#fc-scripture-reader',{state:'attached'});
   assert.equal(await page.locator('#reflection-c2, #picture-emma-c2').count(),0,'Removed weak-fit scene is not retained on current hub');
   assert.equal(await page.locator('main a.fc-inline-scripture[href*="/nt/john/4?"]:visible').count(),0,'Removed John4 citation is historical, not a current journey');
   for(const [index,c]of cases.entries()){
    const href=`https://www.churchofjesuschrist.org/study/scriptures/${c.key}?lang=eng&id=p${c.start}-p${c.end}#p${c.start}`;
    const link=page.locator(`main p > a.fc-inline-scripture[href="${href}"]:visible`);
    assert.equal(await link.count(),1);assert.equal(await link.textContent(),c.linkLabel||c.label);assert.equal(await link.getAttribute('target'),'_blank');assert.equal(await link.getAttribute('rel'),'noopener noreferrer');
    await link.scrollIntoViewIfNeeded();await link.focus();
    const box=await link.evaluate(n=>{const r=n.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};});assert(box.width>0&&box.height>0&&box.x>=-1&&box.right<=width+1);
    await capture(`hub-link-${index}-${width}.jpg`);
    if(c.mode==='keyboard')await page.keyboard.press('Enter');else await link.click();
    const dialog=page.locator('#fc-scripture-reader[open]');await dialog.waitFor({state:'visible'});
    await page.waitForFunction(()=>document.querySelector('#fc-scripture-reader .fc-scripture-verses')?.children.length>0,null,{timeout:8000});
    assert.equal(await dialog.locator('#fc-scripture-title').textContent(),c.label);
    assert.equal(await dialog.locator('.fc-scripture-source').getAttribute('href'),href);
    const selected=c.chapter.verses.filter(v=>v.number>=c.start&&v.number<=c.end);
    assert.deepEqual(await dialog.locator('.fc-scripture-number').allTextContents(),selected.map(v=>String(v.number)));
    const normalized=t=>t.replace(/\s+/g,' ').trim();
    assert.deepEqual((await dialog.locator('.fc-scripture-verse').allTextContents()).map(normalized),selected.map(v=>normalized(v.number+' '+v.text)));
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal page overflow');
    const geometry=await dialog.evaluate(n=>{const r=n.getBoundingClientRect(),b=n.querySelector('.fc-scripture-x').getBoundingClientRect();return{left:r.left,right:r.right,top:r.top,bottom:r.bottom,close:{left:b.left,right:b.right,top:b.top,bottom:b.bottom},viewport:{width:innerWidth,height:innerHeight}};});
    assert(geometry.left>=-1&&geometry.right<=width+1&&geometry.close.left>=0&&geometry.close.right<=width&&geometry.close.top>=0&&geometry.close.bottom<=900,'Reader and close within viewport');
    await capture(`hub-reader-${index}-${width}.jpg`);
    if(c.mode==='keyboard')await page.keyboard.press('Escape');else await dialog.locator('.fc-scripture-x').click();
    await page.waitForFunction(n=>!document.getElementById('fc-scripture-reader').open&&document.activeElement===n&&!document.body.classList.contains('fc-scripture-open'),await link.elementHandle(),{timeout:5000});
    assert.equal(await page.locator('dialog.fc-artwork-detail-dialog[open]').count(),0);
    report.results.push({viewportWidth:width,label:c.label,href,activation:c.mode,close:c.mode==='keyboard'?'Escape':'button',focusReturned:true,verses:selected.map(v=>v.number),source_box:box,reader_geometry:geometry});
   }
  }
  assert.equal(report.results.length,6);assert.equal(report.captures.length,12);assert.deepEqual(report.pageErrors,[]);report.status='PASS';
 }catch(error){report.status='FAIL';report.error=String(error);throw error;}
 finally{
  try{if(browser)await browser.close();}finally{await new Promise(resolve=>server.close(resolve));const b=Buffer.from(JSON.stringify(report,null,2)+'\n');assert(b.length<=64*1024);fs.writeFileSync(path.join(out,'results.json'),b);}
 }
 console.log('PASS six bounded hub scripture journeys; twelve actual viewport captures; not release approval');
})().catch(error=>{console.error(error);process.exitCode=1;});
