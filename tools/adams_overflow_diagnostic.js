/* CI-only, diagnostic evidence; this does not establish release acceptance. */
'use strict';
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const crypto = require('node:crypto'), { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.qa-artifacts', 'adams-overflow-diagnostic');
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.woff2':'font/woff2','.ico':'image/x-icon'};
async function main() {
  if (process.env.CI !== 'true' || process.argv.length !== 2) throw new Error('Hosted CI only; fixed route and profile');
  const actual = execFileSync('git', ['rev-parse','HEAD'], {cwd:root,encoding:'utf8'}).trim();
  if (!process.env.EXPECTED_CHECKOUT_SHA || actual !== process.env.EXPECTED_CHECKOUT_SHA) throw new Error('Checkout SHA mismatch');
  fs.mkdirSync(out, {recursive:true});
  const report = {scope:'Diagnostic only, not release acceptance', checkout:actual, profile:{width:320,height:1000,rootFontSize:'200%'}, route:'/timelines/adams-1881-introduction.html', fidelity:'External requests are blocked here; the original canonical runner does not block them. Exact 371px reproduction is an observation, not proof of cause.', expectedCanonicalScrollWidth:371, served:[], blocked:[], blockedWebSockets:[], errors:[]};
  let server, browser, context, requests=0, servedBytes=0;
  try {
    server = http.createServer((req,res) => {
      if (!['GET','HEAD'].includes(req.method)) return res.writeHead(405).end();
      let requested;
      try { requested = decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname); } catch { return res.writeHead(400).end(); }
      const parts=requested.split('/').filter(Boolean), ext=path.extname(requested).toLowerCase();
      if (parts.some(x=>x.startsWith('.')) || !TYPES[ext] || (parts.length>1 && !['assets','history','timelines','scripture-data'].includes(parts[0]))) return res.writeHead(403).end();
      const file=path.resolve(root,'.'+requested);
      if (!file.startsWith(root+path.sep)) return res.writeHead(403).end();
      try {
        const stat=fs.lstatSync(file);
        if (!stat.isFile() || stat.isSymbolicLink() || fs.realpathSync(file)!==file || stat.size>8*1024*1024) return res.writeHead(403).end();
        const bytes=fs.readFileSync(file); servedBytes+=bytes.length;
        if (servedBytes>128*1024*1024) return res.writeHead(413).end();
        report.served.push({path:requested,bytes:bytes.length,sha256:sha(bytes)});
        res.writeHead(200,{'Content-Type':TYPES[ext]}); res.end(req.method==='HEAD'?undefined:bytes);
      } catch { res.writeHead(404).end(); }
    });
    await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
    const origin='http://127.0.0.1:'+server.address().port;
    browser=await chromium.launch({headless:true});
    report.browserVersion=browser.version();
    context=await browser.newContext({viewport:{width:320,height:1000},deviceScaleFactor:1,serviceWorkers:'block'});
    await context.route('**/*', route=>{
      const url=new URL(route.request().url());
      if (url.origin!==origin) { if(report.blocked.length<200) report.blocked.push({origin:url.origin,path:url.pathname}); return route.abort(); }
      if (++requests>1000) { report.errors.push('Request bound exceeded'); return route.abort(); }
      return route.continue();
    });
    await context.routeWebSocket('**/*', ws=>{ const url=new URL(ws.url()); if(report.blockedWebSockets.length<200) report.blockedWebSockets.push({origin:url.origin,path:url.pathname}); ws.close(); });
    const page=await context.newPage();
    page.on('pageerror',e=>report.errors.push('pageerror: '+String(e).slice(0,2000)));
    page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP '+r.status()+' '+new URL(r.url()).pathname);});
    const response=await page.goto(origin+report.route,{waitUntil:'load',timeout:30000});
    report.status=response?.status() || null;
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%';});
    await page.evaluate(async()=>{
      const local=[...document.images].filter(n=>new URL(n.src,location.href).origin===location.origin);
      local.forEach(n=>{n.loading='eager';});
      await Promise.race([Promise.all(local.map(n=>n.decode().catch(()=>{}))),new Promise(resolve=>setTimeout(resolve,10000))]);
      await Promise.race([document.fonts.ready,new Promise(resolve=>setTimeout(resolve,5000))]);
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    });
    report.measurement=await page.evaluate(()=>{
      const box=r=>({x:r.x,y:r.y,left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height});
      const styleKeys=['display','visibility','opacity','position','overflowX','overflowY','whiteSpace','fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','width','minWidth','maxWidth','height','boxSizing','paddingLeft','paddingRight','marginLeft','marginRight','marginTop','marginBottom','paddingTop','paddingBottom','transform','transformOrigin','content','left','right','top','bottom','inset','overflowWrap','zIndex'];
      const styles=s=>Object.fromEntries(styleKeys.map(k=>[k,s[k]]));
      const selector=n=>{const chain=[];for(let e=n;e&&e.nodeType===1;e=e.parentElement){const parent=e.parentElement;const index=parent?[...parent.children].indexOf(e)+1:1;chain.push(e.tagName.toLowerCase()+':nth-child('+index+')');}return chain.reverse().join(' > ');};
      const nodes=[...document.querySelectorAll('*')];
      const elements=nodes.map((e,i)=>({index:i,selector:selector(e),tag:e.tagName.toLowerCase(),id:e.id||null,classes:e.getAttribute('class'),rect:box(e.getBoundingClientRect()),clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,offsetWidth:e.offsetWidth,scrollLeft:e.scrollLeft,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,style:styles(getComputedStyle(e)),before:styles(getComputedStyle(e,'::before')),after:styles(getComputedStyle(e,'::after'))}));
      const texts=[];const walker=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_TEXT);
      while(walker.nextNode()) { const n=walker.currentNode,range=document.createRange();range.selectNodeContents(n);texts.push({parent:selector(n.parentElement),text:n.data,rect:box(range.getBoundingClientRect()),fragments:[...range.getClientRects()].map(box)}); }
      return {innerWidth,innerHeight,devicePixelRatio,scrollX,scrollY,documentScrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth,rootFontSize:getComputedStyle(document.documentElement).fontSize,fontStatus:document.fonts.status,images:[...document.images].map(i=>({src:i.currentSrc||i.src,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight})),elements,texts};
    });
    report.reproduction=report.measurement.documentScrollWidth===report.expectedCanonicalScrollWidth ? 'MATCHES_371PX_CANONICAL_OBSERVATION' : 'NOT_REPRODUCED_371PX_CANONICAL_OBSERVATION';
    const shot=await page.screenshot({type:'png',fullPage:false,animations:'disabled',timeout:10000});
    fs.writeFileSync(path.join(out,'adams-320-200-percent.png'),shot,{flag:'wx'});
    report.screenshot={file:'adams-320-200-percent.png',bytes:shot.length,sha256:sha(shot)};
    const full=await page.screenshot({type:'png',fullPage:true,animations:'disabled',timeout:10000});
    fs.writeFileSync(path.join(out,'adams-320-200-percent-full-page.png'),full,{flag:'wx'});
    report.fullPageScreenshot={file:'adams-320-200-percent-full-page.png',bytes:full.length,sha256:sha(full)};
    if(report.status!==200) report.errors.push('Document did not return 200');
  } catch(e) { report.errors.push(String(e && e.stack || e)); }
  finally {
    if(context) await context.close().catch(()=>{});
    if(browser) await browser.close().catch(()=>{});
    if(server) await new Promise(resolve=>server.close(resolve));
    fs.writeFileSync(path.join(out,'diagnostic.json'),JSON.stringify(report,null,2)+'\n');
  }
  if(report.errors.length || !report.measurement || !report.screenshot) process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1;});
