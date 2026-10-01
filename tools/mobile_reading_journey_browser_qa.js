const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts/mobile-reading-journey');
fs.mkdirSync(out, {recursive:true});
const server = http.createServer((req,res) => {
  const file = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(root + path.sep)) {res.writeHead(403); return res.end();}
  fs.readFile(file,(err,data) => {if(err){res.writeHead(404);return res.end();}
    const ext=path.extname(file);
    res.setHeader('Content-Type', ({'.html':'text/html','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.png':'image/png'})[ext] || 'application/octet-stream');
    res.end(data);
  });
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({headless:true});
  const results=[];
  try {
    for (const width of [320,360,390,430,700,701,1280]) {
      for (const scale of [1,2]) {
        const page=await browser.newPage({viewport:{width,height:1000}});
        await page.goto('http://127.0.0.1:'+server.address().port+'/answers/what-happens-after-death.html',{waitUntil:'networkidle'});
        if(scale===2) await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        const read=()=>page.evaluate(()=>{
          const nav=document.querySelector('.fc-life-after-death-journey');
          return {display:getComputedStyle(nav).display,overflow:document.documentElement.scrollWidth>innerWidth,
            links:[...nav.querySelectorAll('a')].map(a=>{
              const r=a.getBoundingClientRect(),s=getComputedStyle(a);
              return {text:a.textContent,href:a.getAttribute('href'),target:!!document.querySelector(a.getAttribute('href')),
                x:r.x,y:r.y-nav.getBoundingClientRect().y,width:r.width,height:r.height,scrollWidth:a.scrollWidth,clientWidth:a.clientWidth,
                color:s.color,background:s.backgroundImage,border:s.borderColor,align:s.textAlign};
            })};
        });
        const candidate=await read();
        assert.equal(candidate.links.length,10);
        for(const a of candidate.links){assert(a.target); assert(a.height>=44); assert(a.scrollWidth<=a.clientWidth+1);}
        if(width<=700){
          assert.equal(candidate.display,'grid');
          for(let i=0;i<10;i++){
            const a=candidate.links[i],first=candidate.links[0];
            assert(Math.abs(a.x-first.x)<1);assert(Math.abs(a.width-first.width)<1);assert.equal(a.align,'left');
            if(i) assert(a.y>=candidate.links[i-1].y+candidate.links[i-1].height+8);
          }
        }
        if(width>700){
          await page.evaluate(()=>[...document.querySelectorAll('style')].find(s=>s.textContent.includes('fc-life-after-death-journey')).remove());
          const baseline=await read();
          assert.deepEqual(candidate,baseline,'Desktop must match existing layout');
        }
        const nav=page.locator('.fc-life-after-death-journey');
        await nav.scrollIntoViewIfNeeded();
        await nav.screenshot({path:path.join(out,width+'-'+scale+'x.png')});
        await page.locator('.fc-life-after-death-journey a').first().focus();
        const focus=await page.locator('.fc-life-after-death-journey a').first().evaluate(a=>{
          const s=getComputedStyle(a);return {style:s.outlineStyle,width:s.outlineWidth,offset:s.outlineOffset};
        });
        assert.notEqual(focus.style,'none');assert(parseFloat(focus.width)>=2);
        await page.screenshot({path:path.join(out,width+'-'+scale+'x-focus.png')});
        for(const a of candidate.links){
          await page.locator('.fc-life-after-death-journey a[href="'+a.href+'"]').click();
          assert.equal(new URL(page.url()).hash,a.href);
        }
        results.push({width,scale,focus,...candidate});
        await page.close();
      }
    }
    fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));
    console.log('PASS: 14 phone/desktop and enlarged-text layouts, ten destinations, keyboard focus and desktop preservation');
  } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
