const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/pioneer-sources');
(async()=>{
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,d)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':{'.html':'text/html','.css':'text/css','.js':'text/javascript','.webp':'image/webp'}[path.extname(file)]||'application/octet-stream'}).end(d));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch(),page=await browser.newPage(),records=[];
 fs.mkdirSync(out,{recursive:true});
 try{
  for(const [width,enlarged] of [[320,false],[390,false],[432,false],[1280,false],[390,true]]){
   await page.setViewportSize({width,height:1000});await page.goto(`http://127.0.0.1:${server.address().port}/pioneers.html`,{waitUntil:'load'});
   if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   await page.evaluate(()=>document.fonts.ready);const panels=page.locator('.pioneer-source-notes');assert.equal(await panels.count(),3);
   for(let i=0;i<3;i++){
    const panel=panels.nth(i),summary=panel.locator(':scope > summary');await summary.click();await summary.press('Space');assert.equal(await panel.getAttribute('open'),null);await summary.press('Space');assert.notEqual(await panel.getAttribute('open'),null);
    const groups=panel.locator(':scope > .fc-actions');assert.equal(await groups.count(),i===2?2:1);
    for(const link of await groups.locator('a').all()){await link.focus();assert(await link.evaluate(n=>document.activeElement===n));}
    await panel.evaluate(n=>window.scrollTo(0,n.getBoundingClientRect().top+scrollY-76));await page.screenshot({path:path.join(out,`notes-${i}-${width}${enlarged?'-enlarged':''}.png`)});
   }
   await page.mouse.move(0,0);await panels.first().locator(':scope > summary').focus();
   const measure=await page.evaluate(()=>{
    const ref=document.querySelector('.pioneer-story-copy .pioneer-source-links a'),base=getComputedStyle(ref);
    return {width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth+1,panels:[...document.querySelectorAll('.pioneer-source-notes')].map(panel=>({padding:getComputedStyle(panel).paddingLeft,groups:[...panel.querySelectorAll(':scope > .fc-actions')].map(group=>{const s=getComputedStyle(group),g=group.getBoundingClientRect(),p=panel.getBoundingClientRect();return {center:Math.abs((g.left+g.right-p.left-p.right)/2),gap:s.gap,before:s.marginTop,after:s.marginBottom,onlyLinks:[...group.childNodes].every(n=>n.nodeType===1&&n.tagName==='A'),links:[...group.children].map(a=>{const s=getComputedStyle(a),r=a.getBoundingClientRect();return {label:a.textContent,href:a.getAttribute('href'),height:r.height,contained:r.left>=p.left+17&&r.right<=p.right-17,shared:s.background===base.background&&s.color===base.color&&s.borderRadius===base.borderRadius,wrap:s.whiteSpace!=='nowrap',focusOutline:getComputedStyle(a).outlineWidth};})};})}))};
   });
   assert(!measure.overflow);assert.equal(measure.panels.flatMap(p=>p.groups.flatMap(g=>g.links)).length,6);
   for(const p of measure.panels){assert.equal(p.padding,'18px');for(const g of p.groups){assert(g.center<=1&&g.onlyLinks);assert.equal(g.gap,'10px');assert.equal(g.before,'18px');assert.equal(g.after,'24px');assert(g.links.every(a=>a.height>=44&&a.contained&&a.shared&&a.wrap));}}
   await panels.nth(2).locator(':scope > .fc-actions').last().evaluate(n=>window.scrollTo(0,n.getBoundingClientRect().top+scrollY-76));await page.screenshot({path:path.join(out,`witness-controls-${width}${enlarged?'-enlarged':''}.png`)});records.push({enlarged,...measure});
  }
  fs.writeFileSync(path.join(out,'geometry.json'),JSON.stringify(records,null,2));console.log('PIONEER SOURCE CONTROLS PASS: six shared controls, four centered groups, three disclosures, five viewport/text profiles; keyboard focus and disclosure reopen');
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
