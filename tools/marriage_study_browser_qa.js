const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa-artifacts/marriage-study');
(async()=>{
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!file.startsWith(root+path.sep))return res.writeHead(403).end();fs.readFile(file,(e,d)=>e?res.writeHead(404).end():res.writeHead(200,{'Content-Type':{'.html':'text/html','.css':'text/css','.js':'text/javascript','.webp':'image/webp'}[path.extname(file)]||'application/octet-stream'}).end(d));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({headless:true}),page=await browser.newPage(),results=[];
 fs.mkdirSync(out,{recursive:true});const origin=`http://127.0.0.1:${server.address().port}`;
 const routes=[...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname).filter(r=>fs.readFileSync(path.join(root,r==='/'?'index.html':r.slice(1)),'utf8').includes('data-linked-study-reference="modern-scripture"'));
 assert.equal(routes.length,12);
 try{
 for(const [width,enlarged] of [[320,false],[390,false],[432,false],[1280,false],[390,true]]){
 await page.setViewportSize({width,height:900});await page.goto(origin+'/answers/what-is-eternal-marriage.html');if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
 for(const section of ['practice','scripture-path']){await page.locator('#'+section).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`${section}-${width}${enlarged?"-enlarged":""}.png`)});}
 const geometry=await page.evaluate(()=>{const ol=document.querySelector('.fc-marriage-practice'),s=ol.parentElement,a=ol.getBoundingClientRect(),r=s.getBoundingClientRect(),last=ol.lastElementChild.getBoundingClientRect();return {width:innerWidth,padding:getComputedStyle(ol).paddingLeft,offset:Math.abs((a.left+a.right-r.left-r.right)/2),overflow:document.documentElement.scrollWidth>innerWidth+1,titleAlign:getComputedStyle(s.querySelector('h2')).textAlign,lastWidth:last.width,listWidth:a.width,items:ol.children.length};});
 assert.equal(geometry.padding,'0px');assert(geometry.offset<1);assert(!geometry.overflow);assert.equal(geometry.titleAlign,'center');assert.equal(geometry.items,7);assert(Math.abs(geometry.lastWidth-geometry.listWidth)<1);
 results.push(geometry);
 if(!enlarged&&(width===390||width===1280))for(const route of routes){await page.goto(origin+route);const card=page.locator('[data-linked-study-reference="modern-scripture"]');assert.equal(await page.locator('img[src*="modern-scripture"]').count(),0);assert.equal(await card.locator('a[href="/answers/jesus-christ-latter-day-saint-beliefs.html#picture-modern-scripture"]').count(),1);assert.equal(await card.locator('a[href*="/nt/john/5"]').count(),1);assert.equal(await card.locator('h3').evaluate(n=>getComputedStyle(n).textAlign),'center');}
 }
 await page.goto(origin+'/answers/jesus-christ-latter-day-saint-beliefs.html');assert.equal(await page.locator('#picture-modern-scripture img').count(),1);
 fs.writeFileSync(path.join(out,'geometry.json'),JSON.stringify({results,textReferences:routes,ownerArtworkPreserved:true},null,2));console.log('MARRIAGE STUDY PASS: five centered grid profiles, 24 text-reference profiles, original artwork preserved');
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
