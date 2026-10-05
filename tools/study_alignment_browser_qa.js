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
  page.on('pageerror',e=>console.error('PAGE',e.message));
  const results=[];
  let mobileRows;
  try {
    for(const [width,height,enlarged] of [[1536,792,false],[390,844,false],[320,740,false],[320,740,true]]) {
      await page.setViewportSize({width,height});
      for(const route of ['missionary.html','ask.html','come-follow-me.html','answers/holy-ghost.html','answers/race-priesthood-and-temple-blessings.html']) {
        console.log(route,width);
        await page.goto(`http://127.0.0.1:${server.address().port}/${route}`,{waitUntil:'domcontentloaded'});
        await page.waitForFunction(()=>[...document.styleSheets].some(s=>s.href&&s.href.includes('unified-opening.css')));
        if(route!=='answers/race-priesthood-and-temple-blessings.html') await page.waitForSelector('.fc-unified-continue');
        else await page.locator('.fc-source-directory summary').click();
        await page.evaluate(()=>document.fonts.ready);
        await page.waitForTimeout(60);
        if(enlarged){await page.evaluate(()=>document.documentElement.style.fontSize='200%');await page.waitForTimeout(60);}
        const inspect=()=>{
          const issues=[],c=document.querySelector('.fc-unified-opening-continuation');
          const visible=e=>e.getBoundingClientRect().height>0;
          if(c&&!c.hidden){
            const rect=c.getBoundingClientRect();
            if(getComputedStyle(c).textAlign!=='center')issues.push('continuation text alignment');
            for(const row of c.querySelectorAll(':scope > .fc-actions,:scope > .cfm-actions,:scope > .fc-conference-actions')){
              if(getComputedStyle(row).justifyContent!=='center')issues.push('action row alignment');
              const groups=new Map();
              for(const a of [...row.children].filter(visible)){const r=a.getBoundingClientRect(),key=Math.round(r.top);const group=groups.get(key)||[];group.push(r);groups.set(key,group);if(r.left<0||r.right>document.documentElement.clientWidth+1)issues.push('action overflow');}
              for(const group of groups.values()){const left=Math.min(...group.map(r=>r.left)),right=Math.max(...group.map(r=>r.right));if(Math.abs((left+right)/2-(rect.left+rect.width/2))>2)issues.push('visible action row center');}
            }
            const quote=c.querySelector('.fc-page-intro-scripture'),actions=c.querySelector('.fc-actions');
            if(quote&&actions&&quote.getBoundingClientRect().bottom>actions.getBoundingClientRect().top-15)issues.push('scripture/action vertical separation');
          }
          for(const nav of document.querySelectorAll('.fc-study-nav:not(.jj-local-nav)'))if(visible(nav)&&getComputedStyle(nav).justifyContent!=='center')issues.push('study navigation alignment');
          if(document.documentElement.scrollWidth>innerWidth+1)issues.push('page overflow');
          return issues;
        };
        const checks=await page.evaluate(inspect);
        if(route==='missionary.html'&&width===1536){
          const broken=await page.addStyleTag({content:'.fc-unified-opening-continuation{display:block!important;text-align:left!important}.fc-unified-opening-continuation>.fc-actions{justify-content:flex-start!important}'});
          const negatives=await page.evaluate(inspect);
          if(!negatives.includes('continuation text alignment')||!negatives.includes('action row alignment'))throw Error('Negative old-alignment fixture did not fail');
          await broken.evaluate(n=>n.remove());
        }
        results.push({route,width,height,enlarged,issues:checks});
      }
    }
    mobileRows=await require('./mobile_study_rows_browser_qa')(page,`http://127.0.0.1:${server.address().port}`);
    const reading=await require('./study_reading_balance_browser_qa')(page,`http://127.0.0.1:${server.address().port}`);
    fs.mkdirSync(path.join(root,'.qa-artifacts'),{recursive:true});
    fs.writeFileSync(path.join(root,'.qa-artifacts/study-reading-balance.json'),JSON.stringify(reading,null,2));
  } finally {await browser.close();await new Promise(r=>server.close(r));}
  fs.mkdirSync(path.join(root,'.qa-artifacts'),{recursive:true});
  fs.writeFileSync(path.join(root,'.qa-artifacts/study-alignment.json'),JSON.stringify(results,null,2));
  const failures=results.filter(x=>x.issues.length);console.log(JSON.stringify({cases:results.length,failures},null,2));
  fs.writeFileSync(path.join(root,'.qa-artifacts/mobile-study-rows.json'),JSON.stringify(mobileRows,null,2));
  if(results.length!==20||failures.length||!mobileRows||mobileRows.failures.length)process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
