const assert=require('node:assert/strict');
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
  const records = JSON.parse(fs.readFileSync(path.join(root,'docs/unified-opening-inventory.json'))).pages.filter(x=>x.hero && (!process.env.QA_PATHS || process.env.QA_PATHS.split(",").includes(x.path)));
  const authoredRoutes=new Set(['timelines/latter-day-saint-church-history-timeline.html','timelines/willie-and-martin-handcart-map.html','timelines/life-of-christ-journey-map.html']);
  const authoredCue=record=>{const authored=authoredRoutes.has(record.path);assert.equal(record.template==='standard-timeline-study-reference',authored,'Only exact reviewed timeline routes use authored cue contract');return authored;};
  const results=[],enlarged=[];
  const heroGeometry=()=>{const e=document.querySelector('.fc-visual-hero,[data-covenant-hero-slot],.cfm-desktop-picture,.gc-intro-visual'),r=e.getBoundingClientRect();return {width:r.width,height:r.height,top:r.top+scrollY};};
  try {
    for(const [width,height] of (process.env.QA_PROFILES ? JSON.parse(process.env.QA_PROFILES) : [[1536,792],[1920,900],[1366,768],[320,740],[390,844],[432,810]])) {
      await page.setViewportSize({width,height});
      for(const record of records) {
        const url=`http://127.0.0.1:${server.address().port}/${record.path}`;
        await page.route('**/unified-opening*',r=>r.abort());
        await page.goto(url,{waitUntil:'domcontentloaded'});
        await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(30);
        const heroBefore=await page.evaluate(heroGeometry);
        await page.unroute('**/unified-opening*');
        await page.goto(url,{waitUntil:'domcontentloaded'});
        await page.waitForSelector(authoredCue(record)?'.timeline-opening-continue':'.fc-unified-continue');if(authoredCue(record))await page.waitForSelector('[data-unified-opening]');
        await page.evaluate(()=>document.fonts.ready);
        await page.waitForTimeout(30);
        results.push({path:record.path,width,height,authored:authoredCue(record),heroBefore,heroAfter:await page.evaluate(heroGeometry),...await page.evaluate(authored=>{
          const opening=document.querySelector('[data-unified-opening]'),cue=opening.querySelector(authored?'.timeline-opening-continue':'.fc-unified-continue'),r=cue.getBoundingClientRect();
          const cues=[...document.querySelectorAll('.fc-unified-continue,.fc-scroll-cue,.fc-mobile-scroll-cue,.fc-art-continue,.fc-covenant-continue')].filter(e=>e.getBoundingClientRect().height&&getComputedStyle(e).display!=='none');
          const href=cue.getAttribute('href'),target=href&&document.getElementById(href.slice(1));
          const retained=document.querySelector('.fc-unified-opening-continuation:not([hidden])');
          const contentClipped=[...opening.querySelectorAll('h1,p,a,button,summary')].some(el=>{
            if(el===cue||cue.contains(el))return false;
            const b=el.getBoundingClientRect(),s=getComputedStyle(el);if(!b.width||!b.height||s.display==='none'||s.visibility==='hidden')return false;
            for(let parent=el.parentElement;parent&&parent!==opening.parentElement;parent=parent.parentElement){
              const ps=getComputedStyle(parent),pr=parent.getBoundingClientRect();
              if(/hidden|clip/.test(ps.overflowY)&&(b.bottom>pr.bottom+1||b.top<pr.top-1))return true;
            }
            return b.bottom>r.top+1||b.left < -1||b.right>document.documentElement.clientWidth+1;
          });
          return {bottom:r.bottom,top:r.top,center:r.x+r.width/2,clientCenter:document.documentElement.clientWidth/2,openingBottom:opening.getBoundingClientRect().bottom,overflow:document.documentElement.scrollWidth>innerWidth+1,href,contentClipped,cueCount:cues.length,targetTop:target?target.getBoundingClientRect().top:null,targetExists:!!target,retainedEntered:!retained||!!(target&&(target===retained||target.contains(retained)||(target.compareDocumentPosition(retained)&Node.DOCUMENT_POSITION_FOLLOWING)))};
        },authoredCue(record))});
      }
      console.log(`Measured ${width}x${height}`);
    }
    if(!process.env.QA_PATHS&&!process.env.QA_PROFILES){
      for(const [width,height] of [[320,740],[1280,720]]){
        await page.setViewportSize({width,height});
        for(const record of records){
          await page.goto(`http://127.0.0.1:${server.address().port}/${record.path}`,{waitUntil:'domcontentloaded'});
          await page.waitForSelector(authoredCue(record)?'.timeline-opening-continue':'.fc-unified-continue');if(authoredCue(record))await page.waitForSelector('[data-unified-opening]');
          await page.evaluate(()=>document.documentElement.style.fontSize='200%');
          await page.waitForTimeout(60);
          enlarged.push({path:record.path,width,height,...await page.evaluate(authored=>{
            const o=document.querySelector('[data-unified-opening]'),c=o.querySelector(authored?'.timeline-opening-continue':'.fc-unified-continue'),b=o.getBoundingClientRect(),r=c.getBoundingClientRect();
            const cutoff=[...o.querySelectorAll('h1,p')].some(el=>{
              const e=el.getBoundingClientRect();if(!e.width||!e.height)return false;
              return e.bottom>r.top+1||e.left < -1||e.right>document.documentElement.clientWidth+1;
            });
            return {openingBottom:b.bottom,cueBottom:r.bottom,cueTop:r.top,cutoff,overflow:document.documentElement.scrollWidth>innerWidth+1};
          },authoredCue(record))});
        }
      }
    }
  } finally {
    fs.mkdirSync(path.join(root,'.qa-artifacts'),{recursive:true});
    fs.writeFileSync(path.join(root,'.qa-artifacts/unified-opening.json'),JSON.stringify(results,null,2));
    fs.writeFileSync(path.join(root,'.qa-artifacts/unified-opening-enlarged.json'),JSON.stringify(enlarged,null,2));
    await browser.close();await new Promise(r=>server.close(r));
  }
  const failures=results.filter(x=>(x.authored?(x.bottom>x.height-8||x.top<0||x.targetTop<x.height-1):Math.abs(x.bottom-(x.height-20))>1)||Math.abs(x.center-x.clientCenter)>1||x.openingBottom<x.height-1||x.overflow||x.contentClipped||!x.href||x.cueCount!==1||!x.targetExists||!x.retainedEntered||['width','height','top'].some(k=>Math.abs(x.heroBefore[k]-x.heroAfter[k])>1));
  console.log(JSON.stringify({cases:results.length,failures},null,2));
  const enlargedFailures=enlarged.filter(x=>x.cutoff||x.overflow||x.cueBottom>x.openingBottom||x.openingBottom<x.height-1);
  console.log(JSON.stringify({enlargedCases:enlarged.length,enlargedFailures},null,2));
  if(failures.length||enlargedFailures.length||(!process.env.QA_PATHS && !process.env.QA_PROFILES && (results.length!==282||enlarged.length!==94)))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
