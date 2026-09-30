const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
(async () => {
  const server = http.createServer((req,res) => {
    const file = path.resolve(root, '.' + decodeURIComponent(new URL(req.url,'http://localhost').pathname));
    if (!file.startsWith(root + path.sep)) return res.writeHead(403).end();
    const types = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.webp':'image/webp'};
    fs.readFile(file,(e,data) => e ? res.writeHead(404).end() : res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'}).end(data));
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const browser = await chromium.launch({headless:true,...(process.env.QA_BROWSER_CHANNEL?{channel:process.env.QA_BROWSER_CHANNEL}:{})});
  const page = await browser.newPage();
  await page.route('https://**',r=>r.abort());
  const assert=require('node:assert/strict'),results=[];
  const origin=`http://127.0.0.1:${server.address().port}`;
  const routes=[...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>new URL(m[1]).pathname);
  assert.equal(routes.length,125);
  let onward=0;
  for(const route of routes){const source=fs.readFileSync(path.join(root,route==='/'?'index.html':route.slice(1)),'utf8');
    for(const section of source.matchAll(/<section\b[^>]*id="(?:continue-study|connected-study)"[^>]*>([\s\S]*?)<\/section>/g)){
      for(const tag of section[1].matchAll(/<article\b[^>]*data-balanced-study-row="last"[^>]*>/g)){assert(/class="[^"]*fc-study-promotion/.test(tag[0]),route+' onward card must use established centered class');onward++;}
    }
  }
  assert.equal(onward,15,'All fifteen linked fullspan onward cards inventoried');

  try {
    for(const [width,height,enlarged] of [[1918,991,false],[1536,792,false],[390,844,false],[320,740,false],[1366,900,true],[390,844,true]]) {
      await page.setViewportSize({width,height});
      await page.goto(origin+'/answers.html',{waitUntil:'load'});
      if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
      const measure=()=>{
        const box=n=>{const r=n.getBoundingClientRect();return {left:r.left,right:r.right};};
        const inner=document.querySelector('.fc-conference-inner'),section=inner.parentElement,neighbor=section.nextElementSibling;
        return {inner:box(inner),neighbor:box(neighbor),overflow:document.documentElement.scrollWidth>innerWidth+1};
      };
      const rails=await page.evaluate(measure);
      assert(await page.locator('.gc-intro-visual figcaption').evaluate(c=>{const a=c.querySelector('a');return a.getAttribute('href')==='come-follow-me.html#personal-study-art'&&a.textContent.endsWith('Come, Follow Me.')&&![...c.childNodes].slice([...c.childNodes].indexOf(a)+1).some(n=>n.textContent.trim());}),'Attribution period belongs within its block link');

      assert(Math.abs(rails.inner.left-rails.neighbor.left)<1&&Math.abs(rails.inner.right-rails.neighbor.right)<1,'Conference exact neighboring rails '+width);
      assert(!rails.overflow,'Answers overflow '+width);
      if(width===1918){const bad=await page.addStyleTag({content:'.fc-conference-section{padding-inline:24px!important}.fc-conference-inner{width:auto!important;max-width:1240px!important}'});const wrong=await page.evaluate(measure);assert(Math.abs(wrong.inner.left-wrong.neighbor.left)>50,'Old wide rail fixture must fail');await bad.evaluate(n=>n.remove());}
      await page.goto(origin+'/church-history.html',{waitUntil:'load'});
      if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
      const gaps=await page.evaluate(()=>[...document.querySelectorAll('#aaronic-priesthood-restoration .fc-actions,#melchizedek-priesthood-restoration .fc-actions')].map(a=>({gap:a.getBoundingClientRect().top-a.previousElementSibling.getBoundingClientRect().bottom,expected:parseFloat(getComputedStyle(a).marginTop),classApplied:a.classList.contains('fc-actions--content')})));
      assert.equal(gaps.length,2);assert(gaps.every(g=>g.classApplied&&g.expected>=18&&g.gap>=g.expected-.5),'Priesthood card paragraph/action gap '+width);
      const returnCards=[];
      for(const route of ['answers/aaronic-priesthood-restoration.html','answers/melchizedek-priesthood-restoration.html']){
        await page.goto(origin+'/'+route,{waitUntil:'load'});
        if(enlarged)await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        const card=await page.evaluate(()=>{const a=[...document.querySelectorAll('article[data-balanced-study-row="last"]')].find(x=>x.textContent.includes('Return to Church History')),box=a.getBoundingClientRect();return {classApplied:a.classList.contains('fc-study-promotion'),parts:[...a.querySelectorAll('h3,p')].map(n=>{const range=document.createRange();range.selectNodeContents(n);const r=range.getBoundingClientRect();return {align:getComputedStyle(n).textAlign,centerError:Math.abs(r.left+r.width/2-box.left-box.width/2)};})};});
        assert(card.classApplied&&card.parts.length===2&&card.parts.every(x=>x.align==='center'&&x.centerError<2),'Return card text centered '+route+' '+width);
        returnCards.push({route,...card});
      }
      results.push({width,height,enlarged,rails,gaps,returnCards});
    }
    const mission=await require('./mission_caption_browser_qa')(page,origin);
    fs.mkdirSync(path.join(root,'.qa-artifacts'),{recursive:true});
    fs.writeFileSync(path.join(root,'.qa-artifacts/content-boundaries.json'),JSON.stringify({results,mission},null,2));
    console.log('PASS six conference rail/priesthood gap profiles plus six Mission caption/label profiles');
  } finally {await browser.close();await new Promise(r=>server.close(r));}
})().catch(error=>{console.error(error);process.exitCode=1;});
